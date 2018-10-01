from time import time
import cProfile
import pstats
import unicodedata
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
from datetime import datetime
from outcomeDatasetsProcessor.outcomeDatasetsProcessor import process_outcome_dataset
from plotter.plotter import plot_timeseries
from enumerator.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config,enumerator_complex_from_dataset_new_config,pattern_subsume_pattern,respect_order_complex_not_after_closure,encode_sup,enumerator_generate_random_miserum
from enumerator.enumerator_attribute_hmt import all_parents_tag_exclusive
import gc
import os,shutil
from util.matrixProcessing import transformMatricFromDictToList,adaptMatrices,getInnerMatrix,getCompleteMatrix
from enumerator.enumerator_attribute_complex_couple import enumerator_complex_cbo_init_new_config_couple

from os.path import basename, splitext, dirname
from outcomeAggregator.aggregateOutcome import compute_aggregates_outcomes
from measures.similaritiesDCS import similarity_vector_measure_dcs
from measures.qualityMeasure import compute_quality_and_upperbound
from util.csvProcessing import writeCSV,writeCSVwithHeader
from intbitset import intbitset
import json
#from pympler.asizeof import asizeof

def count_1_bits(n):
	# count = 0
	# while n!=0:
	# 	n &= (n-1)
	# 	count+=1
	# return float(count)
	return float(bin(n).count('1'))

def jaccard_bitset(n1,n2):
	return count_1_bits(n1&n2)/count_1_bits(n1|n2)

cache = LRUCache(maxsize=100000)
cache2 = LRUCache(maxsize=100000)

@cached(cache=cache)
def similarity_between_patterns(eup_extent1,eup_extent2):

	return  (1/3.)*(float(len(eup_extent1[0]&eup_extent2[0]))/float(len(eup_extent1[0]|eup_extent2[0]))+\
			float(len(eup_extent1[1]&eup_extent2[1]))/float(len(eup_extent1[1]|eup_extent2[1]))+\
			float(len(eup_extent1[2]&eup_extent2[2]))/float(len(eup_extent1[2]|eup_extent2[2])))

@cached(cache=cache)
def similarity_between_patterns_2(eup_extent1,eup_extent2):

	return  (1/3.)*(float(len(eup_extent1[0]&eup_extent2[0]))/float(len(eup_extent1[0]|eup_extent2[0]))+\
			max(float(len(eup_extent1[1]&eup_extent2[1]))/float(len(eup_extent1[1]|eup_extent2[1])) + float(len(eup_extent1[2]&eup_extent2[2]))/float(len(eup_extent1[2]|eup_extent2[2])),\
				float(len(eup_extent1[1]&eup_extent2[2]))/float(len(eup_extent1[1]|eup_extent2[2])) + float(len(eup_extent1[2]&eup_extent2[1]))/float(len(eup_extent1[2]|eup_extent2[1]))))

@cached(cache=cache)
def similarity_between_patterns_3(eup_extent1,eup_extent2):

	return  ((float(len(eup_extent1[0]&eup_extent2[0]))/float(len(eup_extent1[0]|eup_extent2[0])))*
			(1./2)*max(float(len(eup_extent1[1]&eup_extent2[1]))/float(len(eup_extent1[1]|eup_extent2[1])) + float(len(eup_extent1[2]&eup_extent2[2]))/float(len(eup_extent1[2]|eup_extent2[2])),\
				float(len(eup_extent1[1]&eup_extent2[2]))/float(len(eup_extent1[1]|eup_extent2[2])) + float(len(eup_extent1[2]&eup_extent2[1]))/float(len(eup_extent1[2]|eup_extent2[1]))))

@cached(cache=cache)
def similarity_between_patterns_4(eup_extent1,eup_extent2): #Geometric mean
	return  sqrt((float(len(eup_extent1[0]&eup_extent2[0]))/float(len(eup_extent1[0]|eup_extent2[0])))*
			(1./2)*max(float(len(eup_extent1[1]&eup_extent2[1]))/float(len(eup_extent1[1]|eup_extent2[1])) + float(len(eup_extent1[2]&eup_extent2[2]))/float(len(eup_extent1[2]|eup_extent2[2])),\
				float(len(eup_extent1[1]&eup_extent2[2]))/float(len(eup_extent1[1]|eup_extent2[2])) + float(len(eup_extent1[2]&eup_extent2[1]))/float(len(eup_extent1[2]|eup_extent2[1]))))



@cached(cache=cache2)
def J(s1,s2):
	return len(s1&s2)/float(len(s1|s2))

@cached(cache=cache)
def similarity_between_patterns_5(eup_extent1,eup_extent2): #Geometric mean
	return (J(eup_extent1[0],eup_extent2[0])*max(J(eup_extent1[1],eup_extent2[1]),J(eup_extent1[1],eup_extent2[2]))*max(J(eup_extent1[2],eup_extent2[1]),J(eup_extent1[2],eup_extent2[2])))**(1/3.)



def similarity_between_bitset_patterns_2(eup_extent1,eup_extent2):

	return  (1/3.)*(jaccard_bitset(eup_extent1[0],eup_extent2[0])+max(jaccard_bitset(eup_extent1[1],eup_extent2[1])+jaccard_bitset(eup_extent1[2],eup_extent2[2]),jaccard_bitset(eup_extent1[1],eup_extent2[2])+jaccard_bitset(eup_extent1[2],eup_extent2[1])))

def similarity_between_bitset_patterns_3(eup_extent1,eup_extent2):

	return  (jaccard_bitset(eup_extent1[0],eup_extent2[0]))*(1/2.)*max(jaccard_bitset(eup_extent1[1],eup_extent2[1])+jaccard_bitset(eup_extent1[2],eup_extent2[2]),jaccard_bitset(eup_extent1[1],eup_extent2[2])+jaccard_bitset(eup_extent1[2],eup_extent2[1]))


def mymax(l):

	l_iter=iter(l)
	try:
		max_to_ret=next(l_iter)
		for e in l_iter:
			if e>max_to_ret: max_to_ret=e
			if max_to_ret>=1.:
				return max_to_ret
		return max_to_ret
	except:
		return 0.


def similarity_between_patterns_set(list_of_eup_extent_1,list_of_eup_extent_2):
	#similarity_between_patterns_4
	SIM_USED=similarity_between_patterns_4#similarity_between_patterns_5

	if len(list_of_eup_extent_2)==0 or len(list_of_eup_extent_1)==0:
		return 0.,0.,0.,0.
	returned_1=0.
	for eup_extent1 in list_of_eup_extent_1:
		returned_1+=mymax(SIM_USED(eup_extent1,eup_extent2) for eup_extent2 in list_of_eup_extent_2)
	returned_2=0.
	for eup_extent2 in list_of_eup_extent_2:
		returned_2+=mymax(SIM_USED(eup_extent1,eup_extent2) for eup_extent1 in list_of_eup_extent_1)
	recall=returned_1/len(list_of_eup_extent_1)
	precision=returned_2/len(list_of_eup_extent_2)
	# print returned_1
	# print returned_2
	return (1/float(len(list_of_eup_extent_1)+len(list_of_eup_extent_2)))*(returned_1+returned_2),2./(1./precision+1./recall),precision,recall

def similarity_between_patterns_set_2(list_of_eup_extent_1,list_of_eup_extent_2):

	returned_1=0.
	for eup_extent1 in list_of_eup_extent_1:
		returned_1+=mymax(similarity_between_patterns_2(eup_extent1,eup_extent2) for eup_extent2 in list_of_eup_extent_2)
	returned_2=0.
	for eup_extent2 in list_of_eup_extent_2:
		returned_2+=mymax(similarity_between_patterns_2(eup_extent1,eup_extent2) for eup_extent1 in list_of_eup_extent_1)
	# print returned_1
	# print returned_2
	return (1/float(len(list_of_eup_extent_1)+len(list_of_eup_extent_2)))*(returned_1+returned_2)


def similarity_between_patterns_set_by_bitset(list_of_eup_extent_1,list_of_eup_extent_2):

	returned_1=0.
	for eup_extent1 in list_of_eup_extent_1:
		returned_1+=max(similarity_between_bitset_patterns_3(eup_extent1,eup_extent2) for eup_extent2 in list_of_eup_extent_2)
	returned_2=0.
	for eup_extent2 in list_of_eup_extent_2:
		returned_2+=max(similarity_between_bitset_patterns_3(eup_extent2,eup_extent1) for eup_extent1 in list_of_eup_extent_1)
	# print returned_1
	# print returned_2
	return (1/float(len(list_of_eup_extent_1)+len(list_of_eup_extent_2)))*(returned_1+returned_2)

def get_tuple_structure(all_users_to_items_outcomes):
	one_entitie=all_users_to_items_outcomes[next(all_users_to_items_outcomes.iterkeys())]
	one_item=next(one_entitie.iterkeys())
	outcome_tuple_structure=tuple(one_entitie[one_item])
	return outcome_tuple_structure


def enumerator_pair_of_users_bfs(considered_users_1_sorted,
							 considered_users_2_sorted,
							 users_id_attribute,
							 all_users_to_items_outcomes,
							 all_votes_id,
							 description_attributes_users,
							 threshold_nb_users_1,
							 threshold_nb_users_2,
							 outcome_tuple_structure,
							 how_much_visited,
							 method_aggregation_outcome,
							 only_square_matrix=False,
							 closed=True): #how_much_visited:{visited:<number>}
	enumerating_peers_time=0.
	types_attributes_users=[x['type'] for x in description_attributes_users]
	st=time()
	outcomeTrack={} #THIS MUST BE TEMPORARY BECAUSE IT KEEP TRACKS OF EVERY AGGREGATED ELEMENTS
	get_users_ids = partial(map,itemgetter(users_id_attribute))
	u1_all=set(get_users_ids(considered_users_1_sorted))
	u2_all=set(get_users_ids(considered_users_2_sorted))
	is_U1_EQUAL_TO_U2=(u1_all==u2_all)



	index_u1_visited=0;index_all_u1_visited=0
	index_u2_visited=0;index_all_u2_visited=0

	if closed:
		enum_u1=enumerator_complex_cbo_init_new_config(considered_users_1_sorted, description_attributes_users,{'contextsVisited':[],'itemsVisited':[]},verbose=False,threshold=threshold_nb_users_1,bfs=True,do_heuristic=False)
	else:
		enum_u1=enumerator_complex_from_dataset_new_config(considered_users_1_sorted, description_attributes_users, {'contextsVisited':[],'itemsVisited':[]},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_1,verbose=False)

	if closed:
		enum_u2=enumerator_complex_cbo_init_new_config(considered_users_2_sorted, description_attributes_users,{'contextsVisited':u1_config['contextsVisited'],'itemsVisited':[]},verbose=True,threshold=threshold_nb_users_2,bfs=False,do_heuristic=False,initValues=initConfig)
	else:
		enum_u2=enumerator_complex_from_dataset_new_config(considered_users_2_sorted, description_attributes_users, {'contextsVisited':u1_config['contextsVisited'],'itemsVisited':[]},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_2,verbose=False)







	visited_1_trace_map={}
	initConfig={'config':None,'attributes':None}
	for u1_p,u1_label,u1_config in enum_u1:
		u1_config['contextsVisited_parent']=u1_config['contextsVisited']
		u1_config['contextsVisited']=u1_config['contextsVisited']+[]
		u1_config['itemsVisited']=u1_config['itemsVisited']+[]
		index_u1_visited+=1
		u1_p_set_users=set(get_users_ids(u1_config['support']))
		attributes_u1_pat=u1_config['attributePattern']
		attributes_u1_refin=u1_config['refinement_index_actu']

		users1_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome,outcomeTrack=outcomeTrack)




		if closed:
			enum_u2=enumerator_complex_cbo_init_new_config(considered_users_2_sorted, description_attributes_users,{'contextsVisited':u1_config['contextsVisited'],'itemsVisited':[]},verbose=True,threshold=threshold_nb_users_2,bfs=False,do_heuristic=False,initValues=initConfig)
		else:
			enum_u2=enumerator_complex_from_dataset_new_config(considered_users_2_sorted, description_attributes_users, {'contextsVisited':u1_config['contextsVisited'],'itemsVisited':[]},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_2,verbose=False)

		equality_reached=False
		for u2_p,u2_label,u2_config in enum_u2:

			u2_config['contextsVisited_parent']=u2_config['contextsVisited']
			u2_config['contextsVisited']=u2_config['contextsVisited']+[]
			u2_config['itemsVisited']=u2_config['itemsVisited']+[]
			index_u2_visited+=1
			attributes_u2_pat=u2_config['attributePattern']
			attributes_u2_refin=u2_config['refinement_index_actu']

			#print pattern_printer(([],u1_p,u2_p),[],types_attributes_users)

			u2_p_set_users=set(get_users_ids(u2_config['support']))

			users2_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome,outcomeTrack=outcomeTrack)

			users_1_infos=(u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config)
			users_2_infos=(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config)

			enumerating_peers_time+=time()-st;
			yield users_1_infos,users_2_infos
			if is_U1_EQUAL_TO_U2 and u1_p==u2_p:
				break
			st=time()

		index_all_u2_visited+=u2_config['nb_visited'][0]
	index_all_u1_visited+=u1_config['nb_visited'][0]
	visited=(index_all_u2_visited-index_u2_visited)+(index_all_u1_visited-index_u1_visited)
	how_much_visited['visited']=visited
	enumerating_peers_time+=time()-st;
	print 'PEERS ENUMERATION TIME',enumerating_peers_time

def enumerator_pair_of_users(users_metadata,considered_users_1_sorted,
							 considered_users_2_sorted,
							 users_id_attribute,
							 all_users_to_items_outcomes,
							 all_votes_id,
							 description_attributes_users,
							 threshold_nb_users_1,
							 threshold_nb_users_2,
							 outcome_tuple_structure,
							 how_much_visited,
							 method_aggregation_outcome,
							 only_square_matrix=False,
							 closed=True): #how_much_visited:{visited:<number>}

	enumerating_peers_time=0.
	types_attributes_users=[x['type'] for x in description_attributes_users]
	st=time()
	nb=0
	outcomeTrack={} #THIS MUST BE TEMPORARY BECAUSE IT KEEP TRACKS OF EVERY AGGREGATED ELEMENTS
	get_users_ids = partial(map,itemgetter(users_id_attribute))
	u1_all=set(get_users_ids(considered_users_1_sorted))
	u2_all=set(get_users_ids(considered_users_2_sorted))
	is_U1_EQUAL_TO_U2=(u1_all==u2_all)



	index_u1_visited=0;index_all_u1_visited=0
	index_u2_visited=0;index_all_u2_visited=0

	if closed:
		enum_u1=enumerator_complex_cbo_init_new_config(considered_users_1_sorted, description_attributes_users,{'contextsVisited':[],'itemsVisited':[]},verbose=False,threshold=threshold_nb_users_1,bfs=False,do_heuristic=False)
	else:
		enum_u1=enumerator_complex_from_dataset_new_config(considered_users_1_sorted, description_attributes_users, {'contextsVisited':[],'itemsVisited':[]},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_1,verbose=False)




	visited_1_trace_map={}
	initConfig={'config':None,'attributes':None}
	for u1_p,u1_label,u1_config in enum_u1:
		u1_config['contextsVisited_parent']=u1_config['contextsVisited']
		u1_config['contextsVisited']=u1_config['contextsVisited']+[]
		u1_config['itemsVisited']=u1_config['itemsVisited']+[]
		index_u1_visited+=1
		u1_p_set_users=set(get_users_ids(u1_config['support']))
		attributes_u1_pat=u1_config['attributePattern']
		attributes_u1_refin=u1_config['refinement_index_actu']

		users1_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome,outcomeTrack=outcomeTrack)




		if closed:
			enum_u2=enumerator_complex_cbo_init_new_config(considered_users_2_sorted, description_attributes_users,{'contextsVisited':u1_config['contextsVisited'],'itemsVisited':[]},verbose=False,threshold=threshold_nb_users_2,bfs=False,do_heuristic=False,initValues=initConfig)
		else:
			enum_u2=enumerator_complex_from_dataset_new_config(considered_users_2_sorted, description_attributes_users, {'contextsVisited':u1_config['contextsVisited'],'itemsVisited':[]},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_2,verbose=False)

		equality_reached=False
		for u2_p,u2_label,u2_config in enum_u2:
			nb+=1
			u2_config['contextsVisited_parent']=u2_config['contextsVisited']
			u2_config['contextsVisited']=u2_config['contextsVisited']+[]
			u2_config['itemsVisited']=u2_config['itemsVisited']+[]
			index_u2_visited+=1
			attributes_u2_pat=u2_config['attributePattern']
			attributes_u2_refin=u2_config['refinement_index_actu']

			# if not equality_reached:
			# 	equality_reached=(u1_p==u2_p)

			# if is_U1_EQUAL_TO_U2 and not equality_reached:
			# 	continue


			# if is_U1_EQUAL_TO_U2 and not respect_order_complex_not_after_closure(attributes_u2_pat,attributes_u1_pat,attributes_u2_refin,attributes_u1_refin): #respect_order_complex_not_after_closure(attributes_u1_pat,attributes_u2_pat,len(u2_p)-1): #TODO I AM HERE LOOK TO THE TERMINAL FIRST
			# 	continue #799
			#parent_pattern=([],u1_config.get('parent',[]),u2_config.get('parent',[])) if u2_config.get('parent',[])==[] else ([],u1_p,u2_config.get('parent',[]))
			#pattern_printer(parent_pattern,[],types_attributes_users)
			#if u1_p[0]==['Poland'] or u2_p[0]==['Poland']:

			#print pattern_printer(([],u1_p,u2_p),[],types_attributes_users)
			print pattern_simpleonly_printer(u1_p,0,len(u1_p))+';'+pattern_simpleonly_printer(u2_p,0,len(u2_p)),nb

			u2_p_set_users=set(get_users_ids(u2_config['support']))

			users2_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome,outcomeTrack=outcomeTrack)


			users_1_infos=(u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config)
			users_2_infos=(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config)

			#print u1_p,u2_p,respect_order_complex_not_after_closure(attributes_u1_pat,attributes_u2_pat,len(u2_p)-1)
			#raw_input('...')
			enumerating_peers_time+=time()-st;
			yield users_1_infos,users_2_infos
			if is_U1_EQUAL_TO_U2 and u1_p==u2_p:
				break
			st=time()
			# if parent_pattern[2]!=[]:
			# 	del u2_config['contextsVisited_parent'][:]
			# 	u2_config['contextsVisited_parent'].extend([((c,a,b)) for (c,a,b) in u2_config['contextsVisited'] if DSC_Pat_subsume_DSC_Pat(([],a,b),parent_pattern,[],types_attributes_users)])
		#u1_config['contextsVisited']

		index_all_u2_visited+=u2_config['nb_visited'][0]
	index_all_u1_visited+=u1_config['nb_visited'][0]
	visited=(index_all_u2_visited-index_u2_visited)+(index_all_u1_visited-index_u1_visited)
	how_much_visited['visited']=visited
	enumerating_peers_time+=time()-st;
	print 'PEERS ENUMERATION TIME',enumerating_peers_time

#1106 305855.0 56.4690001011 6.43899655342 7.74700212479
#1106 303817.0 50.4140000343 6.05300593376 8.46199321747
#96 44919.0 17.0269999504 0.177000284195 2.07800126076
###############SIMILARITIES COMPUTATION#####################

