'''
Created on 14 nov. 2016

@author: Adnene
'''




import os
import shutil

from visualization_histograms.histogram2DPlot import drawHistogram2D
from util.jsonProcessing import writeJSON


def statistics2DimensionsFixedDim1(originalData,dimension1,valueDim1,dimension2) :
    dataset = {}
    total_dim1 = 0
    for index in range(len(originalData)) :
        
        row = originalData[index]
        if not (dataset.has_key(str(row[dimension2]))) :
            dataset[str(row[dimension2])]={'value':0,'label':0,'total_dim1':0}
        if (row[dimension1]==valueDim1) :
            dataset[str(row[dimension2])]['value']+=1
            dataset[str(row[dimension2])]['label']+=1
            total_dim1+=1
        dataset[str(row[dimension2])]['total_dim1']+=1

    for key in dataset :
        try:
            dataset[key]['value']=(float(dataset[key]['value'])/float(total_dim1))*100
        except Exception:
            dataset[key]['value']=0
        
        dataset[key]['label'] = str("%d/%d" % (dataset[key]['label'],dataset[key]['total_dim1']))
    return dataset,total_dim1


def statistics2Dimensions(originalData,dimension1,dimension2) :
    distinctsValues={}
    globalDataSet={}
    
    for index in range(len(originalData)) :
        distinctsValues[originalData[index][dimension1]]=originalData[index][dimension1]
    distinctsValues = distinctsValues.keys()
    distinctsValues.sort()

    for index in range(len(distinctsValues)):
        dataset,total = statistics2DimensionsFixedDim1(originalData,dimension1,distinctsValues[index],dimension2) 
        globalDataSet[distinctsValues[index]]={}
        globalDataSet[distinctsValues[index]]['equal']=distinctsValues[index]
        globalDataSet[distinctsValues[index]]['dataset']=dataset
        globalDataSet[distinctsValues[index]]['total']=total
    
    return globalDataSet,originalData,dimension1,dimension2


        
        
        


def generateHistograms2DOfStatistics(originalData,dimension1,dimension2,destination) :

    if os.path.exists(destination):
        shutil.rmtree(destination)
        os.makedirs(destination)
    else  : 
        os.makedirs(destination)
        
    globalDataSet,originalData,dimension1,dimension2=statistics2Dimensions(originalData,dimension1,dimension2)
    
    for key in globalDataSet:
        plt = drawHistogram2D(globalDataSet[key]['dataset'],dimension1 +' = '+ str(globalDataSet[key]['equal'])+ ',' + 'TOTAL = ' + str(globalDataSet[key]['total']), dimension2, 'Percentage') 
        plt.savefig(destination+'\\'+dimension1 +' = '+ str(key).strip().replace(' ','_').replace('/','_').replace('?','_').replace('"','_'),dpi=300)
        plt.clf()
        plt.gcf().clear()


    writeJSON(globalDataSet,destination+'\\'+'overallStatistiques.json')
    writeJSON(originalData,destination+'\\'+'fullDetails.json')
    

def generateHistograms2DOfStatisticsFromDataset(originalData,dimension1,dimension2,destination) :

    if os.path.exists(destination):
        shutil.rmtree(destination)
        os.makedirs(destination)
    else  : 
        os.makedirs(destination)
        
    globalDataSet,originalData,dimension1,dimension2=statistics2Dimensions(originalData,dimension1,dimension2)
    
    for key in globalDataSet:
        plt = drawHistogram2D(globalDataSet[key]['dataset'],dimension1 +' = '+ str(globalDataSet[key]['equal'])+ ',' + 'TOTAL = ' + str(globalDataSet[key]['total']), dimension2, 'Percentage') 
        plt.savefig(destination+'\\'+dimension1 +' = '+ str(key).strip().replace(' ','_').replace('/','_').replace('?','_').replace('"','_'),dpi=300)
        plt.clf()
        plt.gcf().clear()

    
    return globalDataSet





#################################################################################### 
###############################WorkflowStages####################################### 
#################################################################################### 

def workflowStage_histogramGenerator2D(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    '''
    @param inputs:  {
        'dataset' :  ,
        'destinationRepository' :
    }
    @param configuration: {
        'dimension1'='GROUPE_ID',
        'dimension2'='NATIONAL_PARTY'
    }
    @param outputs: {
        'statistics': 
    }
    '''
     
    localConfiguration={}
    localConfiguration['dimension1']=configuration.get('dimension1','GROUPE_ID') 
    localConfiguration['dimension2']=configuration.get('dimension2','NATIONAL_PARTY') 
    
    
    outputs['statistics']=generateHistograms2DOfStatisticsFromDataset(inputs['dataset'], localConfiguration['dimension1'], localConfiguration['dimension2'], inputs['destinationRepository'])        
    
    return outputs  
        