'''
Created on 25 nov. 2016

@author: Adnene
'''
from _collections import deque
from copy import deepcopy
import itertools


def flattenThemesTree(themes):
    arrNew=[]
    for x in themes :
        arrNew.append(x)
        s= x.split('.')
        for i in range(len(s[:-1])) :
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
    newThemes=flattenThemesTree(themesMAP.keys())
    themes=newThemes[:]
    actualCount=0
    tree={'value':'','description':'','children':[]}
    while not len(newThemes)==0 :
        for x in themes:
            if (x.count('.') == actualCount):
                index=0
                countPoint=x.count('.')
                splitted=x.split('.')
                subtree=tree
                currentx=''
                while index<countPoint:
                    currentx+=str(splitted[index])+'.'
                    subtreeChildren=[v['value'] for v in subtree['children']]
                    subtreeChild=subtreeChildren.index(currentx[:-1])
                    subtree=subtree['children'][subtreeChild]
                    index+=1

                newNode={'value':x,'description':themesMAP.get(x,'-'),'children':[]}
                newThemes.remove(x)
                subtree['children'].append(newNode)
        themes=newThemes[:]
        actualCount+=1
    return tree,themesMAP

def BFS(queue,skip_list=[]):
    if len(queue)>0:
        v=queue.popleft()
        if not (v['value'] in skip_list):
            for w in v['children']:
                queue.append(w)
            yield v['value']
        for v2 in BFS(queue,skip_list):
            yield v2




def childrens_dfs(subtree,value,childs):
    if subtree['value']==value :
        mychilds=[v['value'] for v in subtree['children']]
        childs.extend(mychilds)
        for item in subtree['children']:
            childrens_dfs(item,item['value'],childs)

    else :
        mychilds=[v['value'] for v in subtree['children']]
        for item in subtree['children']:
                childrens_dfs(item,value,childs)

           
                
def childrens(tree,value):
    childsToReturn=[]
    childrens_dfs(tree,value,childsToReturn)
    return childsToReturn

def childrens_dfs_direct(subtree,value,childs):
    if subtree['value']==value :
        mychilds=[v['value'] for v in subtree['children']]
        childs.extend(mychilds)
    else :
        for item in subtree['children']:
                childrens_dfs_direct(item,value,childs)

def childrens_direct(tree,value):
    childsToReturn=[]
    childrens_dfs_direct(tree,value,childsToReturn)
    return childsToReturn

def mychildrens(subtree):
    return [node for node in subtree['children']]

def values(trees):
    return [tree['value'] for tree in trees]

def mychildrens_values(subtree):
    return [node['value'] for node in subtree['children']]


# def childrens_set(tree,themes_arr):
#     childrens_all=[]
#     for i in range(len(themes_arr)):
#         childrens_all.append([themes_arr[i]]+childrens_direct(tree,themes_arr[i]))
#     possibleChilds=[]
#     for subset in itertools.product(*childrens_all):
#         possibleChilds.append(list(subset))
# 
#     newPosChilds=[]
#     for k in range(len(possibleChilds)):
#         posChild=possibleChilds[k]
#         #print posChild
# 
#         if (not any ((posChild[item1]>posChild[item2]) or  posChild[item2] in childrens_direct(tree,posChild[item1]) for item1 in range(len(posChild)-1) for item2 in range(item1+1,len(posChild)))) :
#             newPosChilds.append(posChild)
# 
#     newPosChilds=newPosChilds[1:]    
#     return newPosChilds


