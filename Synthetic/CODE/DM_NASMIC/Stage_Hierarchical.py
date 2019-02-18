'''
Created on 3 mai 2017

@author: Adnene
'''
def get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes,position_attribute,nb_items=None,nb_users=None):
    
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    votes_map_details={};users_map_details={};
    votes_map_details_has_key=votes_map_details.has_key;users_map_details_has_key=users_map_details.has_key
    votes_map_meps={};users_map_votes={}
    users_to_votes_outcomes={};users_to_votes_outcomes_has_key=users_to_votes_outcomes.has_key

    
    ##########################NEW#########################
    voting_keys=set()
    users_keys=set()
    if nb_items is not None and nb_users is not None:
        for d in dataset:        
            voting_keys|={d[vote_id_attributes]}
            users_keys|={d[users_id_attributes]}
        voting_keys=set(sorted(voting_keys)[nb_items:])
        users_keys=set(sorted(users_keys)[nb_users:])
    ##########################NEW#########################
    
    
    for d in dataset:
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if d_vote_id in voting_keys or d_user_id in users_keys:
            continue
        
        d_outcome=d[position_attribute]
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=set()
        votes_map_meps[d_vote_id] |= {d_user_id}
        
        if (not users_to_votes_outcomes_has_key(d_user_id)):
            users_to_votes_outcomes[d_user_id]={}
        users_to_votes_outcomes[d_user_id][d_vote_id]=d_outcome
            
            
        
        
    return votes_map_details,votes_map_meps,users_map_details,users_map_votes,users_to_votes_outcomes


