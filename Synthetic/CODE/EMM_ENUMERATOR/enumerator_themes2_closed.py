'''
Created on 12 fevr. 2017

@author: Adnene
'''
import cProfile
from itertools import product, combinations
from math import trunc
import pstats
from random import uniform
from time import time


def flattenThemesTree2(themes):
    arrNew=[]
    for x in themes :
        s= x.split('.')
        
        for i in range(len(s)) :
            sub=''
            for j in range(i+1):
                sub+=s[j]+'.'
            sub=sub[:-1]
            if sub not in arrNew :
                arrNew.append(sub)
    arrNew.append('')
    arrNew.sort()
    return arrNew

def parent_tag(t):
    if len(t)==0:
        return None
    parent='.'.join(t.split('.')[:-1])
    return parent


def all_parents_tag(t): #PARENTS + SELF
    v=t.split('.')
    all_parents=set(['']) | set(['.'.join(v[0:i+1]) for i in range(len(v))])
    return all_parents#[:len(all_parents)-1]

def all_parents_tag_exclusive(t): #PARENTS + SELF
    if (t==''):
        return set()
    v=t.split('.')
    all_parents=set(['']) | set(['.'.join(v[0:i+1]) for i in range(len(v)-1)])
    return all_parents#[:len(all_parents)-1]

def tree_theme2(themes):
    flat=flattenThemesTree2(themes)
    ret_map={};
    for x in flat:
        parent_x=parent_tag(x)
        all_parents=all_parents_tag(x)
        ret_map[x]={'parent':parent_x,'children':[],'right_borthers':[],'all_parents':all_parents,'all_parents_exclusive':all_parents-{x}}
        if parent_x is not None:
            ret_map[parent_x]['children'].append(x)
        
    for x,y in ret_map.iteritems():
        if y['parent'] is not None:
            brothers=ret_map[y['parent']]['children']
            y['right_borthers']=brothers[brothers.index(x)+1:]
                
            #y['left_brothers']=brothers[:brothers.index(x)]
    return ret_map

def dfs_tags(tree,t):
    yield t
    for x in tree[t]['children']:
        for u in dfs_tags(tree,x):
            yield u
            
def descendants_tags(tree,t):
    iters_dfs=dfs_tags(tree,t)
    next(iters_dfs)
    return list(iters_dfs)
            
# def respect_order_themes2(p1,p2):
#     len_min=min(len(p1),len(p2))-1
#     range_len_min=range(len_min)
#     return all(p1[i]==p2[i] for i in range_len_min) and p1[len_min]<=p2[len_min]

# def respect_order_themes2(p1,p2):
#     range_len_min=range(min(len(p1),len(p2))-1)
#     len_min=min(len(p1),len(p2))-1
#     return all(p1[i]<=p2[i] for i in range_len_min) and p1[len_min]<=p2[len_min]
    
# def respect_order_themes2(p1,p2,ref):
#     
#     len_min=min(len(p1),len(p2))-1
#     range_len_min=range(len_min)
#     
#     range_len_min=range(ref)
#     len_min=ref
#     
#     if len(p1)==len(p2):
#         return all(p1[i]==p2[i] for i in range_len_min) and p1[len_min]<=p2[len_min]
#     else:
#         #ONE IS PARENT AND EVERYTHING IS EQUAL
# #         range_len_min=range(ref)
# #         len_min=ref
#         PARENT_FLAG=True
#         res=True
#         for i in range_len_min:
#             if not res:
#                 return res
#             if (p1[i]<>p2[i] and PARENT_FLAG):
#                 res &=isParent(p1[i],p2[i])
#                 PARENT_FLAG=False
#             else:
#                 res &=(p1[i]==p2[i])
#         if PARENT_FLAG:
#             res&=p1[len_min]<=p2[len_min] #Parent or really precedent
#             
#         else:
#             res&=(p1[len_min]==p2[len_min])
#         
#         return res
#         
#         #return all(p1[i]==p2[i] or isParent(p1[i],p2[i]) for i in range_len_min) and p1[len_min]<=p2[len_min]
#         
# 
#     #return all(x==y for x,y in zip(p1[:len_min],p2[:len_min])) and p1[len_min]<=p2[len_min]


# def respect_order_themes2(tree,p1,p2,ref):
#     if p1==p2:
#         return True
#     #len_min=min(len(p1),len(p2))
#     #range_len_min=range(ref,len_min)
#     range_len_min_comp=range(ref)
#     #len_min=ref
#     #PARENT_FLAG=True
#     res=True
# 
#     for i in range_len_min_comp:
#         res&=(p1[i]==p2[i])
#         if not res:
#             return res
#     if p1[ref]>p2[ref]:
#         return False
#     lcsingp1p2=[y if lcs2(tree,x,y)>=x else '' for x,y in product(p1,p2) ]
#     lcsingp1p2REMOVE=lcsingp1p2[:]
#     if '' in lcsingp1p2REMOVE:
#         lcsingp1p2REMOVE.remove('')
#     return bool(lcsingp1p2[0]<>'' and len(lcsingp1p2REMOVE)>=len(p1)) 
#     return False