def childrens_set(tree,themes_arr,refinement_index=0):
    childrens_all=[]
    for i in range(len(themes_arr)):
        childrens_all.append(childrens_direct(tree,themes_arr[i]))
    possibleChilds=[]

    possibleIterables=[]

    indexDifferents=[]
    valuesDifferents=[]
    for k in range(len(themes_arr)) :
        
        if themes_arr[k] in valuesDifferents:
            indexDifferents[valuesDifferents.index(themes_arr[k])].append(k)
        else :
            indexDifferents.append([k])
            valuesDifferents.append(themes_arr[k])

    
    for indexes in indexDifferents:
        possibleIter=[childrens_all[t] if t in indexes and refinement_index == indexes[0] else [themes_arr[t]] for t in range(len(themes_arr))]
        possibleIterables.append(possibleIter)

    for possibleIter in possibleIterables :

        for subset in itertools.product(*possibleIter):
            
            possibleChilds.append(list(subset))

    newPosChilds=[]
    for k in range(len(possibleChilds)):
        posChild=possibleChilds[k]
        #print posChild

        if (not any ((posChild[item1]>posChild[item2]) or  posChild[item2] in childrens_direct(tree,posChild[item1]) for item1 in range(len(posChild)-1) for item2 in range(item1+1,len(posChild)))) :
            if not posChild ==themes_arr:
                newPosChilds.append(posChild)

    #newPosChilds=newPosChilds[1:]
    return newPosChilds


def childrens_set_opt(trees,refinement_index=0):
    childrens_all=[]
    current_depth=len(trees)
    themes_arr=[tree['value'] for tree in trees]
    for i in range(current_depth):
        childrens_all.append(mychildrens(trees[i]))
    possibleChilds=[]

    possibleIterables=[]

    indexDifferents=[]
    valuesDifferents=[]
    for k in range(current_depth) :
        
        if themes_arr[k] in valuesDifferents:
            indexDifferents[valuesDifferents.index(themes_arr[k])].append(k)
        else :
            indexDifferents.append([k])
            valuesDifferents.append(themes_arr[k])

    
    for indexes in indexDifferents:
        possibleIter=[childrens_all[t] if t in indexes and refinement_index == indexes[0] else [trees[t]] for t in range(current_depth)]
        possibleIterables.append(possibleIter)

    for possibleIter in possibleIterables :

        for subset in itertools.product(*possibleIter):
            
            possibleChilds.append(list(subset))

    newPosChilds=[]
    for k in range(len(possibleChilds)):
        posChild=possibleChilds[k]
        #print posChild

        if (not any ((posChild[item1]['value']>posChild[item2]['value']) or  posChild[item2]['value'] in mychildrens_values(posChild[item1]) for item1 in range(len(posChild)-1) for item2 in range(item1+1,len(posChild)))) :
            if not values(posChild) ==themes_arr:
                newPosChilds.append(posChild)

    #newPosChilds=newPosChilds[1:]
    return newPosChilds

def possible_sub_patterns(pattern):
    toRet=[]
    for width in range(1,len(pattern)+1):
        for comb in itertools.combinations(range(len(pattern)),width):
            index_choosen=list(comb)
            subPatternToCheck=[pattern[t] for t in index_choosen]
            toRet.append(subPatternToCheck)
    return toRet

# def enum_dfs_iterator(tree,themes_arr,parentvalue,configuration):
#     if not (themes_arr in configuration['skip_list']):
#         if not any(themes_arr[i]==themes_arr[j] for i in range(len(themes_arr)-1) for j in range(i+1,len(themes_arr))):
#             yield themes_arr,parentvalue
#         
#         if not (themes_arr in configuration['skip_list']):
#             for child in childrens_set(tree,themes_arr[:]):
#                 if not (themes_arr in configuration['skip_list']):
#                     for val,parentvalue in enum_dfs_iterator(tree,child,themes_arr[:],configuration):
#                         if not (themes_arr in configuration['skip_list']) and (not val in configuration['skip_list']):
#                             yield val,parentvalue

def enum_dfs_iterator(tree,themes_arr,configuration,refinement_index=0):
    if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
        if not any(themes_arr[i]==themes_arr[j] for i in range(len(themes_arr)-1) for j in range(i+1,len(themes_arr))):
            yield themes_arr
        if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
            for pos_refinement in range(refinement_index,len(themes_arr)) : 
                if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
                    for child in childrens_set(tree,themes_arr[:],pos_refinement):
                        if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
                            for val in enum_dfs_iterator(tree,child,configuration,pos_refinement):
                                if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) and not any(x in possible_sub_patterns(val) for x in configuration['skip_list']):
                                    yield val

