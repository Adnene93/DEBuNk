'''
Created on 25 janv. 2017

@author: Adnene
'''
from __builtin__ import raw_input
from itertools import izip
from math import sqrt, copysign, isnan
from operator import concat
import re
from time import time

from bitarray import bitarray
from sortedcontainers.sortedlist import SortedList
from sortedcontainers.sortedset import SortedSet

from EMM_ENUMERATOR.enumerator_nominal import children_nominal, \
    possible_parents_nominal, value_to_yield_nominal, \
    description_from_pattern_nominal
from EMM_ENUMERATOR.enumerator_numbers import children_num, \
    possible_parents_numeric, value_to_yield_num, description_from_pattern_num
from EMM_ENUMERATOR.enumerator_simple import children_simple, \
    value_to_yield_simple, description_from_pattern_simple, \
    possible_parents_simple
from EMM_ENUMERATOR.enumerator_themes import createTreeOutOfThemes, \
    all_childrens_set_opt_depthmax, possible_parents_themes, \
    value_to_yield_themes, description_from_pattern_themes, infimum, \
    respect_order
from EMM_ENUMERATOR.enumerator_themes2 import childrens_themes_exploitable2, \
    value_to_yield_themes2, tree_theme2, childrens_themes2, \
    description_from_pattern_themes2, infimum2
from filterer.filter import filter_pipeline_obj
from measures.qualityMeasure import quality_norm_eloignement, \
    quality_norm_rapprochement, quality_mepwise_eloignement, \
    quality_peer_eloignement, quality_correlation_eloignement
from measures.similaritiesMajorities import similarity_vector_measure
from votesExtractionAndProcessing.pairwiseStatistics import extractStatistics_fromdataset_new, \
    extractStatistics_fromdataset_new_update_not_square, datasetStatistics, \
    extractStatistics_fromdataset_new_update_not_square_vectors, \
    extractStatistics_fromdataset_vectors



POSSIBLE_ENUMERATOR_CHILDREN={
    'numeric':children_num,
    'nominal':children_nominal,
    'themes':all_childrens_set_opt_depthmax,
    'simple':children_simple,
    'themes2':childrens_themes_exploitable2
} 

POSSIBLE_ENUMERATOR_PARENTS={
    'numeric':possible_parents_numeric,
    'nominal':possible_parents_nominal,
    'themes':possible_parents_themes,
    'simple':possible_parents_simple
} 

POSSIBLE_ENUMERATOR_YIELDER={
    'numeric':value_to_yield_num,
    'nominal':value_to_yield_nominal,
    'themes':value_to_yield_themes,
    'simple':value_to_yield_simple,
    'themes2':value_to_yield_themes2
}

POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER={
    'numeric':description_from_pattern_num,
    'nominal':description_from_pattern_nominal,
    'themes':description_from_pattern_themes,
    'simple':description_from_pattern_simple,
    'themes2':description_from_pattern_themes2
}


def get_sim_vectors_old(stats,user1,user2):
    return float(stats[user1][user2]['++']),stats[user1][user2]['NB_VOTES']            




def get_sim_vectors(stats,user1,user2,comparaison_measure='COS'):
    agreementProp,nb_votes=similarity_vector_measure(stats, user1, user2, comparaison_measure)   
    return agreementProp,nb_votes
    




def get_sim_xxx(stats,user1,user2):
    return float(stats[user1][user2]['YY']+stats[user1][user2]['NN']+stats[user1][user2]['AA']),stats[user1][user2]['NB_VOTES']  

def get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute,user_variation_scope=None):
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    range_nb_attributes=range(len(attributes))
    votes_map_details={}
    users_map_details={}
    votes_map_meps={}
    users_map_votes={}
    #users_map_votes_agreement_index={}
    users_map_details_has_key=users_map_details.has_key
    votes_map_details_has_key=votes_map_details.has_key
    arr_distinct_values=[SortedSet() for i in range_nb_attributes]
    for d in dataset:
        for i,attr in enumerate(attributes):
            
            obj_attr_value=d[attr['name']]
            values=set()
            if hasattr(obj_attr_value, '__iter__'):
                values={v for v in obj_attr_value}
            else :
                values={obj_attr_value}
            if (attr['name'] not in users_attributes) or ((attr['name'] in users_attributes) and (d[users_id_attributes] in user_variation_scope)): 
                arr_distinct_values[i] |= values
        
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
            #users_map_votes_agreement_index[d_user_id]=[]
        users_map_votes[d_user_id] |= {d_vote_id}
        
        ###########AGREEMENT_INDEX#####################
        #users_map_votes_agreement_index[d_user_id] +=  [(d_vote_id,d['AgreementIndex'])]
        ###########AGREEMENT_INDEX#####################
        
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=SortedSet()
        votes_map_meps[d_vote_id] |= {d_user_id}
        
    return votes_map_details,votes_map_meps,users_map_details,users_map_votes,arr_distinct_values



def get_arrdata_from_dataset_values(arr_distinct_values,attributes,votes_attributes,users_attributes,position_attribute):
    
    arr_data=[]
    arr_types=[]
    arr_depthmax=[]
    arr_refinement_indexes=[]
    arr_labels=[]
    subgroup_pipeline=[]
    filter_operations=[]
    
    num=r'([0-9]|\.)*'
    reg = re.compile(num)       
    
    for i,attr in enumerate(attributes):
        arr_types.append(attr['type'])
        arr_depthmax.append(attr['bound_width'])
        subgroup_pipeline.append({'dimensionName':attr['name']})
        
        if attr['type']=='numeric':
            arr_data.append(SortedList(arr_distinct_values[i]))
            arr_refinement_indexes.append(0)
            arr_labels.append({})
            
            subgroup_pipeline[-1]['inInterval']=[]
            filter_operations.append('inInterval')
            
        elif attr['type']=='nominal':
            arr_data.append(SortedList(arr_distinct_values[i]))
            arr_refinement_indexes.append(len(arr_data[i]))
            arr_labels.append({})
            
            subgroup_pipeline[-1]['inSet']=[]
            filter_operations.append('inSet')
        
        elif attr['type']=='simple':
            arr_data.append(arr_distinct_values[i])
            arr_refinement_indexes.append(len(arr_data[i]))
            arr_labels.append({})
            
            subgroup_pipeline[-1]['inSet']=[]
            filter_operations.append('inSet')
            
        elif attr['type']=='themes':
            
            data_to_tree=[]
            for val in arr_distinct_values[i]:    
                data_to_tree.append({'ID':reg.search(val).group(),'LABEL':val[reg.search(val).end()+1:]})
            
            tree,themesMAP=createTreeOutOfThemes(data_to_tree)
            arr_data.append([tree])
            arr_refinement_indexes.append(0)
            arr_labels.append(themesMAP)
            
            subgroup_pipeline[-1]['contain_themes']=[] 
            filter_operations.append('contain_themes')
        elif attr['type']=='themes2':
            
            data_to_tree=[]
            for val in arr_distinct_values[i]:    
                data_to_tree.append({'ID':reg.search(val).group(),'LABEL':val[reg.search(val).end()+1:]})
            
            tree,themesMAP=createTreeOutOfThemes(data_to_tree)
            tree_themes=tree_theme2(sorted([x['ID'] for x in data_to_tree]))
            #tree_themes['pattern']=['']
            arr_data.append(tree_themes)
            arr_refinement_indexes.append([''])
            arr_labels.append(themesMAP)
            
            subgroup_pipeline[-1]['contain_themes']=[] 
            filter_operations.append('contain_themes')
    
    subgroup_pipeline_for_votes=[stage for stage in subgroup_pipeline if stage['dimensionName'] in votes_attributes]
    subgroup_pipeline_for_meps=[stage for stage in subgroup_pipeline if stage['dimensionName'] in users_attributes]
    return arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps


