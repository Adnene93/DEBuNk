'''
Created on 22 dec. 2016

@author: Adnene
'''


from EMM_ENUMERATOR.enumerator_nominal import children_nominal, value_to_yield_nominal, \
    description_from_pattern_nominal, possible_parents_nominal
from EMM_ENUMERATOR.enumerator_numbers import children_num, value_to_yield_num, \
    description_from_pattern_num, possible_parents_numeric
from EMM_ENUMERATOR.enumerator_themes import all_childrens_set_opt_depthmax, value_to_yield_themes, \
    createTreeOutOfThemes, description_from_pattern_themes,\
    possible_parents_themes

from random import random
from Queue import Queue
import itertools

POSSIBLE_ENUMERATOR_CHILDREN={
    'numeric':children_num,
    'nominal':children_nominal,
    'themes':all_childrens_set_opt_depthmax
} 

POSSIBLE_ENUMERATOR_PARENTS={
    'numeric':possible_parents_numeric,
    'nominal':possible_parents_nominal,
    'themes':possible_parents_themes
} 

POSSIBLE_ENUMERATOR_YIELDER={
    'numeric':value_to_yield_num,
    'nominal':value_to_yield_nominal,
    'themes':value_to_yield_themes
}

POSSIBLE_ENUMERATOR_DESCRIPTION_YIELDER={
    'numeric':description_from_pattern_num,
    'nominal':description_from_pattern_nominal,
    'themes':description_from_pattern_themes
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
    