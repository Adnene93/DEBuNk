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
from ENUMERATORS_ATTRIBUTES.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config
from util.csvProcessing import readCSVwithHeader
from util.jsonProcessing import readJSON, writeJSON, readJSON_stringifyUnicodes
from workflows.workflowsProcessing import process_workflow_recursive


find_packages()




sys.setrecursionlimit(sys.maxint)
if __name__ == '__main__':
#     print 'HI'
#     evaluate_themes_2(['1.10','1.20','2.10.01','2.10.02'],200)
#     
    
    #print evaluate_themes_2(['1', '1.10', '1.20', '1.30', '2.30', '4.20', '4.30', '4.40.01', '4.40.02', '4.40.03', '5.10', '5.20', '5.30.01', '5.30.02', '6.10', '6.20', '7.10', '7.20','7.30.01','7.30.02','7.30.03','8'],7)
    
    repository='C:\\Users\\Adnene\\Desktop\\ExperimentsDB'    
        
    update_skip_list='list(pattern)' #sourceArr+
    
    source_configuration_test=sys.argv[1]
    #source_configuration_test='C:\Users\Adnene\Desktop\DiscoveringSimilarityChanges\QualitativeXP\parliament\Germany\qualitative.json'
    print source_configuration_test
    data = readJSON_stringifyUnicodes(source_configuration_test)
    source_destination=os.getcwd()
    #dataset_file=source_destination+"\\"+data['dataset_file']
    dataset_file=data['dataset_file']
    dataset_arrayHeader=data['dataset_arrayHeader']
    dataset_numberHeader=data['dataset_numberHeader']
    votes_attributes=data['items_attributes']
    users_attributes=data['users_attributes']#+["MAJORITY"]
    outcome_attribute=data['outcome_attributes']
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
    
    user_1_scope=data["user_1_scope"]
    user_2_scope=data["user_2_scope"]
    
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
                    
                    'country':['France','Germany','United Kingdom','Spain','Belgium','Italy','Portugal'],
                    'party':['Front national','Les R\xc3\xa9publicains'],#,'Les R\xc3\xa9publicains','Front national','Parti socialiste','Alternative fur Deutschland','Christlich Demokratische Union Deutschlands','Sozialdemokratische Partei Deutschlands','Bundnis 90/Die Grunen'
                    
                    'threshold_pair_comparaison':sigma_item,
                    'nb_dossiers_threshold':1,
                    
                    
                    'cover_threshold':2,
                    
                    'top_k':top_k,#5,
                    'quality_threshold':sigma_quality,#0,
                    
                    'comparaison_measure':similarity_measures,#'AVG_RANKING_SIMPLE',#'AVG_RANKING_SIMPLE',
                    'iwant':quality_measures,#'DISAGR_SUMDIFF',#'DISAGR_SUMDIFF',#'DISAGR_FROBENIUS_U1_U2',
                    'heatmap':heatmap_yes,
                    'heatmap_general':False,
                    'heatmap_diff':False,
                    'organizeHeatmaps':False,
                    
                    'pruning':True,
                    
                    
                    
                    #8090     5528     3682     3271     96
                    #######################"
                    
