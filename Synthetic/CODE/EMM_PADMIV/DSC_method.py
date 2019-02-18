'''
Created on 31 mars 2017

@author: Adnene
'''
from bisect import insort_left
from collections import OrderedDict
from heapq import nsmallest
from math import log
from operator import add
from random import random
from sys import stdout
from time import time
#from numba import jit

from ENUMERATORS_ATTRIBUTES.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config, \
    enumerator_complex_from_dataset_new_config
from filterer.filter import filter_pipeline_obj
from measures.qualityMeasure import compute_quality_and_upperbound
from measures.similaritiesDCS import similarity_vector_measure_dcs
from util.matrixProcessing import getCompleteMatrix
from votesExtractionAndProcessing.pairwiseStatistics import extractStatistics_fromdataset_vectors, \
    datasetStatistics


def ressemblance(set1,set2):
    return float(len(set1&set2))/float(min(len(set1),len(set2)))

def compute_aggregates_outcomes_OLD(v_ids,users_map_details_array,users_to_votes_outcomes,users_attributes,aggregation_attributes,size_aggregate_min=2):
    users_aggregated_to_votes_outcomes={}
    users_aggregated_map_details_array={}
    users_aggregated_map_votes={}
    user_id_attr=users_attributes[0]
    users_aggregated_map_to_users={};users_aggregated_map_to_users_has_key=users_aggregated_map_to_users.has_key
    
    for u in users_map_details_array:
        actual_u_id=u[user_id_attr]

        agg_user_identifier=tuple([u[x] for x in aggregation_attributes])
        agg_user_identifier='agg'+'_'+'_'.join(agg_user_identifier)
        if not users_aggregated_map_to_users_has_key(agg_user_identifier):
            users_aggregated_map_to_users[agg_user_identifier]=set()
            users_aggregated_map_details_array[agg_user_identifier]={att:u[att] if att in aggregation_attributes else agg_user_identifier for att in users_attributes}
        users_aggregated_map_to_users[agg_user_identifier]|={actual_u_id}
    
    
    users_aggregated_to_delete=set()
    for u_agg in users_aggregated_map_to_users:
        size_u_agg=len(users_aggregated_map_to_users[u_agg])
        #print u_agg,size_u_agg
        if size_u_agg>=size_aggregate_min:
            users_aggregated_map_details_array[u_agg]['NB_USER']=size_u_agg
            #users_aggregated_map_details_array[u_agg]['AGGREGATION_LEVEL']=1
            users_aggregated_map_votes[u_agg]=set()
            users_aggregated_to_votes_outcomes[u_agg]={}
            for v in v_ids:
                vector_associated=None
                flag_at_least_someone_voted=False
                for u in users_aggregated_map_to_users[u_agg]:
                    try:
                        v_u=users_to_votes_outcomes[u][v]
                        if not flag_at_least_someone_voted:
                            users_aggregated_map_votes[u_agg]|={v}
                        flag_at_least_someone_voted=True
                        if vector_associated is None:
                            vector_associated=tuple(v_u)
                        else :
                            vector_associated=tuple(vector_associated[i]+v_u[i] for i in range(len(v_u)))
                    except:
                        continue
                if flag_at_least_someone_voted:
                    users_aggregated_to_votes_outcomes[u_agg][v]=vector_associated 
        else :
            users_aggregated_to_delete|={u_agg}
            
    
    for u_agg in users_aggregated_to_delete:
        
        del users_aggregated_map_details_array[u_agg]
        del users_aggregated_map_to_users[u_agg]
    
    print 'DOONE'
    return users_aggregated_map_details_array.values(),users_aggregated_map_to_users,users_aggregated_map_votes,users_aggregated_to_votes_outcomes


def construct_user_aggregate(all_users_map_details_array,users_attributes,aggregation_attributes):
    users_aggregated_map_details_dict={}
    user_id_attr=users_attributes[0]
    users_aggregated_map_to_users={};users_aggregated_map_to_users_has_key=users_aggregated_map_to_users.has_key
    for u in all_users_map_details_array:
        actual_u_id=u[user_id_attr]

        agg_user_identifier=tuple([u[x] for x in aggregation_attributes]) if aggregation_attributes is not None else actual_u_id
        agg_user_identifier='agg'+'_'+'_'.join(agg_user_identifier) if aggregation_attributes is not None else actual_u_id
        considered_aggregation_attributes=users_attributes if aggregation_attributes is None else aggregation_attributes
        if not users_aggregated_map_to_users_has_key(agg_user_identifier):
            users_aggregated_map_to_users[agg_user_identifier]=set()
            users_aggregated_map_details_dict[agg_user_identifier]={att:u[att] if att in considered_aggregation_attributes else agg_user_identifier for att in users_attributes}
            users_aggregated_map_details_dict[agg_user_identifier]['NB_USERS']=0
        users_aggregated_map_to_users[agg_user_identifier]|={actual_u_id}
        users_aggregated_map_details_dict[agg_user_identifier]['NB_USERS']+=1

    return users_aggregated_map_details_dict,users_aggregated_map_to_users
        
#u_all_ids : the individuals ids on which the aggregates are built, u_agg_ids : loop only in this aggregates subset ids
def compute_aggregates_outcomes(v_ids,u_all_ids,u_agg_ids,users_aggregated_map_details_dict,users_aggregated_map_to_users,users_to_votes_outcomes,users_attributes,outcome_tuple_structure,size_aggregate_min=2):

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
            users_aggregated_map_votes[u_agg]=set()
            users_aggregated_to_votes_outcomes[u_agg]={}
            for v in v_ids:
                vector_associated=tuple(outcome_tuple_structure)
                flag_at_least_someone_voted=False
                for u in u_agg_ids_corresp:
                    try:
                        v_u=users_to_votes_outcomes[u][v]
                        flag_at_least_someone_voted=True

                        vector_associated=tuple(vector_associated[i]+v_u[i] for i in range_size_tuple)
                    except:
                        continue
                if flag_at_least_someone_voted:
                    users_aggregated_to_votes_outcomes[u_agg][v]=vector_associated 
                    users_aggregated_map_votes[u_agg]|={v}
            users_aggregated_map_details_dict_new[u_agg]=users_aggregated_map_details_dict[u_agg]
            users_aggregated_map_to_users_new[u_agg]=u_agg_ids_corresp
            users_all_ids_to_preserve|=u_agg_ids_corresp
        else :
            users_aggregated_to_delete|={u_agg}
            
    
    users_aggregated_to_preserve=users_aggregated_map_to_users.viewkeys()-users_aggregated_to_delete

    return users_aggregated_map_details_dict_new.values(),users_aggregated_map_to_users_new,users_aggregated_map_votes,users_aggregated_to_votes_outcomes,users_all_ids_to_preserve,users_aggregated_to_preserve,users_all_ids_visited,users_aggregated_ids_visited



def compute_aggregates_outcomes_rappel(v_ids,u_all_ids,u_agg_ids,users_aggregated_map_details_dict,users_aggregated_map_to_users,users_to_votes_outcomes,users_attributes,outcome_tuple_structure,size_aggregate_min=2,users_aggregated_to_votes_outcomes_param={},users_aggregated_map_votes_param={}):

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
            if u_agg_ids_corresp ==users_aggregated_map_to_users[u_agg]:
                users_aggregated_to_votes_outcomes[u_agg]=users_aggregated_to_votes_outcomes_param[u_agg]
                users_aggregated_map_votes[u_agg]=users_aggregated_map_votes_param[u_agg]
            else :
                users_aggregated_map_details_dict[u_agg]['NB_USERS']=size_u_agg
                users_aggregated_map_votes[u_agg]=set()
                users_aggregated_to_votes_outcomes[u_agg]={}
                for v in v_ids:
                    vector_associated=tuple(outcome_tuple_structure)
                    flag_at_least_someone_voted=False
                    for u in u_agg_ids_corresp:
                        try:
                            v_u=users_to_votes_outcomes[u][v]
                            flag_at_least_someone_voted=True
    
                            vector_associated=tuple(vector_associated[i]+v_u[i] for i in range_size_tuple)
                        except:
                            continue
                    if flag_at_least_someone_voted:
                        users_aggregated_to_votes_outcomes[u_agg][v]=vector_associated 
                        users_aggregated_map_votes[u_agg]|={v}
            users_aggregated_map_details_dict_new[u_agg]=users_aggregated_map_details_dict[u_agg]
            users_aggregated_map_to_users_new[u_agg]=u_agg_ids_corresp
            users_all_ids_to_preserve|=u_agg_ids_corresp
        else :
            users_aggregated_to_delete|={u_agg}
            
    
    users_aggregated_to_preserve=users_aggregated_map_to_users.viewkeys()-users_aggregated_to_delete

    return users_aggregated_map_details_dict_new.values(),users_aggregated_map_to_users_new,users_aggregated_map_votes,users_aggregated_to_votes_outcomes,users_all_ids_to_preserve,users_aggregated_to_preserve,users_all_ids_visited,users_aggregated_ids_visited



def compute_aggregates_outcomes_opt(v_ids,u_all_ids,u_agg_ids,users_aggregated_map_details_dict,users_aggregated_map_to_users,users_to_votes_outcomes,users_attributes,outcome_tuple_structure,size_aggregate_min=2,users_aggregated_to_votes_outcomes_param={}):
    timing=0
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
        users_all_ids_visited |= u_agg_ids_corresp
        if size_u_agg>=size_aggregate_min:
#             if u_agg_ids_corresp==users_aggregated_map_to_users[u_agg]:
#                 users_aggregated_map_to_users_new[u_agg]=u_agg_ids_corresp
#                 users_aggregated_map_details_dict_new[u_agg]=users_aggregated_map_details_dict[u_agg]
#                 users_aggregated_to_votes_outcomes[u_agg]=users_aggregated_to_votes_outcomes_param[u_agg]
#                 users_aggregated_map_votes[u_agg]=users_aggregated_to_votes_outcomes[u_agg].viewkeys()
#                 users_all_ids_to_preserve|=u_agg_ids_corresp
#                 continue
            users_aggregated_map_details_dict[u_agg]['NB_USERS']=size_u_agg
            users_aggregated_map_votes[u_agg]=set()
            users_aggregated_to_votes_outcomes[u_agg]={}
            #st=time()
            for v in v_ids:
                vector_associated=list(outcome_tuple_structure)
                flag_at_least_someone_voted=True
                for u in u_agg_ids_corresp:
                    try:
                        v_u=users_to_votes_outcomes[u][v]
                        flag_at_least_someone_voted=True
                        
                        vector_associated=[vector_associated[i]+v_u[i] for i in range_size_tuple] #map(add, vector_associated,v_u)#
                        
                    except:
                        continue
                if flag_at_least_someone_voted:
                    users_aggregated_to_votes_outcomes[u_agg][v]=vector_associated 
                    users_aggregated_map_votes[u_agg]|={v}
            #timing+=time()-st
            users_aggregated_map_details_dict_new[u_agg]=users_aggregated_map_details_dict[u_agg]
            users_aggregated_map_to_users_new[u_agg]=u_agg_ids_corresp
            users_all_ids_to_preserve|=u_agg_ids_corresp
        else :
            users_aggregated_to_delete|={u_agg}
            
    
    users_aggregated_to_preserve=users_aggregated_map_to_users.viewkeys()-users_aggregated_to_delete
    #print timing
    return users_aggregated_map_details_dict_new.values(),users_aggregated_map_to_users_new,users_aggregated_map_votes,users_aggregated_to_votes_outcomes,users_all_ids_to_preserve,users_aggregated_to_preserve,users_all_ids_visited,users_aggregated_ids_visited


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


def compute_similarity(votes_ids,user1_votes_outcome,user2_votes_outcome):
    nbvotes=0;similarity=0.;range3=range(0,3)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            ind_max_v1=0;max_v1=v1[0]
            ind_max_v2=0;max_v2=v2[0]
            for i in range3:
                if v1[i]>max_v1:
                    max_v1=v1[i]
                    ind_max_v1=i
                if v2[i]>max_v2:
                    max_v2=v2[i]
                    ind_max_v2=i
                                
            if ind_max_v1==ind_max_v2:
                similarity+=1 
        except:
            continue
        
    return similarity,nbvotes

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

def compute_similarity_memory(detailed_sim_matrix_ref,votes_ids,u1,u2):
    nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
    for key in votes_ids:
        try:
            v_pair=pairs[key]
            nbvotes+=1
            similarity+=v_pair 
        except:
            continue
        
    return similarity,nbvotes





def compute_similarity_matrix_memory_is_square(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids):
    similarity_matrix={}
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            if user2<=user1: similarity_matrix[user1][user2]=compute_similarity_memory(detailed_sim_matrix_ref,votes_ids,user1,user2)
    for user1 in users1_ids:
        for user2 in users2_ids:
            if user2<user1: similarity_matrix[user2][user1]=similarity_matrix[user1][user2]
    return similarity_matrix

def compute_similarity_matrix_memory_is_not_square(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids):
    similarity_matrix={}
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            similarity_matrix[user1][user2]=compute_similarity_memory(detailed_sim_matrix_ref,votes_ids,user1,user2)
    return similarity_matrix

def compute_similarity_matrix_memory(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,issquare=False):
    if issquare:
        return compute_similarity_matrix_memory_is_square(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids)
    else :
        return compute_similarity_matrix_memory_is_not_square(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids)


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
        
    header=dict((i,header) for (i,header) in zip(range(len(header)),header))
    rower=dict((i,rower) for (i,rower) in zip(range(len(rower)),rower))
    return matrix_general,matrix_pattern,rower,header

###############################################################################
BOUND1OR2=1
def compute_similarity_memory_lowerbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison):
    global BOUND1OR2
    
    if BOUND1OR2==1:
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        for key in votes_ids:#in votes_ids:
            try:
                v_pair=pairs[key]
                nbvotes+=1
                similarity+=v_pair 
            except:
                continue
        bound=max((threshold_comparaison-(nbvotes-similarity))/threshold_comparaison,0); 
    else :
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        pairs_sim_array=[];pairs_sim_array_append=pairs_sim_array.append
        for key in votes_ids:#in votes_ids:
            try:
                v_pair=pairs[key]
                nbvotes+=1
                similarity+=v_pair 
                #insort_left(pairs_sim_array,v_pair)
                pairs_sim_array_append(v_pair)
            except:
                continue
        bound=0.
        if nbvotes>=threshold_comparaison:
            if nbvotes>threshold_comparaison:
                pairs_sim_array=sorted(pairs_sim_array)
            for k in range(int(threshold_comparaison)):
                bound+=pairs_sim_array[k]
            bound/=float(threshold_comparaison)
    return similarity,nbvotes,bound


def compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison):
    global BOUND1OR2
    
    
    if BOUND1OR2==1:
        nbvotes=0;similarity=0.;pairs=detailed_sim_matrix_ref[u1][u2]
        for key in votes_ids:#in votes_ids:
            try:
                v_pair=pairs[key]
                nbvotes+=1
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
                v_pair=pairs[key]
                nbvotes+=1
                similarity+=v_pair 
                #insort_left(pairs_sim_array,v_pair)
                pairs_sim_array_append(v_pair)
            except:
                continue
        #bound=min(similarity/threshold_comparaison,1); 
        bound=0.
        if nbvotes>=threshold_comparaison:
            if nbvotes>threshold_comparaison:
                pairs_sim_array=sorted(pairs_sim_array,reverse=True)
            for k in range(int(threshold_comparaison)):
                bound+=pairs_sim_array[k]
            bound/=float(threshold_comparaison)
    return similarity,nbvotes,bound



LOWERORHIGHER=True

def compute_similarity_memory_with_bounds(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison,lower=LOWERORHIGHER):
    global LOWERORHIGHER
    if LOWERORHIGHER:
        return compute_similarity_memory_lowerbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison)
    else :
        return compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,u1,u2,threshold_comparaison)

def compute_similarity_matrix_memory_is_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison):
    
    similarity_matrix={}
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            if user2<=user1: similarity_matrix[user1][user2]=compute_similarity_memory_with_bounds(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison)
            #if user2<=user1: similarity_matrix[user1][user2]=compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison)
    for user1 in users1_ids:
        for user2 in users2_ids:
            if user2<user1: similarity_matrix[user2][user1]=similarity_matrix[user1][user2]
    return similarity_matrix

def compute_similarity_matrix_memory_is_not_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison):
    similarity_matrix={}
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            similarity_matrix[user1][user2]=compute_similarity_memory_with_bounds(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison)
            #similarity_matrix[user1][user2]=compute_similarity_memory_higherbound(detailed_sim_matrix_ref,votes_ids,user1,user2,threshold_comparaison)
    return similarity_matrix

def compute_similarity_matrix_memory_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,issquare=False,threshold_comparaison=1):
    if issquare:
        return compute_similarity_matrix_memory_is_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison)
    else :
        return compute_similarity_matrix_memory_is_not_square_withbound(detailed_sim_matrix_ref,votes_ids,users1_ids,users2_ids,threshold_comparaison)



def dsc_c_methodWITHHEATMAP(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):

    
    timing=0
    INITIALIZATION=time()
    interesting_patterns=[]
    #elementToShow='PROCEDURE_TITLE'#'movieTitle'
    elementToShow=votes_attributes[1]#'movieTitle'
    
    #########################GETTING CONFIGURATION PARAMETERS################################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',None)
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',None)
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',0)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',0)
    global  BOUND1OR2
    BOUND1OR2=configuration.get('upperbound',1)
    global LOWERORHIGHER
    if iwant == 'DISAGR_SUMDIFF':
        LOWERORHIGHER=True
    elif iwant=='AGR_SUMDIFF':
        LOWERORHIGHER=False
    ##########################################################################################
    
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    #print all_users_map_details
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())

    all_users_map_details_array=all_users_map_details.values()
    all_users_ids=set(all_users_map_details.keys())
    outcome_tuple_structure=tuple(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    ################################# 
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    
    
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)

    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array

    ########################

    users1_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    issquare=users1_ids==users2_ids
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    
    ######
    userpairssimsdetails={}
    for u1 in users1_ids:
        userpairssimsdetails[u1]={}
        for u2 in users2_ids:
            userpairssimsdetails[u1][u2]={v:similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes[u1], users2_aggregated_to_votes_outcomes[u2],u1,u2,comparaison_measure)[0] for v in users1_aggregated_to_votes_outcomes[u1].viewkeys()&users2_aggregated_to_votes_outcomes[u2].viewkeys()}
            
            
                
#             spairs=sorted(userpairssimsdetails[u1][u2].iteritems(),key=lambda x : x[1])
#             userpairssimsdetails[u1][u2]={spairs[x][0]:{'sim':spairs[x][1],'rank':x} for x in range(len(spairs))}

            
    ######
    reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_ids,users2_ids,comparaison_measure)
    
    #enumerator=enumerator_complex_from_dataset_new_config(votes_map_details_array, attributes, {'users1':users1_aggregated_map_votes,'users2':users2_aggregated_map_votes},objet_id_attribute=vote_id_attribute,verbose=True)
    
    #enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, attributes, {'users1':users1_aggregated_map_votes,'users2':users2_aggregated_map_votes},threshold=threshold_pair_comparaison,verbose=True)
    
    enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, attributes, {},threshold=threshold_pair_comparaison,verbose=True)
    INITIALIZATION=time()-INITIALIZATION
    old_lvl=-1;visited=0;modelcomputed=0;verified=0
    #keep_e_config=[];keep_e_config_append=keep_e_config.append;alpha=0.5;beta=0.5
    
    for e_p,e_label,e_config in enumerator:
        #########################################BEAM SEARCH#############################