def children_generic(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0):
    possibleChildrens_arr=[]
    possibleChildrens_types=[]
    possibleChildrens_refinement_index_arr=[]
    actual_childrens=POSSIBLE_ENUMERATOR_CHILDREN[arr_types[refinement_index_attr]](arr_data[refinement_index_attr],refinement_index_arr[refinement_index_attr],depthmax_arr[refinement_index_attr])
    childrens_model_arr=[]
    childrens_model_types=[]
    childrens_refinement_index_arr=[]
    
    for i in range(refinement_index_attr+1):
        if not i==refinement_index_attr:
            childrens_model_arr.append(arr_data[i])
            childrens_model_types.append(arr_types[i])
            childrens_refinement_index_arr.append(refinement_index_arr[i])
        else :
            childrens_model_arr.append(None)
            childrens_model_types.append(arr_types[i])
            childrens_refinement_index_arr.append(None)
            
    for elem,refin in actual_childrens:
        new_child_arr=childrens_model_arr[:]#deepcopy(childrens_model_arr)
        new_child_types=childrens_model_types[:]#deepcopy(childrens_model_types)
        new_child_refinement_index_arr=childrens_refinement_index_arr[:]#deepcopy(childrens_refinement_index_arr)
        new_child_arr[refinement_index_attr]=elem#deepcopy(elem)
        new_child_refinement_index_arr[refinement_index_attr]=refin
        possibleChildrens_arr.append(new_child_arr)
        possibleChildrens_types.append(new_child_types)
        possibleChildrens_refinement_index_arr.append(new_child_refinement_index_arr)
        
    return possibleChildrens_arr,possibleChildrens_types,possibleChildrens_refinement_index_arr


def value_to_yield(arr_data,arr_types,refinement_index_attr,arr_refins=[]):
    yielded_item=[]
    for arr,typeAttr,refin in zip(arr_data,arr_types,arr_refins): #zip(arr_data[:refinement_index_attr+1],arr_types[:refinement_index_attr+1]) 
        yielded_attr=POSSIBLE_ENUMERATOR_YIELDER[typeAttr](arr,opt=refin)
        if yielded_attr is None :
            return None
        yielded_item.append(yielded_attr)
    return yielded_item

def possible_parents(pattern,arr_types,original_data):
    refined_attr=0
    len_pattern=len(pattern)
    range_len_pattern=(range(len_pattern))
    toRet=[]
    
    possible_parents_of_attributes=[POSSIBLE_ENUMERATOR_PARENTS[arr_types[k]](pattern[k],original_data[k]) for k in range_len_pattern]
    
    while refined_attr<len_pattern:
        selected_parents_to_combine=[possible_parents_of_attributes[i] if i==refined_attr else possible_parents_of_attributes[i][-1:] for i in range_len_pattern]
        for k in range(len(selected_parents_to_combine[refined_attr])-1):
            pattern_parent_generated=[selected_parents_to_combine[i][k:k+1][0] if i==refined_attr else selected_parents_to_combine[i][0] for i in range_len_pattern]
            toRet.append(pattern_parent_generated)
        refined_attr+=1
    return toRet


def generic_enumerator_multiattributes_dfs(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None,stats=None): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr,refinement_index_arr)
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
            yield yielded_item,bitwise,stats
        
        bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else bitwise
        statsConfig=configuration['stats'] if (configuration['stats'] is not None) else stats
        closingConfig=configuration['closing'] if (configuration['closing'] is not None) else arr_data
        closingRefinConfig=configuration['closing_refin'] if (configuration['closing_refin'] is not None) else refinement_index_arr
        configuration['stats']=None
        configuration['bitwise']=None  
        configuration['closing']=None
        configuration['closing_refin']=None
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                #childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                childs=children_generic([closingConfig[i] if closingConfig[i] is not None else arr_data[i] for i in range(len(arr_data))], arr_types,[closingRefinConfig[i]  if closingRefinConfig[i] is not None else refinement_index_arr[i] for i in range(len(refinement_index_arr))],depthmax_arr,configuration, actual_refin)
                
                
#                 childs=children_generic([
#                                         (arr_data[i][0],closingConfig[i]) if (closingConfig[i] is not None and arr_types[i]=='themes2') 
#                                          else arr_data[i] if (closingConfig is None and arr_types[i]=='themes2') 
#                                          else closingConfig[i] if closingConfig[i] is not None 
#                                          else arr_data[i] 
#                                          for i in range(len(arr_data))], arr_types,[closingRefinConfig[i]  if closingRefinConfig[i] is not None else refinement_index_arr[i] for i in range(len(refinement_index_arr))],depthmax_arr,configuration, actual_refin)
#                  
                for pos in range(len(childs[0])):
                    for p,psg_bitwise,psg_stats in generic_enumerator_multiattributes_dfs(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin,bitwiseConfig,statsConfig):
                        yield p,psg_bitwise,psg_stats


