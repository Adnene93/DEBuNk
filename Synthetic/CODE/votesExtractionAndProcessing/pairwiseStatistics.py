'''
Created on 11 nov. 2016

@author: Adnene
'''
import csv
from itertools import product
from math import sqrt
import os
import shutil
from sys import stdout
from time import time 
import timeit
import unicodedata

from filterer.filter import filter_pipeline_obj
from util.util import printTimeSpent, listFiles


# HEADER_PAIRWISE_STATISTICS=['MEP1','MEP1_NAME','MEP1_PARTY','MEP1_GROUP','MEP1_COUNTRY',
#               'MEP2','MEP2_NAME','MEP2_PARTY','MEP2_GROUP','MEP2_COUNTRY',
#               'NB_VOTES','YY','NN','AA','YN','YA','NY','NA','AY','AN']
# 
# NUMBERSHEADER_PAIRWISE_STATISTICS=['NB_VOTES','YY','NN','AA','YN','YA','NY','NA','AY','AN']
# 
# VOTES_EXPORTS_HEADER=['VOTEID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID',
#               'COUNTRY','DOSSIERID','VOTE_DATE','USER_VOTE
#%EP ATTRIBUTES (first attribute is the unique identifier plz), VOTES ATTRIBUTES (first attribute is the unique identifier plz), POSITI
def datasetStatistics(mepsStatistics,mepsMeta,votesAttributes,usersAttributes,position_attribute):
    dataset=[]
    dataset_append=dataset.append
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    #print mepsMeta
#     all_header=['MEP1','MEP1_NAME','MEP1_PARTY','MEP1_GROUP','MEP1_COUNTRY',
#               'MEP2','MEP2_NAME','MEP2_PARTY','MEP2_GROUP','MEP2_COUNTRY',
#               'NB_VOTES','YY','NN','AA','YN','YA','NY','NA','AY','AN']
    for key1 in mepsStatistics.keys() : 
        for key2 in mepsStatistics[key1].keys() :
            
            obj = mepsStatistics[key1][key2]
            for attribute_user in usersAttributes[1:] :
                obj[user_1_identifier+'_'+attribute_user]=mepsMeta[obj['USER1']][attribute_user]
                obj[user_2_identifier+'_'+attribute_user]=mepsMeta[obj['USER2']][attribute_user]
            
#                 objToSend=OrderedDict({})
#                 for k in range(len(all_header)):
#                     objToSend[all_header[k]]
            dataset_append(obj)
    return dataset

def transformDatasetToStatsDictionnary(dataset):
    statsDictionnary={}
    for obj in dataset:
        if not (statsDictionnary.has_key(obj['USER1'])) :
            statsDictionnary[obj['USER1']]={}
        statsDictionnary[obj['USER1']][obj['USER2']]=obj 
    return statsDictionnary
def transformStatsDictionnaryToDataset(statsDictionnary):
    dataset=[]
    for key1 in statsDictionnary.keys() : 
        for key2 in statsDictionnary[key1].keys() :
            dataset.append(statsDictionnary[key1][key2])
    return dataset


     


def extractStatistics(sourceRep,nameFiles,votesAttributes,usersAttributes,position_attribute,nbFiles,verbose=False):
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    if verbose :
        print '\n---------------------------------------------------------------'
        print 'Extracting statistics from the splitted files, Percentage of completion : \n'  
    mepsStats={}
    mepsMeta={}
    mapping_user_vote={'for':'Y','against':'N','abstain':'A'}
    k=0
    for i in range (0,nbFiles) :
        
        name_file = nameFiles+'_'+str(i)+'.csv'
        listsOfVotes={}
        with open(sourceRep+'\\'+name_file, 'rb') as csvfile:
            readfile = csv.reader(csvfile, delimiter='\t')
            header=next(readfile)
            for row in readfile:
                obj={}
                for k in range(len(header)):
                    obj[header[k]]=str(row[k])
                vote_id=str(obj[vote_identifier])
                if not (listsOfVotes.has_key(vote_id)) :
                    listsOfVotes[vote_id]=[]
                
                listsOfVotes[vote_id].append(obj)

        mepsStatsHasKey = mepsStats.has_key
        
        for key in listsOfVotes.keys() :
            actualVote=listsOfVotes[key]
            range_actualVote=range(len(actualVote))
            for k in range_actualVote :
                mep1_object=actualVote[k]
                mep1_index=str(mep1_object[user_identifier])
                if not (mepsStatsHasKey(mep1_index)) :
                    mepsStats[mep1_index]={}
                    mepsMeta[mep1_index] = {attribute_user:mep1_object[attribute_user] for attribute_user in usersAttributes}
                pairwiseStatsRowOfMep1=mepsStats[mep1_index]    
                for j in range_actualVote :
                    mep2_object=actualVote[j]
                    mep2_index=str(mep2_object[user_identifier])
                    try:
                        pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]
                        pairOfMeps['NB_VOTES']=pairOfMeps['NB_VOTES']+1
                        statAttribute=mapping_user_vote[str(mep1_object[position_attribute])]+mapping_user_vote[str(mep2_object[position_attribute])]
                        pairOfMeps[statAttribute]+=1  
                    except Exception :
                        pairwiseStatsRowOfMep1[mep2_index]={
                            user_1_identifier : str(mep1_object[user_identifier]),
                            user_2_identifier : str(mep2_object[user_identifier]),
                            'NB_VOTES':0,
                            'YY':0,'NN':0,'AA':0,
                            'YN':0,'YA':0,
                            'NY':0,'NA':0,
                            'AY':0,'AN':0
                        }     
                        pairwiseStatsRowOfMep1[mep2_index]['NB_VOTES']=pairwiseStatsRowOfMep1[mep2_index]['NB_VOTES']+1
                        statAttribute=mapping_user_vote[str(mep1_object[position_attribute])]+mapping_user_vote[str(mep2_object[position_attribute])]
                        pairwiseStatsRowOfMep1[mep2_index][statAttribute]+=1
                    
        if verbose :
            stdout.write("\r%s %2.2f%s" % ('percentage  :', float(float(i)/float(nbFiles-1))*100 if nbFiles-1>0 else 100, '%'))
            stdout.flush()
    return mepsStats,mepsMeta

