'''
Created on 6 janv. 2017

@author: Adnene
'''
from workflows.workflowsProcessing_Pypy import process_workflow_recursive


repository='C:\\Users\\Adnene\\Desktop\\ExperimentsDB'    
    
update_skip_list='sourceArr+list(pattern)' #sourceArr+
wokflow_parameters=[
    {

        'id':'PARAMETERS',
        'type':'pipeliner',
        'inputs':{
            
        },
        'configuration':{
            'outputsFormula':{
                'repository':'C:\\Users\\Adnene\\Desktop\\WORKING_REPO',
                'country':'France',#,'Les R\xe9publicains','Union pour un Mouvement Populaire' #,'Front national'
                'party':['Les R\xc3\xa9publicains'],#['Les R\xc3\xa9publicains','Front national','Parti socialiste'],#'Les R\xe9publicains','Union pour un Mouvement Populaire',
                'threshold_voters_avg':25,
                'threshold_pair_comparaison':25,
                'nb_dossiers_threshold':15,
                'comparaison_measure':'AGREEMENT_ABST',
                'meps_proportion':0.2,
                'depth':2,
                'date_interval':[2014,2016],
                #######################"
                'votes_attributes':['VOTEID','DOSSIERID','VOTE_DATE','PROCEDURE_SUBJECT','PROCEDURE_TITLE'], #first attribute is the unique identifier
                'users_attributes':['EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','GENDER','AGE'], #first attribute is the unique identifier
                'position_attribute':'USER_VOTE',
                'user1_sortDimension' :'USER1_NATIONAL_PARTY',
                'user2_sortDimension' : 'USER2_NATIONAL_PARTY',
                'user1_header' : 'USER1_NAME_FULL',
                'user2_header' : 'USER2_NAME_FULL'
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
            'sourceFile':"PARAMETERS.outputs.repository+'\\France.csv'"
        },
        'configuration':{
            'hasHeader':True,
            'arrayHeader':['PROCEDURE_SUBJECT']
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
                    'equal':'PARAMETERS.outputs.country'
                },
                {
                    'dimensionName':'NATIONAL_PARTY',
                    'inSet':'PARAMETERS.outputs.party'
                }
                
            ]
        },
        'outputs':{
            'dataset':{}
        }
    },
    {
        'id':'GENERAL_AGGREGATOR_VOTES',
        'type':'aggregator',
        'inputs':{
            'dataset': 'GENERAL_FILTER.outputs.dataset'
        },
        'configuration':{
            'dimensions':{
                'VOTEID':'VOTEID',
                'DOSSIERID':'DOSSIERID',
                'VOTE_DATE':'VOTE_DATE'
                
            },
            'measures':{
                
            }
        },
        'outputs':{
            'dataset':{},
            'header':{}
        } 
    },
    {
        'id':'GENERAL_AGGREGATOR_MEPS',
        'type':'aggregator',
        'inputs':{
            'dataset': 'GENERAL_FILTER.outputs.dataset'
        },
        'configuration':{
            'dimensions':{
                'EP_ID':'EP_ID',
                'NAME_FULL':'NAME_FULL',
                'NATIONAL_PARTY':'NATIONAL_PARTY',
                'GROUPE_ID':'GROUPE_ID',
                'COUNTRY':'COUNTRY',
                'GENDER':'GENDER',
                'AGE':'AGE'
            },
            'measures':{
                'VOTES':{
                    'set_append':'VOTEID'
                }
            }
        },
        'outputs':{
            'dataset':{},
            'header':{}
        } 
    },
