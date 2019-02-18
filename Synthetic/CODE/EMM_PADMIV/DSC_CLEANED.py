'''
Created on 3 mai 2017

@author: Adnene
'''
from bisect import bisect_left
from functools import partial  
from heapq import heappush, nsmallest, nlargest
from itertools import product
from math import copysign
from operator import itemgetter
from random import random 
from time import time

from ENUMERATORS_ATTRIBUTES.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config, \
    enumerator_complex_from_dataset_new_config
from ENUMERATORS_ATTRIBUTES.enumerator_attribute_nominal import enumerator_nominal_bottom_up
from filterer.filter import filter_pipeline_obj
from measures.aggregateOutcome import aggregateOutcome_DSC, \
    aggregateOutcomeFinalize_DSC, aggregateOutcomeInitialize_DSC
from measures.qualityMeasure import compute_quality_and_upperbound
from measures.similaritiesDCS import similarity_vector_measure_dcs
from util.matrixProcessing import getCompleteMatrix


# global ponderate
# ponderate = True
def binary_search(a, x, lo=0, hi=None):  # can't use a to specify default for hi
    hi = hi if hi is not None else len(a)  # hi defaults to len(a)
    pos = bisect_left(a, x, lo, hi)  # find insertion position
    return (pos)  
#from numba import jit
def ressemblance(set1,set2):
    return float(len(set1&set2))/float(max(len(set1),len(set2)))


def jaccard(set1,set2):
    return float(len(set1&set2))/float(len(set1|set2))

def transform_to_matrices(reference_matrix_dic,pattern_matrix_dic):
    matrix_general=[];matrix_general_append=matrix_general.append
    matrix_pattern=[];matrix_pattern_append=matrix_pattern.append
    header=[];header_append=header.append
    rower=[];rower_append=rower.append
    flag_header=True
    u1_row=sorted(pattern_matrix_dic)
    u2_row=sorted(pattern_matrix_dic[u1_row[0]])
    for u1 in u1_row:
        
        matrix_general_append([]);matrix_general_actual_row_append=matrix_general[-1].append
        matrix_pattern_append([]);matrix_pattern_actual_row_append=matrix_pattern[-1].append
        row_original_mepwise_sim=reference_matrix_dic[u1]
        row_pattern_mepwise_sim=pattern_matrix_dic[u1]
        rower_append(u1)
        for u2 in u2_row:
            matrix_general_actual_row_append(row_original_mepwise_sim[u2])
            matrix_pattern_actual_row_append(row_pattern_mepwise_sim[u2])
            if flag_header : 
                header_append(u2)
        flag_header=False
     
        
    header_new={};rower_new={};
    
    for i,h in zip(range(len(header)),header):
        header_new[i]=h
    
    for i,r in zip(range(len(rower)),rower):
        rower_new[i]=r
    
    #header_new=dict((i,h) for (i,h) in zip(range(len(header)),header))
    #rower_new=dict((i,r) for (i,r) in zip(range(len(rower)),rower))
    return matrix_general,matrix_pattern,rower_new,header_new


def get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute,nb_items=None,nb_users=None):
    
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    votes_map_details={};users_map_details={};
    votes_map_details_has_key=votes_map_details.has_key;users_map_details_has_key=users_map_details.has_key
    votes_map_meps={};users_map_votes={}
    users_to_votes_outcomes={};users_to_votes_outcomes_has_key=users_to_votes_outcomes.has_key

    
    ##########################NEW#########################
    voting_keys=set()
    users_keys=set()
    if nb_items is not None and nb_users is not None:
        for d in dataset:        
            voting_keys|={d[vote_id_attributes]}
            users_keys|={d[users_id_attributes]}
        voting_keys=set(sorted(voting_keys)[nb_items:])
        users_keys=set(sorted(users_keys)[nb_users:])
    ##########################NEW#########################
    
    
    for d in dataset:
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if d_vote_id in voting_keys or d_user_id in users_keys:
            continue
        
        d_outcome=d[position_attribute]
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=set()
        votes_map_meps[d_vote_id] |= {d_user_id}
        
        if (not users_to_votes_outcomes_has_key(d_user_id)):
            users_to_votes_outcomes[d_user_id]={}
        users_to_votes_outcomes[d_user_id][d_vote_id]=d_outcome
            
            
        
        
    return votes_map_details,votes_map_meps,users_map_details,users_map_votes,users_to_votes_outcomes

def construct_user_aggregate(all_users_map_details_array,users_attributes,aggregation_attributes,who=''):
    users_aggregated_map_details_dict={}
    user_id_attr=users_attributes[0]
    users_aggregated_map_to_users={};users_aggregated_map_to_users_has_key=users_aggregated_map_to_users.has_key
    boolas=False
    for u in all_users_map_details_array:
        actual_u_id=u[user_id_attr]

        agg_user_identifier=tuple([u[x] for x in aggregation_attributes]) if aggregation_attributes is not None else actual_u_id
        agg_user_identifier='_'.join(agg_user_identifier) if aggregation_attributes is not None else actual_u_id
        if len(agg_user_identifier)==0:
            #agg_user_identifier='agg'+who #######WWORKING URGENT ###############
            agg_user_identifier='agg'
            boolas=True
        considered_aggregation_attributes=users_attributes if aggregation_attributes is None else aggregation_attributes
        if not users_aggregated_map_to_users_has_key(agg_user_identifier):
            users_aggregated_map_to_users[agg_user_identifier]=set()
            users_aggregated_map_details_dict[agg_user_identifier]={att:u[att] if att in considered_aggregation_attributes else agg_user_identifier for att in users_attributes}
            if boolas: 
                users_aggregated_map_details_dict[agg_user_identifier]={att:u[att] if att in considered_aggregation_attributes else agg_user_identifier+who for att in users_attributes if att<>user_id_attr} #new
                users_aggregated_map_details_dict[agg_user_identifier][user_id_attr]=agg_user_identifier
            users_aggregated_map_details_dict[agg_user_identifier]['NB_USERS']=0
        users_aggregated_map_to_users[agg_user_identifier]|={actual_u_id}
        users_aggregated_map_details_dict[agg_user_identifier]['NB_USERS']+=1

    return users_aggregated_map_details_dict,users_aggregated_map_to_users



def compute_aggregates_outcomes(v_ids,u_all_ids,u_agg_ids,users_aggregated_map_details_dict,users_aggregated_map_to_users,users_to_votes_outcomes,users_attributes,outcome_tuple_structure,size_aggregate_min=2,outcome_track={},method_aggregation_outcome='STANDARD',keep_track=False):
    
    #method_aggregation_outcome='AVGRATINGS_PONDERATION'
    
    users_all_ids_visited=set()
    users_aggregated_ids_visited=set()
    size_tuple=len(outcome_tuple_structure)
    range_size_tuple=range(size_tuple)
    users_aggregated_map_votes={}
    users_aggregated_to_votes_outcomes={}
    users_aggregated_to_delete=set()
    
    users_aggregated_map_details_dict_new={}
    users_aggregated_map_to_users_new={}
    users_all_ids_to_preserve=set()
    for u_agg in u_agg_ids:
        u_agg_ids_corresp=users_aggregated_map_to_users[u_agg] & u_all_ids
        size_u_agg=len(u_agg_ids_corresp)
        users_aggregated_ids_visited|={u_agg}
        users_all_ids_visited.update(u_agg_ids_corresp)
        if size_u_agg>=size_aggregate_min:
            users_aggregated_map_details_dict[u_agg]['NB_USERS']=size_u_agg
            
            
            
            u_agg_ids_corresp_tuple=tuple(sorted(u_agg_ids_corresp))
            if keep_track and u_agg_ids_corresp_tuple in outcome_track:
                users_aggregated_to_votes_outcomes[u_agg]=outcome_track[u_agg_ids_corresp_tuple]
                users_aggregated_map_votes[u_agg]=outcome_track[u_agg_ids_corresp_tuple].viewkeys()
            else :
            
                users_aggregated_map_votes[u_agg]=set()
                users_aggregated_to_votes_outcomes[u_agg]={}
                for v in v_ids:
                    #vector_associated=tuple(outcome_tuple_structure)
                    vector_associated=aggregateOutcomeInitialize_DSC(outcome_tuple_structure, method_aggregation_outcome)
                    flag_at_least_someone_voted=False
                    #summi_pond=0.
                    for u in u_agg_ids_corresp:
                        try:
                            v_u=users_to_votes_outcomes[u][v]
                            
                            flag_at_least_someone_voted=True
                            #vector_associated=tuple(vector_associated[i]+v_u[i] for i in range_size_tuple)
                            #####################################NEW PONDERATION#####################################
                            vector_associated=aggregateOutcome_DSC(v_u, vector_associated, method_aggregation_outcome)
                            #if method_aggregation_outcome == 'STANDARD':
                            #    vector_associated=aggregateOutcome_DSC(v_u, vector_associated, method_aggregation_outcome)
                            #    #vector_associated=tuple(vector_associated[i]+v_u[i] for i in range_size_tuple)
                            #else :
                            #    #summi_pond+=ponderations_actu[u]
                            #    all_vectors_associated_append(v_u)
                            #    #vector_associated=(vector_associated[0]+v_u[0]*v_u[1],vector_associated[1]+v_u[1])#tuple(vector_associated[i]+v_u[i]*ponderations_actu[u] for i in range_size_tuple)
                            #####################################NEW PONDERATION#####################################
                        except:
                            continue
                    if flag_at_least_someone_voted:
                        #if method_aggregation_outcome <> 'STANDARD':
                        #    #vector_associated=(vector_associated[0]/vector_associated[1],vector_associated[1]/vector_associated[1])
                        #    vector_associated=aggregateOutcome_DSC(all_vectors_associated, outcome_tuple_structure, method_aggregation_outcome)
                            
                        users_aggregated_to_votes_outcomes[u_agg][v]=aggregateOutcomeFinalize_DSC(vector_associated,method_aggregation_outcome)
                        users_aggregated_map_votes[u_agg]|={v}
                if keep_track:
                    outcome_track[u_agg_ids_corresp_tuple]=users_aggregated_to_votes_outcomes[u_agg]
                
            users_aggregated_map_details_dict_new[u_agg]=users_aggregated_map_details_dict[u_agg]
            users_aggregated_map_to_users_new[u_agg]=u_agg_ids_corresp
            users_all_ids_to_preserve|=u_agg_ids_corresp
        else :
            users_aggregated_to_delete|={u_agg}
            
    users_aggregated_to_preserve=users_aggregated_map_to_users.viewkeys()-users_aggregated_to_delete

    return users_aggregated_map_details_dict_new.values(),users_aggregated_map_to_users_new,users_aggregated_map_votes,users_aggregated_to_votes_outcomes,users_all_ids_to_preserve,users_aggregated_to_preserve,users_all_ids_visited,users_aggregated_ids_visited



def compute_similarity_matrix(users1_to_votes_outcomes,users2_to_votes_outcomes,votes_ids,users1_ids,users2_ids,method,issquare=False):
    similarity_matrix={}
    #issquare=users1_ids==users2_ids
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            if issquare :
                if user2<=user1:
                    similarity_matrix[user1][user2]=similarity_vector_measure_dcs(votes_ids,users1_to_votes_outcomes[user1],users2_to_votes_outcomes[user2],user1,user2,method)
            else :
                similarity_matrix[user1][user2]=similarity_vector_measure_dcs(votes_ids,users1_to_votes_outcomes[user1],users2_to_votes_outcomes[user2],user1,user2,method)
            
    if issquare:
        for user1 in users1_ids:
            for user2 in users2_ids:
                if user2<user1:
                    similarity_matrix[user2][user1]=similarity_matrix[user1][user2]
    return similarity_matrix




