'''
Created on 6 dec. 2016

@author: Adnene
'''
from expressionEvaluator.expressionEvaluator import evaluateExpression


def accumulator_count(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,float(0))
    
    
    dataset[grouperEntry['index']][measureKey] = oldValueInDataset + 1  


def accumulator_countDistinct(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    #oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,float(0))
    
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
    
    if (grouperEntry.has_key('set')):
        grouperEntry['set']|={objNewMeasure}
    else :
        grouperEntry['set']=set()
        grouperEntry['set']|={objNewMeasure}
    
    dataset[grouperEntry['index']][measureKey] = len(grouperEntry['set'])

def accumulator_sum(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,float(0))
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
    
    dataset[grouperEntry['index']][measureKey] = oldValueInDataset+objNewMeasure
    
    
def accumulator_avg(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey)
    oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,float(0))
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
          
    #ONE PASS MEAN : m_{k-1} + (x_k - m_{k-1}) / k
    dataset[grouperEntry['index']][measureKey] =  oldValueInDataset+float(objNewMeasure-oldValueInDataset)/grouperEntry['count'] 
    
    
def accumulator_min(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,float('+inf'))
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
    
    dataset[grouperEntry['index']][measureKey] = min(oldValueInDataset,objNewMeasure)


def accumulator_max(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,float('-inf'))
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
    
    dataset[grouperEntry['index']][measureKey] = max(oldValueInDataset,objNewMeasure)    


def accumulator_append(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    #print measureKey,dataset[grouperEntry['index']]
    oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,[])
    
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
    
    dataset[grouperEntry['index']][measureKey] = oldValueInDataset
    dataset[grouperEntry['index']][measureKey].append(objNewMeasure)     

def accumulator_setappend(objNew,tupleKey,dataset,mapsGrouperStats,measureKey,measureFormula,workflow_stats,simple=True):
    grouperEntry= mapsGrouperStats.get(tupleKey) 
    #oldValueInDataset=dataset[grouperEntry['index']].get(measureKey,set())
    if simple :
        objNewMeasure=objNew[measureFormula]
    else : 
        objNewMeasure=evaluateExpression(measureFormula, objNew,workflow_stats)
    
    try :
        dataset[grouperEntry['index']][measureKey]|={objNewMeasure} 
    except:
        dataset[grouperEntry['index']][measureKey]={objNewMeasure} 
#     dataset[grouperEntry['index']][measureKey] = oldValueInDataset
#     dataset[grouperEntry['index']][measureKey]|={objNewMeasure} 
    


ACCUMULATOR_MAP_FUNCTIONS={
    'count' : accumulator_count,
    'sum' : accumulator_sum,
    'avg' : accumulator_avg,
    'max' : accumulator_max,
    'min' : accumulator_min,
    'append' : accumulator_append,
    'set_append' : accumulator_setappend,
    'count_distinct' : accumulator_countDistinct
}

ACCUMULATOR_MAP_FUNCTIONS_INIT={
    'count' : 0,
    'sum' : 0,
    'avg' : 0,
    'max' : 0,
    'min' : 0,
    'append' : [],
    'set_append' : set([]),
    'count_distinct' : 0
}

def aggregate_datasetOLD(dataset,dimensions,measures,workflow_stats={}):
    #mapping
    header=dimensions.keys()+measures.keys()
    rawAggregateMapping={} #tuple and their index in array
    flatResultsDataset=[]
    
    simpleGroupKeys={}
    complexGroupKeys={}
    simpleGroupAid=set(dimensions.values())&set(dataset[0].keys())
    
    simpleMeasuresKeys={}
    complexMeasuresKeys={}
    key_formula_measures= {k:v[v.keys()[0]] for k,v in measures.iteritems()}
    simpleMeasuresAid=set(key_formula_measures.values())&set(dataset[0].keys())
    
    for key,value in dimensions.iteritems():
        if value in simpleGroupAid:
            simpleGroupKeys[key]=value
        else :
            complexGroupKeys[key]=value
    
    for key,value in key_formula_measures.iteritems():
        if value in simpleMeasuresAid:
            simpleMeasuresKeys[key]=value
        else :
            complexMeasuresKeys[key]=value
                
    for d in dataset:
        objToInsert={}
        for key,value in dimensions.iteritems():
            if key in simpleGroupKeys :
                objToInsert[key]=d[value]
            else : 
                objToInsert[key]=evaluateExpression(value, d,workflow_stats) 
        
        tuple_key=tuple(objToInsert.iteritems())
        
        
        for key,value in key_formula_measures.iteritems():
           
            if key in simpleMeasuresKeys :
                objToInsert[key]=d[value]
            else :
                objToInsert[key]=evaluateExpression(value, d,workflow_stats)  
            
            
                  
        indexOfObjInFlatResultsDataset= rawAggregateMapping.get(tuple_key,None)
        if indexOfObjInFlatResultsDataset is None:
            flatResultsDataset.append(objToInsert)
            rawAggregateMapping[tuple_key]={'index':len(flatResultsDataset)-1}
            for key,value in measures.iteritems():
                accumulator=value.keys()[0]
                if accumulator=='append':
                    flatResultsDataset[rawAggregateMapping[tuple_key]['index']][key]=[flatResultsDataset[rawAggregateMapping[tuple_key]['index']][key]]
                elif accumulator=='set_append':
                    flatResultsDataset[rawAggregateMapping[tuple_key]['index']][key]=set([flatResultsDataset[rawAggregateMapping[tuple_key]['index']][key]])
                
        else :
            for key,value in measures.iteritems():
                accumulator=value.keys()[0]
                if accumulator=='sum':
                    flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]+=objToInsert[key]
                
                elif accumulator=='max':
                    flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]=objToInsert[key] if objToInsert[key]>flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key] else flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key] 
                elif accumulator=='min':
                    flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]=objToInsert[key] if objToInsert[key]<flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key] else flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]
                elif accumulator=='avg': #ONE PASS MEAN : m_{k-1} + (x_k - m_{k-1}) / k
                    rawAggregateMapping[tuple_key]['count']=rawAggregateMapping[tuple_key].get('count',1)+1
                    oldAvg=flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]
                    flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]=oldAvg+(float(objToInsert[key]-oldAvg)/float(rawAggregateMapping[tuple_key]['count']))
                
                
                elif accumulator=='append':
                    if type(flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]) is list :
                        flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key].append(objToInsert[key])
                    else :
                        arr=[]
                        arr.append(flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key])
                        flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key]=arr
                        flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key].append(objToInsert[key])
                elif accumulator=='set_append':
                    flatResultsDataset[indexOfObjInFlatResultsDataset['index']][key].add(objToInsert[key])
    return flatResultsDataset,header


