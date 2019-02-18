from operator import is_not
from functools import partial


def get_domain_from_dataset_simple(distinct_values):
    return sorted(distinct_values),{}

def get_starting_pattern_simple(domain):
    starting_pattern=domain[:]
    starting_refinement=0
    default_widthmax=0
    return starting_pattern,starting_refinement,default_widthmax


def value_to_yield_simple(domain,pattern,refinement_index,widthmax):
#     returned=filter(partial(is_not, None), pattern)    
#     return returned if len(returned) else None
    #if len(pattern)>1: return None
    return pattern[:]

# def children_simple(domain,pattern,refinement_index,widthmax=0):
#     if (len(pattern)-pattern.count(None))>1:
#         for i in range(refinement_index,len(domain)):
#             if pattern[i] is None:
#                 continue
#             possible_child=[None]*i+[pattern[i]]+[None]*(len(domain)-(i+1))
#             yield possible_child,len(domain)
            
def children_simple(domain,pattern,refinement_index,widthmax=0):
    if len(pattern)>1:
        for i in range(refinement_index,len(pattern)):
            possible_child=[pattern[i]]
            yield possible_child,len(domain)
        
def enumerator_simple(domain,pattern,refinement_index,widthmax=0):
    yielded_pattern=value_to_yield_simple(domain,pattern,refinement_index,widthmax)
    if yielded_pattern is not None:
        yield yielded_pattern
    for child,refin_child in children_simple(domain,pattern,refinement_index,widthmax):
        for child_pattern in enumerator_simple(domain,child,refin_child,widthmax):
            yield child_pattern
            

def pattern_cover_object_simple(domain,pattern,refinement_index,record,attribute):
    return record[attribute] in pattern

def pattern_cover_object_simple_index(pattern,record,attribute):
    return record[attribute] in pattern

def object_value_for_index_simple(domain,record,attribute):
    return record[attribute]  

def infimum_simple(domain,p1,p2):
    return sorted(set(p1)|set(p2))


def closed_simple(domain,list_patterns):
    list_set_patterns = [{item} for item in list_patterns]
    clos=reduce(set.union,list_set_patterns)
    res=domain[:]
    for k in range(len(res)):
        if res[k] not in clos:
            res[k]=None
    return res


def closed_simple_index(domain,datasetIndices,list_patterns,attr):
    attr_name=attr['name']
    list_patterns=[x[attr_name] for x in list_patterns]
    list_set_patterns = set(list_patterns)
    
    return sorted(list_set_patterns)


def respect_order_simple(p1,p2,refinement_index):
    #return False if any(p1[i]<>p2[i] for i in range(0,refinement_index)) else True
    return True

def closure_continueFrom_simple(domain,pattern,closed,refinement_index): #what is the pattern which represent the one that we need to continue from after closing (it's none if the lexicographic order is not respected)
    return closed[:]

def equality_simple(p1,p2):
    if (len(p1)>1 and len(p2)>1) or (len(p1)==1 and len(p2)==1):
        return True
    return False
    
def index_correspondant_to_simple(attr,indexall):
    attr_name=attr['name']
    index_attr={key:set() for key in attr['domain']}
    for i in range(len(indexall)):
        index_attr[indexall[i][attr_name]]|={i}
        
    attr['index_attr']=index_attr    
    
    
def compute_full_support_simple(set_indices_prec,attr,closed=True):
    #print attr['pattern'],'aha'
    attr_pattern=attr['pattern']
    if len(attr_pattern)>1:
        return set_indices_prec
    else:
        return set_indices_prec&attr['index_attr'][attr_pattern[0]]
    #return set_indices_prec&reduce(set.union,[attr['index_attr'][p] for p in attr['pattern']]) 