def compute_similarity_memory_lowerbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison,bound,votes_map_ponderations={}):
    votes_map_ponderations_get=votes_map_ponderations.get
    ponderate=True if len(votes_map_ponderations)>0 else False
    
    if bound==1:
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        for key in votes_ids:#in votes_ids:
            try:
                #v_pair=pairs[key]
                #nbvotes+=1
                v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
                nbvotes+=votes_map_ponderations_get(key,1.)
                similarity+=v_pair 
            except:
                continue
        bound=max((threshold_comparaison-(nbvotes-similarity))/threshold_comparaison,0); 
    else :
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append;
       
        for key in votes_ids:#in votes_ids:
            try:
                #v_pair=pairs[key]
                #nbvotes+=1
                
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
                
                if ponderate:pairs_sim_array=sorted(pairs_sim_array,key=itemgetter(0))
                else:pairs_sim_array=sorted(pairs_sim_array)
            for k in range(int(threshold_comparaison)):
                if ponderate:
                    bound+=pairs_sim_array[k][0]*pairs_sim_array[k][1]
                    nbs_votes_with_ponds+=pairs_sim_array[k][1]
                else:
                    bound+=pairs_sim_array[k]
            
            if ponderate: bound/=float(nbs_votes_with_ponds) 
            else: bound/=float(threshold_comparaison)
    return similarity,nbvotes,bound


def compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison,bound,votes_map_ponderations={}):
    votes_map_ponderations_get=votes_map_ponderations.get
    ponderate=True if len(votes_map_ponderations)>0 else False
    if bound==1:
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        for key in votes_ids:#in votes_ids:
            try:
                #v_pair=pairs[key]
                #nbvotes+=1
                
                v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
                nbvotes+=votes_map_ponderations_get(key,1.)
                similarity+=v_pair 

            except:
                continue
        bound=min(float(similarity)/float(threshold_comparaison),1.); 
        #print bound
        
    else :
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append
        for key in votes_ids:
            try:
                #v_pair=pairs[key]
                #nbvotes+=1
                
                v_pair=pairs[key]*votes_map_ponderations_get(key,1.)
                nbvotes+=votes_map_ponderations_get(key,1.)
                similarity+=v_pair 
                #insort_left(pairs_sim_array,v_pair)
                if ponderate: pairs_sim_array_append((pairs[key],votes_map_ponderations[key]))
                else:pairs_sim_array_append(v_pair)
            except:
                continue
        #bound=min(similarity/threshold_comparaison,1); 
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
            if ponderate: bound/=float(nbs_votes_with_ponds) 
            else: bound/=float(threshold_comparaison)
    return similarity,nbvotes,bound




def compute_similarity_memory_with_bounds(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison,lower,bound,votes_map_ponderations={}):
    if lower:
        return compute_similarity_memory_lowerbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison,bound,votes_map_ponderations)
    else :
        return compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison,bound,votes_map_ponderations)


def compute_similarity_matrix_memory_is_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison,lower,bound,votes_map_ponderations={}):
    
    similarity_matrix={}
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            if user2<=user1: similarity_matrix[user1][user2]=compute_similarity_memory_with_bounds(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison,lower,bound,votes_map_ponderations)
            #if user2<=user1: similarity_matrix[user1][user2]=compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison)
    for user1 in users1_ids:
        for user2 in users2_ids:
            if user2<user1: similarity_matrix[user2][user1]=similarity_matrix[user1][user2]
    return similarity_matrix

def compute_similarity_matrix_memory_is_not_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison,lower,bound,votes_map_ponderations={}):
    similarity_matrix={}
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            similarity_matrix[user1][user2]=compute_similarity_memory_with_bounds(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison,lower,bound,votes_map_ponderations)
            #similarity_matrix[user1][user2]=compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison)
    return similarity_matrix

def compute_similarity_matrix_memory_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,issquare=False,threshold_comparaison=1,lower=True,bound=1,votes_map_ponderations={}):
    if issquare:
        return compute_similarity_matrix_memory_is_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison,lower,bound,votes_map_ponderations)
    else :
        return compute_similarity_matrix_memory_is_not_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison,lower,bound,votes_map_ponderations)


#####################ENUMERATOR OF PEERS#########################
#Returns the set of users g1,g2 (by intention) which allow the computation the remaining part of the algorithm

#################################################################


def compute_aggregate_choosen(users_attributes,
                            users_map_details_array_filtered_user1,
                            users_map_details_array_filtered_user2,
                            aggregationAttributes_user1,
                            aggregationAttributes_user2,
                            all_users_to_votes_outcomes,
                            u1_p_set_users,
                            u2_p_set_users,
                            all_votes_id,
                            votes_id_reference,
                            votes_id_pattern,
                            nb_aggregation_min_user1,
                            nb_aggregation_min_user2,
                            outcome_tuple_structure,
                            comparaison_measure,
                            qualityMeasure,
                            threshold_pair_comparaison,
                            users_aggregated_track,
                            keep_track_of_visited_aggregate):
    
    
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    
    users1_mappy={tuple(sorted(x & u1_p_set_users)) for x in users1_aggregated_map_to_users.values()}
    users2_mappy={tuple(sorted(x & u2_p_set_users)) for x in users2_aggregated_map_to_users.values()}
    users1_mappy=set(filter(len,users1_mappy))
    users2_mappy=set(filter(len,users2_mappy))
    #print aggregationAttributes_user1,users1_mappy,users2_mappy
    for aw in keep_track_of_visited_aggregate:
        if users1_mappy==aw[0] and users2_mappy==aw[1]:
            return None,None
    
    keep_track_of_visited_aggregate.append([users1_mappy,users2_mappy])
    
    
#     print aggregationAttributes_user1
#     print users1_mappy
#     print users2_mappy
#     raw_input('...')
    
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    
    users1_aggregated_map_details_array_pattern,\
    users1_aggregated_map_to_users_pattern,\
    users1_aggregated_map_votes_pattern,\
    users1_aggregated_to_votes_outcomes_pattern,\
    users1_all_ids_to_preserve,\
    users1_aggregated_to_preserve,\
    users1_all_ids_visited,\
    users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,
                                                              u1_p_set_users,
                                                              users1_agg_ids, 
                                                              users1_aggregated_map_details,
                                                              users1_aggregated_map_to_users, 
                                                              all_users_to_votes_outcomes, 
                                                              users_attributes,outcome_tuple_structure,
                                                              size_aggregate_min=nb_aggregation_min_user1
                                                              ,outcome_track=users_aggregated_track)

    users2_aggregated_map_details_array_pattern,\
    users2_aggregated_map_to_users_pattern,\
    users2_aggregated_map_votes_pattern,\
    users2_aggregated_to_votes_outcomes_pattern,\
    users2_all_ids_to_preserve,\
    users2_aggregated_to_preserve,\
    users2_all_ids_visited,\
    users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,
                                                              u2_p_set_users,
                                                              users2_agg_ids, 
                                                              users2_aggregated_map_details,
                                                              users2_aggregated_map_to_users, 
                                                              all_users_to_votes_outcomes, 
                                                              users_attributes,
                                                              outcome_tuple_structure,
                                                              size_aggregate_min=nb_aggregation_min_user2,
                                                              outcome_track=users_aggregated_track)
    
    nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
    
    threshold_pair_comparaison_dims=1
    reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,votes_id_reference,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
    e_config={'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern}
    users1_ids_set,users2_ids_set,flag_continue=get_users_validating_pairwise_threshold(e_config, votes_id_pattern, users1_aggregated_to_preserve, users2_aggregated_to_preserve, threshold_pair_comparaison_dims, issquare=False)
    pattern_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,votes_id_pattern,users1_ids_set,users2_ids_set,comparaison_measure)
    if len(pattern_matrix_dic)==0: return None,None
        
    reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
    
    for i in range(len(pattern_matrix)):
        for j in range(len(pattern_matrix[i])):
            pattern_matrix[i][j]=pattern_matrix[i][j]+(1.,)
    
    quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison_dims,qualityMeasure,coeff=lambda x : 1/float(nb_users_voted))
    
    
    #threshold_pair_comparaison
    pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison_dims else float('nan') for col in row] for row in pattern_matrix],rower,header)
    reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison_dims else float('nan') for col in row] for row in reference_matrix],rower,header)
    dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                    
    return dataset_stats,quality


def enumerate_aggregations_in_results(interesting_patterns,
                            users_attributes,
                            users_map_details_array_filtered_user1,
                            users_map_details_array_filtered_user2,
                            aggregationAttributes_user2,
                            all_users_to_votes_outcomes,
                            all_votes_id,
                            votes_id_reference,
                            nb_aggregation_min_user1,
                            nb_aggregation_min_user2,
                            outcome_tuple_structure,
                            comparaison_measure,
                            qualityMeasure,
                            threshold_pair_comparaison,
                            users_aggregated_track):
    
    
    
    new_interesting_pattern=[];new_interesting_pattern_append=new_interesting_pattern.append
    
    
    keep_track_of_visited_aggregate=[]
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,votes_id_pattern,uall1,uall2,review_agg in sorted(interesting_patterns,key = itemgetter(3),reverse=True):
        users_attributes_to_pick_from=['NATIONAL_PARTY','AGEGROUP','GENDER','NAME_FULL']
        #users_attributes_to_pick_from=["ageGroup","gender","occupation"]#users_attributes
        enum=enumerator_complex_cbo_init_new_config([{'attr':x} for x in users_attributes_to_pick_from],[
                {'name':'attr', 'type':'nominal'},                                                  
            ],threshold=1,verbose=False)
        
        
        enum=enumerator_nominal_bottom_up(users_attributes_to_pick_from, [], 0)
        for pat_agg in enum:
            pat_agg=[pat_agg]
        #for pat_agg,xlabel,e_config in enum:
            aggregationAttributes_user1_now=aggregationAttributes_user2_now=pat_agg[0]
            dataset_stats_ret,quality_ret=compute_aggregate_choosen(users_attributes,
                                users_map_details_array_filtered_user1,
                                users_map_details_array_filtered_user2,
                                aggregationAttributes_user1_now,
                                aggregationAttributes_user2_now,
                                all_users_to_votes_outcomes,
                                uall1,
                                uall2,
                                all_votes_id,
                                votes_id_reference,
                                votes_id_pattern,
                                nb_aggregation_min_user1,
                                nb_aggregation_min_user2,
                                outcome_tuple_structure,
                                comparaison_measure,
                                qualityMeasure,
                                threshold_pair_comparaison,
                                users_aggregated_track,
                                keep_track_of_visited_aggregate)
            if dataset_stats_ret is None :
                continue
            
            new_interesting_pattern_append([p,label,dataset_stats_ret,quality_ret,borne_max_quality,aggregationAttributes_user1_now,votes_id_pattern,uall1,uall2,review_agg])
    return sorted(new_interesting_pattern,key = itemgetter(3),reverse=True)      
            #yield p,label,dataset_stats_ret,quality_ret,borne_max_quality,aggregationAttributes_user1_now

              

def enumerator_pair_of_users(users_map_details_array_filtered_user1,
                             users_map_details_array_filtered_user2,
                             all_users_to_votes_outcomes,
                             all_votes_id,
                             users1_agg_ids,
                             users2_agg_ids,
                             users1_aggregated_map_details,
                             users2_aggregated_map_details,
                             users1_aggregated_map_to_users,
                             users2_aggregated_map_to_users,
                             users_attributes,
                             subattributes_details_users,
                             threshold_nb_users_1,
                             threshold_nb_users_2,
                             nb_aggregation_min_user1,
                             nb_aggregation_min_user2,
                             outcome_tuple_structure,
                             vector_of_outcome,
                             users_aggregated_track,
                             interesting_pattern_dic,
                             closed,
                             how_much_visited,
                             method_aggregation_outcome,
                             only_square_matrix=False): #how_much_visited:{visited:<number>}
    

    users_id_attribute=users_attributes[0]
    get_users_ids = partial(map,itemgetter(users_id_attribute))