#323 78215.0 21.7779998779 1.35999894142 3.4520008564
#327 121999.0 33.364000082 0.933001279831 4.84899616241 2145
#327 122335.0 33.4960000515 1.23200249672 5.18500208855 2145
def enumerator_pair_of_users_optimized_dfs(users_metadata,considered_users_1_sorted,
							 considered_users_2_sorted,
							 users_id_attribute,
							 all_users_to_items_outcomes,
							 all_votes_id,
							 description_attributes_users,
							 threshold_nb_users_1,
							 threshold_nb_users_2,
							 outcome_tuple_structure,
							 how_much_visited,
							 method_aggregation_outcome,
							 only_square_matrix=False,
							 closed=True,
							 bfs=False,
							 do_heuristic=False,
							 consider_order_between_desc_of_couples=True,
							 heatmap_for_matrix=False,
							 algorithm='DSC+CLOSED+UB2'): #how_much_visited:{visited:<number>}



	enumerating_peers_time=0.
	types_attributes_users=[x['type'] for x in description_attributes_users]
	names_attributes_users=[x['name'] for x in description_attributes_users]
	couple_description_attributes=[{'name':names_attributes_users[k],'type':types_attributes_users[k]} for k in range(len(types_attributes_users))]+\
								  [{'name':names_attributes_users[k]+'_2','type':types_attributes_users[k]} for k in range(len(types_attributes_users))]

	nb=0
	st=time()
	outcomeTrack={} #THIS MUST BE TEMPORARY BECAUSE IT KEEP TRACKS OF EVERY AGGREGATED ELEMENTS
	if heatmap_for_matrix:
		enumerator_pair_of_users_optimized_dfs.outcomeTrack=outcomeTrack
	get_users_ids = partial(map,itemgetter(users_id_attribute))
	u1_all=set(get_users_ids(considered_users_1_sorted))
	u2_all=set(get_users_ids(considered_users_2_sorted))
	considered_users_sorted=sorted(users_metadata.values(),key=itemgetter(users_id_attribute))
	all_users_ids=get_users_ids(considered_users_sorted)
	all_users_ids_to_index={x:i for i,x in enumerate(all_users_ids)}
	indices_1=set(all_users_ids_to_index[x] for x in u1_all)
	indices_2=set(all_users_ids_to_index[x] for x in u2_all)

	filtered_data={'support_1':considered_users_1_sorted,'support_2':considered_users_2_sorted,'indices_1':indices_1,'indices_2':indices_2}

	is_U1_EQUAL_TO_U2=(u1_all==u2_all)



	index_u1_visited=0;index_all_u1_visited=0
	index_u2_visited=0;index_all_u2_visited=0

	initConfig={'config':None,'attributes':None}

	enum=enumerator_complex_cbo_init_new_config_couple(considered_users_sorted, couple_description_attributes,{'contextsVisited':[],'itemsVisited':[]},verbose=False,threshold=threshold_nb_users_1,bfs=bfs,closed=closed,do_heuristic=do_heuristic,initValues=initConfig,filtered_data=filtered_data,consider_order_between_desc_of_couples=consider_order_between_desc_of_couples,heuristic=algorithm)
	old_u1_p=None
	for p_couple,p_couple_label,p_config in enum:
		nb+=1
		if do_heuristic and 'peers_of_individuals' in p_config['mss_node']:
			peers_of_individuals=p_config['mss_node']['peers_of_individuals']
			u1_p=peers_of_individuals[0][0]
			u2_p=peers_of_individuals[1][0]
			#print pattern_simpleonly_printer(u1_p,0,len(u1_p))+';'+pattern_simpleonly_printer(u2_p,0,len(u2_p)),p_config.get('k_eme_son',0),p_config.get('lvl_1',0),p_config.get('lvl_2',0),nb,p_config.get('lvl',0),len(u1_p_set_users),len(u2_p_set_users)
			yield peers_of_individuals
			continue
			#print mss_node.keys()

		st=time()

		u1_p=p_couple[:len(types_attributes_users)]
		u1_label=p_couple_label[:len(types_attributes_users)]
		u1_config=p_config
		u1_p_set_users=set(get_users_ids(p_config['support_1']))

		users1_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome,outcomeTrack=outcomeTrack)

		u2_p=p_couple[len(types_attributes_users):]
		u2_label=p_couple_label[len(types_attributes_users):]
		u2_config=p_config
		u2_p_set_users=set(get_users_ids(p_config['support_2']))

		users2_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome,outcomeTrack=outcomeTrack)
		p_config['contextsVisited_parent']=p_config['contextsVisited']
		p_config['contextsVisited']=p_config['contextsVisited']+[]
		p_config['itemsVisited']=p_config['itemsVisited']+[]

		users_1_infos=(u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config)
		users_2_infos=(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config)
		parent_pattern=p_config.get('parent',None)
		if not do_heuristic and False:
			print pattern_simpleonly_printer(u1_p,0,len(u1_p))+';'+pattern_simpleonly_printer(u2_p,0,len(u2_p)),p_config.get('k_eme_son',0),p_config.get('lvl_1',0),p_config.get('lvl_2',0),nb,p_config.get('lvl',0),len(u1_p_set_users),len(u2_p_set_users)
		enumerating_peers_time+=(time()-st)

		if do_heuristic:
			mss_node=p_config['mss_node']
			mss_node['peers_of_individuals']=(users_1_infos,users_2_infos)
			#print mss_node.keys()

		yield users_1_infos,users_2_infos


	#print 'FINISHED'
	#print 'PEERS ENUMERATION TIME',enumerating_peers_time,p_config['nb_visited']
#345 133026.0 32.9100000858 1.26000070572 6.154992342


def compute_similarity_memory_lowerbound(userpairssimsdetails,votes_ids,threshold_comparaison,bound,pruning,votes_map_ponderations={}):
	votes_map_ponderations_get=votes_map_ponderations.get
	ponderate=True if len(votes_map_ponderations)>0 else False
	if pruning:
		if bound==1:
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			for key in votes_ids:
				try:
					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair
				except:
					continue
			bound=max((threshold_comparaison-(nbvotes-similarity))/threshold_comparaison,0);
		else :
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append;

			for key in votes_ids:
				try:
					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair

					if ponderate:
						pairs_sim_array_append((pairs[key],votes_map_ponderations[key]))
					else:
						pairs_sim_array_append(v_pair)

				except:
					continue


			bound=0.;nbs_votes_with_ponds=0.
			if nbvotes>=threshold_comparaison:
				if nbvotes>threshold_comparaison:
					if ponderate:pairs_sim_array=sorted(pairs_sim_array,key=itemgetter(0))
					else:pairs_sim_array=sorted(pairs_sim_array)
				for k in range(int(threshold_comparaison)):
					if ponderate:
						#try:
						bound+=pairs_sim_array[k][0]*pairs_sim_array[k][1]
						nbs_votes_with_ponds+=pairs_sim_array[k][1]
						# except Exception as e:
						# 	print pairs_sim_array
						# 	raise e

					else:
						bound+=pairs_sim_array[k]

				if ponderate: bound/=float(nbs_votes_with_ponds)
				else: bound/=float(threshold_comparaison)
	else:
		nbvotes=0;similarity=0.;pairs=userpairssimsdetails
		for key in votes_ids:
			try:

				v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
				nbvotes+=votes_map_ponderations_get(key,1.)
				similarity+=v_pair
				# print pairs[key],v_pair
				# raw_input('---')
			except:
				continue
		bound=0.
	return similarity,nbvotes,bound


def compute_similarity_memory_higherbound(userpairssimsdetails,votes_ids,threshold_comparaison,bound,pruning,votes_map_ponderations={}):
	votes_map_ponderations_get=votes_map_ponderations.get
	ponderate=True if len(votes_map_ponderations)>0 else False
	if pruning:
		if bound==1:
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			for key in votes_ids:
				try:

					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair

				except:
					continue
			bound=min(float(similarity)/float(threshold_comparaison),1.);


		else :
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append
			for key in votes_ids:
				try:
					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair
					if ponderate: pairs_sim_array_append((pairs[key],votes_map_ponderations[key]))
					else:pairs_sim_array_append(v_pair)
				except:
					continue
			bound=0.;nbs_votes_with_ponds=0.
			if nbvotes>=threshold_comparaison:
				if nbvotes>threshold_comparaison:
					if ponderate:pairs_sim_array=sorted(pairs_sim_array,key=itemgetter(0),reverse=True)
					else:pairs_sim_array=sorted(pairs_sim_array,reverse=True)

				for k in range(int(threshold_comparaison)):
					if ponderate:
						bound+=pairs_sim_array[k][0]*pairs_sim_array[k][1]
						nbs_votes_with_ponds+=pairs_sim_array[k][1]
					else:
						bound+=pairs_sim_array[k]
				if ponderate: bound/=float(nbs_votes_with_ponds) #Reorder inversly with weights
				else: bound/=float(threshold_comparaison)
	else:
		nbvotes=0;similarity=0.;pairs=userpairssimsdetails
		for key in votes_ids:
			try:
				v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
				nbvotes+=votes_map_ponderations_get(key,1.)
				similarity+=v_pair
			except:
				continue
		bound=0.
	return similarity,nbvotes,bound


def compute_similarity_memory_lowerbound_WEIGHTEDMEAN(userpairssimsdetails,votes_ids,threshold_comparaison,bound,pruning,votes_map_ponderations={}):
	votes_map_ponderations_get=votes_map_ponderations.get
	ponderate=True if len(votes_map_ponderations)>0 else False
	if pruning:
		if bound==1:
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			for key in votes_ids:
				try:
					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair
				except:
					continue
			bound=max((threshold_comparaison-(nbvotes-similarity))/threshold_comparaison,0);
		else :
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append
			pairs_weight_array=[];pairs_weight_array_append=pairs_weight_array.append

			for key in votes_ids:
				try:
					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair

					if ponderate:
						pairs_sim_array_append(pairs[key]*votes_map_ponderations[key])
						pairs_weight_array_append(votes_map_ponderations[key])
					else:
						pairs_sim_array_append(v_pair)

				except:
					continue


			bound=0.;nbs_votes_with_ponds=0.
			if nbvotes>=threshold_comparaison:
				if nbvotes>threshold_comparaison:
					if ponderate:
						pairs_sim_array=sorted(pairs_sim_array,reverse=False)
						pairs_weight_array=sorted(pairs_weight_array,reverse=True)
					else:
						pairs_sim_array=sorted(pairs_sim_array)
				for k in range(int(threshold_comparaison)):
					if ponderate:
						bound+=pairs_sim_array[k]
						nbs_votes_with_ponds+=pairs_weight_array[k]
					else:
						bound+=pairs_sim_array[k]

				if ponderate: bound/=float(nbs_votes_with_ponds)
				else: bound/=float(threshold_comparaison)
	else:
		nbvotes=0;similarity=0.;pairs=userpairssimsdetails
		for key in votes_ids:
			try:

				v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
				nbvotes+=votes_map_ponderations_get(key,1.)
				similarity+=v_pair
				# print pairs[key],v_pair
				# raw_input('---')
			except:
				continue
		bound=0.
	return similarity,nbvotes,bound

def compute_similarity_memory_higherbound_WEIGHTEDMEAN(userpairssimsdetails,votes_ids,threshold_comparaison,bound,pruning,votes_map_ponderations={}):
	votes_map_ponderations_get=votes_map_ponderations.get
	ponderate=True if len(votes_map_ponderations)>0 else False
	if pruning:
		if bound==1:
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			for key in votes_ids:
				try:

					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair

				except:
					continue
			bound=min(float(similarity)/float(threshold_comparaison),1.);


		else :
			nbvotes=0;similarity=0.;pairs=userpairssimsdetails
			pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append
			pairs_weight_array=[];pairs_weight_array_append=pairs_weight_array.append
			for key in votes_ids:
				try:
					v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
					nbvotes+=votes_map_ponderations_get(key,1.)
					similarity+=v_pair
					if ponderate:
						pairs_sim_array_append(pairs[key]*votes_map_ponderations[key])
						pairs_weight_array_append(votes_map_ponderations[key])
					else:
						pairs_sim_array_append(v_pair)
				except:
					continue
			bound=0.;bound_weights=0.;nbs_votes_with_ponds=0.
			if nbvotes>=threshold_comparaison:
				if nbvotes>threshold_comparaison:
					if ponderate:
						pairs_sim_array=sorted(pairs_sim_array,reverse=True)
						pairs_weight_array=sorted(pairs_weight_array,reverse=False)
					else:
						pairs_sim_array=sorted(pairs_sim_array,reverse=True)

				for k in range(int(threshold_comparaison)):
					if ponderate:
						bound+=pairs_sim_array[k]
						nbs_votes_with_ponds+=pairs_weight_array[k]
					else:
						bound+=pairs_sim_array[k]
				if ponderate: bound/=float(nbs_votes_with_ponds) #Reorder inversly with weights
				else: bound/=float(threshold_comparaison)
	else:
		nbvotes=0;similarity=0.;pairs=userpairssimsdetails
		for key in votes_ids:
			try:
				v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
				nbvotes+=votes_map_ponderations_get(key,1.)
				similarity+=v_pair
			except:
				continue
		bound=0.
	return similarity,nbvotes,bound

def compute_similarity_memory_with_bounds(userpairssimsdetails,votes_ids,threshold_comparaison,lower,bound,pruning,votes_map_ponderations={}):
	if lower:
		return compute_similarity_memory_lowerbound_WEIGHTEDMEAN(userpairssimsdetails,votes_ids,threshold_comparaison,bound,pruning,votes_map_ponderations)
	else :
		return compute_similarity_memory_higherbound_WEIGHTEDMEAN(userpairssimsdetails,votes_ids,threshold_comparaison,bound,pruning,votes_map_ponderations)

def compute_similarity_matrix_memory_withbound(userpairssimsdetails,votes_ids,threshold_comparaison,lower,bound,pruning,votes_map_ponderations={}):
	return compute_similarity_memory_with_bounds(userpairssimsdetails,votes_ids,threshold_comparaison,lower,bound,pruning,votes_map_ponderations)





############################################################

def ext_subsume_ext(pattern_1_ext_bitset,pattern_2_ext_bitset,types):
	return pattern_1_ext_bitset&pattern_2_ext_bitset==pattern_2_ext_bitset

def DSC_EXT_subsume_DSC_EXT(pattern_1_ext_bitset,pattern_2_ext_bitset,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=True):
	if consider_order_between_desc_of_couples:
		return (ext_subsume_ext(pattern_1_ext_bitset[0],pattern_2_ext_bitset[0],types_attributes_items) and \
			   ext_subsume_ext(pattern_1_ext_bitset[1],pattern_2_ext_bitset[1],types_attributes_users) and \
			   ext_subsume_ext(pattern_1_ext_bitset[2],pattern_2_ext_bitset[2],types_attributes_users)) \
			   or \
			   (ext_subsume_ext(pattern_1_ext_bitset[0],pattern_2_ext_bitset[0],types_attributes_items) and \
			   ext_subsume_ext(pattern_1_ext_bitset[1],pattern_2_ext_bitset[2],types_attributes_users) and \
			   ext_subsume_ext(pattern_1_ext_bitset[2],pattern_2_ext_bitset[1],types_attributes_users))
	else:
		return (ext_subsume_ext(pattern_1_ext_bitset[0],pattern_2_ext_bitset[0],types_attributes_items) and \
			   ext_subsume_ext(pattern_1_ext_bitset[1],pattern_2_ext_bitset[1],types_attributes_users) and \
			   ext_subsume_ext(pattern_1_ext_bitset[2],pattern_2_ext_bitset[2],types_attributes_users))

def DSC_Pat_subsume_DSC_Pat(pattern_1,pattern_2,types_attributes_items,types_attributes_users):

	return (pattern_subsume_pattern(pattern_1[0],pattern_2[0],types_attributes_items) and \
		   pattern_subsume_pattern(pattern_1[1],pattern_2[1],types_attributes_users) and \
		   pattern_subsume_pattern(pattern_1[2],pattern_2[2],types_attributes_users)) \
		   or \
		   (pattern_subsume_pattern(pattern_1[0],pattern_2[0],types_attributes_items) and \
		   pattern_subsume_pattern(pattern_1[1],pattern_2[2],types_attributes_users) and \
		   pattern_subsume_pattern(pattern_1[2],pattern_2[1],types_attributes_users))

def DSC_Pat_subsume_DSC_Pat_by_extent(extent_1,extent_2,types_attributes_items,types_attributes_users):
	return (extent_1[0]<=extent_2[0] and ((extent_1[1]<=extent_2[1] and extent_1[2]<=extent_2[2]) or (extent_1[1]<=extent_2[2] and extent_1[2]<=extent_2[1])))





def printer_hmt(arr_tag_with_labels):
	#print arr_tag_with_labels
	ret={x[:x.find(' ')]:x for x in arr_tag_with_labels}
	tags=ret.viewkeys()
	#print tags
	tags=sorted(tags-reduce(set.union,[all_parents_tag_exclusive(x) for x in tags]))
	#print [ret[x] for x in tags]
	#raw_input('.....')
	return [ret[x] for x in tags]


def pattern_printer_one(pattern,types_attributes,names_attributes=[]):

	s=''
	for k in range(len(pattern)):
		if types_attributes[k]=='simple':
			if len(pattern[k])>1:
				if True:
					s= '*'
				else:
					s= str(pattern[k])
			else:
				s+= str(pattern[k][0])
		elif types_attributes[k] in {'themes','hmt'}:

			s= printer_hmt(pattern[k])#str(pattern[k])+' '
		else:
			s= pattern[k]
	return s

def pattern_printer(pattern,types_attributes,names_attributes=[]):

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

def pattern_printer_detailed(pattern,types_attributes,names_attributes):
	res=[]

	for k in range(len(pattern)):
		s=''
		if types_attributes[k]=='simple':
			if len(pattern[k])>1:
				if True:
					s= '*'
				else:
					s= pattern[k]
			else:
				s= pattern[k][0]
		elif types_attributes[k] in {'themes','hmt'}:

			s= printer_hmt(pattern[k])#str(pattern[k])+' '
		else:
			s= pattern[k]
		typos=types_attributes[k]
		if typos=='simple':
			typos='Categorical'
		elif typos in {'themes','hmt'}:
			typos='HMT'
		if typos=='numeric':
			typos='Numerical'
		else:
			typos=typos
		res.append([names_attributes[k],s])
	return json.JSONEncoder().encode(res)

# def pattern_printer(pattern,types_attributes_items,types_attributes_users):
# 	s=str(pattern[0])+' ('
# 	for k in range(len(pattern[1])):
# 		if types_attributes_users[k]=='simple' and len(pattern[1][k])>1:
# 			s+= 'ALL'+' '
# 		else:
# 			s+= str(pattern[1][k])+' '
# 	s+='),    ('
# 	for k in range(len(pattern[2])):
# 		if types_attributes_users[k]=='simple' and len(pattern[2][k])>1:
# 			s+= 'ALL'+' '
# 		else:
# 			s+= str(pattern[2][k])+' '
# 	s+=')'
# 	return s

def pattern_simpleonly_printer(pattern,start,end):
	s=''#str(pattern[0])+'      ('
	for k in range(start,end):
		if len(pattern[k])>1:
			s+= 'ALL'+' '
		else:
			s+= str(pattern[k])+' '
	return s


#OLD:
'''
	# if True:
	# 	cartesian_product=[]
	# 	print len(considered_users_1_sorted)
	# 	get_users1_ids = partial(map,itemgetter(users_id_attribute))
	# 	get_users2_ids = partial(map,itemgetter(users_id_attribute+'_2'))
	# 	k=0
	# 	for row in product(considered_users_1_sorted,considered_users_2_sorted):
	# 		new_row={}
	# 		new_row.update(row[0])
	# 		new_row.update({k+'_2':v for k,v in row[1].iteritems()})
	# 		cartesian_product.append(new_row)
	# 		k+=1
	# 		print k



	# 	print len(cartesian_product)
	# 	desc_to_consider=[{'name':'COUNTRY', 'type':'simple'},{'name':'GROUPE_ID', 'type':'simple'},{'name':'NATIONAL_PARTY', 'type':'simple'},{'name':'GENDER', 'type':'simple'},{'name':'AGEGROUP', 'type':'simple'}]
	# 	desc_to_consider+=[{'name':'COUNTRY_2', 'type':'simple'},{'name':'GROUPE_ID_2', 'type':'simple'},{'name':'NATIONAL_PARTY_2', 'type':'simple'},{'name':'GENDER_2', 'type':'simple'},{'name':'AGEGROUP_2', 'type':'simple'}]
	# 	enum=enumerator_complex_cbo_init_new_config(cartesian_product, desc_to_consider,{},verbose=False,threshold=1,bfs=True,do_heuristic=False)
	# 	for p,p_label,p_config in enum:
	# 		u1_set=set(get_users1_ids(p_config['support']))
	# 		u2_set=set(get_users2_ids(p_config['support']))
	# 		#print len(u1_set),len(u2_set)
	# 		print pattern_simpleonly_printer(p,0,5),pattern_simpleonly_printer(p,5,10),p_config['lvl']

			#raw_input('...')

'''