def enum_dfs_iterator_opt(trees,configuration,refinement_index=0):
    themes_arr=[tree['value'] for tree in trees]
    if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
        if not any(themes_arr[i]==themes_arr[j] for i in range(len(themes_arr)-1) for j in range(i+1,len(themes_arr))):
            yield themes_arr
        if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
            for pos_refinement in range(refinement_index,len(themes_arr)) : 
                if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
                    for subtrees in childrens_set_opt(trees,pos_refinement):
                        if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) :
                            for val in enum_dfs_iterator_opt(subtrees,configuration,pos_refinement):
                                if not any(x in possible_sub_patterns(themes_arr) for x in configuration['skip_list']) and not any(x in possible_sub_patterns(val) for x in configuration['skip_list']):
                                    yield val

def subtreesOf(tree,value):
    childsToReturn=[value]
    childrens_dfs(tree,value,childsToReturn)
    
    return childsToReturn


def directSubtreesOf(tree):
    mytree={'value':tree['value'],'description':tree['description'],'children':[]}
    #childsToReturn=[tree['value']]
    for child in tree['children'] :
        newchild={}
        newchild={'value':child['value'],'description':child['description'],'children':[]}
        mytree['children'].append(newchild)
    
    return mytree


def possibleFathers(theme):
    splitted = theme.split('.')
    ret=[]
    for arr in [splitted[0:j+1] for j in range(0,len(splitted)-1)]:
        father=''
        for item in arr:
            father+=item+'.'
        father=father[:-1]
        ret.append(father)
    return ret


def possibleFathers_set(arr_themes):
    ret=[]
    fathers_arr=[possibleFathers(theme) for theme in arr_themes]
    for subset in itertools.product(*fathers_arr):
        ret.append(list(subset))
    return ret







def DFS_lookup(value,subtree):
    if value == subtree['value'] :
        return True
    else :
        bools=False
        for item in subtree['children']:
            bools = bools or DFS_lookup(value,item)
    return bools



def bfs_themes(themes):
    tree=createTreeOutOfThemes(themes)
    queue_tree=deque([tree])
    return BFS(queue_tree)


def DFS(subtree,configuration):
    yield subtree['value']
    for child in subtree['children']:
        #print configuration['skip_list']
        if not (subtree['value'] in configuration['skip_list']):
            for val in DFS(child,configuration):
                yield val
 
def DFS_depth(subtree,configuration,parentvalue):
    if not ([subtree['value']] in configuration['skip_list']):
        yield subtree['value'],parentvalue
        if not ([subtree['value']]in configuration['skip_list']):
            for child in subtree['children']:
                if not ([subtree['value']] in configuration['skip_list']):
                    for val,parentvalue in DFS_depth(child,configuration,subtree['value']):
                        if not ([subtree['value']] in configuration['skip_list']) and not ([val] in configuration['skip_list']) :
                            yield val,parentvalue     
                            
def DFS_depth_withoutParent(subtree,configuration):
    if not ([subtree['value']] in configuration['skip_list']):
        yield subtree['value']
        if not ([subtree['value']]in configuration['skip_list']):
            for child in subtree['children']:
                if not ([subtree['value']] in configuration['skip_list']):
                    for val in DFS_depth_withoutParent(child,configuration):
                        if not ([subtree['value']] in configuration['skip_list']) and not ([val] in configuration['skip_list']) :
                            yield val          
            
def dfs_themes(themes,configuration):
    tree=createTreeOutOfThemes(themes)
    return DFS(tree,configuration)