#     elem={
#         'u1_config':1,
#         'u2_config':2,
#         'u1_p':1,
#         'u2_p':2
#     }
    
    ############################NEW PONDERATION##################################
    #global ponderate
    ponderate=vector_of_outcome is not None#'nb_users' in users_attributes;
    #nb_users_attr='nb_users';ponderations_u1=None;ponderations_u2=None
    ############################NEW PONDERATION##################################
    
    index_u1_visited=0;index_all_u1_visited=0
    index_u2_visited=0;index_all_u2_visited=0
    get_actual_top_k_users_1_full_ids = partial(map,itemgetter(7))
    get_actual_top_k_users_2_full_ids = partial(map,itemgetter(8))
    if closed:
        enum_u1=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1,bfs=False,do_heuristic=False)
    else:
        enum_u1=enumerator_complex_from_dataset_new_config(users_map_details_array_filtered_user1, subattributes_details_users, {},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_1,verbose=False)
            
    
    
    
    visited_1_trace_map={}
    lvl_users_part=0
    
#     if only_square_matrix:
#         for u1_p,u1_label,u1_config in enum_u1:
#             index_u1_visited+=1
#             u1_p_tuple_users=tuple(get_users_ids(u1_config['support']))
#             u1_p_set_users=set(u1_p_tuple_users)
#             users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)
#             if len(users1_aggregated_to_preserve)==0:
#                     u1_config['flag']=False
#                     continue
#         users_1_infos=(u1_p,
#                        u1_label,
#                        users1_all_ids_to_preserve,
#                        users1_aggregated_to_preserve,
#                        users1_aggregated_map_votes_pattern,
#                        users1_aggregated_to_votes_outcomes_pattern,
#                        u1_config)
#         users_2_infos=(u1_p,
#                        u1_label,
#                        users1_all_ids_to_preserve,
#                        users1_aggregated_to_preserve,
#                        users1_aggregated_map_votes_pattern,
#                        users1_aggregated_to_votes_outcomes_pattern,
#                        u1_config)
#         yield users_1_infos,users_2_infos
            
    #else: ####USUAL !!
    for u1_p,u1_label,u1_config in enum_u1:
        index_u1_visited+=1
        u1_p_tuple_users=tuple(get_users_ids(u1_config['support']))
        
        
        u1_p_set_users=set(u1_p_tuple_users)
        
        
        users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)
        
        
        if len(users1_aggregated_to_preserve)==0:
                u1_config['flag']=False
                continue
        if True:
            if not u1_p_tuple_users in visited_1_trace_map:
                visited_1_trace_map[u1_p_tuple_users]=set()
        if closed:
            enum_u2=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_2,bfs=False,do_heuristic=False)
        else:
            enum_u2=enumerator_complex_from_dataset_new_config(users_map_details_array_filtered_user2, subattributes_details_users, {},objet_id_attribute=users_id_attribute,threshold=threshold_nb_users_2,verbose=False)
            
        for u2_p,u2_label,u2_config in enum_u2: 
            #print u1_p,"......................",u2_p
            # if u2_p==u1_p:
            #     u2_config['flag']=False
            if only_square_matrix and u2_p<>u1_p:continue
            index_u2_visited+=1
            u2_p_tuple_users=tuple(get_users_ids(u2_config['support']))
            u2_p_set_users=set(u2_p_tuple_users)
            if True: 

                if (u2_p_tuple_users in visited_1_trace_map and u1_p_tuple_users in visited_1_trace_map[u2_p_tuple_users]) :#or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
                        continue
                else :
                    visited_1_trace_map[u1_p_tuple_users]|={u2_p_tuple_users}  
            
            
            users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            
            if len(users2_aggregated_to_preserve)==0:
                u2_config['flag']=False
                continue
            if nb_users_voted==0:continue
            users_1_infos=(u1_p,
                           u1_label,
                           users1_all_ids_to_preserve,
                           users1_aggregated_to_preserve,
                           users1_aggregated_map_votes_pattern,
                           users1_aggregated_to_votes_outcomes_pattern,
                           u1_config)
            users_2_infos=(u2_p,
                           u2_label,
                           users2_all_ids_to_preserve,
                           users2_aggregated_to_preserve,
                           users2_aggregated_map_votes_pattern,
                           users2_aggregated_to_votes_outcomes_pattern,
                           u2_config)
            
            ##############
            
            couple_ressemblance=0
            if False :
                top_k_actu_users1=get_actual_top_k_users_1_full_ids(interesting_pattern_dic['interestingPatterns'])
                top_k_actu_users2=get_actual_top_k_users_2_full_ids(interesting_pattern_dic['interestingPatterns'])
                top_k_actu_users1_ressemblance=[(ressemblance(x,users1_all_ids_to_preserve)+ressemblance(x,users2_all_ids_to_preserve))/2. for x in top_k_actu_users1]
                top_k_actu_users2_ressemblance=[(ressemblance(x,users1_all_ids_to_preserve)+ressemblance(x,users2_all_ids_to_preserve))/2. for x in top_k_actu_users2]
                
                couple_ressemblance=1-sum([(x+y)/2.for x,y in zip(top_k_actu_users1_ressemblance,top_k_actu_users2_ressemblance)])/len(top_k_actu_users1_ressemblance) if len(top_k_actu_users1_ressemblance)>0 else 1.
                
                
                #ressemblance_u1=sum([(ressemblance(x,users1_all_ids_to_preserve)) for x in top_k_actu_users1])/len(top_k_actu_users1)   if len(top_k_actu_users1)>0. else 0.  
                #ressemblance_u2=sum([(ressemblance(x,users2_all_ids_to_preserve)) for x in top_k_actu_users2])/len(top_k_actu_users1)   if len(top_k_actu_users2)>0. else 0.      
                #print couple_ressemblance
            
                print couple_ressemblance
                #if random()<=couple_ressemblance:
                yield users_1_infos,users_2_infos
            else :
            ##############
                yield users_1_infos,users_2_infos
        index_all_u2_visited+=u2_config['nb_visited'][0]
    index_all_u1_visited+=u1_config['nb_visited'][0]
    visited=(index_all_u2_visited-index_u2_visited)+(index_all_u1_visited-index_u1_visited)
    how_much_visited['visited']=visited       
            
def enumerator_pair_of_usersXX(users_map_details_array_filtered_user1,
                             users_map_details_array_filtered_user2,
                             all_users_to_votes_outcomes,
                             all_votes_id,
                             users1_agg_ids,
                             users2_agg_ids,
                             users1_aggregated_map_details,
                             users2_aggregated_map_details,
                             users1_aggregated_map_to_users,
                             users2_aggregated_map_to_users,
                             users_attributes,
                             subattributes_details_users,
                             threshold_nb_users_1,
                             threshold_nb_users_2,
                             nb_aggregation_min_user1,
                             nb_aggregation_min_user2,
                             outcome_tuple_structure,
                             users_aggregated_track,
                             interesting_pattern_dic):
    
    get_actual_top_k_users_1_full_ids = partial(map,itemgetter(7))
    get_actual_top_k_users_2_full_ids = partial(map,itemgetter(8))
    users_id_attribute=users_attributes[0]
    get_users_ids = partial(map,itemgetter(users_id_attribute))
    users_config_diversity=[];users_config_diversity_append=users_config_diversity.append
    
    get_qualities = partial(map,itemgetter('quality'))
    
    enum_u1=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1,bfs=True)
    
    visited_1_trace_map={}
    lvl_users_part=0
    actual_lvl_1=0
    actual_lvl_2=actual_lvl_1
    new_enum_for_u2=users_map_details_array_filtered_user2
    new_enum_for_u1=users_map_details_array_filtered_user1
    TRUBADOR=False
    flaggy=False
    do_heuristic=True
    users_config_diversity_pos=None
    while True:
        try:
            if not flaggy:
                u1_p,u1_label,u1_config=next(enum_u1)
            else :
                flaggy=False
            if TRUBADOR:    
                if u1_p<>users_config_diversity_pos['u1_p']:
                    enum_u1=enumerator_complex_cbo_init_new_config(users_config_diversity_pos['u1_config']['support'], subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1,bfs=True)
                    actual_lvl_1=0
                    TRUBADOR=False
                    continue
            
            if not u1_config['flag']:
                continue     
            u1_p_tuple_users=tuple(get_users_ids(u1_config['support']))
            u1_p_set_users=set(u1_p_tuple_users)
            users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track)
            if len(users1_aggregated_to_preserve)==0:
                    u1_config['flag']=False
                    continue
            if not u1_p_tuple_users in visited_1_trace_map:
                visited_1_trace_map[u1_p_tuple_users]=set()
            
            #enum_u2=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_2,bfs=True)
            enum_u2=enumerator_complex_cbo_init_new_config(new_enum_for_u2, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_2,bfs=True)
        except:
            break
        for u2_p,u2_label,u2_config in enum_u2: 
            
            u2_p_tuple_users=tuple(get_users_ids(u2_config['support']))
            u2_p_set_users=set(u2_p_tuple_users)
            if (u2_p_tuple_users in visited_1_trace_map and u1_p_tuple_users in visited_1_trace_map[u2_p_tuple_users]) :#or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
                    continue
            else :
                visited_1_trace_map[u1_p_tuple_users]|={u2_p_tuple_users}
            if actual_lvl_2<>u2_config['lvl'] or actual_lvl_1<>u1_config['lvl']:
                actual_lvl_1=u1_config['lvl']
                actual_lvl_2=u2_config['lvl']  
                if do_heuristic:
                    lvl_users_part+=1
                    flaggy=False
                    qualities=get_qualities(users_config_diversity)
                    sum_quality_all=sum(qualities)
                    if sum_quality_all>0:
                        qualities=map(lambda x : x/sum_quality_all,qualities)
                        for ind in range(1,len(qualities)):
                            qualities[ind]+=qualities[ind-1]
                        rn=random()
                        pos=binary_search(qualities,rn)
                        users_config_diversity_pos=users_config_diversity[pos]
                        new_enum_for_u2=users_config_diversity_pos['u2_config']['support']
                        print ''
                        print pos,users_config_diversity_pos['u1_p'],users_config_diversity_pos['u2_p']
                        print ''
                        for i in range(len(users_config_diversity)):
                            if i<>pos :
                                users_config_diversity_i=users_config_diversity[i]
                                users_config_diversity_i['u1_config']['flag']=False if users_config_diversity_i['u1_p']<>users_config_diversity_pos['u1_p'] else True
                                users_config_diversity_i['u2_config']['flag']=False

                        
                        users_config_diversity=[]
                        users_config_diversity_append=users_config_diversity.append
                        
                        #break
                
                        
                        if u1_p<>users_config_diversity_pos['u1_p']:
                            flaggy=True
                            enum_u1=enumerator_complex_cbo_init_new_config(users_config_diversity_pos['u1_config']['support'], subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1,bfs=True)
                            actual_lvl_1=0
                            break                        
                        if u2_p<>users_config_diversity_pos['u2_p']:
                            TRUBADOR=True
                            continue     
                ################################################################
                 
                
            
