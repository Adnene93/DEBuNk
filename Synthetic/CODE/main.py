'''
Created on 11 nov. 2016

@author: Adnene
'''
import argparse
import cProfile
import json
import os
from pprint import pprint
import pstats
import sys
from time import time

from setuptools import setup, find_packages

from EMM_ENUMERATOR.enumerator_themes2 import evaluate_themes_2
from EMM_PADMIV.DSC_method import get_votes_and_users_maps
from ENUMERATORS_ATTRIBUTES.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config, \
    enumerator_complex_from_dataset_new_config
from ENUMERATORS_ATTRIBUTES.enumerator_attribute_themes import similarity_between_descriptions

from util.csvProcessing import readCSVwithHeader, writeCSVwithHeader
from util.jsonProcessing import readJSON, writeJSON, readJSON_stringifyUnicodes
from workflows.workflowsProcessing_Pypy import process_workflow_recursive




find_packages()





if __name__ == '__main__':
#     print 'HI'
#     evaluate_themes_2(['1.10','1.20','2.10.01','2.10.02'],200)
#     
    
    #print evaluate_themes_2(['1', '1.10', '1.20', '1.30', '2.30', '4.20', '4.30', '4.40.01', '4.40.02', '4.40.03', '5.10', '5.20', '5.30.01', '5.30.02', '6.10', '6.20', '7.10', '7.20','7.30.01','7.30.02','7.30.03','8'],7)
    
    type_of_XP=sys.argv[1] if len(sys.argv)>1 else 'quals'
    type_of_XP=sys.argv[1] if len(sys.argv)>1 else 'floss'
    
    
    if type_of_XP=='perf' : #PERFORMANCE
        source_configuration_test=sys.argv[2]
        #source_configuration_test='C:\\Users\\Adnene\\Desktop\\XP_PKDD\\parliament\\All\\dummy\\question_1\\nb_items.json'
        print source_configuration_test
        data = readJSON_stringifyUnicodes(source_configuration_test)
        #dataset_file=os.getcwd()+"\\"+data['dataset_file']
        dataset_file=data.get('dataset_file','')
        dataset_arrayHeader=data['dataset_arrayHeader']
        dataset_numberHeader=data['dataset_numberHeader']
        votes_attributes=data['items_attributes']
        users_attributes=data['users_attributes']#+["MAJORITY"]
        outcome_attribute=data['outcome_attributes']
        items_file=data['items_file']
        users_file=data['users_file']
        reviews_file=data['reviews_file']
        vectors_of_outcome=data.get('vectors_of_outcome',None)
        source_destination=os.getcwd()+'\\'+(os.path.splitext(sys.argv[2])[0])+'.csv'
        destination=source_destination#data['destination']
        figure_destination=os.getcwd()+'\\'+(os.path.splitext(sys.argv[2])[0])+'.jpg'
        
        #print  source_destination#os.path.dirname(os.path.realpath(destination))
        #print(os.path.splitext("path_to_file")[0])
        print 'reading the test configuration and the data file ...'
        
        
        wokflow_parameters3=[
            {
        
                'id':'PARAMETERS',
                'type':'pipeliner',
                'inputs':{
                    
                },
                'configuration':{
                    'outputsFormula':{
                        
                        'repository':'C:\\Users\\Adnene\\Desktop\\WORKING_REPO',
                        'dataset':dataset_file,#movielens100YearsTrNew.csv', #FranceDetailedNew8New
                        
                        'country':['France','Germany','United Kingdom','Spain','Belgium','Italy','Portugal'],
                        'party':['Front national','Les R\xc3\xa9publicains'],#,'Les R\xc3\xa9publicains','Front national','Parti socialiste','Alternative fur Deutschland','Christlich Demokratische Union Deutschlands','Sozialdemokratische Partei Deutschlands','Bundnis 90/Die Grunen'
                        
                        'threshold_pair_comparaison':5,
                        'nb_dossiers_threshold':1,
                        
                        
                        'cover_threshold':2,
                        
                        'top_k':5,
                        'quality_threshold':0,
                        
                        'comparaison_measure':'AVG_RANKING_SIMPLE',#'AVG_RANKING_SIMPLE',
                        'iwant':'DISAGR_SUMDIFF',#'DISAGR_SUMDIFF',#'DISAGR_FROBENIUS_U1_U2',
                        'heatmap':False,
                        'heatmap_general':False,
                        'heatmap_diff':False,
                        'organizeHeatmaps':False,
                        
                        'pruning':True,
                        'vector_of_outcome':vectors_of_outcome,
                        'votes_attributes':votes_attributes,
                        'users_attributes':users_attributes,
                        'position_attribute':outcome_attribute,
                        
                        'aggregation_attributes':None,
                        'nb_aggregation_min':1,
                        
                        'user_1_scope':[
                        ],
                        
                        'user_2_scope':[
                        ],
    
                        'user1_sortDimension' :'USER1_occupation',
                        'user2_sortDimension' : 'USER2_occupation',
                        'user1_header' : 'USER1',
                        'user2_header' : 'USER2'
                        
                    }
                },
                'outputs':{
                    
                    
                }
            }
        ]
        
        workflow_prepdataset3=[
            {
                'id':'VOTES_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':"PARAMETERS.outputs.dataset"
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                },
                'execute':False 
            },
            
            {
                'id':'ITEMS_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':items_file
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                } 
            },
            {
                'id':'USERS_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':users_file
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                } 
            },
            {
                'id':'REVIEWS_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':reviews_file
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                } 
            }, 
            {
        
                'id':'log',
                'type':'log_printer',
                'inputs': {
                    'data' :'\nThe datasets were successfully loaded...\n'  
                },
                'configuration': {
                   'printType':'default'
                },
                'outputs':{
                }
            },                   
