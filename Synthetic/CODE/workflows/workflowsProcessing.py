'''
Created on 25 nov. 2016

@author: Adnene

'''
from copy import deepcopy
from time import time 

from DM_NASMIC.Stage_Hierarchical import workflowStage_hierarchical_stage_michel
from DM_NASMIC.Stage_K_Medoid import workflowStage_kmedoid_stage_nassim
from aggregator.aggregator import workflowStage_aggregator
from clustering.clusteringWorkflowStage import workflowStage_clusterer
from expressionEvaluator.expressionEvaluator import evaluateExpression
from filterer.filter import workflowStage_filter
from projecter.projecter import workflowStage_projecter
from statistics.statisticsHistogramWorkflowStage import workflowStage_histogramGenerator
from util.biwtisesProcessing import workflowStage_coverabilityWithVisited, \
    workflowStage_coverabilityMultiple
from util.csvProcessing import workflowStage_csvReader, workflowStage_csvWriter, \
    workflowStage_csvReader_pandas
from util.jsonProcessing import workflowStage_jsonReader, \
    workflowStage_jsonWriter, readJSON_stringifyUnicodes
from util.logPrinter import workflowStage_logPrinter
from util.matrixProcessing import workflowStage_adaptMatrices, \
    workflowStage_differenceMatrices, workflowStage_matrixNorm, \
    workflowStage_matrixSimilarities
from util.pipelinerStage import workflowStage_pipeliner
from util.util import utilPrint
from visualization_heatmap.heatmap import workflowStage_heatmapGenerator
from votesExtractionAndProcessing.pairwiseSimilarityDistance import workflowStage_extractPairwiseComps
from votesExtractionAndProcessing.pairwiseStatistics import workflowStage_extractPairwiseStats
from votesExtractionAndProcessing.transformToProcessableData import workflowStage_transformPairwiseComparaison
from votesMajoritiesExtractors.votesMajoritiesExtractor import workflowStage_majorities_computer
from workflowsControls.iteratorsStage import workflowStage_simpleIterator, workflowStage_iteratorsOnThemes_Depth, \
    workflowStage_iteratorsOnNominal, workflowStage_iteratorsOnNumerics, \
    workflowStage_iteratorsOnMultipeAttributes, \
    workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise, \
    workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise_subgroups
from workflowsControls.matcherStage import workflowStage_simpleMatch
from workflowsControls.syncersStage import workflowStage_appenderSyncer, workflowStage_simpleSyncer, \
    workflowStage_flatAppenderSyncer


MAP_POSSIBLE_STAGE_TYPES={
    'pipeliner' : workflowStage_pipeliner,
    
    'csvReader' : workflowStage_csvReader,    'csvReader_pandas': workflowStage_csvReader_pandas,
    'csvWriter' : workflowStage_csvWriter,
    'jsonReader' : workflowStage_jsonReader,
    'jsonWriter' : workflowStage_jsonWriter,
    
    'projecter':workflowStage_projecter,
    'aggregator':workflowStage_aggregator, 
    'filter':workflowStage_filter,
    
    #'parltrack_database':workflowStage_parltrack_database,
    
    'majorities_computer':workflowStage_majorities_computer,
    'pairwise_votes_stats':workflowStage_extractPairwiseStats,
    'pairwise_comparaisons':workflowStage_extractPairwiseComps,
    'pairwise_comparaison_transform':workflowStage_transformPairwiseComparaison,
    
    'heatmap_visualization':workflowStage_heatmapGenerator,
    'histograms_visualization':workflowStage_histogramGenerator,
    'clusterer' : workflowStage_clusterer,
    
    'adapt_matrices':workflowStage_adaptMatrices,
    'difference_matrices':workflowStage_differenceMatrices,
    'norm_matrix_computer':workflowStage_matrixNorm,
    'similarities_matrix_computer':workflowStage_matrixSimilarities,
    
    'log_printer':workflowStage_logPrinter,
    
    'simpleIterator':workflowStage_simpleIterator,
    'stringsHierarchyIterator_depth':workflowStage_iteratorsOnThemes_Depth,
    'nominal_iterator':workflowStage_iteratorsOnNominal,
    'numeric_iterator':workflowStage_iteratorsOnNumerics,
    'multiple_attributes_iterator':workflowStage_iteratorsOnMultipeAttributes,
    'multiple_attributes_iterator_sgbitwise':workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise,
    'multiple_attributes_iterator_sgbitwise_subgroups':workflowStage_iteratorsOnMultipeAttributes_subgroupBitwise_subgroups,
    
    'misc_cover':workflowStage_coverabilityWithVisited,
    'misc_covermultiple':workflowStage_coverabilityMultiple,
    
    'simpleSyncer':workflowStage_simpleSyncer,
    'appenderSyncer':workflowStage_appenderSyncer,
    'flatAppenderSyncer':workflowStage_flatAppenderSyncer,
    
    'simpleMatcher':workflowStage_simpleMatch,
    
    ######################################################
    
    
    'hierarchical_stage_michel':workflowStage_hierarchical_stage_michel,
    'kmedoid_stage_nassim':workflowStage_kmedoid_stage_nassim
}

