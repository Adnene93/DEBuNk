'''
Created on 24 nov. 2016

@author: Adnene
'''
'''
@note : stage of filtering is a dictionnary :
{
    'dimension' : 'dimensionName',
    'equal | notEqual | inSet | outSet | inInterval | outInterval | lowerThan | greaterThan' : 
    value or values according to the conditions
    
    note that if the attribute is numeric the values introduced can be wrote as values or as :
    avg for average of the whole dataset in the parameter and
    std for standarddeviation
    
    
}
'''

import math
import os

from util.csvProcessing import writeCSVwithHeader, readCSVwithHeader
from util.util import listFiles


def average(dataset,dimensionName):
    avg_ret=sum([float(x[dimensionName]) for x in dataset])/float(len(dataset))
    return avg_ret

def standardDeviation(dataset,dimensionName):
    avg_ret=sum([float(x[dimensionName]) for x in dataset])/float(len(dataset))
    std_ret = math.sqrt(sum([(float(x[dimensionName])-avg_ret)**2 for x in dataset])/float(len(dataset)))
    return std_ret


def equal(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    for obj in dataset :
        if (obj[dimensionName]==valueInCondition):
            filteredDataSet.append(obj)
    return filteredDataSet
        
    
def notEqual(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    for obj in dataset :
        if not (obj[dimensionName]==valueInCondition):
            filteredDataSet.append(obj)
    return filteredDataSet

def inSet(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    for obj in dataset :
        if (obj[dimensionName] in valueInCondition):
            filteredDataSet.append(obj)
    return filteredDataSet     

def outSet(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    for obj in dataset :
        if not (obj[dimensionName] in valueInCondition):
            filteredDataSet.append(obj)
    return filteredDataSet        

def inInterval(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    avg=0
    std=0
    newValueInCondition = [str(valueInCondition)[0],str(valueInCondition)[1]]
    if 'avg' in newValueInCondition[0] : 
        avg=average(dataset,dimensionName)
        newValueInCondition[0]=newValueInCondition[0].replace('avg',str(avg))
    if 'avg' in newValueInCondition[1] : 
        avg=average(dataset,dimensionName)
        newValueInCondition[1]=newValueInCondition[1].replace('avg',str(avg))
    if 'std' in newValueInCondition[0] : 
        std=standardDeviation(dataset,dimensionName)
        newValueInCondition[0]=newValueInCondition[0].replace('std',str(std))
    if 'std' in newValueInCondition[1] : 
        std=standardDeviation(dataset,dimensionName)
        newValueInCondition[1]=newValueInCondition[1].replace('std',str(std))
        
    newValueInCondition = [float(eval(newValueInCondition[0])),float(eval(newValueInCondition[1]))]
    
    for obj in dataset :
        if (newValueInCondition[0] <= float(obj[dimensionName]) <= newValueInCondition[1]):
            filteredDataSet.append(obj)
    return filteredDataSet     

def outInterval(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    avg=0
    std=0
    newValueInCondition = [str(valueInCondition)[0],str(valueInCondition)[1]]
    if 'avg' in newValueInCondition[0] : 
        avg=average(dataset,dimensionName)
        newValueInCondition[0]=newValueInCondition[0].replace('avg',str(avg))
    if 'avg' in newValueInCondition[1] : 
        avg=average(dataset,dimensionName)
        newValueInCondition[1]=newValueInCondition[1].replace('avg',str(avg))
    if 'std' in newValueInCondition[0] : 
        std=standardDeviation(dataset,dimensionName)
        newValueInCondition[0]=newValueInCondition[0].replace('std',str(std))
    if 'std' in newValueInCondition[1] : 
        std=standardDeviation(dataset,dimensionName)
        newValueInCondition[1]=newValueInCondition[1].replace('std',str(std))
        
    newValueInCondition = [float(eval(newValueInCondition[0])),float(eval(newValueInCondition[1]))]
    
    for obj in dataset :
        if not (newValueInCondition[0] <= float(obj[dimensionName]) <= newValueInCondition[1]):
            filteredDataSet.append(obj)
    return filteredDataSet   

def lowerThan(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    avg=0
    std=0
    newValueInCondition = str(valueInCondition)
    if 'avg' in newValueInCondition : 
        avg=average(dataset,dimensionName)
        newValueInCondition=newValueInCondition.replace('avg',str(avg))
    if 'std' in newValueInCondition : 
        std=standardDeviation(dataset,dimensionName)
        newValueInCondition=newValueInCondition.replace('std',str(std))
    newValueInCondition = float(eval(newValueInCondition))
    
    for obj in dataset :
        if (float(obj[dimensionName]) <= newValueInCondition):
            filteredDataSet.append(obj)
    return filteredDataSet 

def greaterThan(dataset,dimensionName,valueInCondition):
    filteredDataSet=[]
    
    avg=0
    std=0
    newValueInCondition = str(valueInCondition)
    if 'avg' in newValueInCondition : 
        avg=average(dataset,dimensionName)
        newValueInCondition=newValueInCondition.replace('avg',str(avg))
    if 'std' in newValueInCondition : 
        std=standardDeviation(dataset,dimensionName)
        newValueInCondition=newValueInCondition.replace('std',str(std))
    newValueInCondition = float(eval(newValueInCondition))
    for obj in dataset :
        
        if (float(obj[dimensionName]) >= newValueInCondition):
            filteredDataSet.append(obj)
    return filteredDataSet 



MAP_FILTER_TYPE={
    'equal':equal,
    'notEqual':notEqual,
    'inSet':inSet,
    'outSet':outSet,
    'inInterval':inInterval,
    'outInterval':outInterval,
    'lowerThan':lowerThan,
    'greaterThan':greaterThan
}

def filter_stage(dataset,stage): #the data set must be an array of dictionnaries
    
    filteredDataSet=[]
    typeOfCondition=(set(stage.keys()) & set(MAP_FILTER_TYPE.keys())).pop()
    valueOfCondition=stage[typeOfCondition]
    dimensionName=stage['dimensionName']
    filteredDataSet=MAP_FILTER_TYPE[typeOfCondition](dataset,dimensionName,valueOfCondition)
    return filteredDataSet


def filter_pipeline(dataset,pipeline):
    filteredDataSet=[dict(d) for d in dataset]
    for stage in pipeline:
        filteredDataSet=filter_stage(filteredDataSet,stage)
    return filteredDataSet
    
#add a function which do a pipeline instead of one stage ! 

#################################################################"""


def filterData_fromDataset_toDataset(dataset,pipeline):
    filteredDataset=filter_pipeline(dataset,pipeline)
    return filteredDataset

def filterData_fromDataset_toFile(dataset,fileDestinationPath,pipeline):
    filteredDataset=filter_pipeline(dataset, pipeline) ##Think if we can pass an ordered header
    writeCSVwithHeader(filteredDataset, filteredDataset[0].keys(), fileDestinationPath)
    
def filterData_fromFile_toDataset(fileSourcePath,pipeline):
    dataset,header=readCSVwithHeader(fileSourcePath)
    filteredDataset=filter_pipeline(dataset, pipeline)
    return filteredDataset

def filterData_fromFile_toFile(fileSourcePath,fileDestinationPath,pipeline):
    dataset,header=readCSVwithHeader(fileSourcePath)
    filteredDataset=filter_pipeline(dataset, pipeline)
    writeCSVwithHeader(filteredDataset, header, fileDestinationPath)

def filterData_fromRepository_toRepository(repoSourcePath,repoDestinationPath,pipeline):  
    votesExports = listFiles(repoSourcePath)
    for exportFile in iter(votesExports):
        datasetFullPath=repoSourcePath+'\\'+exportFile
        filteredDatasetFullPath=repoDestinationPath+'\\'+os.path.splitext(os.path.basename(exportFile))[0]+'_pairwiseStats.csv'
        filterData_fromFile_toFile(datasetFullPath,filteredDatasetFullPath)


# def workflowStage_filter(
#         inputs={},
#         configuration={},
#         outputs={}
#     ):
#     '''
#     @param inputs:  {sourceFile | sourceRepository | dataset}
#     @param configuration: {'pipeline'}
#     @param outputs: {destinationFile | destinationRepository | dataset}
#     '''
#     
#     pipeline=configuration['pipeline']
#     
#     if 'sourceFile' in inputs:
#         if 'destinationFile' in outputs:
#             filterData_fromFile_toFile(inputs['sourceFile'], outputs['destinationFile'],pipeline)
#         else :
#             outputs['dataset'] = filterData_fromFile_toDataset(inputs['sourceFile'],pipeline)
#     elif 'dataset' in inputs:
#         if 'destinationFile' in outputs:
#             filterData_fromDataset_toFile(inputs['dataset'], outputs['destinationFile'],pipeline)
#         else :
#             outputs['dataset'] = filterData_fromDataset_toDataset(inputs['dataset'],pipeline)
#     elif 'sourceRepository' in inputs and 'destinationRepository' in outputs:
#         filterData_fromRepository_toRepository(inputs['sourceRepository'], outputs['destinationRepository'],pipeline)
#         
#     
#     return outputs

def workflowStage_filter(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    '''
    @param inputs:  {dataset}
    @param configuration: {'pipeline'}
    @param outputs: {dataset}
    '''
    
    localConfiguration={}
    localConfiguration['pipeline']=configuration.get('pipeline',[])
    
                         
    outputs['dataset'] = filter_pipeline(inputs['dataset'],localConfiguration['pipeline'])
    
    return outputs
    
    