#             {
#         
#                 'id':'MAJORITY_COMPUTER', 
#                 'type':'majorities_computer',
#                 'inputs': {
#                     'dataset' :'VOTES_READER.outputs.dataset' 
#                 },
#                 'configuration': {
#                     'votes_attributes':'PARAMETERS.outputs.votes_attributes',
#                     'users_attributes':'PARAMETERS.outputs.users_attributes', 
#                     'users_majorities_attributes':'PARAMETERS.outputs.aggregation_attributes', 
#                     'position_attribute':'PARAMETERS.outputs.position_attribute',
#                     'nb_aggregation_min':'PARAMETERS.outputs.nb_aggregation_min',
#                 },
#                 'outputs':{
#                     'dataset':[]
#                 }
#             },
            {
        
                'id':'MAJORITY_COMPUTER_REVIEWS', 
                'type':'majorities_computer',
                'inputs': {
                    'dataset' :'REVIEWS_READER.outputs.dataset' 
                },
                'configuration': {
                    'votes_attributes':['PARAMETERS.outputs.votes_attributes[0]'],
                    'users_attributes':['PARAMETERS.outputs.users_attributes[0]'], 
                    'users_majorities_attributes':'PARAMETERS.outputs.aggregation_attributes', 
                    'position_attribute':'PARAMETERS.outputs.position_attribute',
                    'nb_aggregation_min':'PARAMETERS.outputs.nb_aggregation_min',
                    'vector_of_outcome':'PARAMETERS.outputs.vector_of_outcome'
                },
                'outputs':{
                    'dataset':[]
                }
            },
     
            ]
         
        workflow_patternsEnumerator3=[     
            {
         
                'id':'PATTERN_ENUMERATOR',
                'type':'multiple_attributes_iterator_sgbitwise_subgroups_tests',
                'inputs': {
                    'dataset':'MAJORITY_COMPUTER.outputs.dataset',#'WORKFLOW_PREPARED_DATASET.outputs.dataset',
                    'attributes':[
                        {'name' : 'genres', 'type' : 'themes'},
                        {'name' : 'releaseDate', 'type' : 'numeric'},
                    ],
                    
                    'user_1_scope':'PARAMETERS.outputs.user_1_scope',
                    
                    'user_2_scope':'PARAMETERS.outputs.user_2_scope',
                    
                    'votes_attributes':'PARAMETERS.outputs.votes_attributes',
                    'users_attributes':'PARAMETERS.outputs.users_attributes',
                    'position_attribute':'PARAMETERS.outputs.position_attribute',
                    'XP':data
                },
                'configuration': {
                    'nb_dossiers_min':'PARAMETERS.outputs.nb_dossiers_threshold',
                    'threshold_pair_comparaison':'PARAMETERS.outputs.threshold_pair_comparaison',
                    'cover_threshold':'PARAMETERS.outputs.cover_threshold', #SEE AGAINS HOW TO DECLARE CONDITIONS ON FREQUENT PATTERN,
                    'quality_threshold':'PARAMETERS.outputs.quality_threshold',
                    'top_k':'PARAMETERS.outputs.top_k',
                    'iwant':'PARAMETERS.outputs.iwant',
                    'pruning':'PARAMETERS.outputs.pruning' ,
                    'nb_items':2000,
                    'nb_users':2000,
                    'aggregation_attributes_user1':['ageGroup'],#['ageGroup'],#['NATIONAL_PARTY'],
                    'aggregation_attributes_user2':['ageGroup'],#['ageGroup'],#['NATIONAL_PARTY'],
                    'nb_aggergation_min_user1':1,
                    'threshold_nb_users_1':1,
                    'nb_aggergation_min_user2':1,
                    'threshold_nb_users_2':1,
                    'comparaison_measure':'PARAMETERS.outputs.comparaison_measure',
                    
                    'reviews_dataset':'MAJORITY_COMPUTER_REVIEWS.outputs.dataset',
                    'items_dataset':'ITEMS_READER.outputs.dataset',
                    'users_dataset':'USERS_READER.outputs.dataset',
                    
                    'vector_of_outcome':'PARAMETERS.outputs.vector_of_outcome'
                },
                'outputs':{
                    'yielded_item':'',
                    'yielded_index':'',
                    'yielded_description':'',
                    'pairwiseStatistics':[]
                }
            },
            {
        
                'id':'WORKFLOW_PATTERNS_ENUMERATOR', 
                'type':'pipeliner',
                'inputs':{
                    'pattern':'PATTERN_ENUMERATOR.outputs.yielded_item',
                    'description':'PATTERN_ENUMERATOR.outputs.yielded_description',
                    'pattern_index':'PATTERN_ENUMERATOR.outputs.yielded_index',
                    'dossiers_voted':'PATTERN_ENUMERATOR.outputs.dossiers_voted',
                    'quality':'PATTERN_ENUMERATOR.outputs.quality',
                    'upper_bound':'PATTERN_ENUMERATOR.outputs.upper_bound',
                    'pairwiseStatistics':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics'
                },
                'configuration':{
                    'outputsFormula':{
                        'data':{
                            'pattern_index':'pattern_index',
                            'pattern':'pattern',
                            'description':'description',
                            'quality':'quality',
                            'dossiers_voted':'dossiers_voted',
                            'upper_bound':'upper_bound',
                            
                        }
                        
                    }
                },
                'outputs':{
                    
                    
                }
            },
            {
                'id':'QUALITIES_CSV_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.data.dossiers_voted',#'FINAL_SYNCER.outputs.syncedData[0].dossiers_voted',
                    'destinationFile':destination
                },
                'configuration':{
                    'hasHeader': True, #,'qualityFrob'
                    'selectedHeader':['quality_measure','similarity_measure','upperbound_type',
                                      'attr_items', 'attr_users','attr_aggregate','#attr_items','#attr_users','#attr_aggregate',
                                      '#ratings','#items','#users1','#users2','#usersagg_1','#usersagg_2',  
                                      'sigma_context','sigma_u1','sigma_u2','sigma_agg_u1','sigma_agg_u2',
                                      'closed','prune',
                                      'sigma_quality','top_k',
                                      '#all_visited_context',    
                                      '#candidates', 
                                      '#init',
                                      '#timespent',
                                      '#patterns',
                                      'max_quality_found'
                                      ],
                    'flag_write_header':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.data.upper_bound'
                    },
                'outputs':{
                    
                } 
            },
            ]
            
        configuration_execution={
            'attr_items_range':'#attr_items',
            'attr_users_range':'#attr_users',
            'attr_aggregates_range':'#attr_aggregate',
            'nb_items_range':'#items',
            'nb_users_range':'#users1',
            'sigma_user_range':'sigma_u1',
            'sigma_agg_range':'sigma_agg_u1',
            'sigma_item_range':'sigma_context',
            'sigma_quality_range':'sigma_quality',
            'top_k_range':'top_k'
                
        }
        
        var_column=''
        for key,value in configuration_execution.iteritems():
            if len(data[key])>1:
                var_column=value
                
        
        #PlotPerf(source_configuration_test, var_column, activated, plot_bars, plot_time)
        workflowFinal3=wokflow_parameters3+workflow_prepdataset3+workflow_patternsEnumerator3
        process_workflow_recursive(workflowFinal3, verbose=False) 
    
    
    if type_of_XP=='fig' :    
        source_destination=sys.argv[2]
        var_column=sys.argv[3]
        activated=eval(sys.argv[4])
        try:
            rot=int(sys.argv[6])
        except:
            rot=0
        try:
            leg=bool(int(sys.argv[5]))
        except:
            leg=True
            
        figure_destination=os.getcwd()+'\\'+(os.path.splitext(sys.argv[2])[0])+'.jpg'    
        from plotters.plotPerformance import PlotPerf
        PlotPerf(source_destination, var_column, activated, True, True,show_legend=leg,rotateDegree=rot)
        #["BASELINE","DSC+UB1","DSC+UB2","CLOSED"]
        
    
    
    
    
    
    if type_of_XP=='qual'  : #QUALITATIVE
        repository='C:\\Users\\Adnene\\Desktop\\ExperimentsDB'    
        
        update_skip_list='list(pattern)' #sourceArr+
        
        source_configuration_test=sys.argv[2] if len(sys.argv)>1 else 'C:\Users\Adnene\Desktop\XP_ICDM\Qualitative\Yelp\qualitative.json'
        #source_configuration_test='C:\Users\Adnene\Desktop\TestingDSC\YELP\qualitative.json'
        print source_configuration_test
        data = readJSON_stringifyUnicodes(source_configuration_test)
        source_destination=os.getcwd()
        qualitiesFile='./'+(os.path.splitext(sys.argv[2])[0])+'.csv'
        qualities_extents_File='./'+(os.path.splitext(sys.argv[2])[0])+'_extents.csv'
        qualities_perf_File='./'+(os.path.splitext(sys.argv[2])[0])+'_perf.csv'
        #dataset_file=source_destination+"\\"+data['dataset_file']
        dataset_file=data.get('dataset_file','')
        
        items_file=data['items_file']
        users_file=data['users_file']
        reviews_file=data['reviews_file']
        
        
        dataset_arrayHeader=data['dataset_arrayHeader']
        dataset_numberHeader=data['dataset_numberHeader']
        votes_attributes=data['items_attributes']
        users_attributes=data['users_attributes']#+["MAJORITY"]
        outcome_attribute=data.get('outcome_attributes',None)
        
        vectors_of_outcome=data.get('vectors_of_outcome',None)
        if outcome_attribute is None : outcome_attribute=vectors_of_outcome[0]
        
        heatmap_yes=data['heatmaps']
        destination=source_destination
        
        attr_items=data["attr_items"]
        attr_users=data["attr_users"]
        attributes=[{'name' : x[0], 'type' : x[1]} for x in attr_items+attr_users ]
        
        attr_aggregates=data["attr_aggregates"]
        sigma_user=data["sigma_user"]
        sigma_agg=data["sigma_agg"]
        sigma_item=data["sigma_item"]
        sigma_quality=data["sigma_quality"]
        top_k=data["top_k"]
        similarity_measures=data["similarity_measures"]
        quality_measures=data["quality_measures"]
        upperbound=data["upperbound"]
        prunning=data["prunning"]
        user_1_scope=data.get("user_1_scope",[])
        user_2_scope=data.get("user_2_scope",[])
        items_scope=data.get("items_scope",[])
        referential_scope=data.get("referential_scope",[])
        
        
        
        nb_items=data.get("nb_items",None)
        nb_users=data.get("nb_users",None)
        ponderate_by_user=data.get("ponderate_by_user",None)
        ponderate_by_item=data.get("ponderate_by_item",None)
        only_square_matrix=data.get('only_square_matrix',False)
        method_aggregation_outcome=data.get("method_aggregation_outcome",'VECTOR_VALUES')
        
        cover_threshold=data.get("cover_threshold",1.)
        
        properties=[[items_file],[users_file],[reviews_file]]
        
        wokflow_parameters2=[
            {
        
                'id':'PARAMETERS',
                'type':'pipeliner',
                'inputs':{
                    
                },
                'configuration':{
                    'outputsFormula':{
                        
                        'repository':destination,#'C:\\Users\\Adnene\\Desktop\\WORKING_REPO',
                        'dataset':dataset_file,#'C:\\Users\\Adnene\\Desktop\\WORKING_REPO\\movielens100YearsTrNew.csv',#movielens100YearsTrNew.csv', #FranceDetailedNew8New
                        'properties':properties,
                        'country':['France','Germany','United Kingdom','Spain','Belgium','Italy','Portugal'],
                        'party':['Front national','Les R\xc3\xa9publicains'],#,'Les R\xc3\xa9publicains','Front national','Parti socialiste','Alternative fur Deutschland','Christlich Demokratische Union Deutschlands','Sozialdemokratische Partei Deutschlands','Bundnis 90/Die Grunen'
                        
                        'threshold_pair_comparaison':sigma_item,
                        'nb_dossiers_threshold':1,
                        
                        
                        'cover_threshold':cover_threshold,
                        
                        'top_k':top_k,#5,
                        'quality_threshold':sigma_quality,#0,
                        
                        'comparaison_measure':similarity_measures,#'AVG_RANKING_SIMPLE',#'AVG_RANKING_SIMPLE',
                        'iwant':quality_measures,#'DISAGR_SUMDIFF',#'DISAGR_SUMDIFF',#'DISAGR_FROBENIUS_U1_U2',
                        'heatmap':heatmap_yes,
                        'heatmap_general':False,
                        'heatmap_diff':False,
                        'organizeHeatmaps':False,
                        
                        'pruning':prunning,
                        'closed':True,
                        
                        
                        #8090     5528     3682     3271     96
                        #######################"
                        
    #                     'votes_attributes':['VOTEID','DOSSIERID','VOTE_DATE','VOTE_DATE_DETAILED','PROCEDURE_SUBJECT','PROCEDURE_TITLE','PROCEDURE_SUBTYPE','COMMITTEE','PROCEDURE_TYPE'],
    #                     'users_attributes':['EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','GENDER','AGE','MAJORITY'], 
    #                     'position_attribute':'USER_VOTE',  
                        
                        'votes_attributes':votes_attributes,#['movieID','movieTitle','releaseDate','genres','IMDBURL'],
                        'users_attributes':users_attributes,#['userid','age','ageGroup','gender','occupation','zipcode','MAJORITY'], 
                        'position_attribute':outcome_attribute,#'Rating',                                                               #'PARAMETERS.outputs.position_attribute'
                        'only_square_matrix':only_square_matrix,
                        'aggregation_attributes':None,#['NATIONAL_PARTY'],
                        'nb_aggregation_min':1,
                        
                        'user_1_scope':user_1_scope,
                        'items_scope':items_scope,
                        'referential_scope':referential_scope,
                        'user_2_scope':user_2_scope,
                        'vector_of_outcome':vectors_of_outcome,
                        
    #                     'user1_sortDimension' :'USER1_NATIONAL_PARTY',
    #                     'user2_sortDimension' : 'USER2_NATIONAL_PARTY',
    #                     'user1_header' : 'USER1',#'USER1',#'USER1_NAME_FULL',
    #                     'user2_header' : 'USER2'#'USER2'#'USER2_NAME_FULL'
                        'user1_sortDimension' :'USER1_occupation',
                        'user2_sortDimension' : 'USER2_occupation',
                        'user1_header' : 'USER1',#'USER1',#'USER1_NAME_FULL',
                        'user2_header' : 'USER2'#'USER2'#'USER2_NAME_FULL'
                    }
                },
                'outputs':{
                    
                    
                }
            }
        ]
        
        workflow_prepdataset2=[
            {
                'id':'VOTES_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':"PARAMETERS.outputs.dataset"
                },
                'configuration':{
                    'hasHeader':True,
                    #'delimiter':';',
                    'arrayHeader':dataset_arrayHeader,#['genres'],
                    'numberHeader':dataset_numberHeader#['releaseDate','age']
                },
                'outputs':{
                    'dataset':{}
                }, 
                'execute':False
            },
                               
            {
                'id':'ITEMS_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':items_file
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                } 
            },
            {
                'id':'USERS_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':users_file
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                } 
            },
            {
                'id':'REVIEWS_READER',
                'type':'csvReader',
                'inputs':{
                    'sourceFile':reviews_file
                },
                'configuration':{
                    'hasHeader':True,
                    'arrayHeader':dataset_arrayHeader,
                    'numberHeader':dataset_numberHeader
                },
                'outputs':{
                    'dataset':{}
                } 
            },                                         
                               
                               
