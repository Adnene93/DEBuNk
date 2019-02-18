'''
Created on 11 nov. 2016

@author: Adnene
'''

from measures.measurements import measures
from measures.similaritiesMajorities import similarity_vector_measure
from votesExtractionAndProcessing.pairwiseStatistics import transformDatasetToStatsDictionnary


NUMBERSHEADER_PAIRWISE_COMPARAISON=['SIMILARITY','DISTANCE','NB_VOTES']



def datasetPairwiseComparaison(mepsComparaison,usersAttributes):
    header_all= ['USER1']+['USER1_'+str(user_attr) for user_attr in usersAttributes[1:]]+\
                ['USER2']+['USER2_'+str(user_attr) for user_attr in usersAttributes[1:]]+\
                ['SIMILARITY','DISTANCE','NB_VOTES']
    
    dataset=[]
    for key1 in mepsComparaison.keys() : 
        for key2 in mepsComparaison[key1].keys() :
            obj={}
            for k in range(len(header_all)):
                obj[header_all[k]]=mepsComparaison[key1][key2][header_all[k]]
            dataset.append(obj)
    return dataset


def transformDatasetToComparaisonsDictionnary(dataset):
    comparaisonsDictionnary={}
    for obj in dataset:
        if not (comparaisonsDictionnary.has_key(obj['USER1'])) :
            comparaisonsDictionnary[obj['USER1']]={}
        comparaisonsDictionnary[obj['USER1']][obj['USER2']]=obj 
    return comparaisonsDictionnary


def transformComparaisonsDictionnaryToDataset(comparaisonsDictionnary):
    dataset=[]
    for key1 in comparaisonsDictionnary.keys() : 
        for key2 in comparaisonsDictionnary[key1].keys() :
            dataset.append(comparaisonsDictionnary[key1][key2])
    return dataset


def pairwiseComparaison(mepsStatistics, measure='AGREEMENT'):
    
    
    for key1 in mepsStatistics.keys() : 
        for key2 in mepsStatistics[key1].keys() :
            similarityFunction,distanceFunction=measures(measure)
            similarity = similarityFunction(mepsStatistics,key1,key2)
            distance = distanceFunction(mepsStatistics,key1,key2)
            mepsStatistics[key1][key2]['SIMILARITY']=similarity
            mepsStatistics[key1][key2]['DISTANCE']=distance
            
    return mepsStatistics

def pairwiseComparaisonVectors(mepsStatistics, measure='COS'):
    
    
    for key1 in mepsStatistics.keys() : 
        for key2 in mepsStatistics[key1].keys() :
            agree_prop,nb_votes = similarity_vector_measure(mepsStatistics,key1,key2,measure)
            if nb_votes>0:
                similarity=agree_prop/nb_votes
            else :
                similarity=float('nan')
            distance = 1-similarity
            mepsStatistics[key1][key2]['SIMILARITY']=similarity
            mepsStatistics[key1][key2]['DISTANCE']=distance
            
    return mepsStatistics

    
#################################################################################### 
###############################WorkflowStages####################################### 
#################################################################################### 


def pairwiseComparaisonFromStatistics_fromDataset_toDataset(statsDataset,usersAttributes,measure='AGREEMENT'):
    statsDictionnary=transformDatasetToStatsDictionnary(statsDataset)
    mepsComparaison=pairwiseComparaisonVectors(statsDictionnary,measure)
    dataset=datasetPairwiseComparaison(mepsComparaison,usersAttributes)
    return dataset

def workflowStage_extractPairwiseComps(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'pairwise_comparaisons',
        'inputs': {
            'dataset':[]
            #can be value or record
        },
        'configuration': {
            'method':'AGREEMENT' #AGREEMENT_ABST | RAJSKI,
            'users_attributes':[], #first attribute is the unique identifier
        },
        'outputs':{
            'dataset':[],
            'header':[],
            'numbersHeader':[]
        }
    }
    '''
    
    
    localConfiguration={}
    localConfiguration['method']=configuration.get('method','AGREEMENT')
    usersAttributes=configuration.get('users_attributes',[])
   
    outputs['dataset'] = pairwiseComparaisonFromStatistics_fromDataset_toDataset(inputs['dataset'],usersAttributes,measure=localConfiguration['method'])
    outputs['header'] = ['USER1']+['USER1_'+str(user_attr) for user_attr in usersAttributes[1:]]+\
                        ['USER2']+['USER2_'+str(user_attr) for user_attr in usersAttributes[1:]]
    outputs['numbersHeader']=NUMBERSHEADER_PAIRWISE_COMPARAISON
    
    return outputs