#         {
#             'id':'FILTERED_CSV_WRITER',
#             'type':'csvWriter',
#             'inputs':{
#                 'dataset':'GENERAL_FILTER.outputs.dataset',
#                 'destinationFile':"PARAMETERS.outputs.repository+'\\France.csv'" 
#             },
#             'configuration':{
#                 'hasHeader': True,
#             },
#             'outputs':{
#                 
#             } 
#         },
    
    
    {

        'id':'DISTINCT_VALUES_GETTER',
        'type':'aggregator',
        'inputs': {
            'dataset':'GENERAL_FILTER.outputs.dataset'
        },
        'configuration': {
            'dimensions':{
            },
            'measures':{
                'PARTIES':{
                    'set_append':'NATIONAL_PARTY' 
                    #count | count_distinct | sum | min | max | avg | append | set_append 
                },
                'DATES':{
                    'set_append':'int(VOTE_DATE)' 
                    #count | count_distinct | sum | min | max | avg | append | set_append 
                },
                'GENDERS':{
                    'set_append':'GENDER' 
                    #count | count_distinct | sum | min | max | avg | append | set_append 
                }
            }
        },
        'outputs':{
            'dataset':[],
            'header':[]
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
        'id':'THEMES_FILE_READER',
        'type':'csvReader',
        'inputs':{
            'sourceFile':"PARAMETERS.outputs.repository+'\\Allthemes.txt'"#'\\themesALL.txt' #themesALL.txt
        },
        'configuration':{
            'hasHeader':True
        },
        'outputs':{
            'dataset':{}
        } 
    },
    
    {
        'id':'DOSSIERS_FILE_READER',
        'type':'csvReader',
        'inputs':{
            'sourceFile':"PARAMETERS.outputs.repository+'\\Themes.csv'" 
        },
        'configuration':{
            'hasHeader':True
        },
        'outputs':{
            'dataset':{}
        } 
    },
    {
        'id':'DOSSIERS_AGGREGATOR_ON_THEMES',
        'type':'aggregator',
        'inputs': {
            'dataset':'DOSSIERS_FILE_READER.outputs.dataset'
        },
        'configuration': {
            'dimensions':{
                'DOSSIERID':'DOSSIERID'
            },
            'measures':{
                'SUBJECTS':{
                    'append':"SUBJECTS_CODE"  #SUBJECTS_CODE+ ' ' + SUBJECTS_LABEL
                } 
            }
        },
        'outputs':{
            'dataset':[],
            'header':[]
        } 
    },
    {

        'id':'WORKFLOW_PREPARED_DATASET',
        'type':'pipeliner',
        'inputs':{
            'dataset':'GENERAL_FILTER.outputs.dataset',
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
                'dossiers':'dossiers', #PROBLEM EVAL EXPRESSION TURN STRING TO FLOAT ! NOOO DON't DO THAT
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
            'position_attribute':'PARAMETERS.outputs.position_attribute'
        },
        'outputs':{
            'dataset':{},
            'mepsStats':{}, #GENERAL_STATS.outputs.mepsStats
            'mepsMeta':{}, #GENERAL_STATS.outputs.mepsMeta
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
            'destinationFile':repository+'\\general_heatmap.png'
        },
        'configuration':{
            'vmin':0.0,
            'vmax':1.0,
            'color':'RdYlGn'
        },
        'outputs':{
                
        },
        'execute':False
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

        'id':'BITWISES_VISITED', 
        'type':'pipeliner',
        'inputs':{
            
            
        },
        'configuration':{
            'outputsFormula':{
                'bitwises_visited_dossiers':[],
                'bitwises_visited_votes':[],
                'bitwises_visited_meps':[]
            }
        },
        'outputs':{
            
            
        }
    },
    {

        'id':'PATTERNS_VISITED', 
        'type':'pipeliner',
        'inputs':{
            
            
        },
        'configuration':{
            'outputsFormula':{
                'patterns':[]
            }
        },
        'outputs':{
            
            
        }
    },
    {

        'id':'PATTERN_ENUMERATOR',
        'type':'multiple_attributes_iterator_sgbitwise',
        'inputs': {
            'array_data':['WORKFLOW_PREPARED_DATASET.outputs.themes','sorted(WORKFLOW_PREPARED_DATASET.outputs.dates)','WORKFLOW_PREPARED_DATASET.outputs.parties'],
            'attibutes_types' : ['themes','numeric','nominal'],
            'depth_max' : [2,7,None]
        },
        'configuration': {
            'skip_list':[],
            'bitwise':[None,None,None]
        },
        'outputs':{
            'yielded_item':'',
            'yielded_index':'',
            'yielded_description':'',
            'yielded_bitwise':[None,None,None]
        }
    },
#         {
#        
#             'id':'REINIT_ENUMERATOR_BITWISE',
#             'type':'pipeliner',
#             'inputs': {
#                 'bitwise':None
#             },
#             'configuration': {
#                 'replace':True,
#                 'outputsFormula':{
#                     'PATTERN_ENUMERATOR.configuration.bitwise':'bitwise'
#                 }
#             },
#             'outputs':{
#                   
#             }
#         },
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
                'bitwise_dossiers':'bitwise[1]',
                'bitwise_meps':'bitwise[2]'
                
                
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

        'id':'THEMES_REGEXP',
        'type':'projecter',
        'inputs': {
            'array':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.themes_pattern'#['4.15','4.15.05']#'columnGetter.outputs.array'
        },
        'configuration': {
            'projection':"value+'%'"
        },
        'outputs':{
            'array':[],
            
        }
    },
    
    
    
    {
        'id':'DOSSIERS_FILTERED',
        'type':'filter',
        'inputs':{
            'dataset':'WORKFLOW_PREPARED_DATASET.outputs.dossiers'
        },
        'configuration':{
            'pipeline':[
                {
                    'dimensionName':'SUBJECTS',
                    'likeContainSet':"THEMES_REGEXP.outputs.array"#["THEMES_ITERATOR.outputs.yielded_item+'%'","%"]
                }
            ],
            'bitwise':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_dossiers'
        },
        'outputs':{
            'dataset':[],
            'bitwise':None
        }
    },  
