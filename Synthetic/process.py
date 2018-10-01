import argparse
from outcomeDatasetsProcessor.outcomeDatasetsProcessor import process_outcome_dataset
from outcomeAggregator.aggregateOutcome import compute_aggregates_outcomes
from outcomeAggregator.outcomeRepresentation import outcome_representation_in_reviews
from util.csvProcessing import readCSVwithHeader,writeCSVwithHeader,writeCSV
from util.jsonProcessing import writeJSON,readJSON,readJSON_stringifyUnicodes
from enumerator.enumerator_attribute_complex import init_attributes_complex,create_index_complex,enumerator_complex_cbo_init_new_config
from subprocess import call
from numpy.random import choice,multinomial,permutation
from itertools import izip,product
from random import random,randint
from measures.similaritiesDCS import similarity_vector_measure_dcs
from subprocess import call,check_output
from operator import itemgetter
import os 
import shutil
from copy import deepcopy
import time
def get_tuple_structure(all_users_to_items_outcomes):
	one_entitie=all_users_to_items_outcomes[next(all_users_to_items_outcomes.iterkeys())]
	one_item=next(one_entitie.iterkeys())
	outcome_tuple_structure=tuple(one_entitie[one_item])
	return outcome_tuple_structure


def create_behavioralconfronting_dataset(
	itemsfile,
	usersfile,
	outcomesfile,
	numeric_attrs=[],
	array_attrs=[],
	outcome_attrs=None,
	method_aggregation_outcome='VECTOR_VALUES',
	itemsScope=[],
	users_1_Scope=[],
	users_2_Scope=[],
	nb_items=float('inf'),
	nb_individuals=float('inf'),
	attributes_to_consider=None,
	nb_items_entities=float('inf'),
	nb_items_individuals=float('inf'),
	hmt_to_itemset=False,
	create_boolean_attributes_for_hmt=False,
	delimiter='\t'): 
	
	tags_with_label=True
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered,vector_of_action =\
		process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,hmt_to_itemset=hmt_to_itemset,delimiter=delimiter)

	all_votes_id=set(_[items_id_attribute] for _ in considered_items_sorted)
	outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)

	u_1_agg_votes=compute_aggregates_outcomes(all_votes_id,set(_[users_id_attribute] for _ in considered_users_1_sorted),all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
	u_2_agg_votes=compute_aggregates_outcomes(all_votes_id,set(_[users_id_attribute] for _ in considered_users_2_sorted),all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)

	considered_votes=set(u_1_agg_votes) & set(u_2_agg_votes)
	new_behavioral_dataset=[]
	

	items,items_header=readCSVwithHeader(itemsfile,numberHeader=numeric_attrs,arrayHeader=array_attrs,selectedHeader=None,delimiter=delimiter)
	##############TEMPORARY#########################
	if create_boolean_attributes_for_hmt:
		attributes=[{'name':attr,'type':'themes'} for attr in set(attributes_to_consider)&set(array_attrs)]
		attributes = init_attributes_complex(considered_items_sorted,attributes) #X
		index_all = create_index_complex(considered_items_sorted, attributes) #Y
		
		for attr in attributes:
			attr_domain=attr['domain']
			attr_name=attr['name']
			attr_labelmap=attr['labelmap']
			for x in attr_labelmap:
				attr_labelmap[x]=attr_labelmap[x].replace(',',';')
				attr_labelmap[x]=attr_labelmap[x].replace(' ','_')
			all_tags=sorted(set(attr_domain)-{''})



			if tags_with_label:
				new_attributes_items={attr_labelmap[x]:None for x in all_tags}
			else:
				new_attributes_items={x:None for x in all_tags}

			items_header=items_header[:items_header.index(attr_name)]+sorted(new_attributes_items)+items_header[items_header.index(attr_name)+1:]
			

			# for t in all_tags:
			# 	print t,attr_labelmap[t]
			# 	raw_input('...')
			for i,o in enumerate(considered_items_sorted):
				print i
				# print o[attr_name]
				# print index_all[i][attr_name]
				
				new_attributes_items_o=dict(new_attributes_items)
				
				for t in index_all[i][attr_name]:
					
					if tags_with_label:
						t_attr_associated=attr_labelmap[t]
					else:
						t_attr_associated=t
					new_attributes_items_o[t_attr_associated]=True


				o.update(new_attributes_items_o)

				



				#raw_input('...')
		# for row in considered_items_sorted:
		# 	for attr in set(attributes_to_consider)&set(array_attrs):
		# 		attr_domain=attr['domain']
		# 		for t in attr_domain:
		# 			print t 
		# 			raw_input('...')

	##############TEMPORARY#########################

	for row in considered_items_sorted:
		if row[items_id_attribute] in considered_votes:
			row_to_insert=dict(row)
			row_to_insert['OUTCOME_U1']=u_1_agg_votes[row[items_id_attribute]]
			row_to_insert['OUTCOME_U2']=u_2_agg_votes[row[items_id_attribute]]
			row_to_insert['SIMILARITY']=float(1.*(row_to_insert['OUTCOME_U1']!=row_to_insert['OUTCOME_U2']))
			new_behavioral_dataset.append(row_to_insert)
	
	#items_header=items_header+['OUTCOME_U1']+['OUTCOME_U2']+['SIMILARITY']
	items_header=['SIMILARITY']+sorted(new_attributes_items)
	return new_behavioral_dataset,items_header




def create_behavioral_cartesian_dataset(
	itemsfile,
	usersfile,
	outcomesfile,
	numeric_attrs=[],
	array_attrs=[],
	outcome_attrs=None,
	method_aggregation_outcome='SYMBOLIC_MAJORITY',
	itemsScope=[],
	users_1_Scope=[],
	users_2_Scope=[],
	nb_items=float('inf'),
	nb_individuals=float('inf'),
	attributes_to_consider=None,
	nb_items_entities=float('inf'),
	nb_items_individuals=float('inf'),
	hmt_to_itemset=False,
	create_boolean_attributes_for_hmt=False,
	delimiter='\t'): 
	
	tags_with_label=True
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered,vector_of_action =\
		process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,hmt_to_itemset=hmt_to_itemset,delimiter=delimiter)

	new_behavioral_dataset_cartesian=[]
	for u in all_users_to_items_outcomes:
		for e in all_users_to_items_outcomes[u]:
			all_users_to_items_outcomes[u][e]=all_users_to_items_outcomes[u][e][0]

	users_set=set(all_users_to_items_outcomes.viewkeys())

	constitute_header=True
	header_to_ret=[]
	for u1 in users_set:
		


		for u2 in users_set-{u1}:

			for e in all_users_to_items_outcomes[u1].viewkeys()&all_users_to_items_outcomes[u2].viewkeys():
				record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
				record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
				if constitute_header:
					header_to_ret=[users_id_attribute+'_1']+sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[users_id_attribute+'_2']+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+[items_id_attribute]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['EQ_VOTE']

				constitute_header=False
				record.update(items_metadata[e])
				record['EQ_VOTE']= '+' if all_users_to_items_outcomes[u1][e]==all_users_to_items_outcomes[u2][e] else '-'
				new_behavioral_dataset_cartesian.append(record)






	
	return new_behavioral_dataset_cartesian,header_to_ret



def create_behavioral_cartesian_dataset_for_COSMIC(
	itemsfile,
	usersfile,
	outcomesfile,
	numeric_attrs=[],
	array_attrs=[],
	outcome_attrs=None,
	method_aggregation_outcome='SYMBOLIC_MAJORITY',
	itemsScope=[],
	users_1_Scope=[],
	users_2_Scope=[],
	nb_items=float('inf'),
	nb_individuals=float('inf'),
	attributes_to_consider=None,
	nb_items_entities=float('inf'),
	nb_items_individuals=float('inf'),
	hmt_to_itemset=False,
	create_boolean_attributes_for_hmt=False,
	delimiter='\t'): 
	
	tags_with_label=True
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered,vector_of_action =\
		process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,hmt_to_itemset=hmt_to_itemset,delimiter=delimiter)
	
	new_behavioral_dataset_cartesian=[]

	for u in all_users_to_items_outcomes:
		for e in all_users_to_items_outcomes[u]:
			all_users_to_items_outcomes[u][e]=all_users_to_items_outcomes[u][e][0]

	users_set=set(all_users_to_items_outcomes.viewkeys())
	users_set_sorted=sorted(users_set)
	constitute_header=True
	header_to_ret=[]
	i,j=0,0
	#for u1 in users_set:
	for u1_index in range(len(users_set_sorted)):
		u1=users_set_sorted[u1_index]

		#for u2 in users_set-{u1}:
		for u2_index in range(u1_index+1,len(users_set_sorted)):
			u2=users_set_sorted[u2_index]
			for e in all_users_to_items_outcomes[u1].viewkeys()&all_users_to_items_outcomes[u2].viewkeys():
				i+=1
				if constitute_header:
					#header_to_ret=[users_id_attribute+'_1']+sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[users_id_attribute+'_2']+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+[items_id_attribute]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['IN','OUT']
					header_to_ret=sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['IN','OUT']
					new_behavioral_dataset_cartesian.append({x:'S' for x in header_to_ret})
					new_behavioral_dataset_cartesian.append({x:'*' for x in header_to_ret})
					#header_to_ret=[users_id_attribute+'_1']+sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['IN','OUT']
					constitute_header=False
				
				if all_users_to_items_outcomes[u1][e]!=all_users_to_items_outcomes[u2][e]:
					j+=1
					record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
					record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
					record.update(items_metadata[e].copy())
					record['IN']= u1
					record['OUT']= u2
					new_behavioral_dataset_cartesian.append(record)
					

					j+=1
					record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
					record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
					record.update(items_metadata[e].copy())
					record['IN']= u2
					record['OUT']= u1
					new_behavioral_dataset_cartesian.append(record)
					
				# else:
				# 	j+=1
				# 	record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
				# 	record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
				# 	record.update(items_metadata[e].copy())
				# 	record['IN']= u1
				# 	record['OUT']= u2
				# 	new_behavioral_dataset_cartesian.append(record)
				# 	j+=1
				# 	record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
				# 	record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
				# 	record.update(items_metadata[e].copy())
				# 	record['IN']= u2
				# 	record['OUT']= u1
				# 	new_behavioral_dataset_cartesian.append(record)

					#print i,j
					# print record
					# raw_input('....')





	print len(new_behavioral_dataset_cartesian)
	#raw_input('....')
	return new_behavioral_dataset_cartesian,header_to_ret




def create_behavioral_cartesian_dataset_for_COSMIC_BIPARTITE(
	itemsfile,
	usersfile,
	outcomesfile,
	numeric_attrs=[],
	array_attrs=[],
	outcome_attrs=None,
	method_aggregation_outcome='SYMBOLIC_MAJORITY',
	itemsScope=[],
	users_1_Scope=[],
	users_2_Scope=[],
	nb_items=float('inf'),
	nb_individuals=float('inf'),
	attributes_to_consider=None,
	nb_items_entities=float('inf'),
	nb_items_individuals=float('inf'),
	hmt_to_itemset=False,
	create_boolean_attributes_for_hmt=False,
	delimiter='\t'): 
	
	tags_with_label=True
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered,vector_of_action =\
		process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,hmt_to_itemset=hmt_to_itemset,delimiter=delimiter)
	
	new_behavioral_dataset_cartesian=[]

	for u in all_users_to_items_outcomes:
		for e in all_users_to_items_outcomes[u]:
			all_users_to_items_outcomes[u][e]=all_users_to_items_outcomes[u][e][0]

	users_set=set(all_users_to_items_outcomes.viewkeys())
	users_set_sorted=sorted(users_set)
	constitute_header=True
	header_to_ret=[]
	i,j=0,0
	for u1 in users_set:
	#for u1_index in range(len(users_set_sorted)):
	#	u1=users_set_sorted[u1_index]

		for u2 in users_set-{u1}:
		#for u2_index in range(u1_index+1,len(users_set_sorted)):
		#	u2=users_set_sorted[u2_index]
			for e in all_users_to_items_outcomes[u1].viewkeys()&all_users_to_items_outcomes[u2].viewkeys():
				i+=1
				if constitute_header:
					#header_to_ret=[users_id_attribute+'_1']+sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[users_id_attribute+'_2']+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+[items_id_attribute]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['IN','OUT']
					header_to_ret=sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['IN','OUT']
					new_behavioral_dataset_cartesian.append({x:'S' for x in header_to_ret})
					new_behavioral_dataset_cartesian.append({x:'*' for x in header_to_ret})
					#header_to_ret=[users_id_attribute+'_1']+sorted([x+'_1' for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[x+'_2' for x in sorted(users_metadata[u2].viewkeys()-{users_id_attribute})]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['IN','OUT']
					constitute_header=False
				
				if all_users_to_items_outcomes[u1][e]!=all_users_to_items_outcomes[u2][e]:
					j+=1
					record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
					record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
					record.update(items_metadata[e].copy())
					record['IN']= u1
					record['OUT']= u2+'PRIME'
					new_behavioral_dataset_cartesian.append(record)
					

					# j+=1
					# record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
					# record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
					# record.update(items_metadata[e].copy())
					# record['IN']= u2+'PRIME'
					# record['OUT']= u1
					# new_behavioral_dataset_cartesian.append(record)
					
				# else:
				# 	j+=1
				# 	record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
				# 	record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
				# 	record.update(items_metadata[e].copy())
				# 	record['IN']= u1
				# 	record['OUT']= u2
				# 	new_behavioral_dataset_cartesian.append(record)
				# 	j+=1
				# 	record={k+'_1':v for k,v in users_metadata[u1].iteritems()}
				# 	record.update({k+'_2':v for k,v in users_metadata[u2].iteritems()})
				# 	record.update(items_metadata[e].copy())
				# 	record['IN']= u2
				# 	record['OUT']= u1
				# 	new_behavioral_dataset_cartesian.append(record)

					#print i,j
					# print record
					# raw_input('....')





	print len(new_behavioral_dataset_cartesian)
	#raw_input('....')
	return new_behavioral_dataset_cartesian,header_to_ret



def create_behavioral_with_majority_dataset(
	itemsfile,
	usersfile,
	outcomesfile,
	numeric_attrs=[],
	array_attrs=[],
	outcome_attrs=None,
	method_aggregation_outcome='SYMBOLIC_MAJORITY',
	itemsScope=[],
	users_1_Scope=[],
	users_2_Scope=[],
	nb_items=float('inf'),
	nb_individuals=float('inf'),
	attributes_to_consider=None,
	nb_items_entities=float('inf'),
	nb_items_individuals=float('inf'),
	hmt_to_itemset=False,
	create_boolean_attributes_for_hmt=False,
	delimiter='\t'): 
	
	tags_with_label=True
	items_metadata,users_metadata,all_users_to_items_outcomes,outcomes_considered,items_id_attribute,users_id_attribute,considered_items_sorted,considered_users_1_sorted,considered_users_2_sorted,nb_outcome_considered,vector_of_action =\
		process_outcome_dataset(itemsFile,usersFile,reviewsFile,numeric_attrs=numeric_attrs,array_attrs=array_attrs,outcome_attrs=outcome_attrs,method_aggregation_outcome=method_aggregation_outcome,itemsScope=itemsScope,users_1_Scope=users_1_Scope,users_2_Scope=users_2_Scope,nb_items=nb_items,nb_individuals=nb_individuals,attributes_to_consider=attributes_to_consider,nb_items_entities=nb_items_entities,nb_items_individuals=nb_items_individuals,hmt_to_itemset=hmt_to_itemset,delimiter=delimiter)

	new_behavioral_dataset_majority=[]
	
	all_votes_id=set(items_metadata.viewkeys())

	for u in all_users_to_items_outcomes:
		for e in all_users_to_items_outcomes[u]:
			all_users_to_items_outcomes[u][e]=all_users_to_items_outcomes[u][e]
			

	users_set=set(all_users_to_items_outcomes.viewkeys())
	constitute_header=True
	outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)
	print outcome_tuple_structure
	majority_agg_votes=compute_aggregates_outcomes(all_votes_id,users_set,all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
	# for e in majority_agg_votes:
	# 	# print e,majority_agg_votes[e]
	# 	# raw_input('....')

	for u in all_users_to_items_outcomes:
		for e in all_users_to_items_outcomes[u]:

			all_users_to_items_outcomes[u][e]=all_users_to_items_outcomes[u][e][0]

	


	header_to_ret=[]
	for u1 in users_set:
		
		
		for e in all_users_to_items_outcomes[u1]:
			record={k:v for k,v in users_metadata[u1].iteritems()}
			if constitute_header:
				header_to_ret=[users_id_attribute]+sorted([x for x in users_metadata[u1].viewkeys()-{users_id_attribute}])+[items_id_attribute]+sorted(items_metadata[e].viewkeys()-{items_id_attribute})+['EQ_VOTE']
				constitute_header=False
			
			record.update(items_metadata[e].copy())
			
			try:
				record['EQ_VOTE']= '+' if all_users_to_items_outcomes[u1][e]==majority_agg_votes[e] else '-'
			except:
				continue
			
			# print record
			# raw_input('....')
			new_behavioral_dataset_majority.append(record)
		
	



	print header_to_ret

	# for row in new_behavioral_dataset:
	# 		print row
	# 		raw_input('...')
	
	return new_behavioral_dataset_majority,header_to_ret



# def recursive_generation(current,choosen=[]):
# 	if len(current)>0:
		
# 		a=current[0]
# 		if len(choosen)==0:
# 			chance_to_not_choose_a=(2**(len(current)-1)-1)/(float(2**len(current)-1))
# 		else:
# 			chance_to_not_choose_a=1/2.
# 		if random()>=chance_to_not_choose_a:
# 			return recursive_generation(current[1:],choosen+[a])
# 		else:
# 			return recursive_generation(current[1:],choosen)
# 	else:
# 		return choosen

def nb_combin(n,r):
	return reduce(lambda x, y: x * y[0] / y[1], izip(xrange(n - r + 1, n+1), xrange(1, r+1)), 1)

def number_of_all_subsets_not_empty_of_size_under_max(n,k):
	return sum(nb_combin(n,x) for x in  range(1,k+1))

def recursive_generation(current,choosen=[]):
	if len(current)>0:

		a=current[0]
		if len(choosen)==0:
			chance_to_not_choose_a=(2**(len(current)-1)-1)/(float(2**len(current)-1))
		else:
			chance_to_not_choose_a=1/2.
		if random()>=chance_to_not_choose_a:
			return recursive_generation(current[1:],choosen+[a])
		else:
			return recursive_generation(current[1:],choosen)
	else:
		return choosen

#recursive_generation(['a','b','c'])

# def recursive_generation_2(current,choosen=[],nb_max=float('inf')):
# 	if nb_max==float('inf'):
# 		nb_max=len(current)
# 	if len(current)>0 and nb_max>0:

# 		aindex=choice(range(len(current)),1)[0]
# 		a=current[aindex]
# 		new_current=current[:aindex]+current[aindex+1:]
# 		if len(choosen)==0:
# 			#nb_not_containing=float(number_of_all_subsets_not_empty_of_size_under_max(len(current),nb_max-1))
# 			chance_to_not_choose_a=number_of_all_subsets_not_empty_of_size_under_max(len(current)-1,nb_max-1)/float(number_of_all_subsets_not_empty_of_size_under_max(len(current),nb_max))
# 		else:
# 			chance_to_not_choose_a=1/2.
# 		if random()>=chance_to_not_choose_a:
# 			return recursive_generation_2(new_current,choosen+[a],nb_max-1)
# 		else:
# 			return recursive_generation_2(new_current,choosen,nb_max-1)
# 	else:
# 		return choosen

# def generate_random_non_empty_itemset_2(attributes,nb_max=float('inf')):
# 	#attributes_to_use=permutation(attributes)
# 	return sorted(recursive_generation_2(attributes,[],nb_max))

def generate_random_non_empty_itemset_with_max(attributes,nb_max=float('inf')):
	if nb_max==float('inf'):
		nb_max=len(attributes)
	probability_of_a_subset=[nb_combin(len(attributes),k) for k in range(1,nb_max+1)]
	all_weights=float(sum(probability_of_a_subset))
	probability_of_a_subset=[x/all_weights for x in probability_of_a_subset]
	size_subset=choice(nb_max, 1, p=probability_of_a_subset)[0]+1
	subset=choice(attributes, size_subset,replace=False)
	return sorted(subset)


def generate_random_non_empty_itemset_with_min_and_max(attributes,nb_min=1,nb_max=float('inf')):
	if nb_max==float('inf'):
		nb_max=len(attributes)
	probability_of_a_subset=[nb_combin(len(attributes),k) for k in range(nb_min,nb_max+1)]
	all_weights=float(sum(probability_of_a_subset))
	probability_of_a_subset=[x/all_weights for x in probability_of_a_subset]
	size_subset=choice(len(probability_of_a_subset), 1, p=probability_of_a_subset)[0]+nb_min
	subset=choice(attributes, size_subset,replace=False)
	return sorted(subset)



# def generate_random_subsuming_patterns(itemset_1,itemset_2):
# 	s_1=set(itemset_1)
# 	s_2=set(itemset_2)
# 	g_1=set(itemset_1)
# 	g_2=set(itemset_2)
# 	while g_1 == s_1 and g_2 == s_2:
# 		ret_1=sorted(generate_random_non_empty_itemset_with_max(itemset_1,nb_max=len(itemset_1)-1))
# 		ret_2=sorted(generate_random_non_empty_itemset_with_max(itemset_2,nb_max=len(itemset_2)-1))
# 		g_1=set(ret_1)
# 		g_2=set(ret_2)
# 	#print itemset_1,itemset_2,ret_1,ret_2	
# 	return ret_1,ret_2

def generate_random_subsuming_behavioral_patterns(c,g_1,g_2):
	
	#while g_1 == s_1 and g_2 == s_2:
	ret_c=sorted(generate_random_non_empty_itemset_with_max(c,nb_max=len(c)-1))
	ret_g_1=sorted(generate_random_non_empty_itemset_with_max(g_1,nb_max=len(g_1)-1))
	ret_g_2=sorted(generate_random_non_empty_itemset_with_max(g_2,nb_max=len(g_2)-1))
		
	#print itemset_1,itemset_2,ret_1,ret_2	
	return ret_c,ret_g_1,ret_g_2

# def generate_random_subsuming_behavioral_patterns_with_a_taboo_list_authorize_subsumption(c,g_1,g_2):
	
# 	#while g_1 == s_1 and g_2 == s_2:
# 	ret_c=sorted(generate_random_non_empty_itemset_with_max(c,nb_max=len(c)-1))
# 	ret_g_1=sorted(generate_random_non_empty_itemset_with_max(g_1,nb_max=len(g_1)-1))
# 	ret_g_2=sorted(generate_random_non_empty_itemset_with_max(g_2,nb_max=len(g_2)-1))
		
# 	#print itemset_1,itemset_2,ret_1,ret_2	
# 	return ret_c,ret_g_1,ret_g_2




def generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes,nb_max=float('inf'),taboo_list=[]):
	taboo_list_sets=set(frozenset(x) for x in taboo_list)
	
	while True:
		clean_itemset_to_generate=True
		ret=generate_random_non_empty_itemset_with_max(attributes,nb_max)
		s_ret=frozenset(ret)
		for x in taboo_list_sets:
			if x<=s_ret:
				clean_itemset_to_generate=False
				break



		if clean_itemset_to_generate:
			break 
	return ret