#             {
#                 'id':'GENERAL_FILTER',
#                 'type':'filter',
#                 'inputs':{
#                     'dataset':'VOTES_READER.outputs.dataset'
#                 },
#                 'configuration':{
#                     'pipeline':items_scope
#                 },
#                 'outputs':{
#                     'dataset':{}
#                 }
#             },
            {
        
                'id':'MAJORITY_COMPUTER', 
                'type':'majorities_computer',
                'inputs': {
                    'dataset' :'VOTES_READER.outputs.dataset' 
                },
                'configuration': {
                    'votes_attributes':'PARAMETERS.outputs.votes_attributes',
                    'users_attributes':'PARAMETERS.outputs.users_attributes', 
                    'users_majorities_attributes':'PARAMETERS.outputs.aggregation_attributes', 
                    'position_attribute':'PARAMETERS.outputs.position_attribute',
                    'nb_aggregation_min':'PARAMETERS.outputs.nb_aggregation_min',
                    'vector_of_outcome':'PARAMETERS.outputs.vector_of_outcome',
                    'method_aggregation_outcome':method_aggregation_outcome
                },
                'outputs':{
                    'dataset':[]
                },
                'execute':False
            },
            {
        
                'id':'MAJORITY_COMPUTER_REVIEWS', 
                'type':'majorities_computer',
                'inputs': {
                    'dataset' :'REVIEWS_READER.outputs.dataset' 
                },
                'configuration': {
                    'votes_attributes':['PARAMETERS.outputs.votes_attributes[0]'],
                    'users_attributes':['PARAMETERS.outputs.users_attributes[0]'], 
                    'users_majorities_attributes':'PARAMETERS.outputs.aggregation_attributes', 
                    'position_attribute':'PARAMETERS.outputs.position_attribute',
                    'nb_aggregation_min':'PARAMETERS.outputs.nb_aggregation_min',
                    'vector_of_outcome':'PARAMETERS.outputs.vector_of_outcome',
                    'method_aggregation_outcome':method_aggregation_outcome
                },
                'outputs':{
                    'dataset':[]
                }
            },
                              