#         {
#        
#             'id':'UPDATE_ENUMERATOR_BITWISE',
#             'type':'pipeliner',
#             'inputs': {
#                 'bitwise_votes':None,
#                 'bitwise_dossiers':'DOSSIERS_FILTERED.outputs.bitwise'
#             },
#             'configuration': {
#                 'replace':True,
#                 'outputsFormula':{
#                     'PATTERN_ENUMERATOR.configuration.bitwise':[None,'bitwise_dossiers']
#                 }
#             },
#             'outputs':{
#                   
#             }
#         },
                             
    {
        'id':'DOSSIERS_FILTERED_COLUMN_PROJECTOR',
        'type':'projecter',
        'inputs':{
            'dataset': 'DOSSIERS_FILTERED.outputs.dataset'
        },
        'configuration':{
            'projection':{
                'DOSSIERID':'DOSSIERID'
            }
        },
        'outputs':{
            'column':[]
        } 
    },
    
                            
#         {
#       
#             'id':'UPDATE_NON_VALID_PATTERNS_1',
#             'type':'pipeliner',
#             'inputs': {
#                 'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
#                 'sourceArr':'PATTERN_ENUMERATOR.configuration.skip_list'
#             },
#             'configuration': {
#                 'replace':True,
#                 'outputsFormula':{
#                     'PATTERN_ENUMERATOR.configuration.skip_list':update_skip_list
#                 }
#             },
#             'outputs':{
#                  
#             },
#             'execute':'len(DOSSIERS_FILTERED_COLUMN_PROJECTOR.outputs.column)<PARAMETERS.outputs.nb_dossiers_threshold' # and len(THEMES_ITERATOR.outputs.yielded_item)==1
#         },
#         
#                                 
#         {
#             'id':'MATCHER_VALID_PATTERN_1',
#             'type':'simpleMatcher',
#             'inputs':{
#                 'value':'len(DOSSIERS_FILTERED_COLUMN_PROJECTOR.outputs.column)'
#             },
#             'configuration':{
#                 'pipeline':[
#                     
#                     {
#                         'greaterThanOrEqual':'PARAMETERS.outputs.nb_dossiers_threshold'
#                     }
#                 ]
#             },
#             'outputs':{
#                 'value':{}
#             }
#         },
    
    {
        'id':'VOTES_SUBGROUP_VOTES',
        'type':'filter',
        'inputs':{
            'dataset':'GENERAL_AGGREGATOR_VOTES.outputs.dataset'
            
        },
        'configuration':{
            'pipeline':[
                {
                    'dimensionName':'DOSSIERID',
                    'inSet':'DOSSIERS_FILTERED_COLUMN_PROJECTOR.outputs.column'
                },
                {
                    'dimensionName':'VOTE_DATE',
                    'inInterval':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.date_pattern'
                }
            ],
            'bitwise':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_votes_subgroup'
        },
        'outputs':{
            'dataset':[],
            'bitwise':None
        }
    },
    {
        'id':'VOTES_SUBGROUP_VOTES_COUNT_DOSSIERS',
        'type':'aggregator',
        'inputs':{
            'dataset': 'VOTES_SUBGROUP_VOTES.outputs.dataset'
        },
        'configuration':{
            'dimensions':{
                
            },
            'measures':{
                'DOSSIERS_COUNT':{
                    'count_distinct':'DOSSIERID'
                }
            }
        },
        'outputs':{
            'dataset':{},
            'header':{}
        } 
    },
