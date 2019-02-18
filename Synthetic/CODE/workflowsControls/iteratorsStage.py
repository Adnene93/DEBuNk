'''
Created on 29 nov. 2016

@author: Adnene
'''

import math
from sys import stdout
from time import time
import unicodedata

from EMM_ENUMERATOR.enumerator_multiple_attributes import generic_enumerators, \
    generic_enumerators_subgroupBitwise
from EMM_ENUMERATOR.enumerator_nominal import enum_nominal_minimal_size_new
from EMM_ENUMERATOR.enumerator_numbers import enum_num_minimal_size
from EMM_ENUMERATOR.enumerator_themes import dfs_themes_depthmax_dfs
from EMM_GENERIC_ENUMERATOR.emm_generic_enumerator import generic_enumerators_top_k
from EMM_PADMIV.DSC_CLEANED import DSC, DSCFORPERF
from EMM_PADMIV.DSC_method import dsc_c_method, dsc_uuc_method, \
    dsc_c_methodWITHHEATMAP, dsc_uuc_method_HEATMAP
from EMM_PADMIV.emm_padmiv import generic_enumerators_top_k_cbo, \
    generic_enumerators_top_k_cbo_users, \
    generic_enumerators_top_k_cbo_users1_users2
from enumerators_and_subgroups.enumerator_multi_attributes_subgroups import generic_enumerators_dataset, \
    generic_enumerators_dataset_stats, \
    generic_enumerators_dataset_stats_two_cases, \
    generic_enumerators_dataset_stats_two_cases_new, \
    generic_enumerators_dataset_stats_two_cases_separated, \
    generic_enumerators_dataset_stats_two_cases_top_k, \
    generic_enumerators_dataset_stats_two_cases_top_k_NEW
from filterer.filter import filter_pipeline_obj
from util.matrixProcessing import getInnerMatrix, getCompleteMatrix



def yielderOnArray(array):
    for obj in array:
        yield obj

def yielder(array,outputs={}):
    for val in array :
        outputs['yielded_item']=val
        yield    outputs['yielded_item']
    outputs['yielded_item']='TERMINATED'
    

def workflowStage_simpleIterator( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'simpleIterator',
        'inputs': {
            'array':[]
        },
        'configuration': {
        },
        'outputs':{
            'yielded_item':''
            'yielded_index:'' 
        }
    }
    '''  
    
    
    index=0
    for val in inputs['array'] :
        outputs['yielded_item']=val
        outputs['yielded_index']=index
        index+=1
        yield outputs
    outputs['yielded_item']='TERMINATED'
    outputs['yielded_index']='TERMINATED'
    if not (outputs['yielded_item']=='TERMINATED') :
        yield outputs 
        

    
def workflowStage_iteratorsOnThemes_Depth( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'THEMES_ITERATOR',
        'type':'stringsHierarchyIterator_depth',
        'inputs': {
            'array':'THEMES_FILE_READER.outputs.dataset'#'THEMES_ARRAY_PROJECTER.outputs.column'#['4.15','4.15.05']#'columnGetter.outputs.array'
        },
        'configuration': {
            'skip_list':[],
            'depth_max':'PARAMETERS.outputs.depth' #max width of a pattern
        },
        'outputs':{
            'yielded_item':'',
            'yielded_description':'',
            'yielded_index':'' 
        }
    }
    '''
    depth_max= configuration.get('depth_max',None)
    iterator=dfs_themes_depthmax_dfs(inputs['array'],configuration,depth_max)#dfs_themes(inputs['array'],configuration)
    next(iterator)
    index=0
    for node in iterator :
        
        outputs['yielded_item']=node[0]#[str(x)+'%' for x in node]
        #outputs['yielded_description']=node[1]
        #we can add yielded_label
        outputs['yielded_index']=index
        index+=1
        yield outputs
        
        