#             {
#                 'id':'GENERAL_FILTER_2',
#                 'type':'filter',
#                 'inputs':{
#                     'dataset':'MAJORITY_COMPUTER.outputs.dataset'
#                 },
#                 'configuration':{
#                     'pipeline':[
#     #                     {
#     #                         'dimensionName':'NATIONAL_PARTY',
#     #                         'inSet':'PARAMETERS.outputs.party'
#     #                     },
#                         {
#                             'dimensionName':'MAJORITY',
#                             'greaterThanOrEqual':0
#                             #'greaterThanOrEqual':1
#                         }
#     #                     {
#     #                         'dimensionName':'NATIONAL_PARTY',
#     #                         'inSet':'PARAMETERS.outputs.party'
#     #                     }
#                         
#                     ]
#                 },
#                 'outputs':{
#                     'dataset':{}
#                 }
#             },
#             {
#         
#                 'id':'WORKFLOW_PREPARED_DATASET',
#                 'type':'pipeliner',
#                 'inputs':{
#                     'dataset':'GENERAL_FILTER_2.outputs.dataset',#'GENERAL_FILTER.outputs.dataset',
#                     #'meps_count':'float(GENERAL_MEPS_COUNTER.outputs.dataset[0].MEPS_COUNT)',
#                     #'themes':'THEMES_FILE_READER.outputs.dataset',
#                     #'dossiers':'DOSSIERS_AGGREGATOR_ON_THEMES.outputs.dataset',
#                     #'parties':'DISTINCT_VALUES_GETTER.outputs.dataset[0].PARTIES',
#                     #'dates':'DISTINCT_VALUES_GETTER.outputs.dataset[0].DATES'
#         
#                 },
#                 'configuration':{
#                     'outputsFormula':{
#                         'dataset':'dataset',
#     #                     'meps_count':'meps_count',
#     #                     'themes':'themes',
#     #                     'dossiers':'dossiers',
#     #                     'parties':'toArray(parties)',
#     #                     'dates':'toArray(dates)'
#                     }
#                 },
#                 'outputs':{
#                     
#                     
#                 }
#             }
            ]
        
        
        workflow_patternsEnumerator2=[     
            {
         
                'id':'PATTERN_ENUMERATOR',
                'type':'multiple_attributes_iterator_sgbitwise_subgroups',
                'inputs': {
                    'dataset':[],#'MAJORITY_COMPUTER.outputs.dataset',
    #                 'attributes':[
    # 
    # #                     {'name' : 'PROCEDURE_SUBJECT', 'type' : 'themes'},
    # #                     {'name':'PROCEDURE_SUBTYPE', 'type':'simple'},
    # #                     {'name':'PROCEDURE_TYPE', 'type':'simple'},
    # #                     {'name':'COMMITTEE', 'type':'simple'},
    # #                     {'name' : 'VOTE_DATE', 'type' : 'numeric'},
    # #                     {'name' : 'GROUPE_ID', 'type' : 'simple'},
    # #                     {'name' : 'NATIONAL_PARTY', 'type' : 'simple'},
    # #                     {'name' : 'GENDER', 'type' : 'simple'},
    #                     
    #                     #{'name' : 'AGE', 'type' : 'numeric'}
    #                     #
    #                     
    #                     
    #                     {'name' : 'genres', 'type' : 'themes'},
    #                     {'name' : 'releaseDate', 'type' : 'numeric'},
    #                     #{'name' : 'ageGroup', 'type' : 'simple'},
    #                     #{'name' : 'gender', 'type' : 'simple'},
    # #                     {'name' : 'releaseDate', 'type' : 'numeric'},
    # #                     {'name' : 'occupation', 'type' : 'simple'}
    #                     #{'name' : 'NATIONAL_PARTY', 'type' : 'nominal'}    
    #                 ],
    
    
                    
                    'attributes':attributes,
                    'items_scope':'PARAMETERS.outputs.items_scope',
                    'referential_scope':'PARAMETERS.outputs.referential_scope',
                    'user_1_scope':'PARAMETERS.outputs.user_1_scope',
                    
                    'user_2_scope':'PARAMETERS.outputs.user_2_scope',
                    
                    'votes_attributes':'PARAMETERS.outputs.votes_attributes',
                    'users_attributes':'PARAMETERS.outputs.users_attributes',
                    'position_attribute':'PARAMETERS.outputs.position_attribute'
                },
                'configuration': {
                    'only_square_matrix':'PARAMETERS.outputs.only_square_matrix',
                    'nb_dossiers_min':'PARAMETERS.outputs.nb_dossiers_threshold',
                    'threshold_pair_comparaison':'PARAMETERS.outputs.threshold_pair_comparaison',
                    'cover_threshold':'PARAMETERS.outputs.cover_threshold', #SEE AGAINS HOW TO DECLARE CONDITIONS ON FREQUENT PATTERN,
                    'quality_threshold':'PARAMETERS.outputs.quality_threshold',
                    'top_k':'PARAMETERS.outputs.top_k',
                    
                    'iwant':'PARAMETERS.outputs.iwant',
                    'pruning':'PARAMETERS.outputs.pruning' ,
                    'closed':'PARAMETERS.outputs.closed' ,
                    
                    'aggregation_attributes_user1':attr_aggregates,#['ageGroup'],#['NATIONAL_PARTY'],
                    'aggregation_attributes_user2':attr_aggregates,#['ageGroup'],#['NATIONAL_PARTY'],
                    'nb_aggergation_min_user1':sigma_agg,
                    'threshold_nb_users_1':sigma_user,
                    'nb_aggergation_min_user2':sigma_agg,
                    'threshold_nb_users_2':sigma_user,
                    'comparaison_measure':'PARAMETERS.outputs.comparaison_measure',
                    'upperbound':upperbound,
                    'reviews_dataset':'MAJORITY_COMPUTER_REVIEWS.outputs.dataset',
                    'items_dataset':'ITEMS_READER.outputs.dataset',
                    'users_dataset':'USERS_READER.outputs.dataset',
                    
                    'vector_of_outcome':'PARAMETERS.outputs.vector_of_outcome',
                    'nb_items':nb_items,
                    'nb_users':nb_users,
                    
                    'ponderate_by_user':ponderate_by_user,
                    'ponderate_by_item':ponderate_by_item,
                    'method_aggregation_outcome':method_aggregation_outcome
                    #1019     668     523     352 
                    #9338     5158     1866     1866
                },
                'outputs':{
                    'yielded_item':'',
                    'yielded_index':'',
                    'yielded_description':'',
                    'pairwiseStatistics':[]
                }
            },
            {
        
                'id':'WORKFLOW_PATTERNS_ENUMERATOR', 
                'type':'pipeliner',
                'inputs':{
                    'pattern':'PATTERN_ENUMERATOR.outputs.yielded_item',
                    'description':'PATTERN_ENUMERATOR.outputs.yielded_description',
                    'pattern_index':'PATTERN_ENUMERATOR.outputs.yielded_index',
                    'dossiers_voted':'PATTERN_ENUMERATOR.outputs.dossiers_voted',
                    'quality':'PATTERN_ENUMERATOR.outputs.quality',
                    'upper_bound':'PATTERN_ENUMERATOR.outputs.upper_bound',
                    'pairwiseStatistics':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics',
                    'disp':'PATTERN_ENUMERATOR.outputs.disp',
                    'disp_ext':'PATTERN_ENUMERATOR.outputs.disp_ext',
                    'reviews':'PATTERN_ENUMERATOR.outputs.disp.reviews',
                    'votes_and_ids_considered':'PATTERN_ENUMERATOR.outputs.disp.votes_and_ids_considered',
                },
                'configuration':{
                    'outputsFormula':{
                        'data':{
                            'pattern_index':'pattern_index',
                            'pattern':'pattern',
                            'description':'description',
                            'quality':'quality',
                            'dossiers_voted':'dossiers_voted',
                            'upper_bound':'upper_bound',
                            'disp':'disp',
                            'disp_ext':'disp_ext',
                            'reviews':'reviews',
                            'votes_and_ids_considered':'votes_and_ids_considered'
                        }
                        
                    }
                },
                'outputs':{
                    
                    
                }
            },
            {
                'id':'MATRICES_DIFFERENCE',
                'type':'difference_matrices',
                'inputs':{
                    'matrix_1' : 'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[0]', #with header and rower
                    'matrix_2' : 'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[1]' #with header and rower
                },
                'configuration':{
                    'printType':'default'
                },
                'outputs':{
                    'matrix' : []
                } 
            },    
            {
                'id':'GENERAL_HEATMAP',
                'type':'heatmap_visualization',
                'inputs':{
                    'dataset':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[0]',
                    'destinationFile':"'./Figures/Ref_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"#"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAPREF_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"
                },
                'configuration':{
                    'vmin':0.0,
                    'vmax':1.0,
                    'color':'RdYlGn',
                    'organize':'PARAMETERS.outputs.organizeHeatmaps',
                    'title':'Reference model'
                },
                'outputs':{
                        
                },
                'execute':'PARAMETERS.outputs.heatmap'
            },
            {
                'id':'PATTERN_HEATMAP',
                'type':'heatmap_visualization',
                'inputs':{
                    'dataset':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[1]',
                    'destinationFile':"'./Figures/Pattern_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"#"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAPPATTERN_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"
                },
                'configuration':{
                    'vmin':0.0,
                    'vmax':1.0,
                    'color':'RdYlGn',
                    'organize':'PARAMETERS.outputs.organizeHeatmaps',
                    'title':'pattern model'
                },
                'outputs':{
                        
                },
                'execute':'PARAMETERS.outputs.heatmap'
            },
            {
                'id':'SUBGROUP_HEATMAP_DIFFERENCES',
                'type':'heatmap_visualization',
                'inputs':{
                    'dataset':'MATRICES_DIFFERENCE.outputs.matrix',
                    'destinationFile':"PARAMETERS.outputs.repository+'\\Figures\\Diffs_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"
                },
                'configuration':{
                    'vmin':-1.0,
                    'vmax':1.0,
                    'color':'RdYlGn',
                    #'organize':True
                },
                'outputs':{
                        
                },
                'execute':False
                #'(NORM_COMPUTER.outputs.norm*((len(MATRICES_DIFFERENCE.outputs.matrix)-1)/(len(GENERAL_TRANFORMATOR.outputs.comparaisonMatrixDataset)-1)))>0.02'
            },
            {
                'id':'REF_MATRIX_CSV_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[0]',
                    'destinationFile':"'./Figures/RefMatrix_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.csv'"
                },
                'configuration':{
                    'hasHeader': False, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                },
                'outputs':{
                    
                },
                'execute':False
            },
            {
                'id':'PATTERN_MATRIX_CSV_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[1]',
                    'destinationFile':"'./Figures/PatternMatrix_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.csv'"
                },
                'configuration':{
                    'hasHeader': False, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                },
                'outputs':{
                    
                },
                'execute':False
            },                          
            {
                'id':'votes_and_ids_considered_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'PARAMETERS.outputs.properties + WORKFLOW_PATTERNS_ENUMERATOR.outputs.data.votes_and_ids_considered',
                    'destinationFile':"'./Figures/votes_and_ids_considered_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.csv'"
                },
                'configuration':{
                    'hasHeader': False, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                },
                'outputs':{
                    
                },
                'execute':False
            },       
                 
                                      
            {
                'id':'REVIEWS_SUBSET_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.data.reviews',
                    'destinationFile':"'./Figures/ReviewsPattern_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.csv'"
                },
                'configuration':{
                    'hasHeader': True, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                    'selectedHeader':votes_attributes+users_attributes+[outcome_attribute]
                },
                'outputs':{
                    
                },
                'execute':False
            },
            {
                'id':'FINAL_SYNCER',
                'type':'flatAppenderSyncer',
                'inputs':{
                    'data':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.data.disp'
                },
                'configuration':{
                     
                },
                'outputs':{
                    'syncedData':[]
                } 
            },
            {
                'id':'QUALITIES_CSV_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'FINAL_SYNCER.outputs.syncedData',
                    'destinationFile':qualitiesFile
                },
                'configuration':{
                    'hasHeader': True, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                    'selectedHeader':['index','pattern','context','g1','g2','|subgroup(context)|','|subgroup(g1)|','|subgroup(g2)|','#reviews','quality','upperbound','items_details']
                },
                'outputs':{
                    
                } 
            },
            {
                'id':'QUALITIES_CSV_WRITER_EXTENTS',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'FINAL_SYNCER.outputs.syncedData',
                    'destinationFile':qualities_extents_File
                },
                'configuration':{
                    'hasHeader': True, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                    'selectedHeader':['context_extent','g_1_extent','g_2_extent','context','g_1','g_2','sim_context','sim_ref','quality']
                },
                'outputs':{
                    
                },
                'execute':False 
            },
            {
                'id':'PERFORMANCE_CSV_WRITER',
                'type':'csvWriter',
                'inputs':{
                    'dataset':'FINAL_SYNCER.outputs.syncedData',
                    'destinationFile':qualities_perf_File
                },
                'configuration':{
                    'hasHeader': True, #,'qualityFrob'
                    #'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
                    'selectedHeader':['visited','nb_patterns','Outcomes_covered'],
                    'OnlyOneRow':True
                },
                'outputs':{
                    
                } 
            },
            ]
        
        #######################################################################################
       
        
        
        #source_configuration_test=sys.argv[1]
        
        
        
        
        
        
        print 'reading the test configuration and the data file ...'
        
    
            
        workflowFinal2=wokflow_parameters2+workflow_prepdataset2+workflow_patternsEnumerator2
    
        
        
        
        configuration_execution={
            'attr_items_range':[],
            'attr_users_range':[],
            'attr_aggregates_range':[],
            'nb_items_range':[],
            'nb_users_range':[],
            'sigma_user_range':[],
            'sigma_agg_range':[],
            'sigma_item_range':[],
            'sigma_quality_range':[],
            'top_k_range':[],
            'prunning_closed_range':[]
                
        }
        Profiling=False
        if len(sys.argv)==1 : Profiling=True
        figure_directory='./Figures'
        if not os.path.exists(figure_directory):
            os.makedirs(figure_directory)
        if Profiling:
            pr = cProfile.Profile()
            pr.enable()
        if heatmap_yes:
            from workflows.workflowsProcessing import process_workflow_recursive 
            
        process_workflow_recursive(workflowFinal2, verbose=False,verbose2=True)
        if Profiling:
            pr.disable()
            ps = pstats.Stats(pr)
            ps.sort_stats('cumulative').print_stats(100) #time
            




    #################################################
    
    if False :
