'''
Created on 11 nov. 2016

@author: Adnene
'''


import argparse
import cProfile
import json
import pstats
import sys
import os 

from EMM_ENUMERATOR.enumerator_themes2 import evaluate_themes_2
from util.jsonProcessing import readJSON, writeJSON, readJSON_stringifyUnicodes
from workflows.workflowsProcessing_Pypy import process_workflow_recursive

from pprint import pprint
from plotters.plotPerformance import PlotPerf
#from plotters.plotPerformance import PlotPerf
sys.setrecursionlimit(sys.maxint)
if __name__ == '__main__':
    
    source_configuration_test=sys.argv[1]
    #source_configuration_test='C:\\Users\\Adnene\\Desktop\\XP_PKDD\\parliament\\All\\dummy\\question_1\\nb_items.json'
    print source_configuration_test
    data = readJSON_stringifyUnicodes(source_configuration_test)
    #dataset_file=os.getcwd()+"\\"+data['dataset_file']
    dataset_file=data['dataset_file']
    dataset_arrayHeader=data['dataset_arrayHeader']
    dataset_numberHeader=data['dataset_numberHeader']
    votes_attributes=data['items_attributes']
    users_attributes=data['users_attributes']#+["MAJORITY"]
    outcome_attribute=data['outcome_attributes']
    source_destination=os.getcwd()+'\\'+(os.path.splitext(sys.argv[1])[0])+'.csv'
    destination=source_destination#data['destination']
    figure_destination=os.getcwd()+'\\'+(os.path.splitext(sys.argv[1])[0])+'.jpg'
    
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
            } 
        },
        {
    
            'id':'log',
            'type':'log_printer',
            'inputs': {
                'data' :'\nThe dataset file : ' + dataset_file+' is successfully loaded...\n'  
            },
            'configuration': {
               'printType':'default'
            },
            'outputs':{
            }
        },
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
                'comparaison_measure':'PARAMETERS.outputs.comparaison_measure' 
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
                        'upper_bound':'upper_bound'
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
    draw_figure=False
    if draw_figure :
        PlotPerf(source_destination, var_column, ["BASELINE","DSC+UB1","DSC+UB2","CLOSED"], True, True)
    