'''
json_config={
	"objects_file":"path",
	"individuals_file":"path",
	"reviews_file":"path",
	"delimiter":"\t",

	"nb_objects":float('inf'),
	"nb_individuals":float('inf'),

	"arrayHeader":[],
	"numericHeader":[],
	"vector_of_outcome":[],  #| None,
	"ponderation_attribute":"attribute_name", #if the attribute figure in the outcome then it's a weighted mean using second groups of individuals outcomes as a weight

	"description_attributes_objects":[["name","type"], ...],
	"description_attributes_individuals":[["name","type"], ...],

	"threshold_individuals":50,
	"threshold_objects":10,
	"threshold_quality":0.01,


	"aggregation_measure":'VECTOR_VALUES',
	"similarity_measure":"MAAD",
	"quality_measure":"DISAGR_SUMDIFF",
	"algorithm":"DSC+CLOSED+UB2",# X could be : DSC, DSC+CLOSED, DSC+CLOSED+UB1, DSC+CLOSED+UB2, DSC+RandomWalk
	"timebudget":1000,


	"objects_scope":[
	],
	"individuals_1_scope":[
	],
	"individuals_2_scope":[
	],

	"results_destination":'./results.csv'
}
'''

def DSC_input_config(json_config_input,heatmap_for_matrix=False,verbose=False):

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

		'hmt_to_itemset':json_config_input.get('hmt_to_itemset',False),

		"nb_items_entities" : json_config_input.get('nb_items_entities',float('inf')),
		"nb_items_individuals" : json_config_input.get('nb_items_individuals',float('inf')),

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
		"nb_random_walks":json_config_input.get('nb_random_walks',30),

		"results_destination":json_config_input.get('results_destination',None),
        "detailed_results_destination":json_config_input.get('detailed_results_destination',None)
	}

	nb_items_entities=json_config['nb_items_entities']
	nb_items_individuals=json_config['nb_items_individuals']


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


	attributes_to_consider=[x['name'] for x in description_attributes_objects]
	attributes_to_consider=attributes_to_consider+[x['name'] for x in description_attributes_individuals]
	#print attributes_to_consider
	#raw_input('...')
	for returned in DSC_Entry_Point(json_config['objects_file'],json_config['individuals_file'],json_config['reviews_file'],
		numeric_attrs=json_config['numericHeader'],array_attrs=json_config['arrayHeader'],outcome_attrs=json_config['vector_of_outcome'],method_aggregation_outcome=json_config['aggregation_measure'],
		itemsScope=json_config['objects_scope'],users_1_Scope=json_config['individuals_1_scope'],users_2_Scope=json_config['individuals_2_scope'],delimiter=json_config['delimiter'],
		description_attributes_items=description_attributes_objects,description_attributes_users=description_attributes_individuals,
		comparaison_measure=json_config['similarity_measure'],qualityMeasure=json_config['quality_measure'],nb_items=json_config['nb_objects'],nb_individuals=json_config['nb_individuals'],
		threshold_comparaison=json_config['threshold_objects'],threshold_nb_users_1=json_config['threshold_individuals'],threshold_nb_users_2=json_config['threshold_individuals'],
		quality_threshold=json_config['threshold_quality'],ponderation_attribute=json_config['ponderation_attribute'],
		bound_type=bound_type,pruning=pruning,closed=closed,
		do_heuristic_contexts=do_heuristic_contexts,do_heuristic_peers=do_heuristic_peers,timebudget=json_config['timebudget'],results_destination=json_config['results_destination'], detailed_results_destination=json_config['detailed_results_destination'],attributes_to_consider=attributes_to_consider,heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,symmetry=json_config['symmetry'],nb_random_walks=json_config['nb_random_walks'],hmt_to_itemset=json_config['hmt_to_itemset'],verbose=verbose):




		#take as an input a json and either do a qualitative experiments or quantitatvie experiments
		#Consider three algorithm (exhaustive search algorithm) baseline(closed=False,Pruning=False), DSC+CLOSED(closed=True,Pruning=False), DSC+CLOSED+UB1(closed=True,Pruning=True,bound_type=1),DSC+CLOSED+UB2(closed=True,Pruning=True,bound_type=2),
		#Consider after ward the comparison between the random walk and the exhaustive search algorithm with several timebudget
		#Once this is done we can launch the Experiments

		#We need to prepare the dataset EPD8, EPD7, EPD78 and EPD678
		DSC_input_config.stats=DSC_Entry_Point.stats
		DSC_input_config.stats['algorithm']=algorithm
		if heatmap_for_matrix:
			DSC_input_config.outcomeTrack=DSC_Entry_Point.outcomeTrack
		DSC_input_config.types_attributes_items=DSC_Entry_Point.types_attributes_items
		DSC_input_config.types_attributes_users=DSC_Entry_Point.types_attributes_users
		yield returned



def DSC_input_config_alpha(json_config_input,heatmap_for_matrix=False,verbose=False):

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

		'hmt_to_itemset':json_config_input.get('hmt_to_itemset',False),

		"nb_items_entities" : json_config_input.get('nb_items_entities',float('inf')),
		"nb_items_individuals" : json_config_input.get('nb_items_individuals',float('inf')),

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
		"nb_random_walks":json_config_input.get('nb_random_walks',30),

		"results_destination":json_config_input.get('results_destination',None)
		#"cover_threshold":json_config_input.get('cover_threshold',1.),

	}

	nb_items_entities=json_config['nb_items_entities']
	nb_items_individuals=json_config['nb_items_individuals']


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


	attributes_to_consider=[x['name'] for x in description_attributes_objects]
	attributes_to_consider=attributes_to_consider+[x['name'] for x in description_attributes_individuals]
	#print attributes_to_consider
	#raw_input('...')
	from Alpha_Algorithm.ALPHA import Alpha_Entry_Point
	#print json_config['results_destination']
	#raw_input('....')
	returned=Alpha_Entry_Point(json_config['objects_file'],json_config['individuals_file'],json_config['reviews_file'],
		numeric_attrs=json_config['numericHeader'],array_attrs=json_config['arrayHeader'],outcome_attrs=json_config['vector_of_outcome'],method_aggregation_outcome=json_config['aggregation_measure'],
		itemsScope=json_config['objects_scope'],users_1_Scope=json_config['individuals_1_scope'],users_2_Scope=json_config['individuals_2_scope'],delimiter=json_config['delimiter'],
		description_attributes_items=description_attributes_objects,description_attributes_users=description_attributes_individuals,
		comparaison_measure=json_config['similarity_measure'],qualityMeasure=json_config['quality_measure'],nb_items=json_config['nb_objects'],nb_individuals=json_config['nb_individuals'],
		threshold_comparaison=json_config['threshold_objects'],threshold_nb_users_1=json_config['threshold_individuals'],threshold_nb_users_2=json_config['threshold_individuals'],
		quality_threshold=json_config['threshold_quality'],ponderation_attribute=json_config['ponderation_attribute'],
		bound_type=bound_type,pruning=pruning,closed=closed,
		do_heuristic_contexts=do_heuristic_contexts,do_heuristic_peers=do_heuristic_peers,timebudget=json_config['timebudget'],results_destination=json_config['results_destination'],attributes_to_consider=attributes_to_consider,heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,symmetry=json_config['symmetry'],nb_random_walks=json_config['nb_random_walks'],hmt_to_itemset=json_config['hmt_to_itemset'],verbose=verbose)



	writeCSVwithHeader(returned,json_config['results_destination'],selectedHeader=['index','pattern','contextSize','reliability','cohesion','full_vector','myreliability'])
		#take as an input a json and either do a qualitative experiments or quantitatvie experiments
		#Consider three algorithm (exhaustive search algorithm) baseline(closed=False,Pruning=False), DSC+CLOSED(closed=True,Pruning=False), DSC+CLOSED+UB1(closed=True,Pruning=True,bound_type=1),DSC+CLOSED+UB2(closed=True,Pruning=True,bound_type=2),
		#Consider after ward the comparison between the random walk and the exhaustive search algorithm with several timebudget
		#Once this is done we can launch the Experiments

		#We need to prepare the dataset EPD8, EPD7, EPD78 and EPD678
		#DSC_input_config.stats=DSC_Entry_Point.stats
		#DSC_input_config.stats['algorithm']=algorithm
		#if heatmap_for_matrix:
		#	DSC_input_config.outcomeTrack=DSC_Entry_Point.outcomeTrack
		#DSC_input_config.types_attributes_items=DSC_Entry_Point.types_attributes_items
		#DSC_input_config.types_attributes_users=DSC_Entry_Point.types_attributes_users
	yield returned




def DSC_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=[],array_attrs=None,outcome_attrs=None,method_aggregation_outcome='VECTOR_VALUES',itemsScope=[],users_1_Scope=[],users_2_Scope=[],delimiter='\t',
	description_attributes_items=[],description_attributes_users=[],
	comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',nb_items=float('inf'),nb_individuals=float('inf'),threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
	ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,results_destination='.//results.csv',detailed_results_destination='./DetailedResults',attributes_to_consider=None,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',nb_items_entities=float('inf'),nb_items_individuals=float('inf'),symmetry=True,nb_random_walks=30,hmt_to_itemset=False,debug=False,verbose=False):
	if debug:
		data=[
			{'attr1':'a','attr2':1},
			{'attr1':'a','attr2':2},
			{'attr1':'b','attr2':3},
			{'attr1':'c','attr2':2}
		]
		desc=[{'name':'attr1', 'type':'simple'},{'name':'attr2', 'type':'numeric'}]
		types_desc=[x['type'] for x in desc]
		#enum=enumerator_generate_random_miserum(considered_items_sorted, description_attributes_items,{},verbose=False,threshold=1,closed=True,bfs=False,do_heuristic=False)
		enum=enumerator_generate_random_miserum(data, desc,{},verbose=False,threshold=1,closed=True,bfs=False,do_heuristic=False)
		k=0;lim=100000.;
		t=time()
		all_lists={}
		for p,p_label,p_config in enum:
			pp=pattern_printer(p,types_desc)
			if pp not in all_lists:
				all_lists[pp]=[0,len(p_config['indices'])]
			all_lists[pp][0]=all_lists[pp][0]+1
			k+=1
			if k==lim:
				break
			#raw_input('...')
		for pp in all_lists:
			print pp,all_lists[pp][0]/float(lim),all_lists[pp][1]
		raw_input('........')

		enum=enumerator_complex_cbo_init_new_config_couple(considered_users_1_sorted, desc_to_consider,{},verbose=False,threshold=threshold_nb_users_1,closed=True,bfs=False,do_heuristic=False)
		k=0
		t=time()
		for p,p_label,p_config in enum:
			k+=1
		t=time()-t
		print 'timespent   ' + str(t), 'nb   ' + str(k)
		raw_input('***********')


	DATASET_STATISTIC_COMPUTING=False
	inited=time()
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered,vector_of_action =\
		process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,hmt_to_itemset=hmt_to_itemset,delimiter=delimiter)

	# print vector_of_action
	# raw_input('.....')
	###############################################STATS DATASETS#############################################################################
	if DATASET_STATISTIC_COMPUTING:
		print 'nb_entities : ',len(considered_items_sorted)
		print 'nb_users : ',len(users_metadata)
		print 'nb_users_1 : ',len(considered_users_1_sorted)
		print 'nb_users_2 : ',len(considered_users_2_sorted)
		print 'nb_reviews : ',nb_outcome_considered
		print 'nb_attrs_entities : ', len(description_attributes_items)
		print 'nb_attrs_individuals : ', len(description_attributes_users)
		_,_,conf=next(enumerator_complex_cbo_init_new_config(considered_items_sorted,description_attributes_items))


		# infos=[]
		# iter_s=iter(sorted(conf['attributes'][0]['labelmap']))
		# next(iter_s)
		# for r in iter_s:

		# 	r_val=conf['attributes'][0]['labelmap'][r]
		# 	#print r,' '.join(r_val.split(' ')[1:])
		# 	#raw_input('.....')
		# 	infos.append({'tag_id':r,'tag_label':' '.join(r_val.split(' ')[1:])})
		# writeCSVwithHeader(infos,'EPD_TAGS.csv',selectedHeader=['tag_id','tag_label'])
		# raw_input('.....')

		for ind_attr,attr in enumerate(conf['attributes']):
			if attr['type']=='themes':
				from enumerator.enumerator_attribute_themes2 import maximum_tree
				nb_tags_explicit_implicit_avg=0;nb_tags_explicit_implicit_max=0
				nb_tags_explicit_avg=0;nb_tags_explicit_avg_max=0
				
				
				# print "-----------------------"
				# tagous=[]
				# CALCULUS=0.;nb_CALCULUS=0.;minous=100000
				# for x in sorted(attr['index_attr']):
				# 	#print x,len(attr['index_attr'][x])
				# 	tagous.append({'tag':x,'label':attr['labelmap'].get(x,x),'nb_obj':len(attr['index_attr'][x])})
				# 	if x.count(".")==2:
				# 		CALCULUS+=len(attr['index_attr'][x])
				# 		nb_CALCULUS+=1
				# 		minous=min(minous,len(attr['index_attr'][x]))
				
				# print CALCULUS,nb_CALCULUS,CALCULUS/nb_CALCULUS,minous
				# writeCSVwithHeader(tagous,'./TAGS_DETAILS.csv',selectedHeader=['tag','label','nb_obj'])

				# print "-------------------------"

				for x in conf['allindex']:
					nb_tags_explicit_implicit_avg+= len(x[attr['name']])
					nb_tags_explicit_implicit_max=max(nb_tags_explicit_implicit_max,len(x[attr['name']]))
					nb_tags_explicit_avg+=len(maximum_tree(attr['domain'],x[attr['name']]))
					nb_tags_explicit_avg_max=max(nb_tags_explicit_avg_max,len(maximum_tree(attr['domain'],x[attr['name']])))
				nb_tags_explicit_implicit_avg/=float(len(conf['allindex']))
				nb_tags_explicit_avg/=float(len(conf['allindex']))
				print '\t', attr['name'], attr['type'], len(attr['domain']),'%.2f'%nb_tags_explicit_implicit_avg,'%.2f'%nb_tags_explicit_avg,nb_tags_explicit_implicit_max,nb_tags_explicit_avg_max

			else:
				print '\t', attr['name'], attr['type'], len(attr['domain'])

		all_avgs=0.
		nb_items_per_entities={}
		for ind,x in enumerate(conf['allindex']):
			avg_nb_items=0.
			for ind_attr,attr in enumerate(conf['attributes']):
				if attr['type']=='themes':
					avg_nb_items+=len(x[attr['name']])
				elif attr['type']=='simple':
					avg_nb_items+=1
				elif attr['type']=='numeric':
					avg_nb_items+=len(attr['domain'])+1
					#print (len(attr['domain'])-bisect_left(attr['domain'],x[attr['name']]))+(bisect_left(attr['domain'],x[attr['name']]))+1
			#print avg_nb_items
			nb_items_per_entities[considered_items_sorted[ind][items_id_attribute]]=avg_nb_items
			all_avgs+=avg_nb_items
		print 'nb_itemset : ', conf['nb_itemset'], all_avgs/len(conf['allindex'])
		nb_itemset_entities=conf['nb_itemset']

		_,_,conf=next(enumerator_complex_cbo_init_new_config(considered_users_1_sorted,description_attributes_users))
		for ind_attr,attr in enumerate(conf['attributes']):
			if attr['type']=='themes':
				from enumerator.enumerator_attribute_themes2 import maximum_tree
				nb_tags_explicit_implicit_avg=0;nb_tags_explicit_implicit_max=0
				nb_tags_explicit_avg=0;nb_tags_explicit_avg_max=0
				for x in conf['allindex']:
					nb_tags_explicit_implicit_avg+= len(x[attr['name']])
					nb_tags_explicit_implicit_max=max(nb_tags_explicit_implicit_max,len(x[attr['name']]))
					nb_tags_explicit_avg+=len(maximum_tree(attr['domain'],x[attr['name']]))
					nb_tags_explicit_avg_max=max(nb_tags_explicit_avg_max,len(maximum_tree(attr['domain'],x[attr['name']])))
				nb_tags_explicit_implicit_avg/=float(len(conf['allindex']))
				nb_tags_explicit_avg/=float(len(conf['allindex']))
				print '\t', attr['name'], attr['type'], len(attr['domain']),'%.2f'%nb_tags_explicit_implicit_avg,'%.2f'%nb_tags_explicit_avg,nb_tags_explicit_implicit_max,nb_tags_explicit_avg_max

			else:
				print '\t', attr['name'], attr['type'], len(attr['domain'])

		all_avgs=0.
		nb_items_per_individual={}
		for ind,x in enumerate(conf['allindex']):
			avg_nb_items=0.
			for ind_attr,attr in enumerate(conf['attributes']):
				if attr['type']=='themes':
					avg_nb_items+=len(x[attr['name']])
				elif attr['type']=='simple':
					avg_nb_items+=1
				elif attr['type']=='numeric':
					avg_nb_items+=len(attr['domain'])+1
			nb_items_per_individual[considered_users_1_sorted[ind][users_id_attribute]]=avg_nb_items

			#print (len(attr['domain'])-bisect_left(attr['domain'],x[attr['name']]))+(bisect_left(attr['domain'],x[attr['name']]))+1
			#print avg_nb_items
			all_avgs+=avg_nb_items

		print 'nb_itemset : ', conf['nb_itemset'], all_avgs/len(conf['allindex'])
		nb_itemset_individuals=conf['nb_itemset']
		nb_itemset_individuals_avg=all_avgs/len(conf['allindex'])
		entities_to_users_outcomes={}
		for u in all_users_to_items_outcomes:
			for e in all_users_to_items_outcomes[u]:
				if e not in entities_to_users_outcomes:
					entities_to_users_outcomes[e]=set()
				entities_to_users_outcomes[e]|={u}

		nb_e_u_s=sum(len(x) for x in entities_to_users_outcomes.values())
		nb_e_uu_s=sum(len(x)*len(x) for x in entities_to_users_outcomes.values())
		#nb_avg_itemset=sum(len(entities_to_users_outcomes[x])*len(entities_to_users_outcomes[x])*(nb_items_per_entities[x]+nb_itemset_individuals_avg) for x in entities_to_users_outcomes)/float(nb_e_uu_s)
		nb_avg_itemset=sum((nb_items_per_entities[x]+nb_items_per_individual[y])*len(entities_to_users_outcomes[x]) for x in entities_to_users_outcomes for y in entities_to_users_outcomes[x])/float(nb_e_uu_s)
		print 'nb_considered_reviews ', nb_e_u_s
		print 'nb_considered_entries_cartesian ', nb_e_uu_s
		print 'nb_itemsets_full ', nb_itemset_entities+nb_itemset_individuals*2
		print 'nb_itemsets_avg_per_transaction ', nb_avg_itemset
		raw_input('...')
	###############################################STATS DATASETS#############################################################################


	gc.collect()
	types_attributes_users=[x['type'] for x in description_attributes_users]
	types_attributes_items=[x['type'] for x in description_attributes_items]
	DSC_Entry_Point.types_attributes_items=types_attributes_items
	DSC_Entry_Point.types_attributes_users=types_attributes_users

	k=0



	if ponderation_attribute is not None and ponderation_attribute not in considered_items_sorted[0].viewkeys():
		ponderation_attribute=outcome_attrs.index(ponderation_attribute)

	#print 'STARTING AFTER PREPROCESSING....'
	#DSC(items_metadata,users_metadata,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,all_users_to_items_outcomes,items_id_attribute,users_id_attribute,method_aggregation_outcome=method_aggregation_outcome)
	TOCALL=DSC
	if do_heuristic_peers:
		TOCALL=DSC_AnyTimeRandomWalk


	TOCALL.stats={
		'quality_measure':qualityMeasure,
		'comparaison_measure':comparaison_measure,
		'method_aggregation_outcome':method_aggregation_outcome,

		'attrs_objects':[(x['name'],x['type']) for x in description_attributes_items],
		'attrs_users':[(x['name'],x['type']) for x in description_attributes_users],

		'nb_attrs_objects':len(types_attributes_items),
		'nb_attrs_objects_in_itemset':0,
		'nb_attrs_users':len(types_attributes_users),
		'nb_attrs_users_in_itemset':0,

		'quality_threshold':quality_threshold,
		'threshold_objects':threshold_comparaison,
		'threshold_nb_users_1':threshold_nb_users_1,
		'threshold_nb_users_2':threshold_nb_users_2,
		'nb_objects':len(considered_items_sorted),
		'nb_users':len(users_metadata),
		'nb_users_1':len(considered_users_1_sorted),
		'nb_users_2':len(considered_users_2_sorted),
		'nb_reviews':nb_outcome_considered,

		'closed':closed,
		'pruning_ub':pruning,
		'RandomWalk':do_heuristic_peers,
		'timebudget':timebudget,
		'bound_type':bound_type,

		'nb_generated_subgroups':0,
		'nb_visited_subgroups':0,
		'nb_candidates_subgroups':0,
		'nb_patterns':0,

		'timespent_init':time()-inited,
		'timespent':0,
		'timespent_total':0



	}

	if verbose:# and not do_heuristic_peers:
		enum=enumerator_complex_cbo_init_new_config(considered_users_1_sorted, description_attributes_users,{},verbose=False,threshold=threshold_nb_users_1,closed=closed,bfs=False,do_heuristic=False)
		estimated_maximum_number_of_called_peers=0.
		for _ in enum: estimated_maximum_number_of_called_peers+=1
		if symmetry:
			estimated_maximum_number_of_called_peers=(estimated_maximum_number_of_called_peers*(estimated_maximum_number_of_called_peers+1))/2
		else:
			estimated_maximum_number_of_called_peers=estimated_maximum_number_of_called_peers*estimated_maximum_number_of_called_peers
		stdout.write('%s\r' % ('#MAX_PEERS = ' + str(estimated_maximum_number_of_called_peers)));stdout.flush();

		enum=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items,{},verbose=False,threshold=threshold_comparaison,closed=closed,bfs=False,do_heuristic=False)
		estimated_maximum_number_of_entities=0
		for _ in enum: estimated_maximum_number_of_entities+=1

		TOCALL.stats['estimated_maximum_number_of_entities']=estimated_maximum_number_of_entities
		TOCALL.stats['estimated_maximum_number_of_called_peers']=estimated_maximum_number_of_called_peers
		# print 'NB Entities : ', float(estimated_maximum_number_of_entities)
		# print 'NB Max Peers : ', float(estimated_maximum_number_of_called_peers)
		# print 'Ratio : ', float(estimated_maximum_number_of_entities)/float(estimated_maximum_number_of_called_peers)

	for interesting_patterns in TOCALL(items_metadata,users_metadata,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,all_users_to_items_outcomes,
		items_id_attribute,users_id_attribute,description_attributes_items=description_attributes_items,description_attributes_users=description_attributes_users,method_aggregation_outcome=method_aggregation_outcome,
		comparaison_measure=comparaison_measure,qualityMeasure=qualityMeasure,threshold_comparaison=threshold_comparaison,threshold_nb_users_1=threshold_nb_users_1,threshold_nb_users_2=threshold_nb_users_2,quality_threshold=quality_threshold,
		ponderation_attribute=ponderation_attribute,bound_type=bound_type,pruning=pruning,closed=closed,do_heuristic_contexts=do_heuristic_contexts,do_heuristic_peers=do_heuristic_peers,timebudget=timebudget,heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,consider_order_between_desc_of_couples=symmetry,nb_random_walks=nb_random_walks,verbose=verbose):



		TOCALL.stats['timespent_total']=float('%.2f'%(time()-inited))
		TOCALL.stats['timespent_init']=float('%.2f'%(TOCALL.stats['timespent_init']))
		TOCALL.stats['timespent']=float('%.2f'%(TOCALL.stats['timespent']))
		# for k,v in TOCALL.stats.iteritems():
		# 	print k,' : ',v

		DSC_Entry_Point.stats=TOCALL.stats
		#raw_input('...')
		if heatmap_for_matrix:
			DSC_Entry_Point.outcomeTrack=TOCALL.outcomeTrack
		write_results_in_file=True if results_destination is not None else False
		if write_results_in_file:
			yield DSC_exiting_point(interesting_patterns,all_users_to_items_outcomes,items_metadata,users_metadata,items_id_attribute,users_id_attribute,results_destination, detailed_results_destination,types_attributes_items,types_attributes_users,TOCALL.stats['attrs_objects'],TOCALL.stats['attrs_users'],vector_of_action,write_results_in_file)
		else:
			yield DSC_Entry_Point.stats





