'''
Created on 24 mai 2017

@author: Adnene
'''
from ENUMERATORS_ATTRIBUTES.enumerator_attribute_nominal import enumerator_nominal_bottom_up, \
    enumerator_nominal_bottom_up_bfs


def encode(arr_pos,len_map_keys):
    to_shift_in_last=len_map_keys-arr_pos[-1]
    for i in range(1,len(arr_pos))[::-1]:
        arr_pos[i]-=arr_pos[i-1]
    ret=int(1)
    for i in arr_pos:
        ret=(ret<<i)|1
    return ret<<to_shift_in_last


def partition(dataset,attr_list):
    mappi={}
    key_list=[]
    len_dataset=len(dataset)
    for i in range(len_dataset):
        o = tuple((dataset[i][attr] for attr in attr_list))
        if o not in mappi:
            key_list.append(o)
            mappi[o]=[]
        mappi[o].append(i)
    return {encode(mappi[k],len_dataset) for k in key_list}

def compute_partitions(dataset):
    partitions={tuple(k):partition(dataset,k) for k in enumerator_nominal_bottom_up(sorted(dataset[0].keys()),[],0)}
    return partitions

def verify_df_new(partitions,attr_list_1,attr_list_2):
        part_1=partitions[tuple(attr_list_1)]
        part_2=partitions[tuple(attr_list_2)]

        for s_1 in part_1:
            if not any(s_1&s_2==s_1 for s_2 in part_2):
                return False

        return True
    
    
def find_dfs(dataset,attributes=None):
    
    partitions=compute_partitions(dataset)
    attributes=attributes if attributes is not None else sorted(dataset[0].keys())
    
    
    for k1,conf1 in enumerator_nominal_bottom_up_bfs(attributes) :
        for k2,conf2 in enumerator_nominal_bottom_up_bfs([y for y in attributes if y not in k1]):
            if k2==[]:continue
            if verify_df_new(partitions,k1,k2):
                print k1,'->',k2
                raw_input('...')
                
def find_dfs_fixed_right(dataset,attributes=None,fixed_right=[]):
    
    partitions=compute_partitions(dataset)
    if attributes is None:
        #attributes=sorted(dataset[0].keys())
        attributes=[y[0] for y in sorted([[k,len(partitions[tuple([k])])] for k in dataset[0].keys()],key=lambda x : x[1],reverse=True)]
        print attributes
        
    for k1,conf1 in enumerator_nominal_bottom_up_bfs(attributes) :
        k2=fixed_right
        if not (set(k2) <= set(k1)):
            if verify_df_new(partitions,k1,k2):
                print k1,'->',k2
                conf1['flag']=False
                raw_input('...')
        else :
            conf1['flag']=False    
            


def find_dfs_new(dataset,attributes=None):
    
    partitions=compute_partitions(dataset)
    if attributes is None:
        #attributes=sorted(dataset[0].keys())
        attributes=[y[0] for y in sorted([[k,len(partitions[tuple([k])])] for k in dataset[0].keys()],key=lambda x : x[1],reverse=True)]
        print attributes
    
    for k2,conf2 in enumerator_nominal_bottom_up_bfs(attributes) : 
            
        for k1,conf1 in enumerator_nominal_bottom_up_bfs([z for z in attributes if z not in k2]) :
            if verify_df_new(partitions,k1,k2):
                print k1,'->',k2
                conf1['flag']=False
                raw_input('...')    