#                     'votes_attributes':['VOTEID','DOSSIERID','VOTE_DATE','VOTE_DATE_DETAILED','PROCEDURE_SUBJECT','PROCEDURE_TITLE','PROCEDURE_SUBTYPE','COMMITTEE','PROCEDURE_TYPE'],
#                     'users_attributes':['EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','GENDER','AGE','MAJORITY'], 
#                     'position_attribute':'USER_VOTE',  
                    
                    'votes_attributes':votes_attributes,#['movieID','movieTitle','releaseDate','genres','IMDBURL'],
                    'users_attributes':users_attributes,#['userid','age','ageGroup','gender','occupation','zipcode','MAJORITY'], 
                    'position_attribute':outcome_attribute,#'Rating',                                                               #'PARAMETERS.outputs.position_attribute'
                    
                    'aggregation_attributes':None,#['NATIONAL_PARTY'],
                    'nb_aggregation_min':1,
                    
                    'user_1_scope':user_1_scope,
                    
                    'user_2_scope':user_2_scope,
                    
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
#                 'arrayHeader':['PROCEDURE_SUBJECT'],
#                 'numberHeader':['VOTE_DATE','AGE']
                'arrayHeader':dataset_arrayHeader,#['genres'],
                'numberHeader':dataset_numberHeader#['releaseDate','age']
            },
            'outputs':{
                'dataset':{}
            } 
        },
        {
            'id':'GENERAL_FILTER',
            'type':'filter',
            'inputs':{
                'dataset':'VOTES_READER.outputs.dataset'
            },
            'configuration':{
                'pipeline':[
#                     {
#                         'dimensionName':'COUNTRY',
#                         'inSet':'PARAMETERS.outputs.country'
#                     },
#                     {
#                         'dimensionName':'NATIONAL_PARTY',
#                         'inSet':'PARAMETERS.outputs.party'
#                     }
#                     
                ]
            },
            'outputs':{
                'dataset':{}
            }
        },
        {
    
            'id':'MAJORITY_COMPUTER', 
            'type':'majorities_computer',
            'inputs': {
                'dataset' :'GENERAL_FILTER.outputs.dataset' 
            },
            'configuration': {
                'votes_attributes':'PARAMETERS.outputs.votes_attributes',
                'users_attributes':'PARAMETERS.outputs.users_attributes', 
                'users_majorities_attributes':'PARAMETERS.outputs.aggregation_attributes', 
                'position_attribute':'PARAMETERS.outputs.position_attribute',
                'nb_aggregation_min':'PARAMETERS.outputs.nb_aggregation_min',
                #'vector_of_outcome':['Voix','Votants']
            },
            'outputs':{
                'dataset':[]
            }
        },
                          
        {
            'id':'GENERAL_FILTER_2',
            'type':'filter',
            'inputs':{
                'dataset':'MAJORITY_COMPUTER.outputs.dataset'
            },
            'configuration':{
                'pipeline':[
#                     {
#                         'dimensionName':'NATIONAL_PARTY',
#                         'inSet':'PARAMETERS.outputs.party'
#                     },
                    {
                        'dimensionName':'MAJORITY',
                        'greaterThanOrEqual':0
                        #'greaterThanOrEqual':1
                    }
#                     {
#                         'dimensionName':'NATIONAL_PARTY',
#                         'inSet':'PARAMETERS.outputs.party'
#                     }
                    
                ]
            },
            'outputs':{
                'dataset':{}
            }
        },
        {
    
            'id':'WORKFLOW_PREPARED_DATASET',
            'type':'pipeliner',
            'inputs':{
                'dataset':'GENERAL_FILTER_2.outputs.dataset',#'GENERAL_FILTER.outputs.dataset',
                #'meps_count':'float(GENERAL_MEPS_COUNTER.outputs.dataset[0].MEPS_COUNT)',
                #'themes':'THEMES_FILE_READER.outputs.dataset',
                #'dossiers':'DOSSIERS_AGGREGATOR_ON_THEMES.outputs.dataset',
                #'parties':'DISTINCT_VALUES_GETTER.outputs.dataset[0].PARTIES',
                #'dates':'DISTINCT_VALUES_GETTER.outputs.dataset[0].DATES'
    
            },
            'configuration':{
                'outputsFormula':{
                    'dataset':'dataset',
#                     'meps_count':'meps_count',
#                     'themes':'themes',
#                     'dossiers':'dossiers',
#                     'parties':'toArray(parties)',
#                     'dates':'toArray(dates)'
                }
            },
            'outputs':{
                
                
            }
        }
        ]
    
    
    workflow_patternsEnumerator2=[     
        {
     
            'id':'PATTERN_ENUMERATOR',
            'type':'multiple_attributes_iterator_sgbitwise_subgroups',
            'inputs': {
                'dataset':'WORKFLOW_PREPARED_DATASET.outputs.dataset',
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
                'user_1_scope':'PARAMETERS.outputs.user_1_scope',
                
                'user_2_scope':'PARAMETERS.outputs.user_2_scope',
                
                'votes_attributes':'PARAMETERS.outputs.votes_attributes',
                'users_attributes':'PARAMETERS.outputs.users_attributes',
                'position_attribute':'PARAMETERS.outputs.position_attribute'
            },
            'configuration': {
                'nb_dossiers_min':'PARAMETERS.outputs.nb_dossiers_threshold',
                'threshold_pair_comparaison':'PARAMETERS.outputs.threshold_pair_comparaison',
                'cover_threshold':'PARAMETERS.outputs.cover_threshold', #SEE AGAINS HOW TO DECLARE CONDITIONS ON FREQUENT PATTERN,
                'quality_threshold':'PARAMETERS.outputs.quality_threshold',
                'top_k':'PARAMETERS.outputs.top_k',
                
                'iwant':'PARAMETERS.outputs.iwant',
                'pruning':'PARAMETERS.outputs.pruning' ,
                
                'aggregation_attributes_user1':attr_aggregates,#['ageGroup'],#['NATIONAL_PARTY'],
                'aggregation_attributes_user2':attr_aggregates,#['ageGroup'],#['NATIONAL_PARTY'],
                'nb_aggergation_min_user1':sigma_agg,
                'threshold_nb_users_1':sigma_user,
                'nb_aggergation_min_user2':sigma_agg,
                'threshold_nb_users_2':sigma_user,
                'comparaison_measure':'PARAMETERS.outputs.comparaison_measure',
                'upperbound':upperbound
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
                'context_extent':'PATTERN_ENUMERATOR.outputs.context_extent',
                'g_1_extent':'PATTERN_ENUMERATOR.outputs.g_1_extent',
                'g_2_extent':'PATTERN_ENUMERATOR.outputs.g_2_extent',
                'context':'PATTERN_ENUMERATOR.outputs.context',
                'g_1':'PATTERN_ENUMERATOR.outputs.g_1',
                'g_2':'PATTERN_ENUMERATOR.outputs.g_2'
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
                        
                        'context_extent':'context_extent',
                        'g_1_extent':'g_1_extent',
                        'g_2_extent':'g_2_extent',
                        'context':'context',
                        'g_1':'g_1',
                        'g_2':'g_2',
                        'sim_context':-1,
                        'sim_ref':-1
                        #sim_ref    sim_context quality
                    }
                    
                }
            },
            'outputs':{
                
                
            }
        },
        {
            'id':'GENERAL_HEATMAP',
            'type':'heatmap_visualization',
            'inputs':{
                'dataset':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics[0]',
                'destinationFile':"PARAMETERS.outputs.repository+'\\Figures\\Ref_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"#"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAPREF_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"
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
                'destinationFile':"PARAMETERS.outputs.repository+'\\Figures\\Pattern_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"#"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAPPATTERN_'+str(PATTERN_ENUMERATOR.outputs.yielded_index)+'.jpg'"
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
            'id':'FINAL_SYNCER',
            'type':'flatAppenderSyncer',
            'inputs':{
                'data':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.data'
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
                'destinationFile':"PARAMETERS.outputs.repository+'\\qualities.txt'" 
            },
            'configuration':{
                'hasHeader': True, #,'qualityFrob'
                'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','dossiers_voted']
            },
            'outputs':{
                
            } 
        }, 
        #'context_extent','g_1_extent','g_2_extent','context','g_1','g_2','sim_context','sim_ref','quality'
        {
            'id':'QUALITIES_CSV_WRITER_EXTENT',
            'type':'csvWriter',
            'inputs':{
                'dataset':'FINAL_SYNCER.outputs.syncedData',
                'destinationFile':"PARAMETERS.outputs.repository+'\\qualities_extent.txt'" 
            },
            'configuration':{
                'hasHeader': True, #,'qualityFrob'
                'selectedHeader':['context_extent','g_1_extent','g_2_extent','context','g_1','g_2','sim_context','sim_ref','quality']
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
    
    figure_directory=source_destination+'\\Figures'
    if not os.path.exists(figure_directory):
        os.makedirs(figure_directory)
#     pr = cProfile.Profile()
#     pr.enable()
    process_workflow_recursive(workflowFinal2, verbose=False)
#     pr.disable()
#     ps = pstats.Stats(pr)
#     ps.sort_stats('time').print_stats(100) #cumulativ





    #################################################
    