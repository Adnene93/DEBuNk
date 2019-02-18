from itertools import product, combinations


# def flattenThemesTree(themes):
#     arrNew=[]
#     for x in themes :
#         arrNew.append(x)
#         s= x.split('.')
#         for i in range(len(s[:-1])) :
#             sub=''
#             for j in range(i+1):
#                 sub+=s[j]+'.'
#             sub=sub[:-1]
#             if sub not in arrNew :
#                 arrNew.append(sub)
#     arrNew.sort()
#     return arrNew

def respect_order(p1,p2):
    return sorted(p1)<=sorted(p2)

def lcs(s1,s2):
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

def infimum(p1,p2):
    toRet=set()
    for x,y in product(p1,p2):
#         lcs_x_y=lcs(x,y)
#         if lcs_x_y==x or lcs_x_y==y :
#             continue
        toRet|={lcs(x,y)}
    #toRet2=toRet.copy()
    toRet_remove=toRet.remove
    for x,y in combinations(toRet,2):
        if x not in toRet or y not in toRet:
            continue
        item=lcs(x,y)
        if item in toRet:
            toRet_remove(item)
    return toRet
# def infimum(p1,p2):

def description_minimal_themes(arr_p):
    pattern=sorted(reduce(infimum,set([tuple(x) for x in arr_p])))
    return pattern,None,None #pattern,arr_data,refin_index


def flattenThemesTree(themes):
    arrNew=[]
    for x in themes :
        #arrNew.append(x)
        s= x.split('.')
        for i in range(len(s)) :
            sub=''
            for j in range(i+1):
                sub+=s[j]+'.'
            sub=sub[:-1]
            if sub not in arrNew :
                arrNew.append(sub)
    arrNew.sort()
    return arrNew

def createTreeOutOfThemes(themes):
    themesMAP={o['ID']:o['LABEL'] for o in themes}
    themesMAP_full={}
    newThemes=flattenThemesTree(themesMAP)#themesMAP.keys()
    themesCopy=newThemes[:]
    themes=newThemes[:]
    actualCount=0
    nb_nodes=0
    tree={'value':'','description':'','children':[],'nb_nodes':0}
    while not len(newThemes)==0 :
        for x in themes:
            seq_description=''
            if (x.count('.') == actualCount):
                index=0
                countPoint=x.count('.')
                splitted=x.split('.')
                subtree=tree
                #cutted_root=dict(tree)
                currentx=''
                while index<countPoint:
                    
                    currentx+=str(splitted[index])+'.'
                    subtreeChildren=[v['value'] for v in subtree['children']]
                    subtreeChild=subtreeChildren.index(currentx[:-1])
                    subtree=subtree['children'][subtreeChild]
                    seq_description=seq_description+subtree['description']+' | '
                    index+=1
                newNode={'value':x,'description':themesMAP.get(x,'-'),'children':[],'root':tree}
                seq_description=seq_description+newNode['description']
                newThemes.remove(x)
                themesMAP_full[x]=seq_description
                subtree['children'].append(newNode)
                nb_nodes+=1
         
        themes=newThemes[:]
        
        actualCount+=1
    tree['nb_nodes']=nb_nodes
    tree['root']=tree
    
    
    
    #REGULARIZE ROOTS :
    newThemes=themesCopy[:]
    themes=themesCopy[:]
    actualCount=0
    while not len(newThemes)==0 :
        for x in themes:
            if (x.count('.') == actualCount):
                index=0
                countPoint=x.count('.')
                splitted=x.split('.')
                subtree=tree
                
                currentx=''
                
                seq_indexes=[]
                
                while index<=countPoint:
                    
                    currentx+=str(splitted[index])+'.'
                    subtreeChildren=[v['value'] for v in subtree['children']]
                    subtreeChild=subtreeChildren.index(currentx[:-1])
                    subtree=subtree['children'][subtreeChild]
                    seq_indexes.append(subtreeChild)
                    index+=1
                
                newThemes.remove(x)
                
                cutted_root={'value':tree['value'],'description':tree['description'],'children':tree['children'][:],'root':tree,'nb_nodes':tree['nb_nodes']}
                
                remove_childs=cutted_root
                
                for ind in seq_indexes:
                    remove_childs['children']=remove_childs['children'][ind:]
                    
                    remove_childs['children'][0]={'value':remove_childs['children'][0]['value'],'description':remove_childs['children'][0]['description'],'children':remove_childs['children'][0]['children'][:],'root':remove_childs['children'][0]['root'],'nb_nodes':tree['nb_nodes']}
                    remove_childs=remove_childs['children'][0]
                
                subtree['root']=cutted_root
                if len(remove_childs['children'])>0:
                    remove_childs['children'][0]['root']=cutted_root