def workflowStage_iteratorsOnNominal( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'nominal_iterator',
        'inputs': {
            'array':[] #sorted nominal attribute
            'minimal_size':#min width of a pattern if None do a complete exploration
        },
        'configuration': {
            'skip_list':[]
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'' 
        }
    }
    '''  
    index=0
    localConfiguration={}
    localConfiguration['skip_list']=configuration.get('skip_list',[])
    localConfiguration['minimal_size']=configuration.get('minimal_size',None)
    iterator=enum_nominal_minimal_size_new(inputs['array'],localConfiguration,localConfiguration['minimal_size'])
    for node in iterator :
        
        outputs['yielded_item']=node#[str(x)+'%' for x in node]
        outputs['yielded_index']=index
        index+=1
        yield outputs


def workflowStage_iteratorsOnNumerics( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'numeric_iterator',
        'inputs': {
            'array':[] #sorted nominal attribute
        },
        'configuration': {
            'skip_list':[]
            'minimal_size':#min larger authorized
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'' 
        }
    }
    '''  
    index=0
    localConfiguration={}
    localConfiguration['skip_list']=configuration.get('skip_list',[])
    localConfiguration['minimal_size']=configuration.get('minimal_size',None)
    iterator=enum_num_minimal_size(inputs['array'],localConfiguration,localConfiguration['minimal_size'])  
    for node in iterator :
        
        outputs['yielded_item']=node#[str(x)+'%' for x in node]
        outputs['yielded_index']=index
        index+=1
        yield outputs
        

def workflowStage_iteratorsOnMultipeAttributes(
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ):
    '''
    {
    
        'id':'stage_id',
        'type':'multiple_attributes_iterator',
        'inputs': {
            'array_data':[],
            'attibutes_types' : [],
            'depth_max' : None
        },
        'configuration': {
            'skip_list':[]
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'' 
        }
    }
    '''  
    localConfiguration={}
    localInputs={}
    #localConfiguration['skip_list']=configuration.get('skip_list',[])
    
    localInputs['array_data']=inputs.get('array_data',[])
    localInputs['attibutes_types']=inputs.get('attibutes_types',[])
    localInputs['depth_max']=inputs.get('depth_max',None)
    
    iterator=generic_enumerators(localInputs['array_data'],localInputs['attibutes_types'],configuration,localInputs['depth_max']) 
    next(iterator)
    index=0
    for pattern,description in iterator :
        outputs['yielded_item']=pattern
        outputs['yielded_description']=description
        outputs['yielded_index']=index
        index+=1
        yield outputs
        
def workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise(
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ):
    '''
    {
    
        'id':'stage_id',
        'type':'multiple_attributes_iterator_sgbitwise',
        'inputs': {
            'array_data':[],
            'attibutes_types' : [],
            'depth_max' : None
        },
        'configuration': {
            'skip_list':[],
            'bitwise':[]
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'' 
        }
    }
    '''  
    localConfiguration={}
    localInputs={}
    #localConfiguration['skip_list']=configuration.get('skip_list',[])
    
    localInputs['array_data']=inputs.get('array_data',[])
    localInputs['attibutes_types']=inputs.get('attibutes_types',[])
    localInputs['depth_max']=inputs.get('depth_max',None)
    
    iterator=generic_enumerators_subgroupBitwise(localInputs['array_data'],localInputs['attibutes_types'],configuration,localInputs['depth_max']) 
    next(iterator)
    index=0
    for pattern,description,bitwise in iterator :
        outputs['yielded_item']=pattern
        outputs['yielded_description']=description
        outputs['yielded_index']=index
        outputs['yielded_bitwise']=bitwise
        index+=1
        yield outputs
    


