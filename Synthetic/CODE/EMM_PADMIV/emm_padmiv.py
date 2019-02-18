'''
Created on 6 mars 2017

@author: Adnene
'''
from math import log, sqrt
from time import time

from ENUMERATORS_ATTRIBUTES.enumerator_attribute_complex import enumerator_complex_cbo_init_new_config, \
    enumerator_complex_from_dataset_new_config
from filterer.filter import filter_pipeline_obj
from measures.qualityMeasure import quality_norm_eloignement, \
    quality_norm_rapprochement, quality_norm_eloignement_new, \
    compute_quality_and_upperbound
from measures.similaritiesMajorities import similarity_vector_measure
from votesExtractionAndProcessing.pairwiseStatistics import extractStatistics_fromdataset_vectors, \
    extractStatistics_fromdataset_new_update_not_square_vectors, \
    datasetStatistics



def cover(set1,set2):
    return float(len(set1&set2))/float(len(set2))

def ressemblance(set1,set2):
    return float(len(set1&set2))/float(min(len(set1),len(set2)))

def get_sim_vectors(stats,user1,user2,comparaison_measure='COS'):
    agreementProp,nb_votes=similarity_vector_measure(stats, user1, user2, comparaison_measure)   
    return agreementProp,nb_votes

def get_sim_min(stats,user1,user2,threshold_pair_comparaison=1):
    pairinfo=stats[user1][user2]
    pairinfovotes=pairinfo['**'].values()
    sim_min=0.+sum(sorted(pairinfovotes)[:int(threshold_pair_comparaison)])
    sim_min/=threshold_pair_comparaison
    return sim_min

# def get_sim(stats,user1,user1_votes,user2,user2_votes):
#     pairinfo=stats[user1][user2]
#     nb=pairinfo['NB_VOTES']
#     pairinfo_votes=pairinfo['**']
#     #pair_votes_keys=
#     return 0.+sum(pairinfo_votes[key] for key in user1_votes&user2_votes),nb

def compute_models(original_mepwise_similarities,pattern_mepsStatsNumbers,comparaison_measure='COS'):
    
    matrix_general=[];matrix_general_append=matrix_general.append
    matrix_pattern=[];matrix_pattern_append=matrix_pattern.append
    
    for user1 in pattern_mepsStatsNumbers:
        matrix_general_append([]);matrix_general_actual_row_append=matrix_general[-1].append
        matrix_pattern_append([]);matrix_pattern_actual_row_append=matrix_pattern[-1].append
        row_original_mepwise_sim=original_mepwise_similarities[user1]
        row_pattern_mepwise_sim=pattern_mepsStatsNumbers[user1]
        for user2 in row_pattern_mepwise_sim:
#                 pair_votes_user1_user2_pattern=row_pattern_mepwise_sim[user2]
#                 if pair_votes_user1_user2_pattern['FLAGCOMPUTED']:
#                     agg_p=0.+sum(pair_votes_user1_user2_pattern['**'].values())
#                     all_p=pair_votes_user1_user2_pattern['NB_VOTES']
#                 else:
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2,comparaison_measure)# if user2 not in matrix_pattern_map or user1 not in matrix_pattern_map[user2] else matrix_pattern_map[user1][user2]
                
                #sim_min_excpected=sum(pattern_mepsStatsNumbers[user1][user2]['**'][x] for x in keys_for_ub)
                #agg_p,all_p=get_sim(pattern_mepsStatsNumbers,user1,users_map_votes[user1],user2,users_map_votes[user2])
                
                agg_o,all_o=row_original_mepwise_sim[user2]
                matrix_general_actual_row_append((agg_o,all_o))
                matrix_pattern_actual_row_append((agg_p,all_p))
                #matrix_ub_actual_row_append(sim_min_excpected)
    return matrix_general,matrix_pattern



