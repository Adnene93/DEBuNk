'''
Created on 3 mai 2017

@author: Adnene
'''


'''
Created on 3 mai 2017

@author: Adnene
'''

from random import randint


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


def findRandomMedoid(matrix, k) :
    medoids=[]
    length = len(matrix)

    i = 0
    while len(medoids) < k :
        randX = randint(1, length-1)

        if matrix[randX] not in medoids:
            medoids.append(matrix[randX])
        
    return medoids


def kMedoidCluster(dist_matrix,mapping_meps,inv_map_meps,meps_metadata, k):
    clusters = {}
    mapCluster = {}
    previousClusters = {}


    #mapmep list of ed-ipds, inv_map_meps contains all ep_ids with their position in the matrix
    #mapping_meps, inv_map_meps = createMapMeps(source)
    #matrix = distanceMatrix(source, mapping_meps) 
    length = len(dist_matrix)
    #Forming the clusters with identifiers being the index
    

    #clustering others according to centroids and their distance
    previousTotalDistance = 100000000000
    #looping while total cost is decreasing
    while True :
        medoids = findRandomMedoid(mapping_meps, k)
        index = 0
        while index < len(medoids):
            clusters[index]=([medoids[index]])
            mapCluster[medoids[index]] = index
            index+=1
        actualDistance = 0
        totalDistance = 0
        for index in mapping_meps :
            previousDistance = 100000000000
            indexX = 0

            for medoid in medoids :
                if(mapping_meps[index] not in medoids ):
                    actualDistance = dist_matrix[index][inv_map_meps[medoid]]
                    if(previousDistance > actualDistance) :
                        previousDistance = actualDistance
                        indexX=mapCluster[medoid]
    
            totalDistance += actualDistance

            if (mapping_meps[index] not in medoids): 
                clusters[indexX].append(mapping_meps[index])
        print(totalDistance)
        if(previousTotalDistance>totalDistance):
            previousTotalDistance = totalDistance
            previousClusters = clusters
        else :
            #if the previous distance is lesser the optimal cluster is previous cluster
            clusters = previousClusters
            break


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


def k_medoid_parliament(dataset,k): #K-medoid_PAM Partitioning Around Medoids (PAM)

    matrix,map_meps,inv_map_meps,meps_metadata = ComputeDistanceMatrix(dataset)
    clusters_dataset=kMedoidCluster(matrix,map_meps,inv_map_meps,meps_metadata,k)
    return sorted(clusters_dataset,key=lambda x : x['CLUSTER'])



def workflowStage_kmedoid_stage_nassim( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    '''
    {
    
        'id':'stage_id',
        'type':'kmedoid_stage_nassim',
        'inputs': {
            'dataset':[]
        },
        'configuration': {
            'nb_clusters':3
        },
        'outputs':{
            'dataset':[]
        }
    
    }
    '''
    
    localConfiguration={}
    localConfiguration['nb_clusters']=configuration.get('nb_clusters',3) 
    
    dataset=inputs['dataset']
    

    outputs['dataset']=k_medoid_parliament(dataset, localConfiguration['nb_clusters'])