def generate_random_subsuming_behavioral_patterns_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_individuals,nb_max_items_entities,nb_max_items_individuals,taboo_list):
	

	ret_c=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_entities,nb_max=nb_max_items_entities,taboo_list=[x[0] for x in taboo_list]))
	ret_g_1=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[x[1] for x in taboo_list]+[x[2] for x in taboo_list]))
	ret_g_2=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[x[1] for x in taboo_list]+[x[2] for x in taboo_list]))

	#print itemset_1,itemset_2,ret_1,ret_2	
	return ret_c,ret_g_1,ret_g_2






def generate_random_non_empty_itemset_with_min_and_max_with_a_taboo_list_not_comparable(attributes,nb_min=1,nb_max=float('inf'),taboo_list=[]):
	taboo_list_sets=set(frozenset(x) for x in taboo_list)
	
	while True:
		clean_itemset_to_generate=True
		ret=generate_random_non_empty_itemset_with_min_and_max(attributes,nb_min=nb_min,nb_max=nb_max)
		s_ret=frozenset(ret)
		for x in taboo_list_sets:
			if x<=s_ret or x>=s_ret:
				clean_itemset_to_generate=False
				break



		if clean_itemset_to_generate:
			break 
	return ret


def generate_random_non_empty_itemset(attributes):
	#attributes_to_use=permutations(attributes)
	return recursive_generation(attributes,[])





def test_generator(n,attrs):
	dicts={}
	for _ in xrange(n):
		gen=tuple(generate_random_non_empty_itemset(attrs))
		dicts[gen]=dicts.get(gen,0)+1
	for row in dicts:
		dicts[row]=float(dicts[row])/float(n)
	for row in sorted(dicts):
		print row,dicts[row]


def test_generator_with_max(n,attrs,nb_max=float('inf')):
	dicts={}
	for _ in xrange(n):
		gen=tuple(generate_random_non_empty_itemset_with_max(attrs,nb_max))
		dicts[gen]=dicts.get(gen,0)+1
	for row in dicts:
		dicts[row]=float(dicts[row])/float(n)
	for row in sorted(dicts):
		print row,dicts[row]

#noise_factor: the objects generated of the pattern being positive are affected to their specific description with a probability of 1-noise_factor.
#noise_rate_add_subsuming_parents: we generate noise_rate_add_subsuming_parents*support_of_hidden_patterns objects with a negative label.


def compute_support(dataset,pattern):
	sp=set(pattern)
	
	return [i for i,row in enumerate(dataset) if row>=sp]











def generate_random_non_empty_categorical_description(categorical_attributes,domains_per_attributes):
	

	#desc_length=randint(1,len(categorical_attributes))
	desc_length=randint(2,len(categorical_attributes))

	desc_attributes=choice(categorical_attributes, desc_length,replace=False).tolist()


	desc_ret={a:choice(domains_per_attributes[a], 1)[0] for a in desc_attributes}
	# print desc_length
	# print desc_attributes
	# print desc_ret
	# raw_input('....')
	return desc_ret

def generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(categorical_attributes,domains_per_attributes,taboo_list=[]):
	
	while True:
		can_return=True

		desc_ret=generate_random_non_empty_categorical_description(categorical_attributes,domains_per_attributes)
		desc_ret_set=set(desc_ret.values())
		for d in taboo_list:
			set_d=set(d.values()) 
			if desc_ret_set<=set_d or desc_ret_set>=set_d:
				can_return=False
				break
		if can_return:
			break


	return desc_ret

def generate_random_non_empty_categorical_description_with_a_taboo_list_authorize_subsumption(categorical_attributes,domains_per_attributes,taboo_list=[]):
	
	while True:
		can_return=True

		desc_ret=generate_random_non_empty_categorical_description(categorical_attributes,domains_per_attributes)
		desc_ret_set=set(desc_ret.values())
		for d in taboo_list:
			set_d=set(d.values()) 
			if set_d<=desc_ret_set:
				can_return=False
				break
		if can_return:
			break


	return desc_ret

def generate_random_object_with_categories(categorical_attributes,domains_per_attributes,starting_description={}):
	o=starting_description.copy()
	for a in set(categorical_attributes)-set(o):
		o[a]=choice(domains_per_attributes[a], 1)[0]
	return o

def generate_random_object_with_categories_with_a_taboo_list_not_comparable(categorical_attributes,domains_per_attributes,starting_description={},taboo_list=[]):
	

	while True:
		can_return=True
		o=generate_random_object_with_categories(categorical_attributes,domains_per_attributes,starting_description)
		o_ret=set(o.values())
		for d in taboo_list:
			set_d=set(d.values()) 
			if set_d<=o_ret or set_d>=o_ret:
				can_return=False
				break

		if can_return:
			break

	return o

def generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(categorical_attributes,domains_per_attributes,starting_description={},taboo_list=[]):
	
	nb_iter_max=50
	while True:
		
		can_return=True
		o=generate_random_object_with_categories(categorical_attributes,domains_per_attributes,starting_description)
		o_ret=set(o.values())
		for d in taboo_list:
			set_d=set(d.values()) 
			if set_d<=o_ret:
				can_return=False
				break

		if can_return:
			break
		
		nb_iter_max-=1
		if nb_iter_max==0:
			o=generate_random_object_with_categories(categorical_attributes,domains_per_attributes,starting_description)
			print 'SOUCII !!'
			break
	return o

def generate_random_object_with_categories_which_is_a_subsumption(categorical_attributes,domains_per_attributes,starting_description={},taboo_list=[]):
	

	while True:
		can_return=True
		starting_description_copied=deepcopy(starting_description) 
		random_length_of_modif=randint(0,len(starting_description)-1)
		if random_length_of_modif>0:
			#print len(starting_description),sorted(starting_description.values()),random_length_of_modif
			attrs_to_modify=choice(sorted(starting_description), random_length_of_modif,replace=False).tolist()
			for a in attrs_to_modify:
				starting_description_copied[a]=choice(domains_per_attributes[a], 1)[0]



		o=generate_random_object_with_categories(categorical_attributes,domains_per_attributes,starting_description_copied)
		o_ret=set(o.values())
		for d in taboo_list:
			set_d=set(d.values()) 
			if set_d<=o_ret:
				can_return=False
				break

		if can_return:
			break

	return o

def compute_support_categorical(dataset,pattern):
	sp=set(pattern.values())
	
	return [i for i,row in enumerate(dataset) if set(row.values())>=sp]