#             actual_lvl_1=u1_config['lvl']
#             actual_lvl_2=u2_config['lvl']    
            users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track)
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            if len(users2_aggregated_to_preserve)==0:
                u2_config['flag']=False
                continue
            
            users_1_infos=(u1_p,
                           u1_label,
                           users1_all_ids_to_preserve,
                           users1_aggregated_to_preserve,
                           users1_aggregated_map_votes_pattern,
                           users1_aggregated_to_votes_outcomes_pattern,
                           u1_config)
            users_2_infos=(u2_p,
                           u2_label,
                           users2_all_ids_to_preserve,
                           users2_aggregated_to_preserve,
                           users2_aggregated_map_votes_pattern,
                           users2_aggregated_to_votes_outcomes_pattern,
                           u2_config)
            
            yield users_1_infos,users_2_infos
            
            ##############
            couple_ressemblance=0
            if do_heuristic:
                
                top_k_actu_users1=get_actual_top_k_users_1_full_ids(interesting_pattern_dic['interestingPatterns'])
                top_k_actu_users2=get_actual_top_k_users_2_full_ids(interesting_pattern_dic['interestingPatterns'])
                top_k_actu_users1_ressemblance=[(ressemblance(x,users1_all_ids_to_preserve)+ressemblance(x,users2_all_ids_to_preserve))/2. for x in top_k_actu_users1]
                top_k_actu_users2_ressemblance=[(ressemblance(x,users1_all_ids_to_preserve)+ressemblance(x,users2_all_ids_to_preserve))/2. for x in top_k_actu_users2]
                couple_ressemblance=1-sum([(x+y)/2.for x,y in zip(top_k_actu_users1_ressemblance,top_k_actu_users2_ressemblance)])/len(top_k_actu_users1_ressemblance) if len(top_k_actu_users1_ressemblance)>0 else 0.
                #ressemblance_u1=sum([(ressemblance(x,users1_all_ids_to_preserve)) for x in top_k_actu_users1])/len(top_k_actu_users1)   if len(top_k_actu_users1)>0. else 0.  
                #ressemblance_u2=sum([(ressemblance(x,users2_all_ids_to_preserve)) for x in top_k_actu_users2])/len(top_k_actu_users1)   if len(top_k_actu_users2)>0. else 0.      
                users_config_diversity_append({
                    'quality':couple_ressemblance,
                    'u1_config':u1_config,
                    'u2_config':u2_config,
                    'u1_p':u1_p,
                    'u2_p':u2_p,
                })



def get_users_validating_pairwise_threshold(e_config,v_ids,users1_aggregated_to_preserve,users2_aggregated_to_preserve,threshold_pair_comparaison,issquare):
       
    e_users_1=e_config['users1']
    e_users_2=e_config['users2']
    flag_continue=False
    new_e_users_1={}
    users1_ids_set=set()
    users2_ids_set=set()
    max_votes_pairwise=0
    for key in e_users_1:
        value=e_users_1[key]
        votes_user=(value & v_ids)
        len_votes_user=len(votes_user)
        if len_votes_user>=threshold_pair_comparaison:
            new_e_users_1[key]=votes_user
            users1_ids_set|={key}
            max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
      
    e_config['users1']=new_e_users_1   
      
    if max_votes_pairwise<threshold_pair_comparaison :
        e_config['flag']=False
        flag_continue=True
        return users1_ids_set,users2_ids_set,flag_continue
      
    if issquare :
        new_e_users_2=new_e_users_1
        users2_ids_set=users1_ids_set
    else :
        new_e_users_2={}
        users2_ids_set=set()
        max_votes_pairwise=0
        for key in e_users_2:
            value=e_users_2[key]
            votes_user=(value & v_ids)
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                new_e_users_2[key]=votes_user
                users2_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
      
    e_config['users2']=new_e_users_2  
    if max_votes_pairwise<threshold_pair_comparaison :
        e_config['flag']=False
        flag_continue=True
        return users1_ids_set,users2_ids_set,flag_continue
    users1_ids_set=users1_aggregated_to_preserve & users1_ids_set
    users2_ids_set=users2_aggregated_to_preserve & users2_ids_set      
    return users1_ids_set,users2_ids_set,flag_continue





def DSC(dataset,attributes,configuration,items_scope,referential_scope,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    ##########################TODO######################################
    #1. Find a way to dynamically compute aggregate of users without a great overhead which is the cas now
    #2. Is there a way to explore less patterns by using the fade first aproach (selecting the candidate description that lend the minimum poissible support
    #3. Is there a way to reverse the way of enumeration to exploit the upper bound over all the three-set
    #4. Find an upper bound that is more tight than the two others (the infamous one that compute a maximum of sum rather than max by one but has a giant overhead)
    #5. Use sampling method and select smartly the three sets parts (ressemblance, cover, adventage diversity and exploitation. MCTS ?) 
    ####################################################################
    
    
    
    initialization=time()
    timing=0;ends=0
    nb_patterns=0
    interesting_patterns=[]
    elementToShow=votes_attributes[1] if len(votes_attributes)>2 else votes_attributes[0]
    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    how_much_visited={'visited':0}
    compute_agg_reviews=False
    
    ###################PARAMETERS_COMPUTING###################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold
    if quality_threshold==0:quality_threshold=0.0000001
    pruning = configuration.get('pruning',False)
    closed = configuration.get('closed',True)
    bound_1_2=configuration.get('upperbound',1)
    qualityMeasure=configuration['iwant']
    
    lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False

    comparaison_measure=configuration['comparaison_measure']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',[users_attributes[0]])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',[users_attributes[0]])
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    threshold_nb_users_1=configuration.get('threshold_nb_users_1',1)
    threshold_nb_users_2=configuration.get('threshold_nb_users_2',1)
    vector_of_outcome=configuration.get('vector_of_outcome',None)
   
    nb_items_to_study=configuration.get('nb_items',None)
    nb_users_to_study=configuration.get('nb_users',None)
    method_aggregation_outcome=configuration.get('method_aggregation_outcome','STANDARD')
    ponderate_by_user=configuration.get('ponderate_by_user',None)
    ponderate_by_item=configuration.get('ponderate_by_item',None)
    
    
    only_square_matrix=configuration.get('only_square_matrix',False)    
    
    ###################PARAMETERS_COMPUTING###################
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    get_votes_ids = partial(map,itemgetter(vote_id_attribute))
    get_users_ids = partial(map,itemgetter(users_id_attribute))
    
    
    #############NEW#########################################
    reviews_dataset=configuration['reviews_dataset']
    new_review_dataset=[]
    items_dataset=configuration['items_dataset']
    users_dataset=configuration['users_dataset']
    items_ids_to_remove=set(sorted(get_votes_ids(items_dataset))[nb_items_to_study:]) if nb_items_to_study is not None else set()
    users_ids_to_remove=set(sorted(get_users_ids(users_dataset))[nb_users_to_study:]) if nb_users_to_study is not None else set()
    all_users_to_votes_outcomes={}#x[users_id_attribute]:{} for x in reviews_dataset}
    
    
    for row in reviews_dataset:
        v_id_rev=row[vote_id_attribute]
        u_id_rev=row[users_id_attribute]
        if v_id_rev in items_ids_to_remove or u_id_rev in users_ids_to_remove:
            continue
        pos_rev=row[position_attribute]
        new_review_dataset.append(row)
        if u_id_rev not in all_users_to_votes_outcomes:
            all_users_to_votes_outcomes[u_id_rev]={}
        all_users_to_votes_outcomes[u_id_rev][v_id_rev]=pos_rev
    items_dataset=[i for i in items_dataset if i[vote_id_attribute] not in items_ids_to_remove]    
    users_dataset=[i for i in users_dataset if i[users_id_attribute] not in users_ids_to_remove]
    
    #############NEW#########################################
    

    ######################"Scope over items and referential"#############################
    if len(referential_scope)>0:
        votes_map_details_array_for_reference=filter_pipeline_obj(items_dataset, referential_scope)[0]#filter_pipeline_obj(dataset, referential_scope)[0]
        votes_id_reference=set(get_votes_ids(votes_map_details_array_for_reference)) 
 
    #dataset=filter_pipeline_obj(dataset, items_scope)[0]
    
    #####################################################################################
    
    
    #votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,rev_all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    
    
    
    votes_map_details_array=items_dataset#votes_map_details.values()
    
    votes_map_details_from_array={row[vote_id_attribute]:row for row in votes_map_details_array}
    users_map_details_from_array={row[users_id_attribute]:row for row in users_dataset}
    ############################PONDERATIONS##########################################
    #ponderate_by_item=None
    votes_map_ponderations={}
    #users_map_ponderations={}
    if ponderate_by_item is not None:
        votes_map_ponderations={k:float(votes_map_details_from_array[k][ponderate_by_item]) for k in votes_map_details_from_array}
#     if ponderate_by_user is not None:
#         users_map_ponderations={k:float(users_map_details_from_array[k][ponderate_by_user]) for k in users_map_details_from_array}
    #print next(votes_map_ponderations.iteritems())
    ############################PONDERATIONS##########################################
    
    ######################"Scope over items and referential"#############################
    votes_map_details_array=filter_pipeline_obj(votes_map_details_array, items_scope)[0]
    
    scope_votes_id=set(get_votes_ids(votes_map_details_array))
    ######################"Scope over items and referential"#############################
    
    all_votes_id= set(get_votes_ids(items_dataset))#set(votes_map_details.keys())
    
    ######################"Scope over items and referential"#############################
    if len(referential_scope)==0:
        votes_id_reference=set(get_votes_ids(votes_map_details_array)) 
    ######################"Scope over items and referential"#############################
    
    all_users_map_details_array=users_dataset#all_users_map_details.values()
    outcome_tuple_structure=list(all_users_to_votes_outcomes.values()[0].values()[0])#list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1,who='1')
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2,who='2')
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users_aggregated_track={}
    
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)

    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)
    
    
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    #reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure,issquare=(users1_all_ids_to_preserve==users2_all_ids_to_preserve))
    
    
    users_map_details_array_filtered_user1=sorted([row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve],key=itemgetter(users_id_attribute))
    users_map_details_array_filtered_user2=sorted([row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve],key=itemgetter(users_id_attribute))
    
    
    
    if False:
        map_details={votes_map_details_from_array[v_id][elementToShow]:{elementToShow:votes_map_details_from_array[v_id][elementToShow]} for v_id in votes_map_details_from_array}
        for v_id,v_value in votes_map_details_from_array.iteritems():
            map_details[v_value[elementToShow]]['NB_VOTES']=map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
    
    
    index_visited=0
    
    get_0_items=partial(map,itemgetter(0))
    get_actual_top_k_users_1_full_ids = partial(map,itemgetter(7))
    get_actual_top_k_users_2_full_ids = partial(map,itemgetter(8))
    get_doss = partial(map,itemgetter(elementToShow))
    
    lvl_users_part=0
    initialization=time()-initialization
    st=time() 
    interesting_patterns_dic={'interestingPatterns':interesting_patterns}
    enum_pair_of_users=enumerator_pair_of_users(users_map_details_array_filtered_user1,
                             users_map_details_array_filtered_user2,
                             all_users_to_votes_outcomes,
                             all_votes_id,
                             users1_agg_ids,
                             users2_agg_ids,
                             users1_aggregated_map_details,
                             users2_aggregated_map_details,
                             users1_aggregated_map_to_users,
                             users2_aggregated_map_to_users,
                             users_attributes,
                             subattributes_details_users,
                             threshold_nb_users_1,
                             threshold_nb_users_2,
                             nb_aggregation_min_user1,
                             nb_aggregation_min_user2,
                             outcome_tuple_structure,
                             vector_of_outcome,
                             users_aggregated_track,
                             interesting_patterns_dic,
                             closed,
                             how_much_visited,
                             method_aggregation_outcome,only_square_matrix=only_square_matrix)
    
    
    
    
    #initConfig=next(enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {},threshold=threshold_pair_comparaison,verbose=False,bfs=False,do_heuristic=False,initValues=None))[2]
    
    initConfig={'config':None,'attributes':None}
    for (u1_p,u1_label,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,u1_config),(u2_p,u2_label,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,u2_config) in enum_pair_of_users:
            
            issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            
            reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,votes_id_reference,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
            reference_updated=False
            
            if closed:
                enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},threshold=threshold_pair_comparaison,verbose=False,bfs=False,do_heuristic=False,initValues=initConfig)
            else:
                enumerator_contexts=enumerator_complex_from_dataset_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},objet_id_attribute=vote_id_attribute,threshold=threshold_pair_comparaison,verbose=False)
            


            userpairssimsdetails={}
            for u1 in users1_aggregated_to_preserve:
                userpairssimsdetails[u1]={}
                for u2 in users2_aggregated_to_preserve:
                    userpairssimsdetails[u1][u2]={}
                    for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys():
                        simi_u1_u2=similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],u1,u2,comparaison_measure)[0]
                        userpairssimsdetails[u1][u2][v]=simi_u1_u2
            reference_matrix_dic
            #print u1,u2,userpairssimsdetails
            # print u1_p,u2_p,userpairssimsdetails
            # for xxx in sorted(users1_aggregated_to_votes_outcomes_pattern['agg']):
            #     print xxx,' ',users1_aggregated_to_votes_outcomes_pattern['agg'][xxx]
            # print '     '           
            # for xxx in sorted(users2_aggregated_to_votes_outcomes_pattern['agg']):
            #     print xxx,' ',users2_aggregated_to_votes_outcomes_pattern['agg'][xxx]
            # #print users2_aggregated_to_votes_outcomes_pattern[u1]
            # raw_input('....')
            
            for e_p,e_label,e_config in enumerator_contexts:
                index_visited+=1
                v_ids=set()
                e_u_p=(e_p,u1_p,u2_p)
                e_u_label=(e_label,u1_label,u2_label)
                e_votes=e_config['support']
         

                v_ids=set(get_votes_ids(e_votes))
                dossiers_ids=set()
                #dossiers_ids=set(get_doss(e_votes))
                    
                users1_ids_set,users2_ids_set,flag_continue=get_users_validating_pairwise_threshold(e_config, v_ids, users1_aggregated_to_preserve, users2_aggregated_to_preserve, threshold_pair_comparaison, issquare)
                if flag_continue: 
                    e_config['flag']=False
                    continue    
                
                ###########THIS IS WORKING!!!!#############   
                #pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2,votes_map_ponderations)
                ###########THIS IS WORKING!!!!#############
                #######WORKING SHITS ON MEDOCS##############
                if comparaison_measure=='similarity_candidates':#not pruning :
                    
                    #pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
                    pattern_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,v_ids,users1_ids_set,users2_ids_set,comparaison_measure)
                    
                    for u1agg in users1_ids_set:
                        for u2agg in users2_ids_set:
                            sizeofpop_ui_indiv1=0
                            sizeofpop_ui_indiv2=0
                            for u1_indiv in users1_all_ids_to_preserve&users1_aggregated_map_to_users[u1agg]:
                                #sizeofpop_ui_indiv1=max(sizeofpop_ui_indiv1,users_map_details_from_array[u1_indiv]['sizeOfPop'])
                                sizeofpop_ui_indiv1+=users_map_details_from_array[u1_indiv]['sizeOfPop']
                            for u2_indiv in users2_all_ids_to_preserve&users2_aggregated_map_to_users[u2agg]:
                                #sizeofpop_ui_indiv2=max(sizeofpop_ui_indiv2,users_map_details_from_array[u2_indiv]['sizeOfPop'])
                                sizeofpop_ui_indiv2+=users_map_details_from_array[u2_indiv]['sizeOfPop']