def similarity_vector_MAAD(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes=0;similarity=0.;range3=range(0,3)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            ind_max_v1=0;max_v1=v1[0]
            ind_max_v2=0;max_v2=v2[0]
            for i in range3:
                if v1[i]>max_v1:
                    max_v1=v1[i]
                    ind_max_v1=i
                if v2[i]>max_v2:
                    max_v2=v2[i]
                    ind_max_v2=i
                                
            if ind_max_v1==ind_max_v2:
                similarity+=1 
        except:
            continue

    return similarity/ float(nbvotes)


def compute_similarity_matrix(users1_to_votes_outcomes,users2_to_votes_outcomes,votes_ids,users1_ids,users2_ids,issquare=False):
    similarity_matrix={}
    #issquare=users1_ids==users2_ids
    for user1 in users1_ids:
        similarity_matrix[user1]={}
        for user2 in users2_ids:
            if issquare :
                if user2<=user1:
                    similarity_matrix[user1][user2]=similarity_vector_MAAD(votes_ids,users1_to_votes_outcomes[user1],users2_to_votes_outcomes[user2],user1,user2)
            else :
                similarity_matrix[user1][user2]=similarity_vector_MAAD(votes_ids,users1_to_votes_outcomes[user1],users2_to_votes_outcomes[user2],user1,user2)
            
    if issquare:
        for user1 in users1_ids:
            for user2 in users2_ids:
                if user2<user1:
                    similarity_matrix[user2][user1]=similarity_matrix[user1][user2]
    return similarity_matrix



def ComputeDistanceMatrix(dataset):
    votes_map_details,votes_map_meps,all_users_map_details,all_users_map_votes,all_users_to_votes_outcomes=get_votes_and_users_maps(dataset,[],["VOTEID","PROCEDURE_TITLE","VOTE_DATE","VOTE_DATE_DETAILED","PROCEDURE_SUBJECT","DOSSIERID","PROCEDURE_SUBTYPE","COMMITTEE","PROCEDURE_TYPE"],["EP_ID","NAME_FULL","NATIONAL_PARTY","GROUPE_ID","COUNTRY","AGEGROUP","GENDER","AGE"],"USER_VOTE")
    similarity_matrix=compute_similarity_matrix(all_users_to_votes_outcomes,all_users_to_votes_outcomes,votes_map_details.viewkeys(),sorted(all_users_to_votes_outcomes.viewkeys()),sorted(all_users_to_votes_outcomes.viewkeys()),True)

    distance_matrix={}

    for k1 in similarity_matrix:
        distance_matrix[k1]={}
        for k2 in similarity_matrix[k1]:
            distance_matrix[k1][k2]=1-similarity_matrix[k1][k2]


    map_meps=sorted(distance_matrix.viewkeys())

    simple_distance_matrix=[]

    for k1 in map_meps:
        simple_distance_matrix.append([])
        for k2 in map_meps:
            simple_distance_matrix[-1].append(distance_matrix[k1][k2])

    map_meps= {i:map_meps[i] for i in range(len(map_meps))}
    inv_map_meps= {v:k for k,v in map_meps.iteritems()}
    return simple_distance_matrix,map_meps,inv_map_meps,all_users_map_details

def clustersLinkage(dMatrix,linkage,cluster1,cluster2,map_meps_inverse):
    a = -1
    b = -1

    if linkage == 'single':
        value = 1
    elif linkage == 'complete':
        value = 0
    elif linkage == 'average':
        value = 0

    for id1 in cluster1:
        for id2 in cluster2:
            x = map_meps_inverse[id1]
            y = map_meps_inverse[id2]
            if linkage == 'single':
                if dMatrix[x][y] < value:
                    value = dMatrix[x][y]
                    a = x
                    b = y
            elif linkage == 'complete':
                if dMatrix[x][y] > value:
                    value = dMatrix[x][y]
                    a = x
                    b = y
            elif linkage == 'average':
                value = value + dMatrix[x][y]

    if linkage == 'average':
        l1 = len(cluster1)
        l2 = len(cluster2)
        value = value / (l1*l2)

    return value,a,b

def computeLinkageOnMatrix(dMatrix,linkage,map_clusters,map_meps_inverse):
    value = 1
    a = -1
    b = -1

    length = len(map_clusters)
    for i in range(0,length-1):
        for j in range(i+1,length):
            val,x,y = clustersLinkage(dMatrix,linkage,map_clusters[i],map_clusters[j],map_meps_inverse)
            if val < value:
                    value = val
                    a = i
                    b = j
        
    #print(value)
    return value,a,b

def initclusters(map_meps): # Return => {0: ['97137'], 1: ['124748'],...}
    map_clusters = {}
    for key in map_meps:
        map_clusters[key] = [map_meps[key]]
    
    return map_clusters

def updateMapClusters(map_clusters,new_cluster):
    new_map = {}
    n = 0
    for key in map_clusters:
        new_map[n] = map_clusters[key]
        n = n + 1

    new_map[n] = new_cluster
    #print(new_map)
    return new_map

def hierarchicalClustering(dMatrix,linkage,map_meps,map_meps_inverse,meps_metadata,distance):
    map_clusters = initclusters(map_meps)
    length_map_clusters = len(map_clusters)
    
    while length_map_clusters > 1:
        value,x,y = computeLinkageOnMatrix(dMatrix,linkage,map_clusters,map_meps_inverse)
        if value < distance:
            result = map_clusters.copy()
            
        new_cluster = map_clusters[x] + map_clusters[y]
        #print(new_cluster)
        del map_clusters[x]
        del map_clusters[y]
        map_clusters = updateMapClusters(map_clusters,new_cluster)
        length_map_clusters = len(map_clusters)
        #print('------------------------------------------------------------------------------\n')

    clusters=result
    clusters_inv={}
    for cl in clusters:
        for mep in clusters[cl]:
            clusters_inv[mep]=cl
    users_map_details_clustering={}

    for m in meps_metadata:
        new_m = {key:v for key,v in meps_metadata[m].iteritems()}
        new_m['CLUSTER']=clusters_inv[m]
        users_map_details_clustering[m]=new_m
    clusters_dataset=users_map_details_clustering.values()
    return clusters_dataset

def generateDataset(clusters,dataset):
    result = []
    n = 1
    
    for key in clusters:
        for ep_id in clusters[key]:
            i = 1
            for line in dataset:
                content = line[i]
                if content['EP_ID'] == ep_id:
                    value = line[i]
                    obj = {}
                    obj['EP_ID'] = content['EP_ID']
                    obj['NAME_FULL'] = content['NAME_FULL']
                    obj['GENDER'] = content['GENDER']
                    obj['AGE'] = content['AGE']
                    obj['NATIONAL_PARTY'] = content['NATIONAL_PARTY']
                    obj['GROUPE_ID'] = content['GROUPE_ID']
                    obj['COUNTRY'] = content['COUNTRY']
                    obj['NUM_CLUSTER'] = key

                    result.append({n:obj})
                    n = n+1
                    break
            
                i = i+1
    
    return result


def hierarchical_parliament(dataset,linkage,distance): #Hierarchical Clustering _ All usual linkages

    matrix,map_meps,inv_map_meps,meps_metadata = ComputeDistanceMatrix(dataset)
    clusters_dataset=hierarchicalClustering(matrix,linkage,map_meps,inv_map_meps,meps_metadata,distance)
    #sorted()
    return sorted(clusters_dataset,key=lambda x : x['CLUSTER'])


def workflowStage_hierarchical_stage_michel( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'hierarchical_stage_michel',
        'inputs': {
            'dataset':[]
        },
        'configuration': {
            'threshold_distance':0.4,
            'linkage': single | average | complete
        },
        'outputs':{
            'dataset':[]
        }
    
    }
    '''
    
    results=[]
    header=[]
    localConfiguration={}
    localConfiguration['threshold_distance']=configuration.get('threshold_distance',0.3) 
    localConfiguration['linkage']=configuration.get('linkage','average') 
    
    dataset=inputs['dataset']
    

    outputs['dataset']=hierarchical_parliament(dataset, localConfiguration['linkage'], localConfiguration['threshold_distance'])