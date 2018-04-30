'''
Created on 20 janv. 2017

@author: Adnene
'''
from math import sqrt
from outcomeAggregator.aggregateOutcome import aggregateOutcomeInitialize_DSC,aggregateOutcome_DSC,aggregateOutcomeFinalize_DSC 

def compute_aggregates_outcomes(v_ids,u_ids,entities_to_items_outcomes,method_aggregation_outcome='STANDARD'):
	
	one_entitie=entities_to_items_outcomes[next(entities_to_items_outcomes.iterkeys())]
	one_item=next(one_entitie.iterkeys())
	outcome_tuple_structure=tuple(one_entitie[one_item])
	
	u_aggregated_to_items_outcomes={}

	for v in v_ids:
		vector_associated=aggregateOutcomeInitialize_DSC(outcome_tuple_structure, method_aggregation_outcome) 
		flag_at_least_someone_voted=False
		for u in u_ids:
			try:
				v_u=entities_to_items_outcomes[u][v]
				flag_at_least_someone_voted=True
				vector_associated=aggregateOutcome_DSC(v_u, vector_associated, method_aggregation_outcome)
			except:
				continue
		if flag_at_least_someone_voted:
			u_aggregated_to_items_outcomes[v]=aggregateOutcomeFinalize_DSC(vector_associated,method_aggregation_outcome)


	return u_aggregated_to_items_outcomes