def compute_models_upperbounds(original_mepwise_similarities,pattern_mepsStatsNumbers,comparaison_measure='COS',threshold_pair_comparaison=1,ub_keys=set()):
    
    matrix_general=[];matrix_general_append=matrix_general.append
    matrix_pattern=[];matrix_pattern_append=matrix_pattern.append
    minsim_model=[];minsim_model_append=minsim_model.append

    for user1 in pattern_mepsStatsNumbers:
        matrix_general_append([]);matrix_general_actual_row_append=matrix_general[-1].append
        matrix_pattern_append([]);matrix_pattern_actual_row_append=matrix_pattern[-1].append
        minsim_model_append([]);minsim_model_actual_row_append=minsim_model[-1].append
        row_original_mepwise_sim=original_mepwise_similarities[user1]
        for user2 in pattern_mepsStatsNumbers[user1]:
                pair_user1_user2_votes=pattern_mepsStatsNumbers[user1][user2]['**'];pair_user1_user2_votes_get=pair_user1_user2_votes.get
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2,comparaison_measure)# if user2 not in matrix_pattern_map or user1 not in matrix_pattern_map[user2] else matrix_pattern_map[user1][user2]
                minsim_model_actual_row_append(sum(pair_user1_user2_votes_get(k,0.) for k in ub_keys)/float(threshold_pair_comparaison))
                agg_o,all_o=row_original_mepwise_sim[user2]
                matrix_general_actual_row_append((agg_o,all_o))
                matrix_pattern_actual_row_append((agg_p,all_p))
                
                
                
                
                #matrix_ub_actual_row_append(sim_min_excpected)
    #big_vector_votes_keyValueTuple=dict(sorted(filter(lambda tup: tup[0] in pair_user1_user2_votes_keys,big_vector_votes.iteritems()),key=lambda x : x[1])[:int(threshold_pair_comparaison)]).viewkeys()
    
    #minsim_model=[[sum(pattern_mepsStatsNumbers[user1][user2]['**'][k] for k in pattern_mepsStatsNumbers[user1][user2]['**'] if k in big_vector_votes_keyValueTuple) for user2 in pattern_mepsStatsNumbers[user1]] for user1 in pattern_mepsStatsNumbers]
    #print big_vector_votes_keyValueTuple[:15]
    return matrix_general,matrix_pattern,minsim_model

def compute_models_mapping(original_mepwise_similarities,pattern_mepsStatsNumbers,comparaison_measure='COS'):
    
    
    matrix_general=[];matrix_general_append=matrix_general.append
    matrix_pattern=[];matrix_pattern_append=matrix_pattern.append
    mapping_rows=[];mapping_rows_append=mapping_rows.append
    mapping_columns=[];mapping_columns_append=mapping_columns.append
    flag_mapping_columns=True
    
    for user1 in sorted(pattern_mepsStatsNumbers):
        matrix_general_append([]);matrix_general_actual_row_append=matrix_general[-1].append
        matrix_pattern_append([]);matrix_pattern_actual_row_append=matrix_pattern[-1].append
        mapping_rows_append(user1)
        row_original_mepwise_sim=original_mepwise_similarities[user1]
        for user2 in sorted(pattern_mepsStatsNumbers[user1]):
                if flag_mapping_columns:
                    mapping_columns_append(user2)
                agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2,comparaison_measure)# if user2 not in matrix_pattern_map or user1 not in matrix_pattern_map[user2] else matrix_pattern_map[user1][user2]
                
                #agg_p,all_p=get_sim(pattern_mepsStatsNumbers,user1,users_map_votes[user1],user2,users_map_votes[user2])
                agg_o,all_o=row_original_mepwise_sim[user2]
                matrix_general_actual_row_append((agg_o,all_o))
                matrix_pattern_actual_row_append((agg_p,all_p))
        flag_mapping_columns=False
    return matrix_general,matrix_pattern,mapping_rows,mapping_columns


def get_sub_model_filter_rows(general_model,pattern_model,mapping_rows,mapping_columns,set_users):
    
    new_general_model=[];new_general_model_append=new_general_model.append
    new_pattern_model=[];new_pattern_model_append=new_pattern_model.append
    new_mapping_row=[];new_mapping_row_append=new_mapping_row.append
    new_mapping_column=mapping_columns
    
    for i in range(len(general_model)):
        if mapping_rows[i] in set_users:
            new_general_model_append(general_model[i])
            new_pattern_model_append(pattern_model[i])
            new_mapping_row_append(mapping_rows[i])
    
    
    return new_general_model,new_pattern_model,new_mapping_row,new_mapping_column
    

def get_sub_model_filter_rows_column2(general_model,pattern_model,mapping_rows,mapping_columns,set_users1,set_users2):
    
    new_general_model=[];new_general_model_append=new_general_model.append
    new_pattern_model=[];new_pattern_model_append=new_pattern_model.append
    new_mapping_row=[];new_mapping_row_append=new_mapping_row.append
    new_mapping_column=[];new_mapping_column_append=new_mapping_column.append
    
    for i in range(len(general_model)):
        if mapping_rows[i] in set_users1:
            new_general_model_append([])
            new_pattern_model_append([])
            new_mapping_row_append(mapping_rows[i])
            for j in range(len(general_model[i])):
                if mapping_columns[j] in set_users2:
                    new_general_model[-1].append(general_model[i][j])
                    new_pattern_model[-1].append(pattern_model[i][j])
                    if mapping_columns[j] not in new_mapping_column:
                        new_mapping_column_append(mapping_columns[j])
    
    
    return new_general_model,new_pattern_model,new_mapping_row,new_mapping_column


