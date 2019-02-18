'''
Created on 2 dec. 2016

@author: Adnene
'''
from filterer.filtererOld import filter_pipeline
from filterer.filter import workflowStage_filter


def workflowStage_simpleMatch( #iterator matcher
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    
    '''
    {
    
        'id':'stage_id',
        'type':'simpleMatcher',
        'inputs': {
            'dataset':[]
            #can be value or record or array
        },
        'configuration': {
            'pipeline':[
                {
                    'dimensionName':'dim_name', # if it's a dataset or a record in entry
                    'equal': 'value_expression' #expression is in function of other stages and the dataset
                    #normal operators : equal | notEqual | inSet | outSet | inInterval | outInterval | lowerThan | greaterThan | like | likeInSet | likeOutSet
                    #set operators : likeContainSet | likeNotContainSet
                }
            ]
        },
        'outputs':{
            'dataset':[]
            #can be value or record or array
            'continue' : True #False means all stages in the nested iteration are not done if the condition is not verfied 
            #If the input is dataset or array means that if the resulted array is empty do nothing after
            #If the input is record or value means that if the value or record does not verify the condition stipulated in the filter pipeline
        }
    }
    ''' 
    
    
    workflowStage_filter(inputs,configuration,outputs,workflow_stats)
    
    if inputs.has_key('dataset') :
        outputs['continue']=len(outputs['dataset'])>0
        
    elif inputs.has_key('array') :   
        outputs['continue']=len(outputs['array'])>0
    
    elif inputs.has_key('record') : #is a dataset unique object   
        outputs['continue']=outputs['record'] is not None            
    
    elif inputs.has_key('value') :
        outputs['continue']=outputs['value'] is not None    
    
    return outputs