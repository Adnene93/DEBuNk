'''
Created on 11 janv. 2017

@author: Adnene
'''
def description_minimal_simple(arr_p):
    arr_data=sorted(set(arr_p))
    pattern=arr_data
    refin=len(pattern) if len(pattern)>1 else 0
    return pattern,arr_data,refin #pattern,arr_data,refin_index

def children_simple(arr_sorted,refinement_index=0,minimal_size=None):
    #print arr_sorted
    for i in range(refinement_index):
        possible_child=[arr_sorted[i]]
        yield possible_child,0
        
def possible_parents_simple(actual_arr,original_arr):
    return original_arr      

def value_to_yield_simple(arr,opt=['']):
    return [x for x in arr]

def description_from_pattern_simple(pattern,labelmap={}):
    return [labelmap.get(key,key) for key in pattern]

def respect_order_simple(p1,p2):
    #return sorted(p1)<=sorted(p2)
    return True