def generic_enumerators_rec_subgroupBitwise_subgroups_stats_new_bfs(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None,stats=None): #TODO!
    fifo=[]
    appender=fifo.append
    popper=fifo.pop
    level=0
    index=0
    appender([arr_data,arr_types,refinement_index_arr,refinement_index_attr,bitwise,stats,level])
    while (len(fifo))>0:
        configuration['bitwise']=None
        configuration['stats']=None
        actual_arr_data,actual_arr_types,actual_refinement_index_arr,actual_refinement_index_attr,actual_bitwise,actual_stats,actual_level=popper(0)
        yielded_item=value_to_yield(actual_arr_data,actual_arr_types,actual_refinement_index_arr)
        if (yielded_item is None or all(x not in configuration['skip_list'] for x in possible_parents(yielded_item, arr_types, arr_data))):
            if yielded_item is not None :
                yield yielded_item,actual_bitwise,actual_stats
                
            bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else actual_bitwise
            statsConfig=configuration['stats'] if (configuration['stats'] is not None) else actual_stats
            
            if yielded_item not in configuration['skip_list'] :
                if yielded_item is not None :
                    tuple_p=tuple(tuple(x) for x in yielded_item)
                    #print configuration['patterns_visited'][tuple_p]
                    #,configuration['patterns_visited'][tuple_p]['quality']
                    print yielded_item,actual_level,configuration['patterns_visited'][tuple_p]['quality']
                for actual_refin in range(actual_refinement_index_attr,len(arr_data)):
                    childs=children_generic(actual_arr_data, actual_arr_types,actual_refinement_index_arr,depthmax_arr,configuration, actual_refin)
                    for pos in range(len(childs[0])):
                        appender((childs[0][pos]+actual_arr_data[actual_refin+1:],childs[1][pos]+actual_arr_types[actual_refin+1:],childs[2][pos]+actual_refinement_index_arr[actual_refin+1:],actual_refin,bitwiseConfig,statsConfig,actual_level+1))

def generic_enumerators_rec_subgroupBitwise_subgroups_stats_new_beamsearch(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None,stats=None): #TODO!
    candidates=[]
    fathercandidates=[None]
    fifo=[]
    appender=fifo.append
    popper=fifo.pop
    level=0
    index=0
    precedent_level=0
    actual_level=0
    appender([None,arr_data,arr_types,refinement_index_arr,refinement_index_attr,bitwise,stats,level])
    while (len(fifo))>0:
        precedent_level=actual_level
        configuration['bitwise']=None
        configuration['stats']=None
        father,actual_arr_data,actual_arr_types,actual_refinement_index_arr,actual_refinement_index_attr,actual_bitwise,actual_stats,actual_level=popper(0)
        
        if precedent_level<>actual_level:
            fathercandidates=[t[0] for t in sorted(candidates,key=lambda x : x [1],reverse=True)[:30]]+[None]
            candidates=[]
        
        yielded_item=value_to_yield(actual_arr_data,actual_arr_types,actual_refinement_index_arr)
        if (yielded_item is None or all(x not in configuration['skip_list'] for x in possible_parents(yielded_item, arr_types, arr_data)) and (father in fathercandidates)):
            if yielded_item is not None :
                yield yielded_item,actual_bitwise,actual_stats
                
            bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else actual_bitwise
            statsConfig=configuration['stats'] if (configuration['stats'] is not None) else actual_stats
            
            if yielded_item not in configuration['skip_list'] :
                if yielded_item is not None :
                    tuple_p=tuple(tuple(x) for x in yielded_item)
                    #print configuration['patterns_visited'][tuple_p]
                    #,configuration['patterns_visited'][tuple_p]['quality']
                    print father,yielded_item,precedent_level,actual_level,configuration['patterns_visited'][tuple_p]['quality']
                    candidates.append((yielded_item,configuration['patterns_visited'][tuple_p]['quality']))
                for actual_refin in range(actual_refinement_index_attr,len(arr_data)):
                    childs=children_generic(actual_arr_data, actual_arr_types,actual_refinement_index_arr,depthmax_arr,configuration, actual_refin)
                    for pos in range(len(childs[0])):
                        appender((yielded_item,childs[0][pos]+actual_arr_data[actual_refin+1:],childs[1][pos]+actual_arr_types[actual_refin+1:],childs[2][pos]+actual_refinement_index_arr[actual_refin+1:],actual_refin,bitwiseConfig,statsConfig,actual_level+1))


def cover_max_computation_OLD(actual_pattern,actual_subpattern_user,bitwise_pattern,patterns_visited,subpatterns_users_visited,bitwises_visited,cover_threshold):
    bitarray_bitwise=bitarray(bitwise_pattern)
    bitarray_bitwise_count=bitarray_bitwise.count()
    
    max_cover=0
    borne_max_cover=0
    pattern_max_cover=[]
    
    for (b,count_obj,b_max),p_users_visited,p_visited in zip(bitwises_visited,subpatterns_users_visited,patterns_visited):
        if (bitarray_bitwise_count<=count_obj) and (p_users_visited==actual_subpattern_user):  
            act_cover=(float((bitarray_bitwise & b).count()) / count_obj)
            if (act_cover>max_cover):
                borne_max_cover=b_max
                pattern_max_cover=p_visited
            max_cover=max(max_cover,act_cover)
            
            if max_cover>=cover_threshold:
                break
   
    return max_cover,borne_max_cover,pattern_max_cover,bitarray_bitwise,bitarray_bitwise_count


def cover_max_computation(actual_pattern,bitwise_pattern,patterns_visited,bitwises_visited,cover_threshold):
    bitarray_bitwise=bitarray(bitwise_pattern)
    bitarray_bitwise_count=bitarray_bitwise.count()
    
    max_cover=0
    borne_max_cover=0
    pattern_max_cover=[]
    
    for (b,count_obj,b_max),p_visited in zip(bitwises_visited,patterns_visited):
        if (bitarray_bitwise_count<=count_obj):  
            act_cover=(float((bitarray_bitwise & b).count()) / count_obj)
            if (act_cover>max_cover):
                borne_max_cover=b_max
                pattern_max_cover=p_visited
            max_cover=max(max_cover,act_cover)
            
            if max_cover>=cover_threshold:
                break
   
    return max_cover,borne_max_cover,pattern_max_cover,bitarray_bitwise,bitarray_bitwise_count

