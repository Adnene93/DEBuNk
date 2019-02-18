'''
Created on 8 janv. 2017

@author: Adnene
'''
'''
Created on 22 dec. 2016

@author: Adnene
'''

from Queue import Queue
import itertools
from math import sqrt
import math
from random import random
import re
from time import time 

from bitarray import bitarray
from  sortedcontainers import SortedList, SortedSet, SortedDict, SortedListWithKey

from EMM_ENUMERATOR.enumerator_nominal import children_nominal, value_to_yield_nominal, \
    description_from_pattern_nominal, possible_parents_nominal
from EMM_ENUMERATOR.enumerator_numbers import children_num, value_to_yield_num, \
    description_from_pattern_num, possible_parents_numeric
from EMM_ENUMERATOR.enumerator_simple import children_simple, \
    value_to_yield_simple, description_from_pattern_simple
from EMM_ENUMERATOR.enumerator_themes import all_childrens_set_opt_depthmax, value_to_yield_themes, \
    createTreeOutOfThemes, description_from_pattern_themes, \
    possible_parents_themes
from filterer.filter import filter_pipeline_obj
from votesExtractionAndProcessing.pairwiseStatistics import extractStatistics_fromdataset_new, \
    extractStatistics_fromdataset_new_update, datasetStatistics, \
    extractStatistics_fromdataset_new_update_not_square
from votesExtractionAndProcessing.votesPairwiseStatistics import extractVotesStatistics_fromdataset, \
    extractVotesStatistics_fromdataset_update


POSSIBLE_ENUMERATOR_CHILDREN={
    'numeric':children_num,
    'nominal':children_nominal,
    'themes':all_childrens_set_opt_depthmax,
    'simple':children_simple
} 

POSSIBLE_ENUMERATOR_PARENTS={
    'numeric':possible_parents_numeric,
    'nominal':possible_parents_nominal,
    'themes':possible_parents_themes
} 

POSSIBLE_ENUMERATOR_YIELDER={
    'numeric':value_to_yield_num,
    'nominal':value_to_yield_nominal,
    'themes':value_to_yield_themes,
    'simple':value_to_yield_simple
}

POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER={
    'numeric':description_from_pattern_num,
    'nominal':description_from_pattern_nominal,
    'themes':description_from_pattern_themes,
    'simple':description_from_pattern_simple
}


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
        new_child_refinement_index_arr[refinement_index_attr]=refin#deepcopy(refin)
        possibleChildrens_arr.append(new_child_arr)
        possibleChildrens_types.append(new_child_types)
        possibleChildrens_refinement_index_arr.append(new_child_refinement_index_arr)
        
    return possibleChildrens_arr,possibleChildrens_types,possibleChildrens_refinement_index_arr


def value_to_yield(arr_data,arr_types,refinement_index_attr):
    yielded_item=[]
    for arr,typeAttr in zip(arr_data,arr_types): #zip(arr_data[:refinement_index_attr+1],arr_types[:refinement_index_attr+1]) 
        yielded_attr=POSSIBLE_ENUMERATOR_YIELDER[typeAttr](arr)
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
    
    



def generic_enumerators_rec(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr)
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
    #         return
    #     else : 
            yield yielded_item
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childs[0])):
                    for p in generic_enumerators_rec(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin):
                        yield p



def generic_enumerators_rec_subgroupBitwise(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr)
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
            print yielded_item
            yield yielded_item,bitwise
        bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None and any(b is not None for b in configuration['bitwise'])) else bitwise
        #configuration['bitwise']=None  
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childs[0])):
                    for p,psg_bitwise in generic_enumerators_rec_subgroupBitwise(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin,bitwiseConfig):
                        yield p,psg_bitwise                        


def generic_enumerators_rec_subgroupBitwise_bfs(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None): #TODO!
    fifo=[]
    appender=fifo.append
    popper=fifo.pop
    level=0
    index=0
    appender([arr_data,arr_types,refinement_index_arr,refinement_index_attr,bitwise,level])
    
    while (len(fifo))>0:
        actual_arr_data,actual_arr_types,actual_refinement_index_arr,actual_refinement_index_attr,actual_bitwise,actual_level = popper(0)
        yielded_item=value_to_yield(actual_arr_data,actual_arr_types,actual_refinement_index_arr)
        
        if (yielded_item is None or all(x not in configuration['skip_list'] for x in possible_parents(yielded_item, arr_types, arr_data))):
            if yielded_item is not None :
                print yielded_item,actual_level,index
                index+=1
                yield yielded_item,actual_bitwise
                
            if yielded_item not in configuration['skip_list']:
                bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None and any(b is not None for b in configuration['bitwise'])) else actual_bitwise
                for actual_refin in range(actual_refinement_index_attr,len(arr_data)):
                    childs=children_generic(actual_arr_data, actual_arr_types,actual_refinement_index_arr,depthmax_arr,configuration, actual_refin)
                    for pos in range(len(childs[0])):
                        child_pattern=childs[0][pos]+actual_arr_data[actual_refin+1:]
                        child_pattern_types=childs[1][pos]+actual_arr_types[actual_refin+1:]
                        #if (level==0) or (random()<(1-(float(level)/20))):
                        appender([child_pattern,child_pattern_types,childs[2][pos]+actual_refinement_index_arr[actual_refin+1:],actual_refin,bitwiseConfig,actual_level+1])
                        

def generic_enumerators(arr_data,arr_types,configuration,depthmax_arr=None):
    if depthmax_arr is None:
        depthmax_arr=[None for arr in arr_data]
    
    
    
    refinement_index_arr=[]
    descriptions_label_maps=[] #it's an array with the same length as the number of attributes where each case contain a map linking the pattern to it's description
    index=0
    for attr,type_attr in zip(arr_data,arr_types):
        if type_attr=='numeric':
            refinement_index_arr.append(0)
            descriptions_label_maps.append({})
        elif type_attr=='nominal':
            refinement_index_arr.append(len(attr))
            descriptions_label_maps.append({})
        elif type_attr=='themes':
            refinement_index_arr.append(0)
            tree,themesMAP=createTreeOutOfThemes(arr_data[index])
            arr_data[index]=[tree]
            descriptions_label_maps.append(themesMAP)
        index+=1
    for p in generic_enumerators_rec(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration):
        
        description = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],descriptions_label_maps[i]) for i in range(len(p))]
        yield p,description
        #raw_input("Press Enter to continue...")
    
    
def generic_enumerators_subgroupBitwise(arr_data,arr_types,configuration,depthmax_arr=None):
    if depthmax_arr is None:
        depthmax_arr=[None for arr in arr_data]
    
    
    
    refinement_index_arr=[]
    descriptions_label_maps=[] #it's an array with the same lungth as the number of attributes where each case contain a map linking the pattern to it's description
    index=0
    for attr,type_attr in zip(arr_data,arr_types):
        if type_attr=='numeric':
            refinement_index_arr.append(0)
            descriptions_label_maps.append({})
        elif type_attr=='nominal':
            refinement_index_arr.append(len(attr))
            descriptions_label_maps.append({})
        elif type_attr=='themes':
            refinement_index_arr.append(0)
            tree,themesMAP=createTreeOutOfThemes(arr_data[index])
            arr_data[index]=[tree]
            descriptions_label_maps.append(themesMAP)
        index+=1
    
    biwtises=configuration.get('bitwise',None)
    for p,bitwise in generic_enumerators_rec_subgroupBitwise(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,bitwise=biwtises):
        
        description = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],descriptions_label_maps[i]) for i in range(len(p))]
        yield p,description,bitwise
        
        

        


