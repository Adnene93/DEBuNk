# coding: utf-8
from time import time
import cProfile
import pstats
import csv
import unicodedata
from random import randint,uniform,random
from copy import deepcopy
from itertools import chain,product,ifilter
from filterer.filter import filter_pipeline_obj 
from math import trunc,sqrt
from sys import stdout
from collections import deque
from operator import iand,ior
#import numpy as np
from bisect import bisect_left
from math import log
from bisect import bisect
from functools import partial
from operator import itemgetter 
from cachetools import cached,LRUCache
import datetime
from outcomeDatasetsProcessor.outcomeDatasetsProcessor import process_outcome_dataset
from plotter.plotter import plot_timeseries
from enumerator.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config,enumerator_complex_from_dataset_new_config,pattern_subsume_pattern,respect_order_complex_not_after_closure,encode_sup,enumerator_generate_random_miserum
from enumerator.enumerator_attribute_hmt import all_parents_tag_exclusive
import gc




from enumerator.enumerator_attribute_complex_couple import enumerator_complex_cbo_init_new_config_couple


from outcomeAggregator.aggregateOutcome import compute_aggregates_outcomes
from measures.similaritiesDCS import similarity_vector_measure_dcs
from measures.qualityMeasure import compute_quality_and_upperbound
from util.csvProcessing import writeCSV,writeCSVwithHeader
from util.matrixProcessing import transformMatricFromDictToList,adaptMatrices,getInnerMatrix,getCompleteMatrix
from numpy.random import choice,multinomial
#from pympler.asizeof import asizeof




def printer_hmt(arr_tag_with_labels):
	ret={x[:x.find(' ')]:x for x in arr_tag_with_labels}
	tags=ret.viewkeys()
	tags=sorted(tags-reduce(set.union,[all_parents_tag_exclusive(x) for x in tags]))
	
	return [ret[x] for x in tags]

def pattern_printer(pattern,types_attributes):
	
	s=''
	for k in range(len(pattern)):
		if types_attributes[k]=='simple':
			if len(pattern[k])>1:
				if True:
					s+= '*'+' '
				else:
					s+= str(pattern[k])+' '
			else:
				s+= str(pattern[k][0])+' '
		elif types_attributes[k] in {'themes','hmt'}:
			
			s+= str(printer_hmt(pattern[k]))+' '#str(pattern[k])+' '
		else:
			s+= str(pattern[k])+' '
	return s


def Alpha_input_config(json_config_input,heatmap_for_matrix=False,verbose=False):
	
	json_config={
		"objects_file":json_config_input.get('objects_file'),
		"individuals_file":json_config_input.get('individuals_file'),
		"reviews_file":json_config_input.get('reviews_file'),
		"attributes_to_consider":json_config_input.get('attributes_to_consider',None),
		"delimiter":json_config_input.get('delimiter','\t'),

		"nb_objects":float(json_config_input.get('nb_objects',float('inf'))),
		"nb_individuals":float(json_config_input.get('nb_individuals',float('inf'))),

		"arrayHeader":(json_config_input.get('arrayHeader',[])),
		"numericHeader":(json_config_input.get('numericHeader',[])),
		"vector_of_outcome":(json_config_input.get('vector_of_outcome','None')),  #| None,
		"ponderation_attribute":(json_config_input.get('ponderation_attribute','None')), #if the attribute figure in the outcome then it's a weighted mean using second groups of individuals outcomes as a weight 

		"description_attributes_objects":(json_config_input.get('description_attributes_objects',[])),
		"description_attributes_individuals":(json_config_input.get('description_attributes_individuals',[])),
		
		"threshold_individuals":float(json_config_input.get('threshold_individuals',1)),
		"threshold_objects":float(json_config_input.get('threshold_objects',1)),
		"threshold_quality":float(json_config_input.get('threshold_quality',0.2)),
		

		"aggregation_measure":json_config_input.get('aggregation_measure','VECTOR_VALUES'),
		"similarity_measure":json_config_input.get('similarity_measure','MAAD'),
		"quality_measure":json_config_input.get('quality_measure','DISAGR_SUMDIFF'),
		"algorithm":json_config_input.get('algorithm','DSC+CLOSED+UB2'),# X could be : DSC, DSC+CLOSED, DSC+CLOSED+UB1, DSC+CLOSED+UB2, DSC+RandomWalk 
		"timebudget":json_config_input.get('timebudget',3600),
		

		"objects_scope":(json_config_input.get('objects_scope',[])),
		"individuals_1_scope":(json_config_input.get('individuals_1_scope',[])),
		"individuals_2_scope":(json_config_input.get('individuals_2_scope',[])),

		"symmetry":json_config_input.get('symmetry',True),

		"results_destination":json_config_input.get('results_destination',None)
	}


	description_attributes_objects=[{'name':x,'type':y} for x,y in json_config['description_attributes_objects']]
	description_attributes_individuals=[{'name':x,'type':y} for x,y in json_config['description_attributes_individuals']]
	algorithm=json_config['algorithm']
	if algorithm == 'DSC':
		bound_type=1
		pruning=False
		closed=False
		do_heuristic_contexts=False
		do_heuristic_peers=False
	elif algorithm == 'DSC+CLOSED':
		bound_type=1
		pruning=False
		closed=True
		do_heuristic_contexts=False
		do_heuristic_peers=False
	elif algorithm == 'DSC+CLOSED+UB1':
		bound_type=1
		pruning=True
		closed=True
		do_heuristic_contexts=False
		do_heuristic_peers=False
	elif algorithm == 'DSC+CLOSED+UB2':
		bound_type=2
		pruning=True
		closed=True
		do_heuristic_contexts=False
		do_heuristic_peers=False
	elif algorithm == 'DSC+RandomWalk':
		bound_type=2
		pruning=True
		closed=True
		do_heuristic_contexts=True
		do_heuristic_peers=True
	elif algorithm == 'DSC+SamplingPeers+RandomWalk':
		bound_type=2
		pruning=True
		closed=True
		do_heuristic_contexts=True
		do_heuristic_peers=True
	else:
		algorithm='DSC+CLOSED+UB2'
		bound_type=2
		pruning=True
		closed=True
		do_heuristic_contexts=False
		do_heuristic_peers=False

	for returned in Alpha_Entry_Point(json_config['objects_file'],json_config['individuals_file'],json_config['reviews_file'],
		numeric_attrs=json_config['numericHeader'],array_attrs=json_config['arrayHeader'],outcome_attrs=json_config['vector_of_outcome'],method_aggregation_outcome=json_config['aggregation_measure'],
		itemsScope=json_config['objects_scope'],users_1_Scope=json_config['individuals_1_scope'],users_2_Scope=json_config['individuals_2_scope'],delimiter=json_config['delimiter'],
		description_attributes_items=description_attributes_objects,description_attributes_users=description_attributes_individuals,
		comparaison_measure=json_config['similarity_measure'],qualityMeasure=json_config['quality_measure'],nb_items=json_config['nb_objects'],nb_individuals=json_config['nb_individuals'],
		threshold_comparaison=json_config['threshold_objects'],threshold_nb_users_1=json_config['threshold_individuals'],threshold_nb_users_2=json_config['threshold_individuals'],
		quality_threshold=json_config['threshold_quality'],ponderation_attribute=json_config['ponderation_attribute'],
		bound_type=bound_type,pruning=pruning,closed=closed,
		do_heuristic_contexts=do_heuristic_contexts,do_heuristic_peers=do_heuristic_peers,timebudget=json_config['timebudget'],results_destination=json_config['results_destination'],attributes_to_consider=json_config['attributes_to_consider'],heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,symmetry=json_config['symmetry'],verbose=verbose):




		#take as an input a json and either do a qualitative experiments or quantitatvie experiments
		#Consider three algorithm (exhaustive search algorithm) baseline(closed=False,Pruning=False), DSC+CLOSED(closed=True,Pruning=False), DSC+CLOSED+UB1(closed=True,Pruning=True,bound_type=1),DSC+CLOSED+UB2(closed=True,Pruning=True,bound_type=2),
		#Consider after ward the comparison between the random walk and the exhaustive search algorithm with several timebudget
		#Once this is done we can launch the Experiments

		#We need to prepare the dataset EPD8, EPD7, EPD78 and EPD678
		Alpha_input_config.stats=Alpha_Entry_Point.stats
		Alpha_input_config.stats['algorithm']=algorithm
		if heatmap_for_matrix:
			Alpha_input_config.outcomeTrack=Alpha_Entry_Point.outcomeTrack
		Alpha_input_config.types_attributes_items=Alpha_Entry_Point.types_attributes_items
		Alpha_input_config.types_attributes_users=Alpha_Entry_Point.types_attributes_users
		return returned