# def jaccard(s1,s2):
# 	return float(len(s1&s2))/len(s1|s2)

# def get_top_k_div_from_a_pattern_set(interesting_patterns,threshold_sim=0.6,k=1000): #patterns = [(p,rel,len_sup,qual,ci,sup)]


# 	returned_patterns=[]
# 	sorted_patterns=sorted(interesting_patterns,key=lambda x:x[3],reverse=True)
# 	tp=sorted_patterns[0]
# 	returned_patterns.append(tp)

# 	while 1:
# 		if len(returned_patterns)==k:
# 			break

# 		found_yet=False

# 		for p in sorted_patterns:
# 			sup=p[5]
# 			if all(jaccard(sup,supc)<=threshold_sim for _,_,_,_,_,supc in returned_patterns):
# 				found_yet=True
# 				#t_p=(p,sup,supbitset,qual)
# 				returned_patterns.append(p)
# 				break

# 		if not found_yet:
# 			break


# 	return returned_patterns

def from_string_to_date(str_date,dateformat="%d/%m/%y"):
	return datetime.strptime(str_date, dateformat)

def from_date_to_string(dateObj,dateformat="%Y-%m-%d"):
	return datetime.strftime(dateObj, dateformat)


def DSC_exiting_point(interesting_patterns,all_users_to_items_outcomes,items_metadata,users_metadata,items_id_attribute,users_id_attribute,file_destination, detailed_results_destination,types_attributes_items,types_attributes_users,description_attributes_items,description_attributes_users,vector_of_action,write_results_in_file=True):
	sorted_interesting_patterns=sorted(interesting_patterns,key = lambda x:x[0][0],reverse=True)
	k=1
	already_seen=None
	to_write=[]
	to_write_for_GAT=[]
	WRITE_MORE_DETAILS=False
	CSV_RESULTS_FILE_FOR_GAT_ANTOINE=False
	COMPUTE_REF=False
	#TAKE_INTO_ACCOUNT_INFOS=False
	DRAW_FIGURES=False
	type_of_data="EPD"#"OPENMEDIC"
	#MOVIELENS  #YELP  #OPENMEDIC


	if WRITE_MORE_DETAILS:
		if not os.path.exists(detailed_results_destination):
			os.makedirs(detailed_results_destination)
		else:
			shutil.rmtree(detailed_results_destination)
			os.makedirs(detailed_results_destination)

	indice_attr_date=None
	COMPLETLY_OPTIONAL_FOR_DATE_PRINTING=True
	description_attributes_items_names=[x[0] for x in description_attributes_items]
	description_attributes_users_names=[x[0] for x in description_attributes_users]
	if COMPLETLY_OPTIONAL_FOR_DATE_PRINTING:
		if 'VOTE_DATE' in description_attributes_items_names:
			indice_attr_date=description_attributes_items_names.index('VOTE_DATE')
	# print description_attributes_users
	# print description_attributes_items
	# raw_input('....')


	for e_u_p,e_u_label,quality,borne_max_quality,e_u_p_ext,e_u_p_ext_bitset,ref_sim,pattern_sim in sorted_interesting_patterns:

		e_u_list_label=list(e_u_label)
		if COMPLETLY_OPTIONAL_FOR_DATE_PRINTING and indice_attr_date is not None:
			#print e_u_label[indice_attr_date]
			#2014-10-21 12:52:08
			dates=[from_string_to_date(items_metadata[e]['VOTE_DATE_DETAILED'],dateformat="%Y-%m-%d %H:%M:%S") for e in e_u_p_ext[0]]
			min_date=min(dates)
			max_date=max(dates)
			#print from_date_to_string(min_date,"%d %B %Y"),from_date_to_string(max_date,"%d %B %Y")
			e_u_list_label[0]=list(e_u_list_label[0])
			if False:
				e_u_list_label[0][indice_attr_date]=' between ' + from_date_to_string(min_date,"%d %B %Y") +  ' and ' + from_date_to_string(max_date,"%d %B %Y")+ " "
			else:
				e_u_list_label[0][indice_attr_date]=[from_date_to_string(min_date,"%d %B %Y"),from_date_to_string(max_date,"%d %B %Y")]
			
			#e_u_label[0][indice_attr_date]=' between ' + from_date_to_string(min_date,"%d %B %Y") +  ' and ' + from_date_to_string(max_date,"%d %B %Y")+ " "
			e_u_list_label[0]=tuple(e_u_list_label[0])
			e_u_label=tuple(e_u_list_label)
		obj={
			'ind':k,
			'context':pattern_printer(e_u_label[0],types_attributes_items,description_attributes_items_names), #pattern_printer
			'g1':pattern_printer(e_u_label[1],types_attributes_users,description_attributes_users_names),
			'g2':pattern_printer(e_u_label[2],types_attributes_users,description_attributes_users_names),
			'|subgroup(context)|':len(e_u_p_ext[0]),
			'|subgroup(g1)|':len(e_u_p_ext[1]),
			'|subgroup(g2)|':len(e_u_p_ext[2]),
			'|ratings(c,g1,g2)|':sum(len(all_users_to_items_outcomes.get(u,{}).viewkeys()&e_u_p_ext[0]) for u in e_u_p_ext[1]|e_u_p_ext[2]),
			#'|ratings(c,g1,g2)|':sum(sum([all_users_to_items_outcomes[u][e][1] for e in all_users_to_items_outcomes.get(u,{}).viewkeys()&e_u_p_ext[0]]) for u in e_u_p_ext[1]|e_u_p_ext[2]),
			'quality':quality,#'%.2f'%quality,
			'ref_sim':ref_sim,#'%.2f'%ref_sim,
			'pattern_sim':pattern_sim#'%.2f'%pattern_sim
		}





		to_write.append(obj)


		if CSV_RESULTS_FILE_FOR_GAT_ANTOINE:
			dictionnaire_antoine={
				'PROCEDURE_SUBJECT':'subject',
				'VOTE_DATE':'date',
				'NATIONAL_PARTY':'NP',
				'GROUPE_ID':'EPG',
				'GENDER':'Gender',
				'COUNTRY':'Country',
			}
			obj_for_gat={
				'ind':k,
				'context':[pattern_printer_one([e_u_label[0][z]],[types_attributes_items[z]],[description_attributes_items_names[z]]) for z in range(len(e_u_label[0]))],#pattern_printer(e_u_label[0],types_attributes_items,description_attributes_items_names), #pattern_printer_detailed
				'meta_context':[dictionnaire_antoine.get(z,z) for z in description_attributes_items_names],
				'g1':[pattern_printer_one([e_u_label[1][z]],[types_attributes_users[z]],[description_attributes_users_names[z]]) for z in range(len(e_u_label[1]))],#pattern_printer(e_u_label[1],types_attributes_users,description_attributes_users_names),
				'meta_g1':[dictionnaire_antoine.get(z,z) for z in description_attributes_users_names],
				'g2':[pattern_printer_one([e_u_label[2][z]],[types_attributes_users[z]],[description_attributes_users_names[z]]) for z in range(len(e_u_label[2]))],#e_u_label[2],#pattern_printer(e_u_label[2],types_attributes_users,description_attributes_users_names),
				'meta_g2':[dictionnaire_antoine.get(z,z) for z in description_attributes_users_names],
				'|subgroup(context)|':len(e_u_p_ext[0]),
				'|subgroup(g1)|':len(e_u_p_ext[1]),
				'|subgroup(g2)|':len(e_u_p_ext[2]),
				'|ratings(c,g1,g2)|':sum(len(all_users_to_items_outcomes.get(u,{}).viewkeys()&e_u_p_ext[0]) for u in e_u_p_ext[1]|e_u_p_ext[2]),
				#'|ratings(c,g1,g2)|':sum(sum([all_users_to_items_outcomes[u][e][1] for e in all_users_to_items_outcomes.get(u,{}).viewkeys()&e_u_p_ext[0]]) for u in e_u_p_ext[1]|e_u_p_ext[2]),
				'quality':quality,#'%.2f'%quality,
				'ref_sim':ref_sim,#'%.2f'%ref_sim,
				'pattern_sim':pattern_sim#'%.2f'%pattern_sim
			}
			indices_to_keep=[zindex for zindex,z in enumerate(obj_for_gat['context']) if z!='*']
			obj_for_gat['context']=[obj_for_gat['context'][z] for z in indices_to_keep]
			obj_for_gat['meta_context']=[obj_for_gat['meta_context'][z] for z in indices_to_keep]

			indices_to_keep=[zindex for zindex,z in enumerate(obj_for_gat['g1']) if z!='*']
			obj_for_gat['g1']=[obj_for_gat['g1'][z] for z in indices_to_keep]
			obj_for_gat['meta_g1']=[obj_for_gat['meta_g1'][z] for z in indices_to_keep]

			indices_to_keep=[zindex for zindex,z in enumerate(obj_for_gat['g2']) if z!='*']
			obj_for_gat['g2']=[obj_for_gat['g2'][z] for z in indices_to_keep]
			obj_for_gat['meta_g2']=[obj_for_gat['meta_g2'][z] for z in indices_to_keep]

			#print obj_for_gat['context'],type(obj_for_gat['context'])
			to_write_for_GAT.append(obj_for_gat)
		k+=1
	writeCSVwithHeader(to_write,file_destination,selectedHeader=['ind','context','g1','g2','|subgroup(context)|','|subgroup(g1)|','|subgroup(g2)|','|ratings(c,g1,g2)|','ref_sim','pattern_sim','quality'])
	if CSV_RESULTS_FILE_FOR_GAT_ANTOINE:
		filename, file_extension = splitext(file_destination)
		file_destination_for_gat=filename+'_FOR_GAT'+file_extension
		writeCSVwithHeader(to_write_for_GAT,file_destination_for_gat,selectedHeader=['ind','meta_context','context','meta_g1','g1','meta_g2','g2','|subgroup(context)|','|subgroup(g1)|','|subgroup(g2)|','|ratings(c,g1,g2)|','ref_sim','pattern_sim','quality'])

	to_write=[]
	k=1
	for e_u_p,e_u_label,quality,borne_max_quality,e_u_p_ext,e_u_p_ext_bitset,ref_sim,pattern_sim in sorted_interesting_patterns:
		#print e_u_p, quality, ref_sim ,pattern_sim

		obj={
			'ind':k,
			'context':pattern_printer_detailed(e_u_label[0],types_attributes_items,description_attributes_items_names),
			'g1':pattern_printer_detailed(e_u_label[1],types_attributes_users,description_attributes_users_names),
			'g2':pattern_printer_detailed(e_u_label[2],types_attributes_users,description_attributes_users_names),
			'|subgroup(context)|':len(e_u_p_ext[0]),
			'|subgroup(g1)|':len(e_u_p_ext[1]),
			'|subgroup(g2)|':len(e_u_p_ext[2]),
			'|ratings(c,g1,g2)|':sum(len(all_users_to_items_outcomes.get(u,{}).viewkeys()&e_u_p_ext[0]) for u in e_u_p_ext[1]|e_u_p_ext[2]),
			#'|ratings(c,g1,g2)|':sum(sum([all_users_to_items_outcomes[u][e][1] for e in all_users_to_items_outcomes.get(u,{}).viewkeys()&e_u_p_ext[0]]) for u in e_u_p_ext[1]|e_u_p_ext[2]),
			'quality':'%.2f'%quality,
			'ref_sim':'%.2f'%ref_sim,
			'pattern_sim':'%.2f'%pattern_sim
		}
		to_write.append(obj)
		# print e_u_p
		# print [items_metadata[e] for e in e_u_p_ext[0]]
		# print '--------'

		if WRITE_MORE_DETAILS:





			if type_of_data=='EPD':
				#print str(k) + ' additional informations saved ....'
				#print ''
				REF_computed=False
				DIMENSION_CONSIDERED='COUNTRY'#GROUPE_ID
				all_votes_id=set(items_metadata.keys())
				outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)






				all_agg_votes=compute_aggregates_outcomes(all_votes_id,set(users_metadata.keys()),all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome='VECTOR_VALUES')

				if DRAW_FIGURES:

					groups={}
					for key,value in users_metadata.iteritems():
						value[DIMENSION_CONSIDERED]=unicodedata.normalize('NFD', unicode(str(value[DIMENSION_CONSIDERED]),'iso-8859-1')).encode('ascii', 'ignore')
					for key,value in users_metadata.iteritems():
						if value[DIMENSION_CONSIDERED] not in groups:
							groups[value[DIMENSION_CONSIDERED]]=set()
						groups[value[DIMENSION_CONSIDERED]]|={key}
					outcomes_groups={}
					for gr,gr_set in groups.iteritems():
						users_aggregated_to_items_outcomes=compute_aggregates_outcomes(all_votes_id,gr_set,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome='VECTOR_VALUES')
						outcomes_groups[gr]=users_aggregated_to_items_outcomes
					similarities_groups={}
					for gr1 in outcomes_groups:
						similarities_groups[gr1]={}
						for gr2 in outcomes_groups:
							sim,nb=similarity_vector_measure_dcs(e_u_p_ext[0],outcomes_groups[gr1],outcomes_groups[gr2],'1','2',method='MAAD')
							similarities_groups[gr1][gr2]=sim/float(nb) if nb >0. else float('NaN')
							#print gr1,gr2, similarities_groups[gr1][gr2]
					if not REF_computed:
						similarities_groups_ref={}
						for gr1 in outcomes_groups:
							similarities_groups_ref[gr1]={}
							for gr2 in outcomes_groups:
								sim,nb=similarity_vector_measure_dcs(all_votes_id,outcomes_groups[gr1],outcomes_groups[gr2],'1','2',method='MAAD')
								similarities_groups_ref[gr1][gr2]=sim/float(nb)  if nb >0. else float('NaN')
								#print gr1,gr2, similarities_groups_ref[gr1][gr2]

						matrice_ref=transformMatricFromDictToList(similarities_groups_ref)
					matrice_pattern=transformMatricFromDictToList(similarities_groups)


					from heatmap.heatmap import generateHeatMap
					#adaptMatrices
					cp_matrice_pattern=generateHeatMap(matrice_pattern,detailed_results_destination+str(k).zfill(4)+'_pattern.jpg',vmin=0.,vmax=1.,showvalues_text=False,only_heatmap=True,organize=True)#,title=title,highlight=highlight_way)

					innerMatrix,rower,header=getInnerMatrix(cp_matrice_pattern)
					rower=[rower[r] for r in sorted(rower)]
					header=[header[r] for r in sorted(header)]
					rower_inv={v:key for key,v in enumerate(rower)}
					header_inv={v:key for key,v in enumerate(header)}

					innerMatrix_ref,rower_ref,header_ref=getInnerMatrix(matrice_ref)
					rower_ref=[rower_ref[r] for r in sorted(rower_ref)]
					header_ref=[header_ref[r] for r in sorted(header_ref)]
					rower_ref_inv={v:key for key,v in enumerate(rower_ref)}
					header_ref_inv={v:key for key,v in enumerate(header_ref)}


					new_inner_matrix=[[innerMatrix_ref[rower_ref_inv[rowVal]][header_ref_inv[headVal]] for headVal in header] for rowVal in rower]
					matrice_ref_new=getCompleteMatrix(new_inner_matrix,{xx:yy for xx,yy in enumerate(rower)},{xx:yy for xx,yy in enumerate(header)})

					generateHeatMap(matrice_ref_new,detailed_results_destination+str(k).zfill(4)+'_ref.jpg',vmin=0.,vmax=1.,showvalues_text=False,only_heatmap=True,organize=False)#,title=title,highlight=highlight_way)

				TO_WRITE_DETAILS_U1=[]

				dictionnary_of_similarities_granular={}
				g1_agg_votes=compute_aggregates_outcomes(all_votes_id,e_u_p_ext[1],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome='VECTOR_VALUES')
				g2_agg_votes=compute_aggregates_outcomes(all_votes_id,e_u_p_ext[2],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome='VECTOR_VALUES')

				for e in e_u_p_ext[0]:
					dictionnary_of_similarities_granular[e]=similarity_vector_measure_dcs({e},g1_agg_votes,g2_agg_votes,'1','2',method='MAAD')
					dictionnary_of_similarities_granular[e]=dictionnary_of_similarities_granular[e][0]/float(dictionnary_of_similarities_granular[e][1]) if float(dictionnary_of_similarities_granular[e][1])>0 else '-'
				for e in e_u_p_ext[0]:
					d={}
					d.update(items_metadata[e])
					d['SIM']=dictionnary_of_similarities_granular[e]
					if True:
						if 'MAJORITY_VOTE' not in d:
							d['MAJORITY_VOTE']=''
						if 'MAJORITY_VOTE_DISTRIBUTION' not in d:
							d['MAJORITY_VOTE_DISTRIBUTION']=''

					# d['MAJORITY_VOTE']=vector_of_action[all_agg_votes[e].index(max(all_agg_votes[e]))]
					# d['MAJORITY_VOTE_DISTRIBUTION']=list(all_agg_votes[e])[::-1]
					#print all_agg_votes[e], vector_of_action[all_agg_votes[e].index(max(all_agg_votes[e]))]
					#raw_input('....')
					#d.update(users_metadata[i1])
					TO_WRITE_DETAILS_U1.append(d)
					#print str(vector_of_action)




				entities_file_selected_header=[items_id_attribute]+sorted([x for x in items_metadata.values()[0].keys() if x not in {items_id_attribute,'MAJORITY_VOTE','MAJORITY_VOTE_DISTRIBUTION'}])+['SIM','MAJORITY_VOTE','MAJORITY_VOTE_DISTRIBUTION']
				users_file_selected_header=[users_id_attribute]+sorted([x for x in users_metadata.values()[0].keys() if x!=users_id_attribute])
				writeCSVwithHeader(TO_WRITE_DETAILS_U1,detailed_results_destination+str(k).zfill(4)+'_entities'+'.csv',selectedHeader=entities_file_selected_header)
				writeCSVwithHeader([users_metadata[i] for i in e_u_p_ext[1]],detailed_results_destination+str(k).zfill(4)+'_g1'+'.csv',selectedHeader=users_file_selected_header)
				writeCSVwithHeader([users_metadata[i] for i in e_u_p_ext[2]],detailed_results_destination+str(k).zfill(4)+'_g2'+'.csv',selectedHeader=users_file_selected_header)



				mapping_vector_actions={}
				for x in range(len(vector_of_action)):
					o=[0]*len(vector_of_action);o[x]=1
					mapping_vector_actions[tuple(o)]=vector_of_action[x]

				g1_outcomes=[{items_id_attribute:e, users_id_attribute:i,'outcome':mapping_vector_actions[all_users_to_items_outcomes[i][e]] if e in all_users_to_items_outcomes[i] else '-'} for e in e_u_p_ext[0] for i in e_u_p_ext[1] ]
				g2_outcomes=[{items_id_attribute:e, users_id_attribute:i,'outcome':mapping_vector_actions[all_users_to_items_outcomes[i][e]] if e in all_users_to_items_outcomes[i] else '-'} for e in e_u_p_ext[0] for i in e_u_p_ext[2] ]

				writeCSVwithHeader(g1_outcomes,detailed_results_destination+str(k).zfill(4)+'_g1_outcomes'+'.csv',selectedHeader=[items_id_attribute,users_id_attribute,'outcome'])
				writeCSVwithHeader(g2_outcomes,detailed_results_destination+str(k).zfill(4)+'_g2_outcomes'+'.csv',selectedHeader=[items_id_attribute,users_id_attribute,'outcome'])


				writeCSVwithHeader([{items_id_attribute:e, users_id_attribute:'g1','outcome '+str(vector_of_action):g1_agg_votes[e] if e in g1_agg_votes else '-'} for e in e_u_p_ext[0]],detailed_results_destination+str(k).zfill(4)+'_g1_aggregated_outcomes'+'.csv',selectedHeader=[items_id_attribute,users_id_attribute,'outcome '+str(vector_of_action)])
				writeCSVwithHeader([{items_id_attribute:e, users_id_attribute:'g2','outcome '+str(vector_of_action):g2_agg_votes[e] if e in g2_agg_votes else '-'} for e in e_u_p_ext[0]],detailed_results_destination+str(k).zfill(4)+'_g2_aggregated_outcomes'+'.csv',selectedHeader=[items_id_attribute,users_id_attribute,'outcome '+str(vector_of_action)])




				REF_computed=True





			else:
				TO_WRITE_DETAILS_U1=[]
				TO_WRITE_AGG_U1=[]
				BIG_V1={}
				BIG_V1_REF={}
				BIG_V1_POP={}
				for e in e_u_p_ext[0]:
					vector={}
					for i1 in e_u_p_ext[1]:
						try:
							outcome=all_users_to_items_outcomes[i1][e]
							vector[outcome[0]]=vector.get(outcome[0],0.)+1

							if type_of_data=='MOVIELENS':
								BIG_V1[outcome[0]]=BIG_V1.get(outcome[0],0.)+1
							elif type_of_data=='YELP':
								for note in range(5):
									ind_note=note+1
									BIG_V1[ind_note]=BIG_V1.get(ind_note,0.)+outcome[2][note]
							elif type_of_data=='OPENMEDIC':
								#BIG_V1['sizepop']=
								BIG_V1['Context']=BIG_V1.get('Context',0.)+outcome[0]

							d={'outcome':outcome}
							d.update(items_metadata[e])
							d.update(users_metadata[i1])
							TO_WRITE_DETAILS_U1.append(d)


						except Exception as excepas:
							continue
					TO_WRITE_AGG_U1.append({items_id_attribute:e,'outcome':[vector.get(x,0.) for x in range(1,6)]})

				if COMPUTE_REF:
					for i1 in e_u_p_ext[1]:
						for e in all_users_to_items_outcomes[i1]:
							outcome=all_users_to_items_outcomes[i1][e]
							if type_of_data=='MOVIELENS':
								BIG_V1_REF[outcome[0]]=BIG_V1_REF.get(outcome[0],0.)+1
							elif type_of_data=='YELP':
								for note in range(5):
									ind_note=note+1
									BIG_V1_REF[ind_note]=BIG_V1_REF.get(ind_note,0.)+outcome[2][note]
							elif type_of_data=='OPENMEDIC':
								#BIG_V1['sizepop']=
								BIG_V1_REF['*']=BIG_V1_REF.get('*',0.)+outcome[0]

						if type_of_data=='OPENMEDIC':
							BIG_V1_POP['Population']=BIG_V1_POP.get('Population',0.) + users_metadata[i1]['sizeOfPop']






				TO_WRITE_AGG_U1.append({items_id_attribute:'*','outcome':[BIG_V1.get(x,0.) for x in range(1,6)]})
				writeCSVwithHeader(TO_WRITE_DETAILS_U1,detailed_results_destination+str(k).zfill(4)+'_u1'+'.csv',selectedHeader=[items_id_attribute]+[x for x in items_metadata.values()[0].keys() if x!=items_id_attribute]+[users_id_attribute]+[x for x in users_metadata.values()[0].keys() if x!=users_id_attribute]+['outcome'])
				writeCSVwithHeader(TO_WRITE_AGG_U1,detailed_results_destination+str(k).zfill(4)+'_u1_agg'+'.csv',selectedHeader=[items_id_attribute,'outcome'])
				if DRAW_FIGURES:
					from plotter.perfPlotter import plot_bars_vector,plot_bars_vector_many_populations
					vector_for_movielens=[BIG_V1.get(x,0.) for x in range(1,6)]
					plot_bars_vector(vector_for_movielens,detailed_results_destination+str(k).zfill(4)+'_u1_agg'+'.pdf')

				TO_WRITE_DETAILS_U2=[]
				TO_WRITE_AGG_U2=[]
				BIG_V2={}
				BIG_V2_REF={}
				BIG_V2_POP={}
				for e in e_u_p_ext[0]:
					vector={}
					for i2 in e_u_p_ext[2]:
						try:
							outcome=all_users_to_items_outcomes[i2][e]
							vector[outcome[0]]=vector.get(outcome[0],0.)+1
							if type_of_data=='MOVIELENS':
								BIG_V2[outcome[0]]=BIG_V2.get(outcome[0],0.)+1
							elif type_of_data=='YELP':
								for note in range(5):
									ind_note=note+1
									BIG_V2[ind_note]=BIG_V2.get(ind_note,0.)+outcome[2][note]
							elif type_of_data=='OPENMEDIC':
								#BIG_V1['sizepop']=
								BIG_V2['Context']=BIG_V2.get('Context',0.)+outcome[0]

							d={'outcome':outcome}
							d.update(items_metadata[e])
							d.update(users_metadata[i2])
							TO_WRITE_DETAILS_U2.append(d)


						except Exception as excepas:
							continue
					TO_WRITE_AGG_U2.append({items_id_attribute:e,'outcome':[vector.get(x,0.) for x in range(1,6)]})

				if COMPUTE_REF:
					for i2 in e_u_p_ext[2]:
						for e in all_users_to_items_outcomes[i2]:
							outcome=all_users_to_items_outcomes[i2][e]
							if type_of_data=='MOVIELENS':
								BIG_V2_REF[outcome[0]]=BIG_V2_REF.get(outcome[0],0.)+1
							elif type_of_data=='YELP':
								for note in range(5):
									ind_note=note+1
									BIG_V2_REF[ind_note]=BIG_V2_REF.get(ind_note,0.)+outcome[2][note]
							elif type_of_data=='OPENMEDIC':
								#BIG_V1['sizepop']=
								BIG_V2_REF['*']=BIG_V2_REF.get('*',0.)+outcome[0]

						if type_of_data=='OPENMEDIC':
							BIG_V2_POP['Population']=BIG_V2_POP.get('Population',0.) + users_metadata[i2]['sizeOfPop']

				if type_of_data=='OPENMEDIC':

					# print obj['g1'],BIG_V1,BIG_V1_REF,BIG_V1_POP
					# print obj['g2'],BIG_V2,BIG_V2_REF,BIG_V2_POP
					# print obj['quality'],obj['ref_sim'],obj['pattern_sim']
					dictus1={};dictus1.update(BIG_V1);dictus1.update(BIG_V1_REF);dictus1.update(BIG_V1_POP)
					dictus2={};dictus2.update(BIG_V2);dictus2.update(BIG_V2_REF);dictus2.update(BIG_V2_POP)
					dictus={pattern_printer(e_u_label[1],types_attributes_users):dictus1,pattern_printer(e_u_label[2],types_attributes_users):dictus2}
					#dictus.update(BIG_V1)
					if DRAW_FIGURES:
						from plotter.perfPlotter import plot_bars_vector_many_populations_openmedic
						plot_bars_vector_many_populations_openmedic(dictus,detailed_results_destination+str(k).zfill(4)+'_patternAndRef'+'.pdf',['Population','*','Context'])
					#raw_input('...')

				TO_WRITE_AGG_U2.append({items_id_attribute:'*','outcome':[BIG_V2.get(x,0.) for x in range(1,6)]})
				writeCSVwithHeader(TO_WRITE_DETAILS_U2,detailed_results_destination+str(k).zfill(4)+'_u2'+'.csv',selectedHeader=[items_id_attribute]+[x for x in items_metadata.values()[0].keys() if x!=items_id_attribute]+[users_id_attribute]+[x for x in users_metadata.values()[0].keys() if x!=users_id_attribute]+['outcome'])
				writeCSVwithHeader(TO_WRITE_AGG_U2,detailed_results_destination+str(k).zfill(4)+'_u2_agg'+'.csv',selectedHeader=[items_id_attribute,'outcome'])

				if type_of_data in {'MOVIELENS','YELP'}:
					pattern_u1_movielens=[BIG_V1.get(x,0.) for x in range(1,6)]
					pattern_u2_movielens=[BIG_V2.get(x,0.) for x in range(1,6)]
					ref_u1_movielens=[BIG_V1_REF.get(x,0.) for x in range(1,6)]
					ref_u2_movielens=[BIG_V2_REF.get(x,0.) for x in range(1,6)]
					# print BIG_V1
					# print BIG_V1_REF
					# raw_input('...')
					if DRAW_FIGURES:
						from plotter.perfPlotter import plot_bars_vector
						DICT_VECTOR={pattern_printer(e_u_label[1],types_attributes_users):pattern_u1_movielens,pattern_printer(e_u_label[2],types_attributes_users):pattern_u2_movielens}
						plot_bars_vector_many_populations(DICT_VECTOR,detailed_results_destination+str(k).zfill(4)+'_u2_agg'+'.pdf')
						DICT_VECTOR={pattern_printer(e_u_label[1],types_attributes_users):ref_u1_movielens,pattern_printer(e_u_label[2],types_attributes_users):ref_u2_movielens}
						plot_bars_vector_many_populations(DICT_VECTOR,detailed_results_destination+str(k).zfill(4)+'_u2_agg_referencial'+'.pdf')
		k+=1
	#writeCSVwithHeader(to_write,file_destination,selectedHeader=['ind','context','g1','g2','|subgroup(context)|','|subgroup(g1)|','|subgroup(g2)|','|ratings(c,g1,g2)|','ref_sim','pattern_sim','quality'])
	#raw_input('....')
	return [(eup_l,eup_ext,e_u_p_ext_bitset) for (eup,eup_l,qual,borne_max_quality,eup_ext,e_u_p_ext_bitset,_,_) in sorted_interesting_patterns]