def get_arrdata_from_dataset_values(arr_distinct_values,attributes,votes_attributes,users_attributes,position_attribute):
    nb_attributes=len(arr_distinct_values)
    range_nb_attributes=range(nb_attributes)
    
    arr_data=[]
    arr_types=[]
    arr_depthmax=[]
    arr_refinement_indexes=[]
    arr_labels=[]
    subgroup_pipeline=[]
    subgroup_pipeline_for_votes=[]
    filter_operations=[]
    
    alpha = r' [a-zA-Z]'
    
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
            
            #subgroup_pipeline[-1]['likeContainSet']=[] 
            #filter_operations.append('likeContainSet')
    
    subgroup_pipeline_for_votes=[stage for stage in subgroup_pipeline if stage['dimensionName'] in votes_attributes]
    subgroup_pipeline_for_meps=[stage for stage in subgroup_pipeline if stage['dimensionName'] in users_attributes]
    return arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps

'''
attributes=[
attribute= {
    'name' : name_attribute,
    'type' : 'themes' | 'numeric' | 'nominal',
    'depthmax': None | 'or a value'
}
]
'''


def generic_enumerators_rec_subgroupBitwise_subgroups(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr)
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
            
            yield yielded_item,bitwise
        bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else bitwise
        #configuration['bitwise']=None  
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childs[0])):
                    for p,psg_bitwise in generic_enumerators_rec_subgroupBitwise_subgroups(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin,bitwiseConfig):
                        yield p,psg_bitwise       
                        
                        
def generic_enumerators_dataset(dataset,attributes,configuration,votes_attributes,users_attributes,position_attribute):
    ####
    # start by getting distinct values #
    ####
    
    configuration['skip_list']=[]
    nb_attributes=len(attributes)
    range_nb_attributes=range(nb_attributes)
    arr_distinct_values=[SortedSet() for i in range_nb_attributes]
    
    votes_map_details={}
    votes_map_meps={}
    votes_map_details_has_key=votes_map_details.has_key
    votes_map_details_array=[]
    votes_map_meps_has_key=votes_map_meps.has_key
    
    vote_id_attributes=votes_attributes[0]
    
    users_map_votes={}
    users_map_votes_has_key=users_map_votes.has_key
    users_map_details={}
    users_map_details_has_key=users_map_details.has_key
    
    users_id_attributes=users_attributes[0]
    
    #sortedDataset=SortedListWithKey([{'a': 2, 'b': 0}, {'a': 1, 'b': 1}, {'a': 0, 'b': 2}],lambda x : x['VOTEID'])
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    
    patterns_visited=[]
    subpatterns_votes_visited=[]
    subpatterns_users_visited=[]
    bitwises_visited=[]
    patterns_visited_append=patterns_visited.append
    subpatterns_votes_visited_append=subpatterns_votes_visited.append
    subpatterns_users_visited_append=subpatterns_users_visited.append
    bitwises_visited_append=bitwises_visited.append
    
    
    for d in dataset:
        for i,attr in enumerate(attributes):
            
            obj_attr_value=d[attr['name']]
            values=set()
            if hasattr(obj_attr_value, '__iter__'):
                values={v for v in obj_attr_value}
            else :
                values={obj_attr_value}
            arr_distinct_values[i] |= values
        
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=[]
        votes_map_meps[d_vote_id].append(d)
        
        
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    
    
    
    for p,bitwise in generic_enumerators_rec_subgroupBitwise_subgroups(arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None):
        
        for attr_ind,p_attr in enumerate(p):
            if attributes[attr_ind]['type']=='themes':
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
            else:
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
            
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise) 
        
        
        
        configuration['bitwise']=bitwise
        
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        
        nb_dossiers=len(set([v['DOSSIERID'] for v in filteredDataset_votes]))
        
        
        if nb_dossiers<15 :
            configuration['skip_list']=[p] 
            continue
        
        users_map_details_array_filtered=filter_pipeline_obj(users_map_details_array, subgroup_pipeline_for_meps)[0]
        users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
        filteredDataset_meps_votes={key:(users_map_votes[key] & v_ids) for key in users_ids}
        
        avg_votes_by_users= float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(len(users_ids))
        
        
        if avg_votes_by_users<25 :
            configuration['skip_list']=[p] 
            continue
        
        bitarray_bitwise=bitarray(bitwise)
        bitarray_bitwise_count=bitarray_bitwise.count()
        subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
        subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
        
        
        max_cover=0
        for (b,count_obj),p_users_visited in zip(bitwises_visited,subpatterns_users_visited):
            if (bitarray_bitwise_count<=count_obj) and (p_users_visited==subpattern_users):  
                act_cover=(float((bitarray_bitwise & b).count()) / count_obj)
                max_cover=max(max_cover,act_cover)
                if max_cover==1:
                    break
        
        if (max_cover==1):
            continue
        
          
        patterns_visited_append(p)
        subpatterns_votes_visited_append(subpattern_vote)
        subpatterns_users_visited_append(subpattern_users)
        bitwises_visited_append((bitarray_bitwise,bitarray_bitwise.count()))
        
        #filter_pipeline_obj(votes_map_meps[key],subgroup_pipeline_for_meps)[0]
        
        filteredDataset_votes_meps={key: [v for v in votes_map_meps[key] if v[users_id_attributes] in users_ids] for key in v_ids}
        filteredDataset=[item  for li in filteredDataset_votes_meps.values() for item in li]
        
        
        description = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],arr_labels[i]) for i in range(len(p))]
        
        
        
        print p,nb_dossiers,len(v_ids),max_cover
        
        
        yield p,description,filteredDataset
    

def generic_enumerators_rec_subgroupBitwise_subgroups_stats(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr)
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
            
            yield yielded_item,bitwise
        bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else bitwise
        configuration['bitwise']=None  
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childs[0])):
                    for p,psg_bitwise in generic_enumerators_rec_subgroupBitwise_subgroups_stats(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin,bitwiseConfig):
                        yield p,psg_bitwise 