def cover_max_computation_new(actual_pattern,pattern_vote,pattern_user,bitwise_pattern,patterns_visited,cover_threshold):
    #{'pattern':p,'dossiers':dossiers_ids,'bitwise':bitarray_bitwise,'bitwise_count':bitarray_bitwise_count,'upper_bound':borne_max_quality}
    bitarray_bitwise=bitarray(bitwise_pattern)
    bitarray_bitwise_count=float(bitarray_bitwise.count())
    
    max_cover=0
    borne_max_cover=0
    pattern_max_cover=[]
    
    
    for p_visited in patterns_visited:
        value = patterns_visited[p_visited]
        count_obj=value['bitwise_count']
        b_max=value['upper_bound']
        b=value['bitwise']
        p_visited_user=value['pattern_user']
        if p_visited_user==pattern_user:
            if (bitarray_bitwise_count<=count_obj and (bitarray_bitwise_count/count_obj)>=cover_threshold ):  
                act_cover=((bitarray_bitwise & b).count() / count_obj)
                if (act_cover>max_cover):
                    borne_max_cover=b_max
                    pattern_max_cover=p_visited
                    max_cover=act_cover#max(max_cover,act_cover)
                
                if max_cover>=cover_threshold:
                    break
   
    return max_cover,borne_max_cover,pattern_max_cover,bitarray_bitwise,bitarray_bitwise_count

def compute_quality_and_upper_boundOLD(original_mepwise_similarities,pattern_mepsStatsNumbers,nb_users_voted,threshold_pair_comparaison,iwant='disagreement',comparaison_measure='COS'):
    
    disagreement=(iwant=='disagreement')
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    nb_pair=0
    
    nb_interesting=0
    nb_interesting_max=0
    arr_interesting=[]
    arr_interesting_max=[]
    for user1 in pattern_mepsStatsNumbers:
        arr_interesting.append(0)
        arr_interesting_max.append(0)
        for user2 in pattern_mepsStatsNumbers[user1]:
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2,comparaison_measure)
                agg_o,all_o=original_mepwise_similarities[user1][user2]

                if all_p>=threshold_pair_comparaison:
                    nb_pair+=1.
                    if disagreement:
                        agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                        qp=max((agg_o/all_o)-(agg_p/all_p),0)
                        min_sim_expected=agg_min/threshold_pair_comparaison
                        diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                    else:
                        agg_max=float(min(agg_p,threshold_pair_comparaison))
                        qp=max((agg_p/all_p)-(agg_o/all_o),0)
                        max_sim_expected=agg_max/threshold_pair_comparaison
                        diff_p_max_expected=max(max_sim_expected-(agg_o/all_o),0)
                    if qp>0 :
                        nb_interesting+=1.
                        arr_interesting[-1]+=1
                    if diff_p_max_expected>0:
                        nb_interesting_max+=1.
                        arr_interesting_max[-1]+=1
                    qps_append(copysign(qp,1))
                    qps_max_append(copysign(diff_p_max_expected,1))
                

    quality=sqrt(sum(x**2 for x in qps))/float(nb_users_voted) #* (nb_interesting/nb_pair)
    borne_max_quality=sqrt(sum(x**2 for x in qps_max))/float(nb_users_voted) #* (nb_interesting_max/nb_pair)
    
    ratio_interesting_dep = [x/float(nb_users_voted)>0.8 for x in arr_interesting].count(True)/float(nb_users_voted)
    ratio_interesting_dep_max = [x/float(nb_users_voted)>0.8 for x in arr_interesting_max].count(True)/float(nb_users_voted)
    #print ratio_interesting_dep,ratio_interesting_dep_max
    
    quality*=ratio_interesting_dep
    borne_max_quality*=ratio_interesting_dep_max
    
    return quality,borne_max_quality

def compute_models(original_mepwise_similarities,pattern_mepsStatsNumbers,comparaison_measure='COS',issquare=False):
    
    matrix_general=[];matrix_general_append=matrix_general.append
    matrix_pattern=[];matrix_pattern_append=matrix_pattern.append
    
    for user1 in pattern_mepsStatsNumbers:
        matrix_general_append([]);matrix_general_actual_row_append=matrix_general[-1].append
        matrix_pattern_append([]);matrix_pattern_actual_row_append=matrix_pattern[-1].append
        row_original_mepwise_sim=original_mepwise_similarities[user1]
        for user2 in pattern_mepsStatsNumbers[user1]:
            #if issquare and user2<=user1:
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2,comparaison_measure)# if user2 not in matrix_pattern_map or user1 not in matrix_pattern_map[user2] else matrix_pattern_map[user1][user2]
                agg_o,all_o=row_original_mepwise_sim[user2]
                matrix_general_actual_row_append((agg_o,all_o))
                matrix_pattern_actual_row_append((agg_p,all_p))

#     if issquare:
#         len_matrix_general=len(matrix_general)
#         for i in range(len_matrix_general):
#             matrix_general_i_append=matrix_general[i].append
#             matrix_pattern_i_append=matrix_pattern[i].append
#             for j in range(i+1,len_matrix_general):
#                 matrix_general_i_append(matrix_general[j][i])
#                 matrix_pattern_i_append(matrix_pattern[j][i])
            
    return matrix_general,matrix_pattern

def compute_quality(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted,iwant):
    if iwant=='disagreement': 
        return quality_norm_eloignement(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted)
    else:
        return quality_norm_rapprochement(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted)
    
#1328     241     222     181     26
#1328     241     164     128     26
MAP_ENUMERATORS={
    'dfs':generic_enumerator_multiattributes_dfs,
    'bfs':generic_enumerators_rec_subgroupBitwise_subgroups_stats_new_beamsearch
}