def del_from_list_by_index(l,del_indexes):
	del_indexes_new_indexes=[];del_indexes_new_indexes_append=del_indexes_new_indexes.append
	if len(del_indexes):
		del l[del_indexes[0]]
		del_indexes_new_indexes_append(del_indexes[0])
		for k in range(1,len(del_indexes)):
			del_indexes_new_indexes_append((del_indexes[k]-del_indexes[k-1])+del_indexes_new_indexes[k-1]-1)
			del l[del_indexes_new_indexes[-1]]#l[del_indexes[k]-del_indexes[k-1]]


def worse_action_vector_expected(vec_start,vec_to_compare_with,threshold_nb_deputy=1):
	index_max_vec_to_compare_with=0;max_vec_to_compare_with=vec_to_compare_with[0]
	for k in range(1,len(vec_to_compare_with)):
		vec_value=vec_to_compare_with[k]
		if max_vec_to_compare_with<vec_value:
			index_max_vec_to_compare_with=k
			max_vec_to_compare_with=vec_value
	nb_in_vote=sum(vec_start)
	maximum_to_eliminate=max(nb_in_vote-threshold_nb_deputy,0)
	worse_vector=list(vec_start)
	worse_vector[index_max_vec_to_compare_with]=worse_vector[index_max_vec_to_compare_with]-min(worse_vector[index_max_vec_to_compare_with],maximum_to_eliminate)
	return tuple(worse_vector)



	#print index_max_vec_to_compare_with,max_vec_to_compare_with