def generic_enumerators_dataset_stats(dataset,attributes,configuration,votes_attributes,users_attributes,position_attribute):
    ####
    # start by getting distinct values #
    ####
    
    start=time()
    ##########STATS * ###################"
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_new(dataset,votes_attributes,users_attributes,position_attribute)
    
    #print 'nb item : ', len(dataset)
    ######################################
    
    nb_dossiers_min=configuration['nb_dossiers_min']
    avg_users_votes_min=configuration['avg_users_votes_min']
    cover_threshold=configuration['cover_threshold']
    
    configuration['skip_list']=[]
    nb_attributes=len(attributes)
    range_nb_attributes=range(nb_attributes)
    arr_distinct_values=[SortedSet() for i in range_nb_attributes]
    
    votes_map_details={}
    votes_map_meps={}
    votes_map_details_has_key=votes_map_details.has_key
    votes_map_details_array=[]
    votes_map_meps_has_key=votes_map_meps.has_key
    
    vote_id_attributes=votes_attributes[0]
    
    users_map_votes={}
    users_map_votes_has_key=users_map_votes.has_key
    users_map_details={}
    users_map_details_has_key=users_map_details.has_key
    
    users_id_attributes=users_attributes[0]
    
    #sortedDataset=SortedListWithKey([{'a': 2, 'b': 0}, {'a': 1, 'b': 1}, {'a': 0, 'b': 2}],lambda x : x['VOTEID'])
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    
    patterns_visited=[]
    subpatterns_votes_visited=[]
    subpatterns_users_visited=[]
    bitwises_visited=[]
    patterns_visited_append=patterns_visited.append
    subpatterns_votes_visited_append=subpatterns_votes_visited.append
    subpatterns_users_visited_append=subpatterns_users_visited.append
    bitwises_visited_append=bitwises_visited.append
    
    
    for d in dataset:
        for i,attr in enumerate(attributes):
            
            obj_attr_value=d[attr['name']]
            values=set()
            if hasattr(obj_attr_value, '__iter__'):
                values={v for v in obj_attr_value}
            else :
                values={obj_attr_value}
            arr_distinct_values[i] |= values
        
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=[]
        votes_map_meps[d_vote_id].append(d)
        
    nb_votes_origin=len(votes_map_meps.keys())
    nb_meps_origin=len(users_map_details.keys())
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    
    
    enumerator=generic_enumerators_rec_subgroupBitwise_subgroups_stats(arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None)
    
    #print 'time spent initializing the enumerator : ' , time()-start
    index=0
    for p,bitwise in enumerator:
        index+=1
        for attr_ind,p_attr in enumerate(p):
            if attributes[attr_ind]['type']=='themes':
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
            else:
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
            
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise) 
        configuration['bitwise']=bitwise
        
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        nb_dossiers=len(set([v['DOSSIERID'] for v in filteredDataset_votes]))
        
        if nb_dossiers<nb_dossiers_min :
            configuration['skip_list']=[p] 
            continue
        
        users_map_details_array_filtered=filter_pipeline_obj(users_map_details_array, subgroup_pipeline_for_meps)[0]
        users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
        filteredDataset_meps_votes={key:(users_map_votes[key] & v_ids) for key in users_ids}
        
        avg_votes_by_users= float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(len(users_ids))
        
        if avg_votes_by_users<avg_users_votes_min : #avg_votes_by_users it's not LOGIC because patterns with restricted list of meps can have an average who is greater than the minimum threshold
            configuration['skip_list']=[p] 
            continue
        
        bitarray_bitwise=bitarray(bitwise)
        bitarray_bitwise_count=bitarray_bitwise.count()
        subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
        subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
        
        max_cover=0
        for (b,count_obj),p_users_visited in zip(bitwises_visited,subpatterns_users_visited):
            if (bitarray_bitwise_count<=count_obj) and (p_users_visited==subpattern_users):  
                act_cover=(float((bitarray_bitwise & b).count()) / count_obj)
                max_cover=max(max_cover,act_cover)
                if max_cover>=cover_threshold:
                    break
        
        if (max_cover>=cover_threshold):
            continue
        
         
         
         
        patterns_visited_append(p)
        subpatterns_votes_visited_append(subpattern_vote)
        subpatterns_users_visited_append(subpattern_users)
        bitwises_visited_append((bitarray_bitwise,bitarray_bitwise.count()))
        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update(original_mepsStatistics, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids)
        dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
        
        
        
        borne_min=sum([(max( (((item['YY']+item['NN']+item['AA'])/float(item['NB_VOTES']))-1) *(float(item['NB_VOTES'])/float(25)) +1  ,0) - (float(original_mepsStatsNumbers[item['USER1']][item['USER2']]['YY']+original_mepsStatsNumbers[item['USER1']][item['USER2']]['NN']+original_mepsStatsNumbers[item['USER1']][item['USER2']]['AA'])/original_mepsStatsNumbers[item['USER1']][item['USER2']]['NB_VOTES'])) if (item['NB_VOTES'] > 25) else 0 for item in dataset_stats])/float(len(users_ids))
        borne_max=sum([(min(((item['YY']+item['NN']+item['AA'])/float(25)),1) - (float(original_mepsStatsNumbers[item['USER1']][item['USER2']]['YY']+original_mepsStatsNumbers[item['USER1']][item['USER2']]['NN']+original_mepsStatsNumbers[item['USER1']][item['USER2']]['AA'])/original_mepsStatsNumbers[item['USER1']][item['USER2']]['NB_VOTES'])) if (item['NB_VOTES'] > 25) else 0 for item in dataset_stats])/float(len(users_ids))
        
        label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],arr_labels[i]) for i in range(len(p))]
        print p,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',borne_min,'\t',borne_max,'\t',index
        
        
        yield p,label,dataset_stats,borne_min,borne_max 
        
        

def get_sim_vectors(stats,user1,user2):
    return float(stats[user1][user2]['YY']+stats[user1][user2]['NN']+stats[user1][user2]['AA']),stats[user1][user2]['NB_VOTES']            

# def get_sim_new(stats,user1,user2):
#     return float(stats[user1][user2]['YY']+stats[user1][user2]['NN']+stats[user1][user2]['AA']),stats[user1][user2]['NB_VOTES'] 


def generic_enumerator_multiattributes_dfs(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None,stats=None): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr)
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
            yield yielded_item,bitwise,stats
        
        bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else bitwise
        statsConfig=configuration['stats'] if (configuration['stats'] is not None) else stats
        configuration['stats']=None
        configuration['bitwise']=None  
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childs[0])):
                    for p,psg_bitwise,psg_stats in generic_enumerator_multiattributes_dfs(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin,bitwiseConfig,statsConfig):
                        yield p,psg_bitwise,psg_stats
                        


                        

def generic_enumerators_rec_subgroupBitwise_subgroups_stats_new_CHILDS(arr_data,arr_types,refinement_index_arr,depthmax_arr,configuration,refinement_index_attr=0,bitwise=None,stats=None): #TODO!
    yielded_item=value_to_yield(arr_data,arr_types,refinement_index_attr)
    expectedChilds=[]
    if yielded_item not in configuration['skip_list'] :
        if yielded_item is not None :
            
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childsx=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childsx[0])):
                    oneChildPattern=value_to_yield(childsx[0][pos]+arr_data[actual_refin+1:],childsx[1][pos]+arr_types[actual_refin+1:],childsx[2][pos]+refinement_index_arr[actual_refin+1:])
                    if oneChildPattern is not None : 
                        expectedChilds.append(oneChildPattern)
                    
            yield yielded_item,bitwise,stats,expectedChilds
        
        bitwiseConfig=configuration['bitwise'] if (configuration['bitwise'] is not None) else bitwise
        statsConfig=configuration['stats'] if (configuration['stats'] is not None) else stats
        configuration['stats']=None
        #configuration['bitwise']=None  
        if  yielded_item not in configuration['skip_list']:
            for actual_refin in range(refinement_index_attr,len(arr_data)):
                childs=children_generic(arr_data, arr_types,refinement_index_arr,depthmax_arr,configuration, actual_refin)
                for pos in range(len(childs[0])):
                    for p,psg_bitwise,psg_stats,psg_childs in generic_enumerator_multiattributes_dfs(childs[0][pos]+arr_data[actual_refin+1:],childs[1][pos]+arr_types[actual_refin+1:],childs[2][pos]+refinement_index_arr[actual_refin+1:],depthmax_arr,configuration,actual_refin,bitwiseConfig,statsConfig):
                        yield p,psg_bitwise,psg_stats,psg_childs
                        
              
              



def get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute):
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    range_nb_attributes=range(len(attributes))
    votes_map_details={}
    users_map_details={}
    votes_map_meps={}
    users_map_votes={}
    users_map_votes_agreement_index={}
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
            arr_distinct_values[i] |= values
        
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
            users_map_votes_agreement_index[d_user_id]=[]
        users_map_votes[d_user_id] |= {d_vote_id}
        
        ###########AGREEMENT_INDEX#####################
        users_map_votes_agreement_index[d_user_id] +=  [(d_vote_id,d['AgreementIndex'])]
        ###########AGREEMENT_INDEX#####################
        
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=SortedSet()
        votes_map_meps[d_vote_id] |= {d_user_id}
        
    return votes_map_details,votes_map_meps,users_map_details,users_map_votes,users_map_votes_agreement_index,arr_distinct_values


