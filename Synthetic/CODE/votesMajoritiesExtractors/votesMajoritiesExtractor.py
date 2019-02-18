'''
Created on 20 janv. 2017

@author: Adnene
'''
from math import sqrt
#from numba import jit

def compute_majorities_in_votes_dataset_multi_layers_oldWORKING(dataset,votesAttributes,usersAttributes,usersAggregationAttributes,position_attribute,nb_aggregation_min=0,vector_of_outcome=None,method_aggregation_outcome='VECTOR_VALUES'): #[vector_of_outcome=['attr1,'attr2]]
    #mapping_user_vote={'for':'Y','against':'N','abstain':'A'}

    distinct_actions=set()
    vote_identifier=str(votesAttributes[0])
    user_identifier_mep=str(usersAttributes[0])

    datasetToReturn=dataset[:]
    listsOfVotes={}
    listsOfVotesHasKey=listsOfVotes.has_key
    
    mepsmeta_majorities={}
    mepsmeta_majorities_layers={}
    
    len_usersAggregationAttributes=len(usersAggregationAttributes) if usersAggregationAttributes is not None else 0
    
    possibleUsersAggregationsAttr=[usersAggregationAttributes[i:] for i in range(len_usersAggregationAttributes)]+[[]] 
    layers=range(1,len(possibleUsersAggregationsAttr)+1)
    #print possibleUsersAggregationsAttr
    
    for obj in dataset : 
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotesHasKey(vote_id)) :
            listsOfVotes[vote_id]={}
        #listsOfVotes[vote_id].append(obj)
        
        for arr,arr_layer in zip(possibleUsersAggregationsAttr,layers):
            if arr<>[]: #TODO!
                user_identifier=tuple([obj[x] for x in arr])
                user_identifier_majority='majority'+'_'+'_'.join(user_identifier)
            else:
                user_identifier=tuple([x for x in arr])
                user_identifier_majority='all'
            
            if not mepsmeta_majorities.has_key(user_identifier_majority):
                mepsmeta_majorities[user_identifier_majority]=set()
                mepsmeta_majorities_layers[user_identifier_majority]={'layer': arr_layer,'attr':arr}
            mepsmeta_majorities[user_identifier_majority]|={obj[user_identifier_mep]}
            
                
            if not listsOfVotes[vote_id].has_key(user_identifier_majority):
                listsOfVotes[vote_id][user_identifier_majority]=[]
            listsOfVotes[vote_id][user_identifier_majority].append(obj)
    
    
    for vote_id in listsOfVotes : 
        votes=listsOfVotes[vote_id]
        for user_identifier_majority in votes : 
            if len(mepsmeta_majorities[user_identifier_majority])>=nb_aggregation_min: #TOODOO !
            #user_identifier_majority='majority'+'_'+'_'.join(majority_user)
                votes_majority_user_splitted={}
                for item in votes[user_identifier_majority]:
                    
                    position_item=item.get(position_attribute,0.)
                    distinct_actions|={position_item}
                    if not votes_majority_user_splitted.has_key(position_item):
                        votes_majority_user_splitted[position_item]=0
                    votes_majority_user_splitted[position_item]+=1
                new_user_and_vote_entry={v_attr:item[v_attr] for v_attr in votesAttributes}
                new_user_and_vote_entry.update({u_attr:user_identifier_majority for u_attr in usersAttributes if u_attr <> 'MAJORITY'})
                new_user_and_vote_entry.update({u_attr:item[u_attr]for u_attr in mepsmeta_majorities_layers[user_identifier_majority]['attr']})
                
                new_user_and_vote_entry.update({position_attribute:votes_majority_user_splitted}) #new vector
                new_user_and_vote_entry['MAJORITY']=mepsmeta_majorities_layers[user_identifier_majority]['layer']
                
                #smepsmeta_majorities[votes_majority_user_splitted]
                if usersAggregationAttributes is not None:
                    datasetToReturn.append(new_user_and_vote_entry)
    #vector_of_actions=('Y','N','A')    
    #vector_of_actions=('for','against','abstain')
    vector_of_actions=tuple(sorted(distinct_actions))    
    
    ##############################
    if vector_of_outcome is None or method_aggregation_outcome=='VECTOR_VALUES':
        vector_of_outcome=None
        print 'possible Outcomes are : ', vector_of_actions
    
    
    
    for x in datasetToReturn:
        #print x[position_attribute]
        x['MAJORITY']=x.get('MAJORITY',0)
        if not x['MAJORITY']:
            
            
            if vector_of_outcome is None :
                x[position_attribute]={x[position_attribute]:1.}
            else :
                vector_of_actions=vector_of_outcome
                x[position_attribute]={f:x[f] for f in vector_of_actions}
                
            
            x[position_attribute]=tuple([x[position_attribute].get(pos,0.) for pos in vector_of_actions])
            #x[position_attribute]=tuple([float(x[position_attribute].get(pos,0.)) for pos in vector_of_actions])
            
        else :
            if usersAggregationAttributes is not None:
            #x[position_attribute]={mapping_user_vote[k]:v for k,v in x[position_attribute].iteritems()}
                x[position_attribute]=tuple([float(x[position_attribute].get(pos,0.)) for pos in vector_of_actions])
                #x[position_attribute]+=(float(len(mepsmeta_majorities[x[user_identifier_mep]]))-sum(x[position_attribute]),)
                x[user_identifier_mep]=x[user_identifier_mep]+'_'+str(len(mepsmeta_majorities[x[user_identifier_mep]])) 
    return datasetToReturn,mepsmeta_majorities 