def generic_enumerators_top_k(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute,exploration='dfs',closed=True): #disagreement
    spent=0
    visited_patterns_more_detailed=set()
    nb_quality_measured=0
    interesting_patterns=[]
    len_attributes=len(attributes)
    range_len_attributes=range(len_attributes)
    top_k=configuration.get('top_k',float('inf'))
    if top_k is None : 
        top_k=float('inf')
    quality_threshold=float(configuration.get('quality_threshold',0))
    if quality_threshold is None:
        quality_threshold=0
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    #subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
     
    patterns_visited={}
    patterns_visited_valid={}
    ############################### GET DISTINCT VALUES ####################################
    #datasetFiltered=filter_pipeline_obj(dataset, user2_scope)[0]
    user2_scope_values={x[users_id_attributes] for x in filter_pipeline_obj(dataset, user2_scope)[0]}
    #print user2_scope_values
    votes_map_details,votes_map_meps,users_map_details,users_map_votes,arr_distinct_values=get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute,user2_scope_values)
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    ##############################################################################################
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    users_ids=set([obj[users_id_attributes] for obj in users_map_details_array])
    users1_ids=set([p_attr[users_id_attributes] for p_attr in users_map_details_array_filtered_user1])
    users2_ids=set([p_attr[users_id_attributes] for p_attr in users_map_details_array_filtered_user2])
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    ############################STATS for * ######################################
    
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    
    original_mepwise_similarities={}
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2,comparaison_measure)
                
    ##############################################################################
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    configuration['stats']=original_mepsStatistics
    configuration['patterns_visited']=patterns_visited
    configuration['skip_list']=[]
    configuration['closing']=[None]*len(attributes)
    configuration['closing_refin']=[None]*len(attributes)
    skip_list_append=configuration['skip_list'].append
    
    enumerator=MAP_ENUMERATORS[exploration](arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None,stats=original_mepsStatistics)
    index,index_has_been_visited,index_frequent,index_valid,index_non_valid,index_good=0,0,0,0,0,0
    
    ##################################TO FAST PROCESS THEMES#################################
    for attr in attributes:
        if attr['type'] in ['themes','themes2']:
            dimensionName=attr['name']
            for obj in votes_map_details_array:
                s2_arr=[]
                obj_idlabels=set()
                s2_arr_extend=s2_arr.extend
                for val in obj[dimensionName]: 
                    v_theme_id=val[:val.index(' ')]
                    #print v_theme_id
                    obj_idlabels|={v_theme_id}
                    v=v_theme_id.split('.')
                    s2_arr_extend(['.'.join(v[0:x+1]) for x in range(len(v))])
                s2=set(s2_arr)
                obj[dimensionName+'0']=obj_idlabels#obj[dimensionName][:]
                if obj[dimensionName]==[]:
                    obj[dimensionName+'0']=[' ']
                obj[dimensionName]=s2
    ##################################TO FAST PROCESS THEMES#################################    
    
    for p,bitwise_p,stats in enumerator: 
        
        zip_pvote_filter=zip(p,subpattern_votes_filter)
        p_vote=[];p_vote_append=p_vote.append
        p_mep=[];p_mep_append=p_mep.append

        
        
        tuple_p=tuple();attr_ind=0
        for p_attr,y in zip_pvote_filter:
            if y:
                p_vote_append(p_attr)
            else:
                p_mep_append(p_attr)
            tuple_p+=(tuple(p_attr),)
            subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
            attr_ind+=1
        
        index+=1
        
        if exploration=='bfs':
            patterns_visited[tuple_p]={'pattern':p,'upper_bound':100,'quality':0.}
            pos_parents=possible_parents(p, arr_types, arr_data)
            pos_parents_tuple=[tuple(tuple(sub_x) for sub_x in p_attr) for p_attr in pos_parents]
            b_maxes_parents=[patterns_visited.get(p_attr,{'upper_bound':1000})['upper_bound'] for p_attr in pos_parents_tuple]
            borne_max_quality=min(b_maxes_parents)
            if (pruning and borne_max_quality<quality_threshold):
                skip_list_append(p)
                continue 
        
        
        
        #################################COMPUTE SUBGROUP et CHECK IF IT IS A FREQUENT PATTERN##########################"
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise_p) 
        nb_votes=len(filteredDataset_votes)
        #print p,set().union(*[obj[attributes[0]['name']] for obj in filteredDataset_votes])
#         raw_input('...')
        
        
        configuration['bitwise']=bitwise
        users_map_details_array_filtered_user2_pattern,unused_bitwise=filter_pipeline_obj(users_map_details_array_filtered_user2, subgroup_pipeline_for_meps) 
        users2_ids_pattern=set([p_attr[users_id_attributes] for p_attr in users_map_details_array_filtered_user2_pattern])    
        
        v_ids=set()
        dossiers_ids=set()
        #8479     4934     3733     3514     176
        if nb_votes<=threshold_pair_comparaison :
            if exploration=='bfs':
                skip_list_append(p)
            else:
                configuration['skip_list']=[p]
            if nb_votes<threshold_pair_comparaison :
                continue
        
        
        for obj in filteredDataset_votes:
            v_ids |= {obj[vote_id_attributes]}
            dossiers_ids |= {obj['DOSSIERID']}
        p_more_detailed=p
        #tuple_p_more_detailed=tuple_p
        ################CLOSED###################
        start=time()
        if closed:
            p_more_detailed=[];p_more_detailed_append=p_more_detailed.append
            arr_data_detailed=[];arr_data_detailed_append= arr_data_detailed.append
            arr_refin_detailed=[];arr_refin_detailed_append=arr_refin_detailed.append
            tuple_p_more_detailed=tuple()
            for i in range_len_attributes:
                attr=attributes[i];attr_name=attr['name'];attr_type=attr['type']
                subp=p[i]
                
                
                
                if attr_type=='numeric':
                    values=sorted({x[attr_name] for x in filteredDataset_votes})
                    arr_data_detailed_append(values)
                    arr_refin_detailed_append(None)
                    p_more_detailed_append([values[0],values[-1]])
                
                elif attr_type == 'themes':
                    attr_name0=attr_name+'0'
                    values=[x[attr_name0] for x in filteredDataset_votes] ##{y[:y.index(' ')] for y in x[attr_name+'0']}
                    values2=reduce(infimum,set([tuple(x) for x in values]))
                    arr_data_detailed_append(None)
                    arr_refin_detailed_append(None)
                    p_more_detailed_append(sorted(values2))
                elif attr_type == 'themes2':
                    attr_name0=attr_name+'0'
                    values={tuple(x[attr_name0]) for x in filteredDataset_votes} ##{y[:y.index(' ')] for y in x[attr_name+'0']}
                    values2=sorted(reduce(infimum2,values))
                    #arr_data_detailed_append(None)
                    arr_data_detailed_append(None)
                    arr_refin_detailed_append(values2)
                    p_more_detailed_append(values2)
                elif attr_type=='simple':
                    values=sorted({x[attr_name] for x in filteredDataset_votes})
                    arr_data_detailed_append(values)
                    arr_refin_detailed_append(len(values) if len(values)>1 else 0)
                    p_more_detailed_append(values)
                
                else :
                    arr_data_detailed_append(None)
                    arr_refin_detailed_append(None)
                    p_more_detailed_append(subp)
                tuple_p_more_detailed+=(tuple(p_more_detailed[-1]),)

