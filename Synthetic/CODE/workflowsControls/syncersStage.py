'''
Created on 30 nov. 2016

@author: Adnene
'''


def workflowStage_simpleSyncer( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'simpleSyncer',
        'inputs': {
        },
        'configuration': {
        },
        'outputs':{
        }
    }
    '''  
    
    
    
    
    return outputs

def workflowStage_appenderSyncer( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    
    '''
    {
    
        'id':'stage_id',
        'type':'appenderSyncer',
        'inputs': {
            'data':[] #can have any type 
        },
        'configuration': {
        },
        'outputs':{
            'syncedData':[]
        }
    }
    '''  
    
    
    
    if outputs.get('syncedData',None) is None:
        outputs['syncedData']=[]
    
    if inputs['data'] is not None : 
        outputs['syncedData'].append(inputs['data']) 
    
    return outputs


def workflowStage_flatAppenderSyncer( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    
    '''
    {
    
        'id':'stage_id',
        'type':'flatAppenderSyncer',
        'inputs': {
            'data':[] #can have any type 
        },
        'configuration': {
        },
        'outputs':{
            'syncedData':[]
        }
    }
    '''  
    
    
    if outputs.get('syncedData',None) is None:
        outputs['syncedData']=[]
    
    if inputs['data'] is not None : 
        if  (type(inputs['data']) is list):
            for val in inputs['data'] : 
                outputs['syncedData'].append(val)
        else :
            outputs['syncedData'].append(inputs['data']) 
    
    return outputs
                