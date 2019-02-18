'''
Created on 11 nov. 2016

@author: Adnene
'''


import cProfile
import pstats
import sys

from EMM_ENUMERATOR.enumerator_themes2 import evaluate_themes_2
from util.jsonProcessing import readJSON, writeJSON, readJSON_stringifyUnicodes
from workflows.workflowsProcessing import process_workflow_recursive

import argparse

#sys.setrecursionlimit(sys.maxint)
if __name__ == '__main__':
#     print 'HI'
#     evaluate_themes_2(['1.10','1.20','2.10.01','2.10.02'],200)
#     
    
    #print evaluate_themes_2(['1', '1.10', '1.20', '1.30', '2.30', '4.20', '4.30', '4.40.01', '4.40.02', '4.40.03', '5.10', '5.20', '5.30.01', '5.30.02', '6.10', '6.20', '7.10', '7.20','7.30.01','7.30.02','7.30.03','8'],7)
    
    repository='/home/nassim/Bureau/exemple_pour_plateforme'    
    
    update_skip_list='list(pattern)' #sourceArr+
    wokflow_parameters=[
        {
    
            'id':'PARAMETERS',
            'type':'pipeliner',
            'inputs':{
                
            },
            'configuration':{
                'outputsFormula':{
                    
                    'repository':'/home/nassim/Bureau/exemple_pour_plateforme',
                    'dataset':'/home/nassim/Bureau/exemple_pour_plateforme/export.csv',
                    
                    'country':['France','Germany','United Kingdom','Spain','Belgium','Italy','Portugal'],
                    'party':['Front national','Les R\xc3\xa9publicains'],#,'Les R\xc3\xa9publicains','Front national','Parti socialiste','Alternative fur Deutschland','Christlich Demokratische Union Deutschlands','Sozialdemokratische Partei Deutschlands','Bundnis 90/Die Grunen'
                    
                    'threshold_pair_comparaison':1,
                    'nb_dossiers_threshold':1,
                    
                    
                    'cover_threshold':1.,
                    
                    'top_k':None,
                    'quality_threshold':0.,
                    
                    'comparaison_measure':'MMAP',
                    'iwant':'disagreement',
                    'heatmap':False,
                    'heatmap_general':False,
                    'heatmap_diff':False,
                    'organizeHeatmaps':True,
                    
                    'pruning':True,
                    
                    
                    #8090     5528     3682     3271     96
                    #######################"
                    
                    'votes_attributes':['VOTEID','DOSSIERID','VOTE_DATE','VOTE_DATE_DETAILED','PROCEDURE_SUBJECT','PROCEDURE_TITLE','PROCEDURE_SUBTYPE','COMMITTEE','PROCEDURE_TYPE'], #,'PROCEDURE_TYPE','COMMITTEE'
                    'users_attributes':['EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','GENDER','AGE','MAJORITY'], #'PARAMETERS.outputs.users_attributes'
                    'position_attribute':'USER_VOTE',                                                               #'PARAMETERS.outputs.position_attribute'
                    
                    'aggregation_attributes':['NATIONAL_PARTY'],
                    'nb_aggregation_min':6,
                    
                    'user_1_scope':[
                        {
                            'dimensionName':'MAJORITY',
                            'equal':1
                        },
#                         {
#                             'dimensionName':'NAME_FULL',
#                             'inSet':['Marine LE PEN']
#                         }
                    
                    ],
                    
                    'user_2_scope':[
                        {
                            'dimensionName':'MAJORITY',
                            'equal':1
                        },
#                         {
#                             'dimensionName':'NAME_FULL',
#                             'outSet':['Louis ALIOT','Marine LE PEN']
#                         }
                    ],
                    
                    'user1_sortDimension' :'USER1_NATIONAL_PARTY',
                    'user2_sortDimension' : 'USER2_NATIONAL_PARTY',
                    'user1_header' : 'USER1_NAME_FULL',#'USER1',#'USER1_NAME_FULL',
                    'user2_header' : 'USER2_NAME_FULL'#'USER2'#'USER2_NAME_FULL'
                }
            },
            'outputs':{
                
                
            }
        }
    ]
    
    
    workflow_prepdataset=[
        {
            'id':'VOTES_READER',
            'type':'csvReader',
            'inputs':{
                'sourceFile':"PARAMETERS.outputs.dataset"
            },
            'configuration':{
                'hasHeader':True,
                'arrayHeader':['PROCEDURE_SUBJECT'],
                'numberHeader':['VOTE_DATE','AGE']
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
                    {
                        'dimensionName':'COUNTRY',
                        'inSet':'PARAMETERS.outputs.country'
                    },
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
            'id':'GENERAL_MEPS_COUNTER',
            'type':'aggregator',
            'inputs':{
                'dataset': 'GENERAL_FILTER_2.outputs.dataset'
            },
            'configuration':{
                'dimensions':{
                    
                },
                'measures':{
                    'MEPS_COUNT':{
                        'count_distinct':'EP_ID'
                    }
                }
            },
            'outputs':{
                'dataset':{},
                'header':{}
            } 
        },        
#         {
#             'id':'DOSSIERS_FILE_READER',
#             'type':'csvReader',
#             'inputs':{
#                 'sourceFile':"PARAMETERS.outputs.repository+'\\Themes.csv'" 
#             },
#             'configuration':{
#                 'hasHeader':True
#             },
#             'outputs':{
#                 'dataset':{}
#             } 
#         },
#         {
#             'id':'DOSSIERS_AGGREGATOR_ON_THEMES',
#             'type':'aggregator',
#             'inputs': {
#                 'dataset':'DOSSIERS_FILE_READER.outputs.dataset'
#             },
#             'configuration': {
#                 'dimensions':{
#                     'DOSSIERID':'DOSSIERID'
#                 },
#                 'measures':{
#                     'SUBJECTS':{
#                         'append':"SUBJECTS_CODE + ' ' + SUBJECTS_LABEL" 
#                     } 
#                 }
#             },
#             'outputs':{
#                 'dataset':[],
#                 'header':[]
#             } 
#         },
        {
    
            'id':'WORKFLOW_PREPARED_DATASET',
            'type':'pipeliner',
            'inputs':{
                'dataset':'GENERAL_FILTER_2.outputs.dataset',#'GENERAL_FILTER.outputs.dataset',
                'meps_count':'float(GENERAL_MEPS_COUNTER.outputs.dataset[0].MEPS_COUNT)',
                'themes':'THEMES_FILE_READER.outputs.dataset',
                'dossiers':'DOSSIERS_AGGREGATOR_ON_THEMES.outputs.dataset',
                'parties':'DISTINCT_VALUES_GETTER.outputs.dataset[0].PARTIES',
                'dates':'DISTINCT_VALUES_GETTER.outputs.dataset[0].DATES'
    
            },
            'configuration':{
                'outputsFormula':{
                    'dataset':'dataset',
                    'meps_count':'meps_count',
                    'themes':'themes',
                    'dossiers':'dossiers',
                    'parties':'toArray(parties)',
                    'dates':'toArray(dates)'
                }
            },
            'outputs':{
                
                
            }
        },
        
        {
            'id':'DISTINCT_VALUES_LOGGER',
            'type':'log_printer',
            'inputs':{
                'data':['WORKFLOW_PREPARED_DATASET.outputs.parties','WORKFLOW_PREPARED_DATASET.outputs.dates'] 
            },
            'configuration':{
                 
            },
            'outputs':{
                 
            },
            'execute':False
        },
                          
        
    
    ]
    
    workflow_generalmodel=[
        {
            'id':'GENERAL_STATS',
            'type':'pairwise_votes_stats',
            'inputs':{
                'dataset':'WORKFLOW_PREPARED_DATASET.outputs.dataset'
            },
            'configuration':{
                #'granularity':20
                'votes_attributes':'PARAMETERS.outputs.votes_attributes', #first attribute is the unique identifier
                'users_attributes':'PARAMETERS.outputs.users_attributes', #first attribute is the unique identifier
                'position_attribute':'PARAMETERS.outputs.position_attribute',
                'user_1_scope':'PARAMETERS.outputs.user_1_scope',
                'user_2_scope':'PARAMETERS.outputs.user_2_scope'
            },
            'outputs':{
                'dataset':{}
            } 
        },
        
        {
            'id':'GENERAL_COMPARAISON',
            'type':'pairwise_comparaisons',
            'inputs':{
                'dataset':'GENERAL_STATS.outputs.dataset'
            },
            'configuration':{
                'method': 'PARAMETERS.outputs.comparaison_measure',
                'users_attributes':'PARAMETERS.outputs.users_attributes'
            },
            'outputs':{
                'dataset':[],
                'header':[]
            } 
        },
        {
            'id':'GENERAL_TRANFORMATOR',
            'type':'pairwise_comparaison_transform',
            'inputs':{
                'dataset':'GENERAL_COMPARAISON.outputs.dataset'  
            },
            'configuration':{
                'users_attributes':'PARAMETERS.outputs.users_attributes',
                'matrix_values' : 'SIMILARITY',
                'user1_sortDimension' :'PARAMETERS.outputs.user1_sortDimension',
                'user2_sortDimension' : 'PARAMETERS.outputs.user2_sortDimension',
                'user1_header' : 'PARAMETERS.outputs.user1_header',
                'user2_header' : 'PARAMETERS.outputs.user2_header'
            },
            'outputs':{
                'metadataDataset':[],
                'metadataHeader':[],
                'comparaisonMatrixDataset':[],
                'comparaisonGraphDataset':[]
            } 
        },
        {
            'id':'GENERAL_HEATMAP',
            'type':'heatmap_visualization',
            'inputs':{
                'dataset':'GENERAL_TRANFORMATOR.outputs.comparaisonMatrixDataset',
                'destinationFile':"PARAMETERS.outputs.repository +'\\general_heatmap.png'"
            },
            'configuration':{
                'vmin':0.0,
                'vmax':1.0,
                'color':'RdYlGn',
                'organize':'PARAMETERS.outputs.organizeHeatmaps',
                'title':'General ModelS'
            },
            'outputs':{
                    
            },
            'execute':'PARAMETERS.outputs.heatmap'
        },
        {
    
            'id':'WORKFLOW_GENERAL_MODEL',
            'type':'pipeliner',
            'inputs':{
                
            },
            'configuration':{
                'outputsFormula':{
                    'model_matrix':'GENERAL_TRANFORMATOR.outputs.comparaisonMatrixDataset',
                    'meps_count':'WORKFLOW_PREPARED_DATASET.outputs.meps_count',
                    
                }
            },
            'outputs':{
                
                
            }
        }
        
    ]
    
    
    workflow_patternsEnumerator=[     
        {
     
            'id':'PATTERN_ENUMERATOR',
            'type':'multiple_attributes_iterator_sgbitwise_subgroups',
            'inputs': {
                'dataset':'WORKFLOW_PREPARED_DATASET.outputs.dataset',
                'attributes':[
#                     {
#                         'name' : 'NATIONAL_PARTY',
#                         'type' : 'nominal',
#                         'bound_width': None
#                     },
                    {
                        'name' : 'PROCEDURE_SUBJECT',
                        'type' : 'themes2',
                        'bound_width': float('inf')
                    },
#                     {
#                         'name' : 'VOTE_DATE',
#                         'type' : 'numeric',
#                         'bound_width': None
#                     },
#                     {
#                         'name' : 'NATIONAL_PARTY',
#                         'type' : 'nominal',
#                         'bound_width': None
#                     },
#                     {
#                         'name' : 'NATIONAL_PARTY',
#                         'type' : 'nominal',
#                         'bound_width': None
#                     },
#                     {
#                         'name' : 'NATIONAL_PARTY',
#                         'type' : 'nominal',
#                         'bound_width': None
#                     }, 
                    
                    
#                     {
#                         'name':'COMMITTEE',
#                         'type':'simple',
#                         'bound_width': None
#                     },
                              
                              
#                     {
#                         'name':'PROCEDURE_TYPE',
#                         'type':'simple',
#                         'bound_width': None
#                     },
#                     {
#                         'name':'PROCEDURE_SUBTYPE',
#                         'type':'simple',
#                         'bound_width': None
#                     },          
#                     {
#                         'name':'DOSSIERID',
#                         'type':'simple',
#                         'bound_width': None
#                     },
#                     {
#                         'name' : 'NATIONAL_PARTY',
#                         'type' : 'nominal',
#                         'bound_width': 1   
#                     },
#                     
                ],
                
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
                
                'comparaison_measure':'PARAMETERS.outputs.comparaison_measure' 
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
                'themes_pattern':'PATTERN_ENUMERATOR.outputs.yielded_item[0]',
                'date_pattern':'PATTERN_ENUMERATOR.outputs.yielded_item[1]',
                'party_pattern':'PATTERN_ENUMERATOR.outputs.yielded_item[2]',
                'pattern_index':'PATTERN_ENUMERATOR.outputs.yielded_index',
                'bitwise':'PATTERN_ENUMERATOR.outputs.yielded_bitwise'
                
            },
            'configuration':{
                'outputsFormula':{
                    'pattern':'pattern',
                    'description':'description',
                    'themes_pattern':'themes_pattern',
                    'party_pattern':'party_pattern',
                    'date_pattern':'date_pattern',
                    'pattern_index':'pattern_index',
                    'bitwise_votes_subgroup':'bitwise[0]',
                    'bitwise_dossiers':'bitwise[1]'
                    
                    
                }
            },
            'outputs':{
                
                
            }
        },
        {
            'id':'DOSSIERS_THEME_VOTES_BY_MEPS_LOG',
            'type':'log_printer',
            'inputs':{
                'data':{
                    'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
                    'index':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern_index',
                    
                }
            },
            'configuration':{
                'printType':'default'
            },
            'outputs':{
                 
            },
            'execute':False
        }
        
    
    ]
    
    
    workflow_patterns_validity=[ 
        {
    
            'id':'WORKFLOW_PATTERN_VALIDITY',
            'type':'pipeliner',
            'inputs':{
                'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
                'themes_pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.themes_pattern',
                'date_pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.date_pattern',
                'subgroup':'PATTERN_ENUMERATOR.outputs.dataset',
                'meps_count':'float(DOSSIERS_FILTERED_AVERAGE_VOTES_BY_MEPS.outputs.dataset[0].COUNT_MEPS)'
            },
            'configuration':{
                'outputsFormula':{
                    'pattern':'pattern',
                    'themes_pattern':'themes_pattern',
                    'date_pattern':'date_pattern',
                    'subgroup':'subgroup',
                    'meps_count':'meps_count'
                    
                    
                    
                }
            },
            'outputs':{
                
                
            }
        }                        
    
    ]
    
    workflow_subgroupmodel=[

#         {
#             'id':'SUBGROUP_STATS',
#             'type':'pairwise_votes_stats',
#             'inputs':{
#                 'dataset':'WORKFLOW_PATTERN_VALIDITY.outputs.subgroup'
# 
#             },
#             'configuration':{
#                 'votes_attributes':'PARAMETERS.outputs.votes_attributes', #first attribute is the unique identifier
#                 'users_attributes':'PARAMETERS.outputs.users_attributes', #first attribute is the unique identifier
#                 'position_attribute':'PARAMETERS.outputs.position_attribute'
#             },
#             'outputs':{
#                 'dataset':{},
#                 'mepsStats':{}
#             } 
#         },
        {
            'id':'SUBGROUP_STATS_FILTER',
            'type':'filter',
            'inputs':{
                'dataset':'PATTERN_ENUMERATOR.outputs.pairwiseStatistics'
            },
            'configuration':{
                'pipeline':[
                    {
                        'dimensionName':'NB_VOTES',
                        'greaterThanOrEqual':'PARAMETERS.outputs.threshold_pair_comparaison'
                    }
                ]
      
            },
            'outputs':{
                'dataset':{}
            } 
        },       
              
        {
            'id':'SUBGROUP_COMPARAISON',
            'type':'pairwise_comparaisons',
            'inputs':{
                'dataset':'SUBGROUP_STATS_FILTER.outputs.dataset'
            },
            'configuration':{
                'users_attributes':'PARAMETERS.outputs.users_attributes',
                'method': 'PARAMETERS.outputs.comparaison_measure'
            },
            'outputs':{
                'dataset':[],
                'header':[]
            } 
        },
        
        {
            'id':'SUBGROUP_TRANFORMATOR',
            'type':'pairwise_comparaison_transform',
            'inputs':{
                'dataset':'SUBGROUP_COMPARAISON.outputs.dataset'  
            },
            'configuration':{
                'users_attributes':'PARAMETERS.outputs.users_attributes',
                'matrix_values' : 'SIMILARITY',
                'user1_sortDimension' :'PARAMETERS.outputs.user1_sortDimension',
                'user2_sortDimension' : 'PARAMETERS.outputs.user2_sortDimension',
                'user1_header' : 'PARAMETERS.outputs.user1_header',
                'user2_header' : 'PARAMETERS.outputs.user2_header'
            },
            'outputs':{
                'metadataDataset':[],
                'metadataHeader':[],
                'comparaisonMatrixDataset':[],
                'comparaisonGraphDataset':[]
            } 
        },
     
        {
    
            'id':'WORKFLOW_SUBGROUP_MODEL',
            'type':'pipeliner',
            'inputs':{
                'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
                'model_matrix':'SUBGROUP_TRANFORMATOR.outputs.comparaisonMatrixDataset',
                'meps_count':'WORKFLOW_PATTERN_VALIDITY.outputs.meps_count',
            },
            'configuration':{
                'outputsFormula':{
                    'pattern':'pattern',
                    'model_matrix':'model_matrix',
                    'meps_count':'meps_count',
                    
                }
            },
            'outputs':{
                
                
            }
        }
        
    ]
    
    workflow_modelcomparaison=[
        {
            'id':'MATRICES_ADAPTER',
            'type':'adapt_matrices',
            'inputs':{
                'matrix_1' : 'WORKFLOW_GENERAL_MODEL.outputs.model_matrix', #with header and rower
                'matrix_2' : 'WORKFLOW_SUBGROUP_MODEL.outputs.model_matrix' #with header and rower
            },
            'configuration':{
                'printType':'default'
            },
            'outputs':{
                'matrix_1' : [],
                'matrix_2' : []
            } 
        },        
        {
            'id':'MATRICES_DIFFERENCE',
            'type':'difference_matrices',
            'inputs':{
                'matrix_1' : 'MATRICES_ADAPTER.outputs.matrix_2', #with header and rower
                'matrix_2' : 'MATRICES_ADAPTER.outputs.matrix_1' #with header and rower
            },
            'configuration':{
                'printType':'default'
            },
            'outputs':{
                'matrix' : []
            } 
        },       
        {
            'id':'NORM_COMPUTER',
            'type':'norm_matrix_computer',
            'inputs':{
                'matrix' : 'MATRICES_DIFFERENCE.outputs.matrix' #with header and rower
            },
            'configuration':{
                'selectedNorm':'frobenius'
            },
            'outputs':{
                'norm':0 
            } 
        },
        {
            'id':'NORM_COMPUTER_MEPWISE',
            'type':'norm_matrix_computer',
            'inputs':{
                'matrix' : 'MATRICES_DIFFERENCE.outputs.matrix' #with header and rower
            },
            'configuration':{
                'selectedNorm':'mepwise'
            },
            'outputs':{
                'norm':0 
            } 
        },
#         {
#     
#             'id':'CORR_SIMILARITIES',
#             'type':'similarities_matrix_computer',
#             'inputs': {
#                 'matrix_1':'MATRICES_ADAPTER.outputs.matrix_2',
#                 'matrix_2':'MATRICES_ADAPTER.outputs.matrix_1'
#             },
#             'configuration': {
#                'selectedSimilarity':'cosinus' # mepwise 
#             },
#             'outputs':{
#                 'similarity':0 
#             }
#         },
        {
    
            'id':'WORKFLOW_MODEL_COMPARAISON',
            'type':'pipeliner',
            'inputs':{
                'pattern_index':"WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern_index",
                'pattern':"WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern",
                'description':"WORKFLOW_PATTERNS_ENUMERATOR.outputs.description",
                'qualityFrob':'NORM_COMPUTER.outputs.norm', #*((len(MATRICES_DIFFERENCE.outputs.matrix)-1)/(len(WORKFLOW_GENERAL_MODEL.outputs.model_matrix)-1))
                'qualityMepWise':'NORM_COMPUTER_MEPWISE.outputs.norm',
                #'correlation':'CORR_SIMILARITIES.outputs.similarity',
                'nbmeps':"float(len(MATRICES_DIFFERENCE.outputs.matrix)-1)",
                'nbtotal':"float((len(WORKFLOW_GENERAL_MODEL.outputs.model_matrix)-1))",
                'quality':'PATTERN_ENUMERATOR.outputs.quality',
                'upper_bound':'PATTERN_ENUMERATOR.outputs.upper_bound',
                'dossiers_voted':'PATTERN_ENUMERATOR.outputs.dossiers_voted'
            },
            'configuration':{
                'outputsFormula':{
                    'data':{
                        'pattern_index':"pattern_index",
                        'pattern':"pattern",
                        'description':"description",
                        'qualityFrob':'qualityFrob',
                        'qualityMepWise':'qualityMepWise',
                        #'correlation':'correlation',
                        'nbmeps':"nbmeps",
                        'nbtotal':"nbtotal",
                        'upper_bound':'upper_bound',
                        'quality':'quality',
                        'dossiers_voted':'dossiers_voted'
                    }
                    
                }
            },
            'outputs':{
                
                
            }
        }
                    
        
    ]
    
    workflow_final_syncer=[
        {
            'id':'SUBGROUP_HEATMAP',
            'type':'heatmap_visualization',
            'inputs':{
                'dataset':'MATRICES_ADAPTER.outputs.matrix_2',
                'destinationFile':"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAP_'+str(WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern_index)+'.jpg'"
            },
            'configuration':{
                'vmin':0.0,
                'vmax':1.0,
                'color':'RdYlGn',
                'organize':'PARAMETERS.outputs.organizeHeatmaps',
                'title':"WORKFLOW_MODEL_COMPARAISON.outputs.data.description"
            },
            'outputs':{
                    
            },
            'execute':'PARAMETERS.outputs.heatmap'
            #'(NORM_COMPUTER.outputs.norm*((len(MATRICES_DIFFERENCE.outputs.matrix)-1)/(len(GENERAL_TRANFORMATOR.outputs.comparaisonMatrixDataset)-1)))>0.02'
        },
        {
            'id':'SUBGROUP_HEATMAP_GENERAL',
            'type':'heatmap_visualization',
            'inputs':{
                'dataset':'MATRICES_ADAPTER.outputs.matrix_1',
                'destinationFile':"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAPGENERAL_'+str(WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern_index)+'.jpg'"
            },
            'configuration':{
                'vmin':0.0,
                'vmax':1.0,
                'color':'RdYlGn'
            },
            'outputs':{
                    
            },
            'execute':'PARAMETERS.outputs.heatmap_general'
            #'(NORM_COMPUTER.outputs.norm*((len(MATRICES_DIFFERENCE.outputs.matrix)-1)/(len(GENERAL_TRANFORMATOR.outputs.comparaisonMatrixDataset)-1)))>0.02'
        },
        {
            'id':'SUBGROUP_HEATMAP_DIFFERENCES',
            'type':'heatmap_visualization',
            'inputs':{
                'dataset':'MATRICES_DIFFERENCE.outputs.matrix',
                'destinationFile':"PARAMETERS.outputs.repository+'\\Subgroup_Heatmap\\HEATMAPDIFFERENCES_'+str(WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern_index)+'.jpg'"
            },
            'configuration':{
                'vmin':-1.0,
                'vmax':1.0,
                'color':'RdYlGn'
            },
            'outputs':{
                    
            },
            'execute':'PARAMETERS.outputs.heatmap_diff'
            #'(NORM_COMPUTER.outputs.norm*((len(MATRICES_DIFFERENCE.outputs.matrix)-1)/(len(GENERAL_TRANFORMATOR.outputs.comparaisonMatrixDataset)-1)))>0.02'
        },
        {
            'id':'FINAL_SYNCER',
            'type':'flatAppenderSyncer',
            'inputs':{
                'data':'WORKFLOW_MODEL_COMPARAISON.outputs.data'
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
                'selectedHeader':['pattern_index','pattern','description','quality','upper_bound','qualityFrob','qualityMepWise','nbmeps','nbtotal','dossiers_voted']
            },
            'outputs':{
                
            } 
        },
        {
            'id':'FINAL_LOG',
            'type':'log_printer',
            'inputs':{
                'data':'FINAL_SYNCER.outputs.syncedData',
            },
            'configuration':{
                'printType':'dataset'
            },
            'outputs':{
                
            },
            'execute':False
        }
    ]

    workflowFinal=wokflow_parameters+workflow_prepdataset+workflow_generalmodel+workflow_patternsEnumerator+workflow_patterns_validity+workflow_subgroupmodel+workflow_modelcomparaison+workflow_final_syncer

#     pr = cProfile.Profile()
#     pr.enable()

    #process_workflow_recursive(workflowFinal, verbose=False)
    
    
    sampleWorkflow=[
        {
            'id':'VOTES_READER',
            'type':'csvReader',
            'inputs':{
                'sourceFile':'/home/nassim/Bureau/exemple_pour_plateforme/export.csv'
            },
            'configuration':{
                'hasHeader':True,
                'arrayHeader':['PROCEDURE_SUBJECT'],
                'numberHeader':['VOTE_DATE','AGE']
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
                    {
                        'dimensionName':'COUNTRY',
                        'equal':'France'
                    },
                    {
                        'dimensionName':'NATIONAL_PARTY',
                        'inSet':['Front national','Parti socialiste']
                    }                     
                ]
            },
            'outputs':{
                'dataset':{}
            }
        },
        {
            'id':'GENERAL_MEPS_COUNTER',
            'type':'aggregator',
            'inputs':{
                'dataset': 'GENERAL_FILTER.outputs.dataset'
            },
            'configuration':{
                'dimensions':{
                    'NATIONAL_PARTY':'NATIONAL_PARTY'
                },
                'measures':{
                    'MEPS_COUNT':{
                        'count_distinct':'EP_ID'
                    }
                }
            },
            'outputs':{
                'dataset':{},
                'header':{}
            } 
        }, 
        {
            'id':'QUALITIES_CSV_WRITER',
            'type':'csvWriter',
            'inputs':{
                'dataset':'GENERAL_MEPS_COUNTER.outputs.dataset',
                'destinationFile':"C:\\Users\\Adnene\\Desktop\\WORKING_REPO\\json\\output.csv" 
            },
            'configuration':{
                'hasHeader': True
            },
            'outputs':{
                
            } 
        }            
    ]
    #writeJSON(sampleWorkflow, 'C:\\Users\\Adnene\\Desktop\\WORKING_REPO\\json\\workflow.json')
    
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("sourceFile", help="get the sourceFile")
    args = parser.parse_args()
    
    
    #print readJSON_stringifyUnicodes('C:\\Users\\Adnene\\Desktop\\WORKING_REPO\\json\\workflow.json')
    
    
    
    process_workflow_recursive(readJSON_stringifyUnicodes(args.sourceFile), verbose=True)
    
#     #908     234     212     175     28
    #1328     241     222     181     26
#     pr.disable()
#     ps = pstats.Stats(pr)
#     ps.sort_stats('time').print_stats(100) #cumulative
       
    #cProfile.run('process_workflow_recursive(workflowFinal, verbose=False)') #SIMILARITY MEASURE TAKE TIME
    #process_workflow_recursive(workflowFinal, verbose=False)
    
    #
    
    
    
    
    
    
    
    
    
    
