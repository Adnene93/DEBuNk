'''
Created on 11 nov. 2016

@author: Adnene
'''



import math
from operator import itemgetter

#HEADER_METADATA_MEPS=['ID','ROW_ID','COLUMN_ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY']



def transformPairwiseSimilarities_comparaisonAll(dataset,usersAttributes,matrix_values='SIMILARITY',mep1_sortDimension='USER2_PARTY',mep2_sortDimension='USER1_PARTY',mep1_header='USER1',mep2_header='USER2'):
    d_mep1 = {}
    sorted_d_mep1 = {}
    inv_detailed_mep1={}
    sorted_inv_detailed_mep1 = {}
    
    d_mep2 = {}
    sorted_d_mep2 = {}
    inv_detailed_mep2={}
    sorted_inv_detailed_mep2 = {}
    
    
    #dataset = readPairwiseComparaison(source)
    i = 0;
    j = 0;
    for k in range(len(dataset)) : 
        if not (d_mep1.has_key(str(dataset[k]['USER1']))) :
            d_mep1[str(dataset[k]['USER1'])]=i
            inv_detailed_mep1[i]=dataset[k]
            i=i+1
        if not (d_mep2.has_key(str(dataset[k]['USER2']))) :
            d_mep2[str(dataset[k]['USER2'])]=j
            inv_detailed_mep2[j]=dataset[k]
            j=j+1
        
        
            
    simMatrix = [[float('nan') for k in range(len(d_mep2.keys()))] for j in range(len(d_mep1.keys()))] 
    
    #########################SORT NEW#########################################
    i=0
    for key in sorted(d_mep1) :
        sorted_d_mep1[key]= i
        sorted_inv_detailed_mep1[i]=inv_detailed_mep1[d_mep1[key]]
        i+=1
    i=0
    for key in sorted(d_mep2) :
        sorted_d_mep2[key]= i
        sorted_inv_detailed_mep2[i]=inv_detailed_mep2[d_mep2[key]]
        i+=1
    #########################SORT NEW#########################################

    #########################SORT NEW2#########################################
    i=0
    sorted_d2_mep1={}
    sorted_inv_detailed2_mep1={}
    for key,o in sorted(sorted_inv_detailed_mep1.items(), key=lambda x: x[1][mep1_sortDimension]) :
        sorted_d2_mep1[str(o['USER1'])]= i
        sorted_inv_detailed2_mep1[i]=sorted_inv_detailed_mep1[sorted_d_mep1[str(o['USER1'])]]
        i+=1
    inv_sorted_d2_mep1  = {v: k for k, v in sorted_d2_mep1.iteritems()} 
    i=0
    sorted_d2_mep2={}
    sorted_inv_detailed2_mep2={}
    for key,o in sorted(sorted_inv_detailed_mep2.items(), key=lambda x: x[1][mep2_sortDimension]) :
        sorted_d2_mep2[str(o['USER2'])]= i
        sorted_inv_detailed2_mep2[i]=sorted_inv_detailed_mep2[sorted_d_mep2[str(o['USER2'])]]
        i+=1
    inv_sorted_d2_mep2  = {v: k for k, v in sorted_d2_mep2.iteritems()} 
    
    #########################SORT NEW2#########################################"

    for k in range(len(dataset)) : 
        simMatrix[sorted_d2_mep1[str(dataset[k]['USER1'])]][sorted_d2_mep2[str(dataset[k]['USER2'])]] = str(dataset[k][matrix_values])
        simMatrix[sorted_d2_mep1[str(dataset[k]['USER1'])]][sorted_d2_mep2[str(dataset[k]['USER2'])]] = float(simMatrix[sorted_d2_mep1[str(dataset[k]['USER1'])]][sorted_d2_mep2[str(dataset[k]['USER2'])]].replace(',', '.'))
        
    k=0
    

    i = 0
    header = ['USERS']
    simMatrixWithHeader=[]
    
    for l in simMatrix :
        simMatrixWithHeader.append(l[:])
        #l.insert(0,inv_sorted_d2_mep1[i])
        i=i+1
        
    i=0
    
    for l2 in simMatrixWithHeader :
        l2.insert(0,sorted_inv_detailed2_mep1[i][mep1_header])  #unicodedata.normalize('NFD', unicode(,'iso-8859-1')).encode('ascii', 'ignore')
        i=i+1
    j=0
    for j in range(len(simMatrixWithHeader[0])-1) :
        header.append(sorted_inv_detailed2_mep2[j][mep2_header]) #unicodedata.normalize('NFD', unicode(,'iso-8859-1')).encode('ascii', 'ignore')
        #j=j+1
    i=0
    
    simMatrixWithHeader.insert(0,header)
    
    i = 0  
    #header=['ID','ROW_ID','COLUMN_ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY']
    header=['ID','ROW_ID','COLUMN_ID']+usersAttributes
    rowsToWrite={}
    arrayMetadata=[]
    metadataDataset=[]
    
    for key, value in sorted_inv_detailed2_mep1.items():
        rowsToWrite[value['USER1']] = [key,None]+[value['USER1']]+[value['USER1_'+str(user_attr)] for user_attr in usersAttributes[1:]]
        #[key,None,value['USER1'],value['MEP1_NAME'],value['MEP1_PARTY'],value['MEP1_GROUP'],value['MEP1_COUNTRY']]
    for key, value in sorted_inv_detailed2_mep2.items():
        if (rowsToWrite.has_key(value['USER2'])):     
            rowsToWrite[value['USER2']][1]=key   
        else :
            rowsToWrite[value['USER2']]=[None,key]+[value['USER2']]+[value['USER2_'+str(user_attr)] for user_attr in usersAttributes[1:]]
            #[None,key,value['USER2'],value['MEP2_NAME'],value['MEP2_PARTY'],value['MEP2_GROUP'],value['MEP2_COUNTRY']]
    
    metaID=0
    for key, row in sorted(sorted(rowsToWrite.items(), key=lambda x: x[1][0]), key=lambda x: x[1][1]):
        
        arrayMetadata.append([metaID]+row)
        metaID+=1
        
    for row in arrayMetadata:
        obj={}
        for index in range(len(header)) :
            obj[header[index]]=row[index]
        metadataDataset.append(obj)
    
    map_mep_1={}
    map_mep_2={}
    all_nodes_keys=[]
    for row in arrayMetadata:
        all_nodes_keys.append(row[0])
        if (row[1] is not None ):
            map_mep_1[row[0]]=row[1]
        if (row[2] is not None ):
            map_mep_2[row[0]]=row[2]
    
    
    resLouvain  = []
    for j in range(len(all_nodes_keys)) :
        for i in range(j) :
            if i in map_mep_1 and j in map_mep_2 : 
                if (not math.isnan(simMatrix[map_mep_1[i]][map_mep_2[j]]) and simMatrix[map_mep_1[i]][map_mep_2[j]]>0.0):
                    resLouvain.append([i,j,simMatrix[map_mep_1[i]][map_mep_2[j]]]) #,'Undirected'
                    k=k+1
    resLouvain = sorted(resLouvain, key=itemgetter(0))
    
    
    return simMatrixWithHeader,resLouvain,metadataDataset
        
    