def extractStatistics_fromdataset(dataset,votesAttributes,usersAttributes,position_attribute,verbose=False):
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    if verbose :
        print '\n---------------------------------------------------------------'
        print 'Extracting statistics from the splitted files, Percentage of completion : \n'  
    mepsStats={}
    mepsMeta={}
    listsOfVotes={}
        
    mapping_user_vote={'for':'Y','against':'N','abstain':'A'}
    k=0
        
    for obj in dataset :
        
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotes.has_key(vote_id)) :
            listsOfVotes[vote_id]=[]
        listsOfVotes[vote_id].append(obj)

    mepsStatsHasKey = mepsStats.has_key
    
    for key in listsOfVotes.keys() :
        actualVote=listsOfVotes[key]
        range_actualVote=range(len(actualVote))
        for k in range_actualVote :
            mep1_object=actualVote[k]
            mep1_index=str(mep1_object[user_identifier])
            if not (mepsStatsHasKey(mep1_index)) :
                mepsStats[mep1_index]={}
                mepsMeta[mep1_index] = {attribute_user:mep1_object[attribute_user] for attribute_user in usersAttributes}
            pairwiseStatsRowOfMep1=mepsStats[mep1_index]    
            for j in range_actualVote :
                mep2_object=actualVote[j]
                mep2_index=str(mep2_object[user_identifier])
                try:
                    pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]
                    pairOfMeps['NB_VOTES']=pairOfMeps['NB_VOTES']+1
                    statAttribute=mapping_user_vote[str(mep1_object[position_attribute])]+mapping_user_vote[str(mep2_object[position_attribute])]
                    pairOfMeps[statAttribute]+=1  
                except Exception :
                    pairwiseStatsRowOfMep1[mep2_index]={
                        user_1_identifier : str(mep1_object[user_identifier]),
                        user_2_identifier : str(mep2_object[user_identifier]),
                        'NB_VOTES':0,
                        'YY':0,'NN':0,'AA':0,
                        'YN':0,'YA':0,
                        'NY':0,'NA':0,
                        'AY':0,'AN':0
                    }     
                    pairwiseStatsRowOfMep1[mep2_index]['NB_VOTES']=pairwiseStatsRowOfMep1[mep2_index]['NB_VOTES']+1
                    statAttribute=mapping_user_vote[str(mep1_object[position_attribute])]+mapping_user_vote[str(mep2_object[position_attribute])]
                    pairwiseStatsRowOfMep1[mep2_index][statAttribute]+=1
                
    return mepsStats,mepsMeta


def extractStatistics_fromdataset_opt(dataset,votesAttributes,usersAttributes,position_attribute,verbose=False):
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
     
    mepsStats={}
    mepsMeta={}
    listsOfVotes={}
    listsOfVotesHasKey=listsOfVotes.has_key
    mapping_user_vote={'for':'Y','against':'N','abstain':'A'}

    for obj in dataset : 
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotesHasKey(vote_id)) :
            listsOfVotes[vote_id]=[]
        listsOfVotes[vote_id].append(obj) 
        
    iterValues=iter(listsOfVotes.values())
    #print len(listsOfVotes.values())
    for actualVote in iterValues:
        
        for mep1_object in actualVote :
            mep1_index=str(mep1_object[user_identifier])
            try:
                pairwiseStatsRowOfMep1=mepsStats[mep1_index] 
            except:
                mepsStats[mep1_index],mepsMeta[mep1_index]={},{attribute_user:mep1_object[attribute_user] for attribute_user in usersAttributes}
                pairwiseStatsRowOfMep1=mepsStats[mep1_index]    
            
            for mep2_object in actualVote :
                mep2_index=str(mep2_object[user_identifier])
                if mep2_index<=mep1_index:
                    try:
                        pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]
                        
                    except Exception :
                        pairwiseStatsRowOfMep1[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'YY':0,'NN':0,'AA':0,'YN':0,'YA':0,'NY':0,'NA':0,'AY':0,'AN':0}
                        pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]     
                    
                    statAttribute=mapping_user_vote[mep1_object[position_attribute]]+mapping_user_vote[mep2_object[position_attribute]]
                    pairOfMeps['NB_VOTES'],pairOfMeps[statAttribute]=pairOfMeps['NB_VOTES']+1,pairOfMeps[statAttribute]+1
        
    
    for mep1_index in mepsStats :
        for mep2_index in mepsStats[mep1_index]:
            pairwiseStatsRowOfMep2=mepsStats[mep2_index] 
            if not (mep2_index == mep1_index):
                pairwiseStatsRowOfMep2[mep1_index]=dict(mepsStats[mep1_index][mep2_index])
                pairOfMeps=pairwiseStatsRowOfMep2[mep1_index]
                pairOfMeps[user_1_identifier]=mep2_index   
                pairOfMeps[user_2_identifier]=mep1_index 
    
        
    return mepsStats,mepsMeta

