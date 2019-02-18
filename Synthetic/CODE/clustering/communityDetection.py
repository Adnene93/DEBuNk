'''
Created on 11 nov. 2016

@author: Adnene
'''
import csv
import os
import shutil
import subprocess
import unicodedata

from util.csvProcessing import writeCSVwithHeader, writeCSV


HEADER_CLUSTER_RESULTS=['ID','ROW_ID','COLUMN_ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','CLUSTER']


SIMPLE_LOUVAIN='simple'
FIXED_NUMBER_OF_COMMUNITIES_LOUVAIN='nb_clusters'


def writeLouvainResults(communityResults,destination) :
    writeCSVwithHeader(communityResults, communityResults[0].keys(), destination)


def applyLouvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,resolution=1.1) :
    
    
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    modularity_function = 1             #Modularity function (1 = standard; 2 = alternative)
    resolution_parameter = resolution   #Value of the resolution parameter
    optimization_algorithm = 3          #Algorithm for modularity optimization (1 = original Louvain algorithm; 2 = Louvain algorithm with multilevel refinement; 3 = SLM algorithm)
    n_random_starts = 10                #Number of random starts
    n_iterations = 10                   #Number of iterations per random start
    random_seed = 0                     #Seed of the random number generator
    print_output = 0                    #Whether or not to print output to the console (0 = no; 1 = yes)
    
    writeCSV(comparaisonGraphDataset, 'tmp\\graphTemporary.csv', delimiter='\t')
    command = 'java -jar ModularityOptimizer.jar '+'tmp\\graphTemporary.csv'+' '+'tmp\\communityTemporary.csv'+' '+str(modularity_function)+' '+str(resolution_parameter)+' '+str(optimization_algorithm)+' '+str(n_random_starts)+' '+str(n_iterations)+' '+str(random_seed)+' '+str(print_output)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()

    communities={}
    index =0
    with open('tmp\\communityTemporary.csv', 'rb') as csvfile:
        readfile = csv.reader(csvfile, delimiter='\t')
        for row in readfile :
            metadataDataset[int(index)]['CLUSTER']=str(row[0])
            if not communities.has_key(str(row[0])) :
                communities[str(row[0])]=0
            communities[str(row[0])]+=1
            index+=1
            
    
    shutil.rmtree('tmp')
    
    return metadataDataset,communities,resolution

def applyLouvainFixNumberOfCommunitiesFromDataset(metadataDataset,comparaisonGraphDataset,number=5,startResolution=1.5) : 
    resolution=startResolution
    oldResolution=1.5
    step=0.1

    communityResults,communities,resolutionUsed = applyLouvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,resolution)
    total = len(communities.keys())
    nbiter=100
    if total<number:
        while total < number:
            oldResolution=resolution
            resolution+=step
            communityResults,communities,resolutionUsed = applyLouvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,resolution)
            total = len(communities.keys())
            #print 'total = ',total
    elif total>number:
        while total > number:
            oldResolution=resolution
            resolution-=step
            communityResults,communities,resolutionUsed = applyLouvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,resolution)
            total = len(communities.keys())
            #print 'total = ',total
    
    while total!=number:
        communityResults,communities,resolutionUsed = applyLouvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,(oldResolution+resolution)/2)
        total = len(communities.keys())
        #print 'total = ',total
        if (total<number):
            usedResolution=(oldResolution+resolution)/2
            oldResolution=max(oldResolution,resolution)
            resolution=usedResolution
        else :
            usedResolution=(oldResolution+resolution)/2
            oldResolution=min(oldResolution,resolution)
            resolution=usedResolution
        nbiter=nbiter-1
        if (nbiter==0) : 
            break

    return communityResults,communities,resolution

def louvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,resolution=1.1) : 
    communityResults,communities,resolutionUsed = applyLouvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,resolution)
    return communityResults,communities,resolutionUsed

def louvainFixNumberOfCommunitiesFromDataset(metadataDataset,comparaisonGraphDataset,number=5) : 
    communityResults,communities,resolutionUsed=applyLouvainFixNumberOfCommunitiesFromDataset(metadataDataset,comparaisonGraphDataset,number)
    return communityResults,communities,resolutionUsed

def louvainFromDataset(metadataDataset,comparaisonGraphDataset,parameter=1.1,typeOfLouvain=SIMPLE_LOUVAIN):
    if (typeOfLouvain==SIMPLE_LOUVAIN):
        communityResults,communities,resolution=louvainSimpleFromDataset(metadataDataset,comparaisonGraphDataset,float(parameter))
    elif (typeOfLouvain==FIXED_NUMBER_OF_COMMUNITIES_LOUVAIN):
        communityResults,communities,resolution=louvainFixNumberOfCommunitiesFromDataset(metadataDataset,comparaisonGraphDataset,int(parameter))
    return communityResults,communities,resolution
#################################################################################### 
###############################WorkflowStages####################################### 
#################################################################################### 

def workflowStage_louvainClustering(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    '''
    @param inputs:  {metadataDataset | comparaisonGraphDataset}
    @param configuration: {
        'type' : 'nb_clusters',
        'parameter' : 5
    }
    @param outputs: {dataset | header }
    '''
    
    
    localConfiguration={}
    localConfiguration['type']=configuration.get('type','nb_clusters')
    localConfiguration['parameter']=configuration.get('parameter',5)
    metadataDataset=[dict(obj) for obj in inputs['metadataDataset']]
    communityResults,communities,resolution = louvainFromDataset(metadataDataset,inputs['comparaisonGraphDataset'],parameter=localConfiguration['parameter'],typeOfLouvain=localConfiguration['type'])
   
    outputs['dataset'] = communityResults
    outputs['header']=HEADER_CLUSTER_RESULTS
    
    
    return outputs