#         if old_lvl<>e_config.get('lvl',0):
#             old_lvl+=1
#             sortedbyqual = sorted(keep_e_config,key = lambda x : x[2], reverse=True)[3:]
#             flag_to_cont=False
#             for saved_e_p,saved_e_config,saved_quality,saved_borne_max in sortedbyqual:
#                 saved_e_config['flag']=False
#                 if saved_e_p==e_p:
#                     flag_to_cont=True
#             keep_e_config=[];keep_e_config_append=keep_e_config.append
#             if flag_to_cont:
#                 continue
        #########################################BEAM SEARCH#############################    
        
#         #########################################ONE PIK#############################
#         if old_lvl<>e_config.get('lvl',0):
#             old_lvl+=1
#             sortedbyqual = sorted(keep_e_config,key = lambda x : x[2], reverse=True)
#             suming=sum(x[2] for x in keep_e_config)
#             if suming>0:
#                 
#                 rand=random();to_keep=None
#                 print rand
#                 qualMontant=0;ind=0;flaggosef=False
#                 for saved_e_p,saved_e_config,saved_quality,saved_upper_bound in sortedbyqual:
#                     qualMontant+=saved_quality/suming
#                     if rand<qualMontant and not flaggosef:
#                         flaggosef=True
#                         to_keep=saved_e_p
#                     else :
#                         saved_e_config['flag']=False
#                     
#                 keep_e_config=[];keep_e_config_append=keep_e_config.append    
#                 if to_keep <> e_p and to_keep is not None:
#                     continue
#             else :
#                 keep_e_config=[];keep_e_config_append=keep_e_config.append    
            #print suming,len(keep_e_config), rand
#         #########################################BEAM SEARCH#############################   
        visited+=1      
            
            
            
        
        e_votes=e_config['support']

#         nb_votes=len(e_votes) 
#         if nb_votes<=threshold_pair_comparaison :
#             e_config['flag']=False
#             if nb_votes<threshold_pair_comparaison:
#                 continue
        
        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            dossiers_ids |= {obj[elementToShow]}
     

        

        
        users1_ids_set={u for u in users1_aggregated_map_votes if len(users1_aggregated_map_votes[u]&v_ids)>=threshold_pair_comparaison} 
        users2_ids_set={u for u in users2_aggregated_map_votes if len(users2_aggregated_map_votes[u]&v_ids)>=threshold_pair_comparaison}
        
        if len(users1_ids_set)==0 or len(users2_ids_set)==0:
            continue
        
        modelcomputed+=1 
        #pattern_matrix_dic=compute_similarity_matrix_memory(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare)
        st=time()
        pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison)
        reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
        timing+=time()-st
        nb_users_voted=len(users1_ids)*len(users2_ids)
        if len(users1_ids_set)<=0 or len(users2_ids_set)<=0:
            continue
        quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))

        
        if (pruning and (borne_max_quality<quality_threshold or borne_max_quality==0)):
            e_config['flag']=False
            continue
        verified+=1
        ##################HEURISTIC####################
        #keep_e_config_append((e_p,e_config,quality,borne_max_quality))
        ##################HEURISTIC####################
            #raw_input('...')
        
        
        if (quality>=quality_threshold):
            indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
            if cover_threshold<=1:
                array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
            if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                if len(indices_to_remove_if_inserted)>0: 
                    interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]

                ############NEW FOR HEATMAP############
                pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                
                #######################################
                label=e_label
    
                dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                #dossiers_voted=[]
                interesting_patterns.append([e_p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                if len(interesting_patterns)>top_k:
                    interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                    quality_threshold=interesting_patterns[-1][3]
                    
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '.......',visited,modelcomputed,verified,timing,'.......'


    
def dsc_c_method(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    AllStatus=[]
    itemsRANGE=[500,1000,1500]
    
    #for itemNB in itemsRANGE:
    
    initialisation=time()
    
    interesting_patterns=[]
    #elementToShow='PROCEDURE_TITLE'#'movieTitle'
    #elementToShow='movieTitle'
    
    #########################GETTING CONFIGURATION PARAMETERS################################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    
    global  BOUND1OR2
    
    BOUND1OR2=configuration.get('upperbound',1)
    global LOWERORHIGHER
    if iwant == 'DISAGR_SUMDIFF':
        LOWERORHIGHER=True
    elif iwant=='AGR_SUMDIFF':
        LOWERORHIGHER=False
        
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',None)
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',None)
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',0)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',0)
    
    nb_items_to_study=configuration.get('nb_items',None)
    #nb_items_to_study=itemNB
    nb_users_to_study=configuration.get('nb_users',None)
    
    ##########################################################################################
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute,nb_items=nb_items_to_study,nb_users=nb_users_to_study)
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())
    all_users_map_details_array=all_users_map_details.values()
    all_users_ids=set(all_users_map_details.keys())
    outcome_tuple_structure=tuple(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    nb_ratings = sum(len(all_users_map_votes[k]) for k in  all_users_map_votes)
    
    ########################DOSSIERS_PARTICULAR##########################
#     dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
#     for v_id,v_value in votes_map_details.iteritems():
#         dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    ##################################################################  
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    
    
    
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    
    CLOSED=configuration['closed']
    parameters={
        'sigma_context':threshold_pair_comparaison,
        'sigma_u1':1,
        'sigma_u2':1,
        'sigma_agg_u1':nb_aggregation_min_user1,
        'sigma_agg_u2':nb_aggregation_min_user2,
        '#ratings':nb_ratings,
        '#items':len(all_votes_id),
        '#users1':len(all_users1_ids),
        '#usersagg_1':len(users1_agg_ids),
        '#users2':len(all_users2_ids),
        '#usersagg_2':len(users2_agg_ids),
        '#attr_items':len(attributes),
        'attr_items':[(x['name'],x['type']) for x in attributes if x['name'] in votes_attributes],
        '#attr_users':len([(x['name'],x['type']) for x in attributes if x['name'] in users_attributes]),
        'attr_users':[(x['name'],x['type']) for x in attributes if x['name'] in users_attributes],
        '#attr_aggregate':len(aggregationAttributes_user1),
        'attr_aggregate':[aggregationAttributes_user1],
        'closed':CLOSED,
        'prune':pruning,
        'sigma_quality':quality_threshold,
        'top_k':top_k,
        'quality_measure':iwant,
        'similarity_measure':comparaison_measure,
        'upperbound_type':BOUND1OR2
    }
    
    
                                  
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)

    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array

    ################################################

    users1_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    issquare=users1_ids==users2_ids
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    initialisation=time()-initialisation
    
    
    
    
    
    timing=time()
    ######
    userpairssimsdetails={}
    for u1 in users1_ids:
        userpairssimsdetails[u1]={}
        for u2 in users2_ids:
            userpairssimsdetails[u1][u2]={v:similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes[u1], users2_aggregated_to_votes_outcomes[u2],u1,u2,comparaison_measure)[0] for v in users1_aggregated_to_votes_outcomes[u1].viewkeys()&users2_aggregated_to_votes_outcomes[u2].viewkeys()}
    ######
    
    
    
    reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_ids,users2_ids,comparaison_measure,issquare=issquare)
    
    #enumerator=enumerator_complex_from_dataset_new_config(votes_map_details_array, attributes, {'users1':users1_aggregated_map_votes,'users2':users2_aggregated_map_votes},objet_id_attribute=vote_id_attribute,verbose=True)
    #enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, attributes, {'users1':users1_aggregated_map_votes,'users2':users2_aggregated_map_votes},threshold=threshold_pair_comparaison,verbose=True)
    if CLOSED:
        enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, attributes, {},threshold=threshold_pair_comparaison,verbose=False)
    else :
        enumerator=enumerator_complex_from_dataset_new_config(votes_map_details_array, attributes, {},objet_id_attribute=vote_id_attribute,threshold=threshold_pair_comparaison,verbose=False)
    visited=0
    for e_p,e_label,e_config in enumerator:
        visited+=1      
        e_votes=e_config['support']

        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            #dossiers_ids |= {obj[elementToShow]}
     
        users1_ids_set={u for u in users1_aggregated_map_votes if len(users1_aggregated_map_votes[u]&v_ids)>=threshold_pair_comparaison} 
        users2_ids_set={u for u in users2_aggregated_map_votes if len(users2_aggregated_map_votes[u]&v_ids)>=threshold_pair_comparaison}
        
        if len(users1_ids_set)==0 or len(users2_ids_set)==0:
            continue
        
        pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison)
        reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
        
        nb_users_voted=len(users1_ids)*len(users2_ids)
        if len(users1_ids_set)<=0 or len(users2_ids_set)<=0:
            continue
        quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))

        
        if (pruning and (borne_max_quality<quality_threshold or borne_max_quality==0)):
            e_config['flag']=False
            continue
       
        if (quality>=quality_threshold):
            indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
            if cover_threshold<=1:
                array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
            if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                if len(indices_to_remove_if_inserted)>0: 
                    interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]

                ############NEW FOR HEATMAP############
                dataset_stats=[]
                #######################################
                label=e_label
    
                #dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                dossiers_voted=[]
                interesting_patterns.append([e_p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                if len(interesting_patterns)>top_k:
                    interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                    quality_threshold=interesting_patterns[-1][3]
    
    timing=time()-timing   
    #statusmamus=[e_config['nb_visited'][0],e_config['nb_visited'][1],initialisation,timing]             
    statusmamus={
        '#all_visited_context':e_config['nb_visited'][0],
        '#candidates':visited,
        '#init':initialisation,
        '#timespent':timing,
        '#patterns':len(interesting_patterns),
        'max_quality_found':max(interesting_patterns[i][3] for i in range(len(interesting_patterns))) if len(interesting_patterns)>0 else 0
    }
    statusmamus.update(parameters)
    AllStatus.append(statusmamus)
    
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in [(1,2,3,4,5,6,7)]:
        
        yield p,label,dataset_stats,quality,borne_max_quality,AllStatus
    
    #stdout.write('\r.......'+str('%.2f' % (timing+initialisation))+'.......')

    
    
def dsc_cuu_method_old(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    ##########"
    #original_mepsStatistics,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    dataset_original=[]#datasetStatistics(original_mepsStatistics, original_mepsMeta,votes_attributes,users_attributes,position_attribute)
    ########"
    
    timing=0
    interesting_patterns=[]
    elementToShow='PROCEDURE_TITLE'
    
    #########################GETTING CONFIGURATION PARAMETERS################################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',['NATIONAL_PARTY'])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',['NATIONAL_PARTY'])
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    ##########################################################################################
    
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    #print all_users_map_details
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())

    all_users_map_details_array=all_users_map_details.values()
    all_users_ids=set(all_users_map_details.keys())
    outcome_tuple_structure=tuple(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=tuple(0 for i in range(outcome_tuple_size))
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    ################################# 
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    
    
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
      
    #users_aggregated_map_details_array,users_aggregated_map_to_users,users_aggregated_map_votes,users_aggregated_to_votes_outcomes=compute_aggregates_outcomes_OLD(all_votes_id, all_users_map_details_array, users_to_votes_outcomes, users_attributes, ['NATIONAL_PARTY'])
    
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    
    users_aggregtated_to_votes_outcomes=users1_aggregated_to_votes_outcomes.copy()
    users_aggregtated_to_votes_outcomes.update(users2_aggregated_to_votes_outcomes)
    users_aggregated_map_votes=users1_aggregated_map_votes.copy()
    users_aggregated_map_votes.update(users2_aggregated_map_votes)
    #users1_to_votes_outcomes=users1_aggregated_to_votes_outcomes
    #users2_to_votes_outcomes=users2_aggregated_to_votes_outcomes
#     users1_map_votes=users1_aggregated_map_votes
#     users2_map_votes=users2_aggregated_map_votes
    ########################
    
    
    
    
    
    
    
    users_ids=set([obj[users_id_attribute] for obj in all_users_map_details_array])
    users1_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    nb_users_voted=len(users1_ids)*len(users2_ids)
    
    
    ######
    userpairssimsdetails={}
    for u1 in users1_ids:
        userpairssimsdetails[u1]={}
        for u2 in users2_ids:
            userpairssimsdetails[u1][u2]={v:compute_similarity({v}, users_aggregtated_to_votes_outcomes[u1], users_aggregtated_to_votes_outcomes[u2])[0] for v in users_aggregtated_to_votes_outcomes[u1].viewkeys()&users_aggregtated_to_votes_outcomes[u2].viewkeys()}
    ######
    
    reference_matrix_dic=compute_similarity_matrix(users_aggregtated_to_votes_outcomes,all_votes_id,users1_ids,users2_ids,comparaison_measure)
    
    enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users':users_aggregated_map_votes},True)
    
    for e_p,e_label,e_config in enumerator:
        
        e_votes=e_config['support']
        e_users=e_config['users']

        nb_votes=len(e_votes) 
        if nb_votes<=threshold_pair_comparaison :
            e_config['flag']=False
            if nb_votes<threshold_pair_comparaison:
                continue
        
        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            dossiers_ids |= {obj[elementToShow]}
     
        new_e_users={}
        users_ids_set=set()
        max_votes_pairwise=0
         
        for key in e_users:
            value=e_users[key]
            votes_user=(value & v_ids)
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                new_e_users[key]=votes_user
                users_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
        e_config['users']=new_e_users    
         
        if max_votes_pairwise<threshold_pair_comparaison :
            e_config['flag']=False
            continue
        
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set

        
        for u1_p,u1_label,u1_config in enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{},False):
            u1_p_set_users=set(x[users_id_attribute] for x in u1_config['support'])
            users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_ids_set, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
            for u2_p,u2_label,u2_config in enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{},False):
                e_u_p=e_p + u1_p + u2_p
                e_u_label=e_label + u1_label + u2_label
                u2_p_set_users=set(x[users_id_attribute] for x in u2_config['support'])
                users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_ids_set-users1_aggregated_to_preserve, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
                users_aggregtated_to_votes_outcomes_pattern=users1_aggregated_to_votes_outcomes_pattern.copy()
                users_aggregtated_to_votes_outcomes_pattern.update(users2_aggregated_to_votes_outcomes_pattern)
                users_aggregated_map_votes_pattern=users1_aggregated_map_votes_pattern.copy()
                users_aggregated_map_votes_pattern.update(users2_aggregated_map_votes_pattern)
                
                users_ids_set_pattern=set()
                #new_e_users_pattern={}
                
                for key in users_aggregated_map_votes_pattern:
                    value=users_aggregated_map_votes_pattern[key]
                    votes_user=(value & v_ids)
                    len_votes_user=len(votes_user)
                    if len_votes_user>=threshold_pair_comparaison:
                        #new_e_users_pattern[key]=votes_user
                        users_ids_set_pattern|={key}
                        max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
                
                if max_votes_pairwise<threshold_pair_comparaison :
                    #e_config['flag']=False
                    continue
                
                users1_ids_set_pattern=users1_aggregated_to_preserve & users_ids_set_pattern
                users2_ids_set_pattern=users2_aggregated_to_preserve & users_ids_set_pattern
        
                st=time()
                pattern_matrix_dic=compute_similarity_matrix(users_aggregtated_to_votes_outcomes,v_ids,users1_ids_set_pattern,users2_ids_set_pattern,comparaison_measure)
                #pattern_matrix_dic=compute_similarity_matrix_memory(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set)
                timing+=time()-st
                reference_matrix, pattern_matrix,header,rower = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                
                #nb_users_voted=len(users1_ids)*len(users2_ids)
                coeff=lambda nb_voter_1,nb_voter_2 : (log(nb_voter_2+nb_voter_1+1,2)/log(len(users2_ids)+len(users1_ids)+1,2))/float(nb_voter_2+nb_voter_1)
                quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,iwant,coeff=coeff)
                
                