mapping_user_vote_all_comb={'AA', 'NN', 'YN', 'YA', 'NA', 'AN', 'YY', 'NY', 'AY'}

def extractStatistics_fromdataset_new(dataset,votesAttributes,usersAttributes,position_attribute,verbose=False):
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    
    
    mepsStats={}
    mepsMeta={}
    listsOfVotes={}
    listsOfVotesHasKey=listsOfVotes.has_key
    mapping_user_vote={'for':'Y','against':'N','abstain':'A'}

    for obj in dataset : 
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotesHasKey(vote_id)) :
            listsOfVotes[vote_id]=[]
        listsOfVotes[vote_id].append(obj) 
        
    iterValues=listsOfVotes.iteritems()
    #print len(listsOfVotes.values())
    for vote_id,actualVote in iterValues:
        #vote_id=actualVote[vote_identifier]
        for mep1_object in actualVote :
            mep1_index=str(mep1_object[user_identifier])
            try:
                pairwiseStatsRowOfMep1=mepsStats[mep1_index] 
            except:
                mepsStats[mep1_index],mepsMeta[mep1_index]={},{attribute_user:mep1_object[attribute_user] for attribute_user in usersAttributes}
                pairwiseStatsRowOfMep1=mepsStats[mep1_index]    
            
            for mep2_object in actualVote :
                    mep2_index=str(mep2_object[user_identifier])
                #if mep2_index<=mep1_index:
                    try:
                        pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]
                        
                    except Exception :
                        pairwiseStatsRowOfMep1[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'YY':set(),'NN':set(),'AA':set(),'YN':set(),'YA':set(),'NY':set(),'NA':set(),'AY':set(),'AN':set(),'**':set()}
                        pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]     
                    
                    statAttribute=mapping_user_vote[mep1_object[position_attribute]]+mapping_user_vote[mep2_object[position_attribute]]
                    pairOfMeps['NB_VOTES']=pairOfMeps['NB_VOTES']+1
                    
                    pairOfMeps[statAttribute] |= {vote_id}
                    #pairOfMeps['**'] |= {vote_id}
    
    
    
    
