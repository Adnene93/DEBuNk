#from memory_profiler import profile
import argparse
import shutil
from time import time
import cProfile
import pstats
import csv
import json
from random import randint,uniform,random
from copy import deepcopy
from itertools import chain,product,ifilter
from filterer.filter import filter_pipeline_obj 
from math import trunc
from collections import deque
from operator import iand,ior
#import numpy as np
from bisect import bisect_left
from math import log
from bisect import bisect
from functools import partial
from operator import itemgetter 
import sys
from util.csvProcessing import writeCSV,writeCSVwithHeader,readCSVwithHeader
import datetime
from outcomeDatasetsProcessor.outcomeDatasetsProcessor import process_outcome_dataset
from plotter.plotter import plot_timeseries
from os.path import basename, splitext, dirname
import os
from enumerator.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config
from outcomeAggregator.aggregateOutcome import compute_aggregates_outcomes
from DSC_Algorithm.DSC_Algo import DSC_Entry_Point,similarity_between_patterns_set,similarity_between_patterns_set_by_bitset,similarity_between_patterns_set_2,DSC_input_config,pattern_printer,printer_hmt,DSC
import pickle
from util.jsonProcessing import readJSON,readJSON_stringifyUnicodes
from util.matrixProcessing import transformMatricFromDictToList
from math import isnan
from measures.similaritiesDCS import similarity_vector_measure_dcs
import sys
sys.setrecursionlimit(50000)
import gc
#from pympler import asizeof
###############################TOREMOVE#######################################
def from_string_to_date(str_date,dateformat="%d/%m/%y"):
	return datetime.datetime.strptime(str_date, dateformat)

def get_tuple_structure(all_users_to_items_outcomes):
	one_entitie=all_users_to_items_outcomes[next(all_users_to_items_outcomes.iterkeys())]
	one_item=next(one_entitie.iterkeys())
	outcome_tuple_structure=tuple(one_entitie[one_item])
	return outcome_tuple_structure

def add_linejumps(s,nbchar=10):
	i=0
	ret=''
	while i<len(s):
		j=i
		i+=nbchar
		while i<len(s) and s[i]!=' ':
			i+=1
		ret=ret + s[j:i]+'\n'
	return ret


###############################TOREMOVE#######################################