def organize_matrix(pairwiseStatistics):
    mat_pattern=pairwiseStatistics[1] 
    
    mat_ref=pairwiseStatistics[0] 
    innerMatrix,rower,header=getInnerMatrix(mat_pattern)
    rower=[unicodedata.normalize('NFD', unicode(str(rower[k]),'iso-8859-1')).encode('ascii', 'ignore') for k in sorted(rower)]
    header=[unicodedata.normalize('NFD', unicode(str(header[k]),'iso-8859-1')).encode('ascii', 'ignore')  for k in sorted(header)] 
    import pandas as pd
    import scipy.spatial.distance as ssd
    from  scipy.cluster.hierarchy import linkage
    from scipy.cluster import hierarchy
    
    nba=pd.DataFrame(innerMatrix,index=rower,columns=header,dtype=float)
    header_new=header[:]
    rower_new=rower[:]
    matrix=nba.as_matrix()
    
    matrix=[[1-x for x in row] for row in matrix]
    
    isSquare=True
    if len(matrix)<>len(matrix[0]):
        isSquare=False
    if isSquare:
        for index,row in enumerate(matrix) :
            for column,val in enumerate(row) :
                if not innerMatrix[column][index] == matrix[index][column] :
                    if (math.isnan(matrix[index][column])) :
                        matrix[index][column]=1.
                    #print innerMatrix[index][column],'-',innerMatrix[column][index] ##ERREURE d'ARRONDIE
                    else :
                        matrix[index][column]=matrix[column][index] ##ERREURE d'ARRONDIE
                if index==column:
                    matrix[index][column]=0.
    
    
    
        
        distArray = ssd.squareform(matrix)    
        linkageMatrix=linkage(distArray, 'average')
        
        cuttreeclusters=sorted([(i,t) for (i,t) in enumerate(hierarchy.fcluster(linkageMatrix,0.2,'distance'))],key=lambda x : x[1])
        clusters={}
        for i,c in cuttreeclusters:
            if not clusters.has_key(c):
                clusters[c]=[]
            clusters[c].append(i)
        #print clusters
            
        cuttreeclustersSorted=[]
         
        pairs=[]
        for i in range(len(matrix)):
            row = matrix[i]
            for j in range(len(row)):
                pairs.append((i,j,row[j]))
        pairs=sorted(pairs,key=lambda x : x[2])
        visited=[]
        for c,c_elems in clusters.iteritems():
            for i,j,d in pairs:
                if i in c_elems and j in c_elems:
                    if i not in visited:
                        visited.append(i)
                        cuttreeclustersSorted.append((i,c))
                    if j not in visited:
                        visited.append(j)
                        cuttreeclustersSorted.append((j,c))
        
        rower_new=[rower[t[0]] for t in cuttreeclustersSorted]
        header_new=[header[t[0]] for t in cuttreeclustersSorted]

        nba=nba.reindex(index=rower_new,columns=header_new)
        
        
    else:
        cuttreeclustersSorted=[]
        pairs=[]
        for i in range(len(matrix)):
            row = matrix[i]
            for j in range(len(row)):
                pairs.append((i,sum(row)))
        pairs=sorted(pairs,key=lambda x : x[1])       
        visited=[]     
        for i,d in pairs:
            if i not in visited:
                visited.append(i)
                cuttreeclustersSorted.append((i,0))         
    
        rower_new=[rower[t[0]] for t in cuttreeclustersSorted]
        header_new=header[:]
        nba=nba.reindex(index=rower_new,columns=header_new)
    new_inner_matrix=nba.get_values().tolist()
    

    new_rower=list(nba.index)
    new_header=list(nba)
    new_rower_map={i:v for i,v in enumerate(new_rower)}
    new_header_map={i:v for i,v in enumerate(new_header)}
    new_mat_pattern=getCompleteMatrix(new_inner_matrix, new_rower_map, new_header_map)
    innerMatrix2,rower2,header2=getInnerMatrix(mat_ref)
    rower2=[unicodedata.normalize('NFD', unicode(str(rower[k]),'iso-8859-1')).encode('ascii', 'ignore') for k in sorted(rower2)]
    header2=[unicodedata.normalize('NFD', unicode(str(header[k]),'iso-8859-1')).encode('ascii', 'ignore')  for k in sorted(header2)] 
    nba2=pd.DataFrame(innerMatrix2,index=rower2,columns=header2,dtype=float)
    
    nba2=nba2.reindex(index=rower_new,columns=header_new)
    
    new_inner_matrix2=nba2.get_values().tolist()
    new_mat_ref=getCompleteMatrix(new_inner_matrix2, new_rower_map, new_header_map)
    return [new_mat_ref,new_mat_pattern]


def pattern_printer_one(pattern,types_attributes,names_attributes=[]):
    if len(pattern)==0:
        return '*'

    s=''
    for k in range(len(pattern)):
        if types_attributes[k]=='simple':
            if len(pattern[k])>1:
                if True:
                    s= '*'
                else:
                    s= str(pattern[k])
            else:
                s+= str(pattern[k][0])
        # elif types_attributes[k] in {'themes','hmt'}:

        #     s= printer_hmt(pattern[k])#str(pattern[k])+' '
        else:
            s= pattern[k]
    return s


def workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise_subgroups(
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ):
    '''
    {
    
        'id':'stage_id',
        'type':'multiple_attributes_iterator_sgbitwise_subgroups',
        'inputs': {
            'dataset':[]
            'attributes':[
                {
                    'name' : name_attribute,
                    'type' : 'themes' | 'numeric' | 'nominal',
                    'depthmax': None | 'or a value'
                }, ...
            ]
        },
        'configuration': {
            'skip_list':[],
            'bitwise':[]
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'' 
        }
    }
    '''  
    
    
    votes_attributes=inputs['votes_attributes']
    users_attributes=inputs['users_attributes']
    position_attribute=inputs['position_attribute']
    
    user1_scope=inputs.get("user_1_scope",[])
    user2_scope=inputs.get("user_2_scope",[])
    items_scope=inputs.get("items_scope",[])
    referential_scope=inputs.get("referential_scope",[])
    attributes=inputs['attributes']

    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    types_items=[a['type'] for a in subattributes_details_votes]
    types_users=[a['type'] for a in subattributes_details_users]
    
#     print items_scope
#     print type(items_scope[0]['inSet'][0])
#     raw_input('...')
    ####################"
    dataset=inputs['dataset']
    
    
    
    
#     filteredDataset1=filter_pipeline_obj(dataset, user1_scope)[0]
#       
#     filteredDataset2=filter_pipeline_obj(dataset, user2_scope)[0]
#     filteredDataset=filteredDataset1+filteredDataset2 if (user1_scope <> user2_scope) else filteredDataset1

    attr_users_nb=len([x for x in attributes if x['name'] in users_attributes])
    if True :
        iterator=DSC(dataset,attributes,configuration,items_scope,referential_scope,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#     if False :
#         if attr_users_nb==0:
#             #iterator=generic_enumerators_top_k_cbo(filteredDataset,inputs['attributes'],configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#             iterator=dsc_c_methodWITHHEATMAP(filteredDataset,inputs['attributes'],configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#         
#         else:
#             #OLD#iterator=generic_enumerators_top_k_cbo_users(filteredDataset,inputs['attributes'],configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#             
#             
#             #iterator=generic_enumerators_top_k_cbo_users1_users2(filteredDataset,inputs['attributes'],configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#             
#             iterator=dsc_uuc_method_HEATMAP(filteredDataset,inputs['attributes'],configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#     
    
    #next(iterator)
    index=0
    for pattern,description,pairwiseStatistics,quality,upper_bound,dossiers_voted,new_disposition in iterator :
        
        outputs['yielded_item']=pattern
        outputs['yielded_description']=description
        outputs['yielded_index']=index
        outputs['quality']=quality
        outputs['upper_bound']=upper_bound
        outputs['dossiers_voted']=dossiers_voted
        #outputs['yielded_bitwise']=bitwise
        
        ####################ORGANIZING HEAtMAPS####################
        if False:
            pairwiseStatistics=organize_matrix(pairwiseStatistics)
        
        
        ###########################################################
        
        outputs['pairwiseStatistics']=pairwiseStatistics
        
        #context_extent g_1_extent  g_2_extent
        #context    g_1 g_2
        new_disposition.update({
            # context_desc=sorted(pattern_printer_one([z],[json_config['description_attributes_objects'][ind][1]]) for ind,z in enumerate(eup[0]))
            #     g1_desc=sorted(pattern_printer_one([z],[json_config['description_attributes_individuals'][ind][1]]) for ind,z in enumerate(eup[1]))
            #     g2_desc=sorted(pattern_printer_one([z],[json_config['description_attributes_individuals'][ind][1]]) for ind,z in enumerate(eup[2]))

            'context':sorted(pattern_printer_one([z],[types_items[ind]]) for ind,z in enumerate(pattern[0])),
            'g_1':sorted(pattern_printer_one([z],[types_users[ind]]) for ind,z in enumerate(pattern[1])),#pattern_printer_one(pattern[1],types_items),
            'g_2':sorted(pattern_printer_one([z],[types_users[ind]]) for ind,z in enumerate(pattern[2])),#pattern_printer_one(pattern[2],types_items),
            'context_extent':new_disposition['votes_and_ids_considered'][3],
            'g_1_extent':new_disposition['votes_and_ids_considered'][0],
            'g_2_extent':new_disposition['votes_and_ids_considered'][1],
            'sim_context':-1,
            'sim_ref':-1,
            'quality':quality,

        })
        # outputs['disp_ext']={
        #     'context':pattern_printer_one(pattern[0],types_items),
        #     'g_1':pattern_printer_one(pattern[1],types_items),
        #     'g_2':pattern_printer_one(pattern[2],types_items),
        #     'context_extent':new_disposition['votes_and_ids_considered'][3],
        #     'g_1_extent':new_disposition['votes_and_ids_considered'][0],
        #     'g_2_extent':new_disposition['votes_and_ids_considered'][1],
        #     'sim_context':-1,
        #     'sim_ref':-1,
        #     'quality':quality,

        # }

        outputs['disp']=new_disposition
        outputs['context']=pattern_printer_one(pattern[0],types_items)
        outputs['g_1']=pattern_printer_one(pattern[1],types_users)
        outputs['g_2']=pattern_printer_one(pattern[2],types_users)
        outputs['context_extent']=new_disposition['votes_and_ids_considered'][3]
        outputs['g_1_extent']=new_disposition['votes_and_ids_considered'][0]
        outputs['g_2_extent']=new_disposition['votes_and_ids_considered'][1]
        index+=1
        yield outputs
        
        


def workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise_subgroups_tests(
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ):
    '''
    {
    
        'id':'stage_id',
        'type':'multiple_attributes_iterator_sgbitwise_subgroups',
        'inputs': {
            'dataset':[]
            'attributes':[
                {
                    'name' : name_attribute,
                    'type' : 'themes' | 'numeric' | 'nominal',
                    'depthmax': None | 'or a value'
                }, ...
            ]
        },
        'configuration': {
            'skip_list':[],
            'bitwise':[]
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'' 
        }
    }
    '''  
    
    
    votes_attributes=inputs['votes_attributes']
    users_attributes=inputs['users_attributes']
    position_attribute=inputs['position_attribute']
    vector_of_outcome=configuration.get('vector_of_outcome',None)
    user1_scope=inputs['user_1_scope']
    user2_scope=inputs['user_2_scope']
    
    ####################"
    dataset=inputs['dataset']
    
    
    reviews_dataset=configuration['reviews_dataset']
    items_dataset=configuration['items_dataset']
    users_dataset=configuration['users_dataset']
    
    filteredDataset1=filter_pipeline_obj(dataset, user1_scope)[0]
      
    filteredDataset2=filter_pipeline_obj(dataset, user2_scope)[0]
    filteredDataset=filteredDataset1+filteredDataset2 if (user1_scope <> user2_scope) else filteredDataset1
    configuration_execution= inputs['XP']
    
    print ''
    final_stats=[]
    
    considered=['attr_items_range','attr_users_range','upperbound','attr_aggregates_range','nb_items_range','nb_users_range','sigma_user_range','sigma_agg_range','sigma_item_range','sigma_quality_range','top_k_range','prunning_range','closed_range','similarity_measures','quality_measures']
    total=1
    for key in considered:
        total*=len(configuration_execution[key])
    index=0
    actu_config=[]
    last_config=[];last_time_spent=0;time_threshold=3600
    
    start=time()
    stdout.write('\rPercentage Done : '+'%.2f'%(index*100/float(total))+' %\t'+'Time elapsed : ' + '%.2f'%(time()-start)+'s')
    for closed_inst in configuration_execution['closed_range'] :
        for prunning_inst in configuration_execution['prunning_range'] :
            if prunning_inst and not closed_inst : continue
            for attr_item_inst in configuration_execution['attr_items_range']:
                for attr_users_inst in configuration_execution['attr_users_range']:
                    for attr_users_agg_inst in configuration_execution['attr_aggregates_range']:
                        for nb_items_inst in configuration_execution['nb_items_range']:
                            for nb_users_inst in configuration_execution['nb_users_range']:
                                for sigma_items_inst in configuration_execution['sigma_item_range']:
                                    for sigma_users_inst in configuration_execution['sigma_user_range']:
                                        for sigma_agg_users_inst in configuration_execution['sigma_agg_range']:   
                                            for sim_measure_inst in configuration_execution['similarity_measures']:
                                                for quality_measure_inst in configuration_execution['quality_measures']:
                                                    for sigma_quality_inst in configuration_execution['sigma_quality_range']:
                                                        for top_k_inst in configuration_execution['top_k_range']:
                                                            upperbound_range=configuration_execution['upperbound']
                                                            if not prunning_inst:
                                                                upperbound_range=[1]
                                                            
                                                            for upperboundType in upperbound_range:
                                                                
                                                                
                                                                
                                                                index+=1
                                                                input_new_attributes=[{'name':tupe[0],'type':tupe[1]} for tupe in attr_item_inst]
                                                                input_new_attributes+=[{'name':tupe[0],'type':tupe[1]} for tupe in attr_users_inst]
                                                                conf_new={
                                                                    'nb_dossiers_min':1,
                                                                    'threshold_pair_comparaison':sigma_items_inst,
                                                                    'cover_threshold':configuration['cover_threshold'], #SEE AGAINS HOW TO DECLARE CONDITIONS ON FREQUENT PATTERN,
                                                                    'quality_threshold':sigma_quality_inst,
                                                                    'top_k':top_k_inst,
                                                                    'iwant':quality_measure_inst,
                                                                    'upperbound':upperboundType,
                                                                    'closed':closed_inst,
                                                                    'pruning':prunning_inst,
                                                                    'nb_items':nb_items_inst,
                                                                    'nb_users':nb_users_inst,
                                                                    'aggregation_attributes_user1':attr_users_agg_inst,#['ageGroup'],#['NATIONAL_PARTY'],
                                                                    'aggregation_attributes_user2':attr_users_agg_inst,#['ageGroup'],#['NATIONAL_PARTY'],
                                                                    'nb_aggergation_min_user1':sigma_agg_users_inst,
                                                                    'threshold_nb_users_1':sigma_users_inst,
                                                                    'nb_aggergation_min_user2':sigma_agg_users_inst,
                                                                    'threshold_nb_users_2':sigma_users_inst,
                                                                    'comparaison_measure':sim_measure_inst,
                                                                    'reviews_dataset':reviews_dataset,
                                                                    'items_dataset':items_dataset,
                                                                    'users_dataset':users_dataset,
                                                                    'vector_of_outcome':vector_of_outcome
                                                                    
                                                                }
                                                                
                                                                actu_config=[conf_new['closed'],conf_new['pruning'],conf_new['upperbound']]
                                                                if actu_config==last_config and last_time_spent>=time_threshold: continue
                                                                
                                                                attr_users_nb=len([x for x in input_new_attributes if x['name'] in users_attributes])
#                                                                 if attr_users_nb==0:
#                                                                     iterator=dsc_c_method(filteredDataset,input_new_attributes,conf_new,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#                                                                 else:
#                                                                     iterator=dsc_uuc_method(filteredDataset,input_new_attributes,conf_new,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
#                                                                 
                                                                iterator=DSCFORPERF(filteredDataset,input_new_attributes,conf_new,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute)
                                                                
                                                                #next(iterator)
                                                               
                                                                
                                                                for pattern,description,pairwiseStatistics,quality,upper_bound,dossiers_voted in iterator :
                                                                    
                                                                    outputs['yielded_item']=pattern
                                                                    outputs['yielded_description']=description
                                                                    outputs['yielded_index']=index
                                                                    outputs['quality']=quality
                                                                    outputs['upper_bound']=True if index==1 else False
                                                                    outputs['dossiers_voted']=dossiers_voted
                                                                    #outputs['yielded_bitwise']=bitwise
                                                                    outputs['pairwiseStatistics']=pairwiseStatistics
                                                                    #yield outputs
                                                                    final_stats=final_stats+dossiers_voted
                                                                    #print dossiers_voted
                                                                    yield dossiers_voted
                                                                last_config=actu_config[:]
                                                                last_time_spent=dossiers_voted[0]['#timespent']
                                                                stdout.write('\rPercentage Done : '+'%.2f'%(index*100/float(total))+' %\t'+'Time elapsed : ' + '%.2f'%(time()-start)+'s')
                                                            
    outputs['dossiers_voted']=final_stats
    #yield outputs
            