#                 if (pruning and borne_max_quality<quality_threshold):
#                     e_config['flag']=False
#                     continue
                
                if (quality>=quality_threshold):
                    indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                    if cover_threshold<=1:
                        array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                        array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                        indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                        indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
                    if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                        if len(indices_to_remove_if_inserted)>0: 
                            interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
        
                        #dataset_stats=datasetStatistics(returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                        dataset_stats=dataset_original
                        label=e_label
            
                        dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                        #dossiers_voted=[]
                        interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                        if len(interesting_patterns)>top_k:
                            interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                            quality_threshold=interesting_patterns[-1][3]
                    
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '.......',timing,'.......'
    

def dsc_uuc_method_rappel(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    timing=0
    interesting_patterns=[]
    elementToShow='PROCEDURE_TITLE'
    
    #########################GETTING CONFIGURATION PARAMETERS################################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',['NATIONAL_PARTY'])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',['NATIONAL_PARTY'])
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    ratio_agg_threshold=configuration.get('ratio_agg_threshold',0.3)
    
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())
    all_users_map_details_array=all_users_map_details.values()
    all_users_ids=set(all_users_map_details.keys())
    outcome_tuple_structure=list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    u1_isequalto_u2=(all_users1_ids==all_users2_ids)
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    
    #len_starting_users1_ids=len(users1_all_ids_to_preserve)
    
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    
    #users_aggregtated_to_votes_outcomes_ref=users1_aggregated_to_votes_outcomes.copy()
    #users_aggregtated_to_votes_outcomes_ref.update(users2_aggregated_to_votes_outcomes)
    
    reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure)
    #print reference_matrix_dic
    users_map_details_array_filtered_user1=[row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve]
    users_map_details_array_filtered_user2=[row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve]
    
    users_map_details_array_filtered_user1 = sorted(users_map_details_array_filtered_user1,key=lambda x : x[users_id_attribute])
    users_map_details_array_filtered_user2 = sorted(users_map_details_array_filtered_user2,key=lambda x : x[users_id_attribute])
    
    len_users1_all_starting=len(users_map_details_array_filtered_user1)
    len_users2_all_starting=len(users_map_details_array_filtered_user2)
    
    #print len_users1_all_starting,len_users2_all_starting
    
    
    
    visited_aggregated_outcome={}
    visited_1_trace=set()
    visited_2_trace=set()
    visited_aggregated_outcome_has_key=visited_aggregated_outcome.has_key
    
    enum_u1=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{'FORBIDDEN_U1':[],'users1_aggregated_map_to_users_pattern':users1_aggregated_map_to_users,'users1_aggregated_to_votes_outcomes_pattern':users1_aggregated_to_votes_outcomes,'users1_aggregated_map_votes_pattern':users1_aggregated_map_votes,'users1_aggregated_to_preserve':users1_agg_ids},False)
    index_visited=0
    for u1_p,u1_label,u1_config in enum_u1:
        visited_1=False
        u1_p_tuple_users=tuple(x[users_id_attribute] for x in u1_config['support'])
        u1_p_set_users=set(u1_p_tuple_users)
        ratio_u1_p=len(u1_p_set_users)/float(len_users1_all_starting)
        if ratio_u1_p<ratio_agg_threshold:
            u1_config['flag']=False
            continue
        st=time()