SYNCERS_STAGES_ARRAY=[
    'simpleSyncer',
    'appenderSyncer',
    'flatAppenderSyncer'
    
]

MATCHERS_STAGES_ARRAY=[
    'simpleMatcher'
]

ITERATORS_STAGES_ARRAY=[
    'simpleIterator',
    'stringsHierarchyIterator_depth',
    'nominal_iterator',
    'numeric_iterator',
    'multiple_attributes_iterator',
    'multiple_attributes_iterator_sgbitwise',
    'multiple_attributes_iterator_sgbitwise_subgroups'
    
]



#ADD PROCESSING WHEN INPUTS ARE OUTPUTS OF PRECEDENTS WORKFLOW STAGES
def process_workflowStage(stage,current_workflow_stats):
    '''
    a stage is composed of : 
    {
        id : 
        type : 
        inputs : 
        configuration:
        outputs : 
    }
    '''
    
    
    checkReferencesInIterableAttributes(stage['inputs'],current_workflow_stats)
    checkReferencesInIterableAttributes(stage['configuration'],current_workflow_stats)
    
    
    
    current_id=stage['id']
    current_workflow_stats[current_id]=stage
    current_stage=current_workflow_stats[current_id]
    typeOfCurrentStage=(set([stage['type']]) & set(MAP_POSSIBLE_STAGE_TYPES.keys())).pop()
    
    
    
    current_stage_instanciation=MAP_POSSIBLE_STAGE_TYPES[typeOfCurrentStage] #THE FUNCTION
    
    return current_stage_instanciation(inputs=current_stage['inputs'], 
                                configuration=current_stage['configuration'], 
                                outputs=current_stage['outputs'],
                                workflow_stats=current_workflow_stats
                                )
    
    
    #return current_stage['outputs']
    

def getInputFromOtherStage(identificationString,current_workflow_stats):
    results=[]
    identificationStringSplitted = identificationString.split('.')
    for index,key in enumerate(identificationStringSplitted):
        try :
            if (index==0):
                results=current_workflow_stats[key] #['outputs']
            else:
                results=results[key]
        except Exception: #if it does not contain the suitable key
            results=None
            break
    return results

def checkReferencesInIterableAttributes(iterableObject,current_workflow_stats):
    
    if type(iterableObject) is dict :
        for key,value in iterableObject.iteritems():
            if hasattr(iterableObject[key], '__iter__'):
                checkReferencesInIterableAttributes(iterableObject[key],current_workflow_stats) 
            #elif (type(value) is str and '.' in value and value.split('.')[0] in current_workflow_stats) :
            #    iterableObject[key]=getInputFromOtherStage(iterableObject[key],current_workflow_stats)
            elif (type(value) is str) :
                iterableObject[key]=evaluateExpression(value, {}, current_workflow_stats)
                
    if type(iterableObject) is list or type(iterableObject) is tuple :
        for key,value in enumerate(iterableObject):
            if hasattr(iterableObject[key], '__iter__'):
                checkReferencesInIterableAttributes(iterableObject[key],current_workflow_stats) 
            #elif (type(value) is str and '.' in value and value.split('.')[0] in current_workflow_stats) :
            #    iterableObject[key]=getInputFromOtherStage(iterableObject[key],current_workflow_stats)
            elif (type(value) is str) :
                iterableObject[key]=evaluateExpression(value, {}, current_workflow_stats)  
         
def process_workflow(workflow): #workflow is a pipeline of stages (array)
    '''
    in the workflows attribtus point(.) is not authorized until you wan access to some other stages atributes! 
    '''
    
    current_workflow_stats={}
    startWorkflow = time()
    for index,stage in enumerate(workflow) :  
        startStage = time()
        utilPrint('start processing stage ' + stage['id'] + ' of type' + stage['type'])
        process_workflowStage(stage,current_workflow_stats)
        
        stopStage = time()
        utilPrint('time elapsed while processing stage '+ stage['id']+ ' : '+ str(stopStage-startStage))
        
    stopWorkflow = time()
    utilPrint('time elapsed while processing the whole workflow : '+ str(stopWorkflow-startWorkflow))    
    
    #DON'T FORGET TO UPDATE ALWAYS DATASETS POSSIBLE OUTPUTS

def init_workflow(workflow,current_workflow_stats={}): #workflow is a pipeline of stages (array)
    
    for index,stage in enumerate(workflow) :  
        current_workflow_stats[stage['id']]={'id':stage['id'],'type':stage['type'],'inputs':{},'configuration':{},'outputs':{},'timespent':0}
        stage['inputs']=stage.get('inputs',{})   
        stage['configuration']=stage.get('configuration',{}) 
        stage['outputs']=stage.get('outputs',{}) 
    

def process_workflow_innerRecursive(workflow,current_workflow_stats={},currentIndex=0,fromIter=False,verbose=False):
    
    
    if currentIndex < len(workflow) :
        
        startProccessingStage = time()
        
        stage=workflow[currentIndex]
        
        stage['execute']=stage.get('execute',True)
        
        
        if (stage['type'] in ITERATORS_STAGES_ARRAY):
            
            stageCopy={}
            stageCopy['inputs']=deepcopy(stage['inputs'])
            stageCopy['configuration']=deepcopy(stage['configuration'])
            stageCopy['execute']=deepcopy(stage['execute'])
            if verbose :
                utilPrint('start processing stage ' + stage['id'] + ' of type' + stage['type'])
            iterableStage=process_workflowStage(stage,current_workflow_stats)
            lastReachedIndex=currentIndex+1
            
            enditerations=0
            beforeiterations=0
            sumTimeIterations=0
            while(next(iterableStage,None)):
                beforeiterations = time() 
                newCurrentIndex=currentIndex+1
                newFromIter=True
                lastReachedIndex=process_workflow_innerRecursive(workflow,current_workflow_stats,newCurrentIndex,newFromIter,verbose) 
                enditerations = time() 
                sumTimeIterations+=(enditerations-beforeiterations)
                
            stage['inputs']=deepcopy(stageCopy['inputs'])
            stage['configuration']=deepcopy(stageCopy['configuration'])    
            stage['execute']=deepcopy(stageCopy['execute'])
            
            endProccessingStage = time() 
            stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage)-sumTimeIterations
            return process_workflow_innerRecursive(workflow,current_workflow_stats,lastReachedIndex+1,fromIter,verbose)   
            
        elif (stage['type'] in MATCHERS_STAGES_ARRAY):
            if evaluateExpression(stage['execute'] , {}, current_workflow_stats):
                stageCopy={}
                stageCopy['inputs']=deepcopy(stage['inputs'])
                stageCopy['configuration']=deepcopy(stage['configuration'])
                stageCopy['execute']=deepcopy(stage['execute'])
            
                if verbose :
                    utilPrint('start processing stage ' + stage['id'] + ' of type : ' + stage['type'])
                process_workflowStage(stage,current_workflow_stats)    
                stage['inputs']=(stageCopy['inputs'])
                stage['configuration']=(stageCopy['configuration'])
                stage['execute']=(stageCopy['execute'])
            
                
                if (stage['outputs']['continue']) :
                    currentIndex+=1
                    endProccessingStage = time()  
                    stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage)   
                    return process_workflow_innerRecursive(workflow,current_workflow_stats,currentIndex,fromIter,verbose)
                else :
                    currentChain=getWorkflowChain(workflow)
                    for indexToReturn in range(currentIndex,len(currentChain)):
                        if currentChain[indexToReturn]==')' :
                            break
                    endProccessingStage = time()   
                    stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage)  
                    return indexToReturn
            else :
                currentIndex+=1
                endProccessingStage = time()  
                stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage)   
                return process_workflow_innerRecursive(workflow,current_workflow_stats,currentIndex,fromIter,verbose) 
                    
        
        elif (stage['type'] in SYNCERS_STAGES_ARRAY and fromIter):
            #this is processed each time this method reach a syncer stage after starting an iterator
            
            stageCopy={}
            stageCopy['inputs']=deepcopy(stage['inputs'])
            stageCopy['configuration']=deepcopy(stage['configuration'])
            stageCopy['execute']=deepcopy(stage['execute'])
            
            if verbose :
                utilPrint('start processing stage ' + stage['id'] + ' of type : ' + stage['type'])
            process_workflowStage(stage,current_workflow_stats)    
            stage['inputs']=(stageCopy['inputs'])
            stage['configuration']=(stageCopy['configuration'])
            stage['execute']=(stageCopy['execute'])
            
            
            #Nested ietration syncers must be reinitialized after each terminaison
            syncersStageToReInit=get_sincerStages_to_reinitialize(workflow[:currentIndex+1])
            for i in syncersStageToReInit:
                stageToReinit=workflow[i]
                stageToReinit['outputs']={'syncedData':None}
            
            endProccessingStage = time()   
            stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage)  
            return currentIndex  #process_workflow_innerRecursive(workflow,current_workflow_stats,currentIndex+1,verbose)    
        
        elif (stage['type'] in SYNCERS_STAGES_ARRAY and not fromIter):
            #this is processed each time this method reach a syncer stage but not after an iteration of stages, it means do nothing and process the next stages
            
            #new
            stageCopy={}
            stageCopy['inputs']=deepcopy(stage['inputs'])
            stageCopy['configuration']=deepcopy(stage['configuration'])
            stageCopy['execute']=deepcopy(stage['execute'])
            
            if verbose :
                utilPrint('start processing stage ' + stage['id'] + ' of type : ' + stage['type'])
            process_workflowStage(stage,current_workflow_stats)    
            stage['inputs']=(stageCopy['inputs'])
            stage['configuration']=(stageCopy['configuration'])
            stage['execute']=(stageCopy['execute'])
            
            #new
            
            currentIndex+=1
            
            endProccessingStage = time()   
            stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage)  
            return process_workflow_innerRecursive(workflow,current_workflow_stats,currentIndex,fromIter,verbose)
        
        
        else :   
            currentIndex+=1
            startStage = time()
            if evaluateExpression(stage['execute'] , {}, current_workflow_stats):
                stageCopy={}
                stageCopy['inputs']=deepcopy(stage['inputs'])
                stageCopy['configuration']=deepcopy(stage['configuration'])
                stageCopy['execute']=deepcopy(stage['execute'])
            
                
                if verbose :
                    utilPrint('start processing stage ' + stage['id'] + ' of type' + stage['type'])
                process_workflowStage(stage,current_workflow_stats)
                stopStage = time()
                if verbose :
                    utilPrint('time elapsed while processing stage '+ stage['id']+ ' : '+ str(stopStage-startStage))
                
                stage['inputs']=(stageCopy['inputs'])
                stage['configuration']=(stageCopy['configuration'])
                stage['execute']=(stageCopy['execute'])
            
                
            endProccessingStage = time()    
            stage['timespent']=stage.get('timespent',0)+  (endProccessingStage-startProccessingStage) 
            return process_workflow_innerRecursive(workflow,current_workflow_stats,currentIndex,fromIter,verbose) #ADD RETURN
        
    return currentIndex