def compute_quality_and_upper_bound(original_mepwise_similarities,pattern_mepsStatsNumbers,nb_users_voted,threshold_pair_comparaison,iwant='disagreement'):
    
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
            #if user2<user1:
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2)
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
                    qps_append(math.copysign(qp,1))
                    qps_max_append(math.copysign(diff_p_max_expected,1))
                
    
    
    quality=sqrt(sum(x**2 for x in qps))/float(nb_users_voted) #* (nb_interesting/nb_pair)
    borne_max_quality=sqrt(sum(x**2 for x in qps_max))/float(nb_users_voted) #* (nb_interesting_max/nb_pair)
    
    #ratio_interesting_dep = [x/float(nb_users_voted)>0.8 for x in arr_interesting].count(True)/float(nb_users_voted)
    #ratio_interesting_dep_max = [x/float(nb_users_voted)>0.8 for x in arr_interesting_max].count(True)/float(nb_users_voted)
    #print ratio_interesting_dep,ratio_interesting_dep_max
    
#     quality*=ratio_interesting_dep
#     borne_max_quality*=ratio_interesting_dep_max
    
    return quality,borne_max_quality

def compute_quality_and_upper_bound_standard(original_mepwise_similarities,pattern_mepsStatsNumbers,nb_users_voted,threshold_pair_comparaison):
    
    
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    for user1 in pattern_mepsStatsNumbers:
        for user2 in pattern_mepsStatsNumbers[user1]:
            if user2<user1:
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2)
                agg_o,all_o=original_mepwise_similarities[user1][user2]
                
                if all_p>=threshold_pair_comparaison:
                    agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                    min_sim_expected=agg_min/threshold_pair_comparaison
                    diff_p_min_expected=min_sim_expected-(agg_o/all_o)
                    
                    agg_max=float(min(agg_p,threshold_pair_comparaison))
                    max_sim_expected=agg_max/threshold_pair_comparaison
                    diff_p_max_expected=max_sim_expected-(agg_o/all_o)
                    
                    
                    qp=(agg_p/all_p)-(agg_o/all_o)
                    
                    qp_max_expected=max(math.copysign(diff_p_min_expected,1),math.copysign(diff_p_max_expected,1))
                    
                    qps_append(math.copysign(qp,1))
                    qps_max_append(math.copysign(qp_max_expected,1))
                
    
    quality=sqrt(sum(qps)*2)/float(nb_users_voted)
    borne_max_quality=sqrt(sum(qps_max)*2)/float(nb_users_voted)
    
    return quality,borne_max_quality

def cover_max_computation(actual_pattern,actual_subpattern_user,bitwise_pattern,patterns_visited,subpatterns_users_visited,bitwises_visited,cover_threshold):
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

def generic_enumerators_dataset_stats_two_cases(dataset,attributes,configuration,votes_attributes,users_attributes,position_attribute): #disagreement
    
    
    #TODO : ENUMERATOR DIFFERENCIATE BETWEEN USER1 AND USER2 (don't do the half matrix everywhere !) 
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    disagreement=(iwant=='disagreement')
    nb_dossiers_min=configuration['nb_dossiers_min']
    avg_users_votes_min=configuration['avg_users_votes_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    quality_threshold=float(configuration['quality_threshold'])
    configuration['skip_list']=[]
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    ############################STATS for * ######################################
    
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_new(dataset,votes_attributes,users_attributes,position_attribute)
    original_mepwise_similarities={}
    
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            if user2<user1:
                original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2)
    
    ##############################################################################
    
    patterns_visited,subpatterns_votes_visited,subpatterns_users_visited,bitwises_visited=[],[],[],[]
    patterns_visited_append,subpatterns_votes_visited_append,subpatterns_users_visited_append,bitwises_visited_append=patterns_visited.append,subpatterns_votes_visited.append,subpatterns_users_visited.append,bitwises_visited.append

    ############################### GET DISTINCT VALUES ####################################
    votes_map_details,votes_map_meps,users_map_details,users_map_votes,arr_distinct_values=get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    ##############################################################################################
    
    
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    configuration['stats']=original_mepsStatistics
    
    
    enumerator=generic_enumerator_multiattributes_dfs(arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None,stats=original_mepsStatistics)
    index,index_frequent,index_valid,index_non_valid,index_good=0,0,0,0,0
    
    
    for p,bitwise_p,stats in enumerator: 
        index+=1
        
        subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
        subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
        
        
        for attr_ind,p_attr in enumerate(p):
            if attributes[attr_ind]['type']=='themes':
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
            else:
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
        
        
        #################################COMPUTE SUBGROUP et CHECK IF IT IS A FREQUENT PATTERN##########################"
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise_p) 
        configuration['bitwise']=bitwise
        
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        nb_dossiers=len(set([v['DOSSIERID'] for v in filteredDataset_votes]))
        
        if nb_dossiers<nb_dossiers_min :
            configuration['skip_list']=[p] 
            continue
        
        
        
        
        users_map_details_array_filtered=filter_pipeline_obj(users_map_details_array, subgroup_pipeline_for_meps)[0]
        users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
        filteredDataset_meps_votes={}
        for key in users_ids:
            value=users_map_votes[key]
            votes_participated=(value & v_ids)
            if len(votes_participated)>0:
                filteredDataset_meps_votes[key]=votes_participated
        
        
        
        users_ids_set=set(filteredDataset_meps_votes.keys())
        nb_users_voted=len(filteredDataset_meps_votes)
        
        
        
        #votes_map_meps_filtered={key:value & users_ids_set for key,value in votes_map_meps.iteritems() if key in v_ids}

        #nb_votants_minimal = min([len(x) for x in votes_map_meps_filtered.values()])
        
        avg_votes_by_users = float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(nb_users_voted)
        
        if avg_votes_by_users<avg_users_votes_min : #avg_votes_by_users it's not LOGIC because patterns with restricted list of meps can have an average who is greater than the minimum threshold
            #if (avg_votes_by_users*(float(nb_users_voted)/float(nb_votants_minimal)))<avg_users_votes_min:
            configuration['skip_list']=[p] 
            #print nb_votants_minimal,nb_users_voted
            continue
        
        index_frequent+=1
        
        ##########################################################################################
        
        
        ######################################COVER COMPUTING######################################
        
        max_cover,b_max_cover,pattern_max,bitarray_bitwise,bitarray_bitwise_count=cover_max_computation(p, subpattern_users, bitwise, patterns_visited, subpatterns_users_visited, bitwises_visited, cover_threshold)
        
        if (max_cover>=cover_threshold):
            if (pruning and b_max_cover<quality_threshold):
                configuration['skip_list']=[p] 
            continue
        
        #########################################################################################################

        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set)
        configuration['stats']=returned_mepsStatistics
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        
        quality,borne_max_quality=compute_quality_and_upper_bound(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant)
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        
        patterns_visited_append(p)
        subpatterns_votes_visited_append(subpattern_vote)
        subpatterns_users_visited_append(subpattern_users)
        bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
        
        index_non_valid+=1
        
        
        if (pruning and borne_max_quality<quality_threshold):
            configuration['skip_list']=[p] 
            continue

      
        index_valid+=1
        
        label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],arr_labels[i]) for i in range(len(p))]
        print p,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',quality,'\t',borne_max_quality,'\t',quality>=quality_threshold,'\t',index,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid,'\t',index_good
            
        if (quality>=quality_threshold):
            dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
            index_good+=1
            #dossiers_voted=set([(v['PROCEDURE_TITLE'],sum([1 for x in filteredDataset_votes if x['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])) for v in filteredDataset_votes])
            yield p,label,dataset_stats,quality,borne_max_quality
            