#         users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes_opt(all_votes_id,u1_p_set_users,precedent_users1_aggregated_to_preserve, users1_aggregated_map_details,precedent_users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,users_aggregated_to_votes_outcomes_param=precedent_users1_aggregated_to_votes_outcomes)
        
        if not visited_aggregated_outcome_has_key(u1_p_tuple_users):
            prec_agg_map_users=u1_config['users1_aggregated_map_to_users_pattern']
            prec_agg_map_votes=u1_config['users1_aggregated_map_votes_pattern']
            prec_agg_outcome=u1_config['users1_aggregated_to_votes_outcomes_pattern']
            prec_agg_ids=u1_config['users1_aggregated_to_preserve']
            
#             users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=\
#                 compute_aggregates_outcomes_rappel(all_votes_id,
#                                             u1_p_set_users,
#                                             prec_agg_ids, 
#                                             users1_aggregated_map_details,
#                                             prec_agg_map_users, 
#                                             all_users_to_votes_outcomes, 
#                                             users_attributes,
#                                             outcome_tuple_structure,
#                                             size_aggregate_min=nb_aggregation_min_user1,
#                                             users_aggregated_to_votes_outcomes_param=prec_agg_outcome,
#                                             users_aggregated_map_votes_param=prec_agg_map_votes)
            
            users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
            
            u1_config['users1_aggregated_map_to_users_pattern']=users1_aggregated_map_to_users_pattern
            u1_config['users1_aggregated_map_votes_pattern']=users1_aggregated_map_votes_pattern
            u1_config['users1_aggregated_to_votes_outcomes_pattern']=users1_aggregated_to_votes_outcomes_pattern
            u1_config['users1_aggregated_to_preserve']=users1_aggregated_to_preserve
            
            visited_aggregated_outcome[u1_p_tuple_users]={
                    'map_to_votes':users1_aggregated_map_votes_pattern,
                    'votes_outcomes':users1_aggregated_to_votes_outcomes_pattern,
                    'users_all_ids':users1_all_ids_to_preserve,
                    'users_agg_ids':users1_aggregated_to_preserve,
                    'agg_map_users':users1_aggregated_map_to_users_pattern
            }
            
        else :
            cur_visited = visited_aggregated_outcome[u1_p_tuple_users]
            users1_aggregated_map_votes_pattern=cur_visited['map_to_votes']
            users1_aggregated_to_votes_outcomes_pattern=cur_visited['votes_outcomes']
            users1_all_ids_to_preserve=cur_visited['users_all_ids']
            users1_aggregated_to_preserve=cur_visited['users_agg_ids']
            users1_aggregated_map_to_users_pattern=cur_visited['agg_map_users']
            
            visited_1_trace|={u1_p_tuple_users}
            
            u1_config['users1_aggregated_map_to_users_pattern']=users1_aggregated_map_to_users_pattern
            u1_config['users1_aggregated_map_votes_pattern']=users1_aggregated_map_votes_pattern
            u1_config['users1_aggregated_to_votes_outcomes_pattern']=users1_aggregated_to_votes_outcomes_pattern
            u1_config['users1_aggregated_to_preserve']=users1_aggregated_to_preserve
            
        #users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve


        ratio_u1_p=len(users1_all_ids_to_preserve)/float(len_users1_all_starting)
        if ratio_u1_p<ratio_agg_threshold:
            u1_config['flag']=False
            continue
        
        
        timing+=time()-st
#         if True:
#             index_visited+=1
#             print u1_p,index_visited,len(users1_all_ids_to_preserve),ratio_u1_p
#             continue

        #users_map_details_array_filtered_user2_context=[row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in all_users2_ids - users1_all_ids_visited]
        enum_u2=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{'users2_aggregated_map_to_users_pattern':users2_aggregated_map_to_users,'users2_aggregated_to_votes_outcomes_pattern':users2_aggregated_to_votes_outcomes,'users2_aggregated_map_votes_pattern':users2_aggregated_map_votes,'users2_aggregated_to_preserve':users2_agg_ids},False)
        flaggy_u2_first=True
        for u2_p,u2_label,u2_config in enum_u2: 
#             if not (u1_p[1]==['F'] and u2_p[1]==['M'] and u1_p[0]==u2_p[0]):
#                 continue
            u2_p_tuple_users=tuple(x[users_id_attribute] for x in u2_config['support'])
            u2_p_set_users=set(u2_p_tuple_users)
            ratio_u2_p=len(u2_p_set_users)/float(len_users2_all_starting)
            if ratio_u2_p<ratio_agg_threshold:
                u2_config['flag']=False
                if flaggy_u2_first:
                    u1_config['flag']=False
                continue
            
            if u2_p_set_users<u1_p_set_users :
                u2_config['flag']=False
                continue
            if u2_p_set_users>u1_p_set_users:
                flaggy_u2_first=False
                continue
            
            st=time()

            
            if not visited_aggregated_outcome_has_key(u2_p_tuple_users):
                
                prec_agg_map_users2=u2_config['users2_aggregated_map_to_users_pattern']
                prec_agg_map_votes2=u2_config['users2_aggregated_map_votes_pattern']
                prec_agg_outcome2=u2_config['users2_aggregated_to_votes_outcomes_pattern']
                prec_agg_ids2=u2_config['users2_aggregated_to_preserve']
                
#                 users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=\
#                     compute_aggregates_outcomes_rappel(all_votes_id,
#                                                 u2_p_set_users,
#                                                 prec_agg_ids2, 
#                                                 users2_aggregated_map_details,
#                                                 prec_agg_map_users2, 
#                                                 all_users_to_votes_outcomes, 
#                                                 users_attributes,
#                                                 outcome_tuple_structure,
#                                                 size_aggregate_min=nb_aggregation_min_user1,
#                                                 users_aggregated_to_votes_outcomes_param=prec_agg_outcome2,
#                                                 users_aggregated_map_votes_param=prec_agg_map_votes2)
                
                users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
                visited_aggregated_outcome[u2_p_tuple_users]={
                    'map_to_votes':users2_aggregated_map_votes_pattern,
                    'votes_outcomes':users2_aggregated_to_votes_outcomes_pattern,
                    'users_all_ids':users2_all_ids_to_preserve,
                    'users_agg_ids':users2_aggregated_to_preserve,
                    'agg_map_users':users2_aggregated_map_to_users_pattern
                }
                
                u2_config['users2_aggregated_map_to_users_pattern']=users2_aggregated_map_to_users_pattern
                u2_config['users2_aggregated_map_votes_pattern']=users2_aggregated_map_votes_pattern
                u2_config['users2_aggregated_to_votes_outcomes_pattern']=users2_aggregated_to_votes_outcomes_pattern
                u2_config['users2_aggregated_to_preserve']=users2_aggregated_to_preserve
                
            else :
                if (u2_p_tuple_users in visited_1_trace and u1_p_tuple_users in visited_2_trace) or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
                    continue
                cur_visited = visited_aggregated_outcome[u2_p_tuple_users]
                users2_aggregated_map_votes_pattern=cur_visited['map_to_votes']
                users2_aggregated_to_votes_outcomes_pattern=cur_visited['votes_outcomes']
                users2_all_ids_to_preserve=cur_visited['users_all_ids']
                users2_aggregated_to_preserve=cur_visited['users_agg_ids']
                users2_aggregated_map_to_users_pattern=cur_visited['agg_map_users']
                visited_2_trace|={u2_p_tuple_users}
                
                u2_config['users2_aggregated_map_to_users_pattern']=users2_aggregated_map_to_users_pattern
                u2_config['users2_aggregated_map_votes_pattern']=users2_aggregated_map_votes_pattern
                u2_config['users2_aggregated_to_votes_outcomes_pattern']=users2_aggregated_to_votes_outcomes_pattern
                u2_config['users2_aggregated_to_preserve']=users2_aggregated_to_preserve
            
            timing+=time()-st
            ratio_u2_p=len(users2_all_ids_to_preserve)/float(len_users2_all_starting)
            if ratio_u2_p<ratio_agg_threshold:
                u2_config['flag']=False
                continue
            print u1_p,u2_p,len(users1_all_ids_to_preserve),len(users2_all_ids_to_preserve),ratio_u1_p,ratio_u2_p,index_visited
            
            
            
#             if True:
#                 index_visited+=1
#                 print u1_p,u2_p,ratio_u1_p,ratio_u2_p,index_visited
#                 continue
            


            issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
            #print issquare
            reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,all_votes_id,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
            #print reference_matrix_dic
            enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},False)
            
            
            ######
            userpairssimsdetails={}
            for u1 in users1_aggregated_to_preserve:
                userpairssimsdetails[u1]={}
                for u2 in users2_aggregated_to_preserve:
                    userpairssimsdetails[u1][u2]={v:similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],comparaison_measure)[0] for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys()}
            ######
            
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            st=time()
            if nb_users_voted>0:
                flaggy_context=True
                for e_p,e_label,e_config in enumerator_contexts:
                    index_visited+=1
                    e_u_p=e_p + u1_p + u2_p
                    e_u_label=e_label + u1_label + u2_label
                    e_votes=e_config['support']
                    e_users_1=e_config['users1']
                    e_users_2=e_config['users2']
                    nb_votes=len(e_votes) 
                    if nb_votes<=threshold_pair_comparaison :
                        e_config['flag']=False
                        if nb_votes<threshold_pair_comparaison:
                            continue
                    
                    v_ids=set()
                    dossiers_ids=set()
                    
                    for obj in e_votes:
                        v_ids|={obj[vote_id_attribute]}
                        dossiers_ids |= {obj[elementToShow]}
                 
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
            
                
#                     if len(users1_ids_set)==0 or len(users2_ids_set)==0:
#                         continue
                    
                    #pattern_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,v_ids,users1_ids_set,users2_ids_set,comparaison_measure)
                    pattern_matrix_dic=compute_similarity_matrix_memory(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare)
                    #print reference_matrix_dic
                    #print pattern_matrix_dic
                    
                    reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                    quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))
                    if (pruning and borne_max_quality<quality_threshold):
                        e_config['flag']=False