# def compute_models_new(original_mepwise_similarities,pattern_mepsStatsNumbers,comparaison_measure='COS',threshold_pair_comparaison=1):
#     
#     matrix_general=[];matrix_general_append=matrix_general.append
#     matrix_pattern=[];matrix_pattern_append=matrix_pattern.append
#     
#     matrix_agg_min=[];matrix_agg_min_append=matrix_agg_min.append
#     #matrix_agg_max=[];matrix_agg_max_append=matrix_agg_max.append
#     
#     for user1 in pattern_mepsStatsNumbers:
#         matrix_general_append([]);matrix_general_actual_row_append=matrix_general[-1].append
#         matrix_pattern_append([]);matrix_pattern_actual_row_append=matrix_pattern[-1].append
#         matrix_agg_min_append([]);matrix_agg_min_actual_row_append=matrix_agg_min[-1].append
#         #matrix_agg_max_append([]);matrix_agg_max_actual_row_append=matrix_agg_max[-1].append
#         
#         row_original_mepwise_sim=original_mepwise_similarities[user1]
#         for user2 in pattern_mepsStatsNumbers[user1]:
#                 agg_p,all_p=get_sim_vectors(pattern_mepsStatsNumbers, user1, user2,comparaison_measure)# if user2 not in matrix_pattern_map or user1 not in matrix_pattern_map[user2] else matrix_pattern_map[user1][user2]
#                 
#                 #agg_p,all_p=get_sim(pattern_mepsStatsNumbers,user1,users_map_votes[user1],user2,users_map_votes[user2])
#                 agg_o,all_o=row_original_mepwise_sim[user2]
#                 matrix_general_actual_row_append((agg_o,all_o))
#                 matrix_pattern_actual_row_append((agg_p,all_p))
#                 matrix_agg_min_actual_row_append(get_sim_min(pattern_mepsStatsNumbers,user1,user2,threshold_pair_comparaison))
#     return matrix_general,matrix_pattern,matrix_agg_min

# def compute_quality(original_model,pattern_model,threshold_pair_comparaison,iwant,ret_ub_array=False):
#     if iwant=='disagreement': 
#         return quality_norm_eloignement(original_model,pattern_model,threshold_pair_comparaison,ret_ub_array)
#     else:
#         return quality_norm_rapprochement(original_model,pattern_model,threshold_pair_comparaison)
    #return coeff*res[0],coeff*res[1]




def get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes):
    
    vote_id_attributes=votes_attributes[0]
    users_id_attributes=users_attributes[0]
    votes_map_details={};users_map_details={};
    votes_map_details_has_key=votes_map_details.has_key;users_map_details_has_key=users_map_details.has_key
    votes_map_meps={};users_map_votes={}

    for d in dataset:
        
        d_vote_id=d[vote_id_attributes]
        d_user_id=d[users_id_attributes]
        
        if (not users_map_details_has_key(d_user_id)):
            users_map_details[d_user_id]={key:d[key] for key in users_attributes}
            users_map_votes[d_user_id]=set([])
        users_map_votes[d_user_id] |= {d_vote_id}
        
        if (not votes_map_details_has_key(d_vote_id)):
            votes_map_details[d_vote_id]={key:d[key] for key in votes_attributes}
            votes_map_meps[d_vote_id]=set()
        votes_map_meps[d_vote_id] |= {d_user_id}
        
    return votes_map_details,votes_map_meps,users_map_details,users_map_votes


