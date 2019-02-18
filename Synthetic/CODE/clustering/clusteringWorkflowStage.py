'''
Created on 29 nov. 2016

@author: Adnene
'''
from clustering.communityDetection import workflowStage_louvainClustering
from clustering.hierarchicClustering import workflowStage_hierarchicalClustering


POSSIBLE_CLUSTERINGS_MAPS={
    'louvain':workflowStage_louvainClustering,
    'hierarchic':workflowStage_hierarchicalClustering
}

def workflowStage_clusterer(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'clusterer',
        'inputs': {
            'metadataDataset':[],
            'comparaisonGraphDataset' : 'reference to the graph of similarities', # louvain
            'comparaisonMatrixDataset' : 'reference to the matrix of distances' # hierarchic
        },
        'configuration': {
            'clusteringApproach' : 'louvain', #hierarchic
            'type' : 'nb_clusters', #simple
            'parameter' : 5, #real value otherwise
            'method' : 'complete', #if hierarchic : single | average | complete | weighted | centroid | median | ward
            'label_dendrogramme':'NAME_FULL' #attribute from metadata in input
        },
        'outputs':{
            'dataset': [],
            'header': []
        }
    }
    '''
    
    
    
    clusteringApproachStage=POSSIBLE_CLUSTERINGS_MAPS[(set(POSSIBLE_CLUSTERINGS_MAPS.keys()) & set([configuration['clusteringApproach']])).pop()]
    clusteringApproachStage(inputs, configuration, outputs,workflow_stats)
    return outputs