#     for mep1_index in mepsStats :
#         for mep2_index in mepsStats[mep1_index]:
#             pairwiseStatsRowOfMep2=mepsStats[mep2_index] 
#             if not (mep2_index == mep1_index):
#                 pairwiseStatsRowOfMep2[mep1_index]=dict(mepsStats[mep1_index][mep2_index])
#                 pairOfMeps=pairwiseStatsRowOfMep2[mep1_index]
#                 pairOfMeps[user_1_identifier]=mep2_index   
#                 pairOfMeps[user_2_identifier]=mep1_index 
    
    mepsStatsNumbers={}
    
    for mep1_index in mepsStats :
        actualRow=mepsStats[mep1_index]
        mepsStatsNumbers[mep1_index]={}
        actualRowNumbers=mepsStatsNumbers[mep1_index]
        for mep2_index in mepsStats[mep1_index]:   
            pairOfMeps=actualRow[mep2_index]       
            actualRowNumbers[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':pairOfMeps['NB_VOTES']}
            pairOfMepsNumbers=actualRowNumbers[mep2_index]
            for comb in mapping_user_vote_all_comb:
                pairOfMepsNumbers[comb]=len(pairOfMeps[comb])
    
    ################TO ADD EMPTY SET FOR PAIRS WHO HAD NEVER VOTED TOGETHER##############
    mepsArr=mepsMeta.keys()
    for mep1_index in mepsArr:
        for mep2_index in mepsArr:
            if not mepsStats[mep1_index].has_key(mep2_index):
                mepsStats[mep1_index][mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'YY':set(),'NN':set(),'AA':set(),'YN':set(),'YA':set(),'NY':set(),'NA':set(),'AY':set(),'AN':set(),'**':set()}
                mepsStatsNumbers[mep1_index][mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'YY':0,'NN':0,'AA':0,'YN':0,'YA':0,'NY':0,'NA':0,'AY':0,'AN':0,'**':0}
    ################TO ADD EMPTY SET FOR PAIRS WHO HAD NEVER VOTED TOGETHER##############    
    return mepsStats,mepsStatsNumbers,mepsMeta


def extractStatistics_fromdataset_new_update(mepsStats,mepsMeta,votesAttributes,usersAttributes,position_attribute,votesSelected=None,mepsSelected=None,verbose=False):
    #start=time()
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    newMepsNumbers={}
    newMepsStats={}
    newMepsMeta={k:v for k,v in mepsMeta.iteritems() if k in mepsSelected}
    
    
    
    #mapping_user_vote_all_comb={'AA', 'NN', 'YN', 'YA', 'NA', 'AN', 'YY', 'NY', 'AY'}
    
    for mep1_index in newMepsMeta :
        
        pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
        
        newMepsStats[mep1_index]={}
        actualRow=newMepsStats[mep1_index]
        
        newMepsNumbers[mep1_index]={}
        actualRowNumbers=newMepsNumbers[mep1_index]
        
        for mep2_index in newMepsMeta:
            #if mep2_index<=mep1_index:
                
                
                pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                
                actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                actualRowNumbers[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                
                pairOfMeps=actualRow[mep2_index]
                pairOfMepsNumbers=actualRowNumbers[mep2_index]
                
                nbvotes=0
                
                for comb in mapping_user_vote_all_comb:
                
                    pairOfMeps[comb]=pairOfMeps_fromOld[comb] & votesSelected
                    pairOfMepsNumbers[comb]=len(pairOfMeps[comb])
                    nbvotes+=pairOfMepsNumbers[comb]

                pairOfMeps['NB_VOTES']=pairOfMepsNumbers['NB_VOTES']=nbvotes
                #pairOfMeps['**']=pairOfMeps_fromOld['**'] & votesSelected
            
            
#     for mep1_index in newMepsStats :
#         for mep2_index in newMepsStats[mep1_index]:
#             if (mep2_index <> mep1_index):
#                 pairwiseStatsRowOfMep2=newMepsStats[mep2_index] 
#                 pairwiseStatsRowOfMep2Numbers=newMepsNumbers[mep2_index] 
#                 pairwiseStatsRowOfMep2[mep1_index],pairwiseStatsRowOfMep2Numbers[mep1_index]=dict(newMepsStats[mep1_index][mep2_index]),dict(newMepsNumbers[mep1_index][mep2_index])
#                 pairOfMeps,pairOfMepsNumbers=pairwiseStatsRowOfMep2[mep1_index],pairwiseStatsRowOfMep2Numbers[mep1_index]
#                 pairOfMeps[user_1_identifier]=pairOfMepsNumbers[user_1_identifier]=mep2_index   
#                 pairOfMeps[user_2_identifier]=pairOfMepsNumbers[user_2_identifier]=mep1_index   
    return newMepsStats,newMepsNumbers,newMepsMeta


def extractStatistics_fromdataset_new_update_not_square(mepsStats,mepsMeta,votesAttributes,usersAttributes,position_attribute,votesSelected=None,mepsSelected=None,mepsSelected_user1=None,mepsSelected_user2=None,verbose=False):
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    newMepsNumbers={}
    newMepsStats={}
    newMepsMeta={k:v for k,v in mepsMeta.iteritems() if k in mepsSelected}
    
    isSquare=(mepsSelected_user1==mepsSelected_user2)
    
    
    #mapping_user_vote_all_comb={'AA', 'NN', 'YN', 'YA', 'NA', 'AN', 'YY', 'NY', 'AY'}
    
    
    if not isSquare :
        
        for mep1_index in mepsSelected_user1 :
            
            pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
            
            newMepsStats[mep1_index]={}
            actualRow=newMepsStats[mep1_index]
            
            newMepsNumbers[mep1_index]={}
            actualRowNumbers=newMepsNumbers[mep1_index]
            
            for mep2_index in mepsSelected_user2:
                #if mep2_index<=mep1_index:
                    
                    
                    pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                    
                    actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    actualRowNumbers[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    
                    pairOfMeps=actualRow[mep2_index]
                    pairOfMepsNumbers=actualRowNumbers[mep2_index]
                    
                    nbvotes=0
                    
                    for comb in mapping_user_vote_all_comb:
                    
                        pairOfMeps[comb]=pairOfMeps_fromOld[comb] & votesSelected
                        pairOfMepsNumbers[comb]=len(pairOfMeps[comb])
                        nbvotes+=pairOfMepsNumbers[comb]
    
                    pairOfMeps['NB_VOTES']=pairOfMepsNumbers['NB_VOTES']=nbvotes
                    #pairOfMeps['**']=pairOfMeps_fromOld['**'] & votesSelected
    else :
        for mep1_index in mepsSelected_user1 :
            
            pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
            
            newMepsStats[mep1_index]={}
            actualRow=newMepsStats[mep1_index]
            
            newMepsNumbers[mep1_index]={}
            actualRowNumbers=newMepsNumbers[mep1_index]
            
            for mep2_index in mepsSelected_user2:
                if mep2_index<=mep1_index:
                    
                    
                    pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                    
                    actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    actualRowNumbers[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    
                    pairOfMeps=actualRow[mep2_index]
                    pairOfMepsNumbers=actualRowNumbers[mep2_index]
                    
                    nbvotes=0
                    
                    for comb in mapping_user_vote_all_comb:
                    
                        pairOfMeps[comb]=pairOfMeps_fromOld[comb] & votesSelected
                        pairOfMepsNumbers[comb]=len(pairOfMeps[comb])
                        nbvotes+=pairOfMepsNumbers[comb]
    
                    pairOfMeps['NB_VOTES']=pairOfMepsNumbers['NB_VOTES']=nbvotes
            
        if isSquare:
            for mep1_index in newMepsStats :
                for mep2_index in newMepsStats[mep1_index]:
                    if (mep2_index <> mep1_index):
                        pairwiseStatsRowOfMep2=newMepsStats[mep2_index] 
                        pairwiseStatsRowOfMep2Numbers=newMepsNumbers[mep2_index] 
                        pairwiseStatsRowOfMep2[mep1_index],pairwiseStatsRowOfMep2Numbers[mep1_index]=dict(newMepsStats[mep1_index][mep2_index]),dict(newMepsNumbers[mep1_index][mep2_index])
                        pairOfMeps,pairOfMepsNumbers=pairwiseStatsRowOfMep2[mep1_index],pairwiseStatsRowOfMep2Numbers[mep1_index]
                        pairOfMeps[user_1_identifier]=pairOfMepsNumbers[user_1_identifier]=mep2_index   
                        pairOfMeps[user_2_identifier]=pairOfMepsNumbers[user_2_identifier]=mep1_index   
    return newMepsStats,newMepsNumbers,newMepsMeta

#################""
def cartesian_product(v1,v2):
    return sum(x1*x2 for x1,x2 in zip(v1,v2))

def norm(v1):
    return sqrt(sum(x1**2 for x1 in v1))

def similarity_vector_COS(v1,v2): #MMAP : Majority Mean Agreement Proportion
    
    range3=range(3)
    similarity=0.
    scalar_product_v1_v2=0.
    norm_v1=0.
    norm_v2=0.
    for index in range3:
        scalar_product_v1_v2+=v1[index]*v2[index]
        norm_v1+=v1[index]**2
        norm_v2+=v2[index]**2
    scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
    similarity+=scalar_product_v1_v2
       
    return similarity
#################################################

def extractStatistics_fromdataset_vectors(dataset,votesAttributes,usersAttributes,position_attribute,user1_scope=[],user2_scope=[]):
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    
    
    
    mepsStats={}
    mepsMeta={}
    listsOfVotes={}
    listsOfVotesHasKey=listsOfVotes.has_key
    
    mapping_user_vote={'for':'Y','against':'N','abstain':'A'}
    users_map_details={}
    users_map_details_has_key=users_map_details.has_key
    for obj in dataset : 
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotesHasKey(vote_id)) :
            listsOfVotes[vote_id]=[]
        listsOfVotes[vote_id].append(obj) 
        
        
        d_user_id=obj[user_identifier]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:obj[key] for key in usersAttributes}   
     
    users_map_details_array=users_map_details.values()
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    
    users1_ids=set([x[user_identifier] for x in users_map_details_array_filtered_user1])
    users2_ids=set([x[user_identifier] for x in users_map_details_array_filtered_user2])
    
    nb_votes_all=len(listsOfVotes)
    iterValues=listsOfVotes.iteritems()
    for vote_id,actualVote in iterValues:
        for mep1_object in actualVote :
            if mep1_object[user_identifier] in users1_ids :
                mep1_index=str(mep1_object[user_identifier])
                try:
                    pairwiseStatsRowOfMep1=mepsStats[mep1_index] 
                except KeyError:
                    mepsStats[mep1_index],mepsMeta[mep1_index]={},{attribute_user:mep1_object[attribute_user] for attribute_user in usersAttributes}
                    pairwiseStatsRowOfMep1=mepsStats[mep1_index]    
                
                for mep2_object in actualVote:
                        if mep2_object[user_identifier] in users2_ids :
                            mep2_index=str(mep2_object[user_identifier])
                            try:
                                pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]
                                
                            except KeyError :
                                pairwiseStatsRowOfMep1[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'**':{},'ALL_VOTES':nb_votes_all,'FLAGCOMPUTED':False}  #FLAGCOMPUTED if computed then informations in stats matrix are vector similarity results and not vectos themselves
                                mepsMeta[mep2_index]={attribute_user:mep2_object[attribute_user] for attribute_user in usersAttributes}
                                pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]     

                            vector_mepwise12=(mep1_object[position_attribute],mep2_object[position_attribute])
                            pairOfMeps['**'][vote_id] = vector_mepwise12
                            pairOfMeps['NB_VOTES']=pairOfMeps['NB_VOTES']+1
    
    ################TO ADD EMPTY SET FOR PAIRS WHO HAD NEVER VOTED TOGETHER##############
    for mep1_index in users1_ids:
        for mep2_index in users2_ids:
            if mepsStats.has_key(mep1_index) and not mepsStats[mep1_index].has_key(mep2_index):
                mepsStats[mep1_index][mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'**':{},'ALL_VOTES':nb_votes_all,'FLAGCOMPUTED':False}
            mepsStats[mep1_index][mep2_index]['KEYS']=set(mepsStats[mep1_index][mep2_index]['**'])
    
    ################TO ADD EMPTY SET FOR PAIRS WHO HAD NEVER VOTED TOGETHER##############    
    
    return mepsStats,mepsMeta