def generate_synthetic_data_categorical(nb_attributes_entities=20
							,nb_max_items_entities=5 #domain size
							,nb_attributes_individuals=20
							,nb_max_items_individuals=5
							,nb_patterns=5
							,support_of_context_best_pattern=30
							,support_of_group_of_indiviudals=30
							,size_entities=1000
							,size_individuals=1000
							,noise_rate_add_subsuming_parents=0.1
							,noise_rate_negative_examples=0.1
							,sparsity_outcome=0.
							,noise_for_both_groups=False):
	
	
	sparsity_bar=1-sparsity_outcome
	possible_categorical_outcomes=['yes','no']
	method_aggregation_outcome='VECTOR_VALUES'
	looking_for_conflict=True

	attributes_entities=['CE'+str(x).zfill(4) for x in range(nb_attributes_entities)]
	attributes_individuals=['CI'+str(x).zfill(4)  for x in range(nb_attributes_individuals)]

	attributes_entities_domains={a:[a+'V'+str(i).zfill(4) for i in range(nb_max_items_entities)] for a in attributes_entities}
	attributes_individuals_domains={a:[a+'V'+str(i).zfill(4) for i in range(nb_max_items_individuals)] for a in attributes_individuals}


	patterns=[]
	patterns_sets=[]


	
	# print generated_context
	# print generate_random_object_with_categories(attributes_entities,attributes_entities_domains,generated_context)
	taboo_list_context=[]
	taboo_list_individuals=[]
	for _ in range(nb_patterns):
		#taboo_list_context=map(itemgetter(0),patterns)

		generated_context= generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(attributes_entities,attributes_entities_domains,taboo_list=taboo_list_context)
		taboo_list_context.append(generated_context)
		generated_g_1= generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,taboo_list=taboo_list_individuals)
		taboo_list_individuals.append(generated_g_1)
		generated_g_2= generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,taboo_list=taboo_list_individuals)
		taboo_list_individuals.append(generated_g_2)
		patterns.append((generated_context,generated_g_1,generated_g_2))
		patterns_sets.append((set(generated_context.values()),set(generated_g_1.values()),set(generated_g_2.values())))
		print patterns[-1]

	id_entity=0
	id_individuals=0


	sorted_data_entities=[]
	sorted_data_entities_only_descs=[]
	sorted_data_individuals=[]
	sorted_data_individuals_only_descs=[]
	support_contexts=[]
	support_individuals_u_1=[]
	support_individuals_u_2=[]
	outcomes={}
	for index,row in enumerate(patterns):
		support_contexts.append([]);
		for _ in range(support_of_context_best_pattern):
			starting_description={}
			starting_description.update(row[0])
			#o=generate_random_object_with_categories(attributes_entities,attributes_entities_domains,starting_description)
			o=generate_random_object_with_categories_with_a_taboo_list_not_comparable(attributes_entities,attributes_entities_domains,starting_description,taboo_list=[p[0] for i,p in enumerate(patterns) if i!=index])
			# print sorted(row[0].values())
			# print sorted(o.values())
			# raw_input('....')
			o['ide']=id_entity
			sorted_data_entities.append(o)
			odesc={x:o[x] for x in o if x != 'ide'}
			sorted_data_entities_only_descs.append(odesc)
			support_contexts[-1].append(id_entity)
			id_entity+=1
		support_individuals_u_1.append([]);

		for _ in range(support_of_group_of_indiviudals):
			starting_description={}
			starting_description.update(row[1])
			#o=generate_random_object_with_categories(attributes_individuals,attributes_individuals_domains,starting_description)
			o=generate_random_object_with_categories_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=[p[1] for i,p in enumerate(patterns) if i!=index]+[p[2] for i,p in enumerate(patterns)])
			o['idi']=id_individuals
			sorted_data_individuals.append(o)
			odesc={x:o[x] for x in o if x != 'idi'}
			sorted_data_individuals_only_descs.append(odesc)
			support_individuals_u_1[-1].append(id_individuals)
			id_individuals+=1
		support_individuals_u_2.append([]);
		for _ in range(support_of_group_of_indiviudals):
			starting_description={}
			starting_description.update(row[2])
			#o=generate_random_object_with_categories(attributes_individuals,attributes_individuals_domains,starting_description)
			o=generate_random_object_with_categories_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=[p[1] for i,p in enumerate(patterns)]+[p[2] for i,p in enumerate(patterns) if i!=index])
			o['idi']=id_individuals
			sorted_data_individuals.append(o)
			odesc={x:o[x] for x in o if x != 'idi'}
			sorted_data_individuals_only_descs.append(odesc)
			support_individuals_u_2[-1].append(id_individuals)

			id_individuals+=1


	for index,row in enumerate(patterns):

		
		sup_context_actu=set(compute_support_categorical(sorted_data_entities_only_descs,row[0]))
		sup_g1_actu=set(compute_support_categorical(sorted_data_individuals_only_descs,row[1]))
		sup_g2_actu=set(compute_support_categorical(sorted_data_individuals_only_descs,row[2]))

		for entity_id in set(range(size_entities)):
			action=choice(range(2),1)[0]
			action_indiv_1=possible_categorical_outcomes[action]
			action_indiv_2=possible_categorical_outcomes[(1+action)%2]
			for indiv_1_id in sup_g1_actu:
				if indiv_1_id not in outcomes:
					outcomes[indiv_1_id]={}
				if random()<= sparsity_bar:
					outcomes[indiv_1_id][entity_id]=action_indiv_1	
					if noise_for_both_groups:
						if random()<=(noise_rate_negative_examples):
							outcomes[indiv_1_id][entity_id]=choice(possible_categorical_outcomes,1)[0]

			for indiv_2_id in sup_g2_actu:
				if indiv_2_id not in outcomes:
					outcomes[indiv_2_id]={}
				
				if random()<= sparsity_bar:
					# if random()<=(1-noise_rate_negative_examples):
					# 	if entity_id in sup_context_actu:
					# 		outcomes[indiv_2_id][entity_id]=action_indiv_2
					# 	else:
					# 		outcomes[indiv_2_id][entity_id]=action_indiv_1
					# else:
					# 	outcomes[indiv_2_id][entity_id]=action_indiv_1
					if entity_id in sup_context_actu:
						if random()<=(1-noise_rate_negative_examples): #If not noisy
							outcomes[indiv_2_id][entity_id]=action_indiv_2
						else: #If noisy the two confronted groups votes the same
							outcomes[indiv_2_id][entity_id]=choice(possible_categorical_outcomes,1)[0]#action_indiv_1
					else:
						if random()<=(1-noise_rate_negative_examples): #If not noisy (the must vote the same outside the context)
							outcomes[indiv_2_id][entity_id]=action_indiv_1
						else: #if noisy they don't vote the same
							if True:
								outcomes[indiv_2_id][entity_id]=choice(possible_categorical_outcomes,1)[0]#action_indiv_2
							else:
								outcomes[indiv_2_id][entity_id]=action_indiv_1
						#outcomes[indiv_2_id][entity_id]=action_indiv_1
		
		#raw_input('...')
		
	
	remaining_entities=[]
	remaining_individuals=[]

	

	if True:
		now_entities=[]
		now_indiv_1=[]
		now_indiv_2=[]
		old_len_sorted_data_entities=len(sorted_data_entities)
		print 'BEFORE len(sorted_data_entities) : ',len(sorted_data_entities)
		print 'BEFORE len(sorted_data_individuals) : ',len(sorted_data_individuals)
		print 'adding_noise_parent_entities : ',int((size_entities-len(sorted_data_entities))*noise_rate_add_subsuming_parents)
		print 'adding_noise_parent_individuals : ',int(((size_individuals-len(sorted_data_individuals))*noise_rate_add_subsuming_parents)/2.)*2

		for _ in range(int((size_entities-len(sorted_data_entities))*noise_rate_add_subsuming_parents)):
			
			starting_description={}
			if True:
				starting_description=deepcopy(patterns[randint(0,len(patterns)-1)][0])
				for x in choice(sorted(starting_description.keys()),randint(1,len(starting_description)),replace=False).tolist():
					del starting_description[x]
			#o=generate_random_object_with_categories(attributes_entities,attributes_entities_domains,starting_description)
			
			#o=generate_random_object_with_categories_which_is_a_subsumption(attributes_entities,attributes_entities_domains,patterns[randint(0,len(patterns)-1)][0],taboo_list=map(itemgetter(0),patterns))
			
			# raw_input('...')

			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_entities_domains,starting_description,taboo_list=map(itemgetter(0),patterns))
			
			# print '------------------'
			# print sorted(patterns[0][0].values())
			# print sorted(o.values())
			# print '------------------'
			# raw_input('...')

			o['ide']=id_entity
			#remaining_entities.append(o)
			sorted_data_entities.append(o)
			odesc={x:o[x] for x in o if x != 'ide'}
			sorted_data_entities_only_descs.append(odesc)
			now_entities.append(id_entity)
			id_entity+=1

		for _ in range(int(((size_individuals-len(sorted_data_individuals))*noise_rate_add_subsuming_parents)/2.)):
			
			if True:
				starting_description=deepcopy(patterns[randint(0,len(patterns)-1)][1])
				for x in choice(sorted(starting_description.keys()),randint(1,len(starting_description)),replace=False).tolist():
					del starting_description[x]
			#o=generate_random_object_with_categories_which_is_a_subsumption(attributes_individuals,attributes_individuals_domains,patterns[randint(0,len(patterns)-1)][1],taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
			o['idi']=id_individuals
			#remaining_individuals.append(o)
			sorted_data_individuals.append(o)
			odesc={x:o[x] for x in o if x != 'idi'}
			sorted_data_individuals_only_descs.append(odesc)
			now_indiv_1.append(id_individuals)
			id_individuals+=1
			#o=generate_random_object_with_categories_which_is_a_subsumption(attributes_individuals,attributes_individuals_domains,patterns[randint(0,len(patterns)-1)][2],taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
			if True:
				starting_description=deepcopy(patterns[randint(0,len(patterns)-1)][2])
				for x in choice(sorted(starting_description.keys()),randint(1,len(starting_description)),replace=False).tolist():
					del starting_description[x]
			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
			o['idi']=id_individuals
			#remaining_individuals.append(o)
			sorted_data_individuals.append(o)
			odesc={x:o[x] for x in o if x != 'idi'}
			sorted_data_individuals_only_descs.append(odesc)
			now_indiv_2.append(id_individuals)
			id_individuals+=1


		for e in range(0,size_entities):	
		#for e in range(0,size_entities):
			action_num=choice(range(2),1)[0]
			#action_num=0
			action=possible_categorical_outcomes[action_num]
			action_bar=possible_categorical_outcomes[(1+action_num)%2]
			# action=choice(possible_categorical_outcomes,1)[0]
			# action_cont=possible_categorical_outcomes[(1+action)%2]
			for i in now_indiv_1:
				if i not in outcomes:
					outcomes[i]={}
				if random()<= sparsity_bar:
					outcomes[i][e]=action
					if noise_for_both_groups:
						if random()<=(noise_rate_negative_examples):
							outcomes[i][e]=choice(possible_categorical_outcomes,1)[0]

			for i in now_indiv_2:
				if i not in outcomes:
					outcomes[i]={}
				if random()<= sparsity_bar:
					#outcomes[i][e]=action
					if True:
						if random()<=(1-noise_rate_negative_examples): #If not noisy (the must vote the same outside the context)
							outcomes[i][e]=action
						else: #if noisy they don't vote the same
							outcomes[i][e]=choice(possible_categorical_outcomes,1)[0]#action_bar
					else:
						outcomes[i][e]=action
		
		print 'AFTER len(sorted_data_entities) : ',len(sorted_data_entities)
		print 'AFTER len(sorted_data_individuals) : ',len(sorted_data_individuals)
		#raw_input('...')
			###########################################
			###########################################

		for _ in range(size_entities-len(sorted_data_entities)):
			starting_description={}
			#o=generate_random_object_with_categories(attributes_entities,attributes_entities_domains,starting_description)
			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_entities_domains,starting_description,taboo_list=map(itemgetter(0),patterns))
			o['ide']=id_entity
			remaining_entities.append(o)
			sorted_data_entities.append(remaining_entities[-1].copy())
			odesc={x:o[x] for x in o if x != 'ide'}
			sorted_data_entities_only_descs.append(odesc)
			id_entity+=1

		
		for _ in range(size_individuals-len(sorted_data_individuals)):
			starting_description={}
			#o=generate_random_object_with_categories(attributes_individuals,attributes_individuals_domains,starting_description)
			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			o['idi']=id_individuals
			remaining_individuals.append(o)
			sorted_data_individuals.append(remaining_individuals[-1].copy())
			odesc={x:o[x] for x in o if x != 'idi'}
			sorted_data_individuals_only_descs.append(odesc)
			id_individuals+=1

		


		for row in remaining_individuals:
			id_individual=row['idi']
			if id_individual not in outcomes:
				outcomes[id_individual]={}

			for e in range(0,size_entities):
				if random()<= sparsity_bar:
					outcomes[id_individual][e]=choice(possible_categorical_outcomes,1)[0]


	outcomes_flat=[ {'idi':i,'ide':e, 'outcome':outcomes[i][e]} for i in outcomes for e in outcomes[i]]
	

	# print outcomes_flat[0]
	# print len(sorted_data_entities)
	# print len(sorted_data_individuals)
	# print len(sorted_data_entities_only_descs)
	# print len(sorted_data_individuals_only_descs)
	# print len(outcomes_flat)

	# for row in sorted_data_individuals_only_descs:
	# 	print row
	# 	raw_input('$$$$')
	
	# print patterns[0][1]
	# raw_input('...')

	patterns_corresponding_support=[(compute_support_categorical(sorted_data_entities_only_descs,p[0]),compute_support_categorical(sorted_data_individuals_only_descs,p[1]),compute_support_categorical(sorted_data_individuals_only_descs,p[2])) for p in patterns]
	#print patterns_corresponding_support

	outcomes_processed,vector_of_action=outcome_representation_in_reviews([x.copy() for x in outcomes_flat],'outcome',None,method_aggregation_outcome)
	all_users_to_items_outcomes={}
	for row in outcomes_processed:
		i=row['idi']
		e=row['ide']
		if i not in all_users_to_items_outcomes:
			all_users_to_items_outcomes[i]={}
		all_users_to_items_outcomes[i][e]=row['outcome']

	min_quality_of_injected_patterns=1.
	patterns_to_ret=[]
	for p,sp in zip(patterns,patterns_corresponding_support):
		# print sp[0]
		# print p[1],sp[1]
		# print p[2],sp[2]
		# raw_input('****')
		all_votes_id=set(_['ide'] for _ in sorted_data_entities)
		outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)

		u_1_agg_votes=compute_aggregates_outcomes(all_votes_id,sp[1],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
		u_2_agg_votes=compute_aggregates_outcomes(all_votes_id,sp[2],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
		
		sim,nb=similarity_vector_measure_dcs(all_votes_id,u_1_agg_votes,u_2_agg_votes,'1','2',method='MAAD')
		sim_ref=sim/float(nb)  if nb >0. else float('NaN')
		sim,nb=similarity_vector_measure_dcs(sp[0],u_1_agg_votes,u_2_agg_votes,'1','2',method='MAAD')
		sim_context=sim/float(nb)  if nb >0. else float('NaN')
		quality=sim_ref-sim_context
		min_quality_of_injected_patterns=min(min_quality_of_injected_patterns,quality)
		print [sorted(p[0].values()),sorted(p[1].values()),sorted(p[2].values())],sim_ref,sim_context,quality
		patterns_to_ret.append({'context':p[0],'g_1':p[1],'g_2':p[2],'context_extent':[str(x) for x in sp[0]],'g_1_extent':[str(x) for x in sp[1]],'g_2_extent':[str(x) for x in sp[2]],'sim_ref':sim_ref,'sim_context':sim_context,'quality':quality})


	print 'min quality of best patterns observed is equal to : ', min_quality_of_injected_patterns
	#raw_input('....')
	#patterns_to_ret=[{'context':p[0],'g1':p[1],'g2':p[2],'context_extent':[str(x) for x in sp[0]],'g_1_extent':[str(x) for x in sp[1]],'g_2_extent':[str(x) for x in sp[2]]} for p,sp in zip(patterns,patterns_corresponding_support)]
	

	for row in outcomes_flat:
		row['idi']='id'+str(row['idi']).zfill(4)
		row['ide']='id'+str(row['ide']).zfill(4)
	for row in sorted_data_entities:
		row['ide']='id'+str(row['ide']).zfill(4)
	for row in sorted_data_individuals:
		row['idi']='id'+str(row['idi']).zfill(4)
	for row in patterns_to_ret:
		row['context_extent']=['id'+str(x).zfill(4) for x in row['context_extent']]
		row['g_1_extent']=['id'+str(x).zfill(4) for x in row['g_1_extent']]
		row['g_2_extent']=['id'+str(x).zfill(4) for x in row['g_2_extent']]


	return sorted_data_entities,sorted_data_individuals,outcomes_flat,patterns_to_ret,attributes_entities,attributes_individuals














# def generate_synthetic_GLUB_data_categorical_NEW(nb_attributes_entities=20
# 							,nb_max_items_entities=5 #domain size
# 							,nb_attributes_individuals=20
# 							,nb_max_items_individuals=5
# 							,nb_patterns=5
# 							,support_of_context_best_pattern=30
# 							,support_of_group_of_indiviudals=30
# 							,size_entities=1000
# 							,size_individuals=1000
# 							,noise_rate_add_subsuming_parents=0.1
# 							,noise_rate_negative_examples=0.1
# 							,sparsity_outcome=0.):
	
	
# 	sparsity_bar=1-sparsity_outcome
# 	possible_categorical_outcomes=['yes','no']
# 	method_aggregation_outcome='VECTOR_VALUES'
# 	looking_for_conflict=True

# 	attributes_entities=['CE'+str(x).zfill(4) for x in range(nb_attributes_entities)]
# 	attributes_individuals=['CI'+str(x).zfill(4)  for x in range(nb_attributes_individuals)]

# 	attributes_entities_domains={a:[a+'V'+str(i).zfill(4) for i in range(nb_max_items_entities)] for a in attributes_entities}
# 	attributes_individuals_domains={a:[a+'V'+str(i).zfill(4) for i in range(nb_max_items_individuals)] for a in attributes_individuals}


# 	patterns=[]
# 	patterns_sets=[]


	
# 	# print generated_context
# 	# print generate_random_object_with_categories(attributes_entities,attributes_entities_domains,generated_context)
# 	taboo_list_context=[]
# 	taboo_list_individuals=[]
# 	for _ in range(nb_patterns):
# 		#taboo_list_context=map(itemgetter(0),patterns)

# 		generated_context= generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(attributes_entities,attributes_entities_domains,taboo_list=taboo_list_context)
# 		taboo_list_context.append(generated_context)
# 		generated_g_1= generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,taboo_list=taboo_list_individuals)
# 		taboo_list_individuals.append(generated_g_1)
# 		generated_g_2= generate_random_non_empty_categorical_description_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,taboo_list=taboo_list_individuals)
# 		taboo_list_individuals.append(generated_g_2)
# 		patterns.append((generated_context,generated_g_1,generated_g_2))
# 		patterns_sets.append((set(generated_context.values()),set(generated_g_1.values()),set(generated_g_2.values())))
# 		print patterns[-1]

# 	id_entity=0
# 	id_individuals=0


# 	sorted_data_entities=[]
# 	sorted_data_entities_only_descs=[]
# 	sorted_data_individuals=[]
# 	sorted_data_individuals_only_descs=[]
# 	support_contexts=[]
# 	support_individuals_u_1=[]
# 	support_individuals_u_2=[]
# 	outcomes={}
# 	for index,row in enumerate(patterns):
# 		support_contexts.append([]);
# 		for _ in range(support_of_context_best_pattern):
# 			starting_description={}
# 			starting_description.update(row[0])
# 			#o=generate_random_object_with_categories(attributes_entities,attributes_entities_domains,starting_description)
# 			o=generate_random_object_with_categories_with_a_taboo_list_not_comparable(attributes_entities,attributes_entities_domains,starting_description,taboo_list=[p[0] for i,p in enumerate(patterns) if i!=index])
# 			# print sorted(row[0].values())
# 			# print sorted(o.values())
# 			# raw_input('....')
# 			o['ide']=id_entity
# 			sorted_data_entities.append(o)
# 			odesc={x:o[x] for x in o if x != 'ide'}
# 			sorted_data_entities_only_descs.append(odesc)
# 			support_contexts[-1].append(id_entity)
# 			id_entity+=1
# 		support_individuals_u_1.append([]);

# 		for _ in range(support_of_group_of_indiviudals):
# 			starting_description={}
# 			starting_description.update(row[1])
# 			#o=generate_random_object_with_categories(attributes_individuals,attributes_individuals_domains,starting_description)
# 			o=generate_random_object_with_categories_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=[p[1] for i,p in enumerate(patterns) if i!=index]+[p[2] for i,p in enumerate(patterns)])
# 			o['idi']=id_individuals
# 			sorted_data_individuals.append(o)
# 			odesc={x:o[x] for x in o if x != 'idi'}
# 			sorted_data_individuals_only_descs.append(odesc)
# 			support_individuals_u_1[-1].append(id_individuals)
# 			id_individuals+=1
# 		support_individuals_u_2.append([]);
# 		for _ in range(support_of_group_of_indiviudals):
# 			starting_description={}
# 			starting_description.update(row[2])
# 			#o=generate_random_object_with_categories(attributes_individuals,attributes_individuals_domains,starting_description)
# 			o=generate_random_object_with_categories_with_a_taboo_list_not_comparable(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=[p[1] for i,p in enumerate(patterns)]+[p[2] for i,p in enumerate(patterns) if i!=index])
# 			o['idi']=id_individuals
# 			sorted_data_individuals.append(o)
# 			odesc={x:o[x] for x in o if x != 'idi'}
# 			sorted_data_individuals_only_descs.append(odesc)
# 			support_individuals_u_2[-1].append(id_individuals)

# 			id_individuals+=1


# 	for index,row in enumerate(patterns):

		
# 		sup_context_actu=set(compute_support_categorical(sorted_data_entities_only_descs,row[0]))
# 		sup_g1_actu=set(compute_support_categorical(sorted_data_individuals_only_descs,row[1]))
# 		sup_g2_actu=set(compute_support_categorical(sorted_data_individuals_only_descs,row[2]))

# 		for entity_id in set(range(size_entities)):
# 			action=choice(range(2),1)[0]
# 			action_indiv_1=possible_categorical_outcomes[action]
# 			action_indiv_2=possible_categorical_outcomes[(1+action)%2]
# 			for indiv_1_id in sup_g1_actu:
# 				if indiv_1_id not in outcomes:
# 					outcomes[indiv_1_id]={}
# 				if random()<= sparsity_bar:
# 					outcomes[indiv_1_id][entity_id]=action_indiv_1	
# 			for indiv_2_id in sup_g2_actu:
# 				if indiv_2_id not in outcomes:
# 					outcomes[indiv_2_id]={}
# 				if random()<= sparsity_bar:
# 					if random()<=(1-noise_rate_negative_examples):
# 						if entity_id in sup_context_actu:
# 							outcomes[indiv_2_id][entity_id]=action_indiv_2
# 						else:
# 							outcomes[indiv_2_id][entity_id]=action_indiv_1
# 					else:
# 						outcomes[indiv_2_id][entity_id]=action_indiv_1
		
# 		#raw_input('...')
		
	
# 	remaining_entities=[]
# 	remaining_individuals=[]

	

# 	if False:
# 		now_entities=[]
# 		now_indiv_1=[]
# 		now_indiv_2=[]

# 		print 'BEFORE len(sorted_data_entities) : ',len(sorted_data_entities)
# 		print 'BEFORE len(sorted_data_individuals) : ',len(sorted_data_individuals)
# 		print 'adding_noise_parent_entities : ',int((size_entities-len(sorted_data_entities))*noise_rate_add_subsuming_parents)
# 		print 'adding_noise_parent_individuals : ',int(((size_individuals-len(sorted_data_individuals))*noise_rate_add_subsuming_parents)/2.)*2

# 		for _ in range(int((size_entities-len(sorted_data_entities))*noise_rate_add_subsuming_parents)):
			
# 			starting_description={}
# 			if True:
# 				starting_description=deepcopy(patterns[randint(0,len(patterns)-1)][0])
# 				for x in choice(sorted(starting_description.keys()),randint(1,len(starting_description)-1),replace=False).tolist():
# 					del starting_description[x]
# 			#o=generate_random_object_with_categories(attributes_entities,attributes_entities_domains,starting_description)
			
# 			#o=generate_random_object_with_categories_which_is_a_subsumption(attributes_entities,attributes_entities_domains,patterns[randint(0,len(patterns)-1)][0],taboo_list=map(itemgetter(0),patterns))
			
# 			# raw_input('...')

# 			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_entities_domains,starting_description,taboo_list=map(itemgetter(0),patterns))
			
# 			# print '------------------'
# 			# print sorted(patterns[0][0].values())
# 			# print sorted(o.values())
# 			# print '------------------'
# 			# raw_input('...')

# 			o['ide']=id_entity
# 			#remaining_entities.append(o)
# 			sorted_data_entities.append(o)
# 			odesc={x:o[x] for x in o if x != 'ide'}
# 			sorted_data_entities_only_descs.append(odesc)
# 			now_entities.append(id_entity)
# 			id_entity+=1

# 		for _ in range(int(((size_individuals-len(sorted_data_individuals))*noise_rate_add_subsuming_parents)/2.)):
			
# 			if True:
# 				starting_description=deepcopy(patterns[randint(0,len(patterns)-1)][1])
# 				for x in choice(sorted(starting_description.keys()),randint(1,len(starting_description)-1),replace=False).tolist():
# 					del starting_description[x]
# 			#o=generate_random_object_with_categories_which_is_a_subsumption(attributes_individuals,attributes_individuals_domains,patterns[randint(0,len(patterns)-1)][1],taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
# 			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
# 			o['idi']=id_individuals
# 			#remaining_individuals.append(o)
# 			sorted_data_individuals.append(o)
# 			odesc={x:o[x] for x in o if x != 'idi'}
# 			sorted_data_individuals_only_descs.append(odesc)
# 			now_indiv_1.append(id_individuals)
# 			id_individuals+=1
# 			#o=generate_random_object_with_categories_which_is_a_subsumption(attributes_individuals,attributes_individuals_domains,patterns[randint(0,len(patterns)-1)][2],taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
# 			if True:
# 				starting_description=deepcopy(patterns[randint(0,len(patterns)-1)][2])
# 				for x in choice(sorted(starting_description.keys()),randint(1,len(starting_description)-1),replace=False).tolist():
# 					del starting_description[x]
# 			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
			
# 			o['idi']=id_individuals
# 			#remaining_individuals.append(o)
# 			sorted_data_individuals.append(o)
# 			odesc={x:o[x] for x in o if x != 'idi'}
# 			sorted_data_individuals_only_descs.append(odesc)
# 			now_indiv_2.append(id_individuals)
# 			id_individuals+=1



# 		for e in range(0,size_entities):
# 			action=choice(possible_categorical_outcomes,1)[0]
# 			for i in now_indiv_1:
# 				if i not in outcomes:
# 					outcomes[i]={}
# 				if random()<= sparsity_bar:
# 					outcomes[i][e]=action
# 			for i in now_indiv_2:
# 				if i not in outcomes:
# 					outcomes[i]={}
# 				if random()<= sparsity_bar:
# 					outcomes[i][e]=action
		
# 		print 'AFTER len(sorted_data_entities) : ',len(sorted_data_entities)
# 		print 'AFTER len(sorted_data_individuals) : ',len(sorted_data_individuals)
# 		#raw_input('...')
# 			###########################################
# 			###########################################

# 		for _ in range(size_entities-len(sorted_data_entities)):
# 			starting_description={}
# 			#o=generate_random_object_with_categories(attributes_entities,attributes_entities_domains,starting_description)
# 			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_entities_domains,starting_description,taboo_list=map(itemgetter(0),patterns))
# 			o['ide']=id_entity
# 			remaining_entities.append(o)
# 			sorted_data_entities.append(remaining_entities[-1].copy())
# 			odesc={x:o[x] for x in o if x != 'ide'}
# 			sorted_data_entities_only_descs.append(odesc)
# 			id_entity+=1

		
# 		for _ in range(size_individuals-len(sorted_data_individuals)):
# 			starting_description={}
# 			#o=generate_random_object_with_categories(attributes_individuals,attributes_individuals_domains,starting_description)
# 			o=generate_random_object_with_categories_with_a_taboo_list_authorize_subsumption(attributes_individuals,attributes_individuals_domains,starting_description,taboo_list=map(itemgetter(1),patterns)+map(itemgetter(2),patterns))
# 			o['idi']=id_individuals
# 			remaining_individuals.append(o)
# 			sorted_data_individuals.append(remaining_individuals[-1].copy())
# 			odesc={x:o[x] for x in o if x != 'idi'}
# 			sorted_data_individuals_only_descs.append(odesc)
# 			id_individuals+=1

		


# 		for row in remaining_individuals:
# 			id_individual=row['idi']
# 			if id_individual not in outcomes:
# 				outcomes[id_individual]={}

# 			for e in range(0,size_entities):
# 				if random()<= sparsity_bar:
# 					outcomes[id_individual][e]=choice(possible_categorical_outcomes,1)[0]


# 	outcomes_flat=[ {'idi':i,'ide':e, 'outcome':outcomes[i][e]} for i in outcomes for e in outcomes[i]]
# 	# print outcomes_flat[0]
# 	# print len(sorted_data_entities)
# 	# print len(sorted_data_individuals)
# 	# print len(sorted_data_entities_only_descs)
# 	# print len(sorted_data_individuals_only_descs)
# 	# print len(outcomes_flat)

# 	# for row in sorted_data_individuals_only_descs:
# 	# 	print row
# 	# 	raw_input('$$$$')
	
# 	# print patterns[0][1]
# 	# raw_input('...')

# 	patterns_corresponding_support=[(compute_support_categorical(sorted_data_entities_only_descs,p[0]),compute_support_categorical(sorted_data_individuals_only_descs,p[1]),compute_support_categorical(sorted_data_individuals_only_descs,p[2])) for p in patterns]
# 	#print patterns_corresponding_support

# 	outcomes_processed,vector_of_action=outcome_representation_in_reviews([x.copy() for x in outcomes_flat],'outcome',None,method_aggregation_outcome)
# 	all_users_to_items_outcomes={}
# 	for row in outcomes_processed:
# 		i=row['idi']
# 		e=row['ide']
# 		if i not in all_users_to_items_outcomes:
# 			all_users_to_items_outcomes[i]={}
# 		all_users_to_items_outcomes[i][e]=row['outcome']

# 	min_quality_of_injected_patterns=1.
# 	patterns_to_ret=[]
# 	for p,sp in zip(patterns,patterns_corresponding_support):
# 		all_votes_id=set(_['ide'] for _ in sorted_data_entities)
# 		outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)

# 		u_1_agg_votes=compute_aggregates_outcomes(all_votes_id,sp[1],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
# 		u_2_agg_votes=compute_aggregates_outcomes(all_votes_id,sp[2],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
		
# 		sim,nb=similarity_vector_measure_dcs(all_votes_id,u_1_agg_votes,u_2_agg_votes,'1','2',method='MAAD')
# 		sim_ref=sim/float(nb)  if nb >0. else float('NaN')
# 		sim,nb=similarity_vector_measure_dcs(sp[0],u_1_agg_votes,u_2_agg_votes,'1','2',method='MAAD')
# 		sim_context=sim/float(nb)  if nb >0. else float('NaN')
# 		quality=sim_ref-sim_context
# 		min_quality_of_injected_patterns=min(min_quality_of_injected_patterns,quality)
# 		print [sorted(p[0].values()),sorted(p[1].values()),sorted(p[2].values())],sim_ref,sim_context,quality
# 		patterns_to_ret.append({'context':p[0],'g_1':p[1],'g_2':p[2],'context_extent':[str(x) for x in sp[0]],'g_1_extent':[str(x) for x in sp[1]],'g_2_extent':[str(x) for x in sp[2]],'sim_ref':sim_ref,'sim_context':sim_context,'quality':quality})
# 	print 'min quality of best patterns observed is equal to : ', min_quality_of_injected_patterns
# 	raw_input('....')
# 	return sorted_data_entities,sorted_data_individuals,outcomes_flat,patterns_to_ret,attributes_entities,attributes_individuals


def generate_synthetic_data(nb_attributes_entities=20
							,nb_max_items_entities=5
							,nb_attributes_individuals=20
							,nb_max_items_individuals=5
							,nb_patterns=5
							,support_of_context_best_pattern=30
							,support_of_group_of_indiviudals=30
							,size_entities=1000
							,size_individuals=1000
							,noise_rate_add_subsuming_parents=0.1
							,noise_rate_negative_examples=0.1
							,sparsity_outcome=0.):
	

	sparsity_bar=1-sparsity_outcome
	possible_categorical_outcomes=['yes','no']
	method_aggregation_outcome='VECTOR_VALUES'
	looking_for_conflict=True


	attributes_entities=['E'+str(x).zfill(4)+' '+'-' for x in range(nb_attributes_entities)]
	attributes_individuals=['I'+str(x).zfill(4)+' '+'-' for x in range(nb_attributes_individuals)]




	attributes_entities=['E'+str(x).zfill(4)+' '+'-' for x in range(nb_attributes_entities)]
	attributes_individuals=['I'+str(x).zfill(4)+' '+'-' for x in range(nb_attributes_individuals)]
	entities_dataset=[]
	
	taboo_list_individuals=[]
	taboo_list_entities=[]
	#################STEP 1 Generating Patterns###############################
	# patterns=[(generate_random_non_empty_itemset_with_min_and_max(attributes_entities,nb_min=2,nb_max=nb_max_items_entities),
	# 		generate_random_non_empty_itemset_with_min_and_max(attributes_individuals[:len(attributes_individuals)/2],nb_min=2,nb_max=nb_max_items_individuals),
	# 		generate_random_non_empty_itemset_with_min_and_max(attributes_individuals[len(attributes_individuals)/2:],nb_min=2,nb_max=nb_max_items_individuals)) for _ in range(nb_patterns)]
	patterns=[];
	patterns_sets=[]
	for _ in range(nb_patterns):
		context=generate_random_non_empty_itemset_with_min_and_max_with_a_taboo_list_not_comparable(attributes_entities,nb_min=2,nb_max=nb_max_items_entities,taboo_list=taboo_list_entities)
		taboo_list_entities.append(context)
		#g_1=generate_random_non_empty_itemset_with_min_and_max(attributes_individuals[:len(attributes_individuals)/2],nb_min=2,nb_max=nb_max_items_individuals)
		g_1=generate_random_non_empty_itemset_with_min_and_max_with_a_taboo_list_not_comparable(attributes_individuals,nb_min=2,nb_max=nb_max_items_individuals,taboo_list=taboo_list_individuals)
		taboo_list_individuals.append(g_1)
		#g_2=generate_random_non_empty_itemset_with_min_and_max(attributes_individuals[len(attributes_individuals)/2:],nb_min=2,nb_max=nb_max_items_individuals)
		g_2=generate_random_non_empty_itemset_with_min_and_max_with_a_taboo_list_not_comparable(attributes_individuals,nb_min=2,nb_max=nb_max_items_individuals,taboo_list=taboo_list_individuals)
		taboo_list_individuals.append(g_2)
		#taboo_list_individuals=[]
		patterns.append((context,g_1,g_2))
		patterns_sets.append((set(context),set(g_1),set(g_2)))
		print patterns[-1]

		#patterns.append((generate_random_non_empty_itemset_with_min_and_max_with_a_taboo_list_not_comparable(attributes_entities,nb_min=2,nb_max=nb_max_items_entities,taboo_list=[context]),g_1,g_2))
	# patterns=[(generate_random_non_empty_itemset_with_min_and_max(attributes_entities,nb_min=2,nb_max=nb_max_items_entities),
	# 		generate_random_non_empty_itemset_with_min_and_max(attributes_individuals,nb_min=2,nb_max=nb_max_items_individuals),
	# 		generate_random_non_empty_itemset_with_min_and_max(,nb_min=2,nb_max=nb_max_items_individuals)) for _ in range(nb_patterns)]
	
	patterns_corresponding_support=[]
	#########################################################################
	
	id_entity=0
	id_individuals=0
	support_contexts=[]
	support_individuals_u_1=[]
	support_individuals_u_2=[]

	sorted_data_entities=[]
	sorted_data_individuals=[]


	#################STEP 2 Generating Objects (Entities/Individuals Supporting the pattern###############################
	outcomes={}
	for index,row in enumerate(patterns):
		
		

		support_contexts.append([]);
		for _ in range(support_of_context_best_pattern):
			support_contexts[-1].append({'ide':id_entity,'descriptionEntity':row[0]})
			sorted_data_entities.append({'ide':id_entity,'descriptionEntity':row[0]})
			id_entity+=1
		support_individuals_u_1.append([]);
		for _ in range(support_of_group_of_indiviudals):
			support_individuals_u_1[-1].append({'idi':id_individuals,'descriptionIndividual':row[1]})
			sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':row[1]})
			id_individuals+=1
		support_individuals_u_2.append([]);
		for _ in range(support_of_group_of_indiviudals):
			support_individuals_u_2[-1].append({'idi':id_individuals,'descriptionIndividual':row[2]})
			sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':row[2]})
			id_individuals+=1

		patterns_corresponding_support.append((sorted({e['ide'] for e in support_contexts[-1]}),sorted({i['idi'] for i in support_individuals_u_1[-1]}),sorted({i['idi'] for i in support_individuals_u_2[-1]})))


	for index,row in enumerate(patterns):

		pat_context_set_actual=patterns_sets[index][0]
		pat_g_1_set_actual=patterns_sets[index][1]
		pat_g_2_set_actual=patterns_sets[index][2]

		sup_context_actual=support_contexts[index]
		sup_g_1_actual=[x['idi'] for x in support_individuals_u_1[index]]
		sup_g_2_actual=[x['idi'] for x in support_individuals_u_2[index]]


		context_subsumed_by_actual=[i for i,x in enumerate(patterns_sets) if pat_context_set_actual<=x[0]]

		g_1_subsumed_by_actual_g_1=[i for i,x in enumerate(patterns_sets) if pat_g_1_set_actual<=x[1]]
		g_2_subsumed_by_actual_g_1=[i for i,x in enumerate(patterns_sets) if pat_g_1_set_actual<=x[2]]
		
		g_1_subsumed_by_actual_g_2=[i for i,x in enumerate(patterns_sets) if pat_g_2_set_actual<=x[1]]
		g_2_subsumed_by_actual_g_2=[i for i,x in enumerate(patterns_sets) if pat_g_2_set_actual<=x[2]]

		#print index,context_subsumed_by_actual
		entity_to_be_in_discord_in=set.union(*[{x['ide'] for x in support_contexts[i]} for i in context_subsumed_by_actual])
		
		sup_g_1_actual_extended=set.union(*([set()]+[{x['idi'] for x in support_individuals_u_1[i]} for i in g_1_subsumed_by_actual_g_1]))|set.union(*([set()]+[{x['idi'] for x in support_individuals_u_2[i]} for i in g_2_subsumed_by_actual_g_1]))
		sup_g_2_actual_extended=set.union(*([set()]+[{x['idi'] for x in support_individuals_u_1[i]} for i in g_1_subsumed_by_actual_g_2]))|set.union(*([set()]+[{x['idi'] for x in support_individuals_u_2[i]} for i in g_2_subsumed_by_actual_g_2]))

		# print sup_g_1_actual,sup_g_1_actual_extended
		# print sup_g_2_actual,sup_g_2_actual_extended
		#print entity_to_be_in_discord_in
		####THIS WAS WORKING BEFORE##########
		# entity_to_be_in_discord_in=set(x['ide'] for x in sup_context_actual)
		# print entity_to_be_in_discord_in
		####THIS WAS WORKING BEFORE##########
		#raw_input('....')
		for entity_id in entity_to_be_in_discord_in:
			action=choice(range(2),1)[0]
			action_indiv_1=possible_categorical_outcomes[action]
			action_indiv_2=possible_categorical_outcomes[(1+action)%2]
			#print action_indiv_1,action_indiv_2
			for indiv_1_id in sup_g_1_actual_extended:
				#indiv_1_id=indiv_1['idi']
				if indiv_1_id not in outcomes:
					outcomes[indiv_1_id]={}
				if random()<= sparsity_bar:
					outcomes[indiv_1_id][entity_id]=action_indiv_1	

			for indiv_2_id in sup_g_2_actual_extended:
				#indiv_2_id=indiv_2['idi']
				if indiv_2_id not in outcomes:
					outcomes[indiv_2_id]={}
				if random()<= sparsity_bar:
					if random()<=(1-noise_rate_negative_examples):
						outcomes[indiv_2_id][entity_id]=action_indiv_2
					else:
						#outcomes[indiv_2_id][entity_id]=action_indiv_1
						outcomes[indiv_2_id][entity_id]=choice(possible_categorical_outcomes,1)[0]


			

		for entity_id in set(range(size_entities))-set(entity_to_be_in_discord_in):
			action=choice(range(2),1)[0]
			action_indiv_1=possible_categorical_outcomes[action]
			action_indiv_2=possible_categorical_outcomes[(1+action)%2]
			for indiv_1_id in sup_g_1_actual_extended:
				#indiv_1_id=indiv_1['idi']
				if indiv_1_id not in outcomes:
					outcomes[indiv_1_id]={}
				if random()<= sparsity_bar:
					outcomes[indiv_1_id][entity_id]=action_indiv_1	

			for indiv_2_id in sup_g_2_actual_extended:
				#indiv_2_id=indiv_2['idi']
				if indiv_2_id not in outcomes:
					outcomes[indiv_2_id]={}
				if random()<= sparsity_bar:
					outcomes[indiv_2_id][entity_id]=action_indiv_1
					# if random()<=(1-noise_rate_negative_examples):
					# 	outcomes[indiv_2_id][entity_id]=action_indiv_1
					# else:
					# 	outcomes[indiv_2_id][entity_id]=action_indiv_2

			
		#################STEP 2 Generating Objects (Entities/Individuals Supporting the pattern###############################
		

		####ADD SOME PARENT BAD PATTERNS#######
		if False:
			now_entities=[]
			now_indiv_1=[]
			now_indiv_2=[]
			
			for _ in range(30):
				subsuming_context,subsuming_g_1,subsuming_g_2=generate_random_subsuming_behavioral_patterns(*row)
				sorted_data_entities.append({'ide':id_entity,'descriptionEntity':subsuming_context})
				now_entities.append(id_entity)
				id_entity+=1
				sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_1})
				now_indiv_1.append(id_individuals)
				id_individuals+=1
				sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_2})
				now_indiv_2.append(id_individuals)
				id_individuals+=1
			for e in range(0,size_entities):
				action=choice(possible_categorical_outcomes,1)[0]
				for i in now_indiv_1:
					if i not in outcomes:
						outcomes[i]={}
					if random()<= sparsity_bar:
						outcomes[i][e]=action
				for i in now_indiv_2:
					if i not in outcomes:
						outcomes[i]={}
					if random()<= sparsity_bar:
						outcomes[i][e]=action
		

		###########


	####ADD SOME PARENT BAD PATTERNS#######


	if False:
		now_entities=[]
		now_indiv_1=[]
		now_indiv_2=[]
		#raw_input('....')
		for _ in range(200):

			subsuming_context,subsuming_g_1,subsuming_g_2=generate_random_subsuming_behavioral_patterns_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_individuals,nb_max_items_entities,nb_max_items_individuals,patterns)
			# print subsuming_context,subsuming_g_1,subsuming_g_2
			# raw_input('yyy')
			sorted_data_entities.append({'ide':id_entity,'descriptionEntity':subsuming_context})
			now_entities.append(id_entity)
			id_entity+=1
			sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_1})
			now_indiv_1.append(id_individuals)
			id_individuals+=1
			sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_2})
			now_indiv_2.append(id_individuals)
			id_individuals+=1
		for e in range(0,size_entities):
			action=choice(possible_categorical_outcomes,1)[0]
			for i in now_indiv_1:
				if i not in outcomes:
					outcomes[i]={}
				if random()<= sparsity_bar:
					outcomes[i][e]=action
			for i in now_indiv_2:
				if i not in outcomes:
					outcomes[i]={}
				if random()<= sparsity_bar:
					outcomes[i][e]=action



	####ADD SOME PARENT BAD PATTERNS#######



	#support_contexts=[[{'ide':k,'description':row[0]} for _ in range(support_of_context_best_pattern)] for row in patterns]
	#support_individuals_u_1=[[{'description':row[1]} for _ in range(support_of_group_of_indiviudals)] for row in patterns]
	#support_individuals_u_2=[[{'description':row[2]} for _ in range(support_of_group_of_indiviudals)] for row in patterns]
	
	if True:


		now_entities=[]
		now_indiv_1=[]
		now_indiv_2=[]
		# ret_c=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_entities,nb_max=nb_max_items_entities,taboo_list=[x[0] for x in patterns]))
		# ret_g_1=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[x[1] for x in patterns]+[x[2] for x in patterns]))
		# ret_g_2=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[x[1] for x in patterns]+[x[2] for x in patterns]))
		
		print 'BEFORE len(sorted_data_entities) : ',len(sorted_data_entities)
		print 'BEFORE len(sorted_data_individuals) : ',len(sorted_data_individuals)
		print 'adding_noise_parent_entities : ',int((size_entities-len(sorted_data_entities))*noise_rate_add_subsuming_parents)
		print 'adding_noise_parent_individuals : ',int(((size_individuals-len(sorted_data_individuals))*noise_rate_add_subsuming_parents)/2.)*2
		
		for _ in range(int((size_entities-len(sorted_data_entities))*noise_rate_add_subsuming_parents)):
			subsuming_context=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_entities,nb_max=nb_max_items_entities,taboo_list=[x[0] for x in patterns]))
			sorted_data_entities.append({'ide':id_entity,'descriptionEntity':subsuming_context})
			now_entities.append(id_entity)
			id_entity+=1

		for _ in range(int(((size_individuals-len(sorted_data_individuals))*noise_rate_add_subsuming_parents)/2.)):
			subsuming_g_1=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[x[1] for x in patterns]+[x[2] for x in patterns]))
			sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_1})
			now_indiv_1.append(id_individuals)
			id_individuals+=1
			subsuming_g_2=sorted(generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[x[1] for x in patterns]+[x[2] for x in patterns]))
			sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_2})
			now_indiv_2.append(id_individuals)
			id_individuals+=1

		for e in range(0,size_entities):
			action=choice(possible_categorical_outcomes,1)[0]
			for i in now_indiv_1:
				if i not in outcomes:
					outcomes[i]={}
				if random()<= sparsity_bar:
					outcomes[i][e]=action
			for i in now_indiv_2:
				if i not in outcomes:
					outcomes[i]={}
				if random()<= sparsity_bar:
					outcomes[i][e]=action

		print 'AFTER len(sorted_data_entities) : ',len(sorted_data_entities)
		print 'AFTER len(sorted_data_individuals) : ',len(sorted_data_individuals)
		# now_entities=[]
		# now_indiv_1=[]
		# now_indiv_2=[]
		# #raw_input('....')
		# for _ in range(noise_rate_add_subsuming_parents):
		# 	subsuming_context,subsuming_g_1,subsuming_g_2=generate_random_subsuming_behavioral_patterns_with_a_taboo_list_authorize_subsumption(attributes_entities,attributes_individuals,nb_max_items_entities,nb_max_items_individuals,patterns)
		# 	# print subsuming_context,subsuming_g_1,subsuming_g_2
		# 	# raw_input('yyy')
		# 	sorted_data_entities.append({'ide':id_entity,'descriptionEntity':subsuming_context})
		# 	now_entities.append(id_entity)
		# 	id_entity+=1
		# 	sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_1})
		# 	now_indiv_1.append(id_individuals)
		# 	id_individuals+=1
		# 	sorted_data_individuals.append({'idi':id_individuals,'descriptionIndividual':subsuming_g_2})
		# 	now_indiv_2.append(id_individuals)
		# 	id_individuals+=1
		# for e in range(0,size_entities):
		# 	action=choice(possible_categorical_outcomes,1)[0]
		# 	for i in now_indiv_1:
		# 		if i not in outcomes:
		# 			outcomes[i]={}
		# 		if random()<= sparsity_bar:
		# 			outcomes[i][e]=action
		# 	for i in now_indiv_2:
		# 		if i not in outcomes:
		# 			outcomes[i]={}
		# 		if random()<= sparsity_bar:
		# 			outcomes[i][e]=action
		
		



		remaining_entities=[]
		remaining_individuals=[]

		for _ in range(size_entities-len(sorted_data_entities)):
			#remaining_entities.append({'ide':id_entity,'descriptionEntity':generate_random_non_empty_itemset_with_max(sorted(set(attributes_entities)-set(patterns[0][0])),nb_max=nb_max_items_entities)})
			remaining_entities.append({'ide':id_entity,'descriptionEntity':generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_entities,nb_max=nb_max_items_entities,taboo_list=[p[0] for p in patterns])})
			sorted_data_entities.append(remaining_entities[-1].copy())
			id_entity+=1

		
		for _ in range(size_individuals-len(sorted_data_individuals)):
			remaining_individuals.append({'idi':id_individuals,'descriptionIndividual':generate_random_non_empty_itemset_with_max_with_a_taboo_list_authorize_subsumption(attributes_individuals,nb_max=nb_max_items_individuals,taboo_list=[p[1] for p in patterns]+[p[2] for p in patterns])})
			sorted_data_individuals.append(remaining_individuals[-1].copy())
			id_individuals+=1

		


		for row in remaining_individuals:
			id_individual=row['idi']
			if id_individual not in outcomes:
				outcomes[id_individual]={}

			for e in range(0,size_entities):
				if random()<= sparsity_bar:
					outcomes[id_individual][e]=choice(possible_categorical_outcomes,1)[0]



	


	# for row in patterns:
	# 	print row
		
	# #print patterns
	# raw_input('...')


	# for _ in range(size_entities):
	# 	item=generate_random_non_empty_itemset_with_max(attributes_entities,nb_max=nb_max_items_entities)
	# 	entities_dataset.append({'description':item})




	# # for row in entities_dataset:
	# # 	print row
	# # 	raw_input('...')
	# enumerator_contexts=enumerator_complex_cbo_init_new_config(entities_dataset, [{'name':'description', 'type':'themes'}],threshold=5)
	# # for  e_p,e_label,e_config in enumerator_contexts:
	# # 	print e_p,len(e_config['support'])
	# #print e_config['nb_visited']
	
	outcomes_flat=[ {'idi':i,'ide':e, 'outcome':outcomes[i][e]} for i in outcomes for e in outcomes[i]]
	print outcomes_flat[0]
	print len(sorted_data_entities)
	print len(sorted_data_individuals)
	print len(outcomes_flat)
	#raw_input('....')

	
	sorted_data_entities_only_descs=[set(x['descriptionEntity']) for x in sorted_data_entities]
	sorted_data_individuals_only_descs=[set(x['descriptionIndividual']) for x in sorted_data_individuals]
	
	patterns_corresponding_support=[(compute_support(sorted_data_entities_only_descs,p[0]),compute_support(sorted_data_individuals_only_descs,p[1]),compute_support(sorted_data_individuals_only_descs,p[2])) for p in patterns]
	

	outcomes_processed,vector_of_action=outcome_representation_in_reviews([x.copy() for x in outcomes_flat],'outcome',None,method_aggregation_outcome)
	all_users_to_items_outcomes={}
	for row in outcomes_processed:
		i=row['idi']
		e=row['ide']
		if i not in all_users_to_items_outcomes:
			all_users_to_items_outcomes[i]={}
		all_users_to_items_outcomes[i][e]=row['outcome']

	min_quality_of_injected_patterns=1.
	patterns_to_ret=[]
	for p,sp in zip(patterns,patterns_corresponding_support):
		all_votes_id=set(_['ide'] for _ in sorted_data_entities)
		outcome_tuple_structure=get_tuple_structure(all_users_to_items_outcomes)

		u_1_agg_votes=compute_aggregates_outcomes(all_votes_id,sp[1],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
		u_2_agg_votes=compute_aggregates_outcomes(all_votes_id,sp[2],all_users_to_items_outcomes,outcome_tuple_structure,method_aggregation_outcome=method_aggregation_outcome)
		
		sim,nb=similarity_vector_measure_dcs(all_votes_id,u_1_agg_votes,u_2_agg_votes,'1','2',method='MAAD')
		sim_ref=sim/float(nb)  if nb >0. else float('NaN')
		sim,nb=similarity_vector_measure_dcs(sp[0],u_1_agg_votes,u_2_agg_votes,'1','2',method='MAAD')
		sim_context=sim/float(nb)  if nb >0. else float('NaN')
		quality=sim_ref-sim_context
		min_quality_of_injected_patterns=min(min_quality_of_injected_patterns,quality)
		print p,sim_ref,sim_context,quality
		##########################OBVIOUSLY##########################
		if quality>0.75:
			 patterns_to_ret.append({'context':p[0],'g_1':p[1],'g_2':p[2],'context_extent':[str(x) for x in sp[0]],'g_1_extent':[str(x) for x in sp[1]],'g_2_extent':[str(x) for x in sp[2]],'sim_ref':sim_ref,'sim_context':sim_context,'quality':quality})
		##########################OBVIOUSLY##########################
		
	print 'min quality of best patterns observed is equal to : ', min_quality_of_injected_patterns
		 
		
		#raw_input('*********')
		
	# for p,sp in zip(patterns,patterns_corresponding_support):
	# 	print p[0],compute_support(sorted_data_entities_only_descs,p[0]),sp[0]
	# 	raw_input('y')


	#patterns_to_ret=[{'context':p[0],'g1':p[1],'g2':p[2],'context_extent':[str(x) for x in sp[0]],'g_1_extent':[str(x) for x in sp[1]],'g_2_extent':[str(x) for x in sp[2]]} for p,sp in zip(patterns,patterns_corresponding_support)]
	for row in patterns_to_ret:
		print row['context_extent'],row['g_1_extent'],row['g_2_extent']
	#print outcomes_flat[0]
	
	return sorted_data_entities,sorted_data_individuals,outcomes_flat,patterns_to_ret




def jaccard(s1,s2):
	return float(len(s1&s2))/len(s1|s2)


def cover(s1,s2): #how much s1 cover s2

	return float(len(s1&s2))/len(s2)


def jaccard_patterns(p1,p2):
	return jaccard(p1[0],p2[0])*(1/2.)*max(jaccard(p1[1],p2[1])+jaccard(p1[2],p2[2]),jaccard(p1[1],p2[2])+jaccard(p1[2],p2[1]))

def cover_patterns(p1,p2):
	return cover(p1[0],p2[0])*(1/2.)*max(cover(p1[1],p2[1])+cover(p1[2],p2[2]),cover(p1[1],p2[2])+cover(p1[2],p2[1]))	

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

def similarity_between_patterns_set_recall(patterns_set,ground_truth_set):
	

	if len(patterns_set)==0 or len(ground_truth_set)==0:
		return 0.
	
	returned_1=0.
	for extent2 in ground_truth_set:
		returned_1+=mymax(jaccard_patterns(extent1,extent2) for extent1 in patterns_set)
	recall=returned_1/len(ground_truth_set)

	return recall

def recall_pattern_by_pattern(patterns_set,ground_truth_set):
	recalls=[]
	if len(patterns_set)==0 or len(ground_truth_set)==0:
		return 0.
	
	returned_1=0.
	for extent2 in ground_truth_set:
		#print extent2
		#print patterns_set
		recalls.append(mymax(jaccard_patterns(extent1,extent2) for extent1 in patterns_set))
		returned_1+=mymax(jaccard_patterns(extent1,extent2) for extent1 in patterns_set)
	recall=returned_1/len(ground_truth_set)

	return recalls

def similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set,ground_truth_set):
	

	if len(patterns_set)==0 or len(ground_truth_set)==0:
		return 0.,0.
	
	returned_1=0.
	for extent2 in ground_truth_set:
		returned_1+=mymax(jaccard_patterns(extent1,extent2) for extent1 in patterns_set)
	recall=returned_1/len(ground_truth_set)

	returned_1=0.
	for extent2 in patterns_set:
		returned_1+=mymax(jaccard_patterns(extent1,extent2) for extent1 in ground_truth_set)
	precision=returned_1/len(patterns_set)

	return precision,recall