def generic_enumerators_dataset_stats_two_cases_top_k(dataset,attributes,configuration,votes_attributes,users_attributes,position_attribute): #disagreement
    
    
    #TODO : ENUMERATOR DIFFERENCIATE BETWEEN USER1 AND USER2 (don't do the half matrix everywhere !) 
    start=0
    quad_error=[]
    nb_quality_measured=0
    interesting_patterns=[]
    top_k=configuration.get('top_k',float('inf'))
    if top_k is None : 
        top_k=float('inf')
    quality_threshold=float(configuration.get('quality_threshold',0))
    if quality_threshold is None : 
        quality_threshold=0
    
    
        
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    disagreement=(iwant=='disagreement')
    nb_dossiers_min=configuration['nb_dossiers_min']
    avg_users_votes_min=configuration['avg_users_votes_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    
    configuration['skip_list']=[]
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    ############################STATS for * ######################################
    
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_new(dataset,votes_attributes,users_attributes,position_attribute)
    original_mepwise_similarities={}
    
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            #if user2<user1:
                original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2)
    
    ##############################################################################
    
    patterns_visited,subpatterns_votes_visited,subpatterns_users_visited,bitwises_visited=[],[],[],[]
    patterns_visited_append,subpatterns_votes_visited_append,subpatterns_users_visited_append,bitwises_visited_append=patterns_visited.append,subpatterns_votes_visited.append,subpatterns_users_visited.append,bitwises_visited.append

    ############################### GET DISTINCT VALUES ####################################
    votes_map_details,votes_map_meps,users_map_details,users_map_votes,arr_distinct_values=get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    ##############################################################################################
    
    
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    configuration['stats']=original_mepsStatistics
    
    
    enumerator=generic_enumerator_multiattributes_dfs(arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None,stats=original_mepsStatistics)
    index,index_frequent,index_valid,index_non_valid,index_good=0,0,0,0,0
    
    
    for p,bitwise_p,stats in enumerator: 
        index+=1
        
        subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
        subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
        
        
        for attr_ind,p_attr in enumerate(p):
#             if attributes[attr_ind]['type']=='themes':
#                 subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
#             else:
            subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
        
        
        #################################COMPUTE SUBGROUP et CHECK IF IT IS A FREQUENT PATTERN##########################"
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise_p) 
        configuration['bitwise']=bitwise
       
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        nb_dossiers=len(set([v['DOSSIERID'] for v in filteredDataset_votes]))
        
        if nb_dossiers<nb_dossiers_min :
            configuration['skip_list']=[p] 
            continue
        
        
        
        
        users_map_details_array_filtered=filter_pipeline_obj(users_map_details_array, subgroup_pipeline_for_meps)[0]
        users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
        nb_users_all=len(users_ids)
        filteredDataset_meps_votes={}
        for key in users_ids:
            value=users_map_votes[key]
            votes_participated=(value & v_ids)
            if len(votes_participated)>0:
                filteredDataset_meps_votes[key]=votes_participated
        
        
        users_ids_set=set(filteredDataset_meps_votes.keys())
        nb_users_voted=len(filteredDataset_meps_votes)
        
        
        
        #votes_map_meps_filtered={key:value & users_ids_set for key,value in votes_map_meps.iteritems() if key in v_ids}
        #nb_votants_minimal = min([len(x) for x in votes_map_meps_filtered.values()])
        
        avg_votes_by_users = float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(nb_users_all)
        #try:
        max_votes_pairwise=max(len(value) for key,value in filteredDataset_meps_votes.iteritems())
#         except :
#             continue
        if max_votes_pairwise<avg_users_votes_min : #avg_votes_by_users it's not LOGIC because patterns with restricted list of meps can have an average who is greater than the minimum threshold
            #if (avg_votes_by_users*(float(nb_users_voted)/float(nb_votants_minimal)))<avg_users_votes_min:
            configuration['skip_list']=[p] 
            
            continue
        
        index_frequent+=1
        
        ##########################################################################################
        
        
        ######################################COVER COMPUTING######################################
        
        max_cover,b_max_cover,pattern_max,bitarray_bitwise,bitarray_bitwise_count=cover_max_computation(p, subpattern_users, bitwise, patterns_visited, subpatterns_users_visited, bitwises_visited, cover_threshold)
        
        if (max_cover>=cover_threshold):
            if (pruning and b_max_cover<quality_threshold):
                configuration['skip_list']=[p] 
            continue
        
        #########################################################################################################

        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set)
        configuration['stats']=returned_mepsStatistics
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        quality,borne_max_quality=compute_quality_and_upper_bound(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant)
        quad_error.append(math.copysign((borne_max_quality-quality), 1))
        nb_quality_measured+=1
        #compute_quality_and_upper_bound(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant)
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        
#         patterns_visited_append(p)
#         subpatterns_votes_visited_append(subpattern_vote)
#         subpatterns_users_visited_append(subpattern_users)
#         bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
        
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
    
    print 'ERROR BETWEEN UPPER BOUND AND QUALITY MEASURE', float(sum(quad_error))/nb_quality_measured#quad_error[nb_quality_measured/2]




    
def generic_enumerators_dataset_stats_two_cases_top_k_NEW(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute): #disagreement
    
    
    #TODO : ENUMERATOR DIFFERENCIATE BETWEEN USER1 AND USER2 (don't do the half matrix everywhere !) 
    start=0
    quad_error=[]
    nb_quality_measured=0
    interesting_patterns=[]
    top_k=configuration.get('top_k',float('inf'))
    if top_k is None : 
        top_k=float('inf')
    quality_threshold=float(configuration.get('quality_threshold',0))
    if quality_threshold is None:
        quality_threshold=0
    
    if quality_threshold is None : 
        quality_threshold=0
    
    
        
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    disagreement=(iwant=='disagreement')
    nb_dossiers_min=configuration['nb_dossiers_min']
    #avg_users_votes_min=configuration['avg_users_votes_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    
    configuration['skip_list']=[]
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    ############################STATS for * ######################################
    
    
    
    
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_new(dataset,votes_attributes,users_attributes,position_attribute)
    
    
    
    
    
    original_mepwise_similarities={}
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            #if user2<user1:
                original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2)
#                 if (user1==user2):
#                     original_mepwise_similarities[user1][user2]=
                
    ##############################################################################
    
    patterns_visited,subpatterns_votes_visited,subpatterns_users_visited,bitwises_visited,dossiers_ids_visited=[],[],[],[],[]
    patterns_visited_append,subpatterns_votes_visited_append,subpatterns_users_visited_append,bitwises_visited_append,dossiers_ids_visited_append=patterns_visited.append,subpatterns_votes_visited.append,subpatterns_users_visited.append,bitwises_visited.append,dossiers_ids_visited.append

    ############################### GET DISTINCT VALUES ####################################
    votes_map_details,votes_map_meps,users_map_details,users_map_votes,users_map_votes_agreement_index,arr_distinct_values=get_distinct_values(dataset,attributes,votes_attributes,users_attributes,position_attribute)
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    ##############################################################################################
    
    #####################AGREEMENT_INDEX######################"
     
    users_avg_agreement_index={u:sum([x[1] for x in votes_ai])/float(len(votes_ai)) for u,votes_ai in users_map_votes_agreement_index.iteritems() if users_map_details[u]['MAJORITY']}
      
    for u in users_avg_agreement_index:
        nb_votes_u=float(len(users_map_votes_agreement_index[u]))
        original_mepwise_similarities[u][u]=(users_avg_agreement_index[u]*nb_votes_u,nb_votes_u)
      

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
#             if attributes[attr_ind]['type']=='themes':
#                 subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
#             else:
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
        
        nb_users_all=len(users_ids)
        filteredDataset_meps_votes={}
        for key in users_ids:
            value=users_map_votes[key]
            votes_participated=(value & v_ids)
            if len(votes_participated)>0:
                filteredDataset_meps_votes[key]=votes_participated
        
        
        users_ids_set=set(filteredDataset_meps_votes.keys())
        #nb_users_voted=len(filteredDataset_meps_votes)
        
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set
        
        nb_users_voted=len(users1_ids)+len(users2_ids)
        
        #votes_map_meps_filtered={key:value & users_ids_set for key,value in votes_map_meps.iteritems() if key in v_ids}
        #nb_votants_minimal = min([len(x) for x in votes_map_meps_filtered.values()])
        
        avg_votes_by_users = float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(nb_users_all)
        #try:
        max_votes_pairwise=max(len(value) for key,value in filteredDataset_meps_votes.iteritems())