# def respect_order_themes2(tree,p1,p2,ref):
#     if p1==p2:
#         return True
#     range_len_min_comp=range(ref)
#     res=True
# 
#     for i in range_len_min_comp:
#         res&=(p1[i]==p2[i])
#         if not res:
#             return res
#     if p1[ref]>p2[ref]:
#         return False
#     lcsingp1p2=[y if lcs2(tree,x,y)>=x else '' for x,y in product(p1,p2) ]
#      
#     lcsingp1p2REMOVE=lcsingp1p2[:]
#     if '' in lcsingp1p2REMOVE:
#         lcsingp1p2REMOVE.remove('')
# 
#     
#     return bool(len(lcsingp1p2REMOVE)>=len(p1))
#     #return bool(lcs2(tree,p1[0],p2[0])>=p1[0])
#     return False

def essai(pa,pb):
    j=0
    res=[]
    for i in range(len(pa)):
        actual=[]
        while pa[i]>pb[j]:
            if j>=len(pb):
                break
            j+=1

        if j>=len(pb):
                break
        while (pa[i]==pb[j] or isParent(pa[i],pb[j])):
            actual.append(j)
            j+=1
            if j>=len(pb):
                break
        res.append(actual[:])
        actual=[]
    ret=[x for e in res for x in e]
    ret2=[ret[i+1]-ret[i] for i in range(len(ret)-1)] if len(ret)>1 else [1]
    return all(e==1 for e in ret2)

def fdorfilsfd(s1,s2):
    s1_split=s1.split('.')
    s2_split=s2.split('.')
    len_min=min(len(s1_split),len(s2_split))
    s1_new='.'.join(s1_split[:len_min])
    s2_new='.'.join(s2_split[:len_min])
    lcsbetween=lcs2_OLD(s1_new,s2_new)
    lcsbetween_split=lcsbetween.split('.')
    lcsbetween_len=len(lcsbetween_split) if lcsbetween<>'' else 0
    #if lcsbetween=='' and len_min==1:
    #     return s1_new,s2_new,lcs2_OLD(s1_new,s2_new),True

    return (len_min-lcsbetween_len)==1

def fg(s1,s2):
    s1_split=s1.split('.')
    s2_split=s2.split('.')
    len_min=max(len(s1_split),len(s2_split))
    #s1_new='.'.join(s1_split[:len_min])
    #s2_new='.'.join(s2_split[:len_min])
    lcsbetween=lcs2_OLD(s1,s2)
    lcsbetween_split=lcsbetween.split('.')
    lcsbetween_len=len(lcsbetween_split) if lcsbetween<>'' else 0
    #if lcsbetween=='' and len_min==1:
    #     return s1_new,s2_new,lcs2_OLD(s1_new,s2_new),True

    return (len_min-lcsbetween_len)==1


def essai3(pa,pb):
    j=0
    res=[]
    for i in range(len(pa)):
        actual=[]
        while pa[i]>pb[j]:
            if j>=len(pb):
                break
            if i-1>=0:
                if not fg(pb[j],pa[i]) or fdorfilsfd(pa[i-1],pb[j]):
                    res[-1].append(j)
            j+=1

        if j>=len(pb):
                break
        while (pa[i]==pb[j] or isParent(pa[i],pb[j])):
            actual.append(j)
            j+=1
            if j>=len(pb):
                break
        res.append(actual[:])
        actual=[]
    ret=[x for e in res for x in e]

    ret2=[ret[i+1]-ret[i] for i in range(len(ret)-1)] if len(ret)>1 else [1]
    return all(e==1 for e in ret2)

def respect_order_themes2(p1,p2,ref):
    
    if p1==p2:
        return True

    range_len_min_comp=reversed(range(ref))
    res=True
    
    if (p1[ref]>p2[ref]):
        return False
    
    for i in range_len_min_comp:
        res&=(p1[i]==p2[i])
        if not res:
            return res
    

    return True


def lcs2_OLD(s1,s2):
    joiner='.'.join
    if s1==s2:
        return s1
    elif len(s1)==0 or len(s2)==0 or s1[0]<>s2[0]:
        return ''
    s1_split=s1.split('.')
    s2_split=s2.split('.')
    s1_len=len(s1_split);s2_len=len(s2_split);
    res=[];res_append=res.append
    for i in range(min(s1_len,s2_len)):
        if s1_split[i] <> s2_split[i]:
            break
        res_append(s1_split[i])
    if len(res)==0:
        toret=''
    else:
        toret=joiner(res)
    return toret
# 
# def infimum2(p1,p2):
#     toRet=set()
#     for x,y in product(p1,p2):
#         toRet|={lcs2(x,y)}
#     toRet_remove=toRet.remove
#     for x,y in combinations(toRet,2):
#         if x not in toRet or y not in toRet:
#             continue
#         item=lcs2(x,y)
#         if item in toRet:
#             toRet_remove(item)
#      
#     return toRet

def lcs2(tree,s1,s2):
    return max(tree[s1]['all_parents'] & tree[s2]['all_parents'])