#                         if flaggy_context:
#                             u2_config['flag']=False
#                             if flaggy_u2_first:
#                                 u1_config['flag']=False
                        continue
#                     if e_p==[['']]:
#                         print reference_matrix_dic
#                         print pattern_matrix_dic
#                         print quality
#                         raw_input('...')
                    
                    #print quality,e_u_p
                    #raw_input('...')
                    if (quality>=quality_threshold):
                        indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                        if cover_threshold<=1:
                            array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                            array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                            indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                            indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
                        if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                            if len(indices_to_remove_if_inserted)>0: 
                                interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
            
                            #dataset_stats=datasetStatistics(returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                            dataset_stats=[]
                            label=e_label
                            
                            ############NNNEEEW FOR HEATMAP
#                             pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
#                             reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
#                             dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                            dataset_stats=[]
                            #################################
                            
                            dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                            #dossiers_voted=[]
                            interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                            if len(interesting_patterns)>top_k:
                                interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                                quality_threshold=interesting_patterns[-1][3]
                    flaggy_context=False            
#             else:
#                 u2_config['flag']=False
#                 if flaggy_u2_first:
#                     u1_config['flag']=False
            #timing+=time()-st        
            flaggy_u2_first=False          
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '.......',timing,index_visited,'.......'

    
def dsc_uuc_method_HEATMAP(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    timing=0
    interesting_patterns=[]
    #elementToShow='PROCEDURE_TITLE'
    #elementToShow='movieTitle'
    elementToShow=votes_attributes[1]
    
    #########################GETTING CONFIGURATION PARAMETERS################################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',['NATIONAL_PARTY'])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',['NATIONAL_PARTY'])
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    ratio_agg_threshold=configuration.get('ratio_agg_threshold',0.01)
    threshold_nb_users_1=configuration.get('threshold_nb_users_1',1)
    threshold_nb_users_2=configuration.get('threshold_nb_users_2',1)
    
    global  BOUND1OR2
    BOUND1OR2=configuration.get('upperbound',1)
    global LOWERORHIGHER
    if iwant == 'DISAGR_SUMDIFF':
        LOWERORHIGHER=True
    elif iwant=='AGR_SUMDIFF':
        LOWERORHIGHER=False
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())
    all_users_map_details_array=all_users_map_details.values()
    all_users_ids=set(all_users_map_details.keys())
    outcome_tuple_structure=list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    u1_isequalto_u2=(all_users1_ids==all_users2_ids)
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    
    #len_starting_users1_ids=len(users1_all_ids_to_preserve)
    
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    
    #users_aggregtated_to_votes_outcomes_ref=users1_aggregated_to_votes_outcomes.copy()
    #users_aggregtated_to_votes_outcomes_ref.update(users2_aggregated_to_votes_outcomes)
    
    reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure,issquare=(users1_all_ids_to_preserve==users2_all_ids_to_preserve))
    #print reference_matrix_dic
    users_map_details_array_filtered_user1=[row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve]
    users_map_details_array_filtered_user2=[row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve]
    
    users_map_details_array_filtered_user1 = sorted(users_map_details_array_filtered_user1,key=lambda x : x[users_id_attribute])
    users_map_details_array_filtered_user2 = sorted(users_map_details_array_filtered_user2,key=lambda x : x[users_id_attribute])
    
    len_users1_all_starting=len(users_map_details_array_filtered_user1)
    len_users2_all_starting=len(users_map_details_array_filtered_user2)
    
    #print len_users1_all_starting,len_users2_all_starting
    
    
    
    visited_aggregated_outcome={}
    visited_1_trace_map={}
    visited_1_trace=set()
    visited_2_trace=set()
    visited_aggregated_outcome_has_key=visited_aggregated_outcome.has_key
    
    enum_u1=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1)
    index_visited=0
    for u1_p,u1_label,u1_config in enum_u1:
        visited_1=False
        u1_p_tuple_users=tuple(x[users_id_attribute] for x in u1_config['support'])
        u1_p_set_users=set(u1_p_tuple_users)
        ratio_u1_p=len(u1_p_set_users)/float(len_users1_all_starting)
        if ratio_u1_p<ratio_agg_threshold:
            u1_config['flag']=False
            continue
        st=time()
#         users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes_opt(all_votes_id,u1_p_set_users,precedent_users1_aggregated_to_preserve, users1_aggregated_map_details,precedent_users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,users_aggregated_to_votes_outcomes_param=precedent_users1_aggregated_to_votes_outcomes)
        if not u1_p_tuple_users in visited_1_trace_map:
            visited_1_trace_map[u1_p_tuple_users]=set()
            
            
        if not visited_aggregated_outcome_has_key(u1_p_tuple_users):
            users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)

            
            visited_aggregated_outcome[u1_p_tuple_users]={
                    'map_to_votes':users1_aggregated_map_votes_pattern,
                    'votes_outcomes':users1_aggregated_to_votes_outcomes_pattern,
                    'users_all_ids':users1_all_ids_to_preserve,
                    'users_agg_ids':users1_aggregated_to_preserve
            }
            
        else :
            cur_visited = visited_aggregated_outcome[u1_p_tuple_users]
            users1_aggregated_map_votes_pattern=cur_visited['map_to_votes']
            users1_aggregated_to_votes_outcomes_pattern=cur_visited['votes_outcomes']
            users1_all_ids_to_preserve=cur_visited['users_all_ids']
            users1_aggregated_to_preserve=cur_visited['users_agg_ids']
            #visited_1_trace_map[u1_p_tuple_users]=set()
            visited_1_trace|={u1_p_tuple_users}
            
            
        #users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve


        ratio_u1_p=len(users1_all_ids_to_preserve)/float(len_users1_all_starting)
        if ratio_u1_p<ratio_agg_threshold:
            u1_config['flag']=False
            continue
        
        
        timing+=time()-st
#         if True:
#             index_visited+=1
#             print u1_p,index_visited,len(users1_all_ids_to_preserve),ratio_u1_p
#             continue

        #users_map_details_array_filtered_user2_context=[row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in all_users2_ids - users1_all_ids_visited]
        enum_u2=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_2)
        flaggy_u2_first=True
        for u2_p,u2_label,u2_config in enum_u2: 
#             if not (u1_p[1]==['F'] and u2_p[1]==['M'] and u1_p[0]==u2_p[0]):
#                 continue
            u2_p_tuple_users=tuple(x[users_id_attribute] for x in u2_config['support'])
            u2_p_set_users=set(u2_p_tuple_users)
            ratio_u2_p=len(u2_p_set_users)/float(len_users2_all_starting)
            if ratio_u2_p<ratio_agg_threshold:
                u2_config['flag']=False
                if flaggy_u2_first:
                    u1_config['flag']=False
                continue
            
            if u2_p_set_users<u1_p_set_users :
                u2_config['flag']=False
                continue
            if u2_p_set_users>u1_p_set_users:
                flaggy_u2_first=False
                continue
            
            st=time()
            
            if (u2_p_tuple_users in visited_1_trace_map and u1_p_tuple_users in visited_1_trace_map[u2_p_tuple_users]) :#or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
                    continue
            else :
                visited_1_trace_map[u1_p_tuple_users]|={u2_p_tuple_users}
            
            
            if not visited_aggregated_outcome_has_key(u2_p_tuple_users):

                users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
                visited_aggregated_outcome[u2_p_tuple_users]={
                    'map_to_votes':users2_aggregated_map_votes_pattern,
                    'votes_outcomes':users2_aggregated_to_votes_outcomes_pattern,
                    'users_all_ids':users2_all_ids_to_preserve,
                    'users_agg_ids':users2_aggregated_to_preserve
                }
                

                
            else :
                ##########################EERRROOOOOOOOOOOOOR ! #################################
#                 if (u2_p_tuple_users in visited_1_trace_map and u1_p_tuple_users in visited_1_trace_map[u2_p_tuple_users]) :#or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
#                     continue
                ##########################EERRROOOOOOOOOOOOOR ! #################################
                cur_visited = visited_aggregated_outcome[u2_p_tuple_users]
                users2_aggregated_map_votes_pattern=cur_visited['map_to_votes']
                users2_aggregated_to_votes_outcomes_pattern=cur_visited['votes_outcomes']
                users2_all_ids_to_preserve=cur_visited['users_all_ids']
                users2_aggregated_to_preserve=cur_visited['users_agg_ids']
                visited_2_trace|={u2_p_tuple_users}
                #visited_1_trace_map[u1_p_tuple_users]|={u2_p_tuple_users}

            timing+=time()-st
            ratio_u2_p=len(users2_all_ids_to_preserve)/float(len_users2_all_starting)
            if ratio_u2_p<ratio_agg_threshold:
                u2_config['flag']=False
                continue
            print u1_p,u2_p,len(users1_all_ids_to_preserve),len(users2_all_ids_to_preserve),ratio_u1_p,ratio_u2_p,index_visited
            
            
            