def generic_enumerators_top_k_cbo(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    timing=0
    interesting_patterns=[]
    
    elementToShow='PROCEDURE_TITLE'
    
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0]
    users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    votes_map_details,votes_map_meps,users_map_details,users_map_votes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes)
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
    
    ########################DOSSIERS_PARTICULAR##########################
    
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    users_ids=set([obj[users_id_attribute] for obj in users_map_details_array])
    users1_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user1])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user2])
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    
    original_mepsStatistics,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    
    original_mepwise_similarities={}
    

    for user1 in original_mepsStatistics:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatistics[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatistics,user1,user2,comparaison_measure)

    
    
    
    enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, attributes, {'stats':original_mepsStatistics,'users':users_map_votes},True)
    #enumerator=enumerator_complex_from_dataset_new_config(votes_map_details_array, attributes, {'stats':original_mepsStatistics,'users':users_map_votes},objet_id_attribute=vote_id_attribute,verbose=True)
    
    
    
    index_to_test,index_valid,index_good=0,0,0
    for e_p,e_label,e_config in enumerator:
        
        e_stats=e_config['stats']
        e_votes=e_config['support']
        e_users=e_config['users']
        nb_votes=len(e_votes) 
        if nb_votes<=threshold_pair_comparaison :
            e_config['flag']=False
            if nb_votes<threshold_pair_comparaison:
                continue
        
        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            dossiers_ids |= {obj[elementToShow]}
        
        nb_dossiers=len(dossiers_ids)
         
        
        if nb_dossiers<=nb_dossiers_min:
            e_config['flag']=False
            if nb_dossiers<nb_dossiers_min:
                continue
        
        users_ids_set=set()
        max_votes_pairwise=0
        

        new_e_users={};all_votes=v_ids
        for key in e_users:
            value=e_users[key]
            votes_user=(value & v_ids)
            #all_votes&=votes_user
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                new_e_users[key]=votes_user
                users_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
        e_config['users']=new_e_users        

        if max_votes_pairwise<threshold_pair_comparaison :
            e_config['flag']=False
            continue
        
        index_to_test+=1
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set           
        
        st=time()
        returned_mepsStatistics,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(e_stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        timing += time()-st
        e_config['stats']=returned_mepsStatistics
        
        
        original_model,pattern_model=compute_models(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure)
       
        nb_users_voted=len(users1_ids)*len(users2_ids)
        quality,borne_max_quality=compute_quality_and_upperbound(original_model,pattern_model,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))
        
        
        if (pruning and borne_max_quality<quality_threshold):
            e_config['flag']=False
            continue
        
        #print e_p,'\t',quality,'\t',borne_max_quality,'\t',len(v_ids) # parent_vote,'\t',parent_mep,'\t',
        index_valid+=1
        
        if (quality>=quality_threshold):
            
            index_good+=1
            array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
            array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
            indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
            indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
            if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                if len(indices_to_remove_if_inserted)>0: 
                    interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]

                dataset_stats=datasetStatistics(returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                label=e_label
                
                dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                
                interesting_patterns.append([e_p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                if len(interesting_patterns)>top_k:
                    interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                    quality_threshold=interesting_patterns[-1][3]
            
            
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '------------------',index_to_test,index_valid,index_good,'...',timing,'-----------------------'
    
def generic_enumerators_top_k_cbo_OLD(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    timing=0
    interesting_patterns=[]
    
    elementToShow='PROCEDURE_TITLE'
    
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0]
    users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    votes_map_details,votes_map_meps,users_map_details,users_map_votes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes)
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    users_ids=set([obj[users_id_attribute] for obj in users_map_details_array])
    users1_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user1])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user2])
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    
    original_mepsStatistics,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    
    original_mepwise_similarities={}
    
    all_users_votes={}
    
    votes_to_pairs={}
    
    for user1 in original_mepsStatistics:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatistics[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatistics,user1,user2,comparaison_measure)
            pair_of_users_votes=original_mepsStatistics[user1][user2]['**']
            for key in pair_of_users_votes:
                
                all_users_votes[key]=all_users_votes.get(key,0.)+pair_of_users_votes[key]
                if not votes_to_pairs.has_key(key):
                    votes_to_pairs[key]={}
                if not votes_to_pairs[key].has_key(user1):
                    votes_to_pairs[key][user1]={}
                
                votes_to_pairs[key][user1][user2]=pair_of_users_votes[key]  
                    
                
    #print all_users_votes
    all_users_votes_items=sorted(all_users_votes.iteritems(),key=lambda x :x[1])
    mapping_all_users_votes=[all_users_votes_items[i][0] for i in range(len(all_users_votes_items))]
    
    
    enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, attributes, {'stats':original_mepsStatistics,'users':users_map_votes},True)
    
    #enumerator=enumerator_complex_from_dataset_new_config(votes_map_details_array, attributes, {'stats':original_mepsStatistics,'users':users_map_votes},objet_id_attribute=vote_id_attribute,verbose=True)
    
    
    
    index_to_test,index_valid,index_good=0,0,0
    for e_p,e_label,e_config in enumerator:
        
        e_stats=e_config['stats']
        e_votes=e_config['support']
        e_users=e_config['users']
        nb_votes=len(e_votes) 
        if nb_votes<=threshold_pair_comparaison :
            e_config['flag']=False
            if nb_votes<threshold_pair_comparaison:
                continue
        
        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            dossiers_ids |= {obj[elementToShow]}
        
        nb_dossiers=len(dossiers_ids)
         
        
        if nb_dossiers<=nb_dossiers_min:
            e_config['flag']=False
            if nb_dossiers<nb_dossiers_min:
                continue
        
        users_ids_set=set()
        max_votes_pairwise=0
        

        new_e_users={};all_votes=set(v_ids)
        for key in e_users:
            value=e_users[key]
            votes_user=(value & v_ids)
            all_votes&=votes_user
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                new_e_users[key]=votes_user
                
                users_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
        e_config['users']=new_e_users        
        
        
        