#                 print subtree['value'],seq_indexes,#[t['value'] for t in cutted_root['children']]
#                 explorer=cutted_root
#                 for ind in seq_indexes:
#                     print [t['value'] for t in explorer['children']],
#                      
#                     explorer=explorer['children'][0]
#                 print ''
        themes=newThemes[:]
        
        actualCount+=1
    
    
    return tree,themesMAP_full

def possible_sub_patterns(pattern):
    toRet=[]
    for width in range(1,len(pattern)+1):
        for comb in combinations(range(len(pattern)),width):
            index_choosen=list(comb)
            subPatternToCheck=[pattern[t] for t in index_choosen]
            toRet.append(subPatternToCheck)
    return toRet




def childrens_set_opt(trees,configuration,refinement_index=0):
    childrens_all=[]
    
    current_depth=len(trees)
    themes_arr=[tree['value'] for tree in trees]
    subpatterns_themes_arr=possible_sub_patterns(themes_arr)
    if not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
        for i in range(current_depth):
            childrens_all.append([node for node in trees[i]['children']])
        
        indexDifferents=[]
        valuesDifferents=[]
        #newPosChilds=[]
        for k in range(current_depth) :
            
            if themes_arr[k] in valuesDifferents:
                indexDifferents[valuesDifferents.index(themes_arr[k])].append(k)
            else :
                indexDifferents.append([k])
                valuesDifferents.append(themes_arr[k])
    
        for indexes in indexDifferents:
            possibleIter=[childrens_all[t] if t in indexes and refinement_index == indexes[0] else [trees[t]] for t in range(current_depth)]
            
            for subset in product(*possibleIter):
                posChild=list(subset)
                posChildArrValues=[tree['value'] for tree in posChild]
                
                if (not all(posChildArrValues[j]==themes_arr[j] for j in range(current_depth)) and 
                    all ((posChild[item1]['value']<=posChild[item1+1]['value'])
                    for item1 in range(current_depth-1))) :    
                        if any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
                            return
                        yield posChild

def enum_dfs_iterator_opt(trees,configuration,refinement_index=0):
    themes_arr=[tree['value'] for tree in trees]
    subpatterns_themes_arr=possible_sub_patterns(themes_arr)
    if not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
        if not any(themes_arr[i]==themes_arr[j] for i in range(len(themes_arr)-1) for j in range(i+1,len(themes_arr))):
            yield themes_arr
        #if not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
        for pos_refinement in range(refinement_index,len(themes_arr)) : 
            #if not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
                for subtrees in childrens_set_opt(trees,configuration,pos_refinement):
                    #if not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
                        for val in enum_dfs_iterator_opt(subtrees,configuration,pos_refinement):
                            #if not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
                                # and not any(x in possible_sub_patterns(val) for x in configuration['skip_list'])
                                yield val
                                


def direct_children(tree):
    return [node for node in tree['children']]



    

def childrens_set_opt_depthmax(trees,refinement_index=0): #refine one tree
        childrens_all=[]
        childrens_all_append=childrens_all.append
        current_depth=len(trees)
        themes_arr=[tree['value'] for tree in trees]
        
        for i in range(current_depth):
            childrens_all_append([node for node in trees[i]['children']])
        
        indexDifferents=[]
        indexDifferents_append=indexDifferents.append
        valuesDifferents=[]
        valuesDifferents_append=valuesDifferents.append
        for k in range(current_depth) :
            
            if themes_arr[k] in valuesDifferents:
                indexDifferents[valuesDifferents.index(themes_arr[k])].append(k)
            else :
                indexDifferents_append([k])
                valuesDifferents_append(themes_arr[k])
                
        for indexes in indexDifferents:
            indexes_0=indexes[0]
            possibleIter=[childrens_all[t] if t in indexes and refinement_index == indexes_0 else [trees[t]] for t in range(current_depth)]
            for subset in product(*possibleIter):
                posChild=list(subset)
                posChildArrValues=[tree['value'] for tree in posChild]
                if not (posChildArrValues[-1]==themes_arr[-1]): #(not all(posChildArrValues[j]==themes_arr[j] for j in range(current_depth))) :
                    yield posChild
                        
def all_childrens_set_opt_depthmax(trees,refinement_index=0,depthmax=None): #refine all
    root_tree=trees[-1]['root']
    values=[subtree['value'] for subtree in trees]
    if all(values[i]<values[j] for i in range(len(values)-2) for j in range(i+1,len(values)-1)):
        if depthmax is None:
            depthmax=root_tree['nb_nodes']
        
        for pos_refinement in xrange(refinement_index,depthmax) :
            trees2=trees[:]
            trees2_append=trees2.append
            for k in xrange(len(trees),pos_refinement+1):
                trees2_append(trees2[-1]['root'])
            for subtrees in childrens_set_opt_depthmax(trees2,pos_refinement):
                yield subtrees,pos_refinement