def infimum2_OLDLYUSED(tree,p1,p2):
    toRet=set()
    if p1<>p2:
        for x,y in product(p1,p2):
            toRet|={lcs2(tree,x,y)}
    else :
        toRet=set(p1)
    toRet_remove=toRet.remove
    for x,y in combinations(toRet,2):
        if x not in toRet or y not in toRet:
            continue
        item=lcs2(tree,x,y)
        if item in toRet:
            toRet_remove(item)
     
    return toRet

def infimum2(tree,p1,p2):
    toRet=set()
    if p1<>p2:
        toRet={max(tree[x]['all_parents'] & tree[y]['all_parents']) for x in p1 for y in p2}
    else :
        toRet=set(p1)
    for x in toRet:
        toRet=toRet-tree[x]['all_parents_exclusive']

    return sorted(toRet)

def maximum_tree(tree,set_tag):
    return sorted(set_tag-{tag_parent for tag in set_tag for tag_parent in tree[tag]['all_parents_exclusive']})

def maximum(set_tag):
    return sorted(set_tag-{tag_parent for tag in set_tag for tag_parent in all_parents_tag_exclusive(tag)})


def isParent(t1,t2):
        if len(t1)==0:
            return True
        t1_split=t1.split('.')
        t2_split=t2.split('.')
        if len(t1_split)<len(t2_split):
            return all([t1_split[i]==t2_split[i] for i in range(len(t1_split))])
        return False
    

# def original_pattern_and_refin(tree,closed,toContinueFrom,ref=0):
#     if toContinueFrom==closed :#or len(toContinueFrom)>(len(original_p)+1):
#         return [closed]
# #     toContinueFrom_afterref=toContinueFrom[ref+1:]
# #     if toContinueFrom_afterref==sorted(infimum2(tree,toContinueFrom_afterref,toContinueFrom_afterref)): #After ref+1 every we must have a correct pattern (no parents included with their sons in toContinueFrom[ref+1]
# #         return [toContinueFrom,closed]
#     return [toContinueFrom,closed]

def original_pattern_and_refin(closed,toContinueFrom):
    if toContinueFrom==closed :
        return [closed]
    return [toContinueFrom,closed]

# def order_by_refin(p1,p2): #When do we consider than p1<=p2 when a closure happened ( we don't refine only from the ending)
#     range_len_min=range(min(len(p1),len(p2)))
#     
#     return all((p1[i]<=p2[i]) or isParent(p2[i],p1[i]) for i in range_len_min )
    #return all((x<=y) or isParent(y,x) for x,y in zip(p1,p2) ) #and all(p1[i]<p1[i+1] for i in range(len(p1)-1))
    
    
# def order_by_refin(p1,p2): #When do we consider than p1<=p2 when a closure happened ( we don't refine only from the ending)
#     min_len_range=range(min(len(p1),len(p2)))
#     return all((p1[i]<=p2[i]) or isParent(p2[i],p1[i]) for i in min_len_range ) #and all(p1[i]<p1[i+1] for i in range(len(p1)-1))


# def value_to_yield_refin_correct(tree,toContinueFrom,refin):
#     p_refin=toContinueFrom[:refin]
#     #all(toContinueFrom[i]<toContinueFrom[i+1] for i in range(len(toContinueFrom)-1)) and 
#     return True if sorted(infimum2(tree,p_refin,p_refin))==p_refin  else False

# def order_by_refin(p1,p2): #When do we consider than p1<=p2 when a closure happened ( we don't refine only from the ending)
#     return True 


def childrens_themes2_refin(tree,p,width_max=float('inf'),refin_index=None):
    len_p=len(p)
    if len_p<=width_max:
        refin_index=len_p-1
        last_t=p[refin_index]
        actual=tree[last_t]
        parent=actual['parent']
        for c in actual['children']:
            actual_child=p[:]
            actual_child[refin_index]=c
            yield actual_child,refin_index
        if len_p<width_max:
            brothers_and_uncles=[]
            brothers_and_uncles_extend=brothers_and_uncles.extend
            while parent is not None:
                brothers_and_uncles_extend(actual['right_borthers'])
                actual=tree[parent]
                parent=actual['parent']
            for b in brothers_and_uncles:
                actual_child=p[:]
                actual_child.insert(refin_index+1,b)
                yield actual_child,refin_index+1


def childrens_themes2_refin_new(tree,pattern,widthmax=float('inf'),refinement_index=None):
    len_p=len(pattern)
    refin_index_is_not_last=refinement_index+1<len_p 
    p_refinindex_1=pattern[refinement_index+1] if refin_index_is_not_last else None
    if len_p<=widthmax:
        if refinement_index is None:
            refinement_index=len_p
        last_t=pattern[refinement_index]
        actual=tree[last_t]
        parent=actual['parent']
        for c in actual['children']:
            if refin_index_is_not_last and c>=p_refinindex_1:
                continue
            actual_child=pattern[:]
            actual_child[refinement_index]=c
            yield actual_child,refinement_index
        if len_p<widthmax:
            brothers_and_uncles=[br for par in actual['all_parents'] for br in tree[par]['right_borthers'] if not (refin_index_is_not_last and br>=p_refinindex_1)]
            for b in brothers_and_uncles:
                actual_child=pattern[:]
                actual_child.insert(refinement_index+1,b)
                yield actual_child,refinement_index+1