#                             if reference_updated and u2_p==[["R\xe9gions et D\xe9partements d'outre-mer "]]:
#                                 print '--------------------',u1_p,u2_p,sizeofpop_ui_indiv1,sizeofpop_ui_indiv2,sizeofpop_ui_indiv2/sizeofpop_ui_indiv1,'--------------------'
                            ponderat=sizeofpop_ui_indiv2/sizeofpop_ui_indiv1
#                             print '**************AVANT  ',pattern_matrix_dic[u1agg][u2agg],'******************************'
#                             print '**************AVANT  ',reference_matrix_dic[u1agg][u2agg],'******************************'
                            pattern_matrix_dic[u1agg][u2agg]=(pattern_matrix_dic[u1agg][u2agg][0]*ponderat,pattern_matrix_dic[u1agg][u2agg][1])
                            if not reference_updated:
                                reference_matrix_dic[u1agg][u2agg]=(reference_matrix_dic[u1agg][u2agg][0]*ponderat,reference_matrix_dic[u1agg][u2agg][1])
#                             print '**************APRES  ',pattern_matrix_dic[u1agg][u2agg],'******************************'
#                             print '**************APRES  ',reference_matrix_dic[u1agg][u2agg],'******************************'
                    reference_updated=True
                    
                else:
                    pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2,votes_map_ponderations)
                #######WORKING SHITS ON MEDOCS##############
                  
                reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,qualityMeasure,coeff=lambda x : 1/float(nb_users_voted))
                
                e_config['quality']=quality
                e_config['upperbound']=borne_max_quality
                #########################
                
                #########################
                if (pruning and borne_max_quality<quality_threshold):
                    e_config['flag']=False
                    continue
                if (quality>=quality_threshold):
                    
                    ##############################################THIS NEED TO BE REMOVED#############################
                    
                    reviews_agg={}
                    if compute_agg_reviews:
                        reviews_agg1=[{users_id_attribute:u,vote_id_attribute:v,position_attribute:users1_aggregated_to_votes_outcomes_pattern[u][v]} for u in users1_ids_set for v in v_ids if v in users1_aggregated_to_votes_outcomes_pattern[u]]
                        reviews_agg2=[{users_id_attribute:u,vote_id_attribute:v,position_attribute:users2_aggregated_to_votes_outcomes_pattern[u][v]} for u in users2_ids_set-users1_ids_set for v in v_ids if v in users2_aggregated_to_votes_outcomes_pattern[u]]
                        if not issquare and len(users1_ids_set)==len(users2_ids_set)==1:
                            reviews_agg2=[{users_id_attribute:u,vote_id_attribute:v,position_attribute:users2_aggregated_to_votes_outcomes_pattern[u][v]} for u in users2_ids_set for v in v_ids if v in users2_aggregated_to_votes_outcomes_pattern[u]]
                        
                        for row in reviews_agg1:
                            row.update(votes_map_details_from_array[row[vote_id_attribute]])
                            row.update(users1_aggregated_map_details[row[users_id_attribute]])
                        
                        for row in reviews_agg2:
                            row.update(votes_map_details_from_array[row[vote_id_attribute]])
                            row.update(users2_aggregated_map_details[row[users_id_attribute]])
                        reviews_agg=reviews_agg1+reviews_agg2
                    ##############################################THIS NEED TO BE REMOVED#############################
                    
                    pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                    reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                    dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                    
                    dossiers_voted=[]
                    if False:
                        dossiers_voted=sorted([(map_details[d][elementToShow],map_details[d]['NB_VOTES']) for d in dossiers_ids],key = itemgetter(1),reverse=True)
                        dossiers_voted=get_0_items(dossiers_voted)

                    
                    ##############"SPECIAL VOTES ELECTION AND MEDOCS##############
                    if comparaison_measure=='similarity_candidates':
                        res_election={}
#                         sizeofpop_ui_indiv1=0
#                         sizeofpop_ui_indiv2=0
#                         for u1agg in users1_ids_set:
#                             for u2agg in users2_ids_set:
#                                 for u1_indiv in users1_aggregated_map_to_users[u1agg]:
#                                     sizeofpop_ui_indiv1=max(sizeofpop_ui_indiv1,users_map_details_from_array[u1_indiv]['sizeOfPop'])
#                                 for u2_indiv in users2_aggregated_map_to_users[u2agg]:
#                                     sizeofpop_ui_indiv2=max(sizeofpop_ui_indiv2,users_map_details_from_array[u2_indiv]['sizeOfPop'])
                        for u1agg in users1_ids_set:
                            for u2agg in users2_ids_set:
                                sizeofpop_ui_indiv1=0
                                sizeofpop_ui_indiv2=0
                                for u1_indiv in users1_all_ids_to_preserve&users1_aggregated_map_to_users[u1agg]:
                                    #sizeofpop_ui_indiv1=max(sizeofpop_ui_indiv1,users_map_details_from_array[u1_indiv]['sizeOfPop'])
                                    sizeofpop_ui_indiv1+=users_map_details_from_array[u1_indiv]['sizeOfPop']
                                for u2_indiv in users2_all_ids_to_preserve&users2_aggregated_map_to_users[u2agg]:
                                    #sizeofpop_ui_indiv2=max(sizeofpop_ui_indiv2,users_map_details_from_array[u2_indiv]['sizeOfPop'])
                                    sizeofpop_ui_indiv2+=users_map_details_from_array[u2_indiv]['sizeOfPop']
                                
                        for u1 in users1_aggregated_to_votes_outcomes_pattern:
                            res_election['agg'+'1']=sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][0] if v in users1_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in v_ids)#/float(sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][1] if v in users1_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in v_ids))*10000
                            res_election['agg'+'1Total']=sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][0] if v in users1_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in votes_id_reference)#/float(sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][1] if v in users1_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in votes_id_reference))*10000
                            res_election['agg'+'1SIZEOFPOP']=sizeofpop_ui_indiv1#sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][1] if v in users1_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in votes_id_reference)
                        for u1 in users2_aggregated_to_votes_outcomes_pattern:
                            res_election['agg'+'2']=sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][0] if v in users2_aggregated_to_votes_outcomes_pattern[u1] else 0.  for v in v_ids)#/float(sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][1] if v in users2_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in v_ids))*10000
                            res_election['agg'+'2Total']=sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][0] if v in users2_aggregated_to_votes_outcomes_pattern[u1] else 0.  for v in votes_id_reference)#/float(sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][1] if v in users2_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in votes_id_reference))*10000
                            res_election['agg'+'2SIZEOFPOP']=sizeofpop_ui_indiv2#sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][1] if v in users2_aggregated_to_votes_outcomes_pattern[u1] else 0. for v in votes_id_reference)
                        
                        dossiers_voted=res_election
                    
                    ###################################################
                    
                    nb_patterns+=1
                    #if len(interesting_patterns) <= 10000:
                    interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids,users1_all_ids_to_preserve,users2_all_ids_to_preserve,reviews_agg])
                    #NEW FOR TESTS

                    #NEW FOR TESTS

                    if len(interesting_patterns)>top_k:
                        interesting_patterns=sorted(interesting_patterns,key = itemgetter(3),reverse=True)[:top_k]
                        quality_threshold=interesting_patterns[-1][3]
                        interesting_patterns_dic['interestingPatterns']=interesting_patterns
                        
                    
                        
    timing+=time()-st
    new_timing=time()
    
#     new_interesting_patterns=enumerate_aggregations_in_results(interesting_patterns,
#                             users_attributes,
#                             users_map_details_array_filtered_user1,
#                             users_map_details_array_filtered_user2,
#                             aggregationAttributes_user2,
#                             all_users_to_votes_outcomes,
#                             all_votes_id,
#                             votes_id_reference,
#                             nb_aggregation_min_user1,
#                             nb_aggregation_min_user2,
#                             outcome_tuple_structure,
#                             comparaison_measure,
#                             qualityMeasure,
#                             threshold_pair_comparaison,
#                             users_aggregated_track)
#     interesting_patterns=new_interesting_patterns
    
    b=cover_threshold<1;ii=0
    while b:
        #print "qslkdjazlkerjlmsjdmlsq,da:lz,r"
        v_ids_now=interesting_patterns[ii][6]
        #print v_ids_now
        
        array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids_now),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids,K1,K2,reviews_agg),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
        indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold and x[0]<>ii]
        interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
        ii+=1
        #raw_input('...')
        b=False if ii>=len(interesting_patterns) else True
        
    new_timing=time()-new_timing
    print '.......',timing,new_timing,initialization,index_visited,'NB PATTERNS FOUND : ',len(interesting_patterns),'.......'
    
    n=0

    ############
    if False:
        interesting_patterns=interesting_patterns[:1]
    #############

    Outcomes_covered=0
    if True:
        sss_outcomes_sss=set()
        for _,_,_,_,_,_,votes_id_pattern,uall1,uall2,_ in sorted(interesting_patterns,key = itemgetter(3),reverse=True):
            sss_outcomes_sss|={tuple((u,e)) for u in uall1|uall2 for e in  votes_id_pattern if e in all_users_to_votes_outcomes[u]}
        Outcomes_covered=len(sss_outcomes_sss)
    
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,votes_id_pattern,uall1,uall2,reviews_agg in sorted(interesting_patterns,key = itemgetter(3),reverse=True):
        
        ####################################REVIEWES WRITING######################################## 
        votes_and_ids_considered=[sorted(uall1),sorted(uall2),sorted(votes_id_reference),sorted(votes_id_pattern)]+ [["./Figures/ref_for_graph_"+str(n)+".csv"]] + [["./Figures/context_for_graph_"+str(n)+".csv"]]
        #votes_and_ids_considered=[sorted(uall1|uall2),sorted(votes_id_reference),sorted(votes_id_pattern)]+ [["./Figures/ref_for_graph_"+str(n)+".csv"]] + [["./Figures/context_for_graph_"+str(n)+".csv"]]