def aggregate_dataset(dataset,dimensions,measures,workflow_stats={}):
    header=dimensions.keys()+measures.keys()
    rawAggregateMapping={} #tuple and their index in array
    flatResultsDataset=[]
    if len(dataset)>0:
        
        simpleGroupAid=set(dimensions.values())&set(dataset[0].keys())
        key_formula_measures= {k:v[v.keys()[0]] for k,v in measures.iteritems()}
        key_acc_measures= {k:v.keys()[0] for k,v in measures.iteritems()}
        simpleMeasuresAid=set(key_formula_measures.values())&set(dataset[0].keys())
        
        simpleGroupKeys={key:value for key,value in dimensions.iteritems() if value in simpleGroupAid}
        simpleMeasuresKeys={key:value for key,value in key_formula_measures.iteritems() if value in simpleMeasuresAid}

        accumulators_ready_to_use=[]
        for key,value in key_formula_measures.iteritems():
            accumulator_callable=ACCUMULATOR_MAP_FUNCTIONS[key_acc_measures[key]]
            accumulators_ready_to_use.append([key,value,accumulator_callable,key in simpleMeasuresKeys])
        
        resultsAppender=flatResultsDataset.append
        dimensions_iteritems=[[key,value,key in simpleGroupKeys] for key,value in dimensions.iteritems()]
        sizeOfResults=0
        
        for d in dataset:
            objToInsert={key : d[value] if is_simple else evaluateExpression(value, d,workflow_stats) for key,value,is_simple in dimensions_iteritems }
            tuple_key=tuple(objToInsert.iteritems())
            
            try :
                rawAggregateMapping[tuple_key]['count']+=1
            except :
                resultsAppender(objToInsert)
                rawAggregateMapping[tuple_key]={'index':sizeOfResults,'count':1}
                sizeOfResults+=1

                
            for key,value,acc_callable,is_simple_measure in accumulators_ready_to_use :
                acc_callable(dict(d), tuple_key, flatResultsDataset, rawAggregateMapping, key, value, workflow_stats, is_simple_measure)
    elif len(dimensions)==0 :
        
        #key_formula_measures= {k:v[v.keys()[0]] for k,v in measures.iteritems()}
        key_acc_measures= {k:v.keys()[0] for k,v in measures.iteritems()}
        accumulators_ready_to_use=[]
        rowToReturn={}
        for key,value in key_acc_measures.iteritems():
            rowToReturn[key]=ACCUMULATOR_MAP_FUNCTIONS_INIT[value]
        flatResultsDataset.append(rowToReturn)   
        
    return flatResultsDataset,header


def workflowStage_aggregator(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'aggregator',
        'inputs': {
            'dataset':[]
        },
        'configuration': {
            'dimensions':{
                'key':'expresion in function of attribute of records of dataset'
            },
            'measures':{
                'key':{
                    'count':'expresion in function of attribute of records of dataset' 
                    #count | count_distinct | sum | min | max | avg | append | set_append 
                } 
            }
        },
        'outputs':{
            'dataset':[],
            'header':[]
        }
    }
    '''
    
    
    
    localConfiguration={}
    localConfiguration['dimensions']=configuration.get('dimensions',{})
    localConfiguration['measures']=configuration.get('measures',{})
    flatResultsDataset,header=aggregate_dataset(inputs['dataset'],localConfiguration['dimensions'],localConfiguration['measures'],workflow_stats)
    outputs['dataset'] = flatResultsDataset
    outputs['header'] =header
               
    
    
    return outputs