def value_to_yield_refin(tree,p):
    return p if infimum2(tree,p,p)==p else None

def value_to_yield_refin_ref(tree,p,ref):
    return None if (ref<len(p)-1) and p[ref] in tree[p[ref+1]]['all_parents']  else p

def childrens_themes2_all_refin(tree,p,width_max=float('inf'),refin_index=None):
    len_p=len(p)
#     if refin_index is None:
#         refin_index=len_p-1
    for c,refin_child in childrens_themes2_refin(tree,p,width_max,len(p)-1):
        yield c,refin_child
          
def childrens_themes2_all_refin_new(tree,p_from,width_max=float('inf'),refin_index=None):
    for p in p_from:
        len_p=len(p)
        for new_refin in range(refin_index,len_p):
            if new_refin>0 and p[new_refin-1] in tree[p[new_refin]]['all_parents']:#(isParent(p[new_refin-1],p[new_refin]) or p[new_refin-1]==p[new_refin]):
                break
            for c,refin_child in childrens_themes2_refin_new(tree,p,width_max,new_refin):
                yield c,refin_child       

                    
def closed_themes_2(tree,arr_p):
    set_arr_p=set([tuple(x) for x in arr_p])
    if len(set_arr_p)==0:
        return []
    if len(set_arr_p)==1:
        closed=infimum2(tree,arr_p[0],arr_p[0])
    else :

        iter_set_arr_p=iter(set_arr_p)
        closed=next(iter_set_arr_p)
        for x in iter_set_arr_p:
            closed=infimum2(tree,closed,x)
    return closed




def smallest_tree_with_parents(p):
    ret=set([''])
    for t in p :
        v=t.split('.')
        ret|=set(['.'.join(v[0:x+1]) for x in range(len(v))])
    return ret

def pattern_cover_tagged_elem(p,e):
    return smallest_tree_with_parents(e).issuperset(p)


def smallest_tree_with_parents_new(tree,p):
    ret={''}
    for t in p :
        ret|=tree[t]['all_parents']
    return ret

def pattern_cover_tagged_elem_new(tree,p,e):
    return smallest_tree_with_parents_new(tree,e).issuperset(p)
    #return (sorted(infimum2(tree, p, e))==p)


# def closure_continue_from(tree,p,closed,refs): #what is the pattern which represent the one that we need to continue from after closing (it's none if the lexicographic order is not respected)
#     if len(closed)==0:
#         return None #EQUIVALENT TO EMPTY SUPPORT
#     #new_pattern=sorted(set(lcs2(tree,x,y) for x,y in zip(p,closed)) | set(closed)) if respect_order_themes2(p,closed,refs) else None
#     new_pattern=sorted(set(p) | set(closed)) if respect_order_themes2(p,closed,refs) else None
# #     if new_pattern is not None and len(new_pattern)>1 and new_pattern[0]=='':
# #         new_pattern=new_pattern[1:]
#     
#     return new_pattern

def closure_continue_from(pattern,closed,refinement_index): #what is the pattern which represent the one that we need to continue from after closing (it's none if the lexicographic order is not respected)
    if len(closed)==0 or not respect_order_themes2(pattern,closed,refinement_index): #SUPPORT IS EMPTY
        return None
    ref_in_closed=closed[refinement_index]
    ref_in_p=pattern[refinement_index]
    new_pattern=closed[:]
    if ref_in_p<ref_in_closed:
        new_pattern.insert(refinement_index,ref_in_p)
    return [new_pattern] if new_pattern==closed else [new_pattern,closed]

def enumerator_tree_new(tree,p=[''],refin=None,width_max=float('inf')):
    yield p
    for child,new_ref in childrens_themes2_all_refin(tree,p,width_max,refin):
        for val in enumerator_tree_new(tree,child,new_ref,width_max):
            yield val
            


##########################################################################################
def enumerator_tree_new_skip(tree,p=[''],refin=None,width_max=float('inf'),configuration={'skip_list':[]},support=[]):
    #to_yield=value_to_yield_refin(tree,p)
    #if to_yield is not None:
    yield p,support
    supportConfig=configuration['support'] if (configuration['support'] is not None) else support
    configuration['support']=None
    if p not in configuration['skip_list']:
        for child,new_ref in childrens_themes2_all_refin(tree,p,width_max,refin):
            for val,supportCH in enumerator_tree_new_skip(tree,child,new_ref,width_max,configuration,support=supportConfig):
                yield val,supportCH       