#########
'''
TODO For enumerating peers:
   * Orders_not_after_closure for themes and numeric
TODO:
   * Find a way to compute the maximim expected from a peer (d1,d2) or a at least from a specialization from d2
   * Heuristic: Compute the perturbation of d1,d2 (at least d2) in a way and then consider it during the enumeration
TODO for enumerators:
   * put in config the attributePattern and the refinementIndexactu for not closed complex enumerator (MUST BE DONE)
TODO for DSC:
   * fix all the parameters
   * For DSC entrypoint give a JSON file in entry specifying all parameters
   * Find a way to reduce this subsumption verification, it will help a lot
TODO for post-treatement:
   * Regroup results by contexts and then by d1,d2 if possible
   * Give a way to compute the support from only the pattern (must be done to quicken the algorithm and allow to recompute the support for visualization at the last part this seems to be easy)
TODO for tests:
   * Test on the others dataset
   * Fix EPD8 and EPD78 (the new ones) to use them on the data (for this we must give a new id for a voter each time he changes his party or group)
   * Test on this both datasets
TODO in general for Monday work point with Marc, Philippe and Sylvie:
   * Fix the figure (DSC overview) so it will cover the new instance (Semi DONE!)
   * I need to debelop this perturbation point before the reunion so I can justify otherwise I just explicit its semantic
Good luck Monday Adnene :-) (A message from Friday Adnane)
	# EVIT sorting each time for UB2
	* update contextDiscovered even when you backtrack in enumeration and expand it over U1 so it will work DONE
	# BFS and not closed enumeration for that couple enumeration (in the bfs one we just need to fix the order issue between description)



#Paper
## Introduction
## Problem definition (Minimal exceptional pariwise behavior pattern)
## DSC-EX
### Description space and candidates generation (includes HMT in here and provide algorithm for enumeration)
### Pairiwse behavior model (aggregation and similairies  or pairwise behavior observation measure (Generic definition first))
### Comparing two pairwise behavior model (Generic definition for the quality measure + Upperbound) (Two basic quality measures, explain how we can extend to get matrices if we want or other measures)
### Algorithm for DSC - include enumeration, computation of the model and prunning (UB and when it exceeds the upper bound)
## DSC-HEURISTIC
### Provide a heuristic (either perturbation story with DSSD or beam search or try Sampling)
## Patterns visualization to get quick insights
### Regroup patterns based on context (Onto one matrix)
### Aggregate on different level of aggregation to get better insights ?

#SCENARIOS (Qualitative and Quantitative Xperiments)
## Analyzing votes datasets:
### Case of comparing majority (EPD8 EPD7 and EPD6 and then EPD678)
### Case of cohesion measures
## Analyzing review datasets:
### Case of Yelp
### Case of movielens
## Analyzing the medicines consumption behavior for elucidating sicknesses prevalance:
### Use of OPENMEDIC
### Analyzing the Mustapha datasets to get groups having distinct similarities on odors (context are groups of odors) and groups are identified by whether or not an individual smoke, weight  ...

#TODO
#init_config: put the new indices for each new couple and REMOVE <#TOREMOVE BIATCH !> !!


'''
#345 133026.0 32.9100000858 1.26000070572 6.154992342
#1016 394827.0 54.1749999523 2.28300333023 21.7640013695
##########
def DSC(itemsMetadata,users_metadata,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,all_users_to_items_outcomes,
		items_id_attribute,users_id_attribute,description_attributes_items=[],description_attributes_users=[],method_aggregation_outcome='VECTOR_VALUES',
		comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
		ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',consider_order_between_desc_of_couples=True,nb_random_walks=30,verbose=False):

	estimated_maximum_number_of_called_peers= DSC.stats.get('estimated_maximum_number_of_called_peers',1.)
	nb_visited=[0.,0.,0.]
	TEST_SUBSUMPTION_WITH_BISET=True
	CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES=consider_order_between_desc_of_couples
	started=time()
	subsumption_verif_time=0.
	enumeration_on_contexts_time=0.

	get_items_ids = partial(map,itemgetter(items_id_attribute))
	get_users_ids = partial(map,itemgetter(users_id_attribute))

	v_ids_all_list=get_items_ids(considered_items_sorted)
	v_ids_all=set(v_ids_all_list)
	u_1_ids=set(get_users_ids(considered_users_1_sorted))
	u_2_ids=set(get_users_ids(considered_users_2_sorted))

	outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)
	

	interesting_patterns=[]
	interesting_patterns_append=interesting_patterns.append
	index_visited=0.
	#########PARAMS TO GIVE AS INPUT#########
	types_attributes_users=[x['type'] for x in description_attributes_users]
	types_attributes_items=[x['type'] for x in description_attributes_items]

	votes_map_ponderations={}
	u1_name='u1'
	u2_name='u2'
	lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False
	top_k=float('inf')
	#########PARAMS TO GIVE AS INPUT#########

	how_much_visited={'visited':0}
	initConfig={'config':None,'attributes':None}
	nb_pairs=0.
	enumerator_pairs=enumerator_pair_of_users_optimized_dfs(users_metadata,considered_users_1_sorted,considered_users_2_sorted,users_id_attribute,all_users_to_items_outcomes,v_ids_all,description_attributes_users,threshold_nb_users_1,threshold_nb_users_2,outcome_tuple_structure,how_much_visited,method_aggregation_outcome,only_square_matrix=False,closed=closed,do_heuristic=do_heuristic_peers,heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES)
	for (u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config),(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config) in enumerator_pairs:
		nb_pairs+=1
		if verbose:
			stdout.write('%s\r' % ('Percentage Done : ' + ('%.2f'%((nb_pairs/estimated_maximum_number_of_called_peers)*100))+ '%'));stdout.flush();
		#print u1_p,u2_p, s1,s2

		# raw_input('***')
		if (time()-started)>timebudget:break
		if do_heuristic_peers:
			del u2_config['mss_node']['elements_to_yield']
		votes_in_which_the_two_groups_participated=users1_aggregated_to_items_outcomes.viewkeys()&users2_aggregated_to_items_outcomes.viewkeys()

		if len(votes_in_which_the_two_groups_participated)<threshold_comparaison: continue

		userpairssimsdetails={v: similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, users2_aggregated_to_items_outcomes,u1_name,u2_name,comparaison_measure)[0]
								 for v in votes_in_which_the_two_groups_participated}

		# print '_____________'
		# #for u in users1_aggregated_to_items_outcomes:
		# for e in users1_aggregated_to_items_outcomes:
		# 	print users1_aggregated_to_items_outcomes[e]
		# 	print users2_aggregated_to_items_outcomes[e]
		# 	print userpairssimsdetails[e]
		# 	raw_input('..')						 


		############################
		if (type(ponderation_attribute) is int): #This is particular for ratio need to reconsider
			s1=float(sum(users_metadata[k]['sizeOfPop'] for k in u1_p_set_users))
			s2=float(sum(users_metadata[k]['sizeOfPop'] for k in u2_p_set_users))
			ratio = (float(s2)/float(s1))
			userpairssimsdetails={k:(ratio*v) for k,v in userpairssimsdetails.iteritems()}
			votes_map_ponderations={v:users2_aggregated_to_items_outcomes[v][0] for v in votes_in_which_the_two_groups_participated}
		############################

		nbSimItems,nbItems,bound=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_all,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations=votes_map_ponderations)
		reference_matrix=[[(nbSimItems,nbItems)]]
		reference_similarity=(nbSimItems/nbItems)
		# print "       "
		# print u1_p,u2_p,reference_similarity,bound
		# print "       "
		if pruning:
			UP_BOUND_FROM_THIS_COUPLE=max(0,(nbSimItems/nbItems)-bound)  if qualityMeasure == 'DISAGR_SUMDIFF'  else max(0,bound-nbSimItems/nbItems) if qualityMeasure == 'AGR_SUMDIFF' else bound/(nbSimItems/nbItems)
			if UP_BOUND_FROM_THIS_COUPLE<quality_threshold: continue

		######################HEURISTIC HANDLING#########################
			# HEURISTIC_NAME='RN_DIFFERENCE_REFERENCE'
			# if do_heuristic and HEURISTIC_NAME=='RN_DIFFERENCE_REFERENCE':
			# 	u2_config['parent_ref']=u2_config.get('ref',0.)
			# 	u2_config['ref']=(nbSimItems/nbItems)
			# 	u2_config['quality']=abs(u2_config['ref']-u2_config['parent_ref'])
			# 	if not u2_config.get('considerme',False):
			# 		continue
		#################################################################
		u1_p_extent_bitset=u1_config['indices_bitset_1']
		u2_p_extent_bitset=u2_config['indices_bitset_2']
		indices_to_consider={k for k in range(len(v_ids_all_list)) if v_ids_all_list[k] in votes_in_which_the_two_groups_participated}
		indices_to_consider_bitset=encode_sup(sorted(indices_to_consider),len(v_ids_all_list))
		config_updater={'indices':indices_to_consider,'indices_bitset':indices_to_consider_bitset,'nb_visited':nb_visited}
		enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items, config_updater,threshold=threshold_comparaison,verbose=False,bfs=False,closed=closed,do_heuristic=do_heuristic_contexts,initValues=initConfig)

		for e_p,e_label,e_config in enumerator_contexts:
			if (time()-started)>timebudget:break
			st=time()
			#print e_p
			e_p_ext=e_config['indices_bitset']
			index_visited+=1
			if TEST_SUBSUMPTION_WITH_BISET:
				if any(ext_subsume_ext(context_already_visited_bitset,e_p_ext,types_attributes_items) for ((context_already_visited,_,_),(context_already_visited_bitset,_,_)) in u2_config['contextsVisited']):
					e_config['flag']=False
					continue
			else:
				if any(pattern_subsume_pattern(context_already_visited,e_p,types_attributes_items) for ((context_already_visited,_,_),(context_already_visited_bitset,_,_)) in u2_config['contextsVisited']):
					e_config['flag']=False
					continue

			e_u_p=(e_p,u1_p,u2_p)

			e_u_label=(e_label,u1_label,u2_label)
			e_votes=e_config['support']
			v_ids_pattern=set(get_items_ids(e_votes))
			e_u_p_extent=(v_ids_pattern,u1_p_set_users,u2_p_set_users)

			e_u_p_extent_bitset=(e_config['indices_bitset'],u1_p_extent_bitset,u2_p_extent_bitset)


			agg_p,all_p,worst_sim_expected=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_pattern,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations)

			pattern_matrix=[[(agg_p,all_p,worst_sim_expected)]]
			pattern_similarity=agg_p/all_p
			quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_comparaison,qualityMeasure)
			e_config['quality']=quality
			e_config['upperbound']=borne_max_quality

			enumeration_on_contexts_time+=time()-st
			if (pruning and borne_max_quality<quality_threshold):
				e_config['flag']=False
				continue


			if (quality>=quality_threshold):

				e_p_dominated=False
				st=time()
				to_delete=[];to_delete_append=to_delete.append
				#################subsumption_verification#########################
				for k in range(len(interesting_patterns)):
					context_already_visited=interesting_patterns[k][0][0]
					pattern_already_visited=interesting_patterns[k][0]
					pattern_bitset_extent_already_visited=interesting_patterns[k][5]
					pattern_extent_already_visited=interesting_patterns[k][4]
					if TEST_SUBSUMPTION_WITH_BISET:
						if DSC_EXT_subsume_DSC_EXT(pattern_bitset_extent_already_visited,e_u_p_extent_bitset,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES):
							e_p_dominated=True
							break
						elif DSC_EXT_subsume_DSC_EXT(e_u_p_extent_bitset,pattern_bitset_extent_already_visited,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES):
							to_delete_append(k)
					else:
						if DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users):
							e_p_dominated=True
							break
						elif DSC_Pat_subsume_DSC_Pat(e_u_p,pattern_already_visited,types_attributes_items,types_attributes_users):
							to_delete_append(k)


				if not e_p_dominated and len(to_delete):
					del_from_list_by_index(interesting_patterns,to_delete)
				e_config['flag']=False
				subsumption_verif_time+=time()-st
				#################subsumption_verification#########################


				if not e_p_dominated:
					votes_context=v_ids_pattern
					interesting_patterns_append([e_u_p,e_u_label,quality,borne_max_quality,e_u_p_extent,e_u_p_extent_bitset,reference_similarity,pattern_similarity])

				if len(interesting_patterns)>top_k:
					interesting_patterns=sorted(interesting_patterns,key = itemgetter(2),reverse=True)[:top_k]
					quality_threshold=interesting_patterns[-1][3]
		nb_visited=e_config['nb_visited']
		if (time()-started)>timebudget:break
		#raw_input('...')
		if TEST_SUBSUMPTION_WITH_BISET:
			u2_config['contextsVisited'].extend([((c,a,b),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset),_,_) in interesting_patterns if DSC_EXT_subsume_DSC_EXT((0,a_ext_bitset,b_ext_bitset),(0,u1_p_extent_bitset,u2_p_extent_bitset),types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES)])
		else:
			u2_config['contextsVisited'].extend([((c,a,b),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset),_,_) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])#pattern_subsume_pattern(a,u1_p,types_attributes_users) and pattern_subsume_pattern(b,u2_p,types_attributes_users)])# a==u1_p and b==u2_p])

		#######NEW YET NEED TO BE REMOVED - FOR HEURISTIC#######
			# HEUR=None#None
			# if False:
			# 	perturbation=0.0
			# 	#votes_already_percieved=set.union(*[x[4][0] for x in u2_config['contextsVisited']]) if len(u2_config['itemsVisited']) else set()

			# 	lel=[c_ext for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) in interesting_patterns if DSC_EXT_subsume_DSC_EXT((0,a_ext_bitset,b_ext_bitset),(0,u1_p_extent_bitset,u2_p_extent_bitset),types_attributes_items,types_attributes_users)]

			# 	if len(lel)>0:
			# 		votes_already_percieved=set.union(*lel)
			# 	else :
			# 		votes_already_percieved=set()
			# 	#print len(votes_already_percieved),len(interesting_patterns)
			# 	#raw_input('...')
			# 	#votes_already_percieved=set()
			# 	list_of_sims=[];list_of_sims_append=list_of_sims.append
			# 	for v in votes_in_which_the_two_groups_participated-votes_already_percieved:
			# 		#perturbation+=similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users2_aggregated_to_items_outcomes[v],users1_aggregated_to_items_outcomes[v],threshold_nb_users_1)},u1_name,u2_name,comparaison_measure)[0]
			# 		perturbation+=abs(userpairssimsdetails[v]-similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users2_aggregated_to_items_outcomes[v],users1_aggregated_to_items_outcomes[v],threshold_nb_users_1)},u1_name,u2_name,comparaison_measure)[0])+ \
			# 		abs(userpairssimsdetails[v]-similarity_vector_measure_dcs({v}, users2_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users1_aggregated_to_items_outcomes[v],users2_aggregated_to_items_outcomes[v],threshold_nb_users_2)},u1_name,u2_name,comparaison_measure)[0])
			# 		#list_of_sims_append(similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users2_aggregated_to_items_outcomes[v],users1_aggregated_to_items_outcomes[v],threshold_nb_users_1)},u1_name,u2_name,comparaison_measure)[0] )
			# 	perturbation=(perturbation/len(votes_in_which_the_two_groups_participated-votes_already_percieved)) #the similarity between
			# 	#print perturbation
			# 	#raw_input('...')
			# 	if False and perturbation>0.7:
			# 		u2_config['flag']=False
			# 		continue
			# 	u2_config['quality']=perturbation/2.#(2-perturbation)/2.
			# 	u2_config['upperbound']=perturbation/2.#(2-perturbation)/2.

				# if HEUR=='RN_DIF_REF':
				# 	u2_config['parent_ref']=u2_config.get('ref',0.)
				# 	u2_config['ref']=(nbSimItems/nbItems)
				# 	u2_config['quality']=abs(u2_config['ref']-u2_config['parent_ref'])
			# print sum(sorted(list_of_sims,reverse=False)[:threshold_comparaison])
			# print 1-(perturbation/len(votes_in_which_the_two_groups_participated)),len(votes_already_percieved),len(list_of_sims),sum(sorted(list_of_sims,reverse=False)[:threshold_comparaison]),
			# raw_input('...')
		###################

	#print len(interesting_patterns),index_visited,time()-started,subsumption_verif_time,enumeration_on_contexts_time,e_config['nb_visited'],u2_config['nb_visited']
	try:
		e_config=e_config
	except Exception as e:
		e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
	DSC.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
	DSC.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
	DSC.stats['nb_candidates_subgroups']=index_visited
	DSC.stats['nb_patterns']=len(interesting_patterns)
	DSC.stats['timespent']=time()-started
	DSC.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
	DSC.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']

	if heatmap_for_matrix:
		DSC.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
	yield interesting_patterns