#         votes_and_ids_considered={'u_ids_considered':sorted(uall1|uall2),
#          'v_ids_ref':sorted(votes_id_reference),
#          'v_ids_context':sorted(votes_id_pattern)}
        reviews=[]#[x for x in new_review_dataset if x[vote_id_attribute] in votes_id_pattern and (x[users_id_attribute] in uall1 or x[users_id_attribute] in uall2)]
        for row in reviews:
            row.update(votes_map_details_from_array[row[vote_id_attribute]])
            row.update(users_map_details_from_array[row[users_id_attribute]])
        nb_reviews=len(reviews)
        ####################################REVIEWES WRITING########################################
        

        
            #raw_input('.......')

        new_disposition={
            'index':n,
            'pattern':p,
            'context':label[0],
            'g1':label[1],
            'g2':label[2],
            '|subgroup(context)|':len(votes_id_pattern),
            '|subgroup(g1)|':len(uall1),
            '|subgroup(g2)|':len(uall2),
            '#reviews':nb_reviews,
            'quality':round(quality,2),
            'upperbound':borne_max_quality,
            'items_details':dossiers_voted,
            'votes_and_ids_considered':votes_and_ids_considered,
            'reviews':reviews_agg,
            'Outcomes_covered':Outcomes_covered,
            'visited':index_visited,
            'nb_patterns':nb_patterns if False else len(interesting_patterns) #TRUE IF WE WANT TO EVALUATE VS ECML FOR COMPRESSION
        }
        n+=1
        yield p,label,dataset_stats,round(quality,2),borne_max_quality,dossiers_voted,new_disposition
        
    


def DSCFORPERF(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    ##########################TODO######################################
    #1. Find a way to dynamically compute aggregate of users without a great overhead which is the cas now
    #2. Is there a way to explore less patterns by using the fade first aproach (selecting the candidate description that lend the minimum poissible support
    #3. Is there a way to reverse the way of enumeration to exploit the upper bound over all the three-set
    #4. Find an upper bound that is more tight than the two others (the infamous one that compute a maximum of sum rather than max by one but has a giant overhead)
    #5. Use sampling method and select smartly the three sets parts (ressemblance, cover, adventage diversity and exploitation. MCTS ?) 
    ####################################################################
    
    
    
    initialize=time()
    count_verif_thres=0
    time_threshold=3600;obs=0
    timing=0;ends=0
    interesting_patterns=[]
    elementToShow=votes_attributes[1]
    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    how_much_visited={'visited':0}
    maximumqualityobserved=0
    ###################PARAMETERS_COMPUTING###################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold
    if quality_threshold==0:quality_threshold=0.0000001
    pruning = configuration.get('pruning',False)
    closed = configuration.get('closed',True)
    bound_1_2=configuration.get('upperbound',1)
    qualityMeasure=configuration['iwant']
    
    lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False

    comparaison_measure=configuration['comparaison_measure']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',[users_attributes[0]])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',[users_attributes[0]])
    
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    threshold_nb_users_1=configuration.get('threshold_nb_users_1',1)
    threshold_nb_users_2=configuration.get('threshold_nb_users_2',1)
    nb_items_to_study=configuration.get('nb_items',None)
    nb_users_to_study=configuration.get('nb_users',None)
    method_aggregation_outcome=configuration.get('method_aggregation_outcome','STANDARD')
    ###################PARAMETERS_COMPUTING###################
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    get_votes_ids = partial(map,itemgetter(vote_id_attribute))
    get_users_ids = partial(map,itemgetter(users_id_attribute))
    
    
    
    #############NEW#########################################
    reviews_dataset=configuration['reviews_dataset']
    reviews_dataset_new=[];reviews_dataset_new_append=reviews_dataset_new.append
    items_dataset=configuration['items_dataset']
    users_dataset=configuration['users_dataset']
    vector_of_outcome=configuration.get('vector_of_outcome',None)
    
    items_ids_to_remove=set(sorted(get_votes_ids(items_dataset))[nb_items_to_study:]) if nb_items_to_study is not None else set()
    users_ids_to_remove=set(sorted(get_users_ids(users_dataset))[nb_users_to_study:]) if nb_users_to_study is not None else set()
    
    all_users_to_votes_outcomes={}#x[users_id_attribute]:{} for x in reviews_dataset}
    
    for row in reviews_dataset:
        v_id_rev=row[vote_id_attribute]
        u_id_rev=row[users_id_attribute]
        if v_id_rev in items_ids_to_remove or u_id_rev in users_ids_to_remove:
            continue
        reviews_dataset_new_append(row)
        pos_rev=row[position_attribute]
        if u_id_rev not in all_users_to_votes_outcomes:
            all_users_to_votes_outcomes[u_id_rev]={}
        all_users_to_votes_outcomes[u_id_rev][v_id_rev]=pos_rev
    items_dataset=[i for i in items_dataset if i[vote_id_attribute] not in items_ids_to_remove]    
    users_dataset=[i for i in users_dataset if i[users_id_attribute] not in users_ids_to_remove]
    reviews_dataset=reviews_dataset_new
    #############NEW#########################################
    
    
    #votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute,nb_items_to_study,nb_users_to_study)
    #votes_map_details_array=votes_map_details.values()
    
    
    votes_map_details_array=items_dataset#votes_map_details.values()
    votes_map_details_from_array={row[vote_id_attribute]:row for row in votes_map_details_array}
    
    
    
    all_votes_id= set(get_votes_ids(votes_map_details_array))#all_votes_id= set(votes_map_details.keys())
    #all_users_map_details_array=all_users_map_details.values()
    
    all_users_map_details_array=users_dataset
    
    outcome_tuple_structure=list(all_users_to_votes_outcomes.values()[0].values()[0])
    #outcome_tuple_structure=list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users_aggregated_track={}
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)

    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track,method_aggregation_outcome=method_aggregation_outcome)

    
    
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    #reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure,issquare=(users1_all_ids_to_preserve==users2_all_ids_to_preserve))
    
    
    users_map_details_array_filtered_user1=sorted([row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve],key=itemgetter(users_id_attribute))
    users_map_details_array_filtered_user2=sorted([row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve],key=itemgetter(users_id_attribute))

    map_details={votes_map_details_from_array[v_id][elementToShow]:{elementToShow:votes_map_details_from_array[v_id][elementToShow]} for v_id in votes_map_details_from_array}
    for v_id,v_value in votes_map_details_from_array.iteritems():
        map_details[v_value[elementToShow]]['NB_VOTES']=map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
    
    
    index_visited=0
    
    
    get_actual_top_k_users_1_full_ids = partial(map,itemgetter(7))
    get_actual_top_k_users_2_full_ids = partial(map,itemgetter(8))
    get_doss = partial(map,itemgetter(elementToShow))
    
    lvl_users_part=0
    st=time() 
    
    nb_ratings = len(reviews_dataset) #sum(len(all_users_map_votes[k]) for k in  all_users_map_votes)
    parameters={
        'sigma_context':threshold_pair_comparaison,
        'sigma_u1':threshold_nb_users_1,
        'sigma_u2':threshold_nb_users_2,
        'sigma_agg_u1':nb_aggregation_min_user1,
        'sigma_agg_u2':nb_aggregation_min_user2,
        '#ratings':nb_ratings,
        '#items':len(all_votes_id),
        '#users1':len(all_users1_ids),
        '#usersagg_1':len(users1_agg_ids),
        '#users2':len(all_users2_ids),
        '#usersagg_2':len(users2_agg_ids),
        '#attr_items':len(subattributes_details_votes),
        'attr_items':[(x['name'],x['type']) for x in attributes if x['name'] in votes_attributes],
        '#attr_users':len(subattributes_details_users),
        'attr_users':[(x['name'],x['type']) for x in attributes if x['name'] in users_attributes],
        '#attr_aggregate':len(aggregationAttributes_user1),
        'attr_aggregate':[aggregationAttributes_user1],
        'closed':closed,
        'prune':pruning,
        'sigma_quality':quality_threshold,
        'top_k':top_k,
        'quality_measure':qualityMeasure,
        'similarity_measure':comparaison_measure,
        'upperbound_type':bound_1_2
    }
    
    interesting_patterns_dic={'interestingPatterns':interesting_patterns}
    
    index_visited=0
    index_all_descriptions=0
    index_u1_visited=0;index_all_u1_visited=0
    index_u2_visited=0;index_all_u2_visited=0
    initialize=time()-initialize
    timing=time()
    enum_pair_of_users=enumerator_pair_of_users(users_map_details_array_filtered_user1,
                             users_map_details_array_filtered_user2,
                             all_users_to_votes_outcomes,
                             all_votes_id,
                             users1_agg_ids,
                             users2_agg_ids,
                             users1_aggregated_map_details,
                             users2_aggregated_map_details,
                             users1_aggregated_map_to_users,
                             users2_aggregated_map_to_users,
                             users_attributes,
                             subattributes_details_users,
                             threshold_nb_users_1,
                             threshold_nb_users_2,
                             nb_aggregation_min_user1,
                             nb_aggregation_min_user2,
                             outcome_tuple_structure,
                             vector_of_outcome,
                             users_aggregated_track,
                             interesting_patterns_dic,
                             closed,
                             how_much_visited,
                             method_aggregation_outcome)
    
    
    
    
    initConfig={'config':None,'attributes':None}
    for (u1_p,u1_label,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,u1_config),(u2_p,u2_label,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,u2_config) in enum_pair_of_users:
            
            obs=time()-timing
            if obs > time_threshold: break
            issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,all_votes_id,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
            
            
            
            if closed:
                enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},threshold=threshold_pair_comparaison,verbose=False,bfs=False,do_heuristic=False,initValues=initConfig)
            else:
                enumerator_contexts=enumerator_complex_from_dataset_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},objet_id_attribute=vote_id_attribute,threshold=threshold_pair_comparaison,verbose=False,initValues=initConfig)
            


            userpairssimsdetails={}
            for u1 in users1_aggregated_to_preserve:
                userpairssimsdetails[u1]={}
                for u2 in users2_aggregated_to_preserve:
                    userpairssimsdetails[u1][u2]={}
                    for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys():
                        simi_u1_u2=similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],u1,u2,comparaison_measure)[0]
                        userpairssimsdetails[u1][u2][v]=simi_u1_u2
                    
            
            
            ######
            
            #print u1_p,u2_p,len(users1_all_ids_to_preserve),len(users2_all_ids_to_preserve),index_visited,lvl_users_part
            #print index_visited
            
            for e_p,e_label,e_config in enumerator_contexts:
                obs=time()-timing
                if obs > time_threshold: break   
                index_visited+=1
                v_ids=set()
                e_u_p=e_p + u1_p + u2_p
                e_u_label=e_label + u1_label + u2_label
                e_votes=e_config['support']
         

                v_ids=set(get_votes_ids(e_votes))
                dossiers_ids=set()
                dossiers_ids=set(get_doss(e_votes))

                users1_ids_set,users2_ids_set,flag_continue=get_users_validating_pairwise_threshold(e_config, v_ids, users1_aggregated_to_preserve, users2_aggregated_to_preserve, threshold_pair_comparaison, issquare)
                if flag_continue: 
                    e_config['flag']=False
                    continue    
                
                if not pruning:
                    pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
                    ##############"SPECIAL VOTES ELECTION##############
                    #pattern_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,v_ids,users1_ids_set,users2_ids_set,comparaison_measure)
                    ###################################################
                else :    
                    pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
                    

                    
                
                reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,qualityMeasure,coeff=lambda x : 1/float(nb_users_voted))
                
                e_config['quality']=quality
                e_config['upperbound']=borne_max_quality
                #########################
                
                #########################
                if (pruning and borne_max_quality<quality_threshold):
                    e_config['flag']=False
                    continue