def enumerator_tree_new_skip_use(tree,p=[''],refin=None,width_max=float('inf'),configuration={'skip_list':[],'pattern':None}):
    to_yield=value_to_yield_refin(p)
    
    if to_yield is not None:
        yield to_yield
    
    closingConfig=configuration['pattern'] if (configuration['pattern'] is not None) else p
    configuration['pattern'] =None
    
    if to_yield not in configuration['skip_list']:
        for child,new_ref in childrens_themes2_all_refin(tree,closingConfig,width_max,refin):
            for val in enumerator_tree_new_skip_use(tree,child,new_ref,width_max,configuration):
                yield val    
       

def enumerator_tree_new_skip_use_new(tree,p=[''],refin=None,width_max=float('inf'),configuration={'skip_list':[],'pattern':None,'support':None},support=[]):
    to_yield=value_to_yield_refin_ref(tree,p,refin)
    
    if to_yield is not None:
        yield to_yield,refin,support
    
    closingConfig=configuration['pattern'] if (configuration['pattern'] is not None) else [p]
    supportConfig=configuration['support'] if (configuration['support'] is not None) else support
    configuration['pattern'] =None
    configuration['support']=None
    
    if to_yield not in configuration['skip_list']:
        for child,new_ref in childrens_themes2_all_refin_new(tree,closingConfig,width_max,refin):
            for val,val_ref,supportCH in enumerator_tree_new_skip_use_new(tree,child,new_ref,width_max,configuration,support=supportConfig):
                yield val ,val_ref ,supportCH   
            

def get_tree_from_dataset(dataset):
    themes=sorted({x for y in dataset.values()  for x in y})
    return tree_theme2(themes) 



def calcul_support(tree,pattern,dataset):
    support={}
    for e,d_e in dataset.iteritems():
        if pattern_cover_tagged_elem_new(tree,pattern,d_e):
            support[e]=d_e
    return support

def calcul_support_init(tree,pattern,dataset):
    support={}
    
    for e,d_e in dataset.iteritems():
        if set(d_e) & set(list(dfs_tags(tree, pattern[0]))): 
            support[e]=d_e
    return support

def calcul_support_opt(tree,pattern,ref,dataset):
#     for e,d_e in dataset.iteritems():
#         if pattern_cover_tagged_elem_new(tree,pattern,d_e):
#             support[e]=d_e
    keys=set(dataset.keys())
    for t in pattern[ref:]:
        keys&=tree[t]['SUPPORT']
        if len(keys)==0:
            return {}
    support = {k:dataset[k] for k in keys}
    return support
    #return {e:dataset[e] for e in dataset if pattern_cover_tagged_elem_new(tree,pattern,dataset[e])}  


def enumerator_tree_new_dataset1(dataset,width_max=float('inf')):
    t=get_tree_from_dataset(dataset)
    res=[]
    final=[]
    configuration={'skip_list':[],'support':None}
    cnt=0
    cnt2=0
    for x,sup in enumerator_tree_new_skip(t,configuration=configuration,width_max=width_max,support=dataset):
        cnt+=1
        support=calcul_support(t,x,sup)
        descs=list(set([tuple(dataset[e]) for e in support]))
        if len(support)==0:
            configuration['skip_list']=[x]
            continue
        cnt2+=1
        closed=closed_themes_2(t,descs)
        configuration['support']=support
        if closed not in res:
            res.append(closed)
            final.append((x,closed))
            
    print '---------------',cnt,'-',cnt2,'-',len(res),'---------------' 
    return final

def enumerator_tree_new_dataset1_supportopt(dataset,width_max=float('inf'),threshold=1):
    t=get_tree_from_dataset(dataset)
    t['']['SUPPORT']=calcul_support(t,[''],dataset)
    for x in sorted(t) :
        if x == '':
            continue
        x_infos=t[x]
        x_infos['SUPPORT']=calcul_support(t,[x],t[x_infos['parent']]['SUPPORT'])
    for x in t:  
        x_infos=t[x]  
        x_infos['SUPPORT']=set(x_infos['SUPPORT'])
        
        
    res=[]
    final=[]
    configuration={'skip_list':[],'support':None}
    cnt=0
    cnt2=0
    for x,sup in enumerator_tree_new_skip(t,configuration=configuration,width_max=width_max,support=dataset):
        cnt+=1
        support=calcul_support_opt(t,x,len(x)-1,sup)
        descs=list(set([tuple(dataset[e]) for e in support]))
        if len(support)<threshold:
            configuration['skip_list']=[x]
            continue
        cnt2+=1
        closed=closed_themes_2(t,descs)
        configuration['support']=support
        if closed not in res:
            res.append(closed)
            final.append((x,closed))
            
    print '-----------------------------',cnt,'-',cnt2,'-',len(res),'-----------------------------' 
    return final



 

    
