'''
Created on 2 avr. 2017

@author: Adnene
'''
'''
Created on 26 janv. 2017

@author: Adnene
'''
from math import sqrt, copysign

from sortedcollections import ValueSortedDict


def similarity_vector_AP(stats,user1,user2): #Agreement proportion between MEPs 
    nb_pair_votes=float(stats[user1][user2]['NB_VOTES'])
    all_votes_of_pair=stats[user1][user2]['**']
    similarity=sum([(sum((x1*x2 for x1,x2 in zip(v1,v2)))) for (v1,v2) in all_votes_of_pair.values()])
    
    return similarity,nb_pair_votes


def similarity_vector_MAAD_POLARIZED(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes=0;similarity=0.;range3=range(0,3)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
#             ind_max_v1=0;max_v1=v1[0]
#             ind_max_v2=0;max_v2=v2[0]
#             maxus1=set();maxus2=set()
#             for i in range3:
#                 if v1[i]>max_v1:
#                     max_v1=v1[i]
#                     ind_max_v1=i
#                 if v2[i]>max_v2:
#                     max_v2=v2[i]
#                     ind_max_v2=i
#                                 
#             if ind_max_v1==ind_max_v2:
#                 similarity+=1 
                
            
            
            ind_max_v1=0;max_v1=v1[0]
            ind_max_v2=0;max_v2=v2[0]
            
            for i in range3:
                if v1[i]>max_v1:
                    max_v1=v1[i]
                    ind_max_v1=i
                if v2[i]>max_v2:
                    max_v2=v2[i]
                    ind_max_v2=i
            maxus1=set(x for x in range3 if v1[x]==max_v1);maxus2=set(x for x in range3 if v2[x]==max_v2)                    
            
            #if ind_max_v1==ind_max_v2:
            similarity+=float(len(maxus1 & maxus2))/float(len(maxus1 | maxus2))  
        except:
            continue

    return similarity,nbvotes

MAAD_DICT_VOTING_MAP_VALUES=[1,2,4]
MAAD_SIM_PATTERNS={
    1:{1:1.,2:0.,4:0.,3:0.5,5:0.5,6:0.,7:1/3.}, #vote 0
    
    2:{1:0.,2:1.,4:0.,3:0.5,5:0.,6:0.5,7:1/3.}, #vote 1
    
    3:{1:0.5,2:0.5,4:0.,3:1.,5:1/3.,6:1/3.,7:2/3.}, #vote 0+1
    
    4:{1:0.,2:0.,4:1.,3:0.,5:0.5,6:0.5,7:1/3.}, #vote 2
    
    5:{1:0.5,2:0.,4:0.5,3:1/3.,5:1.,6:1/3.,7:2/3.}, #vote 0+2
    
    6:{1:0.,2:0.5,4:0.5,3:1/3.,5:1/3.,6:1.,7:2/3.}, #vote 1+2
    
    7:{1:1/3.,2:1/3.,4:1/3.,3:2/3.,5:2/3.,6:2/3.,7:1.}  #vote 0+1+2
}



def similarity_vector_MAAD(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes=0;similarity=0.;range3=range(1,3)
    

    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            range3=range(1,len(v1))
            # print range3
            # raw_input('...')
            # print v1
            # print v2
            # raw_input('$$$$$$$$$$$')
            nbvotes+=1
            
            ind_max_v1=0;max_v1=v1[0]
            ind_max_v2=0;max_v2=v2[0]
            vote_pattern_1=1
            vote_pattern_2=1
            for i in range3:
                if v1[i]>max_v1:
                    max_v1=v1[i]
                    ind_max_v1=i
                    vote_pattern_1=MAAD_DICT_VOTING_MAP_VALUES[i]
                elif v1[i]==max_v1:
                    vote_pattern_1+=MAAD_DICT_VOTING_MAP_VALUES[i]

                if v2[i]>max_v2:
                    max_v2=v2[i]
                    ind_max_v2=i
                    vote_pattern_2=MAAD_DICT_VOTING_MAP_VALUES[i]
                elif v2[i]==max_v2:
                    vote_pattern_2+=MAAD_DICT_VOTING_MAP_VALUES[i]

            if vote_pattern_1==vote_pattern_2:
                similarity+=1.
            else:
                similarity+=MAAD_SIM_PATTERNS[vote_pattern_1][vote_pattern_2]
        except Exception as e:
            continue

    return similarity,nbvotes


def similarity_vector_COS(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2): #MMAP : Majority Mean Agreement Proportion
    
    nbvotes=0;similarity=0.;range3=range(0,3)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            scalar_product_v1_v2=0.
            norm_v1=0.
            norm_v2=0.
            for i in range3:
                scalar_product_v1_v2+=v1[i]*v2[i]
                norm_v1+=v1[i]**2
                norm_v2+=v2[i]**2
            scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
            similarity+=scalar_product_v1_v2
        except:
            continue

    return similarity,nbvotes


def similarity_vector_same_vote(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes=0.;similarity=0.
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1            
            if v1==v2:
                similarity+=1 
        except:
            continue

    return similarity,nbvotes


def similarity_vector_MAADABS(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes=0;similarity=0.;range4=range(0,4)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            ind_max_v1=0;max_v1=v1[0]
            ind_max_v2=0;max_v2=v2[0]
            for i in range4:
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

    return similarity,nbvotes


def similarity_vector_MAAD_AI(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes=0;similarity=0.;range3=range(0,3)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            # if user1<>user2:
                
            #     ind_max_v1=0;max_v1=v1[0]
            #     ind_max_v2=0;max_v2=v2[0]
            #     for i in range3:
            #         if v1[i]>max_v1:
            #             max_v1=v1[i]
            #             ind_max_v1=i
            #         if v2[i]>max_v2:
            #             max_v2=v2[i]
            #             ind_max_v2=i
                                    
            #     if ind_max_v1==ind_max_v2:
            #         similarity+=1
            # else :
                
            v12_norm=0.;max_v12=v1[0]+v2[0]
            for i in range3:
                v12_norm+= v1[i]+v2[i]
                if (v1[i]+v2[i])>max_v12:
                    max_v12=v1[i]+v2[i]
            max_v12/=float(v12_norm)
            similarity+=(3*max_v12-1)/2.
                
        except:
            continue

    return similarity,nbvotes

# def similarity_vector_MAAD_AI(stats,user1,user2):
#     pairinfo=stats[user1][user2]
#     nb_pair_votes=pairinfo['NB_VOTES']
#     all_votes_of_pair=pairinfo['**']
#     
#     similarity=0.
#     if user1<>user2:
#         for v1,v2 in all_votes_of_pair.values():
#             max_v1=max(v1[:3])
#             max_v2=max(v2[:3])
#             index_max_v1=v1.index(max_v1)
#             index_max_v2=v2.index(max_v2)
#             if index_max_v1==index_max_v2:
#                 similarity+=1
#     else:
#         range3=range(3)
#         for v1,v2 in all_votes_of_pair.values():
#             v1_norm_sum=float(sum(v1[index] for index in range3))
#             v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
#             similarity+=(3*max(v1_normalized)-1)/2.
#              
#             
#     return similarity,nb_pair_votes



def similarity_vector_MAAD_AI_MEMORY(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    
    similarity=0.
    if nb_pair_votes>0:
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                max_v1=max(v1[:3])
                max_v2=max(v2[:3])
                index_max_v1=v1.index(max_v1)
                index_max_v2=v2.index(max_v2)
                if index_max_v1==index_max_v2:
                    similarity+=1
                    all_votes_of_pair[key]=1
                else :
                    all_votes_of_pair[key]=0
        else:
            range3=range(3)
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                v1_norm_sum=float(sum(v1[index] for index in range3))
                v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
                similarity+=(3*max(v1_normalized)-1)/2.
                all_votes_of_pair[key]=(3*max(v1_normalized)-1)/2.
        
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes

def similarity_vector_MAAD_AIT(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    
    similarity=0.
    if user1<>user2:
        for v1,v2 in all_votes_of_pair.values():
            max_v1=max(v1[:3])
            max_v2=max(v2[:3])
            index_max_v1=v1.index(max_v1)
            index_max_v2=v2.index(max_v2)
            if index_max_v1==index_max_v2:
                similarity+=1
    else:
        range3=range(3)
        for v1,v2 in all_votes_of_pair.values():
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            v1_normalized_count_position=3-v1_normalized.count(0)
            if v1_normalized_count_position==2:
                similarity+=(2*max(v1_normalized)-1)
            else :
                similarity+=(3*max(v1_normalized)-1)/2.
    return similarity,nb_pair_votes


def similarity_vector_MAAD_AIT_MEMORY(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    
    similarity=0.
    if nb_pair_votes>0:
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                max_v1=max(v1[:3])
                max_v2=max(v2[:3])
                index_max_v1=v1.index(max_v1)
                index_max_v2=v2.index(max_v2)
                if index_max_v1==index_max_v2:
                    similarity+=1
                    all_votes_of_pair[key]=1
                else :
                    all_votes_of_pair[key]=0
        else:
            range3=range(3)
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                v1_norm_sum=float(sum(v1[index] for index in range3))
                v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
                v1_normalized_count_position=3-v1_normalized.count(0)
                if v1_normalized_count_position==2:
                    similarity+=(2*max(v1_normalized)-1)
                    all_votes_of_pair[key]=(2*max(v1_normalized)-1)
                else :
                    similarity+=(3*max(v1_normalized)-1)/2.
                    all_votes_of_pair[key]=(3*max(v1_normalized)-1)/2.
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes

def similarity_vector_MBZ(stats,user1,user2): #Mobilization
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    
    if user1<>user2:
        similarity=nb_pair_votes
    else:
        
        for v1,v2 in all_votes_of_pair.values():
            #print '--' +  str(v1)
            similarity+=1-(v1[3]/sum(v1))
        
        #print similarity,len(all_votes_of_pair),nb_pair_votes
    return similarity,nb_pair_votes


def similarity_vector_PARTICIPATION(stats,user1,user2): #Mobilization
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['ALL_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    
    if user1<>user2:
        similarity=nb_pair_votes
    else:
        
        for v1,v2 in all_votes_of_pair.values():
            similarity+=1-(v1[3]/sum(v1))
        
    
    return similarity,nb_pair_votes






def similarity_vector_MAAP(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    range3=(0,1,2)
    if nb_pair_votes>0 :
        for v1,v2 in all_votes_of_pair.values():
            scalar_product_v1_v2=0.
            v1_norm_sum=0.
            v2_norm_sum=0.
            for index in range3:
                v1_norm_sum+=v1[index]
                v2_norm_sum+=v2[index]
                scalar_product_v1_v2+=v1[index]*v2[index]
            scalar_product_v1_v2/=((v1_norm_sum*v2_norm_sum))
            similarity+=scalar_product_v1_v2
       
    return similarity,nb_pair_votes


def similarity_vector_MAAP_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    range3=(0,1,2)
    if nb_pair_votes>0 :
        for key in all_votes_of_pair:
            v1,v2=all_votes_of_pair[key]
            scalar_product_v1_v2=0.
            v1_norm_sum=0.
            v2_norm_sum=0.
            for index in range3:
                v1_norm_sum+=v1[index]
                v2_norm_sum+=v2[index]
                scalar_product_v1_v2+=v1[index]*v2[index]
            scalar_product_v1_v2/=((v1_norm_sum*v2_norm_sum))
            all_votes_of_pair[key]=scalar_product_v1_v2
            similarity+=scalar_product_v1_v2
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes




def similarity_vector_MAAP_1(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    range3=range(3)
    similarity=0.
    if user1<>user2:
        for v1,v2 in all_votes_of_pair.values():
            scalar_product_v1_v2=0.
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v2_norm_sum=float(sum(v2[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            v2_normalized=tuple(v2[index]/v2_norm_sum for index in range3)
            for index in range3:
                scalar_product_v1_v2+=v1_normalized[index]*v2_normalized[index]
            similarity+=scalar_product_v1_v2
    else :
        similarity=nb_pair_votes
    return similarity,nb_pair_votes


def similarity_vector_MAAP_1_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    range3=(0,1,2)
    if nb_pair_votes>0 :
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2=all_votes_of_pair[key]
                scalar_product_v1_v2=0.
                v1_norm_sum=0.
                v2_norm_sum=0.
                for index in range3:
                    v1_norm_sum+=v1[index]
                    v2_norm_sum+=v2[index]
                    scalar_product_v1_v2+=v1[index]*v2[index]
                scalar_product_v1_v2/=((v1_norm_sum*v2_norm_sum))
                all_votes_of_pair[key]=scalar_product_v1_v2
                similarity+=scalar_product_v1_v2
        else:
            for key in all_votes_of_pair:
                similarity+=1
                all_votes_of_pair[key]=1
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes


def similarity_vector_MAAP_AI(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    range3=range(3)
    similarity=0.
    if user1<>user2:
        for v1,v2 in all_votes_of_pair.values():
            scalar_product_v1_v2=0.
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v2_norm_sum=float(sum(v2[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            v2_normalized=tuple(v2[index]/v2_norm_sum for index in range3)
            for index in range3:
                scalar_product_v1_v2+=v1_normalized[index]*v2_normalized[index]
            similarity+=scalar_product_v1_v2
    else :
        for v1,v2 in all_votes_of_pair.values():
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            similarity+=(3*max(v1_normalized)-1)/2.
    return similarity,nb_pair_votes


def similarity_vector_MAAP_AI_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    range3=(0,1,2)
    if nb_pair_votes>0 :
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2=all_votes_of_pair[key]
                scalar_product_v1_v2=0.
                v1_norm_sum=0.
                v2_norm_sum=0.
                for index in range3:
                    v1_norm_sum+=v1[index]
                    v2_norm_sum+=v2[index]
                    scalar_product_v1_v2+=v1[index]*v2[index]
                scalar_product_v1_v2/=((v1_norm_sum*v2_norm_sum))
                all_votes_of_pair[key]=scalar_product_v1_v2
                similarity+=scalar_product_v1_v2
        else :
            range3=range(3)
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                v1_norm_sum=float(sum(v1[index] for index in range3))
                v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
                similarity+=(3*max(v1_normalized)-1)/2.
                all_votes_of_pair[key]=(3*max(v1_normalized)-1)/2.
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes


def similarity_vector_MAAP_AIT(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    range3=range(3)
    similarity=0.
    if user1<>user2:
        for v1,v2 in all_votes_of_pair.values():
            scalar_product_v1_v2=0.
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v2_norm_sum=float(sum(v2[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            v2_normalized=tuple(v2[index]/v2_norm_sum for index in range3)
            for index in range3:
                scalar_product_v1_v2+=v1_normalized[index]*v2_normalized[index]
            similarity+=scalar_product_v1_v2
    else :
        for v1,v2 in all_votes_of_pair.values():
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            v1_normalized_count_position=3-v1_normalized.count(0)
            if v1_normalized_count_position==2:
                similarity+=(2*max(v1_normalized)-1)
            else :
                similarity+=(3*max(v1_normalized)-1)/2.
    return similarity,nb_pair_votes



def similarity_vector_MAAP_AIT_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    range3=(0,1,2)
    if nb_pair_votes>0 :
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2=all_votes_of_pair[key]
                scalar_product_v1_v2=0.
                v1_norm_sum=0.
                v2_norm_sum=0.
                for index in range3:
                    v1_norm_sum+=v1[index]
                    v2_norm_sum+=v2[index]
                    scalar_product_v1_v2+=v1[index]*v2[index]
                scalar_product_v1_v2/=((v1_norm_sum*v2_norm_sum))
                all_votes_of_pair[key]=scalar_product_v1_v2
                similarity+=scalar_product_v1_v2
        else :
            range3=range(3)
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                v1_norm_sum=float(sum(v1[index] for index in range3))
                v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
                v1_normalized_count_position=3-v1_normalized.count(0)
                if v1_normalized_count_position==2:
                    similarity+=(2*max(v1_normalized)-1)
                    all_votes_of_pair[key]=(2*max(v1_normalized)-1)
                else :
                    similarity+=(3*max(v1_normalized)-1)/2.
                    all_votes_of_pair[key]=(3*max(v1_normalized)-1)/2.
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes




def similarity_vector_COS_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
     
    range3=range(3)
    similarity=0.
    
    if nb_pair_votes>0:
        for i in all_votes_of_pair:
            v1,v2=all_votes_of_pair[i]
            scalar_product_v1_v2=0.
            norm_v1=0.
            norm_v2=0.
            for index in range3:
                scalar_product_v1_v2+=v1[index]*v2[index]
                norm_v1+=v1[index]**2
                norm_v2+=v2[index]**2
            scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
            all_votes_of_pair[i]=scalar_product_v1_v2
            similarity+=scalar_product_v1_v2
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes


def similarity_vector_COS_AI(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    
    range3=range(3)
    similarity=0.
    if user1<>user2:
        for v1,v2 in all_votes_of_pair.values():
            scalar_product_v1_v2=0.
            norm_v1=0.
            norm_v2=0.
            for index in range3:
                scalar_product_v1_v2+=v1[index]*v2[index]
                norm_v1+=v1[index]**2
                norm_v2+=v2[index]**2
            scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
            similarity+=scalar_product_v1_v2
    else:
        for v1,v2 in all_votes_of_pair.values():
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            similarity+=(3*max(v1_normalized)-1)/2.
    
    return similarity,nb_pair_votes


def similarity_vector_COS_AI_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
     
    range3=range(3)
    similarity=0.
    
    if nb_pair_votes>0:
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2=all_votes_of_pair[key]
                scalar_product_v1_v2=0.
                norm_v1=0.
                norm_v2=0.
                for index in range3:
                    scalar_product_v1_v2+=v1[index]*v2[index]
                    norm_v1+=v1[index]**2
                    norm_v2+=v2[index]**2
                scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
                all_votes_of_pair[key]=scalar_product_v1_v2
                similarity+=scalar_product_v1_v2
        else :
            range3=range(3)
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                v1_norm_sum=float(sum(v1[index] for index in range3))
                v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
                similarity+=(3*max(v1_normalized)-1)/2.
                all_votes_of_pair[key]=(3*max(v1_normalized)-1)/2.
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes


def similarity_vector_COS_AIT(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    
    range3=range(3)
    similarity=0.
    if user1<>user2:
        for v1,v2 in all_votes_of_pair.values():
            scalar_product_v1_v2=0.
            norm_v1=0.
            norm_v2=0.
            for index in range3:
                scalar_product_v1_v2+=v1[index]*v2[index]
                norm_v1+=v1[index]**2
                norm_v2+=v2[index]**2
            scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
            similarity+=scalar_product_v1_v2
    else:
        for v1,v2 in all_votes_of_pair.values():
            v1_norm_sum=float(sum(v1[index] for index in range3))
            v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
            v1_normalized_count_position=3-v1_normalized.count(0)
            if v1_normalized_count_position==2:
                similarity+=(2*max(v1_normalized)-1)
            else :
                similarity+=(3*max(v1_normalized)-1)/2.
    
    return similarity,nb_pair_votes


def similarity_vector_COS_AIT_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
     
    range3=range(3)
    similarity=0.
    
    if nb_pair_votes>0:
        if user1<>user2:
            for key in all_votes_of_pair:
                v1,v2=all_votes_of_pair[key]
                scalar_product_v1_v2=0.
                norm_v1=0.
                norm_v2=0.
                for index in range3:
                    scalar_product_v1_v2+=v1[index]*v2[index]
                    norm_v1+=v1[index]**2
                    norm_v2+=v2[index]**2
                scalar_product_v1_v2/=(sqrt(norm_v1)*sqrt(norm_v2))
                all_votes_of_pair[key]=scalar_product_v1_v2
                similarity+=scalar_product_v1_v2
        else :
            range3=range(3)
            for key in all_votes_of_pair:
                v1,v2 = all_votes_of_pair[key]
                v1_norm_sum=float(sum(v1[index] for index in range3))
                v1_normalized=tuple(v1[index]/v1_norm_sum for index in range3)
                v1_normalized_count_position=3-v1_normalized.count(0)
                if v1_normalized_count_position==2:
                    similarity+=(2*max(v1_normalized)-1)
                    all_votes_of_pair[key]=(2*max(v1_normalized)-1)
                else :
                    similarity+=(3*max(v1_normalized)-1)/2.
                    all_votes_of_pair[key]=(3*max(v1_normalized)-1)/2.
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes

def similarity_vector_IIAI(stats,user1,user2):
    nb_pair_votes=float(stats[user1][user2]['NB_VOTES'])
    all_votes_of_pair=stats[user1][user2]['**'].values()
    similarity=sum([(3*sqrt(max((x1*x2 for x1,x2 in zip(v1,v2))))-1)/2. for (v1,v2) in all_votes_of_pair])
    return similarity,nb_pair_votes

def similarity_vector_IIAIT(stats,user1,user2):
    nb_pair_votes=float(stats[user1][user2]['NB_VOTES'])
    all_votes_of_pair=stats[user1][user2]['**'].values()
    similarity=sum([(3*sqrt(max((x1*x2 for x1,x2 in zip(v1,v2))))-1)/2. if len(v1)==3 or len(v2)==3 else 2*sqrt(max((x1*x2 for x1,x2 in zip(v1,v2))))-1 for (v1,v2) in all_votes_of_pair])
    return similarity,nb_pair_votes


def similarity_vector_ranking_simple_majority_MEMORY(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
     
    range5=range(5)
    similarity=0.
    
    if nb_pair_votes>0:
        for key in all_votes_of_pair:
            v1,v2 = all_votes_of_pair[key]
            if user1<>user2:
                print v1,v2
            max_v1=max(v1[:5])
            max_v2=max(v2[:5])
            index_max_v1=v1.index(max_v1)
            index_max_v2=v2.index(max_v2)
            if index_max_v1==index_max_v2:
                similarity+=1-copysign((index_max_v1-index_max_v2),1)/float(4)
            all_votes_of_pair[key]=1-copysign((index_max_v1-index_max_v2),1)/float(4)
            if user1<>user2:
                print all_votes_of_pair[key]
                raw_input('...')
        #pairinfo['**']=new_pair_info_votes
        pairinfo['FLAGCOMPUTED']=True
        
    return similarity,nb_pair_votes

def similarity_vector_ranking_averaging_majority(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    
    range5=range(5)
    similarity=0.;nbvotes=0
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            mark_avg_u1=0.;sum_avg_u1=0.
            mark_avg_u2=0.;sum_avg_u2=0.

            for i in range5:
                mark_avg_u1+=(i+1)*v1[i]
                mark_avg_u2+=(i+1)*v2[i]
                sum_avg_u1+=v1[i]
                sum_avg_u2+=v2[i]
            mark_avg_u1/=sum_avg_u1
            mark_avg_u2/=sum_avg_u2       
            similarity+=1-copysign((mark_avg_u1-mark_avg_u2),1)/float(4)
        except:
            continue
    
    return similarity,nbvotes


def similarity_vector_yelp_majority(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    
    similarity=0.;nbvotes=0
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            mark_avg_u1=v1[0]
            mark_avg_u2=v2[0]
      
            similarity+=1-copysign((mark_avg_u1-mark_avg_u2),1)/float(4)
        except:
            continue
    
    return similarity,nbvotes


def similarity_vector_presidential_majority(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    
    similarity=0.;nbvotes=0
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            mark_avg_u1=v1[0]
            mark_avg_u2=v2[0]
      
            similarity+=1-copysign((mark_avg_u1-mark_avg_u2),1)/float(4)
        except:
            continue
    
    return similarity,nbvotes

def similarity_vector_ranking_averaging_majority_binary(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    
    range5=range(5)
    similarity=0.;nbvotes=0
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key]
            nbvotes+=1
            mark_avg_u1=0.;sum_avg_u1=0.
            mark_avg_u2=0.;sum_avg_u2=0.

            for i in range5:
                mark_avg_u1+=(i+1)*v1[i]
                mark_avg_u2+=(i+1)*v2[i]
                sum_avg_u1+=v1[i]
                sum_avg_u2+=v2[i]
            mark_avg_u1/=sum_avg_u1
            mark_avg_u2/=sum_avg_u2
            if mark_avg_u1<2.5: mark_avg_u1=1.
            if 2.5<=mark_avg_u1<=3.5 : mark_avg_u1=3.
            if mark_avg_u1>3.5: mark_avg_u1=5.
            if mark_avg_u2<2.5: mark_avg_u2=1.
            if 2.5<=mark_avg_u2<=3.5 : mark_avg_u2=3.
            if mark_avg_u2>3.5: mark_avg_u2=5.
             
            similarity+=1-copysign((mark_avg_u1-mark_avg_u2),1)/float(4)
        except:
            continue
    
    return similarity,nbvotes



# def similarity_candidates(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    
#     similarity=0.;nbvotes=0;#range2=range(len(2))
#     bigv1=(0,0)
#     bigv2=(0,0)
#     for key in votes_ids:
#         try:
#             v1=user1_votes_outcome[key]
#             v2=user2_votes_outcome[key]
#             nbvotes+=1
#             bigv1=(bigv1[0]+v1[0],bigv1[1]+v1[1])
#             bigv2=(bigv2[0]+v2[0],bigv2[1]+v2[1])
#         except:
#             continue
    
# #     print '-------------------'
# #     print bigv1
# #     print bigv2
# #     
# #     print '-------------------'
#     #similarity=((bigv1[0]/float(bigv1[1]))-(bigv2[0]/float(bigv2[1]))) * nbvotes
    
#     try:
#         #similarity=(1-(copysign((bigv1[0]/float(bigv1[1]))-(bigv2[0]/float(bigv2[1])),1))) * nbvotes
#         similarity=(bigv1[0])/(bigv2[0]) * nbvotes# (bigv2[1]/bigv1[1])* nbvotes
#     except:
#         similarity=1.
#     return similarity,nbvotes


def similarity_candidates(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    similarity=0.;nbvotes=0;
    bigv1=(0,0)
    bigv2=(0,0)
    for key in votes_ids:
        try:
            v1=user1_votes_outcome[key]
            v2=user2_votes_outcome[key] 
            nbvotes+=1
            bigv1=(bigv1[0]+v1[0],bigv1[1]+v1[1])
            bigv2=(bigv2[0]+v2[0],bigv2[1]+v2[1])
        except:
            continue    
    try:
        similarity=(bigv1[0])/(bigv2[0]) * nbvotes
    except:
        similarity=1.
    return similarity,nbvotes


# def similarity_businesses_OLD(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
#     nbvotes_1=0
#     nbvotes_2=0
#     bigv1=(0,0)
#     bigv2=(0,0)
#     for key in votes_ids:
#         if key in user1_votes_outcome:
#             v1=user1_votes_outcome[key]
#             nbvotes_1+=1
#             #bigv1=(bigv1[0]+(v1[0]*v1[1]),bigv1[1]+v1[1])
#             bigv1=(bigv1[0]+(v1[0]),bigv1[1]+1)
#         if key in user2_votes_outcome:
#             v2=user2_votes_outcome[key]
#             nbvotes_2+=1
#             #bigv2=(bigv2[0]+(v2[0]*v2[1]),bigv2[1]+v2[1])
#             bigv2=(bigv2[0]+(v2[0]),bigv2[1]+1)
#         
#         try:
#             v1=user1_votes_outcome[key]
#             nbvotes_1+=1
#             #bigv1=(bigv1[0]+(v1[0]*v1[1]),bigv1[1]+v1[1])
#             bigv1=(bigv1[0]+(v1[0]),bigv1[1]+1)
#         except:
#             continue
#     
#     avg_mark_1=bigv1[0]/float(bigv1[1]) if nbvotes_1>0. else 0.
#     for key in votes_ids:
#         try:
#             v2=user2_votes_outcome[key]
#             nbvotes_2+=1
#             #bigv2=(bigv2[0]+(v2[0]*v2[1]),bigv2[1]+v2[1])
#             bigv2=(bigv2[0]+(v2[0]),bigv2[1]+1)
#         except:
#             continue
#     avg_mark_2=bigv2[0]/float(bigv2[1]) if nbvotes_2>0. else 0.
#     nbvotes=min(nbvotes_1,nbvotes_2) if nbvotes_1>0 and nbvotes_2>0 else 0
#     similarity=(1-copysign((avg_mark_1-avg_mark_2)/4.,1))*nbvotes
#     return similarity,nbvotes

def similarity_businesses(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2):
    nbvotes_1=0
    nbvotes_2=0
    bigv1=(0,0)
    bigv2=(0,0)
    
    
    
    for key in votes_ids:
        if key in user1_votes_outcome:
            v1=user1_votes_outcome[key]
            nbvotes_1+=1
            #bigv1=(bigv1[0]+(v1[0]*v1[1]),bigv1[1]+v1[1])
            bigv1=(bigv1[0]+(v1[0]),bigv1[1]+1)
        if key in user2_votes_outcome:
            v2=user2_votes_outcome[key]
            nbvotes_2+=1
            #bigv2=(bigv2[0]+(v2[0]*v2[1]),bigv2[1]+v2[1])
            bigv2=(bigv2[0]+(v2[0]),bigv2[1]+1)
        

    
    avg_mark_1=bigv1[0]/float(bigv1[1]) if nbvotes_1>0. else 0.
    avg_mark_2=bigv2[0]/float(bigv2[1]) if nbvotes_2>0. else 0.
    
    nbvotes=min(nbvotes_1,nbvotes_2) if nbvotes_1>0 and nbvotes_2>0 else 0
    similarity=(1-copysign((avg_mark_1-avg_mark_2)/4.,1))*nbvotes
    return similarity,nbvotes

SIMILARITIES_VECTORS_MAP={
    'AP':similarity_vector_AP,
    
    'MAAD':similarity_vector_MAAD,
    'MAAD_POLARIZED':similarity_vector_MAAD_POLARIZED,
    "COS":similarity_vector_COS,
    'MAAD_AI':similarity_vector_MAAD_AI,
    'similarity_candidates':similarity_candidates,
    'similarity_businesses':similarity_businesses,
#     'MAAD_AIT':similarity_vector_MAAD_AIT,
#     'MAADABS':similarity_vector_MAADABS,
#     
#     'MMAP':similarity_vector_MAAP,
#     'MMAP_1':similarity_vector_MAAP_1,
#     'MMAP_AI':similarity_vector_MAAP_AI,
#     'MMAP_AIT':similarity_vector_MAAP_AIT,
#     
#     'COS':similarity_vector_COS,
#     'COS_AI':similarity_vector_COS_AI,
#     'COS_AIT':similarity_vector_COS_AIT,
#     
#     'IIAI':similarity_vector_IIAI,
#     'IIAIT':similarity_vector_IIAIT,
#     
#     'MBZ':similarity_vector_MBZ,
#     'PRTC':similarity_vector_PARTICIPATION,
#    
    'AVG_RANKING_SIMPLE':similarity_vector_ranking_averaging_majority,
    'AVG_RANKING_BINARY':similarity_vector_ranking_averaging_majority_binary,
    'AVG_YELP':similarity_vector_yelp_majority,
    'SAME_VOTE':similarity_vector_same_vote

}





def similarity_vector_measure_dcs(votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2,method='COS'):
    similarity,nb_pair_votes=SIMILARITIES_VECTORS_MAP[method](votes_ids,user1_votes_outcome,user2_votes_outcome,user1,user2)

    return similarity,nb_pair_votes
    