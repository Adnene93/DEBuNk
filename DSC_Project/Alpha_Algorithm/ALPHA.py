from time import time
import cProfile
import pstats
import csv
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
	#raw_input('....')
	return matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome

	
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

	 
	#print nb_votes_casted_by_outcome_sums_tmp,nb_votes_casted_by_outcome_sums
	

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
			expected[c_1][c_2]=(((nb_votes_casted_by_outcome_sums[c_1]*factor)*(nb_votes_casted_by_outcome_sums[c_2]*factor))/(comparable_pairs_number*factor))
	# for k in sorted(new_matrix):
	# 	print k,'\t',
	# 	for k2 in sorted(new_matrix):
	# 		if k2 in new_matrix[k]:
	# 			print new_matrix[k][k2],'\t',
	# 		else:
	# 			print '\t',
	# 	print nb_votes_casted_by_outcome_sums[k],' '

	# for k in sorted(expected):
	# 	print k,'\t',
	# 	for k2 in sorted(expected):
	# 		if k2 in expected[k]:
	# 			print expected[k][k2],'\t',
	# 		else:
	# 			print '\t',
	# 	print nb_votes_casted_by_outcome_sums[k],' '
	# #print new_matrix
	# print sum(new_matrix[v1][v2]*(v1!=v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1)
	# print sum(expected[v1][v2]*(v1!=v2) for v1 in expected for v2 in expected[v1] if v2>=v1)
	#raw_input('...')
	# print expected
	# print nb_votes_casted_by_outcome
	disagreement_observed=(sum(new_matrix[v1][v2]*distance_function(v1,v2) for v1 in new_matrix for v2 in new_matrix[v1] if v2>=v1))
	#print 'disagreement_observed : ',disagreement_observed
	disagreement_expected=(sum(expected[v1][v2]*distance_function(v1,v2) for v1 in expected for v2 in expected[v1] if v2>=v1))
	#print 'disagreement_expected : ', disagreement_expected
	# print disagreement_observed
	# print disagreement_expected

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
		matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome=coincidence_matrix(all_users_to_items_outcomes,individuals_set=groups_indiv)
		
		
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
		frenchdeputies,_=filter_pipeline_obj(considered_users_1_sorted,[{'dimensionName':'GROUPE_ID','inSet':{'ECR'}}]) #[{'dimensionName':'NATIONAL_PARTY','inSet':{'Parti socialiste'}}]
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
		matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome=coincidence_matrix(all_users_to_items_outcomes,individuals_set=frenchdeputies)
		full_reliability,full_sums_votes=compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,set_of_entities)
		


		print 'reliablitiy',full_reliability
		
		enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, [{'name':'PROCEDURE_SUBJECT', 'type':'themes'}],threshold=15)	
		results=[]
		for e_p,e_label,e_config in enumerator_contexts:
			context_pat=pattern_printer(e_label,['themes'])
			items_context=set(x[items_id_attribute] for x in e_config['support'])

			try:
				context_reliablitiy,_=compute_reliability(matrix,individuals_for_each_entitiy,nb_votes_casted_by_outcome,items_context,nb_votes_casted_by_outcome_sums=full_sums_votes)
				cohesion,vector_full=compute_cohesion(all_users_to_items_outcomes,items_context,frenchdeputies)
			except Exception as e:
				print e
				continue
			
			#print context_pat,'context reliablitiy',context_reliablitiy
			results.append([context_pat,context_reliablitiy,cohesion,items_context,vector_full])
		#results.append(['*',full_reliability,set_of_entities])
		results=sorted(results,key=lambda x : x[1],reverse=False)
		to_ret=[]

		for elem in results:
			#print elem[0],elem[1]
			to_ret.append({'pattern':elem[0],'contextSize':len(elem[3]),'reliability':elem[1],'cohesion':elem[2],'full_vector':elem[4]})
			# for c_1 in matrix:
			# 	for c_2 in matrix[c_1]:
			# 		print c_1,c_2,sum(matrix[c_1][c_2][e] for e in elem[2]&matrix[c_1][c_2].viewkeys())
			# for i in frenchdeputies:
			# 	print i, [all_users_to_items_outcomes[i][e] for e in sorted(elem[2]) if e in all_users_to_items_outcomes[i]]
			#raw_input('...')
	#gc.collect()
	return to_ret
	