#         except :
#             continue
        if max_votes_pairwise<threshold_pair_comparaison : #avg_votes_by_users it's not LOGIC because patterns with restricted list of meps can have an average who is greater than the minimum threshold
            #if (avg_votes_by_users*(float(nb_users_voted)/float(nb_votants_minimal)))<avg_users_votes_min:
            configuration['skip_list']=[p] 
            
            continue
        
        index_frequent+=1
        
        ##########################################################################################
        
        
        ######################################COVER COMPUTING######################################
        
        max_cover,b_max_cover,pattern_max,bitarray_bitwise,bitarray_bitwise_count=cover_max_computation(p, subpattern_users, bitwise, patterns_visited, subpatterns_users_visited, bitwises_visited, cover_threshold)
        
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

        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        configuration['stats']=returned_mepsStatistics
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        #########################AGREEMENT INDEX###########################
        users_map_votes_agreement_index_pattern={}
        for u in returned_mepsMeta:
            if returned_mepsMeta[u]['MAJORITY']:
                users_map_votes_agreement_index_pattern[u]=[(v,agr) for v,agr in users_map_votes_agreement_index[u] if v in v_ids]
          
          
        users_avg_agreement_index_pattern={u:sum([x[1] for x in votes_ai])/float(len(votes_ai)) for u,votes_ai in users_map_votes_agreement_index_pattern.iteritems()}
        for u in users_avg_agreement_index_pattern:
            if returned_mepsStatsNumbers.has_key(u):
                if returned_mepsStatsNumbers[u].has_key(u):
                    returned_mepsStatsNumbers[u][u]['YY']=users_avg_agreement_index_pattern[u]*returned_mepsStatsNumbers[u][u]['NB_VOTES']
                    returned_mepsStatsNumbers[u][u]['NN']=0.
                    returned_mepsStatsNumbers[u][u]['AA']=0.
        #########################AGREEMENT INDEX###########################
        
        
        
        quality,borne_max_quality=compute_quality_and_upper_bound(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant)
        quad_error.append(math.copysign((borne_max_quality-quality), 1))
        nb_quality_measured+=1
        #compute_quality_and_upper_bound(original_mepwise_similarities, returned_mepsStatsNumbers, nb_users_voted, threshold_pair_comparaison, iwant)
        
        ######################################UPPER BOUND EXPECTED COMPUTING######################################
        
        
#         patterns_visited_append(p)
#         subpatterns_votes_visited_append(subpattern_vote)
#         subpatterns_users_visited_append(subpattern_users)
#         bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
        
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
    
    print 'ERROR BETWEEN UPPER BOUND AND QUALITY MEASURE', float(sum(quad_error))/nb_quality_measured#quad_error[nb_quality_measured/2]