def enumerator_tree_new_dataset2_new(dataset,width_max=float('inf'),verbose=False):
    tree=get_tree_from_dataset(dataset)
    set_intersection=set.intersection
    dataset_new={}
    for o in dataset:
        dataset_new[o]={x for t in dataset[o] for x in tree[t]['all_parents']}
      
    configuration={'skip_list':[],'pattern':None,'support':None}
    res=[]
    cnt=0
    cnt2=0
    for x,refs,sup in enumerator_tree_new_skip_use_new(tree,configuration=configuration,refin=0,width_max=width_max,support=dataset_new.values()):
        
        cnt+=1
        #support=calcul_support(tree,x,sup)#[e for e in dataset if pattern_cover_tagged_elem_new(tree,x,dataset[e])]
        support=scaling_support_computingQQ(sup,set(x))
        
        if len(support)==0:
            configuration['skip_list']=[x]
            continue
        cnt2+=1
        closed_x=reduce(set_intersection,support)
        closed_pattern=maximum_tree(tree, closed_x)
        continue_from=closure_continue_from(x,closed_pattern,refs)
        if continue_from is None:
            if verbose and len(closed_pattern)>0:
                res.append((closed_pattern,x,refs,None))
            configuration['skip_list']=[x]
            continue
        
        configuration['pattern']=continue_from
        configuration['support']=support
            
        res.append((closed_pattern,x,refs))
    print '---------------',cnt,'-',cnt2,'-',len(res),'---------------' 
    return res


def enumerator_tree_new_dataset2_new_supportopt(dataset,width_max=float('inf'),threshold=1,verbose=False):
    t=get_tree_from_dataset(dataset)
    t['']['SUPPORT']=calcul_support(t,[''],dataset)
    for x in sorted(t) :
        if x == '':
            continue
        x_infos=t[x]
        x_infos['SUPPORT']=calcul_support(t,[x],t[x_infos['parent']]['SUPPORT'])
    for x in t:  
        x_infos=t[x]  
        x_infos['SUPPORT']=set(x_infos['SUPPORT'])
        
        
        
    configuration={'skip_list':[],'pattern':None,'support':None}
    res=[]
    cnt=0
    cnt2=0
    for x,refs,sup in enumerator_tree_new_skip_use_new(t,configuration=configuration,refin=0,width_max=width_max,support=dataset):
        
        cnt+=1
        support=calcul_support_opt(t,x,refs,sup)#[e for e in dataset if pattern_cover_tagged_elem_new(t,x,dataset[e])]
        if len(support)<threshold:
            configuration['skip_list']=[x]
            continue
        cnt2+=1
        #descs=list(set([tuple(dataset[e]) for e in support]))
        descs=[dataset[e] for e in support]
        closed_pattern=closed_themes_2(t,descs)
        continue_from=closure_continue_from(x,closed_pattern,refs)
        #print x,refs,closed_pattern,continue_from
        if continue_from is None:
            if verbose and len(closed_pattern)>0:
                res.append((closed_pattern,x,refs,None))
            configuration['skip_list']=[x]
            continue
        
        configuration['pattern']=continue_from
        configuration['support']=support
            
        res.append((closed_pattern,x,refs))
    print '---------------',cnt,'-',cnt2,'-',len(res),'---------------' 
    return res


#-------------------SCALING------------------------#

def scaling_support_computing(dataset,pattern):
    pattern_issubset=pattern.issubset
    return {x:y for x,y in dataset.iteritems() if pattern_issubset(y)}

def scaling_support_computingQQ(dataset,pattern):
    pattern_issubset=pattern.issubset
    return filter(pattern_issubset,dataset)
    #return {x:y for x,y in dataset.iteritems() if pattern_issubset(y)}

def enumerator_tree_new_dataset_scaling(dataset,d={''},pos=1,attributes=[],nb_visited=[1,1]):
    set_intersection=set.intersection
    attributes_index=attributes.index
    yield d,dataset
    for i in range(pos,len(attributes)):
        if attributes[i] not in d : 
            set_dnew=d|{attributes[i]}
            support = scaling_support_computingQQ(dataset,set_dnew)
            #scaling_support_computingQQ(dataset,set_dnew)#scaling_support_computing(dataset,set_dnew)
            
            nb_visited[0]+=1
            if len(support)>0:
                nb_visited[1]+=1
                closed=reduce(set_intersection,support)
                if not any(attributes_index(x)<i+1 for x in (closed-set_dnew) ):

                    for c,c_dataset in enumerator_tree_new_dataset_scaling(support,closed,i+1,attributes,nb_visited):
                        yield c,c_dataset
    
    


def enumerator_tree_new_dataset_scaling_init(dataset,width_max=float('inf'),verbose=False):
    dataset_new={}
    nb_visited=[1,1]
    for o in dataset:
        dataset_new[o]={x for t in dataset[o] for x in all_parents_tag(t)}
        
    attributes=sorted(reduce(set.union,dataset_new.values()))
    count=0
    for closed,sup in enumerator_tree_new_dataset_scaling(dataset_new.values(),
                                                          reduce(set.intersection,[set(y) for x,y in dataset_new.iteritems()]),
                                                          1,
                                                          attributes,
                                                          nb_visited):
        count+=1
        yield maximum(closed)
    print '------------------------',nb_visited[0],'-',nb_visited[0],'-',count,'-----------------------------'



def support_computing_patternStructure(dataset,pattern):
    pattern_set=set(pattern)
#     pattern_set_issubset=pattern_set.issubset
#     return {x:y for x,y in dataset.iteritems() if pattern_set_issubset(y)}
    pattern_issubset=pattern_set.issubset
    return filter(pattern_issubset,dataset)