def transformPairwiseComparaisons_fromDataset_toDataset(compDataset,configuration):
    comparaisonMatrix,comparaisonGraph,metadataDataset=transformPairwiseSimilarities_comparaisonAll(compDataset,configuration['user_attributes'],matrix_values=configuration['matrix_values'],mep1_sortDimension=configuration['user1_sortDimension'],mep2_sortDimension=configuration['user2_sortDimension'],mep1_header=configuration['user1_header'],mep2_header=configuration['user2_header'])
    return comparaisonMatrix,comparaisonGraph,metadataDataset



def workflowStage_transformPairwiseComparaison(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    '''
    {
    
        'id':'stage_id',
        'type':'pairwise_comparaison_transform',
        'inputs': {
            'dataset':[]
            #can be value or record
        },
        'configuration': {
            'users_attributes':[], #first attribute is the unique identifier,
            'matrix_values' : 'SIMILARITY', #DISTANCE | NB_VOTES
            'user1_sortDimension' :'USER1_PARTY',
            'user2_sortDimension' : 'USER2_PARTY',
            'user1_header' : 'USER1',
            'user2_header' : 'USER2'
        },
        'outputs':{
            'metadataDataset':[],
            'metadataHeader':[],
            'comparaisonMatrixDataset':[],
            'comparaisonGraphDataset':[]
        }
    }
    '''
    
    
    config_matrix_values=configuration.get('matrix_values','SIMILARITY')
    config_mep1_sortDimension=configuration.get('user1_sortDimension','USER1_PARTY')
    config_mep2_sortDimension=configuration.get('user2_sortDimension','USER2_PARTY')
    config_mep1_header=configuration.get('user1_header','USER1')
    config_mep2_header=configuration.get('user2_header','USER2')
    usersAttributes=configuration.get('users_attributes',[])
    
    localConfiguration={
        'matrix_values':config_matrix_values,
        'user1_sortDimension':config_mep1_sortDimension,
        'user2_sortDimension':config_mep2_sortDimension,
        'user1_header':config_mep1_header,
        'user2_header':config_mep2_header,
        'user_attributes':usersAttributes
    }
    
    
    metadataDatasetKey='metadataDataset'
    metadataHeader='metadataHeader'
    comparaisonMatrixDatasetKey='comparaisonMatrixDataset'
    comparaisonGraphDatasetKey='comparaisonGraphDataset'
    
    comparaisonMatrix,comparaisonGraph,metadataDataset = transformPairwiseComparaisons_fromDataset_toDataset(inputs['dataset'],localConfiguration)
    outputs[metadataDatasetKey] = metadataDataset
    outputs[metadataHeader]=['ID','ROW_ID','COLUMN_ID']+usersAttributes
    #outputs[metadataHeader]=['ID','ROW_ID','COLUMN_ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY']
    outputs[comparaisonMatrixDatasetKey] = comparaisonMatrix
    outputs[comparaisonGraphDatasetKey] = comparaisonGraph
    
    return outputs