def generic_enumerators_dataset_stats_two_cases_separated(dataset,attributes,configuration,votes_attributes,users_attributes,position_attribute): #disagreement
    
    
    ####
    # start by getting distinct values #
    ####
    
    #TODO : ENUMERATOR DIFFERENCIATE BETWEEN USER1 AND USER2 (don't do the half matrix everywhere !) 
    
    
    disagreement=(configuration['iwant']=='disagreement')
    start=0
    ##########STATS * ###################"
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractStatistics_fromdataset_new(dataset,votes_attributes,users_attributes,position_attribute)
    original_mepwise_similarities={}
    
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            if user2<user1:
                original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatsNumbers,user1,user2)
    
    #print 'nb item : ', len(dataset)
    ######################################
    
    nb_dossiers_min=configuration['nb_dossiers_min']
    avg_users_votes_min=configuration['avg_users_votes_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    quality_threshold=float(configuration['quality_threshold'])
    
    configuration['skip_list']=[]
    nb_attributes=len(attributes)
    range_nb_attributes=range(nb_attributes)
    arr_distinct_values=[SortedSet() for i in range_nb_attributes]
    
    votes_map_details={}
    votes_map_meps={}
    votes_map_details_has_key=votes_map_details.has_key
    votes_map_details_array=[]
    votes_map_meps_has_key=votes_map_meps.has_key
    
    vote_id_attributes=votes_attributes[0]
    
    users_map_votes={}
    users_map_votes_has_key=users_map_votes.has_key
    users_map_details={}
    users_map_details_has_key=users_map_details.has_key
    
    users_id_attributes=users_attributes[0]
    
    #sortedDataset=SortedListWithKey([{'a': 2, 'b': 0}, {'a': 1, 'b': 1}, {'a': 0, 'b': 2}],lambda x : x['VOTEID'])
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    
    patterns_visited=[]
    subpatterns_votes_visited=[]
    subpatterns_users_visited=[]
    bitwises_visited=[]
    patterns_visited_append=patterns_visited.append
    subpatterns_votes_visited_append=subpatterns_votes_visited.append
    subpatterns_users_visited_append=subpatterns_users_visited.append
    bitwises_visited_append=bitwises_visited.append
    
    
    for d in dataset:
        for i,attr in enumerate(attributes):
            
            obj_attr_value=d[attr['name']]
            values=set()
            if hasattr(obj_attr_value, '__iter__'):
                values={v for v in obj_attr_value}
            else :
                values={obj_attr_value}
            arr_distinct_values[i] |= values
        
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=[]
        votes_map_meps[d_vote_id].append(d)
        
    nb_votes_origin=len(votes_map_meps.keys())
    nb_meps_origin=len(users_map_details.keys())
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    ############
    arr_distinct_values_votes_pattern=[x for i,x in enumerate(arr_distinct_values) if attributes[i]['name'] in votes_attributes]
    arr_distinct_values_users_pattern=[x for i,x in enumerate(arr_distinct_values) if attributes[i]['name'] in users_attributes]
    attributes_votes_pattern=[attr for attr in attributes if attr['name'] in votes_attributes]
    attributes_users_pattern=[attr for attr in attributes if attr['name'] in users_attributes]
    ##############
    
    arr_data_votes,arr_types_votes,arr_depthmax_votes,arr_refinement_indexes_votes,arr_labels_votes,subgroup_pipeline_votes,filter_operations,subgroup_pipeline_for_votesx,subgroup_pipeline_for_mepsx = get_arrdata_from_dataset_values(arr_distinct_values_votes_pattern, attributes_votes_pattern,votes_attributes,users_attributes,position_attribute)
    configuration['stats']=original_mepsStatistics
    
    
    arr_data_users,arr_types_users,arr_depthmax_users,arr_refinement_indexes_users,arr_labels_users,subgroup_pipeline_users,filter_operations_users,subgroup_pipeline_for_xxx,subgroup_pipeline_for_yyy = get_arrdata_from_dataset_values(arr_distinct_values_users_pattern, attributes_users_pattern,votes_attributes,users_attributes,position_attribute)
    
    
    
    
    
    enumeratorUsers=generic_enumerators_rec_subgroupBitwise_subgroups_stats(arr_data_users,arr_types_users,arr_refinement_indexes_users,arr_depthmax_users,{'bitwise':None,'skip_list':[]},bitwise=None)
    
    for p_user,bitwise_user in enumeratorUsers:
        print p_user
        
        for attr_users_ind,p_user_attr in enumerate(p_user):
            if attributes_users_pattern[attr_users_ind]['type']=='themes':
                subgroup_pipeline_users[attr_users_ind][filter_operations_users[attr_users_ind]]=[''.join([val,'%']) for val in p_user_attr]
            else:
                subgroup_pipeline_users[attr_users_ind][filter_operations_users[attr_users_ind]]=p_user_attr
            
        users_map_details_array_actual,bitwise_users_actual = filter_pipeline_obj(users_map_details_array, subgroup_pipeline_users)
        
        users_id_actual=set([x[users_id_attributes] for x in users_map_details_array_actual])
        #print users_id_actual
        dataset_actual=[x for x in dataset if x[users_id_attributes] in users_id_actual]
            
        
        actual_mepsStatistics,actual_mepsStatsNumbers,actual_mepsMeta = extractStatistics_fromdataset_new(dataset_actual,votes_attributes,users_attributes,position_attribute)
        
        arr_data_votes,arr_types_votes,arr_depthmax_votes,arr_refinement_indexes_votes,arr_labels_votes,subgroup_pipeline_votes,filter_operations,subgroup_pipeline_for_votesx,subgroup_pipeline_for_mepsx = get_arrdata_from_dataset_values(arr_distinct_values_votes_pattern, attributes_votes_pattern,votes_attributes,users_attributes,position_attribute)
        
        configuration['stats']=actual_mepsStatistics
        
        
        
        enumerator=generic_enumerator_multiattributes_dfs(arr_data_votes,arr_types_votes,arr_refinement_indexes_votes,arr_depthmax_votes,configuration,bitwise=None,stats=actual_mepsStatistics)
        
        
        index=0
        index_frequent=0
        index_valid=0
        index_non_valid=0
        index_pattern_to_ret=0
        
        
        for p,bitwise_p,stats in enumerator:
            index+=1
            
            
            for attr_ind,p_attr in enumerate(p):
                if attributes_votes_pattern[attr_ind]['type']=='themes':
                    subgroup_pipeline_votes[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
                else:
                    subgroup_pipeline_votes[attr_ind][filter_operations[attr_ind]]=p_attr
             
            timeEval=time()
            filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_votes, bitwise_p) 
            start+=(time()-timeEval)   
            configuration['bitwise']=bitwise
            
            v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
            nb_dossiers=len(set([v['DOSSIERID'] for v in filteredDataset_votes]))
            
            if nb_dossiers<nb_dossiers_min :
                configuration['skip_list']=[p] 
                continue
            
            users_map_details_array_filtered=users_map_details_array#filter_pipeline_obj(users_map_details_array, [])[0]
            #users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
            filteredDataset_meps_votes={}
            for key in users_id_actual:
                value=users_map_votes[key]
                votes_participated=(value & v_ids)
                if len(votes_participated)>0:
                    filteredDataset_meps_votes[key]=value
            
            
            users_ids_set=set(filteredDataset_meps_votes.keys())
            nb_users_voted=len(filteredDataset_meps_votes)
            
            avg_votes_by_users= float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(nb_users_voted)
            
            if avg_votes_by_users<avg_users_votes_min : #avg_votes_by_users it's not LOGIC because patterns with restricted list of meps can have an average who is greater than the minimum threshold
                configuration['skip_list']=[p] 
                continue
            
            index_frequent+=1
            
            
            bitarray_bitwise=bitarray(bitwise)
            bitarray_bitwise_count=bitarray_bitwise.count()
            subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
            subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
            max_cover=0
            b_max_cover=0
            pattern_max_cover=[]
            
            for (b,count_obj,b_max),p_users_visited,p_visited in zip(bitwises_visited,subpatterns_users_visited,patterns_visited):
                if (bitarray_bitwise_count<=count_obj) and (p_users_visited==p_user):  
                    act_cover=(float((bitarray_bitwise & b).count()) / count_obj)
                    if (act_cover>max_cover):
                        b_max_cover=b_max
                        pattern_max_cover=p_visited
                    max_cover=max(max_cover,act_cover)
                    
                    if max_cover>=cover_threshold:
                        break
    
    
    
            if (max_cover>=cover_threshold):
                if (b_max_cover<quality_threshold):
                    configuration['skip_list']=[p] 
                continue
            
            
            returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set)
            configuration['stats']=returned_mepsStatistics
            
            qps=[]
            qps_max=[]
            qps_append=qps.append
            qps_max_append=qps_max.append
            for user1 in returned_mepsStatsNumbers:
                for user2 in returned_mepsStatsNumbers[user1]:
                    if user2<user1:
                        agg_p,all_p=get_sim_vectors(returned_mepsStatsNumbers, user1, user2)
                        agg_o,all_o=original_mepwise_similarities[user1][user2]
                        
                        if all_p>=threshold_pair_comparaison:
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
                                
                            qps_append(qp**2)
                            qps_max_append(diff_p_max_expected**2)
                        
            
            quality=sqrt(sum(qps)*2)/float(nb_users_voted)
            borne_max_quality=sqrt(sum(qps_max)*2)/float(nb_users_voted)
            
            
            patterns_visited_append(p)
            subpatterns_votes_visited_append(subpattern_vote)
            subpatterns_users_visited_append(p_user)
            bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
            
            
    
            index_non_valid+=1
            
            if (borne_max_quality<quality_threshold):
                configuration['skip_list']=[p] 
                continue
    
          
            index_valid+=1
            label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types_votes[i]](p[i],arr_labels_votes[i]) for i in range(len(p))]
            label_user = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types_users[i]](p_user[i],arr_labels_users[i]) for i in range(len(p_user))]
            #print p,p_user
            pattern_to_yield=p[:]
            pattern_to_yield.extend(p_user)
            label.extend(label_user)
            print pattern_to_yield,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',quality,'\t',borne_max_quality,'\t',quality>=quality_threshold,'\t',index,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid,'\t',index_pattern_to_ret
            
            index_pattern_to_ret+=1 if quality>=quality_threshold else 0
            
            if (quality>=quality_threshold):
                dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                #dossiers_voted=set([(v['PROCEDURE_TITLE'],sum([1 for x in filteredDataset_votes if x['PROCEDURE_TITLE']==v['PROCEDURE_TITLE']])) for v in filteredDataset_votes])
                
                yield pattern_to_yield,label,dataset_stats,quality,borne_max_quality
            

    print start
    
                     