def compute_closed_pattern(tree,support):
    return maximum_tree(tree, reduce(set.intersection,support))
def enumerator_tree_new_dataset_patternStructure(tree,dataset,d,refinement=0,width_max=float('inf'),nb_visited=[0,0]):
    #set_intersection=set.intersection
    to_yield=value_to_yield_refin_ref(tree,d,refinement)
    flag_continue=False
    if to_yield is not None:
        nb_visited[0]+=1
        support=support_computing_patternStructure(dataset,d)
        if len(support)>0:
            nb_visited[1]+=1
            closed_pattern=compute_closed_pattern(tree,support)
            continue_from=closure_continue_from(d,closed_pattern,refinement)
            if continue_from is not None:
                to_continue_from=continue_from
                yield closed_pattern,support
                flag_continue=True
                
    else :
        to_continue_from=[d]
        support = dataset
        flag_continue=True
                
    if flag_continue:   
        for child,new_ref in childrens_themes2_all_refin_new(tree,to_continue_from,width_max,refinement):
            for val,val_support in enumerator_tree_new_dataset_patternStructure(tree,support,child,new_ref,width_max,nb_visited):
                yield val,val_support
            
        

def enumerator_tree_new_dataset_patternStructure_init(dataset,width_max=float('inf'),verbose=False):
    tree=get_tree_from_dataset(dataset)
    nb_visited=[0,0]
    dataset_new={}
    for o in dataset:
        dataset_new[o]={x for t in dataset[o] for x in tree[t]['all_parents']}
    
    #support=dataset_new
    support=dataset_new.values()
    count=0
    for closed,sup in enumerator_tree_new_dataset_patternStructure(tree,support,[''],0,width_max,nb_visited):
        count+=1
        yield closed
    print '------------------------',nb_visited[0],'-',nb_visited[1],'-',count,'-----------------------------'


def enumerator_tree_new_dataset_naive(tree,dataset,d,refinement=0,width_max=float('inf'),nb_visited=[0,0]):
    #set_intersection=set.intersection
    
    nb_visited[0]+=1
    support=support_computing_patternStructure(dataset,d)
    
    if len(support)>0:
        yield d,support
        nb_visited[1]+=1
        for child,new_ref in childrens_themes2_all_refin(tree,d,width_max,refinement):
            for val,val_support in enumerator_tree_new_dataset_naive(tree,support,child,new_ref,width_max,nb_visited):
                yield val,val_support


def enumerator_tree_new_dataset_naive_init(dataset,width_max=float('inf'),verbose=False):
    tree=get_tree_from_dataset(dataset)
    nb_visited=[0,0]
    dataset_new={}
    for o in dataset:
        dataset_new[o]={x for t in dataset[o] for x in tree[t]['all_parents']}
    
    #support=dataset_new
    support=dataset_new.values()
    count=0
    closed=[]
    for d,sup in enumerator_tree_new_dataset_naive(tree,support,[''],0,width_max,nb_visited):
        closed_pattern=compute_closed_pattern(tree,sup)
        if closed_pattern in closed:
            continue
        closed.append(closed_pattern)
        count+=1
        yield closed
    print '------------------------',nb_visited[0],'-',nb_visited[1],'-',count,'-----------------------------'

# def compute_closed_pattern(tree,support):
#     supportnew=[reduce(set.union,[set(tree[t]['all_parents']) for t in v]) for v in support]
#     return maximum_tree(tree, reduce(set.intersection,supportnew))
# def enumerator_tree_new_dataset_patternStructure(tree,dataset,d,refinement=0,width_max=float('inf'),nb_visited=[0,0]):
#     #set_intersection=set.intersection
#     to_yield=value_to_yield_refin_ref(tree,d,refinement)
#     flag_continue=False
#     if to_yield is not None:
#         nb_visited[0]+=1
#         support=calcul_support_opt(tree,d,refinement,dataset) #scaling_support_computingQQ(dataset,set(d))
#         if len(support)>0:
#             nb_visited[1]+=1
#             closed_pattern=compute_closed_pattern(tree,support.values())
#             continue_from=closure_continue_from(d,closed_pattern,refinement)
#             if continue_from is not None:
#                 to_continue_from=continue_from
#                 yield closed_pattern,support
#                 flag_continue=True
#                 
#     else :
#         to_continue_from=[d]
#         support = dataset
#         flag_continue=True
#                 
#     if flag_continue:   
#         for child,new_ref in childrens_themes2_all_refin_new(tree,to_continue_from,width_max,refinement):
#             for val,val_support in enumerator_tree_new_dataset_patternStructure(tree,support,child,new_ref,width_max,nb_visited):
#                 yield val,val_support
#             
#         
# 
# def enumerator_tree_new_dataset_patternStructure_init(dataset,width_max=float('inf'),verbose=False):
#     tree=get_tree_from_dataset(dataset)
#     nb_visited=[0,0]
#     
#     tree['']['SUPPORT']=calcul_support(tree,[''],dataset)
#     for x in sorted(tree) :
#         if x == '':
#             continue
#         x_infos=tree[x]
#         x_infos['SUPPORT']=calcul_support(tree,[x],tree[x_infos['parent']]['SUPPORT'])
#     for x in tree:  
#         x_infos=tree[x]  
#         x_infos['SUPPORT']=set(x_infos['SUPPORT'])
# 
#     count=0
#     for closed,sup in enumerator_tree_new_dataset_patternStructure(tree,dataset,[''],0,width_max,nb_visited):
#         count+=1
#         yield closed
#     print '------------------------',nb_visited[0],'-',nb_visited[1],'-',count,'-----------------------------'