def value_to_yield_themes(trees,opt=['']):
    themes_arr = [subtree['value'] for subtree in trees]
    return themes_arr if all(themes_arr[i]<themes_arr[i+1] for i in range(len(themes_arr)-1)) else None

def possible_parents_themes(actual_arr,original_arr=[]):
    #countPoints=[x.count('.') for x in actual_arr]
    indexOfPoints=[[i for i,letter in enumerate(actual_arr[j]) if letter=='.'] for j in range(len(actual_arr))]
    parts_of_actual_arr=[([None] + [actual_arr[j][:k] for k in (indexOfPoints[j]+[None])])[-2:] for j in range(len(actual_arr))]
    
    arr_decal=[1]*len(actual_arr)
    arr_decal[0]=0
    index_of_0=0
    toRet=[]
    while 0 in arr_decal:
        parent=[parts_of_actual_arr[j][arr_decal[j]] for j in range(len(actual_arr))]
        if (index_of_0<len(actual_arr)-1):
            arr_decal[index_of_0+1]=0
            
        arr_decal[index_of_0]=1
        index_of_0+=1
        toRet.append([item for item in parent if item is not None])
    toRet.append(actual_arr[:])
    return toRet


def description_from_pattern_themes(pattern,labelmap={}):
    return [labelmap.get(key,key) for key in pattern]


def valid_pattern(trees):
    themes_arr = [subtree['value'] for subtree in trees]
    if all(themes_arr[i]<themes_arr[i+1] for i in range(len(themes_arr)-1)) : 
        return True
    return False

def enum_dfs_iterator_opt_depthmax(trees,configuration,refinement_index,depthmax=None):
    
    
    themes_arr=value_to_yield_themes(trees)
    
    if not themes_arr in configuration['skip_list'] :#not any(x in configuration['skip_list'] for x in subpatterns_themes_arr) :
        #if all(themes_arr[i]<themes_arr[i+1] for i in range(len(themes_arr)-1)) :                                                                                                                                            # and themes_arr[j] not in [t['value'] for t in trees[i]['children']] 
        if themes_arr is not None :
            yield themes_arr
        if  themes_arr not in configuration['skip_list']:
            for subtrees,pos_refinement in all_childrens_set_opt_depthmax(trees, refinement_index, depthmax):
#             for pos_refinement in range(refinement_index,depthmax) :
#                  
#                 #if themes_arr not in configuration['skip_list']:
#                     trees2=[trees[k] if k<len(trees) else tree for k in range(pos_refinement+1)]
#                     
#                     for subtrees in childrens_set_opt_depthmax(trees2,pos_refinement):
                        #if themes_arr not in configuration['skip_list']:
                            #print pos_refinement
                            for val in enum_dfs_iterator_opt_depthmax(subtrees,configuration,pos_refinement,depthmax):
                                #if themes_arr not in configuration['skip_list']:
                                    # and not any(x in possible_sub_patterns(val) for x in configuration['skip_list'])
                                    yield val
                                
def dfs_themes_depth_new(tree,configuration,depth): 
    trees=[]
    for i in range(depth):
        trees.append(tree)
  
    
    iterators=enum_dfs_iterator_opt(trees, configuration)
    for nexter in iterators :
        arrRet=nexter
        yield arrRet





def dfs_themes_depthmax_bfs(themes,configuration,depthmax):
    
    tree,themesMAP=createTreeOutOfThemes(themes)
    currentDepth=1
#     iterators=enum_dfs_iterator_opt_depthmax(tree,[tree],configuration,0,depthmax)
#     for arrRet in iterators:
#         yield arrRet,[themesMAP.get(key,'-') for key in arrRet]
    while currentDepth<=depthmax:
          
        iters=dfs_themes_depth_new(tree,configuration,currentDepth)
        arrRet=next(iters,None)
        while arrRet is not None :
            yield arrRet,[themesMAP.get(key,'-') for key in arrRet]
            arrRet=next(iters,None)
            if arrRet is None: 
                currentDepth+=1
                break
            
            
def dfs_themes_depthmax_dfs(themes,configuration,depthmax=None):
    
    tree,themesMAP=createTreeOutOfThemes(themes)
    currentDepth=1
    iterators=enum_dfs_iterator_opt_depthmax([tree],configuration,0,depthmax)
    for arrRet in iterators:
        yield arrRet,[themesMAP.get(key,'-') for key in arrRet]