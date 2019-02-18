'''
Created on 14 nov. 2016

@author: Adnene
'''



import os
import shutil

from visualization_histograms.histogram3DPlot import drawHistogram3D
from util.jsonProcessing import writeJSON


def statistics3DimensionsFixedDim1(originalData,dimension1,valueDim1,dimension2,dimension3) :
    dataset = {}
    total = 0
    for index in range(len(originalData)) :
        
        row = originalData[index]
        if not (dataset.has_key(str(row[dimension2]))) :
            dataset[str(row[dimension2])]={'value':0,'label':0,'total':0,'composition':{}}
        if (row[dimension1]==valueDim1) :
            dataset[str(row[dimension2])]['value']+=1
            dataset[str(row[dimension2])]['label']+=1
            total+=1

            if not (dataset[str(row[dimension2])]['composition'].has_key(str(row[dimension3]))) :
                dataset[str(row[dimension2])]['composition'][str(row[dimension3])]=0
            dataset[str(row[dimension2])]['composition'][str(row[dimension3])]+=1
            
        dataset[str(row[dimension2])]['total']+=1

    for key in dataset :
        try:
            dataset[key]['value']=(float(dataset[key]['value'])/float(total))*100
            for key2 in dataset[key]['composition'] :
                try:
                    dataset[key]['composition'][key2]=(float(dataset[key]['composition'][key2])/float(total))*100
                except Exception:
                    dataset[key]['composition'][key2]=0
                
        except Exception:
            dataset[key]['value']=0
        
        dataset[key]['label'] = str("%d/%d" % (dataset[key]['label'],dataset[key]['total']))
    return dataset,total


def statistics3Dimensions(originalData,dimension1,dimension2,dimension3) :
    distinctsValues={}
    globalDataSet={}
    for index in range(len(originalData)) :
        distinctsValues[originalData[index][dimension1]]=originalData[index][dimension1]
    distinctsValues = distinctsValues.keys()
    distinctsValues.sort()
    
    for index in range(len(distinctsValues)):
        dataset,total = statistics3DimensionsFixedDim1(originalData,dimension1,distinctsValues[index],dimension2,dimension3) 
        globalDataSet[distinctsValues[index]]={}
        globalDataSet[distinctsValues[index]]['equal']=distinctsValues[index]
        globalDataSet[distinctsValues[index]]['dataset']=dataset
        globalDataSet[distinctsValues[index]]['total']=total
    
    return globalDataSet,originalData,dimension1,dimension2,dimension3


def generateHistograms3DOfStatistics(originalData,dimension1,dimension2,dimension3,destination) :

    if os.path.exists(destination):
        shutil.rmtree(destination)
        os.makedirs(destination)
    else  : 
        os.makedirs(destination)
        
    globalDataSet,originalData,dimension1,dimension2,dimension3=statistics3Dimensions(originalData,dimension1,dimension2,dimension3)
    
    for key in globalDataSet:
        plt,lgd = drawHistogram3D(globalDataSet[key]['dataset'],dimension1 +' = '+ str(globalDataSet[key]['equal'])+ ',' + 'TOTAL = ' + str(globalDataSet[key]['total']), dimension2, 'Percentage') 
        plt.savefig(destination+'\\'+dimension1 +' = '+ str(key).strip().replace(' ','_').replace('/','_').replace('?','_').replace('"','_'),dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
        plt.gcf().clear()


    writeJSON(globalDataSet,destination+'\\'+'overallStatistiques.json')
    writeJSON(originalData,destination+'\\'+'fullDetails.json')


def generateHistograms3DOfStatisticsFromDataset(originalData,dimension1,dimension2,dimension3,destination) :

    if os.path.exists(destination):
        shutil.rmtree(destination)
        os.makedirs(destination)
    else  : 
        os.makedirs(destination)
        
    globalDataSet,originalData,dimension1,dimension2,dimension3=statistics3Dimensions(originalData,dimension1,dimension2,dimension3)
    
    for key in globalDataSet:
        plt,lgd = drawHistogram3D(globalDataSet[key]['dataset'],dimension1 +' = '+ str(globalDataSet[key]['equal'])+ ',' + 'TOTAL = ' + str(globalDataSet[key]['total']), dimension2, 'Percentage') 
        plt.savefig(destination+'\\'+dimension1 +' = '+ str(key).strip().replace(' ','_').replace('/','_').replace('?','_').replace('"','_'),dpi=300, bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.clf()
        plt.gcf().clear()


    return globalDataSet

def workflowStage_histogramGenerator3D(
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
        'dimension2'='NATIONAL_PARTY',
        'dimension3'='COUNTRY'
    }
    @param outputs: {
       
        'statistics': 
    }
    '''
     
    localConfiguration={}
    localConfiguration['dimension1']=configuration.get('dimension1','GROUPE_ID') 
    localConfiguration['dimension2']=configuration.get('dimension2','NATIONAL_PARTY') 
    localConfiguration['dimension3']=configuration.get('dimension3','COUNTRY') 
    
    outputs['statistics']=generateHistograms3DOfStatisticsFromDataset(inputs['dataset'], localConfiguration['dimension1'], localConfiguration['dimension2'],localConfiguration['dimension3'], inputs['destinationRepository'])        
    
    return outputs
        