#                 if e_u_p==[['04'], [0.0, 1.0], ['AZ'], ['newcomer'], ['senior']]:
#                     print '\n'
#                     print quality,v_ids
                if (quality>=quality_threshold):
                    maximumqualityobserved=max(quality,maximumqualityobserved)
                    count_verif_thres+=1
                    if top_k== float('inf'):
                        continue
                    pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                    reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                    dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                    dossiers_voted=sorted([(map_details[d][elementToShow],map_details[d]['NB_VOTES']) for d in dossiers_ids],key = itemgetter(1),reverse=True)
                    interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids,users1_all_ids_to_preserve,users2_all_ids_to_preserve])

                    if len(interesting_patterns)>top_k:
                        interesting_patterns=sorted(interesting_patterns,key = itemgetter(3),reverse=True)[:top_k]
                        quality_threshold=interesting_patterns[-1][3]
                        interesting_patterns_dic['interestingPatterns']=interesting_patterns
            index_all_descriptions+=e_config['nb_visited'][0]
    visited_pairs=how_much_visited['visited']
    timing=time()-timing 
    statusmamus={
        '#all_visited_context':index_all_descriptions+visited_pairs,
        '#candidates':index_visited,
        '#init':initialize,
        #'#init':[(x[0],x[1],x[3]) for x in interesting_patterns],
        '#timespent':timing,
        '#patterns':len(interesting_patterns) if top_k<> float('inf') else count_verif_thres,
        'max_quality_found':maximumqualityobserved#max(interesting_patterns[i][3] for i in range(len(interesting_patterns))) if len(interesting_patterns)>0 else 0
    }
    statusmamus.update(parameters)                 
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in [(1,2,3,4,5,6,7)]:
        yield p,label,dataset_stats,quality,borne_max_quality,[statusmamus]
    #timing+=time()-st  
    #print '.......',timing,index_visited,ends,'.......'  


def DSCFORPERFOLD(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    ##########################TODO######################################
    #1. Find a way to dynamically compute aggregate of users without a great overhead which is the cas now
    #2. Is there a way to explore less patterns by using the fade first aproach (selecting the candidate description that lend the minimum poissible support
    #3. Is there a way to reverse the way of enumeration to exploit the upper bound over all the three-set
    #4. Find an upper bound that is more tight than the two others (the infamous one that compute a maximum of sum rather than max by one but has a giant overhead)
    #5. Use sampling method and select smartly the three sets parts (ressemblance, cover, adventage diversity and exploitation. MCTS ?) 
    ####################################################################
    
    
    
    initialize=time()
    count_verif_thres=0
    time_threshold=3600;obs=0
    timing=0;ends=0
    interesting_patterns=[]
    elementToShow=votes_attributes[1]
    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    how_much_visited={'visited':0}
    
    ###################PARAMETERS_COMPUTING###################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold
    if quality_threshold==0:quality_threshold=0.0000001
    pruning = configuration.get('pruning',False)
    closed = configuration.get('closed',True)
    bound_1_2=configuration.get('upperbound',1)
    qualityMeasure=configuration['iwant']
    
    lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False

    comparaison_measure=configuration['comparaison_measure']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',[users_attributes[0]])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',[users_attributes[0]])
    
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    threshold_nb_users_1=configuration.get('threshold_nb_users_1',1)
    threshold_nb_users_2=configuration.get('threshold_nb_users_2',1)
    nb_items_to_study=configuration.get('nb_items',None)
    nb_users_to_study=configuration.get('nb_users',None)
    ###################PARAMETERS_COMPUTING###################
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    get_votes_ids = partial(map,itemgetter(vote_id_attribute))
    get_users_ids = partial(map,itemgetter(users_id_attribute))
    
    
    
    #############NEW#########################################
    reviews_dataset=configuration['reviews_dataset']
    items_dataset=configuration['items_dataset']
    users_dataset=configuration['users_dataset']
    vector_of_outcome=configuration.get('vector_of_outcome',None)
    
    items_ids_to_remove=set(sorted(get_votes_ids(items_dataset))[nb_items_to_study:]) if nb_items_to_study is not None else set()
    users_ids_to_remove=set(sorted(get_users_ids(users_dataset))[nb_users_to_study:]) if nb_users_to_study is not None else set()
    
    all_users_to_votes_outcomes={}#x[users_id_attribute]:{} for x in reviews_dataset}
    
    for row in reviews_dataset:
        v_id_rev=row[vote_id_attribute]
        u_id_rev=row[users_id_attribute]
        if v_id_rev in items_ids_to_remove or u_id_rev in users_ids_to_remove:
            continue
        
        pos_rev=row[position_attribute]
        if u_id_rev not in all_users_to_votes_outcomes:
            all_users_to_votes_outcomes[u_id_rev]={}
        all_users_to_votes_outcomes[u_id_rev][v_id_rev]=pos_rev
    items_dataset=[i for i in items_dataset if i[vote_id_attribute] not in items_ids_to_remove]    
    users_dataset=[i for i in users_dataset if i[users_id_attribute] not in users_ids_to_remove]
    #############NEW#########################################
    
    
    #votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute,nb_items_to_study,nb_users_to_study)
    #votes_map_details_array=votes_map_details.values()
    
    
    votes_map_details_array=items_dataset#votes_map_details.values()
    votes_map_details_from_array={row[vote_id_attribute]:row for row in votes_map_details_array}
    
    
    
    all_votes_id= set(get_votes_ids(votes_map_details_array))#all_votes_id= set(votes_map_details.keys())
    #all_users_map_details_array=all_users_map_details.values()
    
    all_users_map_details_array=users_dataset
    
    outcome_tuple_structure=list(all_users_to_votes_outcomes.values()[0].values()[0])
    #outcome_tuple_structure=list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users_aggregated_track={}
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track,ponderations=vector_of_outcome)

    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track,ponderations=vector_of_outcome)

    
    
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    #reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure,issquare=(users1_all_ids_to_preserve==users2_all_ids_to_preserve))
    
    
    users_map_details_array_filtered_user1=sorted([row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve],key=itemgetter(users_id_attribute))
    users_map_details_array_filtered_user2=sorted([row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve],key=itemgetter(users_id_attribute))

    map_details={votes_map_details_from_array[v_id][elementToShow]:{elementToShow:votes_map_details_from_array[v_id][elementToShow]} for v_id in votes_map_details_from_array}
    for v_id,v_value in votes_map_details_from_array.iteritems():
        map_details[v_value[elementToShow]]['NB_VOTES']=map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
    
    
    index_visited=0
    
    
    get_actual_top_k_users_1_full_ids = partial(map,itemgetter(7))
    get_actual_top_k_users_2_full_ids = partial(map,itemgetter(8))
    get_doss = partial(map,itemgetter(elementToShow))
    
    lvl_users_part=0
    st=time() 
    
    nb_ratings = len(reviews_dataset) #sum(len(all_users_map_votes[k]) for k in  all_users_map_votes)
    parameters={
        'sigma_context':threshold_pair_comparaison,
        'sigma_u1':threshold_nb_users_1,
        'sigma_u2':threshold_nb_users_2,
        'sigma_agg_u1':nb_aggregation_min_user1,
        'sigma_agg_u2':nb_aggregation_min_user2,
        '#ratings':nb_ratings,
        '#items':len(all_votes_id),
        '#users1':len(all_users1_ids),
        '#usersagg_1':len(users1_agg_ids),
        '#users2':len(all_users2_ids),
        '#usersagg_2':len(users2_agg_ids),
        '#attr_items':len(subattributes_details_votes),
        'attr_items':[(x['name'],x['type']) for x in attributes if x['name'] in votes_attributes],
        '#attr_users':len(subattributes_details_users),
        'attr_users':[(x['name'],x['type']) for x in attributes if x['name'] in users_attributes],
        '#attr_aggregate':len(aggregationAttributes_user1),
        'attr_aggregate':[aggregationAttributes_user1],
        'closed':closed,
        'prune':pruning,
        'sigma_quality':quality_threshold,
        'top_k':top_k,
        'quality_measure':qualityMeasure,
        'similarity_measure':comparaison_measure,
        'upperbound_type':bound_1_2
    }
    
    interesting_patterns_dic={'interestingPatterns':interesting_patterns}
    
    index_visited=0
    index_all_descriptions=0
    index_u1_visited=0;index_all_u1_visited=0
    index_u2_visited=0;index_all_u2_visited=0
    initialize=time()-initialize
    timing=time()
    enum_pair_of_users=enumerator_pair_of_users(users_map_details_array_filtered_user1,
                             users_map_details_array_filtered_user2,
                             all_users_to_votes_outcomes,
                             all_votes_id,
                             users1_agg_ids,
                             users2_agg_ids,
                             users1_aggregated_map_details,
                             users2_aggregated_map_details,
                             users1_aggregated_map_to_users,
                             users2_aggregated_map_to_users,
                             users_attributes,
                             subattributes_details_users,
                             threshold_nb_users_1,
                             threshold_nb_users_2,
                             nb_aggregation_min_user1,
                             nb_aggregation_min_user2,
                             outcome_tuple_structure,
                             vector_of_outcome,
                             users_aggregated_track,
                             interesting_patterns_dic,
                             closed,
                             how_much_visited)
    
    for (u1_p,u1_label,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,u1_config),(u2_p,u2_label,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,u2_config) in enum_pair_of_users:
        
        obs=time()-timing
        if obs > time_threshold: break   
         
        issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
        nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
        reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,all_votes_id,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
        
        if closed:
            enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},threshold=threshold_pair_comparaison,verbose=False,bfs=False,do_heuristic=False)
        else:
            enumerator_contexts=enumerator_complex_from_dataset_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},objet_id_attribute=vote_id_attribute,threshold=threshold_pair_comparaison,verbose=False)
        

        
        ######
        userpairssimsdetails={}
        for u1 in users1_aggregated_to_preserve:
            userpairssimsdetails[u1]={}
            for u2 in users2_aggregated_to_preserve:
                userpairssimsdetails[u1][u2]={}
                for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys():
                    simi_u1_u2=similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],u1,u2,comparaison_measure)[0]
                    userpairssimsdetails[u1][u2][v]=simi_u1_u2
        ######
        #print u1_p,u2_p,len(users1_all_ids_to_preserve),len(users2_all_ids_to_preserve),index_visited,couple_ressemblance,lvl_users_part
        
        for e_p,e_label,e_config in enumerator_contexts:
            obs=time()-timing
            if obs > time_threshold: break   
            index_visited+=1
            v_ids=set()
            e_u_p=e_p + u1_p + u2_p
            e_u_label=e_label + u1_label + u2_label
            e_votes=e_config['support']
     

            v_ids=set(get_votes_ids(e_votes))
            dossiers_ids=set()
            #dossiers_ids=set(get_doss(e_votes))

            users1_ids_set,users2_ids_set,flag_continue=get_users_validating_pairwise_threshold(e_config, v_ids, users1_aggregated_to_preserve, users2_aggregated_to_preserve, threshold_pair_comparaison, issquare)
            if flag_continue: 
                e_config['flag']=False
                continue
            
            if not pruning:
                pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
                
                ##############"SPECIAL VOTES ELECTION##############
                #pattern_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,v_ids,users1_ids_set,users2_ids_set,comparaison_measure)
                ###################################################
            else :    
                pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
            
            reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
            quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,qualityMeasure,coeff=lambda x : 1/float(nb_users_voted))
            e_config['quality']=quality
            e_config['upperbound']=borne_max_quality
            if (pruning and borne_max_quality<quality_threshold):
                e_config['flag']=False
                continue
            if (quality>=quality_threshold):
                pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                dossiers_voted=sorted([(map_details[d][elementToShow],map_details[d]['NB_VOTES']) for d in dossiers_ids],key = itemgetter(1),reverse=True)

                
                interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids,users1_all_ids_to_preserve,users2_all_ids_to_preserve])

                if len(interesting_patterns)>top_k:
                    interesting_patterns=sorted(interesting_patterns,key = itemgetter(3),reverse=True)[:top_k]
                    quality_threshold=interesting_patterns[-1][3]
                    interesting_patterns_dic['interestingPatterns']=interesting_patterns
        index_all_descriptions+=e_config['nb_visited'][0]
    visited_pairs=how_much_visited['visited']
    timing=time()-timing 
    print timing
    statusmamus={
        '#all_visited_context':index_all_descriptions+visited_pairs,
        '#candidates':index_visited,
        '#init':initialize,
        '#timespent':timing,
        '#patterns':len(interesting_patterns) if top_k<= 10000 else count_verif_thres,
        'max_quality_found':max(interesting_patterns[i][3] for i in range(len(interesting_patterns))) if len(interesting_patterns)>0 else 0
    }
    statusmamus.update(parameters)                 
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in [(1,2,3,4,5,6,7)]:
        yield p,label,dataset_stats,quality,borne_max_quality,[statusmamus]
    #timing+=time()-st  
    #print '.......',timing,index_visited,ends,'.......'  
    
    