#         {
#         
#             'id':'LOGGGGGER',
#             'type':'log_printer',
#             'inputs': {
#                 'data' :'VOTES_SUBGROUP_VOTES_COUNT_DOSSIERS.outputs.dataset'
#             },
#             'configuration': {
#                'printType':'default' # dataset | matrix
#             },
#             'outputs':{
#             }
#         },  
    {
        'id':'VOTES_SUBGROUP_VOTES_PROJECTER',
        'type':'projecter',
        'inputs':{
            'dataset':'VOTES_SUBGROUP_VOTES.outputs.dataset'
            
        },
        'configuration':{
            'projection':{
                'VOTEID':'VOTEID'
            }
            #'bitwise':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_votes_subgroup'
        },
        'outputs':{
            'dataset':[],
            'column':[]
        }
    
    },
    
    {
   
        'id':'VOTES_SUBGROUP_VOTES_PROJECTER_SET',
        'type':'pipeliner',
        'inputs': {
            'votes_array':'VOTES_SUBGROUP_VOTES_PROJECTER.outputs.column'
        },
        'configuration': {
            'outputsFormula':{
                'votes_set':'toSet(votes_array)'
            }
        },
        'outputs':{
              
        }
    },
    
    {
        'id':'VOTES_SUBGROUP_MEPS',
        'type':'filter',
        'inputs':{
            'dataset':'GENERAL_AGGREGATOR_MEPS.outputs.dataset'
            
        },
        'configuration':{
            'pipeline':[
                {
                    'dimensionName':'NATIONAL_PARTY',
                    'inSet':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.party_pattern'
                }
            ],
            'bitwise':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_meps'             
        },
        'outputs':{
            'dataset':[],
            'bitwise':None
        }
    },
    {
        'id':'VOTES_SUBGROUP_VOTES_MEPS',
        'type':'projecter',
        'inputs':{
            'dataset':'VOTES_SUBGROUP_MEPS.outputs.dataset',
            'votes_set':'VOTES_SUBGROUP_VOTES_PROJECTER_SET.outputs.votes_set'
            
        },
        'configuration':{
            'projection':{
                'EP_ID':'EP_ID',
                'NAME_FULL':'NAME_FULL',
                'NATIONAL_PARTY':'NATIONAL_PARTY',
                'GROUPE_ID':'GROUPE_ID',
                'COUNTRY':'COUNTRY',
                'GENDER':'GENDER',
                'AGE':'AGE',
                'VOTES':'intersection(VOTES,votes_set)'
            }
            #'bitwise':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_votes_subgroup'
        },
        'outputs':{
            'dataset':[],
            'column':[]
        }
    
    },
    {
        'id':'VOTES_SUBGROUP_VOTES_MEPS_COUNT_VOTES',
        'type':'aggregator',
        'inputs':{
            'dataset': 'VOTES_SUBGROUP_VOTES_MEPS.outputs.dataset'
        },
        'configuration':{
            'dimensions':{
                'EP_ID':'EP_ID',
                'COUNT_VOTES_BY_MEPS':'len(VOTES)'
            },
            'measures':{
                
            }
        },
        'outputs':{
            'dataset':{},
            'header':{}
        } 
    },
    {
        'id':'VOTES_SUBGROUP_VOTES_MEPS_COUNT_VOTES_FILTER',
        'type':'filter',
        'inputs':{
            'dataset': 'VOTES_SUBGROUP_VOTES_MEPS_COUNT_VOTES.outputs.dataset'
        },
        'configuration':{
            'pipeline':[
                {
                    'dimensionName':'COUNT_VOTES_BY_MEPS',
                    'greaterThanOrEqual':0.01
                }
            
            ]
        },
        'outputs':{
            'dataset':{},
            'header':{}
        } 
    },
    {
        'id':'VOTES_SUBGROUP_VOTES_MEPS_AVERAGE',
        'type':'aggregator',
        'inputs':{
            'dataset': 'VOTES_SUBGROUP_VOTES_MEPS_COUNT_VOTES_FILTER.outputs.dataset'
        },
        'configuration':{
            'dimensions':{
            },
            'measures':{
                'AVERAGE_VOTES_BY_MEPS':{
                    'avg':'COUNT_VOTES_BY_MEPS'
                },
                'COUNT_MEPS':{
                    'count_distinct':'EP_ID'
                },
                'MEPS':{
                    'set_append':'EP_ID'
                }
            }
        },
        'outputs':{
            'dataset':{},
            'header':{}
        } 
    },
    {

        'id':'PIPELINER_TO_VERIFY',
        'type':'pipeliner',
        'inputs':{
            'dossiers_count':'VOTES_SUBGROUP_VOTES_COUNT_DOSSIERS.outputs.dataset[0].DOSSIERS_COUNT',
            'average_votes_by_meps':'VOTES_SUBGROUP_VOTES_MEPS_AVERAGE.outputs.dataset[0].AVERAGE_VOTES_BY_MEPS',
            'count_meps':'VOTES_SUBGROUP_VOTES_MEPS_AVERAGE.outputs.dataset[0].COUNT_MEPS',
            'old_bitwise_votes':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_votes_subgroup',
            'old_bitwise_dossiers':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_dossiers',
            'old_bitwise_meps':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_meps',
            'bitwise_dossiers':'DOSSIERS_FILTERED.outputs.bitwise',
            'bitwise_votes':'VOTES_SUBGROUP_VOTES.outputs.bitwise',
            'bitwise_meps':'VOTES_SUBGROUP_MEPS.outputs.bitwise',
            'selected_votes':'VOTES_SUBGROUP_VOTES_PROJECTER_SET.outputs.votes_set',
            'selected_meps':'VOTES_SUBGROUP_VOTES_MEPS_AVERAGE.outputs.dataset[0].MEPS',
            
        },
        'configuration':{
            'outputsFormula':{
                'dossiers_count':'dossiers_count', 
                'average_votes_by_meps':'average_votes_by_meps',
                'count_meps':'count_meps',
                
                'old_bitwise_dossiers':'old_bitwise_dossiers',
                'old_bitwise_votes':'old_bitwise_votes',
                'old_bitwise_meps':'old_bitwise_meps',
                
                'bitwise_dossiers':'bitwise_dossiers',
                'bitwise_votes':'bitwise_votes',
                'bitwise_meps':'bitwise_meps',
                
                'selected_votes':'selected_votes',
                'selected_meps':'selected_meps'
            }
        },
        'outputs':{
               
        }
    }, 
    