def extractStatistics_fromdataset_new_update_not_square_vectors_WORKING(mepsStats,mepsMeta,votesAttributes,usersAttributes,position_attribute,votesSelected=None,mepsSelected=None,mepsSelected_user1=None,mepsSelected_user2=None,threshold_pair_comparaison=1,verbose=False):
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    all_votes_intersection=votesSelected
    dict_thresholding={};dict_thresholding_get=dict_thresholding.get
    newMepsStats={}
    newMepsMeta={k:v for k,v in mepsMeta.iteritems() if k in mepsSelected}
    nb_votes_all=float(len(votesSelected))
    isSquare=(mepsSelected_user1==mepsSelected_user2)

    if not isSquare :
        
        for mep1_index in mepsSelected_user1 :
            
            pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
            
            newMepsStats[mep1_index]={}
            actualRow=newMepsStats[mep1_index]            
            for mep2_index in mepsSelected_user2:

                    pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                    
                    actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    
                    pairOfMeps=actualRow[mep2_index]
                    #pairOfMeps['KEYS']=pairOfMeps_fromOld['KEYS'] & votesSelected
                    
                    pairOfMeps_fromOldVotes=pairOfMeps_fromOld['**']
                    
                    #pairOfMeps['**']={key:pairOfMeps_fromOldVotes[key] for key in votesSelected if key in pairOfMeps_fromOldVotes}
                    
                    new_votes_dic={}
                    pairOfMeps_keys=votesSelected&pairOfMeps_fromOldVotes.viewkeys()
                    relevant_pair=len(pairOfMeps_keys)>=threshold_pair_comparaison
                    for key in pairOfMeps_keys :
                        new_votes_dic[key]=pairOfMeps_fromOldVotes[key]
                        if relevant_pair:
                            dict_thresholding[key]=dict_thresholding_get(key,0.)+new_votes_dic[key] if mep2_index<>mep1_index else dict_thresholding_get(key,0.)+2*new_votes_dic[key]
                            
                        
                    pairOfMeps['**']=new_votes_dic
                    all_votes_intersection&=new_votes_dic.viewkeys()
                    
                    pairOfMeps['FLAGCOMPUTED']=pairOfMeps_fromOld['FLAGCOMPUTED']
                    all_votes_of_pair=pairOfMeps['**']
                    
                    pairOfMeps['NB_VOTES']=len(all_votes_of_pair)
                    pairOfMeps['ALL_VOTES']=nb_votes_all

    else :
        for mep1_index in mepsSelected_user1 :
            
            pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
            
            newMepsStats[mep1_index]={}
            actualRow=newMepsStats[mep1_index]
            
            for mep2_index in mepsSelected_user2:
                if mep2_index<=mep1_index:
                    
                    
                    pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                    
                    actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    
                    pairOfMeps=actualRow[mep2_index]
                    #pairOfMeps['KEYS']=pairOfMeps_fromOld['KEYS'] & votesSelected
                    
                    pairOfMeps_fromOldVotes=pairOfMeps_fromOld['**']
                    
                    #pairOfMeps['**']={key:pairOfMeps_fromOldVotes[key] for key in votesSelected if key in pairOfMeps_fromOldVotes}
                    new_votes_dic={}
                    pairOfMeps_keys=votesSelected&pairOfMeps_fromOldVotes.viewkeys()
                    relevant_pair=len(pairOfMeps_keys)>=threshold_pair_comparaison
                    for key in pairOfMeps_keys :
                        new_votes_dic[key]=pairOfMeps_fromOldVotes[key]
                        if relevant_pair:
                            dict_thresholding[key]=dict_thresholding_get(key,0.)+new_votes_dic[key] if mep2_index==mep1_index else dict_thresholding_get(key,0.)+2*new_votes_dic[key]
                            
                    
                    pairOfMeps['**']=new_votes_dic
                    all_votes_intersection&=new_votes_dic.viewkeys()
                    
                    pairOfMeps['FLAGCOMPUTED']=pairOfMeps_fromOld['FLAGCOMPUTED']
                    
                    all_votes_of_pair=pairOfMeps['**']
                    pairOfMeps['NB_VOTES']=len(all_votes_of_pair)
                    pairOfMeps['ALL_VOTES']=nb_votes_all
                    
        
        
        for mep1_index in newMepsStats :
            for mep2_index in newMepsStats[mep1_index]:
                if (mep2_index <> mep1_index):
                    pairwiseStatsRowOfMep2=newMepsStats[mep2_index] 
                    pairwiseStatsRowOfMep2[mep1_index]=dict(newMepsStats[mep1_index][mep2_index])
                    pairOfMeps=pairwiseStatsRowOfMep2[mep1_index]
                    pairOfMeps[user_1_identifier]=mep2_index   
                    pairOfMeps[user_2_identifier]=mep1_index 
        
        #dict_thresholding=dict(sorted({key:sum(newMepsStats[mep1_index][mep2_index]['**'][key] for mep1_index in newMepsStats for mep2_index in newMepsStats[mep1_index] if len(newMepsStats[mep1_index][mep2_index]['**'])>=threshold_pair_comparaison) for key in all_votes_intersection}.iteritems(),key = lambda x :x[1])[:int(threshold_pair_comparaison)])        
        dict_thresholding=dict(sorted(dict_thresholding.iteritems(),key=lambda x : x[1])[:int(threshold_pair_comparaison)])
    #print sum(float(x)/float(len(votesSelected)) for x in dict_thresholding.values()), len(all_votes_intersection)
    #print len(all_votes_intersection),len(votesSelected)
    return newMepsStats,newMepsMeta,dict_thresholding.viewkeys()