#             if closed and all(p[i]==p_more_detailed[i] for i in range_len_attributes  if attributes[i]['type']<>'themes' ) and not all(respect_order(p[i],p_more_detailed[i]) for i in range_len_attributes  if attributes[i]['type']=='themes' ):
#                 if tuple_p_more_detailed in visited_patterns_more_detailed:
#                     spent+=time()-start
#                     configuration['skip_list']=[p]
#                     continue
#                 visited_patterns_more_detailed|={tuple_p_more_detailed}
                
            configuration['closing']=arr_data_detailed
            configuration['closing_refin']=arr_refin_detailed        
        spent+=time()-start
        ################################################
        
        
        
        nb_dossiers=len(dossiers_ids)
        
        if nb_dossiers<=nb_dossiers_min :
            if exploration=='bfs':
                skip_list_append(p)
            else:
                configuration['skip_list']=[p]
            if nb_dossiers<nb_dossiers_min:
                continue
        
        filteredDataset_meps_votes={}
        users_ids_set=set()
        max_votes_pairwise=0
        for key in users_ids:
            value=users_map_votes[key]
            votes_user=(value & v_ids)
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                filteredDataset_meps_votes[key]=votes_user
                users_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
        
        
        if max_votes_pairwise<=threshold_pair_comparaison :
            if exploration=='bfs':
                skip_list_append(p)
            else:
                configuration['skip_list']=[p]
            if max_votes_pairwise<threshold_pair_comparaison :
                continue
        
            
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set & users2_ids_pattern
        ###################NEEEEEW#############################
        nb_users_voted=len(users1_ids)+len(users2_ids_pattern)
        ###################NEEEEEW#############################
        
        #max_votes_pairwise=max(len(value) for key,value in filteredDataset_meps_votes.iteritems())
        
        index_frequent+=1
        
        ##########################################################################################
        
        
        ######################################COVER COMPUTING######################################
        
        if closed:
            if tuple_p_more_detailed in visited_patterns_more_detailed:
                spent+=time()-start
                #configuration['skip_list']=[p]
                index_has_been_visited+=1
                continue
            visited_patterns_more_detailed|={tuple_p_more_detailed}
                
        if not closed or cover_threshold<1.:        
            max_cover,b_max_cover,pattern_max,bitarray_bitwise,bitarray_bitwise_count=cover_max_computation_new(p,p_vote,p_mep, bitwise, patterns_visited_valid, cover_threshold)
        
            if (max_cover>=cover_threshold):
                if (pruning and b_max_cover<quality_threshold):
                    if exploration=='bfs':
                        skip_list_append(p)
                    else:
                        configuration['skip_list']=[p]
                continue
        
#         if tuple_p_more_detailed in visited_patterns_more_detailed:
#             continue
#         visited_patterns_more_detailed|={tuple_p_more_detailed}
        
        
        
