'''
Created on 11 nov. 2016

@author: Adnene
'''

from math import sqrt

from measures.distanceMeasures import computeDistanceRajski
from measures.similaritiesMajorities import similarity_vector_measure


def computeSimpleSimilarity(mepsStats,mep1,mep2) :
    nb_pair_votes=float(mepsStats[mep1][mep2]['NB_VOTES'])    
    similarity= float(mepsStats[mep1][mep2]['++'])/nb_pair_votes if nb_pair_votes>0 else 0.
    return similarity


def computeSimilarityVectors(mepsStats,mep1,mep2) :
    similarity,nb_votes=similarity_vector_measure(mepsStats, mep1, mep2, 'MAAD')   
    if nb_votes>0:
        #similarity/=nb_votes if nb_votes>0 else 0.
        similarity/=nb_votes
    else :
        similarity=float('nan')
    return similarity



def computeSimilarityYY_NN(mepsStats,mep1,mep2) :
    similarity=1
    if (mep1==mep2):
        similarity=1
    else :
        
        similarity= float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN'])/float(mepsStats[mep1][mep2]['NB_VOTES'])
    return similarity

def computeSimilarityYY_NN_AA(mepsStats,mep1,mep2) :
#     similarity=1
#     if (mep1==mep2):
#         similarity=1
#     else :
    nb_pair_votes=float(mepsStats[mep1][mep2]['NB_VOTES'])
    
    similarity= float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN']+mepsStats[mep1][mep2]['AA'])/nb_pair_votes if nb_pair_votes>0 else 0.
    return similarity

def computeSimilarityStrict_YY_NN(mepsStats,mep1,mep2) :
    similarity=1
    if (mep1==mep2):
        similarity=1
    elif float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['YN']+mepsStats[mep1][mep2]['NY']+mepsStats[mep1][mep2]['NN'])>0 :
        similarity= float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN'])/float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['YN']+mepsStats[mep1][mep2]['NY']+mepsStats[mep1][mep2]['NN'])
    else :
        similarity=float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN'])/float(mepsStats[mep1][mep2]['NB_VOTES'])
    return similarity


def computeSimilarityRajski(mepsStats,mep1,mep2) :
    similarity = 1 - computeDistanceRajski(mepsStats,mep1,mep2)
    return similarity