def extractStatistics_fromdataset_new_update_not_square_vectors(mepsStats,mepsMeta,votesAttributes,usersAttributes,position_attribute,votesSelected=None,mepsSelected=None,mepsSelected_user1=None,mepsSelected_user2=None,threshold_pair_comparaison=1,verbose=False):
    user_1_identifier='USER1'
    user_2_identifier='USER2'
    #all_votes_intersection=votesSelected
    newMepsStats={}
    newMepsMeta={k:v for k,v in mepsMeta.iteritems() if k in mepsSelected}
    nb_votes_all=float(len(votesSelected))
    isSquare=(mepsSelected_user1==mepsSelected_user2)

    if not isSquare :
        
        for mep1_index in mepsSelected_user1 :
            
            pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
            
            newMepsStats[mep1_index]={}
            actualRow=newMepsStats[mep1_index]            
            for mep2_index in mepsSelected_user2:

                    pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                    
                    actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    
                    pairOfMeps=actualRow[mep2_index]
                    #pairOfMeps['KEYS']=pairOfMeps_fromOld['KEYS'] & votesSelected
                    
                    pairOfMeps_fromOldVotes=pairOfMeps_fromOld['**']
                    
                    #pairOfMeps['**']={key:pairOfMeps_fromOldVotes[key] for key in votesSelected if key in pairOfMeps_fromOldVotes}
                    
                    new_votes_dic={}
                    for key in votesSelected:
                        if key in pairOfMeps_fromOldVotes:
                            new_votes_dic[key]=pairOfMeps_fromOldVotes[key]
                    
                        
                    pairOfMeps['**']=new_votes_dic
                    #all_votes_intersection&=new_votes_dic.viewkeys()
                    
                    pairOfMeps['FLAGCOMPUTED']=pairOfMeps_fromOld['FLAGCOMPUTED']
                    all_votes_of_pair=pairOfMeps['**']
                    
                    pairOfMeps['NB_VOTES']=len(all_votes_of_pair)
                    pairOfMeps['ALL_VOTES']=nb_votes_all

    else :
        for mep1_index in mepsSelected_user1 :
            
            pairwiseStatsRowOfMep1_fromOld=mepsStats[mep1_index] 
            
            newMepsStats[mep1_index]={}
            actualRow=newMepsStats[mep1_index]
            
            for mep2_index in mepsSelected_user2:
                if mep2_index<=mep1_index:
                    
                    
                    pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                    
                    actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                    
                    pairOfMeps=actualRow[mep2_index]
                    #pairOfMeps['KEYS']=pairOfMeps_fromOld['KEYS'] & votesSelected
                    
                    pairOfMeps_fromOldVotes=pairOfMeps_fromOld['**']
                    
                    #pairOfMeps['**']={key:pairOfMeps_fromOldVotes[key] for key in votesSelected if key in pairOfMeps_fromOldVotes}
                    new_votes_dic={}
                    for key in votesSelected:
                        if key in pairOfMeps_fromOldVotes:
                            new_votes_dic[key]=pairOfMeps_fromOldVotes[key]
                    
                    pairOfMeps['**']=new_votes_dic
                    #all_votes_intersection&=new_votes_dic.viewkeys()
                    
                    pairOfMeps['FLAGCOMPUTED']=pairOfMeps_fromOld['FLAGCOMPUTED']
                    
                    all_votes_of_pair=pairOfMeps['**']
                    pairOfMeps['NB_VOTES']=len(all_votes_of_pair)
                    pairOfMeps['ALL_VOTES']=nb_votes_all
                    
        
        
        for mep1_index in newMepsStats :
            for mep2_index in newMepsStats[mep1_index]:
                if (mep2_index <> mep1_index):
                    pairwiseStatsRowOfMep2=newMepsStats[mep2_index] 
                    pairwiseStatsRowOfMep2[mep1_index]=dict(newMepsStats[mep1_index][mep2_index])
                    pairOfMeps=pairwiseStatsRowOfMep2[mep1_index]
                    pairOfMeps[user_1_identifier]=mep2_index   
                    pairOfMeps[user_2_identifier]=mep1_index 
        
        
    #print sum(float(x)/float(len(votesSelected)) for x in dict_thresholding.values()), len(all_votes_intersection)
    #print len(all_votes_intersection),len(votesSelected)
    return newMepsStats,newMepsMeta