def similarity_between_descs_ML_MARC(pdesc,phidden):
	set_pdesc=set(pdesc)
	set_phidden=set(phidden)
	ret_denominator=len(set_pdesc&set_phidden)
	return len(set_pdesc&set_phidden)/float((float(len(set_phidden))+2*(len(set_pdesc-set_phidden))))


def similarity_between_patterns_ML_MARC(pdesc,phidden):
	return similarity_between_descs_ML_MARC(pdesc[0],phidden[0])*(1/2.)*max(similarity_between_descs_ML_MARC(pdesc[1],phidden[1])+similarity_between_descs_ML_MARC(pdesc[2],phidden[2]),similarity_between_descs_ML_MARC(pdesc[1],phidden[2])+similarity_between_descs_ML_MARC(pdesc[2],phidden[1]))



def similarity_between_descs_with_subsumption(pdesc,phidden):
	set_pdesc=set(pdesc)
	set_phidden=set(phidden)
	return len(set_pdesc&set_phidden)/float((float(len(pdesc))))

def similarity_between_patterns_with_subsumption(pdesc,phidden):
	return similarity_between_descs_with_subsumption(pdesc[0],phidden[0])*(1/2.)*max(similarity_between_descs_with_subsumption(pdesc[1],phidden[1])+similarity_between_descs_with_subsumption(pdesc[2],phidden[2]),similarity_between_descs_with_subsumption(pdesc[1],phidden[2])+similarity_between_descs_with_subsumption(pdesc[2],phidden[1]))