#         {
#     
#             'id':'BITWISES_VISITED_COVER_COMPUTATION',
#             'type':'projecter',
#             'inputs': {
#                 'array':'BITWISES_VISITED.outputs.bitwises_visited_dossiers',#['4.15','4.15.05']#'columnGetter.outputs.array'
#                 'toVerifyWith':'PIPELINER_TO_VERIFY.outputs.bitwise_dossiers'
#             },
#             'configuration': {
#                 'projection':"cover(toVerifyWith,value)"
#             },
#             'outputs':{
#                 'array':[]
#                 
#             }
#         },
#         {
#     
#             'id':'BITWISES_VISITED_COVER_COMPUTATION_MAX_ARGS', 
#             'type':'pipeliner',
#             'inputs':{
#                 'cover_array':'BITWISES_VISITED_COVER_COMPUTATION.outputs.array'
#             },
#             'configuration':{
#                 'outputsFormula':{
#                     'coverMax':'max(cover_array)'
#                 }
#             },
#             'outputs':{
#                 
#                 
#             }
#         },
#         {
#         
#             'id':'LOGGGGGGGER',
#             'type':'log_printer',
#             'inputs': {
#                 'data' :'BITWISES_VISITED_COVER_COMPUTATION_MAX_ARGS.outputs'
#             },
#             'configuration': {
#                'printType':'default' # dataset | matrix
#             },
#             'outputs':{
#             }
#         },
#         {
#         
#             'id':'LOGGGGGGGER',
#             'type':'log_printer',
#             'inputs': {
#                 'data' :'BITWISES_VISITED_COVER_COMPUTATION.outputs.array'
#             },
#             'configuration': {
#                'printType':'break' # dataset | matrix
#             },
#             'outputs':{
#             },
#             'execute':False
#             
#         },

    
#         {
#        
#             'id':'LOGGGGGER',
#             'type':'log_printer',
#             'inputs': {
#                 'data' :['PIPELINER_TO_VERIFY.outputs.dossiers_count','PIPELINER_TO_VERIFY.outputs.average_votes_by_meps','PIPELINER_TO_VERIFY.outputs.count_meps']
#             },
#             'configuration': {
#                'printType':'default' # dataset | matrix
#             },
#             'outputs':{
#             }
#         },                        
#         {
#             'id':'VOTES_SUBGROUP',
#             'type':'filter',
#             'inputs':{
#                 'dataset':'WORKFLOW_PREPARED_DATASET.outputs.dataset'
#                 
#             },
#             'configuration':{
#                 'pipeline':[
#                     {
#                         'dimensionName':'DOSSIERID',
#                         'inSet':'DOSSIERS_FILTERED_COLUMN_PROJECTOR.outputs.column'
#                     },
#                     {
#                         'dimensionName':'NATIONAL_PARTY',
#                         'inSet':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.party_pattern'
#                     },
#                     {
#                         'dimensionName':'VOTE_DATE',
#                         'inInterval':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.date_pattern'
#                     }
#                 ],
#                 'bitwise':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.bitwise_votes_subgroup'
#             },
#             'outputs':{
#                 'dataset':[],
#                 'bitwise':None
#             }
#         },
    {
   
        'id':'UPDATE_ENUMERATOR_BITWISE_1',
        'type':'pipeliner',
        'inputs': {
            'bitwise_votes':'PIPELINER_TO_VERIFY.outputs.bitwise_votes',
            'bitwise_dossiers':'PIPELINER_TO_VERIFY.outputs.bitwise_dossiers',
            'bitwise_meps':'PIPELINER_TO_VERIFY.outputs.bitwise_meps'
        },
        'configuration': {
            'replace':True,
            'outputsFormula':{
                'PATTERN_ENUMERATOR.configuration.bitwise':['bitwise_votes','bitwise_dossiers','bitwise_meps']
            }
        },
        'outputs':{
              
        }
    },
    