testas={
	'A':{6:3,7:4,8:1,9:2,10:1,11:1,12:3,13:3,15:3},
	'B':{1:1,3:2,4:1,5:3,6:3,7:4,8:3},
	'C':{3:2,4:1,5:3,6:4,7:4,9:2,10:1,11:1,12:3,13:3,15:4}
}

# def coincidence_matrix(all_users_to_items_outcomes,items_set=None,individuals_set=None):
# 	all_users_to_items_outcomes=testas
# 	individuals_set=all_users_to_items_outcomes.keys()
	

# 	matrix={}
# 	sums={}
# 	m_u={}


# 	sums={}
# 	for i_1 in individuals_set:
# 		for e in all_users_to_items_outcomes[i_1]:
# 			casted=all_users_to_items_outcomes[i_1][e]
# 			if casted not in sums:
# 				sums[casted]={}
# 			if e not in sums[casted]:
# 				sums[casted][e]=0
# 			sums[casted][e]+=1

# 	individuals_set_sorted=sorted(individuals_set)
# 	for i_1 in individuals_set_sorted:
# 		print i_1
# 		i_1_votes=all_users_to_items_outcomes[i_1]
# 		for i_2 in individuals_set_sorted:
# 			if i_1==i_2:
# 				continue
# 			i_2_votes=all_users_to_items_outcomes[i_2]
# 			for e in i_1_votes.viewkeys() & i_2_votes.viewkeys():
# 				i_1_casted=i_1_votes[e]
# 				i_2_casted=i_2_votes[e]
# 				#print i_1,i_2,e,i_1_votes[e][0],i_2_votes[e][0]
# 				if i_1_casted not in sums:
# 					sums[i_1_casted]=0
# 				if i_1_casted not in matrix:
# 					matrix[i_1_casted]={}
# 				if i_2_casted not in matrix[i_1_casted]:
# 					matrix[i_1_casted][i_2_casted]={}
				
# 				if e not in matrix[i_1_casted][i_2_casted]:
# 					matrix[i_1_casted][i_2_casted][e]=0
# 				if e not in m_u:
# 					m_u[e]=set()

# 				# if e ==3721:
					
# 				# 	if i_1_casted=='For' and i_2_casted=='For':
# 				# 		print i_1_casted,i_2_casted,i_1,i_2
# 				# 		print all_users_to_items_outcomes[i_1][e]
# 				# 		print all_users_to_items_outcomes[i_2][e]
# 				# 		raw_input('...')
# 				matrix[i_1_casted][i_2_casted][e]+=1
# 				m_u[e]|={i_1,i_2}


# 				#sums[i_1_casted]+=1
# 				#matrix[i_1_casted][i_2_casted]+=1
# 	print matrix
# 	for k in sorted(m_u):
# 		print k,m_u[k]
	
# 	sums={x:{t1:y[t1] for t1 in y.viewkeys()&m_u.viewkeys()} for x,y in sums.iteritems()}

# 	print sums
# 	individuals_for_each_entitiy=m_u
# 	nb_votes_casted_by_outcome=sums
# 	#raw_input('....')
# 	return matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome

def coincidence_matrix(all_users_to_items_outcomes,items_set=None,individuals_set=None):
	# all_users_to_items_outcomes=testas
	# individuals_set=all_users_to_items_outcomes.keys()
	
	individuals_set=all_users_to_items_outcomes.keys() if individuals_set is None else individuals_set

	# for u in individuals_set:
	# 	votings_u=all_users_to_items_outcomes[u]
	# 	items_set=votings_u.keys() if items_set is None else items_set
	# 	for i in items_set:
	# 		vote_casted=votings_u[i]
	# 		print vote_casted
	# 		raw_input('....')

	matrix={}
	matrix_by_e={}
	sums={}
	m_u={}


	sums={}
	for i_1 in individuals_set:
		for e in all_users_to_items_outcomes[i_1]:
			casted=all_users_to_items_outcomes[i_1][e][0]
			if casted not in sums:
				sums[casted]={}
			if e not in sums[casted]:
				sums[casted][e]=0
			sums[casted][e]+=1

	individuals_set_sorted=sorted(individuals_set)
	for i_1 in individuals_set_sorted:
		print i_1
		i_1_votes=all_users_to_items_outcomes[i_1]
		for i_2 in individuals_set_sorted:
			if i_1==i_2:
				continue
			i_2_votes=all_users_to_items_outcomes[i_2]
			for e in i_1_votes.viewkeys() & i_2_votes.viewkeys():
				if e not in matrix_by_e:
					matrix_by_e[e]={}
				i_1_casted=i_1_votes[e][0]
				i_2_casted=i_2_votes[e][0]
				#print i_1,i_2,e,i_1_votes[e][0],i_2_votes[e][0]
				if i_1_casted not in sums:
					sums[i_1_casted]=0
				if i_1_casted not in matrix:
					matrix[i_1_casted]={}
				if i_2_casted not in matrix[i_1_casted]:
					matrix[i_1_casted][i_2_casted]={}
				
				if e not in matrix[i_1_casted][i_2_casted]:
					matrix[i_1_casted][i_2_casted][e]=0
				
				#matrix_by_e[e][tuple(sorted((i_1_casted,i_2_casted)))]=matrix_by_e[e].get(tuple(sorted((i_1_casted,i_2_casted))),0)+1
				matrix_by_e[e]['_'.join(sorted((i_1_casted,i_2_casted)))]=matrix_by_e[e].get('_'.join(sorted((i_1_casted,i_2_casted))),0)+1
				

				if e not in m_u:
					m_u[e]=set()

				# if e ==3721:
					
				# 	if i_1_casted=='For' and i_2_casted=='For':
				# 		print i_1_casted,i_2_casted,i_1,i_2
				# 		print all_users_to_items_outcomes[i_1][e]
				# 		print all_users_to_items_outcomes[i_2][e]
				# 		raw_input('...')
				matrix[i_1_casted][i_2_casted][e]+=1
				m_u[e]|={i_1,i_2}


				#sums[i_1_casted]+=1
				#matrix[i_1_casted][i_2_casted]+=1
	sums={x:{t1:y[t1] for t1 in y.viewkeys()&m_u.viewkeys()} for x,y in sums.iteritems()}
	individuals_for_each_entitiy=m_u
	nb_votes_casted_by_outcome=sums
	for e in matrix_by_e:
		
		sum_now=float(sum(matrix_by_e[e].values()))
		for e_v in matrix_by_e[e]:
			matrix_by_e[e][e_v]=matrix_by_e[e][e_v]/sum_now
		#matrix_by_e[e]['SUM']=sum_now
		# print matrix_by_e[e]
		# print len(individuals_for_each_entitiy[e])
		# raw_input('....')
	return matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome

	
def compute_cohesion_old(all_users_to_items_outcomes,items_set,individuals_set):
	
	build_vector={};
	for u in individuals_set:
		all_users_to_items_outcomes_u=all_users_to_items_outcomes[u]
		for i in items_set& all_users_to_items_outcomes_u.viewkeys():
			vote=all_users_to_items_outcomes_u[i][0]
			try:
				build_vector[vote]+=1
			except Exception as e:
				build_vector[vote]=1
	vecotrish=tuple(build_vector.values())
	if len(vecotrish)==1:
		vecotrish=tuple(list(vecotrish)+[0.,0.])
	elif len(vecotrish)==2:
		vecotrish=tuple(list(vecotrish)+[0.])



	v1_norm_sum=float(sum(vecotrish[index] for index in range(3)))
	v1_normalized=tuple(vecotrish[index]/v1_norm_sum for index in range(3))
	similarity+=(3*max(v1_normalized)-1)/2.
	print similarity,vecotrish
	return similarity

def compute_cohesion(all_users_to_items_outcomes,items_set,individuals_set):
	
	all_vector={}
	similarity=0.
	nb=len(items_set)
	for i in items_set:
		build_vector={};
		for u in individuals_set:
			all_users_to_items_outcomes_u=all_users_to_items_outcomes[u]
			try:
				vote=all_users_to_items_outcomes_u[i][0]
			except Exception as e:
				continue
			try:
				build_vector[vote]+=1
			except Exception as e:
				build_vector[vote]=1

			try:
				all_vector[vote]+=1
			except Exception as e:
				all_vector[vote]=1
				
		if len(build_vector)>0:
			vecotrish=tuple(build_vector.values())
			if len(vecotrish)==1:
				vecotrish=tuple(list(vecotrish)+[0.,0.])
			elif len(vecotrish)==2:
				vecotrish=tuple(list(vecotrish)+[0.])
			v1_norm_sum=float(sum(vecotrish[index] for index in range(3)))
			v1_normalized=tuple(vecotrish[index]/v1_norm_sum for index in range(3))
			similarity+=(3*max(v1_normalized)-1)/2.
		else:
			nb-=1

	
	



	
	
	return similarity/nb,[all_vector[k] for k in sorted(all_vector)]
			

	

def distance_nominal(o1,o2):
	return int(o1!=o2)

def distance_numerical(o1,o2):
	return float((o1-o2)**2)

def compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal,nb_votes_casted_by_outcome_sums=None):
	m_u={k:float(len(v)) for k,v in individuals_for_each_entitiy.iteritems()}
	factor=1.
	if nb_votes_casted_by_outcome_sums is None:
		nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in set_of_entities&items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
		
	else:
		nb_votes_casted_by_outcome_sums_for_factor={casted:sum(items[k] for k in set_of_entities&items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
		comparable_pairs_number_tmp=(float(sum(nb_votes_casted_by_outcome_sums_for_factor.values()))-1)
		comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
		factor=(comparable_pairs_number_tmp/comparable_pairs_number)
		
		#print comparable_pairs_number,comparable_pairs_number_tmp,factor,(comparable_pairs_number*factor),len(set_of_entities)/4109.
		#factor=len(set_of_entities)/4109.
	new_matrix={k:{k_2:0. for k_2 in matrix} for k in matrix}
	expected={k:{k_2:0. for k_2 in matrix} for k in matrix}
	comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
	for c_1 in matrix:
		for c_2 in matrix:
			if c_2 in matrix[c_1]:
				matrix_c1_c2=matrix[c_1][c_2]
				n_cc=sum(matrix_c1_c2[k]/(m_u[k]-1) for k in matrix_c1_c2.viewkeys()&set_of_entities)
				new_matrix[c_1][c_2]=n_cc
			#expected[c_1][c_2]=(nb_votes_casted_by_outcome_sums[c_1]*nb_votes_casted_by_outcome_sums[c_2])/(float(sum(nb_votes_casted_by_outcome_sums.values()))-1) if c_1!=c_2 else (nb_votes_casted_by_outcome_sums[c_1]*(nb_votes_casted_by_outcome_sums[c_2]-1))/(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
			expected[c_1][c_2]=(((nb_votes_casted_by_outcome_sums[c_1]*factor)*(nb_votes_casted_by_outcome_sums[c_2]*factor))/(comparable_pairs_number*factor)) if c_1!=c_2 else (((nb_votes_casted_by_outcome_sums[c_1]*factor)*((nb_votes_casted_by_outcome_sums[c_2]-1.)*factor))/(comparable_pairs_number*factor))
	disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
	disagreement_expected=(sum(expected[v1][v2]*distance_function(v1,v2) for v1 in expected for v2 in expected[v1] if v2>=v1))
	
	return 1. - (disagreement_observed/disagreement_expected),nb_votes_casted_by_outcome_sums


def compute_reliability_with_bootstraping(matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal):
	NB_BOOTSTRAP=10000
	returned=[]


	m_u={k:float(len(v)) for k,v in individuals_for_each_entitiy.iteritems()}
	factor=1.
	nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in set_of_entities&items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
	expected={k:{k_2:0. for k_2 in matrix} for k in matrix}
	comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
	for c_1 in expected:
		for c_2 in expected:
			expected[c_1][c_2]=(((nb_votes_casted_by_outcome_sums[c_1])*(nb_votes_casted_by_outcome_sums[c_2]))/(comparable_pairs_number)) if c_1!=c_2 else (((nb_votes_casted_by_outcome_sums[c_1])*((nb_votes_casted_by_outcome_sums[c_2]-1.)))/(comparable_pairs_number))
	
	disagreement_expected=(sum(expected[v1][v2]*distance_function(v1,v2) for v1 in expected for v2 in expected[v1] if v2>=v1))
	

	list_of_unities=sorted(matrix_by_e)
	for x in xrange(NB_BOOTSTRAP):
		new_matrix={k:{k_2:0. for k_2 in matrix} for k in matrix}
		nb_iterations=0.

		for sampling_unit_draw in xrange(len(list_of_unities)):
			random_unit=list_of_unities[randint(0,len(list_of_unities)-1)] #http://inter-rater-reliability.blogspot.fr/2015/08/standard-error-of-krippendorffs-alpha.html
			#random_unit=list_of_unities[sampling_unit_draw] #http://web.asc.upenn.edu/usr/krippendorff/boot.c-Alpha.pdf
			####
			# What Kilem L. Gwet Recommends is to generate first randomly n unities from the units set than taking the istinct unit selectng then a subset of the original table 
			# Following by computing the Disagreement expected only on the subset of the table and then compute the disagreement observed which is more correct according to Kilem L. Gwet 
			# and Eforn & Tibshirani for the estimation of the confidence interval with bootstraping
			####
			random_unit_couples_proba=matrix_by_e[random_unit]
			random_unit_couples_proba_items=random_unit_couples_proba.items()
			list_of_candidates=map(itemgetter(0),random_unit_couples_proba_items)
			probability_distribution=map(itemgetter(1),random_unit_couples_proba_items)
			

			# for cand,prob in random_unit_couples_proba.items():
			# 	if cand=='SUM':
			# 		continue
			# 	list_of_candidates.append('_'.join(cand))
			# 	probability_distribution.append(prob)
			nb_draw_by_unit=((m_u[random_unit]-1)*(m_u[random_unit]))/2.
			nb_iterations+=nb_draw_by_unit


			for c1_c2 in choice(list_of_candidates, int(nb_draw_by_unit), p=probability_distribution):
				c1,c2=c1_c2.split('_')
				new_matrix[c1][c2]+=1/float(m_u[random_unit]-1)
				new_matrix[c2][c1]+=1/float(m_u[random_unit]-1)
		disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
		
		alpha_bootstrap=1. - (disagreement_observed/disagreement_expected)
		print alpha_bootstrap,nb_iterations
		
	return returned

	



def compute_reliability_with_bootstraping_KILEM_GWET_BLB(matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal):
	NB_BOOTSTRAP=3
	returned=[]
	bootstrap_small_subset=False
	BLB_bag_little_bootsraps=False
	old_calculation=False
	factor=1.
	m_u={k:float(len(v)) for k,v in individuals_for_each_entitiy.iteritems()}


	
	list_of_unities=sorted(matrix_by_e)
	estimating=[]
	#for x in xrange(NB_BOOTSTRAP):
		
		
	nb_iterations=0.
	constituted_sample_unit_set=set()
	nb_samples_unit=len(list_of_unities)

	constituted_sample_unit=[]
	
	for x in xrange(NB_BOOTSTRAP):
		selected_batch_for_now=choice(list_of_unities, int(nb_samples_unit**0.7), replace=False).tolist()
		#print selected_batch_for_now
		one_blb=[]
		for constituted_sample_unit in multinomial(int(nb_samples_unit), [1./len(selected_batch_for_now)]*len(selected_batch_for_now),50):
			# print constituted_sample_unit,sum(constituted_sample_unit)
			# raw_input('...')
			nb_votes_casted_by_outcome_sums={casted:sum(items[selected_batch_for_now[k]]*nb for k,nb in enumerate(constituted_sample_unit) if selected_batch_for_now[k] in items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
			expected={k:{k_2:0. for k_2 in matrix} for k in matrix}
			comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
			for c_1 in expected:
				for c_2 in expected:
					expected[c_1][c_2]=(((nb_votes_casted_by_outcome_sums[c_1])*(nb_votes_casted_by_outcome_sums[c_2]))/(comparable_pairs_number)) if c_1!=c_2 else (((nb_votes_casted_by_outcome_sums[c_1])*((nb_votes_casted_by_outcome_sums[c_2]-1.)))/(comparable_pairs_number))
			
			disagreement_expected=(sum(expected[v1][v2]*distance_function(v1,v2) for v1 in expected for v2 in expected[v1] if v2>=v1))
			

			#for x in xrange(100): 

			new_matrix={k:{k_2:0. for k_2 in matrix} for k in matrix}
			for random_unit,nb in enumerate(constituted_sample_unit):
				random_unit=selected_batch_for_now[random_unit]
				random_unit_couples_proba=matrix_by_e[random_unit]
				random_unit_couples_proba_items=random_unit_couples_proba.items()
				list_of_candidates=map(itemgetter(0),random_unit_couples_proba_items)
				probability_distribution=map(itemgetter(1),random_unit_couples_proba_items)
				nb_draw_by_unit=(((m_u[random_unit]-1)*(m_u[random_unit]))/2.)*nb
				nb_iterations+=nb_draw_by_unit
				generated_stuffs=[(tuple(list_of_candidates[i].split('_')),float(j))for i,j in enumerate(multinomial(int(nb_draw_by_unit), probability_distribution))]
				for (c1,c2),v in generated_stuffs:
					new_matrix[c1][c2]+=v/float(m_u[random_unit]-1)
					new_matrix[c2][c1]+=v/float(m_u[random_unit]-1)
			disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
			alpha_bootstrap=1. - (disagreement_observed/disagreement_expected)
			one_blb.append(alpha_bootstrap)
		

		one_blb=sorted(one_blb)
		estimating.append([(2)*(sum(one_blb)/float(len(one_blb)))-one_blb[int(len(one_blb)*0.975)],(2)*(sum(one_blb)/float(len(one_blb)))-one_blb[int(len(one_blb)*0.025)]])
		#print one_blb[int(len(one_blb)*0.025)],one_blb[int(len(one_blb)*0.975)]
		print estimating[-1]
	print sum(x[0] for x in estimating)/float(len(estimating)),sum(x[1] for x in estimating)/float(len(estimating))
		#raw_input('....')

			# for sampling_unit_draw in xrange(nb_samples_unit): 
			# 	random_unit=constituted_sample_unit_set_tmp[randint(0,len(constituted_sample_unit_set_tmp)-1)]
			# 	constituted_sample_unit.append(random_unit)
		
		#nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in constituted_sample_unit_set & items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
		
		
		
		

	# 	for random_unit in constituted_sample_unit:

	# 		random_unit_couples_proba=matrix_by_e[random_unit]
	# 		random_unit_couples_proba_items=random_unit_couples_proba.items()
	# 		list_of_candidates=map(itemgetter(0),random_unit_couples_proba_items)
	# 		probability_distribution=map(itemgetter(1),random_unit_couples_proba_items)
	# 		nb_draw_by_unit=((m_u[random_unit]-1)*(m_u[random_unit]))/2.
	# 		nb_iterations+=nb_draw_by_unit

	# 		if old_calculation:
	# 			for c1_c2 in choice(list_of_candidates, int(nb_draw_by_unit), p=probability_distribution):
	# 				c1,c2=c1_c2.split('_')
	# 				new_matrix[c1][c2]+=1/float(m_u[random_unit]-1)
	# 				new_matrix[c2][c1]+=1/float(m_u[random_unit]-1)
	# 		else:
	# 			generated_stuffs=[(tuple(list_of_candidates[i].split('_')),float(j))for i,j in enumerate(multinomial(int(nb_draw_by_unit), probability_distribution))]
	# 			for (c1,c2),v in generated_stuffs:
	# 				new_matrix[c1][c2]+=v/float(m_u[random_unit]-1)
	# 				new_matrix[c2][c1]+=v/float(m_u[random_unit]-1)
		
	# 	disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
		
	# 	if bootstrap_small_subset:
	# 		factor=comparable_pairs_number/float(full_nb_comparable_pairs)
	# 		disagreement_expected_original_full=(sum(expected_original[v1][v2]*factor*distance_function(v1,v2) for v1 in expected_original for v2 in expected_original[v1] if v2>=v1))
	# 		alpha_bootstrap=1. - (disagreement_observed/disagreement_expected_original_full)
	# 	else:
	# 		alpha_bootstrap=1. - (disagreement_observed/disagreement_expected)
	# 	print alpha_bootstrap,nb_iterations
	# 	returned.append(alpha_bootstrap)

	# 	returned_sorted=sorted(returned)
	# print returned_sorted[int(len(returned_sorted)*0.025)],returned_sorted[int(len(returned_sorted)*0.975)]
	# print [(2)*(sum(returned_sorted)/float(len(returned_sorted)))-returned_sorted[int(len(returned_sorted)*0.975)],(2)*(sum(returned_sorted)/float(len(returned_sorted)))-returned_sorted[int(len(returned_sorted)*0.025)]]
	return returned




def compute_reliability_with_bootstraping_KILEM_GWET(matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal):
	NB_BOOTSTRAP=1000
	returned=[]
	bootstrap_small_subset=False
	BLB_bag_little_bootsraps=False
	old_calculation=False
	factor=1.
	m_u={k:float(len(v)) for k,v in individuals_for_each_entitiy.iteritems()}
	
	if bootstrap_small_subset:
		
		nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in set_of_entities&items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
		expected_original={k:{k_2:0. for k_2 in matrix} for k in matrix}
		comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
		for c_1 in expected_original:
			for c_2 in expected_original:
				expected_original[c_1][c_2]=(((nb_votes_casted_by_outcome_sums[c_1])*(nb_votes_casted_by_outcome_sums[c_2]))/(comparable_pairs_number)) if c_1!=c_2 else (((nb_votes_casted_by_outcome_sums[c_1])*((nb_votes_casted_by_outcome_sums[c_2]-1.)))/(comparable_pairs_number))
		
		
		full_nb_comparable_pairs=comparable_pairs_number

	
	list_of_unities=sorted(matrix_by_e)
	for x in xrange(NB_BOOTSTRAP):
		PROFILING=False
		if PROFILING:
			pr = cProfile.Profile()
			pr.enable()
		new_matrix={k:{k_2:0. for k_2 in matrix} for k in matrix}
		nb_iterations=0.
		constituted_sample_unit_set=set()
		if bootstrap_small_subset:
			nb_samples_unit=64#len(list_of_unities)
		else:
			nb_samples_unit=len(list_of_unities)

		constituted_sample_unit=[]
		
		if not BLB_bag_little_bootsraps:
			

			
			for sampling_unit_draw in xrange(nb_samples_unit):
				random_unit=list_of_unities[randint(0,len(list_of_unities)-1)] #http://inter-rater-reliability.blogspot.fr/2015/08/standard-error-of-krippendorffs-alpha.html
				constituted_sample_unit.append(random_unit)
				#constituted_sample_unit_set|={random_unit}
		else:
			
			
			# constituted_sample_unit_set_tmp=constituted_sample_unit_set
			# for sampling_unit_draw in xrange(int(nb_samples_unit**0.5)):
			# 	random_unit=list_of_unities[randint(0,len(list_of_unities)-1)] #http://inter-rater-reliability.blogspot.fr/2015/08/standard-error-of-krippendorffs-alpha.html
			# 	#constituted_sample_unit.append(random_unit)
			# 	constituted_sample_unit_set_tmp|={random_unit}
				
			# #choice(range(nb_samples_unit), nb_samples_unit**0.5, replace=False)
			constituted_sample_unit_set_tmp=choice(list_of_unities, int(nb_samples_unit**0.5), replace=False).tolist()

			#constituted_sample_unit_set_tmp=sorted(constituted_sample_unit_set_tmp)
			
			for sampling_unit_draw in xrange(int(nb_samples_unit)): 
				random_unit=constituted_sample_unit_set_tmp[randint(0,len(constituted_sample_unit_set_tmp)-1)]
				constituted_sample_unit.append(random_unit)
			#constituted_sample_unit=sorted(constituted_sample_unit_set)
			#random_unit=list_of_unities[sampling_unit_draw] #http://web.asc.upenn.edu/usr/krippendorff/boot.c-Alpha.pdf
			####
			# What Kilem L. Gwet Recommends is to generate first randomly n unities from the units set than taking the istinct unit selectng then a subset of the original table 
			# Following by computing the Disagreement expected only on the subset of the table and then compute the disagreement observed which is more correct according to Kilem L. Gwet 
			# and Eforn & Tibshirani for the estimation of the confidence interval with bootstraping
			####
		
		
		#nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in constituted_sample_unit_set & items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
		nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in constituted_sample_unit if k in items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
		expected={k:{k_2:0. for k_2 in matrix} for k in matrix}
		comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
		for c_1 in expected:
			for c_2 in expected:
				expected[c_1][c_2]=(((nb_votes_casted_by_outcome_sums[c_1])*(nb_votes_casted_by_outcome_sums[c_2]))/(comparable_pairs_number)) if c_1!=c_2 else (((nb_votes_casted_by_outcome_sums[c_1])*((nb_votes_casted_by_outcome_sums[c_2]-1.)))/(comparable_pairs_number))
		
		disagreement_expected=(sum(expected[v1][v2]*distance_function(v1,v2) for v1 in expected for v2 in expected[v1] if v2>=v1))

		for random_unit in constituted_sample_unit:

			random_unit_couples_proba=matrix_by_e[random_unit]
			random_unit_couples_proba_items=random_unit_couples_proba.items()
			list_of_candidates=map(itemgetter(0),random_unit_couples_proba_items)
			probability_distribution=map(itemgetter(1),random_unit_couples_proba_items)
			nb_draw_by_unit=((m_u[random_unit]-1)*(m_u[random_unit]))/2.
			nb_iterations+=nb_draw_by_unit

			if old_calculation:
				for c1_c2 in choice(list_of_candidates, int(nb_draw_by_unit), p=probability_distribution):
					c1,c2=c1_c2.split('_')
					new_matrix[c1][c2]+=1/float(m_u[random_unit]-1)
					new_matrix[c2][c1]+=1/float(m_u[random_unit]-1)
			else:
				generated_stuffs=[(tuple(list_of_candidates[i].split('_')),float(j))for i,j in enumerate(multinomial(int(nb_draw_by_unit), probability_distribution))]
				for (c1,c2),v in generated_stuffs:
					new_matrix[c1][c2]+=v/float(m_u[random_unit]-1)
					new_matrix[c2][c1]+=v/float(m_u[random_unit]-1)
		
		disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
		
		if bootstrap_small_subset:
			factor=comparable_pairs_number/float(full_nb_comparable_pairs)
			disagreement_expected_original_full=(sum(expected_original[v1][v2]*factor*distance_function(v1,v2) for v1 in expected_original for v2 in expected_original[v1] if v2>=v1))
			alpha_bootstrap=1. - (disagreement_observed/disagreement_expected_original_full)
		else:
			alpha_bootstrap=1. - (disagreement_observed/disagreement_expected)
		print alpha_bootstrap,nb_iterations
		returned.append(alpha_bootstrap)
		if PROFILING:
			pr.disable()
			ps = pstats.Stats(pr)
			ps.sort_stats('cumulative').print_stats(20) #time
			raw_input('.....')
		returned_sorted=sorted(returned)
	print returned_sorted[int(len(returned_sorted)*0.025)],returned_sorted[int(len(returned_sorted)*0.975)]
	print [(2)*(sum(returned_sorted)/float(len(returned_sorted)))-returned_sorted[int(len(returned_sorted)*0.975)],(2)*(sum(returned_sorted)/float(len(returned_sorted)))-returned_sorted[int(len(returned_sorted)*0.025)]]
	return returned


def compute_reliability_NEW(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal,nb_votes_casted_by_outcome_sums=None):
	m_u={k:float(len(v)) for k,v in individuals_for_each_entitiy.iteritems()}
	factor=1.
	

	nb_votes_casted_by_outcome_sums_for_factor={casted:sum(items[k] for k in set_of_entities&items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
	comparable_pairs_number_tmp=(float(sum(nb_votes_casted_by_outcome_sums_for_factor.values()))-1)
	comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
	factor=(comparable_pairs_number_tmp/comparable_pairs_number)
		
		#print comparable_pairs_number,comparable_pairs_number_tmp,factor,(comparable_pairs_number*factor),len(set_of_entities)/4109.
		#factor=len(set_of_entities)/4109.

	 
	#print nb_votes_casted_by_outcome_sums_tmp,nb_votes_casted_by_outcome_sums
	

	new_matrix={k:{k_2:0. for k_2 in matrix} for k in matrix}
	new_matrix_general={k:{k_2:0. for k_2 in matrix} for k in matrix}
	expected={k:{k_2:0. for k_2 in matrix} for k in matrix}
	comparable_pairs_number=(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)
	for c_1 in matrix:
		for c_2 in matrix:
			if c_2 in matrix[c_1]:
				matrix_c1_c2=matrix[c_1][c_2]
				n_cc=sum(matrix_c1_c2[k]/(m_u[k]-1) for k in matrix_c1_c2.viewkeys()&set_of_entities)
				new_matrix[c_1][c_2]=n_cc
				g_cc=sum(matrix_c1_c2[k]/(m_u[k]-1) for k in matrix_c1_c2.viewkeys())
				new_matrix_general[c_1][c_2]=g_cc

	disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
	
	disagreement_expected=(sum(new_matrix_general[v1][v2]*distance_function(v1,v2) for v1 in new_matrix_general for v2 in new_matrix_general[v1] if v2>=v1))*factor



	return 1. - (disagreement_observed/disagreement_expected),nb_votes_casted_by_outcome_sums


def compute_reliability_numeric(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities):
	m_u={k:float(len(v)) for k,v in individuals_for_each_entitiy.iteritems()}
	nb_votes_casted_by_outcome_sums={casted:sum(items[k] for k in set_of_entities&items.viewkeys()) for casted,items in  nb_votes_casted_by_outcome.iteritems()}
	new_matrix={k:{k_2:0. for k_2 in matrix} for k in matrix}
	expected={k:{k_2:0. for k_2 in matrix} for k in matrix}
	for c_1 in matrix:
		for c_2 in matrix:
			matrix_c1_c2=matrix[c_1][c_2]
			n_cc=sum(matrix_c1_c2[k]/(m_u[k]-1) for k in matrix_c1_c2.viewkeys()&set_of_entities)
			new_matrix[c_1][c_2]=n_cc
			expected[c_1][c_2]=(nb_votes_casted_by_outcome_sums[c_1]*nb_votes_casted_by_outcome_sums[c_2])/(float(sum(nb_votes_casted_by_outcome_sums.values()))-1) if c_1!=c_2 else (nb_votes_casted_by_outcome_sums[c_1]*(nb_votes_casted_by_outcome_sums[c_2]-1))/(float(sum(nb_votes_casted_by_outcome_sums.values()))-1)

	# print new_matrix
	# print expected
	# print nb_votes_casted_by_outcome
	return 1. - ((sum(new_matrix[v1][v2]*((v1-v2)**2) for v1 in new_matrix for v2 in new_matrix[v1]))/(sum(expected[v1][v2]*((v1-v2)**2) for v1 in expected for v2 in expected[v1])))




# DSC_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=[],array_attrs=None,outcome_attrs=None,method_aggregation_outcome='VECTOR_VALUES',itemsScope=[],users_1_Scope=[],users_2_Scope=[],delimiter='\t',
# 	description_attributes_items=[],description_attributes_users=[],
# 	comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',nb_items=float('inf'),nb_individuals=float('inf'),threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
# 	ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,results_destination='.//results.csv',attributes_to_consider=None,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',nb_items_entities=float('inf'),nb_items_individuals=float('inf'),symmetry=True,nb_random_walks=30,hmt_to_itemset=False,debug=False,verbose=False):

# def Alpha_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=[],array_attrs=None,outcome_attrs=None,method_aggregation_outcome='VECTOR_VALUES',itemsScope=[],users_1_Scope=[],users_2_Scope=[],delimiter='\t',
# 	description_attributes_items=[],description_attributes_users=[],
# 	comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',nb_items=float('inf'),nb_individuals=float('inf'),threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
# 	ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,results_destination='.//results.csv',attributes_to_consider=None,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',symmetry=True,debug=False,verbose=False):
	
from measures.similaritiesDCS import similarity_vector_measure_dcs

def similarity_dictionnary(all_users_to_items_outcomes,users_set,entities_set):
	ret={}
	sorted_users=sorted(users_set)
	
	for u1 in sorted_users:
		ret[u1]={}
		for u2 in sorted_users:
			sim_u1_u2=0.
			nb_u1_u2=0.
			for e in entities_set& all_users_to_items_outcomes[u1].viewkeys()&all_users_to_items_outcomes[u2].viewkeys():
				sim_u1_u2+=int(all_users_to_items_outcomes[u1][e][0]==all_users_to_items_outcomes[u2][e][0])
				nb_u1_u2+=1
			ret[u1][u2]=sim_u1_u2/float(nb_u1_u2) if nb_u1_u2>0 else float('NaN')
	return ret

def reorganize_similarly(origin,dest):

	innerMatrix,rower,header=getInnerMatrix(origin)
	rower=[rower[r] for r in sorted(rower)]
	header=[header[r] for r in sorted(header)]
	rower_inv={v:key for key,v in enumerate(rower)}
	header_inv={v:key for key,v in enumerate(header)}

	innerMatrix_ref,rower_ref,header_ref=getInnerMatrix(dest)
	rower_ref=[rower_ref[r] for r in sorted(rower_ref)]
	header_ref=[header_ref[r] for r in sorted(header_ref)]
	rower_ref_inv={v:key for key,v in enumerate(rower_ref)}
	header_ref_inv={v:key for key,v in enumerate(header_ref)}

	
	new_inner_matrix=[[innerMatrix_ref[rower_ref_inv[rowVal]][header_ref_inv[headVal]] for headVal in header] for rowVal in rower]
	dest=getCompleteMatrix(new_inner_matrix,{xx:yy for xx,yy in enumerate(rower)},{xx:yy for xx,yy in enumerate(header)})
	
	
	return origin,dest


def Alpha_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=[],array_attrs=None,outcome_attrs=None,method_aggregation_outcome='VECTOR_VALUES',itemsScope=[],users_1_Scope=[],users_2_Scope=[],delimiter='\t',
	description_attributes_items=[],description_attributes_users=[],
	comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',nb_items=float('inf'),nb_individuals=float('inf'),threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
	ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,results_destination='.//results.csv',attributes_to_consider=None,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',nb_items_entities=float('inf'),nb_items_individuals=float('inf'),symmetry=True,nb_random_walks=30,hmt_to_itemset=False,debug=False,verbose=False):
	
	import pickle
	method_aggregation_outcome='SYMBOLIC_MAJORITY'
	inited=time()
	
	# try:
	# 	with open ('.//TMP.tmp', 'rb') as fp:
	# 		items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered=pickle.load(fp)
	# except Exception as e:
	print 'computing from zero'
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered =\
	process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,delimiter=delimiter)
	# with open('.//TMP.tmp', 'wb') as fp:
	# 	pickle.dump([items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered], fp)
	
	print considered_items_sorted[0]	
	
	if False:
		considered_items_sorted=[x for x in considered_items_sorted if x[items_id_attribute] not in {'0002','0012','0022','0032','0042','0052','0062','0072'}]
		print len(considered_items_sorted)
		#raw_input('...')
		desc_indiv=[{'dimensionName':'CIGARETTE','inSet':{'Je fume'}},{'dimensionName':'SEXE','inSet':{'M'}},{'dimensionName':'AGE','inInterval':[0,25]}][:1]
		groups_indiv,_=filter_pipeline_obj(considered_users_1_sorted,desc_indiv)
		print len(groups_indiv)
		groups_indiv=set(x[users_id_attribute] for x in groups_indiv)
		set_of_entities=set(x[items_id_attribute] for x in considered_items_sorted)
		all_users_to_items_outcomes={u:{x:y for x,y in v.iteritems() if x in set_of_entities} for u,v in all_users_to_items_outcomes.iteritems()}
		matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome=coincidence_matrix(all_users_to_items_outcomes,individuals_set=groups_indiv)
		
		
		full_reliability,full_sums_votes=compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_numerical)
		print 'reliablitiy',full_reliability

		

		enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, [{'name':'odors', 'type':'themes'}],threshold=1)	
		results=[]
		for e_p,e_label,e_config in enumerator_contexts:
			context_pat=pattern_printer(e_label,['themes'])
			items_context=set(x[items_id_attribute] for x in e_config['support'])

			try:
				context_reliablitiy,_=compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,items_context,distance_function=distance_numerical,nb_votes_casted_by_outcome_sums=full_sums_votes)
				print e_p,context_reliablitiy
				raw_input('......')
			except Exception as e:
				continue
			results.append([context_pat,context_reliablitiy,items_context])
		results=sorted(results,key=lambda x : x[1],reverse=False)
		to_ret=[]
		for elem in results:
			print elem[0],elem[1]
			to_ret.append({'pattern':elem[0],'reliability':elem[1]})
			#raw_input('...')
	#raw_input('...') 
		#to_ret=[]
	if True:
		frenchdeputies,_=filter_pipeline_obj(considered_users_1_sorted,[{'dimensionName':'COUNTRY','inSet':{'Greece'}}])#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}])#[{'dimensionName':'GROUPE_ID','inSet':{'ECR'}}]) #[{'dimensionName':'NATIONAL_PARTY','inSet':{'Parti socialiste'}}]
		frenchdeputies_metadata=sorted(frenchdeputies,key=lambda x:x[users_id_attribute]) #Parti socialiste
		for row in frenchdeputies_metadata:
			row['NATIONAL_PARTY']=unicodedata.normalize('NFD', unicode(str(row['NATIONAL_PARTY']),'iso-8859-1')).encode('ascii', 'ignore')
			row['NAME_FULL']=unicodedata.normalize('NFD', unicode(str(row['NAME_FULL']),'iso-8859-1')).encode('ascii', 'ignore')
		
		frenchdeputies=set(x[users_id_attribute] for x in frenchdeputies)

		print len(frenchdeputies)
		set_of_entities=set(x[items_id_attribute] for x in considered_items_sorted)
		#raw_input('...')
		#print considered_items_sorted[0]
		if True:
			print 'Starting filter'
			all_users_to_items_outcomes={u:{x:y for x,y in v.iteritems() if y[0]!='Abstain'} for u,v in all_users_to_items_outcomes.iteritems()}
			print 'Ending filter'
		#print 'cohesion',compute_cohesion(all_users_to_items_outcomes,set_of_entities,frenchdeputies)
		matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome=coincidence_matrix(all_users_to_items_outcomes,individuals_set=frenchdeputies)
		full_reliability,full_sums_votes=compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities)
		


		print 'reliablitiy',full_reliability
		


		#compute_reliability_with_bootstraping_KILEM_GWET(matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal)
		compute_reliability_with_bootstraping_KILEM_GWET_BLB(matrix_by_e,matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities,distance_function=distance_nominal)
		
		# for x,y,z in  enumerator_complex_from_dataset_new_config(considered_items_sorted, [{'name':'VOTEID', 'type':'nominal'}],threshold=5):
		# 	print x
		# 	raw_input('...')
			
		enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, [{'name':'PROCEDURE_SUBJECT', 'type':'themes'}],threshold=5)	
		results=[]
		index=0
		for e_p,e_label,e_config in enumerator_contexts:
			index+=1
			context_pat=pattern_printer(e_label,['themes'])
			items_context=set(x[items_id_attribute] for x in e_config['support'])

			#try:
			context_reliablitiy,_=compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,items_context,nb_votes_casted_by_outcome_sums=full_sums_votes)
			my_reliability,_=compute_reliability_NEW(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,items_context,nb_votes_casted_by_outcome_sums=full_sums_votes)
			
			cohesion,vector_full=compute_cohesion(all_users_to_items_outcomes,items_context,frenchdeputies)
			if context_reliablitiy>0.85 and False:
				from heatmap.heatmap import generateHeatMap
				from clusters.hierarchicalClustering import drawDendrogramme,applyHierarchiqueClusteringFromDataset,hierarchicalClusteringFromDataset
				print context_reliablitiy
				

				ref_matrix=similarity_dictionnary(all_users_to_items_outcomes,frenchdeputies,set_of_entities)
				rower=[x['NATIONAL_PARTY']+'_'+x['NAME_FULL']+'_'+str(x[users_id_attribute]) for x in frenchdeputies_metadata]
				head=[['']]+rower
				ref_matrix_array=[[ref_matrix[u1][u2] if u1<u2 else ref_matrix[u2][u1] if u1>u2 else float(1.)  for u2 in sorted(ref_matrix)] for u1 in sorted(ref_matrix)]
				for k in range(len(ref_matrix_array)):
					ref_matrix_array[k].insert(0,rower[k])
				ref_matrix_array.insert(0,head)
				#ref_matrix_array_after_reorganizing=generateHeatMap(sim_matrix_array,'./Figures/REF_heatmap_'+str(index)+'.png',vmin=0.,vmax=1.,showvalues_text=False,only_heatmap=True,organize=True)



				sim_matrix=similarity_dictionnary(all_users_to_items_outcomes,frenchdeputies,items_context)
				rower=[x['NATIONAL_PARTY']+'_'+x['NAME_FULL']+'_'+str(x[users_id_attribute]) for x in frenchdeputies_metadata]
				head=[['']]+rower
				dist_matrix_array=[[1.-sim_matrix[u1][u2] if u1<u2 else 1.-sim_matrix[u2][u1] if u1>u2 else float(0.)  for u2 in sorted(sim_matrix)] for u1 in sorted(sim_matrix)]
				sim_matrix_array=[[sim_matrix[u1][u2] if u1<u2 else sim_matrix[u2][u1] if u1>u2 else float(1.)  for u2 in sorted(sim_matrix)] for u1 in sorted(sim_matrix)]
				for k in range(len(dist_matrix_array)):
					dist_matrix_array[k].insert(0,rower[k])
					sim_matrix_array[k].insert(0,rower[k])
				dist_matrix_array.insert(0,head)
				sim_matrix_array.insert(0,head)
				# print similarity_dictionnary(all_users_to_items_outcomes,frenchdeputies,items_context)
				# raw_input('...')
				#clusteringResults,clusters,linkageMatrix=applyHierarchiqueClusteringFromDataset(frenchdeputies_metadata,dist_matrix_array,parameter=0.4)
				hierarchicalClusteringFromDataset(frenchdeputies_metadata,dist_matrix_array,dendrogrammeDestination='./Figures/fig_'+str(index)+'.png',parameter=0.4,label_dendrogramme='NAME_FULL')
				writeCSV(dist_matrix_array,'./Figures/matrix_'+str(index)+'.csv',delimiter='\t')
					
					

					


			# except Exception as e:
			# 	raise e
			# 	continue
				cp_matrice_pattern=generateHeatMap(sim_matrix_array,'./Figures/heatmap_'+str(index)+'.png',vmin=0.,vmax=1.,showvalues_text=False,only_heatmap=True,organize=True)
				cp_matrice_pattern,ref_matrix_array=reorganize_similarly(cp_matrice_pattern,ref_matrix_array)
				generateHeatMap(ref_matrix_array,'./Figures/REF_heatmap_'+str(index)+'.png',vmin=0.,vmax=1.,showvalues_text=False,only_heatmap=True,organize=False)
			
			#print context_pat,'context reliablitiy',context_reliablitiy
			results.append([index,context_pat,context_reliablitiy,cohesion,items_context,vector_full,my_reliability])
		#results.append(['*',full_reliability,set_of_entities])
		results=sorted(results,key=lambda x : x[2],reverse=False)
		to_ret=[]

		for elem in results:
			#print elem[0],elem[1]
			to_ret.append({'index':elem[0],'pattern':elem[1],'contextSize':len(elem[4]),'reliability':elem[2],'cohesion':elem[3],'full_vector':elem[5],'myreliability':elem[6]})
			# for c_1 in matrix:
			# 	for c_2 in matrix[c_1]:
			# 		print c_1,c_2,sum(matrix[c_1][c_2][e] for e in elem[2]&matrix[c_1][c_2].viewkeys())
			# for i in frenchdeputies:
			# 	print i, [all_users_to_items_outcomes[i][e] for e in sorted(elem[2]) if e in all_users_to_items_outcomes[i]]
			#raw_input('...')
	#gc.collect()
	return to_ret
	