def similarity_between_patterns_set_recall_precision_with_cover(patterns_set,ground_truth_set):
	

	if len(patterns_set)==0 or len(ground_truth_set)==0:
		return 0.,0.
	
	returned_1=0.
	for extent2 in ground_truth_set:
		cover_max=mymax(cover_patterns(extent1,extent2) for extent1 in patterns_set)
		jacc_max=mymax(jaccard_patterns(extent1,extent2) for extent1 in patterns_set)
		#print cover_max,jacc_max
		returned_1+=cover_max
	recall=returned_1/len(ground_truth_set)

	returned_1=0.
	for extent2 in patterns_set:
		cover_max=mymax(cover_patterns(extent1,extent2) for extent1 in ground_truth_set)
		jacc_max=mymax(jacc_max(extent1,extent2) for extent1 in ground_truth_set)
		#print cover_max,jacc_max
		returned_1+=mymax(cover_patterns(extent1,extent2) for extent1 in ground_truth_set)
	precision=returned_1/len(patterns_set)

	return precision,recall




def similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns,ground_truth):
	if len(patterns)==0 or len(ground_truth)==0:
		return 0.

	ret=0.
	for phidden in ground_truth:
		
		ret+=mymax(similarity_between_patterns_ML_MARC(pdesc,phidden) for pdesc in patterns)
	return ret/float(len(ground_truth))

def similarity_between_patterns_groups_with_subsumption(patterns,ground_truth):
	if len(patterns)==0 or len(ground_truth)==0:
		return 0.

	ret=0.
	for phidden in ground_truth:
		
		ret+=mymax(similarity_between_patterns_with_subsumption(pdesc,phidden) for pdesc in patterns)
	return ret/float(len(ground_truth))