#             if True:
#                 index_visited+=1
#                 print u1_p,u2_p,ratio_u1_p,ratio_u2_p,index_visited
#                 continue
            


            issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
            #print issquare
            reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,all_votes_id,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure)
            #print reference_matrix_dic
            enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},threshold=threshold_pair_comparaison,verbose=False)
            
            
            ######
            userpairssimsdetails={}
            for u1 in users1_aggregated_to_preserve:
                userpairssimsdetails[u1]={}
                for u2 in users2_aggregated_to_preserve:
                    userpairssimsdetails[u1][u2]={v:similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],u1,u2,comparaison_measure)[0] for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys()}
            ######
            
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            st=time()
            if nb_users_voted>0:
                flaggy_context=True
                for e_p,e_label,e_config in enumerator_contexts:
                    index_visited+=1
                    e_u_p=e_p + u1_p + u2_p
                    e_u_label=e_label + u1_label + u2_label
                    e_votes=e_config['support']
                    e_users_1=e_config['users1']
                    e_users_2=e_config['users2']
                    nb_votes=len(e_votes) 
                    if nb_votes<=threshold_pair_comparaison :
                        e_config['flag']=False
                        if nb_votes<threshold_pair_comparaison:
                            continue
                    
                    v_ids=set()
                    dossiers_ids=set()
                    
                    for obj in e_votes:
                        v_ids|={obj[vote_id_attribute]}
                        dossiers_ids |= {obj[elementToShow]}
                 
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
            
                
#                     if len(users1_ids_set)==0 or len(users2_ids_set)==0:
#                         continue
                    
                    #pattern_matrix_dic=compute_similarity_matrix_memory(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare)
                    pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison)
                    
                    reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                    quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))
                    if (pruning and borne_max_quality<quality_threshold):
                        e_config['flag']=False
#                         if flaggy_context:
#                             u2_config['flag']=False
#                             if flaggy_u2_first:
#                                 u1_config['flag']=False
                        continue
#                     if e_p==[['']]:
#                         print reference_matrix_dic
#                         print pattern_matrix_dic
#                         print quality
#                         raw_input('...')
                    
                    #print quality,e_u_p
                    #raw_input('...')
                    if (quality>=quality_threshold):
                        indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                        if cover_threshold<=1:
                            array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                            array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                            indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                            indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
                        if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                            if len(indices_to_remove_if_inserted)>0: 
                                interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
            
                            #dataset_stats=datasetStatistics(returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                            dataset_stats=[]
                            label=e_label
                            
                            ############NNNEEEW FOR HEATMAP
                            pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                            reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                            dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                            #################################
                            
                            dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                            #dossiers_voted=[]
                            interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                            if len(interesting_patterns)>top_k:
                                interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                                quality_threshold=interesting_patterns[-1][3]
                    flaggy_context=False            
#             else:
#                 u2_config['flag']=False
#                 if flaggy_u2_first:
#                     u1_config['flag']=False
            #timing+=time()-st        
            flaggy_u2_first=False          
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '.......',timing,index_visited,'.......'
    





def dsc_uuc_method(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    ###ONLY FOR TESSTS    
    initialize=time()
    interesting_patterns=[]
    #elementToShow='PROCEDURE_TITLE'
    #elementToShow='movieTitle'
    count_verif_thres=0
    time_threshold=600;obs=0
    #########################GETTING CONFIGURATION PARAMETERS################################
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0];users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    
    global LOWERORHIGHER
    global  BOUND1OR2
    BOUND1OR2=configuration.get('upperbound',1)
    if iwant == 'DISAGR_SUMDIFF':
        LOWERORHIGHER=True
    elif iwant=='AGR_SUMDIFF':
        LOWERORHIGHER=False
        
    
    
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    aggregationAttributes_user1=configuration.get('aggregation_attributes_user1',['NATIONAL_PARTY'])
    aggregationAttributes_user2=configuration.get('aggregation_attributes_user2',['NATIONAL_PARTY'])
    nb_aggregation_min_user1=configuration.get('nb_aggergation_min_user1',2)
    nb_aggregation_min_user2=configuration.get('nb_aggergation_min_user2',2)
    ratio_agg_threshold=configuration.get('ratio_agg_threshold',0.01)
    threshold_nb_users_1=configuration.get('threshold_nb_users_1',1)
    threshold_nb_users_2=configuration.get('threshold_nb_users_2',1)
    
    nb_items_to_study=configuration.get('nb_items',None)
    nb_users_to_study=configuration.get('nb_users',None)
    
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute,nb_items=nb_items_to_study,nb_users=nb_users_to_study)
    
    
    votes_map_details_array=votes_map_details.values()
    all_votes_id= set(votes_map_details.keys())
    all_users_map_details_array=all_users_map_details.values()
    all_users_ids=set(all_users_map_details.keys())
    outcome_tuple_structure=list(dataset[0][position_attribute])
    outcome_tuple_size=len(outcome_tuple_structure)
    outcome_tuple_structure=(0,)*outcome_tuple_size
    nb_ratings = sum(len(all_users_map_votes[k]) for k in  all_users_map_votes)
    
    ########################DOSSIERS_PARTICULAR##########################
#     dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
#     for v_id,v_value in votes_map_details.iteritems():
#         dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(all_users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(all_users_map_details_array, user2_scope)[0]
    all_users1_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user1}
    all_users2_ids={x[users_id_attribute] for x in users_map_details_array_filtered_user2}
    u1_isequalto_u2=(all_users1_ids==all_users2_ids)
    users1_aggregated_map_details,users1_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user1, users_attributes, aggregationAttributes_user1)
    users2_aggregated_map_details,users2_aggregated_map_to_users=construct_user_aggregate(users_map_details_array_filtered_user2, users_attributes, aggregationAttributes_user2)
    users1_agg_ids=users1_aggregated_map_details.viewkeys()
    users2_agg_ids=users2_aggregated_map_details.viewkeys()
    
    users1_aggregated_map_details_array,users1_aggregated_map_to_users,users1_aggregated_map_votes,users1_aggregated_to_votes_outcomes,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users1_ids,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)
    users2_aggregated_map_details_array,users2_aggregated_map_to_users,users2_aggregated_map_votes,users2_aggregated_to_votes_outcomes,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,all_users2_ids,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
    user1_after_aggregation=users1_aggregated_map_details_array
    user2_after_aggregation=users2_aggregated_map_details_array
    users1_agg_ids=set([p_attr[users_id_attribute] for p_attr in user1_after_aggregation])
    users2_agg_ids=set([p_attr[users_id_attribute] for p_attr in user2_after_aggregation])
    
    #len_starting_users1_ids=len(users1_all_ids_to_preserve)
    
    nb_users_voted=len(users1_agg_ids)*len(users2_agg_ids)
    
    #users_aggregtated_to_votes_outcomes_ref=users1_aggregated_to_votes_outcomes.copy()
    #users_aggregtated_to_votes_outcomes_ref.update(users2_aggregated_to_votes_outcomes)
    
    reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes,users2_aggregated_to_votes_outcomes,all_votes_id,users1_agg_ids,users2_agg_ids,comparaison_measure)
    #print reference_matrix_dic
    users_map_details_array_filtered_user1=[row for row in users_map_details_array_filtered_user1 if row[users_id_attribute] in users1_all_ids_to_preserve]
    users_map_details_array_filtered_user2=[row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in users2_all_ids_to_preserve]
    
    users_map_details_array_filtered_user1 = sorted(users_map_details_array_filtered_user1,key=lambda x : x[users_id_attribute])
    users_map_details_array_filtered_user2 = sorted(users_map_details_array_filtered_user2,key=lambda x : x[users_id_attribute])
    
    len_users1_all_starting=len(users_map_details_array_filtered_user1)
    len_users2_all_starting=len(users_map_details_array_filtered_user2)
    
    #print len_users1_all_starting,len_users2_all_starting
    CLOSED=configuration['closed']
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
        'closed':CLOSED,
        'prune':pruning,
        'sigma_quality':quality_threshold,
        'top_k':top_k,
        'quality_measure':iwant,
        'similarity_measure':comparaison_measure,
        'upperbound_type':BOUND1OR2
    }
    
    initialize=time()-initialize
    timing=time()
    
    visited_aggregated_outcome={}
    visited_1_trace=set()
    visited_2_trace=set()
    visited_aggregated_outcome_has_key=visited_aggregated_outcome.has_key
    if CLOSED:
        enum_u1=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user1, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_1)
    else :
        enum_u1=enumerator_complex_from_dataset_new_config(users_map_details_array_filtered_user1, subattributes_details_users, {},objet_id_attribute=vote_id_attribute,threshold=threshold_nb_users_1,verbose=False)
    
    index_visited=0
    index_all_descriptions=0
    index_u1_visited=0;index_all_u1_visited=0
    index_u2_visited=0;index_all_u2_visited=0
    for u1_p,u1_label,u1_config in enum_u1:
        visited_1=False
        index_u1_visited+=1
        u1_p_tuple_users=tuple(x[users_id_attribute] for x in u1_config['support'])
        u1_p_set_users=set(u1_p_tuple_users)
        ratio_u1_p=len(u1_p_set_users)/float(len_users1_all_starting)
        