#         {
#        
#             'id':'coverability',
#             'type':'pipeliner',
#             'inputs': {
#                 'bitwise_votes':'VOTES_SUBGROUP.outputs.bitwise',
#                 'bitwise_dossiers':'DOSSIERS_FILTERED.outputs.bitwise'
#             },
#             'configuration': {
#                 
#                 'outputsFormula':{
#                     'cover':[None,'bitwise_dossiers']
#                 }
#             },
#             'outputs':{
#                   
#             }
#         },  
#         {
#       
#             'id':'LOGGGGGER',
#             'type':'log_printer',
#             'inputs': {
#                 'data' :'WORKFLOW_PREPARED_DATASET.outputs.dataset[0]'
#             },
#             'configuration': {
#                'printType':'default' # dataset | matrix
#             },
#             'outputs':{
#             }
#         }, 
#         {
#       
#             'id':'UPDATE_EMPTY_SUBGROUP_NON_VALID',
#             'type':'pipeliner',
#             'inputs': {
#                 'sourceArr':'PATTERN_ENUMERATOR.configuration.skip_list',
#                 'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern'
#             },
#             'configuration': {
#                 'replace':True,
#                 'outputsFormula':{
#                     'PATTERN_ENUMERATOR.configuration.skip_list':update_skip_list
#                 }
#             },
#             'outputs':{
#                  
#             },
#             'execute':'len(VOTES_SUBGROUP.outputs.dataset)<1' # and len(THEMES_ITERATOR.outputs.yielded_item)==1
#         },                
#         {
#             'id':'SUBGROUP_EMPTY_MATCHER',
#             'type':'simpleMatcher',
#             'inputs':{
#                 'value':'len(VOTES_SUBGROUP.outputs.dataset)'
#             },
#             'configuration':{
#                 'pipeline':[
#                     
#                     {
#                         'greaterThanOrEqual':1
#                     }
#                 ]
#             },
#             'outputs':{
#                 'value':{}
#             }
#         },
#                                                         
#         {
#             'id':'SUBGROUP_DOSSIERS_COUNTER',
#             'type':'aggregator',
#             'inputs':{
#                 'dataset': 'VOTES_SUBGROUP.outputs.dataset'
#             },
#             'configuration':{
#                 'dimensions':{
#                     
#                 },
#                 'measures':{
#                     'DOSSIERS_COUNT':{
#                         'count_distinct':'DOSSIERID'
#                     }
#                 }
#             },
#             'outputs':{
#                 'dataset':{},
#                 'header':{}
#             } 
#         },
                            
    {
  
        'id':'UPDATE_NON_VALID_PATTERNS_2',
        'type':'pipeliner',
        'inputs': {
            'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
            'sourceArr':'PATTERN_ENUMERATOR.configuration.skip_list'
        },
        'configuration': {
            'replace':True,
            'outputsFormula':{
                'PATTERN_ENUMERATOR.configuration.skip_list':update_skip_list
            }
        },
        'outputs':{
             
        },
        'execute':'PIPELINER_TO_VERIFY.outputs.dossiers_count<PARAMETERS.outputs.nb_dossiers_threshold' # and len(THEMES_ITERATOR.outputs.yielded_item)==1
    },
                            
    {
        'id':'MATCHER_VALID_PATTERN_2',
        'type':'simpleMatcher',
        'inputs':{
            'value':'PIPELINER_TO_VERIFY.outputs.dossiers_count'
        },
        'configuration':{
            'pipeline':[
                
                {
                    'greaterThanOrEqual':'PARAMETERS.outputs.nb_dossiers_threshold'
                }
            ]
        },
        'outputs':{
            'value':{}
        }
    },
                                                                            
    
    
#         {
#             'id':'DOSSIERS_FILTERED_COUNT_VOTES_BY_MEPS',
#             'type':'aggregator',
#             'inputs':{
#                 'dataset': 'VOTES_SUBGROUP.outputs.dataset'
#             },
#             'configuration':{
#                 'dimensions':{
#                     'EP_ID':'EP_ID'
#                 },
#                 'measures':{
#                     'COUNT_VOTES_BY_MEPS':{
#                         'count':''
#                     }
#                 }
#             },
#             'outputs':{
#                 'dataset':{},
#                 'header':{}
#             } 
#         },
#         {
#             'id':'DOSSIERS_FILTERED_AVERAGE_VOTES_BY_MEPS',
#             'type':'aggregator',
#             'inputs':{
#                 'dataset': 'DOSSIERS_FILTERED_COUNT_VOTES_BY_MEPS.outputs.dataset'
#             },
#             'configuration':{
#                 'dimensions':{
#                 },
#                 'measures':{
#                     'AVERAGE_VOTES_BY_MEPS':{
#                         'avg':'COUNT_VOTES_BY_MEPS'
#                     },
#                     'COUNT_MEPS':{
#                         'sum':1
#                     }
#                 }
#             },
#             'outputs':{
#                 'dataset':{},
#                 'header':{}
#             } 
#         },
#         {
#        
#             'id':'LOGGGGGER',
#             'type':'log_printer',
#             'inputs': {
#                 'data' :['float(DOSSIERS_FILTERED_AVERAGE_VOTES_BY_MEPS.outputs.dataset[0].AVERAGE_VOTES_BY_MEPS)','float(VOTES_SUBGROUP_VOTES_MEPS_AVERAGE.outputs.dataset[0].AVERAGE_VOTES_BY_MEPS)']
#             },
#             'configuration': {
#                'printType':'default' # dataset | matrix
#             },
#             'outputs':{
#             }
#         },                         
    {
  
        'id':'UPDATE_NON_VALID_PATTERNS_3',
        'type':'pipeliner',
        'inputs': {
            'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
            'sourceArr':'PATTERN_ENUMERATOR.configuration.skip_list'
        },
        'configuration': {
            'replace':True,
            'outputsFormula':{
                'PATTERN_ENUMERATOR.configuration.skip_list':update_skip_list
            }
        },
        'outputs':{
             
        },
        'execute':'PIPELINER_TO_VERIFY.outputs.average_votes_by_meps<PARAMETERS.outputs.threshold_voters_avg' # and len(THEMES_ITERATOR.outputs.yielded_item)==1
    },
                            
                            
    {
        'id':'MATCHER_VALID_PATTERN_3',
        'type':'simpleMatcher',
        'inputs':{
            'value':'PIPELINER_TO_VERIFY.outputs.average_votes_by_meps'
        },
        'configuration':{
            'pipeline':[
                
                {
                    'greaterThanOrEqual':'PARAMETERS.outputs.threshold_voters_avg'
                }
            ]
        },
        'outputs':{
            'value':{}
        }
    },
    {
  
        'id':'UPDATE_NON_VALID_PATTERNS_4',
        'type':'pipeliner',
        'inputs': {
            'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
            'sourceArr':'PATTERN_ENUMERATOR.configuration.skip_list'
        },
        'configuration': {
            'replace':True,
            'outputsFormula':{
                'PATTERN_ENUMERATOR.configuration.skip_list':update_skip_list
            }
        },
        'outputs':{
             
        },
        'execute':'(float(PIPELINER_TO_VERIFY.outputs.count_meps)/float(WORKFLOW_PREPARED_DATASET.outputs.meps_count))<PARAMETERS.outputs.meps_proportion' # and len(THEMES_ITERATOR.outputs.yielded_item)==1
    },                        
    {
        'id':'MATCHER_VALID_PATTERN_4',
        'type':'simpleMatcher',
        'inputs':{
            'value':'float(PIPELINER_TO_VERIFY.outputs.count_meps)/float(WORKFLOW_PREPARED_DATASET.outputs.meps_count)'
        },
        'configuration':{
            'pipeline':[
                 
                {
                    'greaterThanOrEqual':"PARAMETERS.outputs.meps_proportion"
                }
            ]
        },
        'outputs':{
            'value':{}
        }
    },