def splitFilesFromDataset(votesDataset,destination,votesAttributes,usersAttributes,position_attribute,granularity=0,verbose=False) :
    
    nblignes=0
    allkeys=0
    listsOfVotes={}
    
    votes_identifier=str(votesAttributes[0])
    
    header=votesAttributes+usersAttributes+[position_attribute]         ##Assume hat the first header is the vote id
    
     
    
    for obj in votesDataset:
        nblignes+=1
        if not (listsOfVotes.has_key(str(obj[votes_identifier]))) :
            listsOfVotes[str(obj[votes_identifier])]=[]
            allkeys+=1
        listsOfVotes[str(obj[votes_identifier])].append(obj)

    if (granularity==0) : 
        granularity=int((float(allkeys)/float(nblignes))*3500)+1
    k=0
    arrKeys=[]
    for key in listsOfVotes.keys() :
        if (k==0) :
            arrKeys.append([])
        arrKeys[len(arrKeys)-1].append(key)
        k+=1
        if (k>=granularity) :
            k=0
    if verbose : 
        print '\n---------------------------------------------------------------'
        print 'Splitting votes ' + ' onto '+ str(len(arrKeys)) + ' files ...'
        print '---------------------------------------------------------------\n'
    for ind in range(len(arrKeys)) :
        with open(destination+"\\"+os.path.splitext('splitted')[0]+"_"+str(ind)+".csv", "wb") as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(header)
            for key in arrKeys[ind] :
                for j in range(len(listsOfVotes[key])) :
                    rowToWrite=[]
                    for k in range(len(header)) :
                        rowToWrite.append(listsOfVotes[key][j][header[k]])
                    writer.writerow(rowToWrite)
    
    return len(arrKeys)      


    