if __name__ == '__main__':


	parser = argparse.ArgumentParser(description='PROCESS')
	parser.add_argument('-T','--Transform',metavar='transform',nargs='*',help='Transform a behavioral dataset to confronting individuals in all contexts.')
	parser.add_argument('-G','--GenerateSynthetic',metavar='generatesynthetic',nargs='*',help='generate Synthetic Data')
	parser.add_argument('-C','--GenerateSyntheticCategorical',metavar='generatesyntheticcategorical',nargs='*',help='generate Synthetic Data')

	parser.add_argument('--sparsity',metavar='sparsity',nargs='*',help='sparisity value')

	parser.add_argument('-E','--EvaluatePerformance',metavar='evaluateperformance',nargs='*',help="Evaluate performance precision/recall of DSC over synthetic Data.")
	parser.add_argument('-P','--Product',metavar='carteisanproduct',nargs='*',help='Transform a behavioral dataset to a labeled cartesian product dataset.')
	parser.add_argument('-M','--Majority',metavar='majority',nargs='*',help='Transform a behavioral dataset to confronting individuals in all contexts.')


	parser.add_argument('--Compare',metavar='compare',nargs='*',help='Launch Comparative Experiments with State-Of-The-Art Algorithms.')

	args=parser.parse_args()

	#print args
	#raw_input('....')
	Command="Transform" #Transform a behavioral dataset to confronting individuals in all contexts.
	Command="GenerateSynthetic" #generate Synthetic Data
	Command="EvaluatePerformance"
	Command="Product"
	Command="TransformMajority"
	Command="ForCosmic"



	# print generate_random_non_empty_itemset_with_max(['a','b','c'],2)
	# raw_input('.....')




	if type(args.Product) is list:
		print "Transform a behavioral dataset to a labeled Caretsian Product E x U x U"

		
		itemsFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_Sparisity_0_5_mn_sampling\GENERATED_0001\items_0001.csv"
		usersFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_Sparisity_0_5_mn_sampling\GENERATED_0001\individuals_0001.csv"
		reviewsFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_Sparisity_0_5_mn_sampling\GENERATED_0001\outcomes_0001.csv"
		numeric_attrs=[]
		array_attrs=['PROCEDURE_SUBJECT']
		outcome_attrs=None
		method_aggregation_outcome="SYMBOLIC_MAJORITY"
		itemsScope=[]
		users_1_Scope=[]
		users_2_Scope=[]
		nb_items=float('inf')
		nb_individuals=float('inf')
		attributes_to_consider=["PROCEDURE_SUBJECT"]
		create_boolean_attributes_for_hmt=True
		nb_items_entities=float('inf')
		nb_items_individuals=float('inf')
		hmt_to_itemset=True
		delimiter="\t"


		new_behavioral_dataset,header=create_behavioral_cartesian_dataset(
			itemsFile,
			usersFile,
			reviewsFile,
			numeric_attrs=numeric_attrs,
			array_attrs=array_attrs,
			outcome_attrs=outcome_attrs,
			method_aggregation_outcome=method_aggregation_outcome,
			itemsScope=itemsScope,
			users_1_Scope=users_1_Scope,
			users_2_Scope=users_2_Scope,
			nb_items=nb_items,
			nb_individuals=nb_individuals,
			attributes_to_consider=attributes_to_consider,
			nb_items_entities=nb_items_entities,
			nb_items_individuals=nb_items_individuals,
			hmt_to_itemset=hmt_to_itemset,
			create_boolean_attributes_for_hmt=create_boolean_attributes_for_hmt,
			delimiter=delimiter)
		writeCSVwithHeader(new_behavioral_dataset,'TEST.csv',selectedHeader=header,delimiter='\t',flagWriteHeader=True)

	if type(args.Compare) is list:
		# print 'HELLO ! '
		# raw_input('........................')
		method_recall_patterns_avg={}
		method_fscore_patterns={}

		if False:
			print "For comparative Study Figures !"
			method_recall_patterns_avg={}
			method_fscore_patterns={}




			iworkingrepo=0
			for vno,vsp,nb_individuals,nb_entities in product([0.,0.2,0.4],[0.,0.25,0.5],[100,125,150],[100,150,200]):
				# if vno!=0 or vsp!=0. or nb_individuals!=100:
				# 	continue
				iworkingrepo+=1

				parameters={
						'nb_attributes_entities':2,
						'nb_max_items_entities':4,
						'nb_attributes_individuals':2,
						'nb_max_items_individuals':4,
						'nb_patterns':3,
						'support_of_context_best_pattern':5,#20 high sparsity
						'support_of_group_of_indiviudals':5,#20 high sparsity
						'size_entities':nb_entities,
						'size_individuals':nb_individuals,
						'noise_rate_add_subsuming_parents':1.,
						'noise_rate_negative_examples':vno,
						'sparsity_outcome':vsp,
						'noise_for_both_groups':False,
						'dataset_size':0,
				}

				working_repo='.//ComparingWithExistingAlgorithms'+'//ComparingWithExistingAlgorithms'+str(iworkingrepo).zfill(3)
				
				# if False:
				# 	new_behavioral_dataset,hhhh=readCSVwithHeader(working_repo+'//TEST_COSMIC.csv',delimiter=';') 
				# 	method_recall_patterns={}
				# 	method_fscore_patterns={}
				# 	print 'COSMIC -REUPDATE-'
				# 	itemsFile=working_repo+"//items_synth.csv"
				# 	usersFile=working_repo+"//users_synth.csv"
				# 	reviewsFile=working_repo+"//reviews_synth.csv"
				# 	items,h_items=readCSVwithHeader(itemsFile,delimiter='\t')
				# 	users,h_users=readCSVwithHeader(usersFile,delimiter='\t')
				# 	parametersFile=[
				# 		['minWeight:2'],
				# 		['minWraccPerEdge:200.'],
				# 		['usedModel:config'],
				# 		['inputFilePath:'+working_repo+'//TEST_COSMIC.csv'],
				# 		['outputFolderPath:'+working_repo+'//results'],#.//ComparingWithExistingAlgorithms//results'],
				# 		['postProcessing:jaccardSummary'],
				# 		['redundancyThreshold:0.01'],
				# 		['minVertexSize:8'],
				# 		['minEdgeSize:10'],
				# 		['minWracc:5.'],
				# 		['minLift:5.'],
				# 		['measure:lift']
				# 	]
				# 	writeCSV(parametersFile,'.//parametersFile.txt')


				# 	print " ".join(['java', '-jar','.//Cosmic.jar','.//parametersFile.txt'])
				# 	tstart=time.time()
				# 	call(['java', '-jar','.//Cosmic.jar','.//parametersFile.txt'])
				# 	#raw_input('*************************')

				# 	res=readJSON_stringifyUnicodes(working_repo+'//results//results.json')
				# 	exceptionalSubgraphs=res['exceptionalSubgraphs']
				# 	to_write=[]
				# 	for eg in exceptionalSubgraphs:
				# 		full_desc={str(x):str(y) for x,y in eg['context'].iteritems()}
				# 		context_desc={x:full_desc[x] for x in full_desc if 'CE' in x}
				# 		context_desc={x:full_desc[x] for x in context_desc if full_desc[x]!='*'}
				# 		#print compute_support_categorical(items,context_desc)
				# 		g_1_desc={x.split('_')[0]:full_desc[x] for x in full_desc if 'CI' in x and '_1' in x and full_desc[x]!='*'}
				# 		g_2_desc={x.split('_')[0]:full_desc[x] for x in full_desc if 'CI' in x and '_2' in x and full_desc[x]!='*'}
				# 		#print context_desc,g_1_desc,g_2_desc
				# 		sup_context=[items[i][h_items[0]] for i in compute_support_categorical(items,context_desc)]
				# 		sup_g1=[users[i][h_users[0]] for i in compute_support_categorical(users,g_1_desc)]
				# 		sup_g2=[users[i][h_users[0]] for i in compute_support_categorical(users,g_2_desc)]
				# 		#print len(sup_context),len(sup_g1),len(sup_g2)
				# 		record={
				# 			'context':context_desc,
				# 			'g_1':g_1_desc,
				# 			'g_2':g_2_desc,
				# 			'context_extent':sup_context,
				# 			'g_1_extent':sup_g1,
				# 			'g_2_extent':sup_g2,
				# 			'sim_ref':0.,
				# 			'sim_context':0.,
				# 			'quality':eg['wRAccSum']
				# 		}
				# 		to_write.append(record)
				# 		#raw_input('ss')
				# 	#raw_input('...')
				# 	writeCSVwithHeader(to_write,working_repo+'//patterns_cosmic_synth_extent.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				# 	timespent=time.time()-tstart



				# 	patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
				# 	patterns_set_results_file=working_repo+"//patterns_cosmic_synth_extent.csv"
				# 	patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
				# 	patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					
				# 	# for row in patterns_set_ground_truth:
				# 	# 	print row['context_extent'],row['g_1_extent'],row['g_2_extent']
				# 	# for row in patterns_set_results:
				# 	# 	print row['context_extent'],row['g_1_extent'],row['g_2_extent']

				# 	patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
				# 	patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
				# 	print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
				# 	print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
				# 	method_recall_patterns['SD-COSMIC']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
				# 	print method_recall_patterns
				# 	results_evaluation={}
				# 	results_evaluation.update(parameters)
				# 	results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
				# 	try:
				# 		results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
				# 	except Exception as xxx:
				# 		results_evaluation['fscore_jaccard']=0.
				# 	results_evaluation['algorithm']='SD-COSMIC*'
				# 	results_evaluation['nb_pattern_returned']=len(patterns_set_results)
				# 	results_evaluation['pattern_by_pattern_recall']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
				# 	results_evaluation['timespent']=timespent
				# 	results_evaluation['dataset_size']=len(new_behavioral_dataset)
				# 	writeCSVwithHeader([results_evaluation],working_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','nb_pattern_returned','pattern_by_pattern_recall','timespent','dataset_size'],delimiter='\t',flagWriteHeader=False)
					
				# 	print 'COSMIC -REUPDATE- Finished'
					














				if False:


					IGNORE=[]#IGNORE=['SD-COSMIC']
					MAPS={'SD-COSMIC*':'COSMIC','SD-COSMIC':'COSMIC'}
					MAPS_FILES_NAMES={
						"Quick-DEBuNk":'results_synthetic_sampling_synth_EXTENTS.csv',
						"DEBuNk": 'results_synthetic_synth_EXTENTS.csv',
						"SD-Majority": 'patterns_extents_synth_subgroup_majority.csv',
						"SD-Cartesian": 'patterns_extents_synth_subgroup_cartesian.csv',
						"COSMIC": 'patterns_cosmic_synth_extent.csv'

					}
					evalres,h=readCSVwithHeader(working_repo+'//evaluation_results.csv',numberHeader=['noise_rate_negative_examples','fscore_jaccard','sparsity_outcome'],arrayHeader=['pattern_by_pattern_recall'],delimiter='\t')
					method_recall_patterns={}
					
					if evalres[0]['noise_rate_negative_examples']!=0. or evalres[0]['sparsity_outcome']!=0.:
						continue
					for row in evalres: 
						names_to_consider=MAPS.get(row['algorithm'],row['algorithm'])
						if row['algorithm'] in IGNORE:
							continue
						method_recall_patterns[names_to_consider]=row['pattern_by_pattern_recall']
						if names_to_consider not in method_fscore_patterns:
							method_fscore_patterns[names_to_consider]=[]
						
						
						recheck_data=True
						if recheck_data:
							patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
							patterns_set_results_file=working_repo+"//"+MAPS_FILES_NAMES[names_to_consider]
							patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=['quality'],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','quality'],delimiter='\t')
							patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=['quality'],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent','quality'],delimiter='\t')
							
							patterns_set_results=sorted(patterns_set_results,key=lambda rec:rec['quality'],reverse=True)[:10]


							patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
							patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
							
							

							precision_jaccard,recall_jaccard=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
							
							try:
								new_fscore=2*(precision_jaccard*recall_jaccard)/(precision_jaccard+recall_jaccard)
							except:
								new_fscore=0.

							method_fscore_patterns[names_to_consider].append(new_fscore)
							print len(patterns_set_results),new_fscore,len(patterns_set_results)
						else:
							method_fscore_patterns[names_to_consider].append(row['fscore_jaccard'])

						#print method_fscore_patterns

					print method_recall_patterns
					try:
						if False:
							from plotter.perfPlotter import plot_radar_chart,plot_boxplot_chart
							plot_radar_chart(working_repo,method_recall_patterns)
						
					except Exception as e:
						raise e
						continue
					
					
					for m,v in method_recall_patterns.iteritems():
						if m not in method_recall_patterns_avg:
							method_recall_patterns_avg[m]=[]
						method_recall_patterns_avg[m].append(v)
			#raw_input('$$$$$$$')
			for m in method_recall_patterns_avg:
				varr=method_recall_patterns_avg[m]
				varr=[x for x in varr if type(x) is list]
				varr_avg=[map(itemgetter(x),varr)  for x in range(len(varr[0]))]
				varr_avg=[sum(x)/float(len(x)) for x in varr_avg]
				#print varr_avg
				method_recall_patterns_avg[m]=varr_avg
			print method_recall_patterns_avg
			from plotter.perfPlotter import plot_radar_chart,plot_boxplot_chart
			for algo in method_fscore_patterns:
				print algo,method_fscore_patterns[algo]
			plot_radar_chart('.//ComparingWithExistingAlgorithms',method_recall_patterns_avg)
			plot_boxplot_chart('.//ComparingWithExistingAlgorithms',method_fscore_patterns)
				#raw_input('...')
			# raw_input('....')
			# raw_input('....')
		
		if True:
			iworkingrepo=0
			print 'Comparative study. All results are in the ComparingWithExistingAlgorithms in the same repo where experiments are launched'
			
			#for nb_entities,nb_individuals,vsp,vno in product([100,100,100,100,100],[100],[0.],[0.]):#[100,150,200,250],[60,80,120,160],[0.,0.25,0.33,0.5],[0.,0.2,0.4,0.5]
			for vno,vsp,nb_individuals,nb_entities in product([0.,0.2,0.4],[0.,0.25,0.5],[100,125,150],[100,150,200]):#
				Evaluation_results_new=True
				iworkingrepo+=1
				working_repo='.//ComparingWithExistingAlgorithms'
				
				results_evaluation={} 
				if not os.path.exists(working_repo):
					os.makedirs(working_repo)
				else:
					if False:
						shutil.rmtree(working_repo)
						os.makedirs(working_repo)

				working_repo=working_repo+'//ComparingWithExistingAlgorithms'+str(iworkingrepo).zfill(3)
				if not os.path.exists(working_repo):
					os.makedirs(working_repo)
				else:
					shutil.rmtree(working_repo)
					os.makedirs(working_repo)

				itemsFile=working_repo+"//items_synth.csv"
				usersFile=working_repo+"//users_synth.csv"
				reviewsFile=working_repo+"//reviews_synth.csv"
				# itemsFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_Sparisity_0_5_mn_sampling\GENERATED_0001\items_0001.csv"
				# usersFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_Sparisity_0_5_mn_sampling\GENERATED_0001\individuals_0001.csv"
				# reviewsFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_Sparisity_0_5_mn_sampling\GENERATED_0001\outcomes_0001.csv"
				method_recall_patterns={}
				if True:
					
					
					parameters={
						'nb_attributes_entities':2,
						'nb_max_items_entities':4,
						'nb_attributes_individuals':2,
						'nb_max_items_individuals':4,
						'nb_patterns':3,
						'support_of_context_best_pattern':5,#20 high sparsity
						'support_of_group_of_indiviudals':5,#20 high sparsity
						'size_entities':nb_entities,
						'size_individuals':nb_individuals,
						'noise_rate_add_subsuming_parents':1.,
						'noise_rate_negative_examples':vno,
						'sparsity_outcome':vsp,
						'noise_for_both_groups':False,
						'dataset_size':0,
					}

					# parameters={ #worked out quiet well
					# 	'nb_attributes_entities':2,
					# 	'nb_max_items_entities':4,
					# 	'nb_attributes_individuals':2,
					# 	'nb_max_items_individuals':4,
					# 	'nb_patterns':3,
					# 	'support_of_context_best_pattern':5,#20 high sparsity
					# 	'support_of_group_of_indiviudals':5,#20 high sparsity
					# 	'size_entities':150,
					# 	'size_individuals':80,
					# 	'noise_rate_add_subsuming_parents':1.,
					# 	'noise_rate_negative_examples':0.2,
					# 	'sparsity_outcome':0.33,
					# 	'noise_for_both_groups':False,
					# 	'dataset_size':0,
					# }



					# parameters={
					# 	'nb_attributes_entities':2,
					# 	'nb_max_items_entities':5,
					# 	'nb_attributes_individuals':2,
					# 	'nb_max_items_individuals':5,
					# 	'nb_patterns':3,
					# 	'support_of_context_best_pattern':4,#20 high sparsity
					# 	'support_of_group_of_indiviudals':4,#20 high sparsity
					# 	'size_entities':200,
					# 	'size_individuals':120,
					# 	'noise_rate_add_subsuming_parents':1.,
					# 	'noise_rate_negative_examples':0.0,
					# 	'sparsity_outcome':0.0,
					# 	'noise_for_both_groups':False,
					# 	'dataset_size':0,
					# }
					
					# parameters={
					# 		'nb_attributes_entities':3,
					# 		'nb_max_items_entities':4,
					# 		'nb_attributes_individuals':3,
					# 		'nb_max_items_individuals':4,
					# 		'nb_patterns':5,
					# 		'support_of_context_best_pattern':10,#20 high sparsity
					# 		'support_of_group_of_indiviudals':10,#20 high sparsity
					# 		'size_entities':2000,
					# 		'size_individuals':500,
					# 		'noise_rate_add_subsuming_parents':1.,
					# 		'noise_rate_negative_examples':0.,
					# 		'sparsity_outcome':0.,
					# 		'noise_for_both_groups':False,
					#		'dataset_size':0,
					# 	}

					entities,individuals,outcomes,patterns,attributes_entities,attributes_individuals=generate_synthetic_data_categorical(
										nb_attributes_entities=parameters['nb_attributes_entities']
										,nb_max_items_entities=parameters['nb_max_items_entities']
										,nb_attributes_individuals=parameters['nb_attributes_individuals']
										,nb_max_items_individuals=parameters['nb_max_items_individuals']
										,nb_patterns=parameters['nb_patterns']
										,support_of_context_best_pattern=parameters['support_of_context_best_pattern']
										,support_of_group_of_indiviudals=parameters['support_of_group_of_indiviudals']
										,size_entities=parameters['size_entities']
										,size_individuals=parameters['size_individuals']
										,noise_rate_add_subsuming_parents=parameters['noise_rate_add_subsuming_parents']
										,noise_rate_negative_examples=parameters['noise_rate_negative_examples']
										,sparsity_outcome=parameters['sparsity_outcome'],
										noise_for_both_groups=parameters['noise_for_both_groups'])

					
					writeCSVwithHeader(entities,itemsFile,selectedHeader=['ide']+[x for x in attributes_entities],delimiter='\t',flagWriteHeader=True)
					writeCSVwithHeader(individuals,usersFile,selectedHeader=['idi']+[x for x in attributes_individuals],delimiter='\t',flagWriteHeader=True)
					writeCSVwithHeader(outcomes,reviewsFile,selectedHeader=['idi','ide','outcome'],delimiter='\t',flagWriteHeader=True)
					writeCSVwithHeader(patterns,working_repo+'//patterns_synth.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
					writeCSVwithHeader(patterns,working_repo+'//patterns_extents_synth.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
					writeCSVwithHeader([parameters],working_repo+'//artificial_data_generator_parameters_synth.csv',selectedHeader=['nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome'],delimiter='\t',flagWriteHeader=True)
					

					JSON_TO_WRITE={
						"objects_file":working_repo+"//items_synth.csv",
						"individuals_file":working_repo+"//users_synth.csv",
						"reviews_file":working_repo+"//reviews_synth.csv",
						"delimiter":"\t",

						"nb_objects":50000,
						"nb_individuals":50000,

						"arrayHeader":[],
						"numericHeader":[],
						"vector_of_outcome":None,
						"vector_of_outcome_OLD":["outcome"],
						"ponderation_attribute":None,

						"description_attributes_objects":[[x,"simple"] for x in attributes_entities],
						"description_attributes_individuals":[[x,"simple"] for x in attributes_individuals],
						
						"threshold_objects":3,
						"threshold_individuals":3,
						"threshold_quality":0.5,
						

						"aggregation_measure":"VECTOR_VALUES",
						"aggregation_measure_OLD":"SYMBOLIC_MAJORITY",
						"similarity_measure":"MAAD",
						"similarity_measure_OLD":"SAME_VOTE",


						"quality_measure":"DISAGR_SUMDIFF",
						"algorithm":"DSC+CLOSED+UB2",
						"algorithm_OLD":"DSC+SamplingPeers+RandomWalk",
						"timebudget":86400,
						

						"objects_scope":[], 
						
						"individuals_1_scope":[
						],
						"individuals_2_scope":[
						],

						
						"results_destination":working_repo+"//results_synthetic_synth.csv",
						"detailed_results_destination":working_repo+"//",
						"symmetry":True

					}


					writeJSON(JSON_TO_WRITE,working_repo+"//to_test_synth.json")
					tstart=time.time()
					call(['pypy', '..//DSC_Project//main.py',working_repo+"//to_test_synth.json",'-q','--export_support','--verbose'])
					timespent=time.time()-tstart


					patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
					patterns_set_results_file=working_repo+"//results_synthetic_synth_EXTENTS.csv"
					patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_ground_truth_DESCS=[(sorted(x['context'].values()),sorted(x['g_1'].values()),sorted(x['g_2'].values())) for x in patterns_set_ground_truth]
					patterns_set_results_DESCS=[(x['context'],x['g_1'],x['g_2']) for x in patterns_set_results]
					# for row in patterns_set_results_DESCS:
					# 	print row
					# print '   '
					# for row in patterns_set_ground_truth_DESCS:
					# 	print row
					# print patterns_set_results_DESCS
					# print patterns_set_ground_truth_DESCS
					#raw_input('.....')
					patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth] 
					patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
					print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
					print similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)

					# results_evaluation={} 
					# results_evaluation.update(parameters)
					# results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					
					# try:
					# 	results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
					# except Exception as e:
					# 	results_evaluation['fscore_jaccard']=0.
					
					

					# results_evaluation['precision_cover'],results_evaluation['recall_cover']=similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					# results_evaluation['recall_pattern_ML']=similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
					# results_evaluation['recall_pattern_cover']=similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
					# results_evaluation['nb_pattern_returned']=len(patterns_set_results)
					# results_evaluation['algorithm']=JSON_TO_WRITE['algorithm']
					
					method_recall_patterns={'DEBuNk':recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)}
					print method_recall_patterns
					results_evaluation={}
					results_evaluation.update(parameters)
					results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					try:
						results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
					except Exception as xxx:
						results_evaluation['fscore_jaccard']=0.
					results_evaluation['algorithm']='DEBuNk'
					results_evaluation['nb_pattern_returned']=len(patterns_set_results)
					results_evaluation['pattern_by_pattern_recall']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
					results_evaluation['timespent']=timespent
					writeCSVwithHeader([results_evaluation],working_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','nb_pattern_returned','pattern_by_pattern_recall','timespent','dataset_size'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
					Evaluation_results_new=False

					#raw_input('....')

					test_sampling_too=True
					if test_sampling_too:
						JSON_TO_WRITE_FOR_SAMPLING=deepcopy(JSON_TO_WRITE)
						JSON_TO_WRITE_FOR_SAMPLING['algorithm']="DSC+SamplingPeers+RandomWalk"
						JSON_TO_WRITE_FOR_SAMPLING['timebudget']=5
						JSON_TO_WRITE_FOR_SAMPLING['results_destination']=working_repo+"//results_synthetic_sampling_synth.csv"
						writeJSON(JSON_TO_WRITE_FOR_SAMPLING,working_repo+"//to_test_sampling_synth.json")
						
						tstart=time.time()
						call(['pypy', '..//DSC_Project//main.py',working_repo+"//to_test_sampling_synth.json",'-q','--export_support','--verbose'])
						timespent=time.time()-tstart

						patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
						patterns_set_results_file=working_repo+"//results_synthetic_sampling_synth_EXTENTS.csv"
						patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
						patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
						patterns_set_ground_truth_DESCS=[(sorted(x['context'].values()),sorted(x['g_1'].values()),sorted(x['g_2'].values())) for x in patterns_set_ground_truth]
						patterns_set_results_DESCS=[(x['context'],x['g_1'],x['g_2']) for x in patterns_set_results]
						# for row in patterns_set_results_DESCS:
						# 	print row
						# print '   '
						# for row in patterns_set_ground_truth_DESCS:
						# 	print row
						# print patterns_set_results_DESCS
						# print patterns_set_ground_truth_DESCS
						#raw_input('.....')
						patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
						patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
						print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
						print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
						print similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
						print similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)

						method_recall_patterns['Quick-DEBuNk']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)


						results_evaluation={}
						results_evaluation.update(parameters)
						results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
						try:
							results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
						except Exception as xxx:
							results_evaluation['fscore_jaccard']=0.
						results_evaluation['algorithm']='Quick-DEBuNk'
						results_evaluation['nb_pattern_returned']=len(patterns_set_results)
						results_evaluation['pattern_by_pattern_recall']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
						results_evaluation['timespent']=timespent
						writeCSVwithHeader([results_evaluation],working_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','nb_pattern_returned','pattern_by_pattern_recall','timespent','dataset_size'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
						


					print method_recall_patterns
					# if True:
					# 	from plotter.perfPlotter import plot_radar_chart
					# 	plot_radar_chart(method_recall_patterns)
					

					#raw_input('...')

				if True:
					
					numeric_attrs=[]
					array_attrs=[]
					outcome_attrs=None
					method_aggregation_outcome="SYMBOLIC_MAJORITY"
					itemsScope=[]
					users_1_Scope=[]
					users_2_Scope=[]
					nb_items=float('inf')
					nb_individuals=float('inf')
					attributes_to_consider=["PROCEDURE_SUBJECT"]
					create_boolean_attributes_for_hmt=True
					nb_items_entities=float('inf')
					nb_items_individuals=float('inf')
					hmt_to_itemset=True
					delimiter="\t"


					
					
					

				if True:  



					new_behavioral_dataset,header=create_behavioral_cartesian_dataset_for_COSMIC_BIPARTITE(
						itemsFile,
						usersFile,
						reviewsFile,
						numeric_attrs=numeric_attrs,
						array_attrs=array_attrs,
						outcome_attrs=outcome_attrs,
						method_aggregation_outcome=method_aggregation_outcome,
						itemsScope=itemsScope,
						users_1_Scope=users_1_Scope,
						users_2_Scope=users_2_Scope,
						nb_items=nb_items,
						nb_individuals=nb_individuals,
						attributes_to_consider=attributes_to_consider,
						nb_items_entities=nb_items_entities,
						nb_items_individuals=nb_items_individuals,
						hmt_to_itemset=hmt_to_itemset,
						create_boolean_attributes_for_hmt=create_boolean_attributes_for_hmt,
						delimiter=delimiter)

					writeCSVwithHeader(new_behavioral_dataset,working_repo+'//TEST_COSMIC.csv',selectedHeader=header,delimiter=';',flagWriteHeader=True) 
					items,h_items=readCSVwithHeader(itemsFile,delimiter='\t')
					
					users,h_users=readCSVwithHeader(usersFile,delimiter='\t')

					# parametersFile=[
					# 	['minWeight:2'],
					# 	['minWraccPerEdge:0.05'],
					# 	['usedModel:config'],
					# 	['inputFilePath:'+working_repo+'//TEST_COSMIC.csv'],
					# 	['outputFolderPath:'+working_repo+'//results'],#.//ComparingWithExistingAlgorithms//results'],
					# 	['postProcessing:jaccardSummary'],
					# 	['redundancyThreshold:0.01'],
					# 	['minVertexSize:8'],
					# 	['minEdgeSize:10'],
					# 	['minWracc:5.'],
					# 	['minLift:5.'],
					# 	['measure:lift']
					# ]

					parametersFile=[
						['minWeight:2'],
						['minWraccPerEdge:200.'],
						['usedModel:config'],
						['inputFilePath:'+working_repo+'//TEST_COSMIC.csv'],
						['outputFolderPath:'+working_repo+'//results'],#.//ComparingWithExistingAlgorithms//results'],
						['postProcessing:jaccardSummary'],
						['redundancyThreshold:0.01'],
						['minVertexSize:8'],
						['minEdgeSize:10'],
						['minWracc:5.'],
						['minLift:5.'],
						['measure:lift']
					]
					writeCSV(parametersFile,'.//parametersFile.txt')


					print " ".join(['java', '-jar','.//Cosmic.jar','.//parametersFile.txt'])
					tstart=time.time()
					call(['java', '-jar','.//Cosmic.jar','.//parametersFile.txt'])
					
					#shutil.move('./results', working_repo+'//results')
					res=readJSON_stringifyUnicodes(working_repo+'//results//results.json')
					exceptionalSubgraphs=res['exceptionalSubgraphs']
					to_write=[]
					for eg in exceptionalSubgraphs:
						full_desc={str(x):str(y) for x,y in eg['context'].iteritems()}
						context_desc={x:full_desc[x] for x in full_desc if 'CE' in x}
						context_desc={x:full_desc[x] for x in context_desc if full_desc[x]!='*'}
						#print compute_support_categorical(items,context_desc)
						g_1_desc={x.split('_')[0]:full_desc[x] for x in full_desc if 'CI' in x and '_1' in x and full_desc[x]!='*'}
						g_2_desc={x.split('_')[0]:full_desc[x] for x in full_desc if 'CI' in x and '_2' in x and full_desc[x]!='*'}
						#print context_desc,g_1_desc,g_2_desc
						sup_context=[items[i][h_items[0]] for i in compute_support_categorical(items,context_desc)]
						sup_g1=[users[i][h_users[0]] for i in compute_support_categorical(users,g_1_desc)]
						sup_g2=[users[i][h_users[0]] for i in compute_support_categorical(users,g_2_desc)]
						#print len(sup_context),len(sup_g1),len(sup_g2)
						record={
							'context':context_desc,
							'g_1':g_1_desc,
							'g_2':g_2_desc,
							'context_extent':sup_context,
							'g_1_extent':sup_g1,
							'g_2_extent':sup_g2,
							'sim_ref':0.,
							'sim_context':0.,
							'quality':0.
						}
						to_write.append(record)
						#raw_input('ss')
					#raw_input('...')
					writeCSVwithHeader(to_write,working_repo+'//patterns_cosmic_synth_extent.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
					timespent=time.time()-tstart



					patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
					patterns_set_results_file=working_repo+"//patterns_cosmic_synth_extent.csv"
					patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					
					# for row in patterns_set_ground_truth:
					# 	print row['context_extent'],row['g_1_extent'],row['g_2_extent']
					# for row in patterns_set_results:
					# 	print row['context_extent'],row['g_1_extent'],row['g_2_extent']

					patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
					patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
					print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					method_recall_patterns['SD-COSMIC']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
					print method_recall_patterns
					results_evaluation={}
					results_evaluation.update(parameters)
					results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					try:
						results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
					except Exception as xxx:
						results_evaluation['fscore_jaccard']=0.
					results_evaluation['algorithm']='SD-COSMIC'
					results_evaluation['nb_pattern_returned']=len(patterns_set_results)
					results_evaluation['pattern_by_pattern_recall']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
					results_evaluation['timespent']=timespent
					results_evaluation['dataset_size']=len(new_behavioral_dataset)
					writeCSVwithHeader([results_evaluation],working_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','nb_pattern_returned','pattern_by_pattern_recall','timespent','dataset_size'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
					
					#raw_input('*****')

				if True:

					
					new_behavioral_dataset_majority,header_majority=create_behavioral_with_majority_dataset(
						itemsFile,
						usersFile,
						reviewsFile,
						numeric_attrs=numeric_attrs,
						array_attrs=array_attrs,
						outcome_attrs=outcome_attrs,
						method_aggregation_outcome=method_aggregation_outcome,
						itemsScope=itemsScope,
						users_1_Scope=users_1_Scope,
						users_2_Scope=users_2_Scope,
						nb_items=nb_items,
						nb_individuals=nb_individuals,
						attributes_to_consider=attributes_to_consider,
						nb_items_entities=nb_items_entities,
						nb_items_individuals=nb_items_individuals,
						hmt_to_itemset=hmt_to_itemset,
						create_boolean_attributes_for_hmt=create_boolean_attributes_for_hmt,
						delimiter=delimiter)
					writeCSVwithHeader(new_behavioral_dataset_majority,working_repo+'//TEST_MAJORITY.csv',selectedHeader=header_majority,delimiter='\t',flagWriteHeader=True)

					tstart=time.time()
					call(['py', 'pysubgroupdemo.py',working_repo+'//TEST_MAJORITY.csv',working_repo+'//patterns_extents_synth_subgroup_majority.csv'])
					timespent=time.time()-tstart
					patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
					patterns_set_results_file=working_repo+"//patterns_extents_synth_subgroup_majority.csv"
					patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					
					patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
					patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
					print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					
					method_recall_patterns['SD-Majority']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)


					results_evaluation={}
					results_evaluation.update(parameters)

					results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					try:
						results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
					except Exception as xxx:
						results_evaluation['fscore_jaccard']=0.
					results_evaluation['algorithm']='SD-Majority'
					results_evaluation['nb_pattern_returned']=len(patterns_set_results)
					results_evaluation['pattern_by_pattern_recall']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
					results_evaluation['timespent']=timespent
					results_evaluation['dataset_size']=len(new_behavioral_dataset_majority)
					writeCSVwithHeader([results_evaluation],working_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','nb_pattern_returned','pattern_by_pattern_recall','timespent','dataset_size'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
					print method_recall_patterns
					# if True:
					# 	from plotter.perfPlotter import plot_radar_chart
					# 	plot_radar_chart(working_repo,method_recall_patterns)

				
				if True:

					new_behavioral_dataset_cartesian,header_cartesian=create_behavioral_cartesian_dataset(
						itemsFile,
						usersFile,
						reviewsFile,
						numeric_attrs=numeric_attrs,
						array_attrs=array_attrs,
						outcome_attrs=outcome_attrs,
						method_aggregation_outcome=method_aggregation_outcome,
						itemsScope=itemsScope,
						users_1_Scope=users_1_Scope,
						users_2_Scope=users_2_Scope,
						nb_items=nb_items,
						nb_individuals=nb_individuals,
						attributes_to_consider=attributes_to_consider,
						nb_items_entities=nb_items_entities,
						nb_items_individuals=nb_items_individuals,
						hmt_to_itemset=hmt_to_itemset,
						create_boolean_attributes_for_hmt=create_boolean_attributes_for_hmt,
						delimiter=delimiter)
					writeCSVwithHeader(new_behavioral_dataset_cartesian,working_repo+'//TEST_CARTESIAN.csv',selectedHeader=header_cartesian,delimiter='\t',flagWriteHeader=True)
					

					tstart=time.time()
					call(['py', 'pysubgroupdemo.py',working_repo+'//TEST_CARTESIAN.csv',working_repo+'//patterns_extents_synth_subgroup_cartesian.csv'])
					timespent=time.time()-tstart
					patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
					patterns_set_results_file=working_repo+"//patterns_extents_synth_subgroup_cartesian.csv"
					patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					
					# for row in patterns_set_ground_truth:
					# 	print row['context_extent'],row['g_1_extent'],row['g_2_extent']
					# for row in patterns_set_results:
					# 	print row['context_extent'],row['g_1_extent'],row['g_2_extent']

					patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
					patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
					print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					method_recall_patterns['SD-Cartesian']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)

					results_evaluation={}
					results_evaluation.update(parameters)
					results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					try:
						results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
					except Exception as xxx:
						results_evaluation['fscore_jaccard']=0.
					results_evaluation['algorithm']='SD-Cartesian'
					results_evaluation['nb_pattern_returned']=len(patterns_set_results)
					results_evaluation['pattern_by_pattern_recall']=recall_pattern_by_pattern(patterns_set_results,patterns_set_ground_truth)
					results_evaluation['timespent']=timespent
					results_evaluation['dataset_size']=len(new_behavioral_dataset_cartesian)
					writeCSVwithHeader([results_evaluation],working_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','nb_pattern_returned','pattern_by_pattern_recall','timespent','dataset_size'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
					print method_recall_patterns
				# if True:
				# 	from plotter.perfPlotter import plot_radar_chart
				# 	plot_radar_chart(working_repo,method_recall_patterns)

				if True:
					IGNORE=[]#IGNORE=['SD-COSMIC']
					MAPS={'SD-COSMIC*':'COSMIC','SD-COSMIC':'COSMIC'}
					MAPS_FILES_NAMES={
						"Quick-DEBuNk":'results_synthetic_sampling_synth_EXTENTS.csv',
						"DEBuNk": 'results_synthetic_synth_EXTENTS.csv',
						"SD-Majority": 'patterns_extents_synth_subgroup_majority.csv',
						"SD-Cartesian": 'patterns_extents_synth_subgroup_cartesian.csv',
						"COSMIC": 'patterns_cosmic_synth_extent.csv'

					}
					evalres,h=readCSVwithHeader(working_repo+'//evaluation_results.csv',numberHeader=['noise_rate_negative_examples','fscore_jaccard','sparsity_outcome'],arrayHeader=['pattern_by_pattern_recall'],delimiter='\t')
					method_recall_patterns={}
					
					if evalres[0]['noise_rate_negative_examples']!=0. or evalres[0]['sparsity_outcome']!=0.:
						continue
					for row in evalres: 
						names_to_consider=MAPS.get(row['algorithm'],row['algorithm'])
						if row['algorithm'] in IGNORE:
							continue
						method_recall_patterns[names_to_consider]=row['pattern_by_pattern_recall']
						if names_to_consider not in method_fscore_patterns:
							method_fscore_patterns[names_to_consider]=[]
						
						
						recheck_data=True
						if recheck_data:
							patterns_set_ground_truth_file=working_repo+"//patterns_extents_synth.csv"
							patterns_set_results_file=working_repo+"//"+MAPS_FILES_NAMES[names_to_consider]
							patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=['quality'],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','quality'],delimiter='\t')
							patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=['quality'],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent','quality'],delimiter='\t')
							
							patterns_set_results=sorted(patterns_set_results,key=lambda rec:rec['quality'],reverse=True)[:10]


							patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
							patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
							
							

							precision_jaccard,recall_jaccard=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
							
							try:
								new_fscore=2*(precision_jaccard*recall_jaccard)/(precision_jaccard+recall_jaccard)
							except:
								new_fscore=0.

							method_fscore_patterns[names_to_consider].append(new_fscore)
							print len(patterns_set_results),new_fscore,len(patterns_set_results)
						else:
							method_fscore_patterns[names_to_consider].append(row['fscore_jaccard'])

						#print method_fscore_patterns

					print method_recall_patterns
					try:
						if False:
							from plotter.perfPlotter import plot_radar_chart,plot_boxplot_chart
							plot_radar_chart(working_repo,method_recall_patterns)
						
					except Exception as e:
						raise e
						continue
					
					
					for m,v in method_recall_patterns.iteritems():
						if m not in method_recall_patterns_avg:
							method_recall_patterns_avg[m]=[]
						method_recall_patterns_avg[m].append(v)
		if True:


				
			#raw_input('$$$$$$$')
			for m in method_recall_patterns_avg:
				varr=method_recall_patterns_avg[m]
				varr=[x for x in varr if type(x) is list]
				varr_avg=[map(itemgetter(x),varr)  for x in range(len(varr[0]))]
				varr_avg=[sum(x)/float(len(x)) for x in varr_avg]
				#print varr_avg
				method_recall_patterns_avg[m]=varr_avg
			print method_recall_patterns_avg
			from plotter.perfPlotter import plot_radar_chart,plot_boxplot_chart
			for algo in method_fscore_patterns:
				print algo,method_fscore_patterns[algo]
			plot_radar_chart('.//ComparingWithExistingAlgorithms',method_recall_patterns_avg)
			plot_boxplot_chart('.//ComparingWithExistingAlgorithms',method_fscore_patterns)
			print 'Aggregated results are plotted in ComparingWithExistingAlgorithms repository ....'
			#raw_input('................................................')





			
	if type(args.Majority) is list:
		print "Transform a behavioral dataset to confronting individuals with the majority."

		itemsFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_1537291063005_USED\GENERATED_0001\items_0001.csv"#"./Data/EPD8/items.csv" 
		usersFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_1537291063005_USED\GENERATED_0001\individuals_0001.csv" #"./Data/EPD8/users.csv" 
		reviewsFile="C:\Users\Adnene\Desktop\LastECMLPKDD2017CODE\DataProcessing\SyntheticData_1537291063005_USED\GENERATED_0001\outcomes_0001.csv"#"./Data/EPD8/reviews.csv" 
		numeric_attrs=[]
		array_attrs=['PROCEDURE_SUBJECT']
		outcome_attrs=None
		method_aggregation_outcome="SYMBOLIC_MAJORITY"
		itemsScope=[]
		users_1_Scope=[]
		users_2_Scope=[]
		nb_items=float('inf')
		nb_individuals=float('inf')
		attributes_to_consider=["PROCEDURE_SUBJECT"]
		create_boolean_attributes_for_hmt=True
		nb_items_entities=float('inf')
		nb_items_individuals=float('inf')
		hmt_to_itemset=True
		delimiter="\t"
		
		new_behavioral_dataset,header=create_behavioral_with_majority_dataset(
			itemsFile,
			usersFile,
			reviewsFile,
			numeric_attrs=numeric_attrs,
			array_attrs=array_attrs,
			outcome_attrs=outcome_attrs,
			method_aggregation_outcome=method_aggregation_outcome,
			itemsScope=itemsScope,
			users_1_Scope=users_1_Scope,
			users_2_Scope=users_2_Scope,
			nb_items=nb_items,
			nb_individuals=nb_individuals,
			attributes_to_consider=attributes_to_consider,
			nb_items_entities=nb_items_entities,
			nb_items_individuals=nb_items_individuals,
			hmt_to_itemset=hmt_to_itemset,
			create_boolean_attributes_for_hmt=create_boolean_attributes_for_hmt,
			delimiter=delimiter)
		

		writeCSVwithHeader(new_behavioral_dataset,'MAJOR.csv',selectedHeader=header,delimiter='\t',flagWriteHeader=True)


	if type(args.Transform) is list:
		print "Transform a behavioral dataset to confronting groups of individuals in all contexts."

		itemsFile="./Data/EPD8/items.csv"
		usersFile="./Data/EPD8/users.csv"
		reviewsFile="./Data/EPD8/reviews.csv"
		numeric_attrs=[]
		array_attrs=['PROCEDURE_SUBJECT']
		outcome_attrs=None
		method_aggregation_outcome="SYMBOLIC_MAJORITY"
		itemsScope=[]
		users_1_Scope=[{"dimensionName":"COUNTRY","inSet":["France"]}]
		users_2_Scope=[{"dimensionName":"COUNTRY","inSet":["Germany"]}]
		nb_items=float('inf')
		nb_individuals=float('inf')
		attributes_to_consider=["PROCEDURE_SUBJECT"]
		create_boolean_attributes_for_hmt=True
		nb_items_entities=float('inf')
		nb_items_individuals=float('inf')
		hmt_to_itemset=True
		delimiter="\t"
		
		new_behavioral_dataset,header=create_behavioralconfronting_dataset(
			itemsFile,
			usersFile,
			reviewsFile,
			numeric_attrs=numeric_attrs,
			array_attrs=array_attrs,
			outcome_attrs=outcome_attrs,
			method_aggregation_outcome=method_aggregation_outcome,
			itemsScope=itemsScope,
			users_1_Scope=users_1_Scope,
			users_2_Scope=users_2_Scope,
			nb_items=nb_items,
			nb_individuals=nb_individuals,
			attributes_to_consider=attributes_to_consider,
			nb_items_entities=nb_items_entities,
			nb_items_individuals=nb_items_individuals,
			hmt_to_itemset=hmt_to_itemset,
			create_boolean_attributes_for_hmt=create_boolean_attributes_for_hmt,
			delimiter=delimiter)
		
		
		writeCSVwithHeader(new_behavioral_dataset,'new.csv',selectedHeader=header,delimiter='\t',flagWriteHeader=True)
		call(["csv2arff", "new.csv","new.arff"])
	
	elif type(args.GenerateSynthetic) is list:
		
		

		print "Generating Synthetic Data"

		if True:
			if not os.path.exists('.//SyntheticData'):
				os.makedirs('.//SyntheticData')
			else:
				if False:
					shutil.rmtree('.//SyntheticData')
					os.makedirs('.//SyntheticData')
			
			Evaluation_results_new=True
			

			varying_sparsity_outcome=[0.,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.9][0:1]
			print varying_sparsity_outcome
			varying_noise_rate_add_subsuming_parents=[0.0]
			varying_noise_rate_negative_examples=[0.0]

			i=0
			for vso,vsp,vne in product(varying_sparsity_outcome,varying_noise_rate_add_subsuming_parents,varying_noise_rate_negative_examples):
				i+=1
				parameters={
					'nb_attributes_entities':7,
					'nb_max_items_entities':4,
					'nb_attributes_individuals':7,
					'nb_max_items_individuals':4,
					'nb_patterns':5,
					'support_of_context_best_pattern':5,#20 high sparsity
					'support_of_group_of_indiviudals':5,#20 high sparsity
					'size_entities':1000,
					'size_individuals':200,
					'noise_rate_add_subsuming_parents':vsp,
					'noise_rate_negative_examples':vne,
					'sparsity_outcome':vso
				}
				#We start first by generating the three-set-patterns
				#We generate objects supporting the three set patterns both in E and U (two groups)
				#We give them categorical votes so that they are in conflict
				#We generate random data to reach the size of the dataset both in entities and individuals 


				# attributes=range(nb_attributes_entities)
				# print generate_random_non_empty_itemset_with_max(attributes,nb_max=nb_max_items_entities)
				
				repoGENERATED=".//SyntheticData//GENERATED_"+str(i).zfill(4)

				if not os.path.exists(repoGENERATED):
					os.makedirs(repoGENERATED)
				else:
					if False:
						shutil.rmtree(repoGENERATED)
						os.makedirs(repoGENERATED)

				entities,individuals,outcomes,patterns=generate_synthetic_data(
									nb_attributes_entities=parameters['nb_attributes_entities']
									,nb_max_items_entities=parameters['nb_max_items_entities']
									,nb_attributes_individuals=parameters['nb_attributes_individuals']
									,nb_max_items_individuals=parameters['nb_max_items_individuals']
									,nb_patterns=parameters['nb_patterns']
									,support_of_context_best_pattern=parameters['support_of_context_best_pattern']
									,support_of_group_of_indiviudals=parameters['support_of_group_of_indiviudals']
									,size_entities=parameters['size_entities']
									,size_individuals=parameters['size_individuals']
									,noise_rate_add_subsuming_parents=parameters['noise_rate_add_subsuming_parents']
									,noise_rate_negative_examples=parameters['noise_rate_negative_examples']
									,sparsity_outcome=parameters['sparsity_outcome'])

				

				#raw_input('......')



				writeCSVwithHeader(entities,repoGENERATED+'//items_'+str(i).zfill(4)+'.csv',selectedHeader=['ide','descriptionEntity'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(individuals,repoGENERATED+'//individuals_'+str(i).zfill(4)+'.csv',selectedHeader=['idi','descriptionIndividual'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(outcomes,repoGENERATED+'//outcomes_'+str(i).zfill(4)+'.csv',selectedHeader=['idi','ide','outcome'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(patterns,repoGENERATED+'//patterns_'+str(i).zfill(4)+'.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(patterns,repoGENERATED+'//patterns_extents_'+str(i).zfill(4)+'.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader([parameters],repoGENERATED+'//artificial_data_generator_parameters_'+str(i).zfill(4)+'.csv',selectedHeader=['nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome'],delimiter='\t',flagWriteHeader=True)
				
				#pypy ..//DSC_Project//main.py ..//DataProcessing//SyntheticData//to_test.json -q --export_support --verbose
			


				JSON_TO_WRITE={
					"objects_file":"..//DataProcessing//"+repoGENERATED+"//items_"+str(i).zfill(4)+".csv",
					"individuals_file":"..//DataProcessing//"+repoGENERATED+"//individuals_"+str(i).zfill(4)+".csv",
					"reviews_file":"..//DataProcessing//"+repoGENERATED+"//outcomes_"+str(i).zfill(4)+".csv",
					"delimiter":"\t",

					"nb_objects":50000,
					"nb_individuals":50000,

					"arrayHeader":["descriptionEntity","descriptionIndividual"],
					"numericHeader":[],
					"vector_of_outcome":None,
					"vector_of_outcome_OLD":["outcome"],
					"ponderation_attribute":None,

					"description_attributes_objects":[["descriptionEntity", "themes"]],
					"description_attributes_individuals":[["descriptionIndividual", "themes"]],
					
					"threshold_objects":1,
					"threshold_individuals":1,
					"threshold_quality":0.75,
					

					"aggregation_measure":"VECTOR_VALUES",
					"aggregation_measure_OLD":"SYMBOLIC_MAJORITY",
					"similarity_measure":"MAAD",
					"similarity_measure_OLD":"SAME_VOTE",


					"quality_measure":"DISAGR_SUMDIFF",
					"algorithm":"DSC+CLOSED+UB2",
					"algorithm_OLD":"DSC+SamplingPeers+RandomWalk",
					"timebudget":15,
					

					"objects_scope":[], 
					
					"individuals_1_scope":[
					],
					"individuals_2_scope":[
					],

					
					"results_destination":repoGENERATED+"//results_synthetic_"+str(i).zfill(4)+".csv",
					"detailed_results_destination":repoGENERATED+"//",
					"symmetry":True

				}

				writeJSON(JSON_TO_WRITE,repoGENERATED+"//to_test_"+str(i).zfill(4)+".json")

				call(['pypy', '..//DSC_Project//main.py',repoGENERATED+"//to_test_"+str(i).zfill(4)+".json",'-q','--export_support','--verbose'])


				patterns_set_ground_truth_file=repoGENERATED+"//patterns_extents_"+str(i).zfill(4)+".csv"
				patterns_set_results_file=repoGENERATED+"//results_synthetic_"+str(i).zfill(4)+"_EXTENTS.csv"


				patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
				patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
				

				patterns_set_ground_truth_DESCS=[(x['context'],x['g_1'],x['g_2']) for x in patterns_set_ground_truth]
				patterns_set_results_DESCS=[(x['context'],x['g_1'],x['g_2']) for x in patterns_set_results]

				patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
				patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]

			


			
				print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
				print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
				print similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
				print similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)

				results_evaluation={} 
				results_evaluation.update(parameters)
				results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
				results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
				results_evaluation['precision_cover'],results_evaluation['recall_cover']=similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
				results_evaluation['recall_pattern_ML']=similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
				results_evaluation['recall_pattern_cover']=similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
				results_evaluation['nb_pattern_returned']=len(patterns_set_results)
				results_evaluation['algorithm']=JSON_TO_WRITE['algorithm']
			
				writeCSVwithHeader([results_evaluation],'./SyntheticData/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','precision_jaccard','recall_jaccard','fscore_jaccard','precision_cover','recall_cover','recall_pattern_ML','recall_pattern_cover','nb_pattern_returned'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
				Evaluation_results_new=False
		from plotter.perfPlotter import plotPerformanceSynthetic
		plotPerformanceSynthetic('./SyntheticData/evaluation_results.csv','sparsity_outcome',['DSC+CLOSED+UB2'])


	elif type(args.GenerateSyntheticCategorical) is list:
		print "Generating Synthetic Data With categorical attributes"
		
		if not os.path.exists('.//NOISE_EXPERIMENTS'):
			os.makedirs('.//NOISE_EXPERIMENTS')
		else:
			if False:
				shutil.rmtree('.//NOISE_EXPERIMENTS')
				os.makedirs('.//NOISE_EXPERIMENTS')

		if type(args.sparsity) is list:
			varying_sparsity_outcome=[float(x) for x in args.sparsity]
		else:
			varying_sparsity_outcome=[0.33,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.9][0:1]
		print varying_sparsity_outcome
		original_repo='NOISE_EXPERIMENTS'#//SyntheticData'+'_'+str(int(time.time()*1000))
		if not os.path.exists(original_repo):
			os.makedirs(original_repo)
		#raw_input('....')

		varying_noise_rate_add_subsuming_parents=[1.0]
		varying_noise_rate_negative_examples=[0.0,0.0,0.0,0.1,0.1,0.1,0.2,0.2,0.2,0.3,0.3,0.3,0.4,0.4,0.4,0.5,0.5,0.5,0.6,0.6,0.6,0.7,0.7,0.7,0.8,0.8,0.8]#,0.9,0.9,0.9,1.,1.,1.]
		Evaluation_results_new=True
		i=0
		if True:
			for vso,vsp,vne in product(varying_sparsity_outcome,varying_noise_rate_add_subsuming_parents,varying_noise_rate_negative_examples):
				i+=1
				
				
				# parameters={
				# 			'nb_attributes_entities':4,
				# 			'nb_max_items_entities':5,
				# 			'nb_attributes_individuals':4,
				# 			'nb_max_items_individuals':5,
				# 			'nb_patterns':5,
				# 			'support_of_context_best_pattern':15,#20 high sparsity
				# 			'support_of_group_of_indiviudals':15,#20 high sparsity
				# 			'size_entities':2500,
				# 			'size_individuals':750,
				# 			'noise_rate_add_subsuming_parents':vsp,
				# 			'noise_rate_negative_examples':vne,
				# 			'sparsity_outcome':vso,
				# 			'noise_for_both_groups':True,
				# 	}


				parameters={
					'nb_attributes_entities':3,
					'nb_max_items_entities':4,
					'nb_attributes_individuals':3,
					'nb_max_items_individuals':4,
					'nb_patterns':5,
					'support_of_context_best_pattern':10,#20 high sparsity
					'support_of_group_of_indiviudals':10,#20 high sparsity
					'size_entities':2000,
					'size_individuals':500,
					'noise_rate_add_subsuming_parents':vsp,
					'noise_rate_negative_examples':vne,
					'sparsity_outcome':vso,
					'noise_for_both_groups':False,
				}




				entities,individuals,outcomes,patterns,attributes_entities,attributes_individuals=generate_synthetic_data_categorical(
									nb_attributes_entities=parameters['nb_attributes_entities']
									,nb_max_items_entities=parameters['nb_max_items_entities']
									,nb_attributes_individuals=parameters['nb_attributes_individuals']
									,nb_max_items_individuals=parameters['nb_max_items_individuals']
									,nb_patterns=parameters['nb_patterns']
									,support_of_context_best_pattern=parameters['support_of_context_best_pattern']
									,support_of_group_of_indiviudals=parameters['support_of_group_of_indiviudals']
									,size_entities=parameters['size_entities']
									,size_individuals=parameters['size_individuals']
									,noise_rate_add_subsuming_parents=parameters['noise_rate_add_subsuming_parents']
									,noise_rate_negative_examples=parameters['noise_rate_negative_examples']
									,sparsity_outcome=parameters['sparsity_outcome'],
									noise_for_both_groups=parameters['noise_for_both_groups'])

				
				repoGENERATED=".//"+original_repo+"//GENERATED_"+str(i).zfill(4)
				repoGENERATEDFORSAMPLING=".//"+original_repo+"//GENERATED_FOR_SAMPLING_"+str(i).zfill(4)

				if not os.path.exists(repoGENERATED):
					os.makedirs(repoGENERATED)
				else:
					if False:
						shutil.rmtree(repoGENERATED)
						os.makedirs(repoGENERATED)


				if not os.path.exists(repoGENERATEDFORSAMPLING):
					os.makedirs(repoGENERATEDFORSAMPLING)
				else:
					if False:
						shutil.rmtree(repoGENERATEDFORSAMPLING)
						os.makedirs(repoGENERATEDFORSAMPLING)


				print len(entities),len(individuals),len(outcomes)
				writeCSVwithHeader(entities,repoGENERATED+'//items_'+str(i).zfill(4)+'.csv',selectedHeader=['ide']+[x for x in attributes_entities],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(individuals,repoGENERATED+'//individuals_'+str(i).zfill(4)+'.csv',selectedHeader=['idi']+[x for x in attributes_individuals],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(outcomes,repoGENERATED+'//outcomes_'+str(i).zfill(4)+'.csv',selectedHeader=['idi','ide','outcome'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(patterns,repoGENERATED+'//patterns_'+str(i).zfill(4)+'.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(patterns,repoGENERATED+'//patterns_extents_'+str(i).zfill(4)+'.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader([parameters],repoGENERATED+'//artificial_data_generator_parameters_'+str(i).zfill(4)+'.csv',selectedHeader=['nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','noise_for_both_groups'],delimiter='\t',flagWriteHeader=True)
				
				writeCSVwithHeader(entities,repoGENERATEDFORSAMPLING+'//items_'+str(i).zfill(4)+'.csv',selectedHeader=['ide']+[x for x in attributes_entities],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(individuals,repoGENERATEDFORSAMPLING+'//individuals_'+str(i).zfill(4)+'.csv',selectedHeader=['idi']+[x for x in attributes_individuals],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(outcomes,repoGENERATEDFORSAMPLING+'//outcomes_'+str(i).zfill(4)+'.csv',selectedHeader=['idi','ide','outcome'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(patterns,repoGENERATEDFORSAMPLING+'//patterns_'+str(i).zfill(4)+'.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader(patterns,repoGENERATEDFORSAMPLING+'//patterns_extents_'+str(i).zfill(4)+'.csv',selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)
				writeCSVwithHeader([parameters],repoGENERATEDFORSAMPLING+'//artificial_data_generator_parameters_'+str(i).zfill(4)+'.csv',selectedHeader=['nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','noise_for_both_groups'],delimiter='\t',flagWriteHeader=True)
				


			


			# raw_input('...........')
			# writeCSVwithHeader(entities,'./SyntheticData/items.csv',selectedHeader=['ide']+attributes_entities,delimiter='\t',flagWriteHeader=True)
			# writeCSVwithHeader(individuals,'./SyntheticData/individuals.csv',selectedHeader=['idi']+attributes_individuals,delimiter='\t',flagWriteHeader=True)
			# writeCSVwithHeader(outcomes,'./SyntheticData/outcomes.csv',selectedHeader=['idi','ide','outcome'],delimiter='\t',flagWriteHeader=True)
			# writeCSVwithHeader(patterns,'./SyntheticData/patterns.csv',selectedHeader=['context','g1','g2','context_extent','g_1_extent','g_2_extent'],delimiter='\t',flagWriteHeader=True)
			# writeCSVwithHeader(patterns,'./SyntheticData/patterns_extents.csv',selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t',flagWriteHeader=True)
			

				JSON_TO_WRITE={
					"objects_file":repoGENERATED+"//items_"+str(i).zfill(4)+".csv",
					"individuals_file":repoGENERATED+"//individuals_"+str(i).zfill(4)+".csv",
					"reviews_file":repoGENERATED+"//outcomes_"+str(i).zfill(4)+".csv",
					"delimiter":"\t",

					"nb_objects":50000,
					"nb_individuals":50000,

					"arrayHeader":[],
					"numericHeader":[],
					"vector_of_outcome":None,
					"vector_of_outcome_OLD":["outcome"],
					"ponderation_attribute":None,

					"description_attributes_objects":[[x,"simple"] for x in attributes_entities],
					"description_attributes_individuals":[[x,"simple"] for x in attributes_individuals],
					
					"threshold_objects":7,
					"threshold_individuals":7,
					"threshold_quality":0.5,
					

					"aggregation_measure":"VECTOR_VALUES",
					"aggregation_measure_OLD":"SYMBOLIC_MAJORITY",
					"similarity_measure":"MAAD",
					"similarity_measure_OLD":"SAME_VOTE",


					"quality_measure":"DISAGR_SUMDIFF",
					"algorithm":"DSC+CLOSED+UB2",
					"algorithm_OLD":"DSC+SamplingPeers+RandomWalk",
					"timebudget":86400,
					

					"objects_scope":[], 
					
					"individuals_1_scope":[
					],
					"individuals_2_scope":[
					],

					
					"results_destination":repoGENERATED+"//results_synthetic_"+str(i).zfill(4)+".csv",
					"detailed_results_destination":repoGENERATED+"//",
					"symmetry":True

				}


				writeJSON(JSON_TO_WRITE,repoGENERATED+"//to_test_"+str(i).zfill(4)+".json")
				
				JSON_TO_WRITE_FOR_SAMPLING=deepcopy(JSON_TO_WRITE)
				JSON_TO_WRITE_FOR_SAMPLING['algorithm']="DSC+SamplingPeers+RandomWalk"
				JSON_TO_WRITE_FOR_SAMPLING['timebudget']=10
				JSON_TO_WRITE_FOR_SAMPLING['results_destination']=repoGENERATEDFORSAMPLING+"//results_synthetic_"+str(i).zfill(4)+".csv"
				JSON_TO_WRITE_FOR_SAMPLING['detailed_results_destination']=repoGENERATEDFORSAMPLING+"//"
				
				JSON_TO_WRITE_FOR_SAMPLING['objects_file']=repoGENERATEDFORSAMPLING+"//items_"+str(i).zfill(4)+".csv"
				JSON_TO_WRITE_FOR_SAMPLING['individuals_file']=repoGENERATEDFORSAMPLING+"//individuals_"+str(i).zfill(4)+".csv"
				JSON_TO_WRITE_FOR_SAMPLING['reviews_file']=repoGENERATEDFORSAMPLING+"//outcomes_"+str(i).zfill(4)+".csv"


				writeJSON(JSON_TO_WRITE_FOR_SAMPLING,repoGENERATEDFORSAMPLING+"//to_test_"+str(i).zfill(4)+".json")

				call(['pypy', '..//DSC_Project//main.py',repoGENERATED+"//to_test_"+str(i).zfill(4)+".json",'-q','--export_support','--verbose'])
				patterns_set_ground_truth_file=repoGENERATED+"//patterns_extents_"+str(i).zfill(4)+".csv"
				patterns_set_results_file=repoGENERATED+"//results_synthetic_"+str(i).zfill(4)+"_EXTENTS.csv"
				patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
				patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
				patterns_set_ground_truth_DESCS=[(sorted(x['context'].values()),sorted(x['g_1'].values()),sorted(x['g_2'].values())) for x in patterns_set_ground_truth]
				patterns_set_results_DESCS=[(x['context'],x['g_1'],x['g_2']) for x in patterns_set_results]
				for row in patterns_set_results_DESCS:
					print row
				print '   '
				for row in patterns_set_ground_truth_DESCS:
					print row
				# print patterns_set_results_DESCS
				# print patterns_set_ground_truth_DESCS
				#raw_input('.....')
				patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
				patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
				print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
				print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
				print similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
				print similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)

				results_evaluation={} 
				results_evaluation.update(parameters)
				results_evaluation['precision_jaccard'],results_evaluation['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
				
				try:
					results_evaluation['fscore_jaccard']=2*(results_evaluation['precision_jaccard']*results_evaluation['recall_jaccard'])/(results_evaluation['precision_jaccard']+results_evaluation['recall_jaccard'])
				except Exception as e:
					results_evaluation['fscore_jaccard']=0.
				
				

				results_evaluation['precision_cover'],results_evaluation['recall_cover']=similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
				results_evaluation['recall_pattern_ML']=similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
				results_evaluation['recall_pattern_cover']=similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
				results_evaluation['nb_pattern_returned']=len(patterns_set_results)
				results_evaluation['algorithm']=JSON_TO_WRITE['algorithm']
			
				writeCSVwithHeader([results_evaluation],'./'+original_repo+'/evaluation_results.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','noise_for_both_groups','precision_jaccard','recall_jaccard','fscore_jaccard','precision_cover','recall_cover','recall_pattern_ML','recall_pattern_cover','nb_pattern_returned'],delimiter='\t',flagWriteHeader=Evaluation_results_new)
				


				if True:
					##########FORSAMPLING############
					call(['pypy', '..//DSC_Project//main.py',repoGENERATEDFORSAMPLING+"//to_test_"+str(i).zfill(4)+".json",'-q','--export_support','--verbose'])
					patterns_set_ground_truth_file=repoGENERATEDFORSAMPLING+"//patterns_extents_"+str(i).zfill(4)+".csv"
					patterns_set_results_file=repoGENERATEDFORSAMPLING+"//results_synthetic_"+str(i).zfill(4)+"_EXTENTS.csv"
					patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent'],delimiter='\t')
					patterns_set_ground_truth_DESCS=[(sorted(x['context'].values()),sorted(x['g_1'].values()),sorted(x['g_2'].values())) for x in patterns_set_ground_truth]
					patterns_set_results_DESCS=[(x['context'],x['g_1'],x['g_2']) for x in patterns_set_results]
					for row in patterns_set_results_DESCS:
						print row
					print '   '
					for row in patterns_set_ground_truth_DESCS:
						print row
					# print patterns_set_results_DESCS
					# print patterns_set_ground_truth_DESCS
					#raw_input('.....')
					patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
					patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
					print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					print similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
					print similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)

					results_evaluation_sampling={} 
					results_evaluation_sampling.update(parameters)
					results_evaluation_sampling['precision_jaccard'],results_evaluation_sampling['recall_jaccard']=similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
					try:
						results_evaluation_sampling['fscore_jaccard']=2*(results_evaluation_sampling['precision_jaccard']*results_evaluation_sampling['recall_jaccard'])/(results_evaluation_sampling['precision_jaccard']+results_evaluation_sampling['recall_jaccard'])
					except Exception as e:
						results_evaluation_sampling['fscore_jaccard']=0.
					
					
					results_evaluation_sampling['precision_cover'],results_evaluation_sampling['recall_cover']=similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
					results_evaluation_sampling['recall_pattern_ML']=similarity_between_patterns_with_equality_MACHINELEARNING_MARC(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
					results_evaluation_sampling['recall_pattern_cover']=similarity_between_patterns_groups_with_subsumption(patterns_set_results_DESCS,patterns_set_ground_truth_DESCS)
					results_evaluation_sampling['nb_pattern_returned']=len(patterns_set_results)
					results_evaluation_sampling['algorithm']=JSON_TO_WRITE['algorithm']
				
					writeCSVwithHeader([results_evaluation_sampling],'./'+original_repo+'/evaluation_results_sampling.csv',selectedHeader=['algorithm','nb_attributes_entities','nb_max_items_entities','nb_attributes_individuals','nb_max_items_individuals','nb_patterns','support_of_context_best_pattern','support_of_group_of_indiviudals','size_entities','size_individuals','noise_rate_add_subsuming_parents','noise_rate_negative_examples','sparsity_outcome','noise_for_both_groups','precision_jaccard','recall_jaccard','fscore_jaccard','precision_cover','recall_cover','recall_pattern_ML','recall_pattern_cover','nb_pattern_returned'],delimiter='\t',flagWriteHeader=Evaluation_results_new)

				##########FORSAMPLING############

				Evaluation_results_new=False
		from plotter.perfPlotter import plotPerformanceSynthetic
		plotPerformanceSynthetic('./'+original_repo+'/evaluation_results.csv','noise_rate_negative_examples',['DSC+CLOSED+UB2'])
		plotPerformanceSynthetic('./'+original_repo+'/evaluation_results_sampling.csv','noise_rate_negative_examples',['DSC+CLOSED+UB2'])
		#writeJSON(JSON_TO_WRITE,'./SyntheticData/to_test.json')




	elif type(args.EvaluatePerformance) is list:
		print "Evaluate performance precision/recall of DSC over synthetic Data."
		patterns_set_ground_truth_file='./SyntheticData/patterns_extents.csv'
		patterns_set_results_file='../Testing_DSC_For_Synthetic/SyntheticResults/results_synthetic_EXTENTS.csv'


		patterns_set_ground_truth,_=readCSVwithHeader(patterns_set_ground_truth_file,numberHeader=[],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t')
		patterns_set_results,_=readCSVwithHeader(patterns_set_results_file,numberHeader=[],arrayHeader=['context_extent','g_1_extent','g_2_extent'],selectedHeader=['context_extent','g_1_extent','g_2_extent'],delimiter='\t')
		patterns_set_ground_truth=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_ground_truth]
		patterns_set_results=[(set(x['context_extent']),set(x['g_1_extent']),set(x['g_2_extent'])) for x in patterns_set_results]
		# print "--------------GROUND TRUTH-----------------"
		# for p in patterns_set_ground_truth:
		# 	print p
		# print "--------------GROUND TRUTH-----------------"
		# print ""
		# print ""


		# print "--------------PATTERNS EXTENTS RETURNED BY DSC-----------------"
		# for p in patterns_set_results:
		# 	print p
		# print "--------------PATTERNS EXTENTS RETURNED BY DSC-----------------"
		
		print similarity_between_patterns_set_recall_precision_with_jaccard(patterns_set_results,patterns_set_ground_truth)
		print similarity_between_patterns_set_recall_precision_with_cover(patterns_set_results,patterns_set_ground_truth)
		#print similarity_between_patterns_set_recall(patterns_set_ground_truth,patterns_set_results)
	# for row in new_behavioral_dataset:
	# 	print row
	# 	raw_input('......')