#         max_cover_dossier=0
#         for ancient_dossiers_visited in dossiers_ids_visited:
#             
#             max_cover_dossier= max(max_cover_dossier,len(ancient_dossiers_visited & dossiers_ids) / float(len(ancient_dossiers_visited)))
#         if (max_cover_dossier>0.3):
#             continue
        
        #########################################################################################################

        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        configuration['stats']=returned_mepsStatistics
        issquare=(users1_ids_set==users2_ids_set)
        #print issquare
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        original_model,pattern_model=compute_models(original_mepwise_similarities,returned_mepsStatsNumbers,comparaison_measure,issquare)
        quality,borne_max_quality=compute_quality(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted,iwant)
        
        #quality,borne_max_quality=compute_quality_and_upper_boundOLD(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant,comparaison_measure)
        if exploration=='bfs': 
            patterns_visited[tuple_p]={'pattern':p,'upper_bound':borne_max_quality,'quality':quality}
        nb_quality_measured+=1
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        index_non_valid+=1
 
        if (pruning and borne_max_quality<quality_threshold):
            if exploration=='bfs':
                skip_list_append(p)
            else:
                configuration['skip_list']=[p]
            continue

      
        index_valid+=1
        
        label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[attr_ind]](p_more_detailed[attr_ind],arr_labels[attr_ind]) for attr_ind in range(len(p_more_detailed))]
        #print p,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',quality,'\t',borne_max_quality,'\t',quality>=quality_threshold,'\t',index,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid,'\t',index_good
        
        if exploration=='dfs':    
            print p_more_detailed,'\t',quality,'\t',borne_max_quality,'\t',nb_votes # parent_vote,'\t',parent_mep,'\t',


        if (quality>=quality_threshold):
            if not closed or cover_threshold<1.:
                if exploration=='dfs':                
                    patterns_visited[tuple_p]={'pattern':p,'dossiers':dossiers_ids,'bitwise':bitarray_bitwise,'bitwise_count':bitarray_bitwise_count,'upper_bound':borne_max_quality,'pattern_vote':p_vote,'pattern_user':p_mep}
                patterns_visited_valid[tuple_p]={'pattern':p,'dossiers':dossiers_ids,'bitwise':bitarray_bitwise,'bitwise_count':bitarray_bitwise_count,'upper_bound':borne_max_quality,'pattern_vote':p_vote,'pattern_user':p_mep}
            
            dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
            
            index_good+=1
            dossiers_voted=sorted([p_attr for p_attr in set([(v['PROCEDURE_TITLE'],float('%.2f' % ((sum([1 for p_attr in filteredDataset_votes if p_attr['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])/float(len(v_ids)))*100) ),sum([1 for p_attr in filteredDataset_votes if p_attr['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])) for v in filteredDataset_votes])],key=lambda p_attr : p_attr[1],reverse=True)
            interesting_patterns.append([p_more_detailed,label,dataset_stats,quality,borne_max_quality,dossiers_voted])
            if len(interesting_patterns)>top_k:
                interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                quality_threshold=interesting_patterns[-1][3]
    
    print index,'\t',index_has_been_visited,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid,'\t',index_good
    print 'TIMESPENT = ',spent
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
        
        
        

def generic_enumerators_top_k_old2(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute,exploration='dfs'): #disagreement
    
    #TODO : ENUMERATOR DIFFERENCIATE BETWEEN USER1 AND USER2 (don't do the half matrix everywhere !) 
    nb_quality_measured=0
    interesting_patterns=[]
    
    top_k=configuration.get('top_k',float('inf'))
    if top_k is None : 
        top_k=float('inf')
    quality_threshold=float(configuration.get('quality_threshold',0))
    if quality_threshold is None:
        quality_threshold=0
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    configuration['skip_list']=[]
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    
    
    patterns_visited,bitwises_visited,dossiers_ids_visited=[],[],[]
    patterns_visited_append,bitwises_visited_append,dossiers_ids_visited_append=patterns_visited.append,bitwises_visited.append,dossiers_ids_visited.append

    ############################### GET DISTINCT VALUES ####################################
    votes_map_details,votes_map_meps,users_map_details,users_map_votes,arr_distinct_values=get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    ##############################################################################################
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    
    
    users_ids=set([obj[users_id_attributes] for obj in users_map_details_array])
    
    users1_ids=set([x[users_id_attributes] for x in users_map_details_array_filtered_user1])
    users2_ids=set([x[users_id_attributes] for x in users_map_details_array_filtered_user2])
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    
    ############################STATS for * ######################################
    
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    
    original_mepwise_similarities={}
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2,comparaison_measure)
                
    ##############################################################################
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    configuration['stats']=original_mepsStatistics
    
    #ENUMERATORRRRRRR"
    enumerator=MAP_ENUMERATORS[exploration](arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None,stats=original_mepsStatistics)
    #159094    1.019    0.000    1.372
    #700413
    index,index_frequent,index_valid,index_non_valid,index_good=0,0,0,0,0
    for p,bitwise_p,stats in enumerator: 
        
        index+=1
        
        for attr_ind,p_attr in enumerate(p):
            subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
        

        #################################COMPUTE SUBGROUP et CHECK IF IT IS A FREQUENT PATTERN##########################"
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise_p) 
        configuration['bitwise']=bitwise
       
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        dossiers_ids=set([v['DOSSIERID'] for v in filteredDataset_votes])
        nb_dossiers=len(dossiers_ids)
        
        if nb_dossiers<nb_dossiers_min :
            configuration['skip_list'].append(p) 
            continue
        
        if nb_dossiers<=nb_dossiers_min:
            configuration['skip_list'].append(p)  
        
        
        
        
        filteredDataset_meps_votes={}
        for key in users_ids:
            value=users_map_votes[key]
            votes_participated=(value & v_ids)
            if len(votes_participated)>0:
                filteredDataset_meps_votes[key]=votes_participated
        
        
        users_ids_set=set(filteredDataset_meps_votes.keys())
        
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set
        

        max_votes_pairwise=max(len(value) for key,value in filteredDataset_meps_votes.iteritems())
        if max_votes_pairwise<threshold_pair_comparaison :
            configuration['skip_list'].append(p)   
            continue
        
        
        if max_votes_pairwise<=threshold_pair_comparaison:
            configuration['skip_list'].append(p) 
        
        index_frequent+=1
        
        ##########################################################################################
        
        
        ######################################COVER COMPUTING######################################
        
        max_cover,b_max_cover,pattern_max,bitarray_bitwise,bitarray_bitwise_count=cover_max_computation(p, bitwise, patterns_visited, bitwises_visited, cover_threshold)
        
        
        if (max_cover>=cover_threshold):
            if (pruning and b_max_cover<quality_threshold):
                configuration['skip_list'].append(p)  
            continue
        
        
        
#         max_cover_dossier=0
#         for ancient_dossiers_visited in dossiers_ids_visited:
#             
#             max_cover_dossier= max(max_cover_dossier,len(ancient_dossiers_visited & dossiers_ids) / float(len(ancient_dossiers_visited)))
#         if (max_cover_dossier>0.3):
#             continue
        
        #########################################################################################################

        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        configuration['stats']=returned_mepsStatistics
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        original_model,pattern_model=compute_models(original_mepwise_similarities,returned_mepsStatsNumbers,comparaison_measure)
        quality,borne_max_quality=compute_quality(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted,iwant)
        
        #quality,borne_max_quality=compute_quality_and_upper_boundOLD(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant,comparaison_measure)
        if exploration=='bfs': 
            patterns_visited_append(p)
            dossiers_ids_visited_append(dossiers_ids)
            bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
        nb_quality_measured+=1
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        index_non_valid+=1
        
        if exploration=='bfs':
            pos_parents=possible_parents(p, arr_types, arr_data)
            for p_visited,(t1,t2,b_visited) in izip(patterns_visited,bitwises_visited):
                if p_visited in pos_parents:
                    borne_max_quality=min(borne_max_quality,b_visited)
            
        
        if (pruning and borne_max_quality<quality_threshold):
            
            configuration['skip_list'].append(p)  
            continue

      
        index_valid+=1
        
        label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],arr_labels[i]) for i in range(len(p))]
        print p,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',quality,'\t',borne_max_quality,'\t',quality>=quality_threshold,'\t',index,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid,'\t',index_good
        #print p,'\t',quality,'\t',borne_max_quality
            
        if (quality>=quality_threshold):
            if exploration=='dfs':                
                patterns_visited_append(p)
                dossiers_ids_visited_append(dossiers_ids)
                bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
 
            dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
            
            index_good+=1
            dossiers_voted=sorted([x for x in set([(v['PROCEDURE_TITLE'],float('%.2f' % ((sum([1 for x in filteredDataset_votes if x['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])/float(len(v_ids)))*100) ),sum([1 for x in filteredDataset_votes if x['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])) for v in filteredDataset_votes])],key=lambda x : x[1],reverse=True)
            interesting_patterns.append([p,label,dataset_stats,quality,borne_max_quality,dossiers_voted])
            if len(interesting_patterns)>top_k:
                interesting_patterns=sorted(interesting_patterns,key=lambda x : x [3],reverse=True)[:top_k]
                quality_threshold=interesting_patterns[-1][3]
    
    
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted in sorted(interesting_patterns,key=lambda x : x [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted


def generic_enumerators_top_k_old(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute): #disagreement
    
    
    #TODO : ENUMERATOR DIFFERENCIATE BETWEEN USER1 AND USER2 (don't do the half matrix everywhere !) 
    nb_quality_measured=0
    interesting_patterns=[]
    
    top_k=configuration.get('top_k',float('inf'))
    if top_k is None : 
        top_k=float('inf')
    quality_threshold=float(configuration.get('quality_threshold',0))
    if quality_threshold is None:
        quality_threshold=0
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    configuration['skip_list']=[]
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    ############################STATS for * ######################################
    
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute)
    
    original_mepwise_similarities={}
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2,comparaison_measure)
                
    ##############################################################################
    
    patterns_visited,subpatterns_votes_visited,subpatterns_users_visited,bitwises_visited,dossiers_ids_visited=[],[],[],[],[]
    patterns_visited_append,subpatterns_votes_visited_append,subpatterns_users_visited_append,bitwises_visited_append,dossiers_ids_visited_append=patterns_visited.append,subpatterns_votes_visited.append,subpatterns_users_visited.append,bitwises_visited.append,dossiers_ids_visited.append

    ############################### GET DISTINCT VALUES ####################################
    votes_map_details,votes_map_meps,users_map_details,users_map_votes,arr_distinct_values=get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    ##############################################################################################
    
    #####################AGREEMENT_INDEX######################"
      
#     users_avg_agreement_index={u:sum([x[1] for x in votes_ai])/float(len(votes_ai)) for u,votes_ai in users_map_votes_agreement_index.iteritems() if users_map_details[u]['MAJORITY']}
#        
#     for u in users_avg_agreement_index:
#         nb_votes_u=float(len(users_map_votes_agreement_index[u]))
#         original_mepwise_similarities[u][u]=(users_avg_agreement_index[u]*nb_votes_u,nb_votes_u)
#        

    #########################################################"
    
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    configuration['stats']=original_mepsStatistics
    
    
    enumerator=generic_enumerator_multiattributes_dfs(arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None,stats=original_mepsStatistics)
    index,index_frequent,index_valid,index_non_valid,index_good=0,0,0,0,0
    
    
    for p,bitwise_p,stats in enumerator: 
        index+=1
        
        subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
        subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
        
        
        for attr_ind,p_attr in enumerate(p):
            subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
        
        
        #################################COMPUTE SUBGROUP et CHECK IF IT IS A FREQUENT PATTERN##########################"
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise_p) 
        configuration['bitwise']=bitwise
       
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        dossiers_ids=set([v['DOSSIERID'] for v in filteredDataset_votes])
        nb_dossiers=len(dossiers_ids)
        
        if nb_dossiers<nb_dossiers_min :
            configuration['skip_list']=[p] 
            continue
        
        
        
        
        users_map_details_array_filtered=filter_pipeline_obj(users_map_details_array, subgroup_pipeline_for_meps)[0]
        
        users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array_filtered, user1_scope)[0]
        users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array_filtered, user2_scope)[0]
        
        
        users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
        
        users1_ids=set([x[users_id_attributes] for x in users_map_details_array_filtered_user1])
        users2_ids=set([x[users_id_attributes] for x in users_map_details_array_filtered_user2])
        
        filteredDataset_meps_votes={}
        for key in users_ids:
            value=users_map_votes[key]
            votes_participated=(value & v_ids)
            if len(votes_participated)>0:
                filteredDataset_meps_votes[key]=votes_participated
        
        
        users_ids_set=set(filteredDataset_meps_votes.keys())
        
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set
        
        nb_users_voted=len(users1_ids)+len(users2_ids)
        
        max_votes_pairwise=max(len(value) for key,value in filteredDataset_meps_votes.iteritems())
        if max_votes_pairwise<threshold_pair_comparaison :
            configuration['skip_list']=[p]  
            continue
        
        index_frequent+=1
        
        ##########################################################################################
        
        
        ######################################COVER COMPUTING######################################
        
        max_cover,b_max_cover,pattern_max,bitarray_bitwise,bitarray_bitwise_count=cover_max_computation_OLD(p, subpattern_users, bitwise, patterns_visited, subpatterns_users_visited, bitwises_visited, cover_threshold)
        
        if (max_cover>=cover_threshold):
            if (pruning and b_max_cover<quality_threshold):
                configuration['skip_list']=[p] 
            continue
        
#         max_cover_dossier=0
#         for ancient_dossiers_visited in dossiers_ids_visited:
#             
#             max_cover_dossier= max(max_cover_dossier,len(ancient_dossiers_visited & dossiers_ids) / float(len(ancient_dossiers_visited)))
#         if (max_cover_dossier>0.3):
#             continue
        
        #########################################################################################################

        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        configuration['stats']=returned_mepsStatistics
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        #########################AGREEMENT INDEX###########################
#         users_map_votes_agreement_index_pattern={}
#         for u in returned_mepsMeta:
#             if returned_mepsMeta[u]['MAJORITY']:
#                 users_map_votes_agreement_index_pattern[u]=[(v,agr) for v,agr in users_map_votes_agreement_index[u] if v in v_ids]
#           
#           
#         users_avg_agreement_index_pattern={u:sum([x[1] for x in votes_ai])/float(len(votes_ai)) for u,votes_ai in users_map_votes_agreement_index_pattern.iteritems()}
#         for u in users_avg_agreement_index_pattern:
#             if returned_mepsStatsNumbers.has_key(u):
#                 if returned_mepsStatsNumbers[u].has_key(u):
#                     returned_mepsStatsNumbers[u][u]['YY']=users_avg_agreement_index_pattern[u]*returned_mepsStatsNumbers[u][u]['NB_VOTES']
#                     returned_mepsStatsNumbers[u][u]['NN']=0.
#                     returned_mepsStatsNumbers[u][u]['AA']=0.
            
        
        #########################AGREEMENT INDEX###########################
        quality,borne_max_quality=compute_quality_and_upper_boundOLD(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant,comparaison_measure)
        nb_quality_measured+=1
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        index_non_valid+=1
        
        if (pruning and borne_max_quality<quality_threshold):
            configuration['skip_list']=[p] 
            continue

      
        index_valid+=1
        
        label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],arr_labels[i]) for i in range(len(p))]
        print p,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',quality,'\t',borne_max_quality,'\t',quality>=quality_threshold,'\t',index,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid,'\t',index_good
            
        if (quality>=quality_threshold):
            patterns_visited_append(p)
            subpatterns_votes_visited_append(subpattern_vote)
            subpatterns_users_visited_append(subpattern_users)
            dossiers_ids_visited_append(dossiers_ids)
            bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
            
            dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
            
            index_good+=1
            dossiers_voted=sorted([x for x in set([(v['PROCEDURE_TITLE'],float('%.2f' % ((sum([1 for x in filteredDataset_votes if x['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])/float(len(v_ids)))*100) ),sum([1 for x in filteredDataset_votes if x['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])) for v in filteredDataset_votes])],key=lambda x : x[1],reverse=True)
            interesting_patterns.append([p,label,dataset_stats,quality,borne_max_quality,dossiers_voted])
            if len(interesting_patterns)>top_k:
                interesting_patterns=sorted(interesting_patterns,key=lambda x : x [3],reverse=True)[:top_k]
                quality_threshold=interesting_patterns[-1][3]
    
    
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted in sorted(interesting_patterns,key=lambda x : x [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted