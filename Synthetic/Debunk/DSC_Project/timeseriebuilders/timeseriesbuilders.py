'''
Created on 20 janv. 2017

@author: Adnene
'''
from math import sqrt
from measures.itemsAggregator import compute_aggregates_outcomes_on_items
from entitiesAggregator.entitiesAggregator import compute_aggregates_outcomes

def buildTimeSerie_For_GroupOfIndividuals_On_CollectionOfItems(items_metadata,entities_metadata,all_entities_to_items_outcomes,
															   time_attribute,v_ids,e_ids,
															   time_interval_length=None,aggoutcome_entities_method="VECTOR_VALUES",aggoutcome_items_method="AgreementIndex"): #iditems are sorted

	if time_interval_length is None:
		time_interval_length=-1 #time_interval_length on day
	u_aggregated_to_items_outcomes=compute_aggregates_outcomes(v_ids,e_ids,all_entities_to_items_outcomes,aggoutcome_entities_method)
	considered_sequences=[[]] #Sliced votes to sequences of votes - subsequence=[,(),...]
	slice_now=False
	for v in sorted(v_ids):
		item=items_metadata[v]
		slice_now=True if len(considered_sequences[0]) and (item[time_attribute]-items_metadata[considered_sequences[-1][0]][time_attribute]).days>time_interval_length else False
		if slice_now:
			considered_sequences.append([])
			slice_now=False
		considered_sequences[-1].append(v)

	timeserie=[compute_aggregates_outcomes_on_items([u_aggregated_to_items_outcomes[v] for v in c_s if v in u_aggregated_to_items_outcomes],aggoutcome_items_method) for c_s in considered_sequences]
	xAxis_timerie=[items_metadata[c_s[0]][time_attribute] for c_s in considered_sequences]
	items_for_each_point=considered_sequences
	return timeserie,xAxis_timerie,items_for_each_point


############################