def dfs_themes_depth(tree,configuration,depth): #iterations_depthmax(allthemes,{'skip_list':[['1.10%'], ['1.20%']]},1)
    
    iterators=[]
    arrRet=[]
    arrParents=[]
    for i in range(depth):
        iterators.append(DFS_depth(tree,configuration,''))
        if i>0 :
            arrRet.append(next(iterators[i],[None])[0])
            arrRet[i]=next(iterators[i],[None])[0]
            arrParents.append('')
        else :
            arrRet.append('')
            arrParents.append('')
    stop=False
    parentsOfActualTrees=[]
    childrensOfActualTrees=[]
    childrensOfAll=childrens(tree, '')
    for i in range(depth):
        parentsOfActualTrees.append('')
        childrensOfActualTrees.append(childrensOfAll)    
        
    while not stop :

        index=0
        nexter=next(iterators[0],[None,None])
        arrRet[0]=nexter[0]
        arrParents[0]=nexter[1]
        
        while arrRet[index] is None:
            if ((index+1)>=depth) :
                stop=True
                break
            
            nexter=next(iterators[index+1],[None,None])
            arrRet[index+1]=nexter[0]
            arrParents[index+1]=nexter[1]
            
            iterators[index]=DFS_depth(tree,configuration,'')
            
            nexter=next(iterators[index],[None,None])
            arrRet[index]=nexter[0]
            arrParents[index]=nexter[1]
            
            index+=1
            
        if stop :
            break
        
        if not all((not arrRet[i]=='') and arrRet[i]<arrRet[i+1] for i in range(depth-1)): #lexicographic order in pattern
            continue
        
        #smartly choose which  index to do next it must be as far as possible    
            
        for k in range(depth):
            if not parentsOfActualTrees[k]==arrRet[k] :
                childrensOfActualTrees[k]=childrens(tree, arrRet[k])
                parentsOfActualTrees[k]=arrRet[k]
                
        
        
        partenthoodRelationship=any(not (arrRet[fils2]=='') and (arrRet[fils1] in  childrensOfActualTrees[fils2]) for fils2 in range(depth-1) for fils1 in range(fils2+1,depth))
         
        #partenthoodRelationship=any(not (arrRet[fils2]=='') and (arrRet[fils2] in possibleFathers(arrRet[fils1])) for fils1 in range(depth-1) for fils2 in range(fils1+1,depth))
         
        if partenthoodRelationship :
            continue
        

        
        
        
        #print arrParents, '->',arrRet#, '---', any(x in possibleFathers_set(arrRet) for x in reversed(configuration['skip_list']))
        if (arrParents in configuration['skip_list']) :
            configuration['skip_list'].append(arrRet[:])
            continue  
        
        #Purpose is to find a subset of the pattern such as the subset_pattern is a child of pattern_father who was discarded before
        patternNonValid=False
        for width in range(2,depth+1):
            for subset in itertools.combinations(range(depth), width):
                indexes_choosen=list(subset)
                generators=[[arrRet[t],arrParents[t]] for t in indexes_choosen] 
                for product in itertools.product(*generators): #*generators pass the arrays of generators as parameters and not only generators 
                    subPatternToCheck=list(product)
                    if subPatternToCheck in configuration['skip_list']:
                        patternNonValid=True
                        configuration['skip_list'].append(arrRet[:])
                        break
                
                if patternNonValid:
                    break
                
            if patternNonValid :
                break
                    
        if patternNonValid:
            continue
        
        yield arrRet
        
    for i in range(depth):
        arrRet[i]=None  
        
        
        
def dfs_themes_depth_new(tree,configuration,depth): #iterations_depthmax(allthemes,{'skip_list':[['1.10%'], ['1.20%']]},1)
    trees=[]
    arrRet=[]
    for i in range(depth):
        #trees.append(tree)
        arrRet.append('')
        
    #iterators=enum_dfs_iterator(tree, arrRet, arrParents, configuration)
    #iterators=enum_dfs_iterator(tree, arrRet, configuration)
    iterators=enum_dfs_iterator_opt(trees, configuration)
    for nexter in iterators :
        arrRet=nexter
        #arrParents=nexter[1]
        #print arrParents,'->',arrRet
        yield arrRet
        