def extractStatisticsFromDataset(votesDataset,votesAttributes,usersAttributes,position_attribute,user1_scope=[],user2_scope=[],granularity=0,verbose=False,bigfile=False):
    if bigfile :
        startFirst = timeit.time()
        if not os.path.exists('splitted'):
            os.makedirs('splitted')
        nbFiles = splitFilesFromDataset(votesDataset,'splitted',votesAttributes,usersAttributes,position_attribute,granularity=granularity,verbose=verbose)
        stop = timeit.time()
          
        if verbose : 
            print '\n---------------------------------------------------------------'
            print 'total files created = ', nbFiles
            printTimeSpent('time elapsed : ',startFirst,stop) 
            print '---------------------------------------------------------------\n'
        mepsStatistics,mepsMeta = extractStatistics('splitted','splitted',votesAttributes,usersAttributes,position_attribute,nbFiles,verbose=verbose)
        shutil.rmtree('splitted')
        dataset=datasetStatistics(mepsStatistics, mepsMeta,votesAttributes,usersAttributes,position_attribute)
    else :
        mepsStats,mepsMeta = extractStatistics_fromdataset_vectors(votesDataset,votesAttributes,usersAttributes,position_attribute,user1_scope,user2_scope)
        dataset=datasetStatistics(mepsStats, mepsMeta,votesAttributes,usersAttributes,position_attribute)
    return dataset 

   
 
    
#################################################################################### 
###############################WorkflowStages####################################### 
#################################################################################### 


    
def workflowStage_extractPairwiseStats(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
       
    '''
    {
       
        'id':'stage_id',
        'type':'pairwise_votes_stats',
        'inputs': {
            'dataset':[]
            #can be value or record
        },
        'configuration': {
            #'granularity':'0' #for experts, keep 0 if you don't want to mess with the execution time :-)
#             'votes_attributes':[], #first attribute is the unique identifier
#             'users_attributes':[], #first attribute is the unique identifier
#             'position_attribute':'U'
                   
            #'bigfile':False   #if bigfile is true call a function which reduce the use of memory in counterparts of time
        },
        'outputs':{
            'dataset':[],
            'header':[]
        }
    }
    '''
       
       
    localConfiguration={}
    localConfiguration['granularity']=configuration.get('granularity',0) 
    localConfiguration['bigfile']=configuration.get('bigfile',False)
       
    votesAttributes=configuration.get('votes_attributes',[])
    usersAttributes=configuration.get('users_attributes',[])
    position_attribute=configuration.get('position_attribute','')
    user_1_scope=configuration.get('user_1_scope',[])
    user_2_scope=configuration.get('user_2_scope',[])
    outputs['dataset'] = extractStatisticsFromDataset(inputs['dataset'],votesAttributes,usersAttributes,position_attribute,user_1_scope,user_2_scope,granularity=localConfiguration['granularity'],verbose=False,bigfile=localConfiguration['bigfile']) 
    outputs['header']=votesAttributes+usersAttributes+[position_attribute]
    outputs['numbersHeader']=['NB_VOTES','YY','NN','AA','YN','YA','NY','NA','AY','AN'] #we can check this after
    return outputs

def workflowStage_extractPairwiseStats2(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
      
    '''
    {
      
        'id':'stage_id',
        'type':'pairwise_votes_stats',
        'inputs': {
            'dataset':[],
              
            'mepsStats':[],
            'mepsMeta':[],
            'votesSelected':[],
            'mepsSelected':[]
              
              
        },
        'configuration': {
            #'granularity':'0' #for experts, keep 0 if you don't want to mess with the execution time :-)
#             'votes_attributes':[], #first attribute is the unique identifier
#             'users_attributes':[], #first attribute is the unique identifier
#             'position_attribute':'U',
            'update':False
            #'bigfile':False   #if bigfile is true call a function which reduce the use of memory in counterparts of time
        },
        'outputs':{
            'dataset':[],
            'mepsStats':{},
            'mepsMeta':{}
            'header':[]
        }
    }
    '''
      
      
      
      
      
    localConfiguration={}
    localConfiguration['granularity']=configuration.get('granularity',0) 
    localConfiguration['update']=configuration.get('update',False)
    update=localConfiguration['update']
      
    votesAttributes=configuration.get('votes_attributes',[])
    usersAttributes=configuration.get('users_attributes',[])
    position_attribute=configuration.get('position_attribute','')
      
    if not update:
        returned_mepsStatistics,pattern_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new(inputs['dataset'],votesAttributes,usersAttributes,position_attribute,verbose=False)
    else :
        mepsStats=inputs['mepsStats']
        mepsMeta=inputs['mepsMeta']
        votesSelected=inputs['votesSelected']
        mepsSelected=inputs['mepsSelected']
        returned_mepsStatistics,pattern_mepsStatsNumbers,returned_mepsMeta = extractStatistics_fromdataset_new_update(mepsStats, mepsMeta, votesAttributes, usersAttributes, position_attribute, votesSelected, mepsSelected, verbose=False)
      
    dataset=datasetStatistics(pattern_mepsStatsNumbers, returned_mepsMeta,votesAttributes,usersAttributes,position_attribute)
      
    outputs['mepsStats'] = returned_mepsStatistics
    outputs['mepsMeta'] = returned_mepsMeta
    outputs['dataset'] = dataset
    outputs['header']=votesAttributes+usersAttributes+[position_attribute]
    outputs['numbersHeader']=['NB_VOTES','YY','NN','AA','YN','YA','NY','NA','AY','AN'] #we can check this after
    return outputs