def process_workflow_recursive(workflow,verbose=False,verbose2=False):
    current_workflow_stats={}
    #Why not initialize all stages by default values or something like
    #Why not in current workflow stats differenciate between same stages executed multiple time 
    
    # init make the stats of stages of workflow all at Null, we need to see if the key is here but still the value is None for each stage type, do nothing at best for each type
    init_workflow(workflow, current_workflow_stats)
    
    ###########################
    
    currentIndex=0
    startWorkflow = time()
    process_workflow_innerRecursive(workflow,current_workflow_stats,currentIndex,False,verbose)
    stopWorkflow = time()
    utilPrint('time elapsed while processing the whole workflow : '+ str(stopWorkflow-startWorkflow))
    
    print '\n'
    print '------------------------------------------------------------------------------------\n'
    print 'ID\tType\tTimespent'
    table=[]
    for key,stage in current_workflow_stats.iteritems():
        table.append([stage['id'],stage['type'],stage['timespent']])
    table=sorted(table,key=lambda x : x [2],reverse=True)
    for row in table :
        print str(row[0])+'\t'+str(row[1])+'\t'+str(row[2])
    print '\n'
    print '------------------------------------------------------------------------------------\n'
    
    

def getWorkflowChain(workflow):
    ret=''
    
    for index,stage in enumerate(workflow) :  
        if stage['type'] in ITERATORS_STAGES_ARRAY :
            ret+= '(' 
        elif stage['type'] in SYNCERS_STAGES_ARRAY :
            ret+= ')' 
        else :
            ret+='-'
        
    return ret


def get_sincerStages_to_reinitialize(workflow) :
    s=getWorkflowChain(workflow)
    ret=[]
    count=0
    reversedRange=range(len(s)-1)
    reversedRange.reverse()
    for x in reversedRange :
        if s[x] ==')' :
            count+=1
        elif s[x]== '(' :
            count-=1
        if count==1 and s[x] ==')':
            ret.append(x)
        if count<0 :
            return ret    
    return ret


def process_workflow_recursive_from_json(sourcefile,verbose=False):
    wf=readJSON_stringifyUnicodes(sourcefile)
    process_workflow_recursive(wf,verbose)
    
    
    

