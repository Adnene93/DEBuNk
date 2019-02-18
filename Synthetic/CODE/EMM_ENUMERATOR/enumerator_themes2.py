from itertools import product, combinations
from time import time

def respect_order_themes2(p1,p2):
    #return sorted(p1)<=sorted(p2)
    len_min=min(len(p1),len(p2))-1
    range_len_min=range(len_min)
    return all(p1[i]==p2[i] for i in range_len_min) and p1[len_min]<=p2[len_min]
        
    
    #return all(x==y for x,y in zip(p1[:len_min],p2[:len_min])) and p1[len_min]<=p2[len_min]
    
def lcs2(s1,s2):
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

def infimum2(p1,p2):
    toRet=set()
    for x,y in product(p1,p2):
        toRet|={lcs2(x,y)}
    toRet_remove=toRet.remove
    for x,y in combinations(toRet,2):
        if x not in toRet or y not in toRet:
            continue
        item=lcs2(x,y)
        if item in toRet:
            toRet_remove(item)
    
    return toRet



def description_minimal_themes2(arr_p):
    set_arr_p=set([tuple(x) for x in arr_p])
    if len(set_arr_p)==1:
        pattern=sorted(infimum2(arr_p[0],arr_p[0]))
    else :
        pattern=sorted(reduce(infimum2,set_arr_p))
    
    #pattern=sorted(infimum2(pattern,pattern))
    return pattern,None,None #pattern,arr_data,refin_index

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


def tree_theme2(themes):
    flat=flattenThemesTree2(themes)
    ret_map={};
    for x in flat:
        parent_x=parent_tag(x)
        ret_map[x]={'parent':parent_x,'children':[],'right_borthers':[],'left_brothers':[]}
        if parent_x is not None:
            ret_map[parent_x]['children'].append(x)

    for x,y in ret_map.iteritems():
        if y['parent'] is not None:
            brothers=ret_map[y['parent']]['children']
            y['right_borthers']=brothers[brothers.index(x)+1:]
            y['left_brothers']=brothers[:brothers.index(x)]
    return ret_map


def childrens_themes2(tree,p,width_max=float('inf')):
    len_p=len(p)
    if len_p<=width_max:
        last_t=p[-1]
        actual=tree[last_t]
        parent=actual['parent']
        for c in actual['children']:
            actual_child=p[:]
            actual_child[-1]=c
            yield actual_child
        if len_p<width_max:
            brothers_and_uncles=[]
            brothers_and_uncles_extend=brothers_and_uncles.extend
            while parent is not None:
                brothers_and_uncles_extend(actual['right_borthers'])
                actual=tree[parent]
                parent=actual['parent']
            for b in brothers_and_uncles:
                actual_child=p+[b]
                yield actual_child

def enumerator_tree2(tree,p=[''],width_max=3):
    yield p
    for child in childrens_themes2(tree,p,width_max):
        for val in enumerator_tree2(tree,child,width_max):
            yield val
            
            

def evaluate_themes_2(themes,width_max=3):
    start=time()
    t=tree_theme2(themes)
    count=0
    for x in enumerator_tree2(t,width_max=width_max):
        count+=1
    end = time()- start
    print 'nbmotifs = ', count, 'timespent = ', end
     
    
        
def value_to_yield_themes2(tree,opt=['']):
    return opt

def childrens_themes_exploitable2(tree,refinement=[''],width_max=float('inf')):
    p=refinement
    if width_max is None:
        width_max=float('inf')
    for x in childrens_themes2(tree,p,width_max):
        yield tree,x
    
def description_from_pattern_themes2(pattern,labelmap={}):
    return [labelmap.get(key,key) for key in pattern]





#############################################################
def isParent(t1,t2):
        if len(t1)==0:
            return True
        p1_split=t1.split('.')
        p2_split=t2.split('.')
        if len(p1_split)<len(p2_split):
            return all([p1_split[i]==p2_split[i] for i in range(len(p1_split))])
        return False
 
 
def order_by_refin(p1,p2): #When do we consider than p1<=p2 when a closure happened ( we don't refine only from the ending)
    return all((x<=y) or isParent(y,x) for x,y in zip(p1,p2) ) and all(p1[i]<p1[i+1] for i in range(len(p1)-1))
 
def childrens_themes2_refin_new(tree,pattern,widthmax=float('inf'),refinement_index=None):
    len_p=len(pattern)
    if len_p<=widthmax:
        if refinement_index is None:
            refinement_index=len(pattern)-1
    
        last_t=pattern[refinement_index]
        actual=tree[last_t]
        parent=actual['parent']
    
        for c in actual['children']:
    
            actual_child=pattern[:]
            actual_child[refinement_index]=c
            if not order_by_refin(actual_child,pattern) :
                continue
            yield actual_child,refinement_index
        if len_p<widthmax:
            brothers_and_uncles=[]
            brothers_and_uncles_extend=brothers_and_uncles.extend
            while parent is not None:
                brothers_and_uncles_extend(actual['right_borthers'])
                actual=tree[parent]
                parent=actual['parent']
            for b in brothers_and_uncles:
                actual_child=pattern[:]
                actual_child.insert(refinement_index+1,b)
                if not order_by_refin(actual_child,pattern) :
                    continue
                yield actual_child,refinement_index+1


def childrens_themes2_all_refin_TO_USE(tree,p,width_max=float('inf'),refin_index=None):
    len_p=len(p)
    if refin_index is None:
        refin_index=len_p-1
    for new_refin in range(refin_index,len_p):
        for c,refin_child in childrens_themes2_refin_new(tree,p,width_max,new_refin):
            yield c,refin_child
            
def value_to_yield_refin_TO_USE(p):
    return p if sorted(infimum2(p,p))==p else None





def childrens_themes2_all_refin(tree,p,width_max=float('inf'),refin_index=None):
    len_p=len(p)
    if refin_index is None:
        refin_index=len_p-1
    for new_refin in range(refin_index,len_p):
        for c,refin_child in childrens_themes2_refin_new(tree,p,width_max,new_refin):
            yield tree,c #,refin_child
 
def value_to_yield_refin(p,opt=['']):
    return opt if sorted(infimum2(opt,opt))==opt else None


def description_from_pattern_themes2_refin(pattern,labelmap={}):
    return [labelmap.get(key,key) for key in pattern]
        
def enumerator_tree_new(tree,p=[''],width_max=float('inf'),refin=None):
    to_yield=value_to_yield_refin_TO_USE(p)
    if to_yield is not None:
        yield to_yield
    for child,new_ref in childrens_themes2_all_refin_TO_USE(tree,p,width_max,refin):
        for val in enumerator_tree_new(tree,child,width_max,new_ref):
            yield val
            
def closure_continue_from(pattern,closed): #what is the pattern which represent the one that we need to continue from after closing (it's none if the lexicographic order is not respected)
    new_pattern=sorted(set(lcs2(x,y) for x,y in zip(pattern,closed)) | set(closed)) if respect_order_themes2(pattern,closed) else None
    #closed_refin=p_refin
    return new_pattern

















            