def generic_enumerators_dataset_stats_two_cases_new(dataset,attributes,configuration,votes_attributes,users_attributes,position_attribute): #disagreement
    
    
    ####
    # start by getting distinct values #
    ####
    
    disagreement=(configuration['iwant']=='disagreement')
    start=time()
    ##########STATS * ###################"
    original_mepsStatistics,original_mepsStatsNumbers,original_mepsMeta = extractVotesStatistics_fromdataset(dataset,votes_attributes,users_attributes,position_attribute)
    original_mepwise_similarities={}
    
    for user1 in original_mepsStatsNumbers:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatsNumbers[user1]:
            if user2<user1:
                original_mepwise_similarities[user1][user2]=(float(original_mepsStatsNumbers[user1][user2]['++']),float(original_mepsStatsNumbers[user1][user2]['NB_VOTES']))
    
    #print 'nb item : ', len(dataset)
    ######################################
    
    nb_dossiers_min=configuration['nb_dossiers_min']
    avg_users_votes_min=configuration['avg_users_votes_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    quality_threshold=float(configuration['quality_threshold'])
    
    configuration['skip_list']=[]
    nb_attributes=len(attributes)
    range_nb_attributes=range(nb_attributes)
    arr_distinct_values=[SortedSet() for i in range_nb_attributes]
    
    votes_map_details={}
    votes_map_meps={}
    votes_map_details_has_key=votes_map_details.has_key
    votes_map_details_array=[]
    votes_map_meps_has_key=votes_map_meps.has_key
    
    vote_id_attributes=votes_attributes[0]
    
    users_map_votes={}
    users_map_votes_has_key=users_map_votes.has_key
    users_map_details={}
    users_map_details_has_key=users_map_details.has_key
    
    users_id_attributes=users_attributes[0]
    
    #sortedDataset=SortedListWithKey([{'a': 2, 'b': 0}, {'a': 1, 'b': 1}, {'a': 0, 'b': 2}],lambda x : x['VOTEID'])
    
    subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    
    patterns_visited=[]
    subpatterns_votes_visited=[]
    subpatterns_users_visited=[]
    bitwises_visited=[]
    patterns_visited_append=patterns_visited.append
    subpatterns_votes_visited_append=subpatterns_votes_visited.append
    subpatterns_users_visited_append=subpatterns_users_visited.append
    bitwises_visited_append=bitwises_visited.append
    
    
    for d in dataset:
        for i,attr in enumerate(attributes):
            
            obj_attr_value=d[attr['name']]
            values=set()
            if hasattr(obj_attr_value, '__iter__'):
                values={v for v in obj_attr_value}
            else :
                values={obj_attr_value}
            arr_distinct_values[i] |= values
        
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=[]
        votes_map_meps[d_vote_id].append(d)
        
    nb_votes_origin=len(votes_map_meps.keys())
    nb_meps_origin=len(users_map_details.keys())
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    
    arr_data,arr_types,arr_depthmax,arr_refinement_indexes,arr_labels,subgroup_pipeline,filter_operations,subgroup_pipeline_for_votes,subgroup_pipeline_for_meps = get_arrdata_from_dataset_values(arr_distinct_values, attributes,votes_attributes,users_attributes,position_attribute)
    
    configuration['stats']=original_mepsStatistics
    enumerator=generic_enumerator_multiattributes_dfs(arr_data,arr_types,arr_refinement_indexes,arr_depthmax,configuration,bitwise=None,stats=original_mepsStatistics)
    
    #print 'time spent initializing the enumerator : ' , time()-start
    index=0
    index_frequent=0
    index_valid=0
    index_non_valid=0
    for p,bitwise,stats in enumerator:
        index+=1
        for attr_ind,p_attr in enumerate(p):
            if attributes[attr_ind]['type']=='themes':
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=[''.join([val,'%']) for val in p_attr]
            else:
                subgroup_pipeline[attr_ind][filter_operations[attr_ind]]=p_attr
            
        
        filteredDataset_votes,bitwise = filter_pipeline_obj(votes_map_details_array, subgroup_pipeline_for_votes, bitwise) 
        configuration['bitwise']=bitwise
        
        v_ids=set([obj[vote_id_attributes] for obj in filteredDataset_votes])
        nb_dossiers=len(set([v['DOSSIERID'] for v in filteredDataset_votes]))
        
        
        if nb_dossiers<nb_dossiers_min :
            configuration['skip_list']=[p] 
            continue
        
        users_map_details_array_filtered=filter_pipeline_obj(users_map_details_array, subgroup_pipeline_for_meps)[0]
        users_ids=set([obj[users_id_attributes] for obj in users_map_details_array_filtered])
        filteredDataset_meps_votes={key:(users_map_votes[key] & v_ids) for key in users_ids if len(users_map_votes[key] & v_ids)>0  }
        
        
        avg_votes_by_users= float(sum(len(value) for key,value in filteredDataset_meps_votes.iteritems()))/(len(users_ids))
        
        if avg_votes_by_users<avg_users_votes_min : #avg_votes_by_users it's not LOGIC because patterns with restricted list of meps can have an average who is greater than the minimum threshold
            configuration['skip_list']=[p] 
            continue
        
        index_frequent+=1
        bitarray_bitwise=bitarray(bitwise)
        bitarray_bitwise_count=bitarray_bitwise.count()
        subpattern_vote=[spat for spat,f in zip(p,subpattern_votes_filter) if f]
        subpattern_users=[spat for spat,f in zip(p,subpattern_users_filter) if f] 
        
        max_cover=0
        b_max_cover=0
        pattern_max_cover=[]
        for (b,count_obj,b_max),p_users_visited,p_visited in zip(bitwises_visited,subpatterns_users_visited,patterns_visited):
            if (bitarray_bitwise_count<=count_obj) and (p_users_visited==subpattern_users):  
                act_cover=(float((bitarray_bitwise & b).count()) / count_obj)
                if (act_cover>max_cover):
                    b_max_cover=b_max
                    pattern_max_cover=p_visited
                max_cover=max(max_cover,act_cover)
                
                if max_cover>=cover_threshold:
                    break
        
        if (max_cover>=cover_threshold):
            continue
        
         
         
         
        
        
        returned_mepsStatistics,returned_mepsStatsNumbers,returned_mepsMeta = extractVotesStatistics_fromdataset_update(stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids)
        configuration['stats']=returned_mepsStatistics
        
        qps=[]
        qps_max=[]
        qps_append=qps.append
        qps_max_append=qps_max.append
        for user1 in returned_mepsStatsNumbers:
            for user2 in returned_mepsStatsNumbers[user1]:
                if user2<user1:
                    agg_p,all_p=float(returned_mepsStatsNumbers[user1][user2]['++']),float(returned_mepsStatsNumbers[user1][user2]['NB_VOTES'])
                    agg_o,all_o=original_mepwise_similarities[user1][user2]
                    
                    if all_p>=threshold_pair_comparaison:
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
                            
                        qps_append(qp**2)
                        qps_max_append(diff_p_max_expected**2)
                    
        
        quality=sqrt(sum(qps)*2)/float(len(users_ids))
        borne_max_quality=sqrt(sum(qps_max)*2)/float(len(users_ids))
        
        
        patterns_visited_append(p)
        subpatterns_votes_visited_append(subpattern_vote)
        subpatterns_users_visited_append(subpattern_users)
        bitwises_visited_append((bitarray_bitwise,bitarray_bitwise_count,borne_max_quality))
        
        

        index_non_valid+=1
        
#         if 0<max_cover  and ((b_max_cover/max_cover)<quality_threshold):
#              
#             configuration['skip_list']=[p] 
#             continue
        
        if (borne_max_quality<quality_threshold):
            configuration['skip_list']=[p] 
            continue
        
        index_valid+=1
        label = [POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER[arr_types[i]](p[i],arr_labels[i]) for i in range(len(p))]
        print p,'\t',nb_dossiers,'\t',len(v_ids),'\t',max_cover,'\t',quality,'\t',borne_max_quality,'\t',quality>=quality_threshold,'\t',index,'\t',index_frequent,'\t',index_non_valid,'\t',index_valid
        
        if (quality>=quality_threshold):
            #print [x for x in possible_parents(p, arr_types, arr_data) if x in patterns_visited]
            dataset_stats=datasetStatistics(returned_mepsStatsNumbers, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
            yield p,label,dataset_stats,quality,borne_max_quality