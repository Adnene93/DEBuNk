'''
Created on 20 dec. 2016

@author: Adnene
'''
import itertools


def description_minimal_nominal(arr_p):
    arr_data=None
    pattern=sorted(set(arr_p))
    return pattern,arr_data,None #pattern,arr_data,refin_index

def children_nominal(arr_sorted,refinement_index=0,minimal_size=None):
    for i in range(refinement_index):
        possible_child=arr_sorted[:i]+[None]+arr_sorted[i+1:]
        lastIndexOfNone=len(possible_child) - 1 - possible_child[::-1].index(None)
        if (any(item is None for item in possible_child[lastIndexOfNone+1:]) or all(item is None for item in possible_child)) or (len(filter(lambda x : x is not None,possible_child))<minimal_size)  :
            continue
        yield possible_child,i
        
def value_to_yield_nominal(arr,opt=['']):
    returned=filter(lambda x : x is not None,arr)
    return returned

def possible_parents_nominal(actual_arr,original_arr):
    original_arr_filtered=[x if x not in actual_arr else None for x in original_arr]
    original_arr_filtered_index=[i for i in range(len(original_arr_filtered)) if original_arr_filtered[i] is not None]
    actual_arr_indexes_in_original_arr=[i for i in range(len(original_arr)) if original_arr[i] in actual_arr]
    
    toRet=[]
    for width in range(1,2):
        for comb in itertools.combinations(original_arr_filtered_index,width):
            values_choosen=list(comb)+actual_arr_indexes_in_original_arr
            element=[None]*len(original_arr)
            for k in values_choosen:
                element[k]=original_arr[k]
            element=value_to_yield_nominal(element)
            
            toRet.append(element) 
    
    toRet.append(actual_arr[:])
    return toRet


    
def description_from_pattern_nominal(pattern,labelmap={}):
    return [labelmap.get(key,key) for key in pattern]


def enum_nominal_minimal_size_new(arr,configuration,minimal_size=None,refinement_index=None):
    if refinement_index is None:
        refinement_index=len(arr)
    returned_arr=value_to_yield_nominal(arr)
    if returned_arr not in configuration['skip_list'] and (minimal_size is None or len(returned_arr)>=minimal_size) :
        yield returned_arr
        if returned_arr not in configuration['skip_list'] and (minimal_size is None or len(returned_arr)>minimal_size) : #because if len(returned_arr)==minimal_size then the children won't verify the constraint
            for arr_child,refin_child in children_nominal(arr,refinement_index,) :
                for p in enum_nominal_minimal_size_new(arr_child,configuration,minimal_size,refin_child):
                    yield p
            