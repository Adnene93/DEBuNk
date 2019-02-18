'''
Created on 29 nov. 2016

@author: Adnene
'''


def workflowStage_stringConcatenator( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    
    '''
    @param inputs:  {
        'strings':''
    }
    @param configuration: {
        'operation' = 'string'
    }
    @param outputs: {
        'string' : ''
    }
    '''
    
    
    outputs['string']=''
    for s in inputs['strings'] :
        outputs['string']+=str(s)
    
    return outputs