def main_1(debug):
	CONSIDERED_DATASET='Parliament'#Parliament

	if CONSIDERED_DATASET=='Parliament':
		numeric_attrs=['VOTE_DATE']
		array_attrs=["PROCEDURE_SUBJECT"]
		itemsFile="../Datasets/EPD8NEW/items.csv"
		usersFile="../Datasets/EPD8NEW/users.csv"
		reviewsFile="../Datasets/EPD8NEW/reviews.csv"
		method_aggregation_outcome='VECTOR_VALUES'
		comparaison_measure='MAAD'
		qualityMeasure='DISAGR_SUMDIFF'
		description_attributes_items=[{'name':'PROCEDURE_SUBJECT', 'type':'themes'},{'name':'VOTE_DATE', 'type':'numeric'},{'name':'COMMITTEE', 'type':'simple'}]#[{'name':'tags', 'type':'themes'}]#[{'name':'PROCEDURE_SUBJECT', 'type':'themes'}]#
		description_attributes_users=[{'name':'COUNTRY', 'type':'simple'},{'name':'GROUPE_ID', 'type':'simple'},{'name':'NATIONAL_PARTY', 'type':'simple'}]#[{'name':'sexe', 'type':'simple'}]#[{'name':'COUNTRY', 'type':'simple'}]#
		u1_scope=[]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'sexe','inSet':{'1'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}]#
		u2_scope=[]#[{'dimensionName':'COUNTRY','inSet':{'Germany'}}]#[{'dimensionName':'COUNTRY','inSet':{'Germany'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'sexe','inSet':{'2'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}]#
		outcome_attrs=None
		nb_items=float('inf')#1000#float('inf')
		nb_individuals=float('inf')#200#float('inf')
		threshold_comparaison=50#1
		threshold_nb_users_1=10
		threshold_nb_users_2=10
		quality_threshold=0.3#0.6
		ponderation_attribute=None

	if CONSIDERED_DATASET=='Mustapha':
		numeric_attrs=['action','AGE']
		array_attrs=["odors"]
		itemsFile="../Datasets/MustaphaDataset/items.csv"
		usersFile="../Datasets/MustaphaDataset/individuals.csv"
		reviewsFile="../Datasets/MustaphaDataset/outcomes.csv"
		method_aggregation_outcome='AVGRATINGS_SIMPLE'
		comparaison_measure='AVG_YELP'
		qualityMeasure='DISAGR_SUMDIFF'
		description_attributes_items=[{'name':'PROCEDURE_SUBJECT', 'type':'themes'},{'name':'VOTE_DATE', 'type':'numeric'},{'name':'COMMITTEE', 'type':'simple'}]#[{'name':'tags', 'type':'themes'}]#[{'name':'PROCEDURE_SUBJECT', 'type':'themes'}]#
		description_attributes_users=[{'name':'COUNTRY', 'type':'simple'},{'name':'GROUPE_ID', 'type':'simple'},{'name':'NATIONAL_PARTY', 'type':'simple'}]#[{'name':'sexe', 'type':'simple'}]#[{'name':'COUNTRY', 'type':'simple'}]#
		u1_scope=[]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'sexe','inSet':{'1'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}]#
		u2_scope=[]#[{'dimensionName':'COUNTRY','inSet':{'Germany'}}]#[{'dimensionName':'COUNTRY','inSet':{'Germany'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'sexe','inSet':{'2'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}]#
		outcome_attrs=None
		nb_items=float('inf')#1000#float('inf')
		nb_individuals=float('inf')#200#float('inf')
		threshold_comparaison=1#1
		threshold_nb_users_1=1
		threshold_nb_users_2=1
		quality_threshold=0.3#0.6
		ponderation_attribute=None

	if CONSIDERED_DATASET=='Full_Parliament':
		numeric_attrs=[]
		array_attrs=["Subjects"]
		itemsFile="../Datasets/EPD78NEW/items.csv"
		usersFile="../Datasets/EPD78NEW/users.csv"
		reviewsFile="../Datasets/EPD78NEW/reviews.csv"
		method_aggregation_outcome='VECTOR_VALUES'
		comparaison_measure='MAAD'
		qualityMeasure='DISAGR_SUMDIFF'
		description_attributes_items=[{'name':'Subjects', 'type':'themes'}]#[{'name':'tags', 'type':'themes'}]#[{'name':'PROCEDURE_SUBJECT', 'type':'themes'}]#
		description_attributes_users=[{'name':'Country', 'type':'simple'}]#[{'name':'sexe', 'type':'simple'}]#[{'name':'COUNTRY', 'type':'simple'}]#
		u1_scope=[]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'sexe','inSet':{'1'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}]#
		u2_scope=[]#[{'dimensionName':'COUNTRY','inSet':{'Germany'}}]#[{'dimensionName':'COUNTRY','inSet':{'Germany'}}]#[{'dimensionName':'COUNTRY','inSet':{'France'}}]#[{'dimensionName':'sexe','inSet':{'2'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]#[{'dimensionName':'GROUPE_ID','inSet':{'S&D'}}]#
		outcome_attrs=None
		nb_items=float('inf')
		nb_individuals=float('inf')
		threshold_comparaison=50#1
		threshold_nb_users_1=10
		threshold_nb_users_2=10
		quality_threshold=0.3#0.6
		ponderation_attribute=None
	elif CONSIDERED_DATASET=='Movielens':
		numeric_attrs=['Rating','releaseDate']
		array_attrs=["genres"]
		itemsFile="../Datasets/Movielens/items.csv"
		usersFile="../Datasets/Movielens/users.csv"
		reviewsFile="../Datasets/Movielens/reviews.csv"
		method_aggregation_outcome='AVGRATINGS_SIMPLE'
		comparaison_measure='AVG_YELP'
		qualityMeasure='DISAGR_SUMDIFF'
		description_attributes_items=[{'name':'genres', 'type':'themes'},{'name':'releaseDate', 'type':'numeric'}]
		description_attributes_users=[{'name':'ageGroup', 'type':'simple'},{'name':'gender', 'type':'simple'},{'name':'occupation', 'type':'simple'}]
		u1_scope=[]
		u2_scope=[]
		outcome_attrs=['Rating']#['boites','size_of_population']#None#
		nb_items=float('inf')
		nb_individuals=float('inf')
		threshold_comparaison=8
		threshold_nb_users_1=50
		threshold_nb_users_2=50
		quality_threshold=0.2
		ponderation_attribute=None
	elif CONSIDERED_DATASET=='Yelp':
		numeric_attrs=['stars','nb_users']
		array_attrs=["categories"]
		itemsFile="../Datasets/Yelp/items.csv"
		usersFile="../Datasets/Yelp/users.csv"
		reviewsFile="../Datasets/Yelp/reviews.csv"
		method_aggregation_outcome='AVGRATINGS_PONDERATION'
		comparaison_measure='AVG_YELP'
		qualityMeasure='DISAGR_SUMDIFF'
		description_attributes_items=[{'name':'categories', 'type':'themes'}]
		description_attributes_users=[{'name':'seniority', 'type':'simple'},{'name':'friends_network', 'type':'simple'}]
		u1_scope=[]
		u2_scope=[]
		outcome_attrs=['stars','nb_users']#['boites','size_of_population']#None#
		nb_items=float('inf')
		nb_individuals=float('inf')
		threshold_comparaison=5
		threshold_nb_users_1=1
		threshold_nb_users_2=1
		quality_threshold=0.5
		ponderation_attribute=None
	elif CONSIDERED_DATASET=='OpenMedic':
		numeric_attrs=['boites','size_of_population','sizeOfPop']#['VOTE_DATE']
		array_attrs=['tags']
		itemsFile="../Datasets/OpenMedic/items.csv"
		usersFile="../Datasets/OpenMedic/users.csv"
		reviewsFile="../Datasets/OpenMedic/reviews.csv"
		method_aggregation_outcome='MEDICAMENTS'
		comparaison_measure='similarity_candidates'
		qualityMeasure='DISAGR_SUMDIFF'
		description_attributes_items=[{'name':'tags', 'type':'themes'}]
		description_attributes_users=[{'name':'region', 'type':'simple'}]
		u1_scope=[{'dimensionName':'sexe','outSet':{'9'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]
		u2_scope=[{'dimensionName':'sexe','outSet':{'9'}},{'dimensionName':'region','outSet':{'ALL'}},{'dimensionName':'age','outSet':{'9'}}]
		outcome_attrs=['boites','size_of_population']
		nb_items=float('inf')
		nb_individuals=float('inf')
		threshold_comparaison=10
		threshold_nb_users_1=1
		threshold_nb_users_2=1
		quality_threshold=1.0
		ponderation_attribute='boites'

	if True:
		from Alpha_Algorithm.ALPHA import Alpha_Entry_Point
		Alpha_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,
						itemsScope=[],users_1_Scope=u1_scope,users_2_Scope=u2_scope,delimiter='\t',
						description_attributes_items=description_attributes_items,description_attributes_users=description_attributes_users,
						comparaison_measure=comparaison_measure,qualityMeasure=qualityMeasure,nb_items=nb_items,nb_individuals=nb_individuals,threshold_comparaison=threshold_comparaison,threshold_nb_users_1=threshold_nb_users_1,
						threshold_nb_users_2=threshold_nb_users_2,quality_threshold=quality_threshold,
						ponderation_attribute=ponderation_attribute,bound_type=2,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,debug=debug)

	#24 723879.0 136.664000034 0.010999917984 41.5139915943
	#24 1365966.0 183.764999866 0.0160000324249 40.0700137615
	
	# if True:
	# 	plot_timeseries({
	# 		'RW':([0.,10.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0],[0.,0.5623379200744384, 0.6348838927150657, 0.7366418002658911, 0.778840156017475, 0.7956683432018453, 0.8128524951934172, 0.8256739422112553]),
	# 		'1':([0.,10.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0],[1.,1.,1.,1.,1.,1.,1.,1.]),
	# 	})
	# 	raw_input('.....')

	PROFILING=False
	if PROFILING:
		pr = cProfile.Profile()
		pr.enable()
	
	#1951 687354.0 195.902999878 60.6310014725 80.8460049629
	if False:
		#2270 3352483.0 488.923000097 8.92399764061 214.4000175

		#3701 4587967.0 573.917999983 22.4369800091 260.651077509
		returned_results_1=next(DSC_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,
						itemsScope=[],users_1_Scope=u1_scope,users_2_Scope=u2_scope,delimiter='\t',
						description_attributes_items=description_attributes_items,description_attributes_users=description_attributes_users,
						comparaison_measure=comparaison_measure,qualityMeasure=qualityMeasure,nb_items=nb_items,nb_individuals=nb_individuals,threshold_comparaison=threshold_comparaison,threshold_nb_users_1=threshold_nb_users_1,
						threshold_nb_users_2=threshold_nb_users_2,quality_threshold=quality_threshold,
						ponderation_attribute=ponderation_attribute,bound_type=2,pruning=True,closed=True,do_heuristic_contexts=False,do_heuristic_peers=False,timebudget=1000,debug=debug))

		for k,v in DSC_Entry_Point.stats.iteritems():
			print k,' : ',v
		raw_input('...')

		with open('./tmp//full_results.dsc', 'wb') as fp:
			pickle.dump(returned_results_1, fp)
	else:
		with open ('./tmp//full_results.dsc', 'rb') as fp:
			returned_results_1 = pickle.load(fp)
	if False:

		print len(returned_results_1)
		returned_results_2=next(DSC_Entry_Point(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,
						itemsScope=[],users_1_Scope=u1_scope,users_2_Scope=u2_scope,delimiter='\t',
						description_attributes_items=description_attributes_items,description_attributes_users=description_attributes_users,
						comparaison_measure=comparaison_measure,qualityMeasure=qualityMeasure,nb_items=nb_items,nb_individuals=nb_individuals,threshold_comparaison=threshold_comparaison,threshold_nb_users_1=threshold_nb_users_1,
						threshold_nb_users_2=threshold_nb_users_2,quality_threshold=quality_threshold,
						ponderation_attribute=ponderation_attribute,bound_type=2,pruning=True,closed=True,do_heuristic_contexts=True,do_heuristic_peers=True,timebudget=35))
		#print len(returned_results_2)
		time_jacc=time()
		#print similarity_between_patterns_set([x[1] for x in returned_results_1],[x[1] for x in returned_results_2]), 'time spent : ',time()-time_jacc
		# pat_set_1=[x[1] for x in returned_results_1]
		# pat_set_2=[x[1] for x in returned_results_2]
		pat_set_1=[(frozenset(x[1][0]),frozenset(x[1][1]),frozenset(x[1][2])) for x in returned_results_1]
		pat_set_2=[(frozenset(x[1][0]),frozenset(x[1][1]),frozenset(x[1][2])) for x in returned_results_2]
		#print similarity_between_patterns_set_2(pat_set_1,pat_set_2), 'time spent : ',time()-time_jacc
		print similarity_between_patterns_set(pat_set_1,pat_set_2), 'time spent : ',time()-time_jacc
		# time_jacc=time()
		# print similarity_between_patterns_set_by_bitset([x[2] for x in returned_results_1],[x[2] for x in returned_results_2]),time()-time_jacc
	if PROFILING:
		pr.disable()
		ps = pstats.Stats(pr)
		ps.sort_stats('cumulative').print_stats(20) #time