#         d,h=readCSVwithHeader('C:\\Users\\Adnene\\Desktop\\XP_PKDD\\parliament\\All\\all_countries8\\France8.csv',arrayHeader=["PROCEDURE_SUBJECT"],numberHeader=["VOTE_DATE","AGE"])
#           
#         infos={
#             "items_attributes":["VOTEID","PROCEDURE_TITLE","VOTE_DATE","VOTE_DATE_DETAILED","PROCEDURE_SUBJECT","DOSSIERID","PROCEDURE_SUBTYPE","COMMITTEE","PROCEDURE_TYPE"],
#             "users_attributes":["EP_ID","NAME_FULL","NATIONAL_PARTY","GROUPE_ID","COUNTRY","AGEGROUP","GENDER","AGE"],
#             "outcome_attributes":"USER_VOTE"    
#         }
#     #     
#         votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(d,[],infos['items_attributes'],infos['users_attributes'],infos['outcome_attributes'])
#         d=votes_map_details.values()
        
        nbHeader=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','aa','ab','ac','ad','ae','af','ag','ah']
        attr_num=[{'name':v, 'type':'numeric'} for v in nbHeader]
        d2,h2=readCSVwithHeader('C:\\Users\\Adnene\\Desktop\\numeric\\Datasets\\iris.csv',numberHeader=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','aa','ab','ac','ad','ae','af','ag','ah'],delimiter=',')
        d,h=readCSVwithHeader('C:\\Users\\Adnene\\Desktop\\Groceries\\irishmt2.csv',arrayHeader=["all","sepal_length_hmt","sepal_width_hmt","petal_length_hmt","petal_width_hmt"],numberHeader=nbHeader+["sepal_length","sepal_width","petal_length","petal_width"])
        s=time()
        PROFILING=False
        
        if PROFILING:
            pr = cProfile.Profile()
            pr.enable()
        
        dataset=d2
        #dataset=d2
        enum=enumerator_complex_cbo_init_new_config(dataset,attr_num[:2],threshold=1,bfs=False,verbose=True)
        
        
        #list(enum)
        #####################
        classes={}
#         def abs(v):
#             if v<0: return (-1*v)*1.
#             return v*1.
        for i,row in enumerate(dataset):
            c=row['class']
            if c not in classes:
                classes[c]=0.
            classes[c]+=1.
        classes={k:v/float(len(dataset)) for k,v in classes.iteritems()}
        print classes
        maxx=0
        raw_input('...')
        #######################
        values_quality=[]
        st=0
        for x in enum:
            
            classes_d={k:0. for k in classes}
            for row in x[2]['support']:
                c=row['class']
                classes_d[c]+=1.
               
            
            classes_d={k:v/float(len(dataset)) for k,v in classes_d.iteritems()}
            wrac_d={k:abs(classes_d[k]-classes[k])*(len(x[2]['support'])+0.)/(len(dataset)+0.) for k,v in classes_d.iteritems()}
            maxx=max(maxx,sum(wrac_d.values()))
            print x[0],len(x[2]['support']),maxx
            values_quality.append(maxx)
            st+=1
#             if maxx>=0.23:
#                 break
            #raw_input('...')
        print 'time spent', time()-s
        if PROFILING: 
            pr.disable()
            ps = pstats.Stats(pr)
            ps.sort_stats('time').print_stats(100) #cumulativ
        
        writeCSVwithHeader([{'index':k,'quality':v} for k,v in enumerate(values_quality)], "C:\\Users\\Adnene\\Desktop\\numeric\\quality_mehdi.csv", ['index','quality'], '\t', True)
        
        raw_input('.....')
        
        
        d,h=readCSVwithHeader('C:\\Users\\Adnene\\Desktop\\YELP\\items.csv',arrayHeader=["categories"],numberHeader=["review_count","stars"]) #,"new_attributes"
        for key in d[0]:
            print d[0][key]
        
        print 'HELLO'
        PROFILING=True
        
        if PROFILING:
            pr = cProfile.Profile()
            pr.enable()
        enum=enumerator_complex_cbo_init_new_config(d,[
            
            {'name':'categories', 'type':'themes'},
             #{'name':'PROCEDURE_SUBJECT', 'type':'themes'},                                                          #'widthmax':2
        ],threshold=1,verbose=True)
        
        
        
    #     enum2=enumerator_complex_from_dataset_new_config(d,[
    #          {'name':'PROCEDURE_SUBJECT', 'type':'themes'},
    #     ],objet_id_attribute='VOTEID',threshold=1,verbose=True)
        
        
        s=time()
        tops=[]
        for x,y,z in enum:
            
            to_remove=set()
            tops.append((x,y,(sum(x['stars']*x['review_count'] for x in z['support'])/sum(x['review_count'] for x in z['support']))))
            if len(tops)>10:
                tops=sorted(tops,reverse=False,key=lambda x : x [2])[:10]
            continue
    #         for k in range(len(tops)-1):
    #             for k2 in range(k+1,len(tops)):
    #                 if similarity_between_descriptions(tops[k][0][0], tops[k2][0][0]):
    #                     to_remove|={k2}
    #         
    #         tops2=[tops[i] for i in range(len(tops)) if i not in to_remove]    
    #         tops=tops2
            
            continue
            continue
            enum2=enumerator_complex_cbo_init_new_config(d,[
                {'name':'categories', 'type':'themes'},
                #{'name':'PROCEDURE_SUBJECT', 'type':'themes'},
            ],threshold=20,verbose=False)
            
            conj_1=x[0]
            for x2,y2,z2 in enum2:
                conj_2=x2[0]
                z2['flag']=not similarity_between_descriptions(conj_1, conj_2)
                if z2['flag']:
                    tops.append((y,y2,(len(z['indices']&z2['indices'])/float(len(z['indices']|z2['indices'])))))
                    if len(tops)>10:
                        tops=sorted(tops,reverse=True,key=lambda x : x [2])[:10]
                
            print conj_1,conj_2
            #print x
            #print x,y,'%.2f' % 
            #print x
            continue
            
    #         tops.append((x,y,(sum(x['stars']*x['review_count'] for x in z['support'])/sum(x['review_count'] for x in z['support']))))
    #         if len(tops)>10:
    #             tops=sorted(tops,reverse=True,key=lambda x : x [2])[:10]
    #         continue
        
        for t in tops:
            print t
        print time()-s
        if PROFILING: 
            pr.disable()
            ps = pstats.Stats(pr)
            ps.sort_stats('time').print_stats(100) #cumulativ
            
         
    if False :
        d,h=readCSVwithHeader('C:\\Users\\Adnene\\Desktop\\Datasets election\\votes_1_tour.csv',numberHeader=["Inscrits","Voix"])
        
        infos={
            "items_attributes":["codeinsee","codedep","labeldep","codecom","labelcom","Inscrits","Abstentions","% Abs/Ins","Votants","% Vot/Ins","Blancs","% Blancs/Ins","% Blancs/Vot","Nuls","% Nuls/Ins","% Nuls/Vot","Exprimes","% Exp/Ins","% Exp/Vot"],
            "users_attributes":["N_Panneau","Sexe","Nom","Prenom"],
            "outcome_attributes":"Voix"  
        }
        
        
        
        
        votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(d,[],infos['items_attributes'],infos['users_attributes'],infos['outcome_attributes'])
        d=votes_map_details.values()
        
        enum=enumerator_complex_cbo_init_new_config(d,[
            
            {'name':'codedep', 'type':'simple'},
             #{'name':'PROCEDURE_SUBJECT', 'type':'themes'},                                                          #'widthmax':2
        ],threshold=1,verbose=True)
        
        for x,y,z in enum:
            print x,len(z['support'])
        
            
    
    
            
    
    
    
    
    
    