def DSC_AnyTimeRandomWalk(itemsMetadata,users_metadata,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,all_users_to_items_outcomes,
		items_id_attribute,users_id_attribute,description_attributes_items=[],description_attributes_users=[],method_aggregation_outcome='VECTOR_VALUES',
		comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
		ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',consider_order_between_desc_of_couples=True,nb_random_walks=30,verbose=False):
	nb_visited=[0.,0.,0.]
	NB_ITER_CONTEXTS_PER_ROUND=nb_random_walks#30
	print 'NB_ITER_CONTEXTS_PER_ROUND : ',NB_ITER_CONTEXTS_PER_ROUND
	TEST_SUBSUMPTION_WITH_BISET=True
	KEEP_IN_MEMORY_STUFFS=True;MRU_SIZE=10000;
	print 'MEMORY USAGE : ', KEEP_IN_MEMORY_STUFFS
	CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES=consider_order_between_desc_of_couples
	TIMEBUDGET=timebudget

	###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
	MANY_INTERRUPTION_FLAG=False
	if type(timebudget) is list:
		MANY_INTERRUPTION_FLAG=True
		TIMEBUDGET=max(timebudget)
		FLAG=0
		TIMEBUDGET_FLAG=timebudget[FLAG]
	###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################


	started=time()
	subsumption_verif_time=0.
	enumeration_on_contexts_time=0.

	get_items_ids = partial(map,itemgetter(items_id_attribute))
	get_users_ids = partial(map,itemgetter(users_id_attribute))

	v_ids_all_list=get_items_ids(considered_items_sorted)
	v_ids_all=set(v_ids_all_list)
	u_1_ids=set(get_users_ids(considered_users_1_sorted))
	u_2_ids=set(get_users_ids(considered_users_2_sorted))

	outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)
	interesting_patterns=[]
	interesting_patterns_append=interesting_patterns.append
	index_visited=0.
	#########PARAMS TO GIVE AS INPUT#########
	types_attributes_users=[x['type'] for x in description_attributes_users]
	types_attributes_items=[x['type'] for x in description_attributes_items]

	votes_map_ponderations={}
	u1_name='u1'
	u2_name='u2'
	lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False
	top_k=float('inf')
	#########PARAMS TO GIVE AS INPUT#########

	how_much_visited={'visited':0}
	initConfig={'config':None,'attributes':None}
	MostRecentlyUsedPeer=None
	enumerator_pairs=enumerator_pair_of_users_optimized_dfs(users_metadata,considered_users_1_sorted,considered_users_2_sorted,users_id_attribute,all_users_to_items_outcomes,v_ids_all,description_attributes_users,threshold_nb_users_1,threshold_nb_users_2,outcome_tuple_structure,how_much_visited,method_aggregation_outcome,only_square_matrix=False,closed=closed,do_heuristic=do_heuristic_peers,heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES)
	for (u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config),(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config) in enumerator_pairs:
		time_it_took_since_beggining=time()-started
		if verbose: stdout.write('%s\r' % ('Percentage Done : ' + ('%.2f'%((time_it_took_since_beggining/TIMEBUDGET)*100))+ '%'));stdout.flush();
		if (time_it_took_since_beggining)>TIMEBUDGET:break

		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
		if MANY_INTERRUPTION_FLAG:
			if (time_it_took_since_beggining)>TIMEBUDGET_FLAG:
				time_it_tooked=time()
				try:
					e_config=e_config
				except Exception as e:
					e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
				DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
				DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
				DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
				DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
				DSC_AnyTimeRandomWalk.stats['timespent']=time_it_took_since_beggining
				DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
				DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
				if heatmap_for_matrix:
					DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
				yield interesting_patterns
				time_it_tooked=time()-time_it_tooked
				FLAG+=1
				TIMEBUDGET_FLAG=timebudget[FLAG]
				started+=time_it_tooked
		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################

		u1_p_extent_bitset=u1_config['indices_bitset_1']
		u2_p_extent_bitset=u2_config['indices_bitset_2']
		jump_initing_context_computation=False



		if KEEP_IN_MEMORY_STUFFS and do_heuristic_peers and 'enumerator_contexts' in u2_config['mss_node'] :
			mss_node=u2_config['mss_node']
			#enumerator_contexts=mss_node['enumerator_contexts']
			votes_map_ponderations,config_updater=mss_node['enumerator_contexts']
			enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items, config_updater,threshold=threshold_comparaison,verbose=False,bfs=False,closed=closed,do_heuristic=do_heuristic_contexts,initValues=initConfig)
			userpairssimsdetails=mss_node['userpairssimsdetails']
			reference_matrix=mss_node['reference_matrix']
			reference_similarity=mss_node['reference_similarity']
			jump_initing_context_computation=True




			# print ' '
			# print 'Hey Memory was used'
			# print ' '


		if not jump_initing_context_computation:

			votes_in_which_the_two_groups_participated=users1_aggregated_to_items_outcomes.viewkeys()&users2_aggregated_to_items_outcomes.viewkeys()
			if len(votes_in_which_the_two_groups_participated)<threshold_comparaison:
				if do_heuristic_peers: del u2_config['mss_node']['elements_to_yield']
				#print 'CASE A'
				continue
			userpairssimsdetails={v: similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, users2_aggregated_to_items_outcomes,u1_name,u2_name,comparaison_measure)[0]
									 for v in votes_in_which_the_two_groups_participated}




			############################
			if (type(ponderation_attribute) is int): #This is particular for ratio need to reconsider
				s1=float(sum(users_metadata[k]['sizeOfPop'] for k in u1_p_set_users))
				s2=float(sum(users_metadata[k]['sizeOfPop'] for k in u2_p_set_users))
				ratio = (float(s2)/float(s1))
				userpairssimsdetails={k:(ratio*v) for k,v in userpairssimsdetails.iteritems()}
				votes_map_ponderations={v:users2_aggregated_to_items_outcomes[v][0] for v in votes_in_which_the_two_groups_participated}
			############################

			nbSimItems,nbItems,bound=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_all,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations=votes_map_ponderations)
			reference_matrix=[[(nbSimItems,nbItems)]]
			reference_similarity=(nbSimItems/nbItems)



			if pruning:
				#UP_BOUND_FROM_THIS_COUPLE=max(0,(nbSimItems/nbItems)-bound)  if qualityMeasure == 'DISAGR_SUMDIFF'  else max(0,bound-nbSimItems/nbItems)
				UP_BOUND_FROM_THIS_COUPLE=max(0,(nbSimItems/nbItems)-bound)  if qualityMeasure == 'DISAGR_SUMDIFF'  else max(0,bound-nbSimItems/nbItems) if qualityMeasure == 'AGR_SUMDIFF' else bound/(nbSimItems/nbItems)
				if UP_BOUND_FROM_THIS_COUPLE<quality_threshold:
					if do_heuristic_peers: del u2_config['mss_node']['elements_to_yield']
					#print 'CASE B'
					continue


			indices_to_consider={k for k in range(len(v_ids_all_list)) if v_ids_all_list[k] in votes_in_which_the_two_groups_participated}

			indices_to_consider_bitset=2**len(v_ids_all_list)-1#encode_sup(sorted(indices_to_consider),len(v_ids_all_list)) #OLD
			#userpairssimsdetails_indices={i:max(reference_similarity-userpairssimsdetails[x[items_id_attribute]] - (quality_threshold-0.0001),0) if lower else max(userpairssimsdetails[x[items_id_attribute]]-reference_similarity - (quality_threshold-0.0001),0) for i,x in enumerate(considered_items_sorted) if x[items_id_attribute] in votes_in_which_the_two_groups_participated}

			if False:
				userpairssimsdetails_indices={i:max(reference_similarity-userpairssimsdetails[x[items_id_attribute]] - (quality_threshold-0.0001),0) if lower else max(userpairssimsdetails[x[items_id_attribute]]-reference_similarity - (quality_threshold-0.0001),0) for i,x in enumerate(considered_items_sorted) if x[items_id_attribute] in votes_in_which_the_two_groups_participated}
			else:
				#userpairssimsdetails_indices={i:max(reference_similarity-userpairssimsdetails[x[items_id_attribute]],0) if lower else max(userpairssimsdetails[x[items_id_attribute]]-reference_similarity,0) for i,x in enumerate(considered_items_sorted) if x[items_id_attribute] in votes_in_which_the_two_groups_participated}
				if True:
					userpairssimsdetails_indices={i: int((reference_similarity-userpairssimsdetails[x[items_id_attribute]] - (quality_threshold))>=0)*(reference_similarity-userpairssimsdetails[x[items_id_attribute]]) if lower else int((userpairssimsdetails[x[items_id_attribute]]-reference_similarity - (quality_threshold))>=0)*(userpairssimsdetails[x[items_id_attribute]]-reference_similarity) for i,x in enumerate(considered_items_sorted) if x[items_id_attribute] in votes_in_which_the_two_groups_participated}
				else:
					userpairssimsdetails_indices={i: int((reference_similarity-userpairssimsdetails[x[items_id_attribute]] - (quality_threshold))>=0) if lower else int((userpairssimsdetails[x[items_id_attribute]]-reference_similarity - (quality_threshold))>=0) for i,x in enumerate(considered_items_sorted) if x[items_id_attribute] in votes_in_which_the_two_groups_participated}



			config_updater={'indices':indices_to_consider,'indices_bitset':indices_to_consider_bitset,'nb_visited':nb_visited,'indices_quality':userpairssimsdetails_indices,'NB_ITER_CONTEXTS_PER_ROUND':NB_ITER_CONTEXTS_PER_ROUND}
			enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items, config_updater,threshold=threshold_comparaison,verbose=False,bfs=False,closed=closed,do_heuristic=do_heuristic_contexts,initValues=initConfig)

			if do_heuristic_peers and KEEP_IN_MEMORY_STUFFS:
				peers_materialized_tree=u2_config['materialized_search_space']
				mss_node=u2_config['mss_node']
				#mss_node['enumerator_contexts']=enumerator_contexts
				mss_node['enumerator_contexts']=[votes_map_ponderations,config_updater]#None
				mss_node['userpairssimsdetails']=userpairssimsdetails
				mss_node['reference_matrix']=reference_matrix
				mss_node['reference_similarity']=reference_similarity
				if len(peers_materialized_tree)>=MRU_SIZE and MostRecentlyUsedPeer is not None:

					del peers_materialized_tree[MostRecentlyUsedPeer]
				MostRecentlyUsedPeer=u2_config['encoded_sup']

		#nb_iter_contexts=NB_ITER_CONTEXTS_PER_ROUND
		#print raw_input('***************')
		for e_p,e_label,e_config in enumerator_contexts:

			# if KEEP_IN_MEMORY_STUFFS and 'materialized_search_space' not in mss_node['enumerator_contexts'][1]:
			# 	in_memory_config_updater=mss_node['enumerator_contexts'][1]
			# 	in_memory_config_updater['materialized_search_space']=e_config['materialized_search_space']
			# 	in_memory_config_updater['patterns_already_generated']=e_config['patterns_already_generated']

			if e_label is None and e_p is None:
				#if e_config['materialized_search_space']['*']['nb_iter']>=NB_ITER_CONTEXTS_PER_ROUND:
				e_config['materialized_search_space']['*']['nb_iter']=0
				break
			#print e_p, len(e_config['support'])
			time_it_took_since_beggining=time()-started
			if (time_it_took_since_beggining)>TIMEBUDGET:break

			###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
			if MANY_INTERRUPTION_FLAG:
				if time_it_took_since_beggining>TIMEBUDGET_FLAG:
					time_it_tooked=time()
					try:
						e_config=e_config
					except Exception as e:
						e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
					DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
					DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
					DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
					DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
					DSC_AnyTimeRandomWalk.stats['timespent']=time_it_took_since_beggining
					DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
					DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
					if heatmap_for_matrix:
						DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
					yield interesting_patterns
					time_it_tooked=time()-time_it_tooked
					FLAG+=1
					TIMEBUDGET_FLAG=timebudget[FLAG]
					started+=time_it_tooked
			###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################

			e_p_ext=e_config['indices_bitset']
			index_visited+=1
			# if TEST_SUBSUMPTION_WITH_BISET:
			# 	if any(ext_subsume_ext(context_already_visited_bitset,e_p_ext,types_attributes_items) for ((context_already_visited,_,_),(context_already_visited_bitset,_,_)) in u2_config['contextsVisited']):
			# 		e_config['flag']=False
			# 		continue
			# else:
			# 	if any(pattern_subsume_pattern(context_already_visited,e_p,types_attributes_items) for ((context_already_visited,_,_),(context_already_visited_bitset,_,_)) in u2_config['contextsVisited']):
			# 		e_config['flag']=False
			# 		continue

			e_u_p=(e_p,u1_p,u2_p)

			e_u_label=(e_label,u1_label,u2_label)
			e_votes=e_config['support']
			v_ids_pattern=set(get_items_ids(e_votes))
			e_u_p_extent=(v_ids_pattern,u1_p_set_users,u2_p_set_users)
			# print v_ids_pattern
			# print e_config['indices']
			# raw_input('****')

			e_u_p_extent_bitset=(e_config['indices_bitset'],u1_p_extent_bitset,u2_p_extent_bitset)


			agg_p,all_p,worst_sim_expected=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_pattern,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations)

			pattern_matrix=[[(agg_p,all_p,worst_sim_expected)]]
			pattern_similarity=agg_p/all_p
			quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_comparaison,qualityMeasure)
			# print e_p,quality

			e_config['quality']=quality
			e_config['upperbound']=borne_max_quality

			#enumeration_on_contexts_time+=time()-st
			if (pruning and borne_max_quality<quality_threshold):
				e_config['flag']=False
				continue


			if (quality>=quality_threshold):
				e_p_dominated=False
				st=time()
				to_delete=[];to_delete_append=to_delete.append
				#################subsumption_verification#########################
				for k in range(len(interesting_patterns)):
					context_already_visited=interesting_patterns[k][0][0]
					pattern_already_visited=interesting_patterns[k][0]
					pattern_bitset_extent_already_visited=interesting_patterns[k][5]

					if TEST_SUBSUMPTION_WITH_BISET:
						if DSC_EXT_subsume_DSC_EXT(pattern_bitset_extent_already_visited,e_u_p_extent_bitset,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES):
							e_p_dominated=True
							break
						elif DSC_EXT_subsume_DSC_EXT(e_u_p_extent_bitset,pattern_bitset_extent_already_visited,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES):
							to_delete_append(k)
					else:
						if DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users):
							e_p_dominated=True
							break
						elif DSC_Pat_subsume_DSC_Pat(e_u_p,pattern_already_visited,types_attributes_items,types_attributes_users):
							to_delete_append(k)


				if not e_p_dominated and len(to_delete):
					del_from_list_by_index(interesting_patterns,to_delete)
				e_config['flag']=False
				#################subsumption_verification#########################
				if not e_p_dominated:
					votes_context=v_ids_pattern
					interesting_patterns_append([e_u_p,e_u_label,quality,borne_max_quality,e_u_p_extent,e_u_p_extent_bitset,reference_similarity,pattern_similarity])

				if len(interesting_patterns)>top_k:
					interesting_patterns=sorted(interesting_patterns,key = itemgetter(2),reverse=True)[:top_k]
					quality_threshold=interesting_patterns[-1][3]
			# nb_iter_contexts-=1
			# if nb_iter_contexts==0:
			# 	break
			if e_config['materialized_search_space']['*']['nb_iter']>=NB_ITER_CONTEXTS_PER_ROUND:
				e_config['materialized_search_space']['*']['nb_iter']=0
				break
		nb_visited=e_config['nb_visited']

		time_it_took_since_beggining=time()-started
		if (time_it_took_since_beggining)>TIMEBUDGET:break
		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
		if MANY_INTERRUPTION_FLAG:
			if (time_it_took_since_beggining)>TIMEBUDGET_FLAG:
				time_it_tooked=time()
				try:
					e_config=e_config
				except Exception as e:
					e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
				DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
				DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
				DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
				DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
				DSC_AnyTimeRandomWalk.stats['timespent']=time_it_took_since_beggining
				DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
				DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
				if heatmap_for_matrix:
					DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
				yield interesting_patterns
				time_it_tooked=time()-time_it_tooked
				FLAG+=1
				TIMEBUDGET_FLAG=timebudget[FLAG]
				started+=time_it_tooked
		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
		#raw_input('...')
		# if TEST_SUBSUMPTION_WITH_BISET:
		# 	u2_config['contextsVisited'].extend([((c,a,b),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset),_,_) in interesting_patterns if DSC_EXT_subsume_DSC_EXT((0,a_ext_bitset,b_ext_bitset),(0,u1_p_extent_bitset,u2_p_extent_bitset),types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES)])
		# else:
		# 	u2_config['contextsVisited'].extend([((c,a,b),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset),_,_) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])#pattern_subsume_pattern(a,u1_p,types_attributes_users) and pattern_subsume_pattern(b,u2_p,types_attributes_users)])# a==u1_p and b==u2_p])

		if do_heuristic_peers:

			if e_config['materialized_search_space']['*']['fully_explored']:
				# print e_config['materialized_search_space']['*']['nb_iter']
				# raw_input('...')
				# print 'DONE'
				# raw_input('...')
				mss_node=u2_config['mss_node']
				if KEEP_IN_MEMORY_STUFFS:
					del mss_node['enumerator_contexts']
					del mss_node['userpairssimsdetails']
					del mss_node['reference_matrix']
				del mss_node['elements_to_yield']



	#print len(interesting_patterns),index_visited,time()-started,subsumption_verif_time,enumeration_on_contexts_time,e_config['nb_visited'],u2_config['nb_visited']
	try:
		e_config=e_config
	except Exception as e:
		e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
	DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
	DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
	DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
	DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
	DSC_AnyTimeRandomWalk.stats['timespent']=time()-started
	DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
	DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
	if heatmap_for_matrix:
		DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
	yield interesting_patterns



def OLDYOLD_DSC_AnyTimeRandomWalk(itemsMetadata,users_metadata,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,all_users_to_items_outcomes,
		items_id_attribute,users_id_attribute,description_attributes_items=[],description_attributes_users=[],method_aggregation_outcome='VECTOR_VALUES',
		comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,
		ponderation_attribute=None,bound_type=1,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,heatmap_for_matrix=False,algorithm='DSC+CLOSED+UB2',consider_order_between_desc_of_couples=True,nb_random_walks=30,verbose=False):
	nb_visited=[0.,0.,0.]
	NB_ITER_CONTEXTS_PER_ROUND=nb_random_walks#30
	print 'NB_ITER_CONTEXTS_PER_ROUND : ',NB_ITER_CONTEXTS_PER_ROUND
	TEST_SUBSUMPTION_WITH_BISET=True
	KEEP_IN_MEMORY_STUFFS=True
	print 'MEMORY USAGE : ', KEEP_IN_MEMORY_STUFFS
	CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES=consider_order_between_desc_of_couples
	TIMEBUDGET=timebudget

	###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
	MANY_INTERRUPTION_FLAG=False
	if type(timebudget) is list:
		MANY_INTERRUPTION_FLAG=True
		TIMEBUDGET=max(timebudget)
		FLAG=0
		TIMEBUDGET_FLAG=timebudget[FLAG]
	###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################


	started=time()
	subsumption_verif_time=0.
	enumeration_on_contexts_time=0.

	get_items_ids = partial(map,itemgetter(items_id_attribute))
	get_users_ids = partial(map,itemgetter(users_id_attribute))

	v_ids_all_list=get_items_ids(considered_items_sorted)
	v_ids_all=set(v_ids_all_list)
	u_1_ids=set(get_users_ids(considered_users_1_sorted))
	u_2_ids=set(get_users_ids(considered_users_2_sorted))

	outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)
	interesting_patterns=[]
	interesting_patterns_append=interesting_patterns.append
	index_visited=0.
	#########PARAMS TO GIVE AS INPUT#########
	types_attributes_users=[x['type'] for x in description_attributes_users]
	types_attributes_items=[x['type'] for x in description_attributes_items]

	votes_map_ponderations={}
	u1_name='u1'
	u2_name='u2'
	lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False
	top_k=float('inf')
	#########PARAMS TO GIVE AS INPUT#########

	how_much_visited={'visited':0}
	initConfig={'config':None,'attributes':None}
	enumerator_pairs=enumerator_pair_of_users_optimized_dfs(users_metadata,considered_users_1_sorted,considered_users_2_sorted,users_id_attribute,all_users_to_items_outcomes,v_ids_all,description_attributes_users,threshold_nb_users_1,threshold_nb_users_2,outcome_tuple_structure,how_much_visited,method_aggregation_outcome,only_square_matrix=False,closed=closed,do_heuristic=do_heuristic_peers,heatmap_for_matrix=heatmap_for_matrix,algorithm=algorithm,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES)
	for (u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config),(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config) in enumerator_pairs:

		time_it_took_since_beggining=time()-started
		if verbose: stdout.write('%s\r' % ('Percentage Done : ' + ('%.2f'%((time_it_took_since_beggining/TIMEBUDGET)*100))+ '%'));stdout.flush();
		if (time_it_took_since_beggining)>TIMEBUDGET:break

		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
		if MANY_INTERRUPTION_FLAG:
			if (time_it_took_since_beggining)>TIMEBUDGET_FLAG:
				time_it_tooked=time()
				try:
					e_config=e_config
				except Exception as e:
					e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
				DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
				DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
				DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
				DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
				DSC_AnyTimeRandomWalk.stats['timespent']=time_it_took_since_beggining
				DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
				DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
				if heatmap_for_matrix:
					DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
				yield interesting_patterns
				time_it_tooked=time()-time_it_tooked
				FLAG+=1
				TIMEBUDGET_FLAG=timebudget[FLAG]
				started+=time_it_tooked
		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################

		u1_p_extent_bitset=u1_config['indices_bitset_1']
		u2_p_extent_bitset=u2_config['indices_bitset_2']
		jump_initing_context_computation=False

		if do_heuristic_peers and 'enumerator_contexts' in u2_config['mss_node']:
			mss_node=u2_config['mss_node']
			enumerator_contexts=mss_node['enumerator_contexts']
			userpairssimsdetails=mss_node['userpairssimsdetails']
			reference_matrix=mss_node['reference_matrix']
			jump_initing_context_computation=True
			# print ' '
			# print 'Hey Memory was used'
			# print ' '


		if not jump_initing_context_computation:

			votes_in_which_the_two_groups_participated=users1_aggregated_to_items_outcomes.viewkeys()&users2_aggregated_to_items_outcomes.viewkeys()
			if len(votes_in_which_the_two_groups_participated)<threshold_comparaison:
				if do_heuristic_peers: del u2_config['mss_node']['elements_to_yield']
				#print 'CASE A'
				continue
			userpairssimsdetails={v: similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, users2_aggregated_to_items_outcomes,u1_name,u2_name,comparaison_measure)[0]
									 for v in votes_in_which_the_two_groups_participated}




			############################
			if (type(ponderation_attribute) is int):
				votes_map_ponderations={v:users2_aggregated_to_items_outcomes[v][0] for v in votes_in_which_the_two_groups_participated}
			############################

			nbSimItems,nbItems,bound=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_all,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations=votes_map_ponderations)
			reference_matrix=[[(nbSimItems,nbItems)]]
			reference_similarity=(nbSimItems/nbItems)



			if pruning:
				UP_BOUND_FROM_THIS_COUPLE=max(0,(nbSimItems/nbItems)-bound)  if qualityMeasure == 'DISAGR_SUMDIFF'  else max(0,bound-nbSimItems/nbItems)
				if UP_BOUND_FROM_THIS_COUPLE<quality_threshold:
					if do_heuristic_peers: del u2_config['mss_node']['elements_to_yield']
					#print 'CASE B'
					continue


			indices_to_consider={k for k in range(len(v_ids_all_list)) if v_ids_all_list[k] in votes_in_which_the_two_groups_participated}

			indices_to_consider_bitset=2**len(v_ids_all_list)-1#encode_sup(sorted(indices_to_consider),len(v_ids_all_list)) #OLD
			userpairssimsdetails_indices={i:max(reference_similarity-userpairssimsdetails[x[items_id_attribute]] - quality_threshold,0) if lower else max(userpairssimsdetails[x[items_id_attribute]]-reference_similarity - quality_threshold,0) for i,x in enumerate(considered_items_sorted) if x[items_id_attribute] in votes_in_which_the_two_groups_participated}

			config_updater={'indices':indices_to_consider,'indices_bitset':indices_to_consider_bitset,'nb_visited':nb_visited,'indices_quality':userpairssimsdetails_indices,'NB_ITER_CONTEXTS_PER_ROUND':NB_ITER_CONTEXTS_PER_ROUND}
			enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items, config_updater,threshold=threshold_comparaison,verbose=False,bfs=False,closed=closed,do_heuristic=do_heuristic_contexts,initValues=initConfig)

			if do_heuristic_peers and KEEP_IN_MEMORY_STUFFS:
				mss_node=u2_config['mss_node']
				mss_node['enumerator_contexts']=enumerator_contexts
				mss_node['userpairssimsdetails']=userpairssimsdetails
				mss_node['reference_matrix']=reference_matrix

		#nb_iter_contexts=NB_ITER_CONTEXTS_PER_ROUND
		#print raw_input('***************')
		for e_p,e_label,e_config in enumerator_contexts:
			if e_label is None and e_p is None:
				#if e_config['materialized_search_space']['*']['nb_iter']>=NB_ITER_CONTEXTS_PER_ROUND:
				e_config['materialized_search_space']['*']['nb_iter']=0
				break
			#print e_p, len(e_config['support'])
			time_it_took_since_beggining=time()-started
			if (time_it_took_since_beggining)>TIMEBUDGET:break

			###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
			if MANY_INTERRUPTION_FLAG:
				if time_it_took_since_beggining>TIMEBUDGET_FLAG:
					time_it_tooked=time()
					try:
						e_config=e_config
					except Exception as e:
						e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
					DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
					DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
					DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
					DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
					DSC_AnyTimeRandomWalk.stats['timespent']=time_it_took_since_beggining
					DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
					DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
					if heatmap_for_matrix:
						DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
					yield interesting_patterns
					time_it_tooked=time()-time_it_tooked
					FLAG+=1
					TIMEBUDGET_FLAG=timebudget[FLAG]
					started+=time_it_tooked
			###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################

			e_p_ext=e_config['indices_bitset']
			index_visited+=1
			if TEST_SUBSUMPTION_WITH_BISET:
				if any(ext_subsume_ext(context_already_visited_bitset,e_p_ext,types_attributes_items) for ((context_already_visited,_,_),(context_already_visited_bitset,_,_)) in u2_config['contextsVisited']):
					e_config['flag']=False
					continue
			else:
				if any(pattern_subsume_pattern(context_already_visited,e_p,types_attributes_items) for ((context_already_visited,_,_),(context_already_visited_bitset,_,_)) in u2_config['contextsVisited']):
					e_config['flag']=False
					continue

			e_u_p=(e_p,u1_p,u2_p)

			e_u_label=(e_label,u1_label,u2_label)
			e_votes=e_config['support']
			v_ids_pattern=set(get_items_ids(e_votes))
			e_u_p_extent=(v_ids_pattern,u1_p_set_users,u2_p_set_users)

			e_u_p_extent_bitset=(e_config['indices_bitset'],u1_p_extent_bitset,u2_p_extent_bitset)


			agg_p,all_p,worst_sim_expected=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_pattern,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations)

			pattern_matrix=[[(agg_p,all_p,worst_sim_expected)]]
			pattern_similarity=agg_p/all_p
			quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_comparaison,qualityMeasure)
			# print e_p,quality

			e_config['quality']=quality
			e_config['upperbound']=borne_max_quality

			#enumeration_on_contexts_time+=time()-st
			if (pruning and borne_max_quality<quality_threshold):
				e_config['flag']=False
				continue


			if (quality>=quality_threshold):
				e_p_dominated=False
				st=time()
				to_delete=[];to_delete_append=to_delete.append
				#################subsumption_verification#########################
				for k in range(len(interesting_patterns)):
					context_already_visited=interesting_patterns[k][0][0]
					pattern_already_visited=interesting_patterns[k][0]
					pattern_bitset_extent_already_visited=interesting_patterns[k][5]

					if TEST_SUBSUMPTION_WITH_BISET:
						if DSC_EXT_subsume_DSC_EXT(pattern_bitset_extent_already_visited,e_u_p_extent_bitset,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES):
							e_p_dominated=True
							break
						elif DSC_EXT_subsume_DSC_EXT(e_u_p_extent_bitset,pattern_bitset_extent_already_visited,types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES):
							to_delete_append(k)
					else:
						if DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users):
							e_p_dominated=True
							break
						elif DSC_Pat_subsume_DSC_Pat(e_u_p,pattern_already_visited,types_attributes_items,types_attributes_users):
							to_delete_append(k)


				if not e_p_dominated and len(to_delete):
					del_from_list_by_index(interesting_patterns,to_delete)
				e_config['flag']=False
				#################subsumption_verification#########################
				if not e_p_dominated:
					votes_context=v_ids_pattern
					interesting_patterns_append([e_u_p,e_u_label,quality,borne_max_quality,e_u_p_extent,e_u_p_extent_bitset,reference_similarity,pattern_similarity])

				if len(interesting_patterns)>top_k:
					interesting_patterns=sorted(interesting_patterns,key = itemgetter(2),reverse=True)[:top_k]
					quality_threshold=interesting_patterns[-1][3]
			# nb_iter_contexts-=1
			# if nb_iter_contexts==0:
			# 	break
			if e_config['materialized_search_space']['*']['nb_iter']>=NB_ITER_CONTEXTS_PER_ROUND:
				e_config['materialized_search_space']['*']['nb_iter']=0
				break
		nb_visited=e_config['nb_visited']

		time_it_took_since_beggining=time()-started
		if (time_it_took_since_beggining)>TIMEBUDGET:break
		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
		if MANY_INTERRUPTION_FLAG:
			if (time_it_took_since_beggining)>TIMEBUDGET_FLAG:
				time_it_tooked=time()
				try:
					e_config=e_config
				except Exception as e:
					e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
				DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
				DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
				DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
				DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
				DSC_AnyTimeRandomWalk.stats['timespent']=time_it_took_since_beggining
				DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
				DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
				if heatmap_for_matrix:
					DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
				yield interesting_patterns
				time_it_tooked=time()-time_it_tooked
				FLAG+=1
				TIMEBUDGET_FLAG=timebudget[FLAG]
				started+=time_it_tooked
		###############Flagging DSC_AnyTimeRandomWalk for timebudget XP##################
		#raw_input('...')
		if TEST_SUBSUMPTION_WITH_BISET:
			u2_config['contextsVisited'].extend([((c,a,b),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset),_,_) in interesting_patterns if DSC_EXT_subsume_DSC_EXT((0,a_ext_bitset,b_ext_bitset),(0,u1_p_extent_bitset,u2_p_extent_bitset),types_attributes_items,types_attributes_users,consider_order_between_desc_of_couples=CONSIDER_ORDER_BETWEEN_DESC_OF_COUPLES)])
		else:
			u2_config['contextsVisited'].extend([((c,a,b),(c_ext_bitset,a_ext_bitset,b_ext_bitset)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext),(c_ext_bitset,a_ext_bitset,b_ext_bitset),_,_) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])#pattern_subsume_pattern(a,u1_p,types_attributes_users) and pattern_subsume_pattern(b,u2_p,types_attributes_users)])# a==u1_p and b==u2_p])

		if do_heuristic_peers:

			if e_config['materialized_search_space']['*']['fully_explored']:
				# print e_config['materialized_search_space']['*']['nb_iter']
				# raw_input('...')
				# print 'DONE'
				# raw_input('...')
				mss_node=u2_config['mss_node']
				if KEEP_IN_MEMORY_STUFFS:
					del mss_node['enumerator_contexts']
					del mss_node['userpairssimsdetails']
					del mss_node['reference_matrix']
				del mss_node['elements_to_yield']



	#print len(interesting_patterns),index_visited,time()-started,subsumption_verif_time,enumeration_on_contexts_time,e_config['nb_visited'],u2_config['nb_visited']
	try:
		e_config=e_config
	except Exception as e:
		e_config={'nb_visited':[0,0,0],'nb_itemset':len(description_attributes_items)}
	DSC_AnyTimeRandomWalk.stats['nb_generated_subgroups']=e_config['nb_visited'][0]
	DSC_AnyTimeRandomWalk.stats['nb_visited_subgroups']=e_config['nb_visited'][1]
	DSC_AnyTimeRandomWalk.stats['nb_candidates_subgroups']=index_visited
	DSC_AnyTimeRandomWalk.stats['nb_patterns']=len(interesting_patterns)
	DSC_AnyTimeRandomWalk.stats['timespent']=time()-started
	DSC_AnyTimeRandomWalk.stats['nb_attrs_objects_in_itemset']=e_config['nb_itemset']
	DSC_AnyTimeRandomWalk.stats['nb_attrs_users_in_itemset']=u2_config['nb_itemset']
	if heatmap_for_matrix:
		DSC_AnyTimeRandomWalk.outcomeTrack = enumerator_pair_of_users_optimized_dfs.outcomeTrack
	yield interesting_patterns

