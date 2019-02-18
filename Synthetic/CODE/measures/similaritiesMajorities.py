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

def similarity_vector_MAAD(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    for v1,v2 in all_votes_of_pair.values():
        max_v1=max(v1[:3])
        max_v2=max(v2[:3])
        index_max_v1=v1.index(max_v1)
        index_max_v2=v2.index(max_v2)
        if index_max_v1==index_max_v2:
            similarity+=1

    return similarity,nb_pair_votes


def similarity_vector_MAAD_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    #new_pair_info_votes=ValueSortedDict()
    if nb_pair_votes>0:
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
        #pairinfo['**']=new_pair_info_votes
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes

def similarity_vector_MAADABS(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    for v1,v2 in all_votes_of_pair.values():
        max_v1=max(v1)
        max_v2=max(v2)
        index_max_v1=v1.index(max_v1)
        index_max_v2=v2.index(max_v2)
        if index_max_v1==index_max_v2:
            similarity+=1

    return similarity,nb_pair_votes

def similarity_vector_MAADABS_MEMORY(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    similarity=0.
    if nb_pair_votes>0:
        for key in all_votes_of_pair:
            v1,v2 = all_votes_of_pair[key]
            max_v1=max(v1)
            max_v2=max(v2)
            index_max_v1=v1.index(max_v1)
            index_max_v2=v2.index(max_v2)
            if index_max_v1==index_max_v2:
                similarity+=1
                all_votes_of_pair[key]=1
            else :
                all_votes_of_pair[key]=0
        pairinfo['FLAGCOMPUTED']=True
    return similarity,nb_pair_votes


def similarity_vector_MAAD_AI(stats,user1,user2):
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
            similarity+=(3*max(v1_normalized)-1)/2.
             
            
    return similarity,nb_pair_votes



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

def similarity_vector_COS(stats,user1,user2): #MMAP : Majority Mean Agreement Proportion
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
     
    range3=range(3)
    similarity=0.
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
        similarity+=scalar_product_v1_v2
        
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

def similarity_vector_ranking_averaging_majority_MEMORY(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
     
    range5=range(5)
    similarity=0.
    
    if nb_pair_votes>0:
        for key in all_votes_of_pair:
            v1,v2 = all_votes_of_pair[key]

            mark_avg_u1=0.
            mark_avg_u2=0.
            
            for i in range5:
                mark_avg_u1+=(i+1)*v1[i]
                mark_avg_u2+=(i+1)*v2[i]
            mark_avg_u1/=sum(v1[:5])
            mark_avg_u2/=sum(v2[:5])
            similarity+=1-copysign((mark_avg_u1-mark_avg_u2),1)/float(4)
            all_votes_of_pair[key]=1-copysign((mark_avg_u1-mark_avg_u2),1)/float(4)
        pairinfo['FLAGCOMPUTED']=True
        
    return similarity,nb_pair_votes


SIMILARITIES_VECTORS_MAP={
    'AP':similarity_vector_AP,
    
    'MAAD':similarity_vector_MAAD_MEMORY,
    'MAAD_AI':similarity_vector_MAAD_AI_MEMORY,
    'MAAD_AIT':similarity_vector_MAAD_AIT_MEMORY,
    'MAADABS':similarity_vector_MAADABS_MEMORY,
    
    'MMAP':similarity_vector_MAAP_MEMORY,
    'MMAP_1':similarity_vector_MAAP_1_MEMORY,
    'MMAP_AI':similarity_vector_MAAP_AI_MEMORY,
    'MMAP_AIT':similarity_vector_MAAP_AIT_MEMORY,
    
    'COS':similarity_vector_COS_MEMORY,
    'COS_AI':similarity_vector_COS_AI_MEMORY,
    'COS_AIT':similarity_vector_COS_AIT_MEMORY,
    
    'IIAI':similarity_vector_IIAI,
    'IIAIT':similarity_vector_IIAIT,
    
    'MBZ':similarity_vector_MBZ,
    'PRTC':similarity_vector_PARTICIPATION,
    
    'MAAD_RANKING_SIMPLE':similarity_vector_ranking_averaging_majority_MEMORY
}


def default_similarity_FLAGCOMPUTED(stats,user1,user2):
    pairinfo=stats[user1][user2]
    nb_pair_votes=pairinfo['NB_VOTES']
    all_votes_of_pair=pairinfo['**']
    #all_votes_of_pair_values=sorted(all_votes_of_pair.values())
    #print all_votes_of_pair.values()
    similarity=0.+sum(all_votes_of_pair.values())
    return similarity,nb_pair_votes


def similarity_vector_measure(stats,user1,user2,method='COS'):
    if stats[user1][user2]['FLAGCOMPUTED']:
        similarity,nb_pair_votes=default_similarity_FLAGCOMPUTED(stats,user1,user2)
    else :
        similarity,nb_pair_votes=SIMILARITIES_VECTORS_MAP[method](stats,user1,user2)
    return similarity,nb_pair_votes


def similarity_vector_measure_dcs(stats,user1,user2,method='COS'):
    similarity,nb_pair_votes=SIMILARITIES_VECTORS_MAP[method](stats,user1,user2)
    return similarity,nb_pair_votes
    