#         ub_keys=set();len_ub_keys=0;int_threshold_pair_comparaison=int(threshold_pair_comparaison)
#         for x in mapping_all_users_votes:
#             if x in all_votes:
#                 ub_keys|={x}
#                 len_ub_keys+=1
#                 if len_ub_keys>=int_threshold_pair_comparaison:
#                     break
#         ub_keys=set([x for x in mapping_all_users_votes if x in v_ids][:int(threshold_pair_comparaison)])
        
        
        #print UB_DICT
        if max_votes_pairwise<threshold_pair_comparaison :
            e_config['flag']=False
            continue
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set    
        
        
        
        
        index_to_test+=1
               
        
        
        #returned_mepsStatistics,returned_mepsMeta,ub_keys = extractStatistics_fromdataset_new_update_not_square_vectors(e_stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set,threshold_pair_comparaison)
        returned_mepsStatistics,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(e_stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set,threshold_pair_comparaison)
        e_config['stats']=returned_mepsStatistics
        
        st=time()
        all_users_votes={key:0.+sum(votes_to_pairs[key][u1][u2] for u1 in users1_ids_set for u2 in users2_ids_set if returned_mepsStatistics[u1][u2]['NB_VOTES']>=threshold_pair_comparaison) for key in all_votes}
        timing += time()-st
        all_users_votes_items=sorted(all_users_votes.iteritems(),key=lambda x :x[1])
        mapping_all_users_votes=[all_users_votes_items[i][0] for i in range(len(all_users_votes_items))][:int(threshold_pair_comparaison)]
        ub_keys=set(mapping_all_users_votes)
        
        
        
        original_model,pattern_model,minsim_model=compute_models_upperbounds(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure,threshold_pair_comparaison,ub_keys)
        #original_model,pattern_model=compute_models(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure)
        
        
        nb_users_voted=len(users1_ids)*len(users2_ids)
        quality,borne_max_quality=compute_quality_and_upperbound(original_model,pattern_model,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted),minsim_model=minsim_model)
        #quality,borne_max_quality=compute_quality_and_upperbound(original_model,pattern_model,threshold_pair_comparaison,iwant,coeff=lambda x : 1/float(nb_users_voted))
        
        
        #coeff=1/float(nb_users_voted)
        #quality,borne_max_quality=coeff*quality,coeff*borne_max_quality
        if (pruning and borne_max_quality<quality_threshold):
            e_config['flag']=False
            continue
        
        #print e_p,'\t',quality,'\t',borne_max_quality,'\t',len(v_ids) # parent_vote,'\t',parent_mep,'\t',
        index_valid+=1
        
        if (quality>=quality_threshold):
            indices_to_remove_if_inserted=[]
            indices_to_remove_quality=[]
            index_good+=1

            array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
            array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
            indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
            indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
            if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                if len(indices_to_remove_if_inserted)>0: 
                    interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]

                dataset_stats=datasetStatistics(returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                label=e_label
                
                dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                
                interesting_patterns.append([e_p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                if len(interesting_patterns)>top_k:
                    interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                    quality_threshold=interesting_patterns[-1][3]
            
            
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        #print dataset_stats
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
        
    print '------------------',index_to_test,index_valid,index_good,'...',timing,'-----------------------'
    
    
    
    
    
    
def generic_enumerators_top_k_cbo_users(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    timing=0
    interesting_patterns=[]
    elementToShow='movieTitle'
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0]
    users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    #subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    #subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    votes_map_details,votes_map_meps,users_map_details,users_map_votes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes)
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id]['DOSSIERID']:{'PROCEDURE_TITLE':votes_map_details[v_id]['PROCEDURE_TITLE']} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value['DOSSIERID']]['NB_VOTES']=dossiers_map_details[v_value['DOSSIERID']].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    users_ids=set([obj[users_id_attribute] for obj in users_map_details_array])
    users1_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user1])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user2])
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    
    original_mepsStatistics,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    
    original_mepwise_similarities={}
    for user1 in original_mepsStatistics:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatistics[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatistics,user1,user2,comparaison_measure)
    
    enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'stats':original_mepsStatistics,'users':users_map_votes},True)
    index_to_test,index_valid,index_good=0,0,0
    for e_p,e_label,e_config in enumerator:
        
        e_stats=e_config['stats']
        e_votes=e_config['support']
        e_users=e_config['users']
        nb_votes=len(e_votes) 
        if nb_votes<=threshold_pair_comparaison :
            e_config['flag']=False
            if nb_votes<threshold_pair_comparaison:
                continue
        
        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            dossiers_ids |= {obj['DOSSIERID']}
        
        nb_dossiers=len(dossiers_ids)
         
        
        if nb_dossiers<=nb_dossiers_min:
            e_config['flag']=False
            if nb_dossiers<nb_dossiers_min:
                continue
        
        users_ids_set=set()
        max_votes_pairwise=0
        

        new_e_users={}  
        for key in e_users:
            value=e_users[key]
            votes_user=(value & v_ids)
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                new_e_users[key]=votes_user
                users_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
        e_config['users']=new_e_users        
        
        
        if max_votes_pairwise<threshold_pair_comparaison :
            e_config['flag']=False
            continue
        
        index_to_test+=1
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set           
        
        
        returned_mepsStatistics,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(e_stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        e_config['stats']=returned_mepsStatistics
        st=time()
        #original_model,pattern_model,bound_model=compute_models_new(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure,threshold_pair_comparaison)
        original_model,pattern_model,mapping_rows,mapping_columns=compute_models_mapping(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure)
        timing += time()-st
        
        
        users_map_details_array_for_context = [row for row in users_map_details_array if row[users_id_attribute] in users1_ids_set]
        #print users_map_details_array_for_context
        
        for u_p,u_label,u_config in enumerator_complex_cbo_init_new_config(users_map_details_array_for_context, subattributes_details_users,{},False):
            if  u_p in e_config.get('FORBIDDEN',[]):
                u_config['flag']=False
                continue
            u_set_users=set(x[users_id_attribute] for x in u_config['support'])
            u_original_model,u_pattern_model,u_mapping_rows,u_mapping_columns=get_sub_model_filter_rows(original_model, pattern_model, mapping_rows, mapping_columns, u_set_users)
            
            e_u_p=e_p + u_p
            e_u_label=e_label + u_label
            
            u_returned_mepsStatistics={x:returned_mepsStatistics[x] for x in u_set_users}
            coeff=lambda nb_voter : (log(nb_voter+1,2)/log(len(users1_ids)+1,2))/float(len(users2_ids)+nb_voter)
            quality,borne_max_quality=compute_quality_and_upperbound(u_original_model,u_pattern_model,threshold_pair_comparaison,iwant,coeff)
            
            
            
            index_valid+=1
            
            if (pruning and borne_max_quality<quality_threshold):
                #e_config['flag']=False
                u_config['flag']=False
                if len(u_set_users)==len(users1_ids_set):
                    
                    e_config['flag']=False
                else :
                    e_config['FORBIDDEN']=e_config.get('FORBIDDEN',[])+[u_p]
                continue
            
            #print e_p,'\t',quality,'\t',borne_max_quality,'\t',len(v_ids) # parent_vote,'\t',parent_mep,'\t',
            
            
            if (quality>=quality_threshold):
                
                index_good+=1
                array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
                if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                    if len(indices_to_remove_if_inserted)>0: 
                        interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
                        
                    dataset_stats=datasetStatistics(u_returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                    label=e_u_label
                    
                    dossiers_voted=sorted([(dossiers_map_details[d]['PROCEDURE_TITLE'],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                    
                    interesting_patterns.append([e_u_p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                    if len(interesting_patterns)>top_k:
                        interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                        quality_threshold=interesting_patterns[-1][3]
            
            
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '------------------',index_to_test,index_valid,index_good,'...',timing,'-----------------------'
    
    
    
    
    
    
    
    
    
def generic_enumerators_top_k_cbo_users1_users2(dataset,attributes,configuration,user1_scope,user2_scope,votes_attributes,users_attributes,position_attribute):
    timing=0
    interesting_patterns=[]
    elementToShow='PROCEDURE_TITLE'
    top_k=configuration.get('top_k',float('inf')); top_k=float('inf') if top_k is None else top_k
    quality_threshold=float(configuration.get('quality_threshold',0)); quality_threshold=0 if quality_threshold is None else quality_threshold

    vote_id_attribute=votes_attributes[0]
    users_id_attribute=users_attributes[0]
    
    pruning = configuration.get('pruning',False)
    iwant=configuration['iwant']
    nb_dossiers_min=configuration['nb_dossiers_min']
    cover_threshold=configuration['cover_threshold']
    threshold_pair_comparaison=float(configuration['threshold_pair_comparaison'])
    comparaison_measure=configuration['comparaison_measure']
    
    #subpattern_votes_filter=[True if attr['name'] in votes_attributes else False for attr in attributes ]
    #subpattern_users_filter=[True if attr['name'] in users_attributes else False for attr in attributes ]
    
    subattributes_details_votes=[attr for attr in attributes if attr['name'] in votes_attributes]
    subattributes_details_users=[attr for attr in attributes if attr['name'] in users_attributes]
    
    votes_map_details,votes_map_meps,users_map_details,users_map_votes=get_votes_and_users_maps(dataset,attributes,votes_attributes,users_attributes)
    
    ########################DOSSIERS_PARTICULAR##########################
    dossiers_map_details={votes_map_details[v_id][elementToShow]:{elementToShow:votes_map_details[v_id][elementToShow]} for v_id in votes_map_details}
    for v_id,v_value in votes_map_details.iteritems():
        dossiers_map_details[v_value[elementToShow]]['NB_VOTES']=dossiers_map_details[v_value[elementToShow]].get('NB_VOTES',0)+1
        
    ########################DOSSIERS_PARTICULAR##########################
    
    votes_map_details_array=votes_map_details.values()    
    users_map_details_array=users_map_details.values()
    
    users_map_details_array_filtered_user1=filter_pipeline_obj(users_map_details_array, user1_scope)[0]
    users_map_details_array_filtered_user2=filter_pipeline_obj(users_map_details_array, user2_scope)[0]
    users_ids=set([obj[users_id_attribute] for obj in users_map_details_array])
     
    users1_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user1])
    users2_ids=set([p_attr[users_id_attribute] for p_attr in users_map_details_array_filtered_user2])
    
    u1_isequalto_u2=(users1_ids==users2_ids)
    #print u1_isequalto_u2
    
    nb_users_voted=len(users1_ids)+len(users2_ids)
    
    
    original_mepsStatistics,original_mepsMeta = extractStatistics_fromdataset_vectors(dataset,votes_attributes,users_attributes,position_attribute,user1_scope,user2_scope)
    
    original_mepwise_similarities={}
    for user1 in original_mepsStatistics:
        original_mepwise_similarities[user1]={}
        for user2 in original_mepsStatistics[user1]:
            original_mepwise_similarities[user1][user2]=get_sim_vectors(original_mepsStatistics,user1,user2,comparaison_measure)
    
    enumerator=enumerator_complex_cbo_init_new_config(votes_map_details_array, subattributes_details_votes, {'stats':original_mepsStatistics,'users':users_map_votes},True)
    index_to_test,index_valid,index_good=0,0,0
    for e_p,e_label,e_config in enumerator:
        
        e_stats=e_config['stats']
        e_votes=e_config['support']
        e_users=e_config['users']
        nb_votes=len(e_votes) 
        if nb_votes<=threshold_pair_comparaison :
            e_config['flag']=False
            if nb_votes<threshold_pair_comparaison:
                continue
        
        v_ids=set()
        dossiers_ids=set()
        
        for obj in e_votes:
            v_ids|={obj[vote_id_attribute]}
            dossiers_ids |= {obj[elementToShow]}
        
        nb_dossiers=len(dossiers_ids)
         
        
        if nb_dossiers<=nb_dossiers_min:
            e_config['flag']=False
            if nb_dossiers<nb_dossiers_min:
                continue
        
        users_ids_set=set()
        max_votes_pairwise=0
        

        new_e_users={}  
        for key in e_users:
            value=e_users[key]
            votes_user=(value & v_ids)
            len_votes_user=len(votes_user)
            if len_votes_user>=threshold_pair_comparaison:
                new_e_users[key]=votes_user
                users_ids_set|={key}
                max_votes_pairwise=len_votes_user if len_votes_user>max_votes_pairwise else max_votes_pairwise
        e_config['users']=new_e_users        
        
        
        if max_votes_pairwise<threshold_pair_comparaison :
            e_config['flag']=False
            continue
        
        index_to_test+=1
        users1_ids_set=users1_ids & users_ids_set
        users2_ids_set=users2_ids & users_ids_set           

        
        returned_mepsStatistics,returned_mepsMeta = extractStatistics_fromdataset_new_update_not_square_vectors(e_stats, original_mepsMeta, votes_attributes, users_attributes, position_attribute, v_ids, users_ids_set,users1_ids_set,users2_ids_set)
        e_config['stats']=returned_mepsStatistics
        
        #original_model,pattern_model,bound_model=compute_models_new(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure,threshold_pair_comparaison)
        original_model,pattern_model,mapping_rows,mapping_columns=compute_models_mapping(original_mepwise_similarities,returned_mepsStatistics,comparaison_measure)
        
        
        
        users1_map_details_array_for_context = [row for row in users_map_details_array if row[users_id_attribute] in users1_ids_set]
        
        
        #print users1_map_details_array_for_context
        
        for u1_p,u1_label,u1_config in enumerator_complex_cbo_init_new_config(users1_map_details_array_for_context, subattributes_details_users,{},False):
            if  u1_p in e_config.get('FORBIDDEN_U1',[]):
                u1_config['flag']=False
                continue
            u1_set_users=set(x[users_id_attribute] for x in u1_config['support'])
            #u_original_model,u_pattern_model,u_mapping_rows,u_mapping_columns=get_sub_model_filter_rows(original_model, pattern_model, mapping_rows, mapping_columns, u1_set_users)
            
            users2_map_details_array_for_context = [row for row in users_map_details_array if row[users_id_attribute] in (users2_ids_set - u1_set_users)]
            
            for u2_p,u2_label,u2_config in enumerator_complex_cbo_init_new_config(users2_map_details_array_for_context, subattributes_details_users,{},False):
                if u1_isequalto_u2:
                    e_config['FORBIDDEN_U1']=e_config.get('FORBIDDEN_U1',[])+[u2_p]
                if  (u1_p,u2_p) in e_config.get('FORBIDDEN_U2',[]):
                    u2_config['flag']=False
                    continue
                st=time()
                u2_set_users=set(x[users_id_attribute] for x in u2_config['support'])
                u2_original_model,u2_pattern_model,u2_mapping_rows,u2_mapping_columns=get_sub_model_filter_rows_column2(original_model, pattern_model, mapping_rows, mapping_columns, u1_set_users,u2_set_users)
            
                
#                 if u1_set_users==u2_set_users and len(u1_set_users)==1:
#                     print '--------------'
#                     print mapping_rows,mapping_
#                     print u2_original_model
#                     print u2_pattern_model
#                     print '--------------'
                e_u_p=e_p + u1_p + u2_p
                e_u_label=e_label + u1_label + u2_label
                
                #u_returned_mepsStatistics={x:returned_mepsStatistics[x] for x in u1_set_users}
                u_returned_mepsStatistics={x:{y: returned_mepsStatistics[x][y] for y in u2_set_users} for x in u1_set_users}
                #coeff=lambda nb_voter : (log(nb_voter+1,2)/log(len(users1_ids)+1,2))/float(len(users2_ids)+nb_voter)
                #(log(len(u2_set_users)+len(u1_set_users)+1,2)/log(len(users2_ids)+len(users1_ids),2))
                coeff=lambda nb_voter_1,nb_voter_2 : (log(nb_voter_2+nb_voter_1+1,2)/log(len(users2_ids)+len(users1_ids)+1,2))/float(nb_voter_2+nb_voter_1)
                
                quality,borne_max_quality=compute_quality_and_upperbound(u2_original_model,u2_pattern_model,threshold_pair_comparaison,iwant,coeff)
                
                
                
                index_valid+=1
                timing += time()-st
                if (pruning and borne_max_quality<quality_threshold):
                    #e_config['flag']=False
                    u2_config['flag']=False
                    if len(u2_set_users)==len(users2_ids_set):                        
                        u1_config['flag']=False
                        if len(u1_set_users)==len(users1_ids_set):
                            e_config['flag']=False
                        else :
                            e_config['FORBIDDEN_U1']=e_config.get('FORBIDDEN_U1',[])+[u1_p]
                    else :
                        e_config['FORBIDDEN_U2']=e_config.get('FORBIDDEN_U2',[])+[(u1_p,u2_p)]
                    continue
                
                #print e_p,'\t',quality,'\t',borne_max_quality,'\t',len(v_ids) # parent_vote,'\t',parent_mep,'\t',
                
                
                if (quality>=quality_threshold):
                    indices_to_remove_quality=[];indices_to_remove_if_inserted=[]
                    index_good+=1
                    if cover_threshold<=1:
                        array_covers=[];indices_to_remove_if_inserted=[];indices_to_remove_quality=[]
                        array_covers=[[ind,c_p,ressemblance(c_d_ids,v_ids),quality>c_quality] for (c_p,c_label,c_dataset_stats,c_quality,c_borne_max_quality,c_dossiers_voted,c_d_ids),ind in zip(interesting_patterns,range(len(interesting_patterns)))]
                        indices_to_remove_if_inserted=[x[0] for x in array_covers if x[2]>cover_threshold]
                        indices_to_remove_quality=[x[0] for x in array_covers if x[2]>cover_threshold and x[3]]
                    if len(indices_to_remove_quality)==len(indices_to_remove_if_inserted):
                        if len(indices_to_remove_if_inserted)>0: 
                            interesting_patterns = [interesting_patterns[i] for i in range(len(interesting_patterns)) if i not in indices_to_remove_if_inserted]
                            
                        dataset_stats=datasetStatistics(u_returned_mepsStatistics, returned_mepsMeta,votes_attributes,users_attributes,position_attribute)
                        label=e_u_label
                        
                        dossiers_voted=sorted([(dossiers_map_details[d][elementToShow],dossiers_map_details[d]['NB_VOTES']) for d in dossiers_ids],key = lambda x : x[1],reverse=True)
                        
                        interesting_patterns.append([e_u_p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,v_ids])
                        if len(interesting_patterns)>top_k:
                            interesting_patterns=sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True)[:top_k]
                            quality_threshold=interesting_patterns[-1][3]
            
            
    for p,label,dataset_stats,quality,borne_max_quality,dossiers_voted,d_ids in sorted(interesting_patterns,key=lambda p_attr : p_attr [3],reverse=True):
        yield p,label,dataset_stats,quality,borne_max_quality,dossiers_voted
    print '------------------',index_to_test,index_valid,index_good,'...',timing,'-----------------------'