#     while not stop :
# 
#         nexter=next(iterators,[None,None])
#         arrRet=nexter[0]
#         arrParents=nexter[1]
#         if arrRet is None:
#             stop=True
#             break
#             
#         yield arrRet
        
#     for i in range(depth):
#         arrRet[i]=None

#{'pattern': ['8', '4.10', '3.70'], 'valid': False}

def dfs_themes_depth_inner_recursive(tree,configuration,depth,iterators,parentsOfActualTrees,childrensOfActualTrees,stop,arrRetOrigin,arrParentsOrigin):
    if not stop :
        index=0
        arrRet=arrRetOrigin[:]
        arrParents=arrParentsOrigin[:]
        
        nexter=next(iterators[0],[None,None])
        arrRet[0]=nexter[0]
        arrParents[0]=nexter[1]
        
        while arrRet[index] is None:
            if ((index+1)>=depth) :
                stop=True
                break
            nexter=next(iterators[index+1],[None,None])
            arrRet[index+1]=nexter[0]
            arrParents[index+1]=nexter[1]
            iterators[index]=DFS_depth(tree,configuration,'')
            nexter=next(iterators[index],[None,None])
            arrRet[index]=nexter[0]
            arrParents[index]=nexter[1]
            index+=1
            
        if not stop :
            
        
            bool_order=False
            falsePattern=True
            falsePattern2=True
            
            while (not bool_order or falsePattern or falsePattern2):
                bool_order=True #constraint of non redunduncty assume a lexicographic order between themes values
                for i in range(depth-1):
                    bool_order= bool_order and (arrRet[i]>arrRet[i+1])
                
                
                falsePattern=False
                for fils1 in range(depth-1):
                    for fils2 in range(fils1+1,depth):
                        if (arrRet[fils1]==arrRet[fils2]):
                            falsePattern=True
                            break
                    if falsePattern :
                        break
                    
                
                
                
                for k in range(depth):
                    if not parentsOfActualTrees[k]==arrRet[k] :
                        childrensOfActualTrees[k]=childrens(tree, arrRet[k])
                        parentsOfActualTrees[k]=arrRet[k]
                    
                
                
                falsePattern2=False
                for fils1 in range(depth-1):
                    for fils2 in range(fils1+1,depth):
                        if (not (arrRet[fils2]=='')) and (arrRet[fils1] in  childrensOfActualTrees[fils2]):
                            falsePattern2=True
                            break
                                 
                    if falsePattern2 :
                        break
                
                
                if (not bool_order or falsePattern or falsePattern2):
                
                    
                    index=0
                    nexter=next(iterators[0],[None,None])
                    arrRet[0]=nexter[0]
                    arrParents[0]=nexter[1]
                    
                    while arrRet[index] is None:
                        
                        if ((index+1)>=depth) :
                            stop=True
                            break
                        nexter=next(iterators[index+1],[None,None])
                        arrRet[index+1]=nexter[0]
                        arrParents[index+1]=nexter[1]
                        iterators[index]=DFS_depth(tree,configuration,'')
                        nexter=next(iterators[index],[None,None])
                        arrRet[index]=nexter[0]
                        arrParents[index]=nexter[1]
                        index+=1
                
                
                
            #print arrParents
            
            #if not (arrParents in configuration['skip_list']) :
            #print arrParents, '->',arrRet
            yield arrRet
            
            arrRetFather=arrRet[:]
            arrParentsFather=arrParents[:]
            for arrRetChild in dfs_themes_depth_inner_recursive(tree,configuration,depth,iterators,parentsOfActualTrees,childrensOfActualTrees,stop,arrRetFather,arrParentsFather):    
                #print arrRetChild,arrRetFather,arrParentsFather
                yield arrRetChild
                