def DSCOLD(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    ##########################TODO######################################
    #1. Find a way to dynamically compute aggregate of users without a great overhead which is the cas now
    #2. Is there a way to explore less patterns by using the fade first aproach (selecting the candidate description that lend the minimum poissible support
    #3. Is there a way to reverse the way of enumeration to exploit the upper bound over all the three-set
    #4. Find an upper bound that is more tight than the two others (the infamous one that compute a maximum of sum rather than max by one but has a giant overhead)
    #5. Use sampling method and select smartly the three sets parts (ressemblance, cover, adventage diversity and exploitation. MCTS ?) 
    ####################################################################
    
    
    
    
    timing=0;ends=0
    interesting_patterns=[]
    elementToShow=votes_attributes[1]
    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    st=time() 
    
    ###################PARAMETERS_COMPUTING###################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold
    pruning = configuration.get('pruning',False)
    closed = configuration.get('closed',False)
    bound_1_2=configuration.get('upperbound',1)
    qualityMeasure=configuration['iwant']
    
    lower=True if qualityMeasure == 'DISAGR_SUMDIFF' else False if qualityMeasure=='AGR_SUMDIFF' else False

    comparaison_measure=configuration['comparaison_measure']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',[users_attributes[0]])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',[users_attributes[0]])
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    threshold_nb_users_1=configuration.get('threshold_nb_users_1',1)
    threshold_nb_users_2=configuration.get('threshold_nb_users_2',1)
    ###################PARAMETERS_COMPUTING###################
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())
    all_users_map_details_array=all_users_map_details.values()
    outcome_tuple_structure=list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users_aggregated_track={}
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track)

    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track)

    
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    #reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure,issquare=(users1_all_ids_to_preserve==users2_all_ids_to_preserve))
    
    
    users_map_details_array_filtered_user1=sorted([row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve],key=itemgetter(users_id_attribute))
    users_map_details_array_filtered_user2=sorted([row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve],key=itemgetter(users_id_attribute))

    map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        map_details[v_value[elementToShow]]['NB_VOTES']=map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
    
    
    index_visited=0
    visited_1_trace_map={}
    get_votes_ids = partial(map,itemgetter(vote_id_attribute))
    get_users_ids = partial(map,itemgetter(users_id_attribute))
    
    get_actual_top_k_users_1_full_ids = partial(map,itemgetter(7))
    get_actual_top_k_users_2_full_ids = partial(map,itemgetter(8))
    
    get_doss = partial(map,itemgetter(elementToShow))
    
    lvl_users_part=0
    enum_u1=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1)
    for u1_p,u1_label,u1_config in enum_u1:
        u1_p_tuple_users=tuple(get_users_ids(u1_config['support']))
        u1_p_set_users=set(u1_p_tuple_users)
        users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,outcome_track=users_aggregated_track)
        if len(users1_aggregated_to_preserve)==0:
                u1_config['flag']=False
                continue
        if not u1_p_tuple_users in visited_1_trace_map:
            visited_1_trace_map[u1_p_tuple_users]=set()
        #lvl_users_part+=1 if u1_config.get('change_in_lvl',None) else 0
        enum_u2=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_2)
        for u2_p,u2_label,u2_config in enum_u2: 
            u2_p_tuple_users=tuple(get_users_ids(u2_config['support']))
            u2_p_set_users=set(u2_p_tuple_users)
            if (u2_p_tuple_users in visited_1_trace_map and u1_p_tuple_users in visited_1_trace_map[u2_p_tuple_users]) :#or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
                    continue
            else :
                visited_1_trace_map[u1_p_tuple_users]|={u2_p_tuple_users}
        
            users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2,outcome_track=users_aggregated_track)
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            if len(users2_aggregated_to_preserve)==0:
                u2_config['flag']=False
                continue
            
            issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
            
            reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,all_votes_id,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
            enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},threshold=threshold_pair_comparaison,verbose=True,bfs=False)
            
            ##############
            couple_ressemblance=0
#             top_k_actu_users1=get_actual_top_k_users_1_full_ids(interesting_patterns)
#             top_k_actu_users2=get_actual_top_k_users_2_full_ids(interesting_patterns)
#             top_k_actu_users1_ressemblance=[(ressemblance(x,users1_all_ids_to_preserve)+ressemblance(x,users2_all_ids_to_preserve))/2. for x in top_k_actu_users1]
#             top_k_actu_users2_ressemblance=[(ressemblance(x,users1_all_ids_to_preserve)+ressemblance(x,users2_all_ids_to_preserve))/2. for x in top_k_actu_users2]
#             couple_ressemblance=sum([(x+y)/2.for x,y in zip(top_k_actu_users1_ressemblance,top_k_actu_users2_ressemblance)])/len(top_k_actu_users1_ressemblance) if len(top_k_actu_users1_ressemblance)>0 else 0.
            
            #lvl_users_part+=1 if u2_config.get('change_in_lvl',None) else 0
            #TODO Find a way to randomly generate pair of users descrition by anes method 
            #print top_k_actu_users1_ressemblance,top_k_actu_users2_ressemblance
            ##############
            
            ######
            userpairssimsdetails={}
            for u1 in users1_aggregated_to_preserve:
                userpairssimsdetails[u1]={}
                for u2 in users2_aggregated_to_preserve:
                    userpairssimsdetails[u1][u2]={v:similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],u1,u2,comparaison_measure)[0] for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys()}
            ######
            
            print u1_p,u2_p,len(users1_all_ids_to_preserve),len(users2_all_ids_to_preserve),index_visited,couple_ressemblance,lvl_users_part
           
            for e_p,e_label,e_config in enumerator_contexts:
                index_visited+=1
                v_ids=set()
                e_u_p=e_p + u1_p + u2_p
                e_u_label=e_label + u1_label + u2_label
                e_votes=e_config['support']
                e_users_1=e_config['users1']
                e_users_2=e_config['users2']
                
                v_ids=set(get_votes_ids(e_votes))
                dossiers_ids=set()
                #dossiers_ids=set(get_doss(e_votes))
                   
                  
                new_e_users_1={}
                users1_ids_set=set()
                max_votes_pairwise=0
                
                for key in e_users_1:
                    value=e_users_1[key]
                    votes_user=(value & v_ids)
                    len_votes_user=len(votes_user)
                    if len_votes_user>=threshold_pair_comparaison:
                        new_e_users_1[key]=votes_user
                        users1_ids_set|={key}
                        max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
                
                e_config['users1']=new_e_users_1   
                
                if max_votes_pairwise<threshold_pair_comparaison :
                    e_config['flag']=False
                    continue
                
                if issquare :
                    new_e_users_2=new_e_users_1
                    users2_ids_set=users1_ids_set
                else :
                    
                    new_e_users_2={}
                    users2_ids_set=set()
                    max_votes_pairwise=0
                    for key in e_users_2:
                        value=e_users_2[key]
                        votes_user=(value & v_ids)
                        len_votes_user=len(votes_user)
                        if len_votes_user>=threshold_pair_comparaison:
                            new_e_users_2[key]=votes_user
                            users2_ids_set|={key}
                            max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
                
                e_config['users2']=new_e_users_2  
                if max_votes_pairwise<threshold_pair_comparaison :
                    e_config['flag']=False
                    continue
                
                users1_ids_set=users1_aggregated_to_preserve & users1_ids_set
                users2_ids_set=users2_aggregated_to_preserve & users2_ids_set
                
                
                if not pruning:
                    #pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
                    
                    pattern_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,v_ids,users1_ids_set,users2_ids_set,comparaison_measure)
                    
                else :    
                    pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison,lower,bound_1_2)
                
                reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,qualityMeasure,coeff=lambda x : 1/float(nb_users_voted))
                e_config['quality']=quality
                e_config['upperbound']=borne_max_quality
                if (pruning and borne_max_quality<quality_threshold):
                    e_config['flag']=False
                    continue
                if (quality>=quality_threshold):
                    pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                    reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                    dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                    dossiers_voted=sorted([(map_details[d][elementToShow],map_details[d]['NB_VOTES']) for d in dossiers_ids],key = itemgetter(1),reverse=True)
                    ##############"SPECIAL VOTES ELECTION##############
                    res_election={}
                    for u1 in users1_aggregated_to_votes_outcomes_pattern:
                        res_election[u1]=sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][0] for v in v_ids)/float(sum(users1_aggregated_to_votes_outcomes_pattern[u1][v][1] for v in v_ids))
                    for u1 in users2_aggregated_to_votes_outcomes_pattern:
                        res_election[u1]=sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][0] for v in v_ids)/float(sum(users2_aggregated_to_votes_outcomes_pattern[u1][v][1] for v in v_ids))
                    res_election['Votants']=sum(votes_map_details[v]['Votants'] for v in v_ids)
                    res_election['Inscrits']=sum(votes_map_details[v]['Inscrits'] for v in v_ids)
                    dossiers_voted=res_election
                    
                    ###################################################
                    
                    interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids,users1_all_ids_to_preserve,users2_all_ids_to_preserve])
                    
                    
                    
                    if len(interesting_patterns)>top_k:
                        interesting_patterns=sorted(interesting_patterns,key = itemgetter(3),reverse=True)[:top_k]
                        quality_threshold=interesting_patterns[-1][3]
            
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids,uall1,uall2 in sorted(interesting_patterns,key = itemgetter(3),reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    timing+=time()-st  
    print '.......',timing,index_visited,ends,'.......'