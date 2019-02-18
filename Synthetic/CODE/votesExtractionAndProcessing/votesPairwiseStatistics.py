'''
Created on 11 janv. 2017

@author: Adnene
'''
#mapping_user_vote_all_comb={'AA', 'NN', 'YN', 'YA', 'NA', 'AN', 'YY', 'NY', 'AY'}

def extractVotesStatistics_fromdataset(dataset,votesAttributes,usersAttributes,position_attribute,verbose=False):
    vote_identifier=str(votesAttributes[0])
    user_identifier=str(usersAttributes[0])
    user_1_identifier='USER1'
    user_2_identifier='USER2'
     
    mepsStats={}
    mepsMeta={}
    listsOfVotes={}
    listsOfVotesHasKey=listsOfVotes.has_key
    #mapping_user_vote={'for':'Y','against':'N','abstain':'A'}

    for obj in dataset : 
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotesHasKey(vote_id)) :
            listsOfVotes[vote_id]=[]
        listsOfVotes[vote_id].append(obj) 
        
    iterValues=listsOfVotes.iteritems()
    for vote_id,actualVote in iterValues:
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
                        pairwiseStatsRowOfMep1[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':0,'++':set(),'**':set()}
                        pairOfMeps=pairwiseStatsRowOfMep1[mep2_index]     
                    
                    if mep1_object[position_attribute]==mep2_object[position_attribute]:
                        pairOfMeps['++'] |= {vote_id}
                        
                    pairOfMeps['**'] |= {vote_id}
                    pairOfMeps['NB_VOTES']=pairOfMeps['NB_VOTES']+1
    
    
    
    
    for mep1_index in mepsStats :
        for mep2_index in mepsStats[mep1_index]:
            pairwiseStatsRowOfMep2=mepsStats[mep2_index] 
            if not (mep2_index == mep1_index):
                pairwiseStatsRowOfMep2[mep1_index]=dict(mepsStats[mep1_index][mep2_index])
                pairOfMeps=pairwiseStatsRowOfMep2[mep1_index]
                pairOfMeps[user_1_identifier]=mep2_index   
                pairOfMeps[user_2_identifier]=mep1_index 
    
    mepsStatsNumbers={}
    
    for mep1_index in mepsStats :
        actualRow=mepsStats[mep1_index]
        mepsStatsNumbers[mep1_index]={}
        actualRowNumbers=mepsStatsNumbers[mep1_index]
        for mep2_index in mepsStats[mep1_index]:   
            pairOfMeps=actualRow[mep2_index]       
            actualRowNumbers[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index,'NB_VOTES':pairOfMeps['NB_VOTES']}
            actualRowNumbers[mep2_index]['++']=len(pairOfMeps['++'])
            #for comb in mapping_user_vote_all_comb:
    
    
    return mepsStats,mepsStatsNumbers,mepsMeta


def extractVotesStatistics_fromdataset_update(mepsStats,mepsMeta,votesAttributes,usersAttributes,position_attribute,votesSelected=None,mepsSelected=None,verbose=False):
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
            if mep2_index<=mep1_index:
                
                pairOfMeps_fromOld=pairwiseStatsRowOfMep1_fromOld[mep2_index] 
                
                actualRow[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                actualRowNumbers[mep2_index]={user_1_identifier : mep1_index,user_2_identifier : mep2_index}
                
                pairOfMeps=actualRow[mep2_index]
                pairOfMepsNumbers=actualRowNumbers[mep2_index]
                
                
                pairOfMeps['++']=pairOfMeps_fromOld['++'] & votesSelected
                pairOfMeps['**']=pairOfMeps_fromOld['**'] & votesSelected
                pairOfMepsNumbers['++']=len(pairOfMeps['++'])
                
                pairOfMeps['NB_VOTES']=pairOfMepsNumbers['NB_VOTES']=len(pairOfMeps['**'])
        
            
            
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