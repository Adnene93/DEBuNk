'''
Created on 8 dec. 2016

@author: Adnene
'''

from expressionEvaluator.expressionEvaluator import evaluateExpression


def checkLocalReferences(iterableObject,sourceObject,workflow_stats):
    
    if type(iterableObject) is dict :
        for key,value in iterableObject.iteritems():
            if hasattr(iterableObject[key], '__iter__'):
                checkLocalReferences(iterableObject[key],sourceObject,workflow_stats) 
            elif (type(value) is str) :
                iterableObject[key]=evaluateExpression(value, sourceObject, workflow_stats)
                
    if type(iterableObject) is list or type(iterableObject) is tuple :
        for key,value in enumerate(iterableObject):
            if hasattr(iterableObject[key], '__iter__'):
                checkLocalReferences(iterableObject[key],sourceObject,workflow_stats) 
            elif (type(value) is str) :
                iterableObject[key]=evaluateExpression(value, sourceObject, workflow_stats)

def getInputFromOtherStage(identificationString,current_workflow_stats):
    results=[]
    fatherOfResults=[]
    resultsKey=None
    identificationStringSplitted = identificationString.split('.')
    for index,key in enumerate(identificationStringSplitted):
        try :
            if (index==0):
                fatherOfResults=current_workflow_stats
                results=current_workflow_stats[key] #['outputs']
                resultsKey=key
            else:
                fatherOfResults=results
                results=results[key]
                resultsKey=key
        except Exception: #if it does not contain the suitable key
            fatherOfResults=None
            results=None
            resultsKey=None
            break
    return results,fatherOfResults,resultsKey

def workflowStage_pipeliner( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'pipeliner',
        'inputs': {
            'dataset':[]
            
        },
        'configuration': {
            'replace':False #if replace = true this means if the key point out a workflow stage outputs attribute then update it
            'outputsFormula':{
            }
        },
        'outputs':{
            'dataset':[]
        }
    }
    #outputsFormula can be in function of inputs references or precedent workflow stages
    '''  
    config_local_replace = configuration.get('replace',False)
    
        
    checkLocalReferences(configuration['outputsFormula'], inputs,workflow_stats)
    for key in configuration['outputsFormula'].keys():
        outputs[key]=configuration['outputsFormula'][key]
    if config_local_replace :
        
        for key in outputs.keys():
           
            res,parent,keyRes=getInputFromOtherStage(key,workflow_stats)
            if parent is not None:
                parent[keyRes]=outputs[key]
    

    
    return outputs
