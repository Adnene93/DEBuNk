'''
Created on 20 dec. 2016

@author: Adnene
'''
import itertools


# def children_num(arr_sorted,refinement_index=0,minimal_size=None):
#     if len(arr_sorted)>1:
#         arr_left=arr_sorted[1:]
#         arr_right=arr_sorted[:-1]
#         possible_children=[[arr_left,arr_right],[0,1]]
#         
#         for k in range(refinement_index,2):
#             if possible_children[0][k][-1]-possible_children[0][k][0]>=minimal_size:
#                 yield possible_children[0][k],possible_children[1][k]


def description_minimal_numeric(arr_p):
    arr_data=sorted(set(arr_p))
    pattern=[arr_data[0],arr_data[-1]]
    
    return pattern,arr_data,None #pattern,arr_data,refin_index

def children_num(arr_sorted,refinement_index=0,minimal_size=None):
    if len(arr_sorted)>1:
        arr_left=arr_sorted[1:]
        arr_right=arr_sorted[:-1]
        possible_children=[[arr_left,arr_right],[0,1]]
        
        for k in range(refinement_index,2):
            if possible_children[0][k][-1]-possible_children[0][k][0]>=minimal_size:
                yield possible_children[0][k],possible_children[1][k]
        
                
def value_to_yield_num(arr_sorted,opt=['']):
    returned=None
    if (len(arr_sorted)>=1):
        returned=[arr_sorted[0],arr_sorted[-1]]
    
    return returned

def possible_parents_numeric(actual_arr,original_arr):
    min_actual_arr=min(actual_arr)
    max_actual_arr=max(actual_arr)
    min_index=original_arr.index(min_actual_arr)
    max_index=original_arr.index(max_actual_arr)
    
    toRet=[]
    if (min_index>0):
        toRet.append([original_arr[min_index-1],max_actual_arr])
    if (max_index<len(original_arr)-1):
        toRet.append([min_actual_arr,original_arr[max_index+1]])
    toRet.append(actual_arr[:])
    return toRet

                        
def description_from_pattern_num(pattern,labelmap={}):
    
    return [labelmap.get(key,key) for key in pattern]
    

    
def enum_num_minimal_size_new_rec(arr_sorted,configuration,minimal_size=None,refinement_index=0):
    returned=value_to_yield_num(arr_sorted)
    if returned not in configuration['skip_list'] and (minimal_size is None or ((returned[1]-returned[0])>=minimal_size)):
        yield returned
        if returned not in configuration['skip_list']:
            for arr_child,refin_child in children_num(arr_sorted,refinement_index,minimal_size):
                for p in enum_num_minimal_size_new_rec(arr_child,configuration,minimal_size,refin_child):
                    yield p
        
def enum_num_minimal_size(arr_numbers,configuration,minimal_size=None):
    arr_sorted=sorted(arr_numbers)
    refinement_index=0
    for p in enum_num_minimal_size_new_rec(arr_sorted,configuration,minimal_size,refinement_index):
        yield p