#         users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes_opt(all_votes_id,u1_p_set_users,precedent_users1_aggregated_to_preserve, users1_aggregated_map_details,precedent_users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1,users_aggregated_to_votes_outcomes_param=precedent_users1_aggregated_to_votes_outcomes)
        
        if not visited_aggregated_outcome_has_key(u1_p_tuple_users):
            users1_aggregated_map_details_array_pattern,users1_aggregated_map_to_users_pattern,users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve,users1_all_ids_visited,users1_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u1_p_set_users,users1_agg_ids, users1_aggregated_map_details,users1_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user1)

            
            visited_aggregated_outcome[u1_p_tuple_users]={
                    'map_to_votes':users1_aggregated_map_votes_pattern,
                    'votes_outcomes':users1_aggregated_to_votes_outcomes_pattern,
                    'users_all_ids':users1_all_ids_to_preserve,
                    'users_agg_ids':users1_aggregated_to_preserve
            }
            
        else :
            cur_visited = visited_aggregated_outcome[u1_p_tuple_users]
            users1_aggregated_map_votes_pattern=cur_visited['map_to_votes']
            users1_aggregated_to_votes_outcomes_pattern=cur_visited['votes_outcomes']
            users1_all_ids_to_preserve=cur_visited['users_all_ids']
            users1_aggregated_to_preserve=cur_visited['users_agg_ids']
            
            visited_1_trace|={u1_p_tuple_users}
            
            
        #users1_aggregated_map_votes_pattern,users1_aggregated_to_votes_outcomes_pattern,users1_all_ids_to_preserve,users1_aggregated_to_preserve


        ratio_u1_p=len(users1_all_ids_to_preserve)/float(len_users1_all_starting)
        if ratio_u1_p<ratio_agg_threshold:
            u1_config['flag']=False
            continue
        

        #users_map_details_array_filtered_user2_context=[row for row in users_map_details_array_filtered_user2 if row[users_id_attribute] in all_users2_ids - users1_all_ids_visited]
        if CLOSED:
            enum_u2=enumerator_complex_cbo_init_new_config(users_map_details_array_filtered_user2, subattributes_details_users,{},verbose=False,threshold=threshold_nb_users_2)
        else :
            enum_u2=enumerator_complex_from_dataset_new_config(users_map_details_array_filtered_user2, subattributes_details_users, {},objet_id_attribute=vote_id_attribute,threshold=threshold_nb_users_2,verbose=False)
        flaggy_u2_first=True
        obs=time()-timing
        if obs > time_threshold: break
        for u2_p,u2_label,u2_config in enum_u2: 
            index_u2_visited+=1
            u2_p_tuple_users=tuple(x[users_id_attribute] for x in u2_config['support'])
            u2_p_set_users=set(u2_p_tuple_users)
            
            
            if u2_p_set_users<u1_p_set_users :
                u2_config['flag']=False
                continue
            if u2_p_set_users>u1_p_set_users:
                flaggy_u2_first=False
                continue
            
            st=time()

            
            if not visited_aggregated_outcome_has_key(u2_p_tuple_users):

                users2_aggregated_map_details_array_pattern,users2_aggregated_map_to_users_pattern,users2_aggregated_map_votes_pattern,users2_aggregated_to_votes_outcomes_pattern,users2_all_ids_to_preserve,users2_aggregated_to_preserve,users2_all_ids_visited,users2_aggregated_ids_visited=compute_aggregates_outcomes(all_votes_id,u2_p_set_users,users2_agg_ids, users2_aggregated_map_details,users2_aggregated_map_to_users, all_users_to_votes_outcomes, users_attributes,outcome_tuple_structure,size_aggregate_min=nb_aggregation_min_user2)
                visited_aggregated_outcome[u2_p_tuple_users]={
                    'map_to_votes':users2_aggregated_map_votes_pattern,
                    'votes_outcomes':users2_aggregated_to_votes_outcomes_pattern,
                    'users_all_ids':users2_all_ids_to_preserve,
                    'users_agg_ids':users2_aggregated_to_preserve
                }
                

                
            else :
                ###########################EERRROOOOOOOOOOOOOR ! #################################
#                 if (u2_p_tuple_users in visited_1_trace and u1_p_tuple_users in visited_2_trace) or (u1_p_tuple_users in visited_1_trace and u2_p_tuple_users in visited_2_trace):
#                     continue
                ###########################EERRROOOOOOOOOOOOOR ! #################################
                cur_visited = visited_aggregated_outcome[u2_p_tuple_users]
                users2_aggregated_map_votes_pattern=cur_visited['map_to_votes']
                users2_aggregated_to_votes_outcomes_pattern=cur_visited['votes_outcomes']
                users2_all_ids_to_preserve=cur_visited['users_all_ids']
                users2_aggregated_to_preserve=cur_visited['users_agg_ids']
                visited_2_trace|={u2_p_tuple_users}
                

            
            ratio_u2_p=len(users2_all_ids_to_preserve)/float(len_users2_all_starting)
            if ratio_u2_p<ratio_agg_threshold:
                u2_config['flag']=False
                continue
            #print u1_p,u2_p,len(users1_all_ids_to_preserve),len(users2_all_ids_to_preserve),ratio_u1_p,ratio_u2_p,index_visited
            
            
            issquare=users1_all_ids_to_preserve==users2_all_ids_to_preserve
            #print issquare
            reference_matrix_dic=compute_similarity_matrix(users1_aggregated_to_votes_outcomes_pattern,users2_aggregated_to_votes_outcomes_pattern,all_votes_id,users1_aggregated_to_preserve,users2_aggregated_to_preserve,comparaison_measure,issquare)
            #print reference_matrix_dic
            if CLOSED:
                enumerator_contexts=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},threshold=threshold_pair_comparaison,verbose=False)
            else :
                enumerator_contexts=enumerator_complex_from_dataset_new_config(votes_map_details_array, subattributes_details_votes, {'users1':users1_aggregated_map_votes_pattern,'users2':users2_aggregated_map_votes_pattern},objet_id_attribute=vote_id_attribute,threshold=threshold_pair_comparaison,verbose=False)
            
            
            
            
            #############
            
            
            #################
            
            
            ######
            userpairssimsdetails={}
            for u1 in users1_aggregated_to_preserve:
                userpairssimsdetails[u1]={}
                for u2 in users2_aggregated_to_preserve:
                    userpairssimsdetails[u1][u2]={v:similarity_vector_measure_dcs({v}, users1_aggregated_to_votes_outcomes_pattern[u1], users2_aggregated_to_votes_outcomes_pattern[u2],u1,u2,comparaison_measure)[0] for v in users1_aggregated_to_votes_outcomes_pattern[u1].viewkeys()&users2_aggregated_to_votes_outcomes_pattern[u2].viewkeys()}
            ######
            obs=time()-timing
            if obs > time_threshold:
                break
            nb_users_voted=len(users1_aggregated_to_preserve)*len(users2_aggregated_to_preserve)
            st=time()
            if nb_users_voted>0:
                flaggy_context=True
                for e_p,e_label,e_config in enumerator_contexts:
                    index_visited+=1
                    obs=time()-timing
                    if obs > time_threshold:
                        break
                    e_u_p=e_p + u1_p + u2_p
                    e_u_label=e_label + u1_label + u2_label
                    e_votes=e_config['support']
                    e_users_1=e_config['users1']
                    e_users_2=e_config['users2']
                    nb_votes=len(e_votes) 
                    if nb_votes<=threshold_pair_comparaison :
                        e_config['flag']=False
                        if nb_votes<threshold_pair_comparaison:
                            continue
                    
                    v_ids=set()
                    dossiers_ids=set()
                    
                    for obj in e_votes:
                        v_ids|={obj[vote_id_attribute]}
                        #dossiers_ids |= {obj[elementToShow]}
                 
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
            
                

                    
                    #pattern_matrix_dic=compute_similarity_matrix_memory(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare)
                    pattern_matrix_dic=compute_similarity_matrix_memory_withbound(userpairssimsdetails,v_ids,users1_ids_set,users2_ids_set,issquare,threshold_pair_comparaison)
                    
                    reference_matrix, pattern_matrix,rower,header = transform_to_matrices(reference_matrix_dic, pattern_matrix_dic)
                    quality,borne_max_quality=compute_quality_and_upperbound(reference_matrix,pattern_matrix,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))
                    if (pruning and borne_max_quality<quality_threshold):
                        e_config['flag']=False

                        continue

                    
                    
                    if (quality>=quality_threshold):
                        if top_k>10000:
                            count_verif_thres+=1
                            continue
                        indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                        if cover_threshold<=1:
                            array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                            array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                            indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                            indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
                        if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                            if len(indices_to_remove_if_inserted)>0: 
                                interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
            
                            #dataset_stats=datasetStatistics(returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                            dataset_stats=[]
                            label=e_label
                            
                            ############NNNEEEW FOR HEATMAP
                            pattern_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in pattern_matrix],rower,header)
                            reference_matrix_complete=getCompleteMatrix([[col[0]/col[1] if col[1]>=threshold_pair_comparaison else float('nan') for col in row] for row in reference_matrix],rower,header)
                            dataset_stats=[reference_matrix_complete,pattern_matrix_complete]
                            #################################
                            
                            #dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                            dossiers_voted=[]
                            interesting_patterns.append([e_u_p,e_u_label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                            if len(interesting_patterns)>top_k:
                                interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                                quality_threshold=interesting_patterns[-1][3]
                    flaggy_context=False            
                index_all_descriptions+=e_config['nb_visited'][0]
        index_all_u2_visited+=u2_config['nb_visited'][0]
    index_all_u1_visited+=u1_config['nb_visited'][0]
            #index_all_descriptions+=e_config['nb_visited'][0]
            #flaggy_u2_first=False  
    timing=time()-timing  
    statusmamus={
        '#all_visited_context':index_all_descriptions+(index_all_u2_visited-index_u2_visited)+(index_all_u1_visited-index_u1_visited),
        '#candidates':index_visited,
        '#init':initialize,
        '#timespent':timing,
        '#patterns':len(interesting_patterns) if top_k<= 10000 else count_verif_thres,
        'max_quality_found':max(interesting_patterns[i][3] for i in range(len(interesting_patterns))) if len(interesting_patterns)>0 else 0
    }
    statusmamus.update(parameters)  
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in [(1,2,3,4,5,6,7)]:
        yield p,label,dataset_stats,quality,borne_max_quality,[statusmamus]
    #stdout.write('\r.......'+str('%.2f' % (timing+initialize))+'.......')