'''
def DSC_OLD(itemsMetadata,users_metadata,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,all_users_to_items_outcomes,items_id_attribute,users_id_attribute,description_attributes_items=[],description_attributes_users=[],method_aggregation_outcome='VECTOR_VALUES',comparaison_measure='MAAD',qualityMeasure='DISAGR_SUMDIFF',threshold_comparaison=30,threshold_nb_users_1=10,threshold_nb_users_2=10,quality_threshold=0.3,ponderation_attribute=None,bound_type=1,pruning=True,closed=True):


	started=time()
	subsumption_verif_time=0.
	enumeration_on_contexts_time=0.

	get_items_ids = partial(map,itemgetter(items_id_attribute))
	get_users_ids = partial(map,itemgetter(users_id_attribute))

	v_ids_all_list=get_items_ids(considered_items_sorted)
	v_ids_all=set(v_ids_all_list)
	u_1_ids=set(get_users_ids(considered_users_1_sorted))
	u_2_ids=set(get_users_ids(considered_users_2_sorted))

	outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)
	interesting_patterns=[]
	interesting_patterns_append=interesting_patterns.append
	index_visited=0.
	#########PARAMS TO GIVE AS INPUT#########
	types_attributes_users=[x['type'] for x in description_attributes_users]
	types_attributes_items=[x['type'] for x in description_attributes_items]

	votes_map_ponderations={}
	u1_name='u1'
	u2_name='u2'
	lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False
	top_k=float('inf')

	#########PARAMS TO GIVE AS INPUT#########

	how_much_visited={'visited':0}
	initConfig={'config':None,'attributes':None}

	for (u1_p,u1_label,u1_p_set_users,users1_aggregated_to_items_outcomes,u1_config),(u2_p,u2_label,u2_p_set_users,users2_aggregated_to_items_outcomes,u2_config) in \
		enumerator_pair_of_users_optimized_dfs(users_metadata,considered_users_1_sorted,considered_users_2_sorted,users_id_attribute,all_users_to_items_outcomes,v_ids_all,description_attributes_users,threshold_nb_users_1,threshold_nb_users_2,outcome_tuple_structure,how_much_visited,method_aggregation_outcome,only_square_matrix=False,closed=closed):
		#enumerator_pair_of_users
		votes_in_which_the_two_groups_participated=users1_aggregated_to_items_outcomes.viewkeys()&users2_aggregated_to_items_outcomes.viewkeys()

		if len(votes_in_which_the_two_groups_participated)<threshold_comparaison: continue

		userpairssimsdetails={v: similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, users2_aggregated_to_items_outcomes,u1_name,u2_name,comparaison_measure)[0]
								 for v in votes_in_which_the_two_groups_participated}




		############################
		if (type(ponderation_attribute) is int):
			votes_map_ponderations={v:users2_aggregated_to_items_outcomes[v][0] for v in votes_in_which_the_two_groups_participated}
		############################
		nbSimItems,nbItems,bound=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_all,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations=votes_map_ponderations)
		reference_matrix=[[(nbSimItems,nbItems)]]
		reference_similarity=(nbSimItems/nbItems)

		if pruning:

			UP_BOUND_FROM_THIS_COUPLE=max(0,(nbSimItems/nbItems)-bound)  if qualityMeasure == 'DISAGR_SUMDIFF'  else max(0,bound-nbSimItems/nbItems)

			if UP_BOUND_FROM_THIS_COUPLE<quality_threshold: continue


		# if closed:
		# 	enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items, {},threshold=threshold_comparaison,verbose=False,bfs=False,do_heuristic=False,initValues=initConfig)
		# else:
		# 	enumerator_contexts=enumerator_complex_from_dataset_new_config(considered_items_sorted, description_attributes_items, {},objet_id_attribute=items_id_attribute,threshold=threshold_comparaison,verbose=False)

		indices_to_consider={k for k in range(len(v_ids_all_list)) if v_ids_all_list[k] in votes_in_which_the_two_groups_participated}
		config_updater={'indices':indices_to_consider}
		enumerator_contexts=enumerator_complex_cbo_init_new_config(considered_items_sorted, description_attributes_items, config_updater,threshold=threshold_comparaison,verbose=False,bfs=False,closed=closed,do_heuristic=False,initValues=initConfig)

		for e_p,e_label,e_config in enumerator_contexts:
			st=time()
			index_visited+=1
			if any(pattern_subsume_pattern(context_already_visited,e_p,types_attributes_items) for ((context_already_visited,_,_)) in u2_config['contextsVisited']):
				e_config['flag']=False
				continue



			# if any(supc<=context_already_visited for ((context_already_visited,_,_),(supc,_,_)) in u2_config['contextsVisited']):
			# 	e_config['flag']=False
			# 	continue


			e_u_p=(e_p,u1_p,u2_p)

			e_u_label=(e_label,u1_label,u2_label)
			e_votes=e_config['support']
			v_ids_pattern=set(get_items_ids(e_votes))
			e_u_p_extent=(v_ids_pattern,u1_p_set_users,u2_p_set_users)

			# if len(v_ids_pattern&votes_in_which_the_two_groups_participated)<threshold_comparaison: #TOREMOVE BIATCH !
			# 	e_config['flag']=False
			# 	continue


			agg_p,all_p,worst_sim_expected=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids_pattern,threshold_comparaison,lower,bound_type,pruning,votes_map_ponderations)

			pattern_matrix=[[agg_p,all_p,worst_sim_expected]]
			pattern_similarity=agg_p/all_p
			quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_comparaison,qualityMeasure)
			e_config['quality']=quality
			e_config['upperbound']=borne_max_quality

			enumeration_on_contexts_time+=time()-st
			if (pruning and borne_max_quality<quality_threshold):
				e_config['flag']=False
				continue

			# for k in range(len(interesting_patterns)):
			# 	pattern_already_visited=interesting_patterns[k][0]
			# 	if DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users): #IS THIS POSSIBLE BY ANY MEAN I DON't THINK SO (I SAW CASE WHERE IT IS POSSIBLE)
			# 		e_config['flag']=False
			# 		break
			# if e_config['flag']==False:
			# 	continue

			if (quality>=quality_threshold):
				e_p_dominated=False
				#################subsumption_verification#########################
				# print '----------------------'
				# for k in range(len(interesting_patterns)):
				# 	px=interesting_patterns[k][0]
				# 	print '\t'+' ' + pattern_printer(px,types_attributes_items,types_attributes_users)
				# print '----------------------'
				# raw_input('...')
				st=time()
				to_delete=[];to_delete_append=to_delete.append
				for k in range(len(interesting_patterns)):
					context_already_visited=interesting_patterns[k][0][0]
					pattern_already_visited=interesting_patterns[k][0]
					#if context_already_visited==[['6.20.03']] and e_p==[['6.20.03']]:
						#print pattern_printer(pattern_already_visited,types_attributes_items,types_attributes_users),'\t\t\t\t',pattern_printer(e_u_p,types_attributes_items,types_attributes_users),'\t\t\t\t',DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users),'\t\t\t\t',DSC_Pat_subsume_DSC_Pat(e_u_p,pattern_already_visited,types_attributes_items,types_attributes_users)
						#print pattern_already_visited,'\t\t',e_u_p,'\t\t\t\t',DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users),'\t\t\t\t',DSC_Pat_subsume_DSC_Pat(e_u_p,pattern_already_visited,types_attributes_items,types_attributes_users)
					if DSC_Pat_subsume_DSC_Pat(pattern_already_visited,e_u_p,types_attributes_items,types_attributes_users):
						e_p_dominated=True
						# print pattern_printer(pattern_already_visited,types_attributes_items,types_attributes_users),pattern_printer(e_u_p,types_attributes_items,types_attributes_users)
						# raw_input('...')
						break
					elif DSC_Pat_subsume_DSC_Pat(e_u_p,pattern_already_visited,types_attributes_items,types_attributes_users):
						to_delete_append(k)

				if not e_p_dominated and len(to_delete):
					del_from_list_by_index(interesting_patterns,to_delete)
				e_config['flag']=False
				subsumption_verif_time+=time()-st



				#################subsumption_verification#########################
				if not e_p_dominated:
					votes_context=v_ids_pattern
					#print reference_matrix[0][0][0]/reference_matrix[0][0][1],pattern_matrix[0][0][0]/pattern_matrix[0][0][1]
					interesting_patterns_append([e_u_p,e_u_label,quality,borne_max_quality,e_u_p_extent])

				if len(interesting_patterns)>top_k:
					interesting_patterns=sorted(interesting_patterns,key = itemgetter(2),reverse=True)[:top_k]
					quality_threshold=interesting_patterns[-1][3]


		u2_config['contextsVisited'].extend([((c,a,b)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext)) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])#pattern_subsume_pattern(a,u1_p,types_attributes_users) and pattern_subsume_pattern(b,u2_p,types_attributes_users)])# a==u1_p and b==u2_p])
		# print len(u2_config['contextsVisited']),len(u1_config['contextsVisited'])
		# raw_input('...')

		#u1_config['contextsVisited'].extend([((c,a,b)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext)) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])
		#u1_config['contextsVisited'].extend([((c,a,b)) for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext)) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])#pattern_subsume_pattern(a,u1_p,types_attributes_users) and pattern_subsume_pattern(b,u2_p,types_attributes_users)])# a==u1_p and b==u2_p])

		# print [u2_config['contextsVisited'][k][0] for k in range(len(u2_config['contextsVisited']))]
		# raw_input('...')


		#######NEW YET NEED TO BE REMOVED#######

		#u2_config['itemsVisited'].extend([itemsAlreadyVisited for (_,_,_,_,itemsAlreadyVisited) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)])

		if False:
			perturbation=0.0
			#votes_already_percieved=set.union(*[x[4][0] for x in u2_config['contextsVisited']]) if len(u2_config['itemsVisited']) else set()

			lel=[c_ext for ((c,a,b),_,_,_,(c_ext,a_ext,b_ext)) in interesting_patterns if DSC_Pat_subsume_DSC_Pat(([],a,b),([],u1_p,u2_p),types_attributes_items,types_attributes_users)]

			if len(lel)>0:
				votes_already_percieved=set.union(*lel)
			else :
				votes_already_percieved=set()
			#print len(votes_already_percieved),len(interesting_patterns)
			#raw_input('...')
			#votes_already_percieved=set()
			list_of_sims=[];list_of_sims_append=list_of_sims.append
			for v in votes_in_which_the_two_groups_participated-votes_already_percieved:
				#perturbation+=similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users2_aggregated_to_items_outcomes[v],users1_aggregated_to_items_outcomes[v],threshold_nb_users_1)},u1_name,u2_name,comparaison_measure)[0]
				perturbation+=abs(userpairssimsdetails[v]-similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users2_aggregated_to_items_outcomes[v],users1_aggregated_to_items_outcomes[v],threshold_nb_users_1)},u1_name,u2_name,comparaison_measure)[0])+ \
				abs(userpairssimsdetails[v]-similarity_vector_measure_dcs({v}, users2_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users1_aggregated_to_items_outcomes[v],users2_aggregated_to_items_outcomes[v],threshold_nb_users_2)},u1_name,u2_name,comparaison_measure)[0])
				#list_of_sims_append(similarity_vector_measure_dcs({v}, users1_aggregated_to_items_outcomes, {v:worse_action_vector_expected(users2_aggregated_to_items_outcomes[v],users1_aggregated_to_items_outcomes[v],threshold_nb_users_1)},u1_name,u2_name,comparaison_measure)[0] )
			perturbation=(perturbation/len(votes_in_which_the_two_groups_participated-votes_already_percieved)) #the similarity between
			#print perturbation
			#raw_input('...')
			if False and perturbation>0.7:
				u2_config['flag']=False
				continue
			u2_config['quality']=2-perturbation
			u2_config['upperbound']=2-perturbation






		#print sum(sorted(list_of_sims,reverse=False)[:threshold_comparaison])
		# print 1-(perturbation/len(votes_in_which_the_two_groups_participated)),len(votes_already_percieved),len(list_of_sims),sum(sorted(list_of_sims,reverse=False)[:threshold_comparaison]),
		# raw_input('...')
		###################

		#print len(u2_config['contextsVisited'])
		#print len(interesting_patterns)


	sorted_interesting_patterns=sorted(interesting_patterns,key = lambda x:x[0][0],reverse=True) #itemgetter(2)
	print len(sorted_interesting_patterns),index_visited,time()-started,subsumption_verif_time,enumeration_on_contexts_time
	if True:
		#raw_input('...')

		k=0
		already_seen=None
		for e_u_p,e_u_label,quality,borne_max_quality,e_u_p_ext in sorted_interesting_patterns:
			if already_seen!=e_u_p[0]:
				k+=1
			#print pattern_printer(e_u_p,types_attributes_items,types_attributes_users),quality,k
			already_seen=e_u_p[0]
			#raw_input('...')
		to_write=[[pattern_printer(p,types_attributes_items,types_attributes_users),qual,borne_max_quality] for (p,l,qual,borne_max_quality,e_u_p_ext) in sorted_interesting_patterns]
		writeCSV(to_write,'../Tests/HEUR_ENUMERATION.csv',delimiter='\t')
	return []
'''
