'''
Created on 5 dec. 2016

@author: Adnene
'''
from expressionEvaluator.expressionEvaluator import evaluateExpression

#now that we have the stats get the stats value bytheir keys





def project_pipelineOLD(dataset,projection,workflow_stats={}):
    #this must be modified to be more efficient
    projectedDataset=[]
    for d in dataset:
        objToInsert={}
        
        if (type(projection) is dict):
            if bool(projection) :
                for key,value in projection.iteritems():
                    objToInsert[key]=evaluateExpression(value, d,workflow_stats)
            else : 
                objToInsert=dict(d)
        elif (type(projection) is str): #it's a value
            objToInsert['value']=evaluateExpression(projection, d,workflow_stats)
            
        projectedDataset.append(objToInsert)
    return projectedDataset



def project_pipeline(dataset,projection,workflow_stats={},parameters=None):
    #this must be modified to be more efficient
    projectedDataset=[]
    if len(dataset)>0:
        
        if (type(projection) is str): #it's a value
            for d in dataset:
                objToInsert={}
                objToInsert['value']=evaluateExpression(projection, d,workflow_stats,parameters)
                
                projectedDataset.append(objToInsert)
                
        elif (type(projection) is dict):
            
            simpleProjectionKeys={}
            complexProjectionKeys={}
            
            simpleProjectionAid=set(projection.values())&set(dataset[0].keys())
            
            for key,value in projection.iteritems():
                if value in simpleProjectionAid:
                    simpleProjectionKeys[key]=value
                else :
                    complexProjectionKeys[key]=value
            
            for d in dataset:
                objToInsert={}
                for key,value in projection.iteritems():
                    if key in simpleProjectionKeys :
                        objToInsert[key]=d[value]
                    else : 
                        objToInsert[key]=evaluateExpression(value, d,workflow_stats,parameters)    
                
                projectedDataset.append(objToInsert)
                
            
    
    return projectedDataset


def workflowStage_projecter(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
     
    '''
    {
     
        'id':'stage_id',
        'type':'projecter',
        'inputs': {
            'dataset':[],
            ###################""
            'param1':....
            #can be array or value or record
        },
        'configuration': {
            'projection':{
                'key':'expresion in function of attribute of records of dataset'
            } #
            #NOTE THAT 'projection': 'expresion in function of attribute of records of dataset' can be used in case an array or a value are in parameters
        },
        'outputs':{
            'dataset':[],
            'column':[]
            #can be array or value or record
        }
    }
    '''
     
     
     
     
     
    localConfiguration={}
    localConfiguration['projection']=(configuration.get('projection',{}))
    parameters=inputs
     
    if inputs.has_key('dataset') :
        results=project_pipeline(inputs['dataset'],localConfiguration['projection'],workflow_stats,parameters)
        outputs['dataset'] = results
        outputs['column'] =[d.values()[0] for d in results]
                
    elif inputs.has_key('record') : #is a dataset unique object   
        usedDataset=[inputs['record']]
        results=project_pipeline(usedDataset,localConfiguration['projection'],workflow_stats,parameters)
        outputs['record'] = results[0]
        outputs['column'] =[d.values()[0] for d in results]
         
    elif inputs.has_key('value') : #is a dataset unique object   
        usedDataset=[{'value':inputs['value']}]
        projected_results=project_pipeline(usedDataset,localConfiguration['projection'],workflow_stats,parameters)
        results=[item['value'] for item in projected_results]
        outputs['value'] =results[0]
        outputs['column'] =[d.values()[0] for d in projected_results]    
         
     
    elif inputs.has_key('array') :   
        
        usedDataset=[{'value':item} for item in inputs['array']]
        projected_results=project_pipeline(usedDataset,localConfiguration['projection'],workflow_stats,parameters)
        results=[item['value'] for item in projected_results]
        outputs['array'] = results
        outputs['column'] =[d.values()[0] for d in projected_results]  
     
    #need to take of the array case as generalfilter ! 
    return outputs

def workflowStage_projecter22OLD(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'projecter',
        'inputs': {
            'dataset':[]
            #can be value or record
        },
        'configuration': {
            'projection':{
                'key':'expresion in function of attribute of records of dataset'
            }
        },
        'outputs':{
            'dataset':[],
            'array':[]
            #can be value or record
        }
    }
    '''
    
    
    
    
    
    localConfiguration={}
    localConfiguration['projection']=(configuration.get('projection',{}))
    
    if inputs.has_key('dataset') :
        results=project_pipeline(inputs['dataset'],localConfiguration['projection'],workflow_stats)
        outputs['dataset'] = results
        outputs['array'] =[d.values()[0] for d in results]
               
    elif inputs.has_key('record') : #is a dataset unique object   
        usedDataset=[inputs['record']]
        results=project_pipeline(usedDataset,localConfiguration['projection'],workflow_stats)
        outputs['record'] = results[0]
        outputs['array'] =[d.values()[0] for d in results]
        
    elif inputs.has_key('value') : #is a dataset unique object   
        usedDataset=[{'value':inputs['value']}]
        results=project_pipeline(usedDataset,localConfiguration['projection'],workflow_stats)
        outputs['array'] =[d.values()[0] for d in results]    
        results=[item['value'] for item in results]
        
        outputs['value'] =results[0]
    
    #need to take of the array case as generalfilter ! 
    return outputs