#TODO - Prepare the parliament dataset
#TODO - Prepare a function to allow qualitative experiments
#TODO - add the experiments for random Walk
#TODO - add the script allowing to draw graphs


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


def main_2():
	parser = argparse.ArgumentParser(description='DSC-XPs')
	parser.add_argument('file', metavar='ConfigurationFile', type=str,  help='the input configuration file')
	parser.add_argument('-p','--performance',metavar='performance',nargs='*',help='execute a performance test')
	parser.add_argument('-q','--qualitative',metavar='qualitative',nargs='*',help='execute a qualitative test')
	parser.add_argument('--heatmap',action='store_true',help='execute a qualitative test with a heatmap (python must be used and not pypy)')
	
	parser.add_argument('-r','--randomwalk',metavar='randomwalk',nargs='*',help='execute a randomwalk test and compare its results against an exhasutive search algorithm')
	parser.add_argument('--oneExecutionTest',action='store_true',help='Execute once the sampling algorithm with multiple interruption flag')
	parser.add_argument('--exhaustiveDoneYet',action='store_true',help='A DSC File must be saved by an apriori execution')

	parser.add_argument('--nb_obj',metavar='nb_obj', nargs='*',help='vary the number of objects',type=int)
	parser.add_argument('--nb_ind',metavar='nb_ind', nargs='*',help='vary the number of individuals',type=int)
	parser.add_argument('--nb_attr_desc_obj',metavar='nb_attr_desc_obj', nargs='*',help='vary the number of description attributes over objects',type=int)
	parser.add_argument('--nb_attr_desc_ind',metavar='nb_attr_desc_ind', nargs='*',help='vary the number of description attributes over individuals',type=int)


	parser.add_argument('--nb_items_desc_obj',metavar='nb_items_desc_obj', nargs='*',help='vary the number of description attributes (by Items) over objects',type=int)
	parser.add_argument('--nb_items_desc_ind',metavar='nb_items_desc_ind', nargs='*',help='vary the number of description attributes (by Items) over individuals',type=int)

	parser.add_argument('--hmt_to_itemset',action='store_true',help='Consider all HMT To Be Itemsets') #args.hmt_to_itemset

	parser.add_argument('--export_support',action='store_true',help='add a qualitiative file containing supports')
	parser.add_argument('--performance_informations',action='store_true',help='add information about number of patterns visited and the number of found patterns')

	parser.add_argument('--algos',metavar='algos', nargs='*',help='vary the algorithms used in experiments',type=str)
	parser.add_argument('--sampling_algorithm',metavar='sampling_algorithm', nargs='*',help='sampling algorithm',type=str)
	parser.add_argument('--sigma_obj',metavar='sigma_obj', nargs='*',help='vary the threshold over the support of objects',type=int)
	parser.add_argument('--sigma_ind',metavar='sigma_ind', nargs='*',help='vary the threshold over the support of individuals',type=int)
	parser.add_argument('--sigma_qual',metavar='sigma_qual', nargs='*',help='vary the threshold over the support of qualities',type=float)

	parser.add_argument('--nrwc',metavar='nrwc',type=int,help='number of random walk performed in the context')

	parser.add_argument('--timebudget',metavar='timebudget',nargs='+',help='timebudget',type=float)

	parser.add_argument('--quality_measure',metavar='quality_measure', nargs='*',help='vary the quality measures',type=str)
	parser.add_argument('--similarity_measure',metavar='similarity_measure', nargs='*',help='vary the similarity measure',type=str)

	parser.add_argument('-f','--figure',metavar='figure',nargs='*',help='show a figure starting from a performance test')
	parser.add_argument('--rwf',action='store_true',help='Draw figure based on similarity')
	parser.add_argument('--x_axis_attribute',metavar='x_axis_attribute',type=str,help='which attribute to vary')
	parser.add_argument('--fig_algos',metavar='fig_algos',nargs='*',help='select the algorithms to show in the figures',type=str)
	parser.add_argument('--linear_scale',action='store_true',help='Log linear_scale')

	parser.add_argument('--do_not_plot_bars',action='store_true',help='do not plot bars')
	parser.add_argument('--do_not_plot_time',action='store_true',help='do not plot time')

	


	parser.add_argument('-v','--verbose',action='store_true',help='verbose execution...')

	parser.add_argument('--debug',action='store_true',help='DEBUGGING ...')


	parser.add_argument('--edf',action='store_true',help='distribution of qualities')
	

	parser.add_argument('--no_generality',action='store_true',help='no generality between patterns considered')
	parser.add_argument('--no_sigma_quality',action='store_true',help='no sigma_quality')
	parser.add_argument('--first_run',action='store_true',help='first_run for edf')

	parser.add_argument('--results_destination',metavar='results_destination', nargs='?',help='XXX',type=str)

	


	args=parser.parse_args()
	json_file_path=args.file
	
	if args.debug:
		main_1(args.debug)
	if type(args.performance) is list:
		json_config=readJSON_stringifyUnicodes(json_file_path)
		FIRST_TEST=True
		VERBOSE=args.verbose
		if VERBOSE:
			print 'Verbose Execution ...'
		print 'Performance Test ... '
		header_XP=['quality_measure','comparaison_measure','method_aggregation_outcome','attrs_objects','attrs_users','nb_attrs_objects','nb_attrs_objects_in_itemset',
		'nb_attrs_users','nb_attrs_users_in_itemset','quality_threshold','threshold_objects','threshold_nb_users_1','threshold_nb_users_2',
		'nb_objects','nb_users','nb_users_1','nb_users_2','nb_reviews','algorithm','closed','pruning_ub','RandomWalk','timebudget','bound_type',
		'nb_generated_subgroups','nb_visited_subgroups','nb_candidates_subgroups','nb_patterns','timespent_init','timespent','timespent_total']
		if len(args.performance)==0:
			result_file_destination='performance.csv'
		else:
			result_file_destination=args.performance[0]

		XPs_results=[]

		json_config['results_destination']=None
		list_to_iter_into = \
		[
			args.algos if args.algos is not None else [json_config['algorithm']],
			args.nb_obj if args.nb_obj is not None else [json_config['nb_objects']],
			args.nb_ind if args.nb_ind is not None else [json_config['nb_individuals']],
			
			args.nb_attr_desc_obj if args.nb_attr_desc_obj is not None else [len(json_config['description_attributes_objects'])],
			args.nb_attr_desc_ind if args.nb_attr_desc_ind is not None else [len(json_config['description_attributes_individuals'])],

			args.nb_items_desc_obj if args.nb_items_desc_obj is not None else [float('inf')],
			args.nb_items_desc_ind if args.nb_items_desc_ind is not None else [float('inf')],


			args.sigma_obj if args.sigma_obj is not None else [json_config['threshold_objects']],
			args.sigma_ind if args.sigma_ind is not None else [json_config['threshold_individuals']],
			args.sigma_qual if args.sigma_qual is not None else [json_config['threshold_quality']],
			
			args.quality_measure if args.quality_measure is not None else [json_config['quality_measure']],
			args.similarity_measure if args.similarity_measure is not None else [json_config['similarity_measure']]
		]

		print list_to_iter_into

		for algorithm,nb_objects,nb_individuals,nb_attr_desc_obj,nb_attr_desc_ind,nb_items_desc_obj,nb_items_desc_ind,threshold_objects,threshold_individuals,threshold_quality,quality_measure,similarity_measure in product(*list_to_iter_into):
			
			print algorithm,nb_objects,nb_individuals,nb_attr_desc_obj,nb_attr_desc_ind,nb_items_desc_obj,nb_items_desc_ind,threshold_objects,threshold_individuals,threshold_quality,quality_measure,similarity_measure

			json_config_copy=deepcopy(json_config)
			json_config_copy['algorithm']=algorithm
			json_config_copy['nb_objects']=nb_objects
			json_config_copy['nb_individuals']=nb_individuals
			json_config_copy['description_attributes_objects']=json_config_copy['description_attributes_objects'][:nb_attr_desc_obj]
			json_config_copy['description_attributes_individuals']=json_config_copy['description_attributes_individuals'][:nb_attr_desc_ind]

			json_config_copy['nb_items_entities']=nb_items_desc_obj
			json_config_copy['nb_items_individuals']=nb_items_desc_ind
			
			json_config_copy['hmt_to_itemset']=args.hmt_to_itemset
			
			json_config_copy['threshold_objects']=threshold_objects
			json_config_copy['threshold_individuals']=threshold_individuals
			json_config_copy['threshold_quality']=threshold_quality

			json_config_copy['quality_measure']=quality_measure
			json_config_copy['similarity_measure']=similarity_measure
			json_config_copy['timebudget']=json_config_copy['timebudget'] if args.timebudget is None else args.timebudget[0]
			#print json_config_copy
			for k in range(1):
				returned = next(DSC_input_config(json_config_copy,verbose=VERBOSE))
			
			XPs_results.append(DSC_input_config.stats)
			writeCSVwithHeader(XPs_results,result_file_destinaton,selectedHeader=header_XP,flagWriteHeader=FIRST_TEST)
			FIRST_TEST=False
			XPs_results=[]
		
		#writeCSVwithHeader(XPs_results,result_file_destination,selectedHeader=header_XP)

	elif type(args.qualitative) is list:
		print 'Qualitative test...'
		FIGURES_FOR_RESULTS=args.heatmap#True
		FILL_HEATMAPS=True
		if FIGURES_FOR_RESULTS:
			print '... Include computation of heatmaps ...'
		else:
			print '... No heatmaps computation wanted...'

		json_config=readJSON_stringifyUnicodes(json_file_path)
		################################################################

		json_config['top_k']=json_config['top_k'] if 'top_k' in json_config else None
		DSC.TOPK=json_config['top_k']
		#########################""
		json_config['algorithm']=args.algos[0] if args.algos is not None else json_config['algorithm']
		json_config['nb_objects']=args.nb_obj[0] if args.nb_obj is not None else json_config['nb_objects']
		json_config['nb_individuals']=args.nb_ind[0] if args.nb_ind is not None else json_config['nb_individuals']
		
		nb_attr_desc_obj=args.nb_attr_desc_obj[0] if args.nb_attr_desc_obj is not None else len(json_config['description_attributes_objects'])
		json_config['description_attributes_objects']=json_config['description_attributes_objects'][:nb_attr_desc_obj]
		nb_attr_desc_ind=args.nb_attr_desc_ind[0] if args.nb_attr_desc_ind is not None else len(json_config['description_attributes_individuals'])
		json_config['description_attributes_individuals']=json_config['description_attributes_individuals'][:nb_attr_desc_ind]


		json_config['nb_items_entities']=args.nb_items_desc_obj[0] if args.nb_items_desc_obj is not None else float('inf')
		json_config['nb_items_individuals']=args.nb_items_desc_ind[0] if args.nb_items_desc_ind is not None else float('inf')
		
		json_config['hmt_to_itemset']=args.hmt_to_itemset


		

		json_config['threshold_objects']=args.sigma_obj[0] if args.sigma_obj is not None else json_config['threshold_objects']
		json_config['threshold_individuals']=args.sigma_ind[0] if args.sigma_ind is not None else json_config['threshold_individuals']
		json_config['threshold_quality']=args.sigma_qual[0] if args.sigma_qual is not None else json_config['threshold_quality']

		json_config['quality_measure']=args.quality_measure[0] if args.quality_measure is not None else json_config['quality_measure']
		json_config['similarity_measure']=args.similarity_measure[0] if args.similarity_measure is not None else json_config['similarity_measure']
		json_config['timebudget']=json_config['timebudget'] if args.timebudget is None else args.timebudget[0]



		json_config['no_generality'] = json_config.get('no_generality',args.no_generality)
		json_config['no_sigma_quality'] = json_config.get('no_sigma_quality',args.no_sigma_quality)

		json_config['nb_random_walks']=args.nrwc if args.nrwc is not None else json_config.get('nb_random_walks',30.)
		################################################################
		
		json_config['results_destination']=args.qualitative[0] if len(args.qualitative)>0 else json_config['results_destination']
		
		VERBOSE=args.verbose
		if VERBOSE:
			print 'Verbose Execution ...'
		returned = next(DSC_input_config(json_config,FIGURES_FOR_RESULTS,edf=args.edf,first_run=args.first_run,verbose=VERBOSE))
		for k,v in DSC_input_config.stats.iteritems():
			if k=='ALL_OBSERVED_QUALITIES':
				continue
			print k,'\t',v


		if args.export_support:
			resulting_file,resulting_file_header=readCSVwithHeader(json_config['results_destination'],numberHeader=['ref_sim','pattern_sim','quality'])
			print 'exporting supports of each pattern'
			to_save=[]
			ii=0
			for eup,eup_ext,e_u_p_ext_bitset in returned:
				context_extent=eup_ext[0]
				d1_extent=eup_ext[1]
				d2_extent=eup_ext[2]
				#to_save.append({'context':sorted(eup[0][0])[1:],'g_1':sorted(eup[1][0])[1:],'g_2':sorted(eup[2][0])[1:],'context_extent':sorted(context_extent),'g_1_extent':sorted(d1_extent),'g_2_extent':sorted(d2_extent),'sim_ref':resulting_file[ii]['ref_sim'],'sim_context':resulting_file[ii]['pattern_sim'],'quality':resulting_file[ii]['quality']})
				# print eup
				# raw_input('**************')

				context_desc=sorted(pattern_printer_one([z],[json_config['description_attributes_objects'][ind][1]]) for ind,z in enumerate(eup[0]))
				g1_desc=sorted(pattern_printer_one([z],[json_config['description_attributes_individuals'][ind][1]]) for ind,z in enumerate(eup[1]))
				g2_desc=sorted(pattern_printer_one([z],[json_config['description_attributes_individuals'][ind][1]]) for ind,z in enumerate(eup[2]))
				
				context_desc=filter(lambda x: x!='*',context_desc)
				g1_desc=filter(lambda x: x!='*',g1_desc)
				g2_desc=filter(lambda x: x!='*',g2_desc)
				to_save.append({'context':context_desc,'g_1':g1_desc,'g_2':g2_desc,'context_extent':sorted(context_extent),'g_1_extent':sorted(d1_extent),'g_2_extent':sorted(d2_extent),'sim_ref':resulting_file[ii]['ref_sim'],'sim_context':resulting_file[ii]['pattern_sim'],'quality':resulting_file[ii]['quality']})
				
				#to_save.append({'context':sorted(z[0] for z in eup[0]),'g_1':sorted(z[0] for z in eup[1]),'g_2':sorted(z[0] for z in eup[2]),'context_extent':sorted(context_extent),'g_1_extent':sorted(d1_extent),'g_2_extent':sorted(d2_extent),'sim_ref':resulting_file[ii]['ref_sim'],'sim_context':resulting_file[ii]['pattern_sim'],'quality':resulting_file[ii]['quality']})
				ii+=1
			filename, file_extension = splitext(json_config['results_destination'])

			
			#print 'ahdhaheqsdaze'
			writeCSVwithHeader(to_save,filename+'_EXTENTS'+file_extension,selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],flagWriteHeader=True)
		if args.performance_informations:
			nb_patterns_visited=DSC_input_config.stats['nb_candidates_subgroups']
			nb_patterns=DSC_input_config.stats['nb_patterns']
			Outcomes_covered=DSC_input_config.stats.get('Outcomes_covered',0)
			filename, file_extension = splitext(json_config['results_destination'])
			writeCSVwithHeader([{'visited':nb_patterns_visited,'nb_patterns':nb_patterns,'Outcomes_covered':Outcomes_covered}],filename+'_perf'+file_extension,selectedHeader=['visited','nb_patterns','Outcomes_covered'],flagWriteHeader=True)

		if FIGURES_FOR_RESULTS:
			


			################RETURNED REORGANIZATION###########
			if FILL_HEATMAPS:
				print len(DSC_input_config.outcomeTrack)
				types_attributes_users=DSC_input_config.types_attributes_users
				types_attributes_items=DSC_input_config.types_attributes_items
				contexts_and_their_extents={}
				individuals_and_their_extents={}
				individuals_and_their_outcomes={}
				for eup,eup_ext,e_u_p_ext_bitset in returned:
					context=pattern_printer(eup[0],types_attributes_items);context_extent=eup_ext[0]
					d1=pattern_printer(eup[1],types_attributes_users);d1_extent=eup_ext[1]
					d2=pattern_printer(eup[2],types_attributes_users);d2_extent=eup_ext[2]
					if context not in contexts_and_their_extents:
						contexts_and_their_extents[context]=context_extent
					if d1 not in individuals_and_their_extents:
						individuals_and_their_extents[d1]=d1_extent
						tup_d1_extent=tuple(sorted(d1_extent))
						individuals_and_their_outcomes[d1]=DSC_input_config.outcomeTrack[tup_d1_extent]
					if d2 not in individuals_and_their_extents:
						individuals_and_their_extents[d2]=d2_extent
						tup_d2_extent=tuple(sorted(d2_extent))
						individuals_and_their_outcomes[d2]=DSC_input_config.outcomeTrack[tup_d2_extent]
			################RETURNED REORGANIZATION###########

			if not os.path.exists('./Figures'):
				os.makedirs('./Figures')
			else:
				shutil.rmtree('./Figures')
				os.makedirs('./Figures')


			resulting_file,resulting_file_header=readCSVwithHeader(json_config['results_destination'],numberHeader=['ref_sim','pattern_sim','quality'])
			from heatmap.heatmap import generateHeatMap
			contexts_grouped={}
			contexts_grouped_org_g1_g2={}
			contexts_grouped_ref_matrices={}
			contexts_grouped_pattern_matrices={}
			lefties=set()
			righties=set()
			for row in resulting_file:
				row_context=row['context']
				row_g1=row['g1']
				row_g2=row['g2']
				ref_sim=row['ref_sim']
				pattern_sim=row['pattern_sim']
				if row_context not in contexts_grouped:
					contexts_grouped[row_context]=[]
					contexts_grouped_org_g1_g2[row_context]={'lefties':set(),'righties':set()}
					

				lefties=contexts_grouped_org_g1_g2[row_context]['lefties']
				righties=contexts_grouped_org_g1_g2[row_context]['righties']
				if row_g2 in lefties or row_g1 in righties:
					row_g1,row_g2=row_g2,row_g1

				contexts_grouped[row_context].append([row_g1,row_g2,ref_sim,pattern_sim])
				lefties|={row_g1}
				righties|={row_g2}
			nb_cont=1
			for k,v in contexts_grouped.iteritems():
				#print k
				contexts_grouped_ref_matrices[k]={g1:{g2:float('nan') for _,g2,_,_ in v} for g1,_,_,_ in v}
				contexts_grouped_pattern_matrices[k]={g1:{g2:float('nan') for _,g2,_,_ in v} for g1,_,_,_ in v}
				for r in v:
					contexts_grouped_ref_matrices[k][r[0]][r[1]]=r[2]
					contexts_grouped_pattern_matrices[k][r[0]][r[1]]=r[3]
				
				################HEATMAP FILLING###########
				highlight_way=None
				if FILL_HEATMAPS:
					highlight_way=[]
					i=0
					for g1 in sorted(contexts_grouped_ref_matrices[k]):
						highlight_way.append([])
						j=0
						for g2 in sorted(contexts_grouped_pattern_matrices[k][g1]):
							if isnan(contexts_grouped_pattern_matrices[k][g1][g2]):
								votes_ids=contexts_and_their_extents[k]
								votes_all_ids=individuals_and_their_outcomes[g1].viewkeys()&individuals_and_their_outcomes[g2].viewkeys()
								# print g1,g2,len(votes_ids&votes_all_ids),len(votes_all_ids),[(individuals_and_their_outcomes[g1][x],individuals_and_their_outcomes[g2][x]) for x in votes_ids]
								# raw_input('...')
								if len(votes_ids&votes_all_ids)>=json_config['threshold_objects']:
									user1_votes_outcome=individuals_and_their_outcomes[g1]
									user2_votes_outcome=individuals_and_their_outcomes[g2]
									simas_nb,nb=similarity_vector_measure_dcs(votes_ids,user1_votes_outcome,user2_votes_outcome,'1','2',method=json_config['similarity_measure'])
									simas_nb_ref,nb_ref=similarity_vector_measure_dcs(votes_all_ids,user1_votes_outcome,user2_votes_outcome,'1','2',method=json_config['similarity_measure'])
									contexts_grouped_ref_matrices[k][g1][g2]=(simas_nb_ref/nb_ref)
									contexts_grouped_pattern_matrices[k][g1][g2]=(simas_nb/nb)
									highlight_way[-1].append(False)
								else:
									highlight_way[-1].append(False)
							else:
								highlight_way[-1].append(True)

							j+=1
						i+=1

				################HEATMAP FILLING###########

				matrice_ref=transformMatricFromDictToList(contexts_grouped_ref_matrices[k])
				matrice_pattern=transformMatricFromDictToList(contexts_grouped_pattern_matrices[k])
				title=add_linejumps(k,70)

				#print matrice_ref
				#print matrice_pattern
				generateHeatMap(matrice_ref,'Figures/'+str(nb_cont).zfill(4)+'_ref.jpg',vmin=0.,vmax=1.,showvalues_text=True,only_heatmap=False,title=title,highlight=highlight_way)
				generateHeatMap(matrice_pattern,'Figures/'+str(nb_cont).zfill(4)+'_pattern.jpg',vmin=0.,vmax=1.,showvalues_text=True,only_heatmap=False,title=title,highlight=highlight_way)
				nb_cont+=1
				#raw_input('...')




	elif type(args.randomwalk) is list:
		ExhaustiveDoneYet=args.exhaustiveDoneYet#False
		OneExecutionTest=args.oneExecutionTest#True
		
		VERBOSE=args.verbose
		if VERBOSE:
			print 'Verbose Execution ...'

		json_config=readJSON_stringifyUnicodes(json_file_path)
		print 'Random Walk test...'
		rw_header=[ 'algorithm','nb_random_walks','timebudget','nb_visited_subgroups','nb_candidates_subgroups','nb_patterns',
					'sim_score_1','f1_score','precision','recall','timespent_init','timespent','timespent_total']
		if len(args.randomwalk)==0:
			result_file_destination='rw_results.csv'
		else:
			result_file_destination=args.randomwalk[0]

		sampling_algorithm='DSC+RandomWalk'
		if args.sampling_algorithm is not None and len(args.sampling_algorithm)>0:
			sampling_algorithm=args.sampling_algorithm[0]

		################################################################
		json_config['algorithm']=args.algos[0] if args.algos is not None else json_config['algorithm']
		json_config['nb_objects']=args.nb_obj[0] if args.nb_obj is not None else json_config['nb_objects']
		json_config['nb_individuals']=args.nb_ind[0] if args.nb_ind is not None else json_config['nb_individuals']
		nb_attr_desc_obj=args.nb_attr_desc_obj[0] if args.nb_attr_desc_obj is not None else len(json_config['description_attributes_objects'])
		json_config['description_attributes_objects']=json_config['description_attributes_objects'][:nb_attr_desc_obj]
		nb_attr_desc_ind=args.nb_attr_desc_ind[0] if args.nb_attr_desc_ind is not None else len(json_config['description_attributes_individuals'])
		json_config['description_attributes_individuals']=json_config['description_attributes_individuals'][:nb_attr_desc_ind]

		json_config['nb_items_entities']=args.nb_items_desc_obj[0] if args.nb_items_desc_obj is not None else float('inf')
		json_config['nb_items_individuals']=args.nb_items_desc_ind[0] if args.nb_items_desc_ind is not None else float('inf')

		json_config['hmt_to_itemset']=args.hmt_to_itemset
		
		json_config['threshold_objects']=args.sigma_obj[0] if args.sigma_obj is not None else json_config['threshold_objects']
		json_config['threshold_individuals']=args.sigma_ind[0] if args.sigma_ind is not None else json_config['threshold_individuals']
		json_config['threshold_quality']=args.sigma_qual[0] if args.sigma_qual is not None else json_config['threshold_quality']

		json_config['quality_measure']=args.quality_measure[0] if args.quality_measure is not None else json_config['quality_measure']
		json_config['similarity_measure']=args.similarity_measure[0] if args.similarity_measure is not None else json_config['similarity_measure']


		json_config['nb_random_walks']=args.nrwc if args.nrwc is not None else json_config.get('nb_random_walks',30.)
		#print json_config['nb_random_walks']
		#json_config['timebudget']=json_config['timebudget'] if args.timebudget is None else args.timebudget[0]
		################################################################



		json_config_copy=deepcopy(json_config)

		json_config_copy['algorithm']='DSC+CLOSED+UB2'
		if not ExhaustiveDoneYet:
			exhaustive_Results=next(DSC_input_config(json_config_copy,verbose=VERBOSE))

			stats_exhaustive_Results=deepcopy(DSC_input_config.stats)
			obj={
				'algorithm':stats_exhaustive_Results['algorithm'],
				'nb_random_walks':json_config['nb_random_walks'],
				'timebudget':stats_exhaustive_Results['timebudget'],
				'nb_visited_subgroups':stats_exhaustive_Results['nb_visited_subgroups'],
				'nb_candidates_subgroups':stats_exhaustive_Results['nb_candidates_subgroups'],
				'nb_patterns':stats_exhaustive_Results['nb_patterns'],
				'sim_score_1':1.,
				'f1_score':1.,
				'precision':1.,
				'recall':1.,
				'timespent_init':stats_exhaustive_Results['timespent_init'],
				'timespent':stats_exhaustive_Results['timespent'],
				'timespent_total':stats_exhaustive_Results['timespent_total']
			}

			results_rw=[]
			results_rw.append(obj)
			writeCSVwithHeader(results_rw,result_file_destination,selectedHeader=rw_header,flagWriteHeader=True)
			print 'Exhaustive search done, timespent = ', obj['timespent']
			pat_set_1=[(frozenset(x[1][0]),frozenset(x[1][1]),frozenset(x[1][2])) for x in exhaustive_Results]


			if not os.path.exists('./RW_Results'):
					os.makedirs('./RW_Results')
			# else:
			# 	shutil.rmtree('./RW_Results')
			# 	os.makedirs('./RW_Results')

			with open('./RW_Results//EX_results.dsc', 'wb') as fp:
				pickle.dump({'stats':stats_exhaustive_Results,'results':exhaustive_Results}, fp)
		else:
			with open ('./RW_Results//EX_results.dsc', 'rb') as fp:
				#returned_results_1 = pickle.load(fp)
				loaded_file=pickle.load(fp)
				stats_exhaustive_Results=loaded_file['stats']
				exhaustive_Results = loaded_file['results']#pickle.load(fp)
				obj={
					'algorithm':stats_exhaustive_Results['algorithm'],
					'nb_random_walks':json_config['nb_random_walks'],
					'timebudget':stats_exhaustive_Results['timebudget'],
					'nb_visited_subgroups':stats_exhaustive_Results['nb_visited_subgroups'],
					'nb_candidates_subgroups':stats_exhaustive_Results['nb_candidates_subgroups'],
					'nb_patterns':stats_exhaustive_Results['nb_patterns'],
					'sim_score_1':1.,
					'f1_score':1.,
					'precision':1.,
					'recall':1.,
					'timespent_init':stats_exhaustive_Results['timespent_init'],
					'timespent':stats_exhaustive_Results['timespent'],
					'timespent_total':stats_exhaustive_Results['timespent_total']
				}

				results_rw=[]
				results_rw.append(obj)
				writeCSVwithHeader(results_rw,result_file_destination,selectedHeader=rw_header,flagWriteHeader=True)


				pat_set_1=[(frozenset(x[1][0]),frozenset(x[1][1]),frozenset(x[1][2])) for x in exhaustive_Results]
				print 'Exhaustive search done, loaded'

		gc.collect()
		timebudget_to_iter_in=json_config_copy['timebudget'] if args.timebudget is None else args.timebudget
		if timebudget_to_iter_in[0]<1.:
			print 'Execution Based On Percentage Of Exhaustive : ', timebudget_to_iter_in
			timebudget_to_iter_in=[x*stats_exhaustive_Results['timespent'] for x in timebudget_to_iter_in]
			print 'Timebudgets : ', timebudget_to_iter_in


		

		if not OneExecutionTest:
			for timebudg in timebudget_to_iter_in:
				dest_new=json_config['results_destination']
				fileparent = dirname(dest_new)
				filename = splitext(basename(dest_new))[0]
				fileext=splitext(basename(dest_new))[1] 
				exportPath = (fileparent+"/" if len(fileparent) > 0 else "")+'RW_'+str(timebudg)+'_'+filename+fileext

				json_config_copy=deepcopy(json_config)
				json_config_copy['results_destination']=exportPath
				json_config_copy['algorithm']=sampling_algorithm#'DSC+RandomWalk'
				json_config_copy['timebudget']=timebudg
				obj={}
				
				obj['results']=next(DSC_input_config(json_config_copy,verbose=VERBOSE))
				##TODO##
				obj['stats']=deepcopy(DSC_input_config.stats)
				pat_set_2=[(frozenset(x[1][0]),frozenset(x[1][1]),frozenset(x[1][2])) for x in obj['results']]

				with open('./RW_Results//'+str(timebudg)+'_results.dsc', 'wb') as fp:
					pickle.dump({'stats':obj['stats'],'results':obj['results']}, fp)


				sim_score_1,f1_score,precision,recall=similarity_between_patterns_set(pat_set_1,pat_set_2) #TAKE TOO MANY TIME FIND A SOLUTION TO COMPUTE IT MORE

				obj['algorithm']=obj['stats']['algorithm']
				obj['nb_random_walks']=json_config['nb_random_walks']
				obj['timebudget']=timebudg
				obj['nb_visited_subgroups']=obj['stats']['nb_visited_subgroups']
				obj['nb_candidates_subgroups']=obj['stats']['nb_candidates_subgroups']
				obj['nb_patterns']=obj['stats']['nb_patterns']

				obj['sim_score_1']=sim_score_1
				obj['f1_score']=f1_score
				obj['precision']=precision
				obj['recall']=recall




				obj['timespent_init']=obj['stats']['timespent_init']
				obj['timespent']=obj['stats']['timespent']
				obj['timespent_total']=obj['stats']['timespent_total']
				results_rw=[]
				results_rw.append(obj)
				writeCSVwithHeader(results_rw,result_file_destination,selectedHeader=rw_header,flagWriteHeader=False)
				print 'RW search algorithm done, timespent = ', obj['timespent'], '%.2f'%(((obj['timespent']*100)/stats_exhaustive_Results['timespent'])), 'Similarity = ', '%.2f'%(obj['f1_score']*100) 
				gc.collect()
		else:
			PROFILING=False
			if PROFILING:
					pr = cProfile.Profile()
					pr.enable()
			
			print 'One execution Sampling Test ...', timebudget_to_iter_in
			flag_step=0
			timebudg=timebudget_to_iter_in[flag_step]

			dest_new=json_config['results_destination']
			fileparent = dirname(dest_new)
			filename = splitext(basename(dest_new))[0]
			fileext=splitext(basename(dest_new))[1] 
			exportPath = (fileparent+"/" if len(fileparent) > 0 else "")+'RW_'+str(timebudg)+'_'+filename+fileext
			json_config_copy=deepcopy(json_config)
			json_config_copy['results_destination']=exportPath
			json_config_copy['algorithm']=sampling_algorithm#'DSC+RandomWalk'
			json_config_copy['timebudget']=timebudget_to_iter_in
			obj={}	
			
			for results in DSC_input_config(json_config_copy,verbose=VERBOSE):

				obj['results']=results
				##TODO##
				obj['stats']=deepcopy(DSC_input_config.stats)
				pat_set_2=[(frozenset(x[1][0]),frozenset(x[1][1]),frozenset(x[1][2])) for x in obj['results']]

				with open('./RW_Results//'+str(timebudg)+'_results.dsc', 'wb') as fp:
					pickle.dump({'stats':obj['stats'],'results':obj['results']}, fp)


				sim_score_1,f1_score,precision,recall=similarity_between_patterns_set(pat_set_1,pat_set_2) #TAKE TOO MANY TIME FIND A SOLUTION TO COMPUTE IT MORE

				obj['algorithm']=obj['stats']['algorithm']
				obj['nb_random_walks']=json_config['nb_random_walks']
				obj['timebudget']=timebudg
				obj['nb_visited_subgroups']=obj['stats']['nb_visited_subgroups']
				obj['nb_candidates_subgroups']=obj['stats']['nb_candidates_subgroups']
				obj['nb_patterns']=obj['stats']['nb_patterns']

				obj['sim_score_1']=sim_score_1
				obj['f1_score']=f1_score
				obj['precision']=precision
				obj['recall']=recall




				obj['timespent_init']=obj['stats']['timespent_init']
				obj['timespent']=obj['stats']['timespent']
				obj['timespent_total']=obj['stats']['timespent_total']
				results_rw=[]
				results_rw.append(obj)
				writeCSVwithHeader(results_rw,result_file_destination,selectedHeader=rw_header,flagWriteHeader=False)
				print 'Timespent = ', obj['timespent'], ' ;', 'Percentage = ', '%.2f'%(((obj['timespent']*100)/stats_exhaustive_Results['timespent'])) + ' %',';', 'Similarity = ', '%.2f'%(obj['f1_score']*100) + ' %'
				flag_step+=1
				if flag_step<len(timebudget_to_iter_in):
					timebudg=timebudget_to_iter_in[flag_step]
					exportPath = (fileparent+"/" if len(fileparent) > 0 else "")+'RW_'+str(timebudg)+'_'+filename+fileext
					json_config_copy['results_destination']=exportPath
			if PROFILING:
					pr.disable()
					ps = pstats.Stats(pr)
					ps.sort_stats('cumulative').print_stats(50) #time

		#writeCSVwithHeader(results_rw,result_file_destination,selectedHeader=rw_header)

	elif type(args.figure) is list:
		from plotter.perfPlotter import plotPerf,plotRW,plotHistograms_edf
		if args.edf:
			resulting_file,resulting_file_header=readCSVwithHeader(json_file_path,numberHeader=['nb_patterns_returned'],arrayHeader=["edf"])
			for row in resulting_file:
				edf_distribution=[float(x) for x in row['edf']]
				row['edf']=edf_distribution
				#print row['algorithm'],row['no_generality'],row['no_sigma_quality'],row['nb_patterns_returned'],edf_distribution,
			plotHistograms_edf(resulting_file,'./figure.pdf',activated=[2,3])
			# algorithm
			# no_generality
			# no_sigma_quality
			# edf
			# nb_patterns_returned
			#readCSVwithHeader(json_file_path,json_config['results_destination'],numberHeader=['ref_sim','pattern_sim','quality'])
		else:
			if not args.rwf:
				activated=args.fig_algos if args.fig_algos is not None and len(args.fig_algos)>0 else ["DSC","DSC+CLOSED","DSC+CLOSED+UB1","DSC+CLOSED+UB2"]
				plotPerf(json_file_path,args.x_axis_attribute,activated=activated,BAR_LOG_SCALE=not args.linear_scale,TIME_LOG_SCALE=not args.linear_scale,plot_bars = not args.do_not_plot_bars, plot_time = not args.do_not_plot_time,results_destination=args.results_destination)
			else:
				sampling_algorithm='DSC+RandomWalk'
				if args.sampling_algorithm is not None and len(args.sampling_algorithm)>0:
					sampling_algorithm=args.sampling_algorithm[0]
				plotRW(json_file_path,args.x_axis_attribute,activated=[sampling_algorithm])
	
	# for k,v in DSC_Entry_Point.stats.iteritems():
	# 	print k,' : ',v
	
if __name__ == '__main__':
	#from plotter.perfPlotter import plotPerf
	#plotPerf('performance.csv','nb_objects',activated=["DSC+CLOSED+UB2","DSC+CLOSED+UB1"])
	
	#main_1()
	main_2()
	
	