def compute_majorities_in_votes_dataset_multi_layers(dataset,votesAttributes,usersAttributes,usersAggregationAttributes,position_attribute,nb_aggregation_min=0,vector_of_outcome=None,method_aggregation_outcome='VECTOR_VALUES'): #[vector_of_outcome=['attr1,'attr2]]
    #mapping_user_vote={'for':'Y','against':'N','abstain':'A'}

    
    mepsmeta_majorities={}
    ##############################
    if vector_of_outcome is None or method_aggregation_outcome=='VECTOR_VALUES':
        vector_of_outcome=None
        vector_of_actions=tuple(sorted(set(x[position_attribute] for x in dataset)))  
        print 'possible Outcomes are : ', vector_of_actions
        
    
    
    for x in dataset:
        #print x[position_attribute]
        x['MAJORITY']=x.get('MAJORITY',0)
        if not x['MAJORITY']:
            
            
            if vector_of_outcome is None :
                x[position_attribute]={x[position_attribute]:1.}
            else :
                vector_of_actions=vector_of_outcome
                x[position_attribute]={f:x[f] for f in vector_of_actions}
                
            
            x[position_attribute]=tuple([x[position_attribute].get(pos,0.) for pos in vector_of_actions])
            #x[position_attribute]=tuple([float(x[position_attribute].get(pos,0.)) for pos in vector_of_actions])
            
        else :
            if usersAggregationAttributes is not None:
            #x[position_attribute]={mapping_user_vote[k]:v for k,v in x[position_attribute].iteritems()}
                x[position_attribute]=tuple([float(x[position_attribute].get(pos,0.)) for pos in vector_of_actions])
                #x[position_attribute]+=(float(len(mepsmeta_majorities[x[user_identifier_mep]]))-sum(x[position_attribute]),)
    return dataset,mepsmeta_majorities 