#         {
#       
#             'id':'BITWISES_VISITED_COVER_COMPUTATION_DOSSIERS',
#             'type':'misc_cover',
#             'inputs': {
#                 'bitwise':'toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_dossiers)',
#                 'bitwises_array':'BITWISES_VISITED.outputs.bitwises_visited_dossiers'
#             },
#             'configuration': {
#                  
#             },
#             'outputs':{
#                 'cover':0
#             }
#         }, 
#         {
#        
#             'id':'BITWISES_VISITED_COVER_COMPUTATION_VOTES',
#             'type':'misc_cover',
#             'inputs': {
#                 'bitwise':'toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_votes)',
#                 'bitwises_array':'BITWISES_VISITED.outputs.bitwises_visited_votes'
#             },
#             'configuration': {
#                   
#             },
#             'outputs':{
#                 'cover':0
#             }
#         },
#         {
#       
#             'id':'BITWISES_VISITED_COVER_COMPUTATION_MEPS',
#             'type':'misc_cover',
#             'inputs': {
#                 'bitwise':'toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_meps)',
#                 'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
#                 'bitwises_array':'BITWISES_VISITED.outputs.bitwises_visited_meps',
#                 'patterns_array':'PATTERNS_VISITED.outputs.patterns'
#             },
#             'configuration': {
#                  
#             },
#             'outputs':{
#                 'cover':0
#             }
#         },
    
