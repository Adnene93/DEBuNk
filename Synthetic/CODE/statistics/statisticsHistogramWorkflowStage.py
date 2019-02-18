'''
Created on 28 nov. 2016

@author: Adnene
'''
from statistics.statisticsExtraction3D import workflowStage_histogramGenerator3D
from statistics.statisticsExtraction2D import workflowStage_histogramGenerator2D

POSSIBLE_HISTOGRAMS_MAPS={
    'histograms2D':workflowStage_histogramGenerator2D,
    'histograms3D':workflowStage_histogramGenerator3D
}


def workflowStage_histogramGenerator(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'histograms_visualization',
        'inputs': {
            'dataset':[],
            'destinationRepository' : 'repository_path' # care the repository path will be deleted first before histograms are created !
        },
        'configuration': {
            'numberOfDimensions'=3
            'dimension1'='GROUPE_ID',
            'dimension2'='NATIONAL_PARTY',
            'dimension3'='COUNTRY',
            #or 2 ?
        },
        'outputs':{
            'statistics': 
        }
    }
    '''
    
     
    localConfiguration={}
    localConfiguration['numberOfDimensions']=configuration.get('numberOfDimensions',3)
    
    if localConfiguration['numberOfDimensions']==2 :
        POSSIBLE_HISTOGRAMS_MAPS['histograms2D'](inputs, configuration, outputs,workflow_stats)
    elif localConfiguration['numberOfDimensions']==3 :
        POSSIBLE_HISTOGRAMS_MAPS['histograms3D'](inputs, configuration, outputs,workflow_stats)
    
    return outputs
    