def compute_majorities_in_votes_dataset_onelayer(dataset,votesAttributes,usersAttributes,usersAggregationAttributes,position_attribute,verbose=False):
    mapping_user_vote={'for':'Y','against':'N','abstain':'A'}
    vote_identifier=str(votesAttributes[0])
    user_identifier_mep=str(usersAttributes[0])
    
    datasetToReturn=dataset[:]
    listsOfVotes={}
    listsOfVotesHasKey=listsOfVotes.has_key
    
    mepsmeta_majorities={}
    
    possibleUsersAggregationsAttr=[usersAggregationAttributes[i:] for i in range(len(usersAggregationAttributes))]
   
    
    for obj in dataset : 
        vote_id=str(obj[vote_identifier])
        if not (listsOfVotesHasKey(vote_id)) :
            listsOfVotes[vote_id]={}
        #listsOfVotes[vote_id].append(obj)
        
        
           
        user_identifier=tuple([obj[x] for x in usersAggregationAttributes])
        user_identifier_majority='majority'+'_'+'_'.join(user_identifier)
        
        if not mepsmeta_majorities.has_key(user_identifier_majority):
            mepsmeta_majorities[user_identifier_majority]=set()
        mepsmeta_majorities[user_identifier_majority]|={obj[user_identifier_mep]}
            
            
        if not listsOfVotes[vote_id].has_key(user_identifier_majority):
            listsOfVotes[vote_id][user_identifier_majority]=[]
        listsOfVotes[vote_id][user_identifier_majority].append(obj)
    
    
    for vote_id in listsOfVotes : 
        votes=listsOfVotes[vote_id]
        for user_identifier_majority in votes : 
            #user_identifier_majority='majority'+'_'+'_'.join(majority_user)
            votes_majority_user_splitted={}
            for item in votes[user_identifier_majority]:
                position_item=item[position_attribute]
                if not votes_majority_user_splitted.has_key(position_item):
                    votes_majority_user_splitted[position_item]=0
                votes_majority_user_splitted[position_item]+=1
            new_user_and_vote_entry={v_attr:item[v_attr] for v_attr in votesAttributes}
            new_user_and_vote_entry.update({u_attr:user_identifier_majority for u_attr in usersAttributes if u_attr <> 'MAJORITY'})
            new_user_and_vote_entry.update({u_attr:item[u_attr]for u_attr in usersAggregationAttributes})
            
            new_user_and_vote_entry.update({position_attribute:votes_majority_user_splitted}) #new vector
            new_user_and_vote_entry['MAJORITY']=True
            datasetToReturn.append(new_user_and_vote_entry)
            
    for x in datasetToReturn:
        x['MAJORITY']=x.get('MAJORITY',False)
        if not x['MAJORITY']:
            x[position_attribute]={x[position_attribute]:1.}
            x[position_attribute]={mapping_user_vote[k]:v for k,v in x[position_attribute].iteritems()}
            x[position_attribute]=tuple([float(x[position_attribute].get(pos,0.)) for pos in ('Y','N','A')])+(0.,)
            
            
        else :
            x[position_attribute]={mapping_user_vote[k]:v for k,v in x[position_attribute].iteritems()}
            x[position_attribute]=tuple([float(x[position_attribute].get(pos,0.)) for pos in ('Y','N','A')])
            x[position_attribute]+=(float(len(mepsmeta_majorities[x[user_identifier_mep]]))-sum(x[position_attribute]),)
    return datasetToReturn,mepsmeta_majorities 
        

def workflowStage_majorities_computer(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'majorities_computer',
        'inputs': {
            'dataset' :[]  
        },
        'configuration': {
           'votes_attributes':[], 
            'users_attributes':[], 
            'users_majorities_attributes':[], 
            'position_attribute':'U',
            'nb_aggregation_min':0,
            'method_aggregation_outcome':'STANDARD'
        },
        'outputs':{
            'dataset':[],
            'majorities':{}
        }
    }
    '''    
    
    dataset=inputs.get('dataset',[])
    
    votesAttributes=configuration.get('votes_attributes',[])
    usersAttributes=configuration.get('users_attributes',[])
    users_majorities_attributes=configuration.get('users_majorities_attributes',[])
    position_attribute=configuration.get('position_attribute','')
    nb_aggregation_min=configuration.get('nb_aggregation_min',0)
    vector_of_outcome=configuration.get('vector_of_outcome',None)
    
    method_aggregation_outcome=configuration.get('method_aggregation_outcome','VECTOR_VALUES')
    #print users_majorities_attributes
    returnedDataset,mepsmeta_majorities=compute_majorities_in_votes_dataset_multi_layers(dataset, votesAttributes, usersAttributes, users_majorities_attributes, position_attribute,nb_aggregation_min,vector_of_outcome,method_aggregation_outcome)
    
    outputs['dataset']=returnedDataset
    outputs['majorities']=mepsmeta_majorities
    return outputs
        
        
        

        
    