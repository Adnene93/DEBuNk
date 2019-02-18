'''
Created on 1 mars 2017

@author: Adnene
'''
from bisect import bisect
def get_domain_from_dataset_numeric(distinct_values):
    return sorted(distinct_values),{}

def get_starting_pattern_numeric(domain):
    starting_pattern=domain[:]
    starting_refinement=0
    default_widthmax=0
    return starting_pattern,starting_refinement,default_widthmax



def value_to_yield_numeric(domain,pattern,refinement_index=0,widthmax=0):
    returned=None
    if (len(pattern)>=1):
        returned=[pattern[0],pattern[-1]]
    return returned

def children_numeric(domain,pattern,refinement_index=0,widthmax=0):
    if len(pattern)>1:
        arr_left=pattern[1:]
        arr_right=pattern[:-1]
        possible_children=[[arr_left,arr_right],[0,1]]

        for k in range(refinement_index,2):
            if possible_children[0][k][-1]-possible_children[0][k][0]>=widthmax:
                yield possible_children[0][k],possible_children[1][k]



def enumerator_numeric(domain,pattern,refinement_index=0,widthmax=0):
    yielded_pattern=value_to_yield_numeric(domain,pattern,refinement_index,widthmax)
    if yielded_pattern is not None:
        yield yielded_pattern
    for child,refin_child in children_numeric(domain,pattern,refinement_index,widthmax):
        for child_pattern in enumerator_numeric(domain,child,refin_child,widthmax):
            yield child_pattern


def pattern_cover_object_numeric(domain,pattern,refinement_index,record,attribute):
    #x=record[attribute]
    return pattern[0] <= record[attribute] <= pattern[-1]

def pattern_cover_object_numeric_index(pattern,record,attribute):
    return pattern[0] <= record[attribute] <= pattern[-1]
    #return record[attribute] in pattern

def object_value_for_index_numeric(domain,record,attribute):
    return record[attribute]   

    

def infimum_numeric(domain,p1,p2):
    return sorted(set(p1)|set(p2))

def closed_numeric(domain,list_patterns):
    #print list_patterns
    list_set_patterns = [{item} for item in list_patterns]
    clos=sorted(reduce(set.union,list_set_patterns))
    res=domain[domain.index(clos[0]):domain.index(clos[-1])+1]
    return res



def closed_numeric_index(domain,datasetIndices,list_patterns,attr):
    attr_name=attr['name']
    #list_patterns=[x[attr_name] for x in list_patterns]
    clos_0=list_patterns[0][attr_name]
    clos_1=clos_0
    for v in list_patterns:
        k=v[attr_name]
        if k<clos_0 :clos_0 = k
        elif k>clos_1 : clos_1 = k
#     clos=sorted(set(list_patterns))
#     clos_0=clos[0]
#     clos_1=clos[-1]
    #print domain[bisect(domain,clos_0)-1:bisect(domain,clos_1)],set([x[attr_name] for x in list_patterns])
    
    return domain[bisect(domain,clos_0)-1:bisect(domain,clos_1)]

def respect_order_numeric(p1,p2,refinement_index):
    return False if refinement_index==1 and p1[0]<>p2[0] else True




def closure_continueFrom_numeric(domain,pattern,closed,refinement_index): #what is the pattern which represent the one that we need to continue from after closing (it's none if the lexicographic order is not respected)
    return closed


def equality_numeric(p1,p2):
    return p1==p2


def index_correspondant_to_numeric(attr,indexall):
    attr_name=attr['name']
    index_attr={key:set() for key in attr['domain']}
    for i in range(len(indexall)):
        index_attr[indexall[i][attr_name]]|={i}
        
    attr['index_attr']=index_attr
    
    
def compute_full_support_numeric(set_indices_prec,attr,closed=True):
    #print attr['pattern'],'aha'
    attr_parent=attr['parent']
    if closed:
        if attr_parent==attr['pattern']:
            return set_indices_prec
        
        to_remove=attr_parent[-1] if attr['refinement_index']==1 else attr_parent[0]
        return set_indices_prec-attr['index_attr'][to_remove]
    else:
        index_attr=attr['index_attr']
        return set_indices_prec&reduce(set.union,[index_attr[p] for p in attr['pattern']])
    
    
#     
#     ############NEW ELECTION############"
# #     if attr_parent==attr['pattern']:
# #         return set_indices_prec
#     ############NEW ELECTION############"
#     
#     
#     #print refin
#     #print attr['pattern']
#     
#     #print attr['domain']
#     
# #     if refin==1:
# #         last_prec=attr['pattern'][-1]+1 if attr['pattern'][-1]<>9 else attr['pattern'][-1]+2
# #     else :
# #         last_prec=attr['pattern'][0]-1 if attr['pattern'][0]<>11 else attr['pattern'][0]-2
# #     #print last_prec,attr['pattern'][0],attr['pattern'][-1]
# #     return set_indices_prec - attr['index_attr'][last_prec]
#     
#     #to_remove=set(attr['parent'])-set(attr['pattern'])
#     #return set_indices_prec-reduce(set.union,[index_attr[p] for p in to_remove])
#     
#     
#     
# #     to_remove=attr_parent[-1] if attr['refinement_index']==1 else attr_parent[0]
# #     return set_indices_prec-attr['index_attr'][to_remove]
#     
# #     index_attr=attr['index_attr']
# #     return set_indices_prec&reduce(set.union,[index_attr[p] for p in attr['pattern']])