# def enumerator_tree_new_dataset_scaling_supportopt(tree,dataset,d=[''],pos=1,attributes=[],nb_visited=[1]):
#     set_intersection=set.intersection
#     attributes_index=attributes.index
#     yield d,dataset
#     for i in range(pos,len(attributes)):
#         if attributes[i] not in d : 
#             dnew=sorted(d+[attributes[i]])
#             set_dnew=set(dnew)
#             #support={x:y for x,y in dataset.iteritems() if set_dnew.issubset(y)}
#             support = calcul_support_opt(tree, dnew, 1, dataset) 
#             #calcul_support(tree, dnew, dataset)
#             #scaling_support_computing(dataset,set_dnew)
#             
#             nb_visited[0]+=1
#             if len(support)>0:
#                 
#                 closed=reduce(set_intersection,support.values())
#                 if not any(attributes_index(x)<i+1 for x in (closed-set_dnew) ):
# 
#                     for c,c_dataset in enumerator_tree_new_dataset_scaling_supportopt(tree,support,sorted(closed),i+1,attributes,nb_visited):
#                         yield c,c_dataset
#                         
#                         
# def enumerator_tree_new_dataset_scaling_init_supportopt(dataset,width_max=float('inf'),verbose=False):
#     dataset_new={}
#     tree=get_tree_from_dataset(dataset)
#     nb_visited=[0]
#     for o in dataset:
#         dataset_new[o]={x for t in dataset[o] for x in all_parents_tag(t)}
#         
#     attributes=sorted(reduce(set.union,[set(y) for x,y in dataset_new.iteritems()]))
#     
#     
#     tree['']['SUPPORT']=calcul_support(tree,[''],dataset)
#     for x in sorted(tree) :
#         if x == '':
#             continue
#         x_infos=tree[x]
#         x_infos['SUPPORT']=calcul_support(tree,[x],tree[x_infos['parent']]['SUPPORT'])
#     for x in tree:  
#         x_infos=tree[x]  
#         x_infos['SUPPORT']=set(x_infos['SUPPORT'])
#     
#     
#     count=0
#     for closed,sup in enumerator_tree_new_dataset_scaling_supportopt(tree,dataset_new,sorted(reduce(set.intersection,[set(y) for x,y in dataset_new.iteritems()])),1,attributes,nb_visited):
#         count+=1
#         yield infimum2(tree,closed,closed)
#     print '------------------------',nb_visited,count,'-----------------------------'
#     
#         
# #-------------------SCALING------------------------#


def evaluate_themes_CLOSED2(dataset,width_max=float('inf')):
    start=time()
    count=0
    pr = cProfile.Profile()
    pr.enable()
    for x in enumerator_tree_new_dataset2_new(dataset,width_max):
        count+=1
    end = time()- start
    pr.disable()
    ps = pstats.Stats(pr)
    print 'COUNT OF CLOSED = ',count
    ps.sort_stats('cumulative').print_stats(10) #cumulative






def evaluate_themes_NOTCLOSED2(dataset,width_max=float('inf')):
    start=time()
    count=0
    pr = cProfile.Profile()
    pr.enable()
    for x in enumerator_tree_new_dataset1(dataset,width_max):
        count+=1
    end = time()- start
    pr.disable()
    ps = pstats.Stats(pr)
    print 'COUNT OF CLOSED = ',count
    ps.sort_stats('cumulative').print_stats(10) #cumulative 
    

# def get_from_whole_alea(nb):
#     len_whole=len(whole)
#     keys=range(len(whole))
#     selectedKeys=[]
#     for x in range(nb):
#         selected=trunc(uniform(0,len(keys)))
#         selectedKeys.append(str(keys[selected]))
#         keys.remove(keys[selected])
#     return {x:whole[x] for x in selectedKeys}
# 
# def test(nb):
#     tt=get_from_whole_alea(nb)
#     len(enumerator_tree_new_dataset2_new(tt))
#     len(enumerator_tree_new_dataset1(tt))
#     return tt


def generate_random_dataset_from_keys(keys,nb,max_width):
    dataset={}
    tree_keys=get_tree_from_dataset({k:[k] for k in keys})
    print len(tree_keys)
    for i in range(nb):
        o=[keys[trunc(uniform(0,len(keys)))] for f in range(trunc(uniform(1,max_width+1)))]
        dataset[str(i)]=sorted(infimum2(tree_keys,o,o))
    return dataset