def dfs_themes_depth_recursive(tree,configuration,depth): #iterations_depthmax(allthemes,{'skip_list':[['1.10%'], ['1.20%']]},1)

    iterators=[]
    arrRet = []
    arrParents=[]
    for i in range(depth):
        iterators.append(DFS_depth(tree,configuration,''))
        if i>0 :
            arrRet.append(next(iterators[i],[None])[0])
            arrRet[i]=next(iterators[i],[None])[0]
            arrParents.append('')
        else :
            arrRet.append('')
            arrParents.append('')
    stop=False
    parentsOfActualTrees=[]
    childrensOfActualTrees=[]
    childrensOfAll=childrens(tree, '')
    for i in range(depth):
        parentsOfActualTrees.append('')
        childrensOfActualTrees.append(childrensOfAll)    
        
    
    iters=dfs_themes_depth_inner_recursive(tree,configuration,depth,iterators,parentsOfActualTrees,childrensOfActualTrees,stop,arrRet,arrParents)
    
    arrRet=next(iters,None)
    while arrRet is not None :
        yield arrRet
        arrRet=next(iters,None)
    
    
    
# def dfs_themes_depthOLD(tree,configuration,depth): #iterations_depthmax(allthemes,{'skip_list':[['1.10%'], ['1.20%']]},1)
#     
#     iterators=[]
#     arrRet=[]
#     arrParents=[]
#     for i in range(depth):
#         iterators.append(DFS_depth(tree,configuration,''))
#         if i>0 :
#             arrRet.append(next(iterators[i],[None])[0])
#             arrRet[i]=next(iterators[i],[None])[0]
#             arrParents.append('')
#         else :
#             arrRet.append('')
#             arrParents.append('')
#     stop=False
#     parentsOfActualTrees=[]
#     childrensOfActualTrees=[]
#     childrensOfAll=childrens(tree, '')
#     for i in range(depth):
#         parentsOfActualTrees.append('')
#         childrensOfActualTrees.append(childrensOfAll)    
#         
#     while not stop :
# 
#         index=0
#         nexter=next(iterators[0],[None,None])
#         arrRet[0]=nexter[0]
#         arrParents[0]=nexter[1]
#         
#         while arrRet[index] is None:
#             if ((index+1)>=depth) :
#                 stop=True
#                 break
#             
#             nexter=next(iterators[index+1],[None,None])
#             arrRet[index+1]=nexter[0]
#             arrParents[index+1]=nexter[1]
#             
#             iterators[index]=DFS_depth(tree,configuration,'')
#             
#             nexter=next(iterators[index],[None,None])
#             arrRet[index]=nexter[0]
#             arrParents[index]=nexter[1]
#             
#             index+=1
#             
#         if stop :
#             break
#         
# #         reversed_skip=reversed(configuration['skip_list'])
# #         if any(x in possibleFathers_set(arrRet) for x in reversed_skip):
# #             continue
#             
# #         bool_order=True #constraint of non redunduncty assume a lexicographic order between themes values
# #         for i in range(depth-1):
# #             bool_order= bool_order and (arrRet[i]>arrRet[i+1])
# #         if (not bool_order) :
# #             continue
# #         
#         if not all(arrRet[i]>arrRet[i+1] for i in range(depth-1)): #lexicographic order in pattern
#             continue
#         
# #         falsePattern=False
# #         for fils1 in range(depth-1):
# #             for fils2 in range(fils1+1,depth):
# #                 if (arrRet[fils1]==arrRet[fils2]):
# #                     falsePattern=True
# #                     break
# #             if falsePattern :
# #                 break
#             
# #         if any(arrRet[fils1]==arrRet[fils2] for fils1 in range(depth-1) for fils2 in range(fils1+1, depth)) :
# #             continue
#             
#         
#         
#         
#         for k in range(depth):
#             if not parentsOfActualTrees[k]==arrRet[k] :
#                 childrensOfActualTrees[k]=childrens(tree, arrRet[k])
#                 parentsOfActualTrees[k]=arrRet[k]
#                 
#         
#         
#         falsePattern=False
#         for fils1 in range(depth-1):
#             for fils2 in range(fils1+1,depth):
#                 if (not (arrRet[fils2]=='')) and (arrRet[fils1] in  childrensOfActualTrees[fils2]):
#                     falsePattern=True
#                     break
#                          
#             if falsePattern :
#                 break
#          
#         if falsePattern :
#             continue
#         
# #         for k in range(depth):
# #             if arrParents[k]=='':
# #                 arrParents[k]=arrRet[k]
#         
#         
#         
#         
#         
#         #print arrParents, '->',arrRet#, '---', any(x in possibleFathers_set(arrRet) for x in reversed(configuration['skip_list']))
#         if (arrParents in configuration['skip_list']) :
#             configuration['skip_list'].append(arrRet[:])
#             continue  
#         
#         #Purpose is to find a subset of the pattern such as the subset_pattern is a child of pattern_father who was discarded before
#         patternNonValid=False
#         for width in range(2,depth+1):
#             for subset in itertools.combinations(range(depth), width):
#                 indexes_choosen=list(subset)
#                 
#                 
#                 generators=[[arrRet[t],arrParents[t]] for t in indexes_choosen] 
#                 
#                 
#                 #subPatternToCheck=[arrRet[t] if arrParents[t]=='' else arrParents[t]  for t in indexes_choosen]
#                 
#                 for product in itertools.product(*generators): #*generators pass the arrays of generators as parameters and not only generators 
#                     subPatternToCheck=list(product)
#                     if subPatternToCheck in configuration['skip_list']:
#                         patternNonValid=True
#                         configuration['skip_list'].append(arrRet[:])
#                         break
#                 
#                 if patternNonValid:
#                     break
#                 
#                 
#                 #print subPatternToCheck
#                  
#                 
#             if patternNonValid :
#                 break
#                  
#                  
#         if patternNonValid:
#             #print product
#             continue
#                 
#         
#         
#         yield arrRet
#         
#         
#     for i in range(depth):
#         arrRet[i]=None  
        
        
# def dfs_themes_depth_OLDOLD(themes,configuration,depth): #iterations_depthmax(allthemes,{'skip_list':[['1.10%'], ['1.20%']]},1)
#     
#     
#     tree=createTreeOutOfThemes(themes)
#     iterators=[]
#     arrRet=[]
#     arrRetChilds=[]
#     for i in range(depth):
#         iterators.append(DFS_depth(tree,configuration))
#         if i>0 :
#             nextitem=next(iterators[i],None)
#             nextitem=next(iterators[i],None)
#             arrRet.append(nextitem[0])
#             arrRet[i]=nextitem[0]
#             arrRetChilds[i]
#         else :
#             arrRet.append('')
#     stop=False
#     parentsOfActualTrees=[]
#     childrensOfActualTrees=[]
#     childrensChanged=[]
#     childrensOfAll=childrens(tree, '')
#     for i in range(depth):
#         parentsOfActualTrees.append('')
#         childrensOfActualTrees.append(childrensOfAll)    
#         childrensChanged.append(False)
#     
#     
#     
#     while not stop :
#         
#         
#         
#         
#         index=0
#         nextitem=next(iterators[0],[None])
#         arrRet[0]=nextitem[0]
#         
#         
#         while arrRet[index] is None:
#             if ((index+1)>=depth) :
#                 stop=True
#                 break
#             nextitem=next(iterators[index+1],[None])
#             arrRet[index+1]=nextitem[0]
#             iterators[index]=DFS_depth(tree,configuration)
#             nextitem=next(iterators[index+1],[None])
#             arrRet[index]=nextitem[0]
#             index+=1
#             
#         if stop :
#             break
#         
#         
#         
#             
#             
#         bool_order=True #constraint of non redunduncty assume an order between themes values
#         for i in range(depth-1):
#             bool_order= bool_order and (arrRet[i]>arrRet[i+1])
#         if (not bool_order) :
#             continue
#         
#         falsePattern=False
#         for fils1 in range(depth-1):
#             for fils2 in range(fils1+1,depth):
#                 if (arrRet[fils1]==arrRet[fils2]):
#                     falsePattern=True
#                     break
#             if falsePattern :
#                 break
#         if falsePattern :
#             continue
#             
#         
#         
#         
#         for k in range(depth):
#             if not parentsOfActualTrees[k]==arrRet[k] :
#                 childrensOfActualTrees[k]=childrens(tree, arrRet[k])
#                 parentsOfActualTrees[k]=arrRet[k]
#                 childrensChanged[k]=True
#             else :
#                 childrensChanged[k]=False
#         
#         
#         
#         falsePattern=False
#         for fils1 in range(depth-1):
#             for fils2 in range(fils1+1,depth):
#                 #verifyParenthood =  ( childrensChanged[fils1] or childrensChanged[fils2])
#                 #if verifyParenthood :
#                 if (not (arrRet[fils2]=='')) and (arrRet[fils1] in  childrensOfActualTrees[fils2]):
#                     falsePattern=True
#                     break
#                          
#             if falsePattern :
#                 break
#          
#         if falsePattern :
#             continue
#         
#         
#         
# #         new_items=configuration['new_items']
# #         new_item_set=set([item for sublist in configuration['new_items'] for item in sublist])
# #         
# #         skip_list=configuration['skip_list'] #set([item[:-1] for sublist in configuration['skip_list'] for item in sublist])
# #         skip_list_set=set(skip_list)
# #         skip_list_enhanced=set(skip_list_set)
# #         for item in new_item_set:
# #             skip_list_enhanced.add(item)#skip_list_enhanced=skip_list_enhanced.union(set(subtreesOf(tree,item)))
# #         configuration['new_items']=[]
# #         configuration['skip_list']=skip_list_enhanced
#         
# #         skip_pattern=False
# #         
# #         range_depth=range(depth)
# #         range_depth.reverse()
# #         
# #         for i in range_depth:
# #             skip_pattern = skip_pattern or ( arrRet[i] in (skip_list_enhanced)) #to discard a pattern based on skip_list each item must be in the subtree of one of the skip_list
# #             if skip_pattern :
# #                 break
# #         
# #         #print 'intermediate : ', arrRet#, 'i fucked ', i
# #         if i>0:
# #             arrRet[i]=next(iterators[i],None)
# #             
# #             for k in range(i):
# #                 iterators[k]=DFS_depth(tree,configuration)
# #                 arrRet[k]=next(iterators[k],None)
# # 
# #             
# #         if skip_pattern:
# #             continue
#         
# #         skip_pattern=False
# #         for item in itertools.combinations(arrRet,depth) :
# #             if  list(item) in configuration['skip_list'] :
# #                 skip_pattern=True
# #                 break
# #         if skip_pattern :
# #             continue
#         
#           
#         yield arrRet
#         
#         #new_items=configuration['new_items']
#         #new_item_set=set([item for sublist in configuration['new_items'] for item in sublist])
#         
#         #skip_list=configuration['skip_list'] #set([item[:-1] for sublist in configuration['skip_list'] for item in sublist])
#         #skip_list_set=set(skip_list)
#         #skip_list_enhanced=set(skip_list_set)
#         #for item in new_items:
#         #    configuration['skip_list'].append(item)#skip_list_enhanced=skip_list_enhanced.union(set(subtreesOf(tree,item)))
#         #configuration['new_items']=[]
#         #configuration['skip_list']=skip_list_enhanced
#         
#     for i in range(depth):
#         arrRet[i]=None        
    
    

def dfs_themes_depthmax(themes,configuration,depthmax):
    tree,themesMAP=createTreeOutOfThemes(themes)
    currentDepth=1#1
    #iters=dfs_themes_depth_new(tree,configuration,currentDepth)
#     for x in iters :
#         print x
    
    while currentDepth<=depthmax:
        
        iters=dfs_themes_depth_new(tree,configuration,currentDepth)
        arrRet=next(iters,None)
        while arrRet is not None :
            yield arrRet,[themesMAP.get(key,'-') for key in arrRet]
            arrRet=next(iters,None)
            if arrRet is None: 
                currentDepth+=1
                break
        
        
    
    #yield arrRet
    #return DFS(tree,configuration)