#         {
#      
#             'id':'BITWISES_VISITED_COVER_COMPUTATION',
#             'type':'misc_covermultiple',
#             'inputs': {
#                 'bitwises':['toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_meps)','toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_votes)'],#'toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_meps)'],
#                 'bitwises_arrays':['BITWISES_VISITED.outputs.bitwises_visited_meps','BITWISES_VISITED.outputs.bitwises_visited_votes'],#'BITWISES_VISITED.outputs.bitwises_visited_meps'],
#                 'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
#                 'patterns_array':'PATTERNS_VISITED.outputs.patterns'
#             },
#             'configuration': {
#                  
#             },
#             'outputs':{
#                 'cover':0
#             }
#         },
#         {
#      
#             'id':'BITWISES_VISITED_UPDATE', 
#             'type':'pipeliner',
#             'inputs':{
#                 'bitwises_visited_votes':'BITWISES_VISITED.outputs.bitwises_visited_votes',
#                 'bitwises_visited_meps':'BITWISES_VISITED.outputs.bitwises_visited_meps'
#             },
#             'configuration':{
#                 'replace':True,
#                 'outputsFormula':{
#                     'BITWISES_VISITED.outputs.bitwises_visited_votes':'bitwises_visited_votes + list(toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_votes))',
#                     'BITWISES_VISITED.outputs.bitwises_visited_meps':'bitwises_visited_meps + list(toBitarray(PIPELINER_TO_VERIFY.outputs.bitwise_meps))'
#                 }
#             },
#             'outputs':{
#                  
#                  
#             }
#         },
#         {
#      
#             'id':'PATTERNS_VISITED_UPDATE', 
#             'type':'pipeliner',
#             'inputs':{
#                 'patterns':'PATTERNS_VISITED.outputs.patterns'
#             },
#             'configuration':{
#                 'replace':True,
#                 'outputsFormula':{
#                     'PATTERNS_VISITED.outputs.patterns':'patterns + list(WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern)'
#                 }
#             },
#             'outputs':{
#                  
#                  
#             }
#         },
#         
#         {
#             'id':'MATCHER_COVER_SEUIL',
#             'type':'simpleMatcher',
#             'inputs':{
#                 'value':'BITWISES_VISITED_COVER_COMPUTATION.outputs.cover'
#             },
#             'configuration':{
#                 'pipeline':[
#                         
#                     {
#                         'lowerThan':0.85
#                     }
#                 ]
#             },
#             'outputs':{
#                 'value':{}
#             }
#         },
    {

        'id':'WORKFLOW_PATTERN_VALIDITY',
        'type':'pipeliner',
        'inputs':{
            'pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern',
            'themes_pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.themes_pattern',
            'date_pattern':'WORKFLOW_PATTERNS_ENUMERATOR.outputs.date_pattern',
            'subgroup':'VOTES_SUBGROUP.outputs.dataset',
            'meps_count':'PIPELINER_TO_VERIFY.outputs.count_meps'
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
#        
#             'id':'SELECTED_VOTES_AND_MEPS',
#             'type':'aggregator',
#             'inputs': {
#                 'dataset':'VOTES_SUBGROUP.outputs.dataset'
#             },
#             'configuration': {
#                 'dimensions':{
#                 },
#                 'measures':{
#                     'MEPS':{
#                         'set_append':'EP_ID' 
#                         #count | count_distinct | sum | min | max | avg | append | set_append 
#                     },
#                     'VOTES':{
#                         'set_append':'VOTEID' 
#                         #count | count_distinct | sum | min | max | avg | append | set_append 
#                     }
#                 }
#             },
#             'outputs':{
#                 'dataset':[],
#                 'header':[]
#             }
#         },
    {
        'id':'SELECTED_VOTES_AND_MEPS_LOGGER',
        'type':'log_printer',
        'inputs':{
            'data':['SELECTED_VOTES_AND_MEPS.outputs.dataset[0].MEPS','SELECTED_VOTES_AND_MEPS.outputs.dataset[0].VOTES'] 
        },
        'configuration':{
                
        },
        'outputs':{
                
        },
        'execute':False
    },
    {
        'id':'SUBGROUP_STATS',
        'type':'pairwise_votes_stats',
        'inputs':{
            #'dataset':'WORKFLOW_PATTERN_VALIDITY.outputs.subgroup'
            'mepsStats':'GENERAL_STATS.outputs.mepsStats',
            'mepsMeta':'GENERAL_STATS.outputs.mepsMeta',
            'votesSelected':'PIPELINER_TO_VERIFY.outputs.selected_votes',
            'mepsSelected':'PIPELINER_TO_VERIFY.outputs.selected_meps'
        },
        'configuration':{
            #'granularity':20
            'votes_attributes':'PARAMETERS.outputs.votes_attributes', #first attribute is the unique identifier
            'users_attributes':'PARAMETERS.outputs.users_attributes', #first attribute is the unique identifier
            'position_attribute':'PARAMETERS.outputs.position_attribute',
            'update':True
        },
        'outputs':{
            'dataset':{},
            'mepsStats':{}
        } 
    },
    {
        'id':'SUBGROUP_STATS_FILTER',
        'type':'filter',
        'inputs':{
            'dataset':'SUBGROUP_STATS.outputs.dataset'
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
            'selectedNorm':'sum'
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
    {

        'id':'CORR_SIMILARITIES',
        'type':'similarities_matrix_computer',
        'inputs': {
            'matrix_1':'MATRICES_ADAPTER.outputs.matrix_2',
            'matrix_2':'MATRICES_ADAPTER.outputs.matrix_1'
        },
        'configuration': {
           'selectedSimilarity':'cosinus_signed' # mepwise 
        },
        'outputs':{
            'similarity':0 
        }
    },
    {

        'id':'WORKFLOW_MODEL_COMPARAISON',
        'type':'pipeliner',
        'inputs':{
            'pattern_index':"WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern_index",
            'pattern':"WORKFLOW_PATTERNS_ENUMERATOR.outputs.pattern",
            'description':"WORKFLOW_PATTERNS_ENUMERATOR.outputs.description",
            'qualityFrob':'NORM_COMPUTER.outputs.norm*((len(MATRICES_DIFFERENCE.outputs.matrix)-1)/(len(WORKFLOW_GENERAL_MODEL.outputs.model_matrix)-1))',
            'qualityMepWise':'NORM_COMPUTER_MEPWISE.outputs.norm',
            'correlation':'CORR_SIMILARITIES.outputs.similarity',
            'nbmeps':"WORKFLOW_SUBGROUP_MODEL.outputs.meps_count",
            'nbtotal':"WORKFLOW_GENERAL_MODEL.outputs.meps_count"
        },
        'configuration':{
            'outputsFormula':{
                'data':{
                    'pattern_index':"pattern_index",
                    'pattern':"pattern",
                    'description':"description",
                    'qualityFrob':'qualityFrob',
                    'qualityMepWise':'qualityMepWise',
                    'correlation':'correlation',
                    'nbmeps':"nbmeps",
                    'nbtotal':"nbtotal"
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
            'color':'RdYlGn'
        },
        'outputs':{
                
        },
        'execute':False
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
            'hasHeader': True,
            'selectedHeader':['pattern_index','pattern','description','qualityFrob','qualityMepWise','correlation','nbmeps','nbtotal']
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

process_workflow_recursive(workflowFinal, verbose=False)