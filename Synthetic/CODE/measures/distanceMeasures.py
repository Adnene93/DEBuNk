'''
Created on 11 nov. 2016

@author: Adnene
'''

from math import log, sqrt
import math

from measures.similaritiesMajorities import similarity_vector_measure


def computeSimpleDistance(mepsStats,mep1,mep2) :
    nb_pair_votes=float(mepsStats[mep1][mep2]['NB_VOTES'])  
    distance= 1- (float(mepsStats[mep1][mep2]['++'])/nb_pair_votes) if nb_pair_votes>0 else 1.
    return distance



def computeDistanceVectors(mepsStats,mep1,mep2) :
    similarity,nb_votes=similarity_vector_measure(mepsStats, mep1, mep2, 'COS')   
    if nb_votes>0:
        #similarity/=nb_votes if nb_votes>0 else 0.
        similarity/=nb_votes
    else :
        similarity=float('nan')
    distance=1-similarity
    return distance

def computeDistanceYY_NN(mepsStats,mep1,mep2) :
    
    distance=0
    if (mep1==mep2):
        distance=0
    else :
        distance=1-float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN'])/float(mepsStats[mep1][mep2]['NB_VOTES'])
    return distance



def computeDistanceYY_NN_AA(mepsStats,mep1,mep2) :  
    
#     distance=0
#     if (mep1==mep2):
#         distance=0
#     else :
    
    nb_pair_votes=float(mepsStats[mep1][mep2]['NB_VOTES'])
    distance=1-float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN']+mepsStats[mep1][mep2]['AA'])/nb_pair_votes if nb_pair_votes>0 else 1.
    
    return distance


def computeDistanceStrict_YY_NN(mepsStats,mep1,mep2):
    distance=0
    if (mep1==mep2):
        distance=0
    elif float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['YN']+mepsStats[mep1][mep2]['NY']+mepsStats[mep1][mep2]['NN'])>0:
        distance=1-float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN'])/float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['YN']+mepsStats[mep1][mep2]['NY']+mepsStats[mep1][mep2]['NN'])
    else :
        distance=1-float(mepsStats[mep1][mep2]['YY']+mepsStats[mep1][mep2]['NN'])/float(mepsStats[mep1][mep2]['NB_VOTES'])
    return distance

def computeDistanceRajski(mepsStats,mep1,mep2) :  
    entryIntersect = mepsStats[mep1][mep2]
    
    PXYarrOcc=[entryIntersect['YY'],entryIntersect['YN'],entryIntersect['YA'],entryIntersect['NY'],entryIntersect['NN'],entryIntersect['NA'],entryIntersect['AY'],entryIntersect['AN'],entryIntersect['AA']]
    PXYarr=[(float(v)/float(entryIntersect['NB_VOTES'])) for v in PXYarrOcc]
    
    #PYXarr=[PXYarr[0],PXYarr[3],PXYarr[6],PXYarr[1],PXYarr[4],PXYarr[7],PXYarr[2],PXYarr[5],PXYarr[8]]
    PYXarrOcc=[entryIntersect['YY'],entryIntersect['NY'],entryIntersect['AY'],entryIntersect['YN'],entryIntersect['NN'],entryIntersect['AN'],entryIntersect['YA'],entryIntersect['NA'],entryIntersect['AA']]
    PYXarr=[(float(v)/float(entryIntersect['NB_VOTES'])) for v in PYXarrOcc]
    
    
    HXY = (-1)*sum([ float(v)*log(float(v),2) if (v>0) else 0  for v in PXYarr])
    
    #HXY = (-1)*sum([ float(v) if (v>0) else 0  for v in PXYarr])
    PXarrOcc=[float(entryIntersect['YY'])+float(entryIntersect['YN'])+float(entryIntersect['YA']),
           float(entryIntersect['NN'])+float(entryIntersect['NY'])+float(entryIntersect['NA']),
           float(entryIntersect['AA'])+float(entryIntersect['AY'])+float(entryIntersect['AN'])]
    PXarr=[float(v)/float(entryIntersect['NB_VOTES']) for v in PXarrOcc]
    PYarr=[float(entryIntersect['YY'])+float(entryIntersect['NY'])+float(entryIntersect['AY']),
           float(entryIntersect['NN'])+float(entryIntersect['YN'])+float(entryIntersect['AN']),
           float(entryIntersect['NA'])+float(entryIntersect['YA'])+float(entryIntersect['AA'])]
    PYarr=[float(v)/float(entryIntersect['NB_VOTES']) for v in PYarr]
    
    PXgivenY_Yae=[float(v1)/float(v2) if v2>0 else 0 for v1,v2 in zip(PYXarr[0:3],[PYarr[0],PYarr[0],PYarr[0]])]
    PXgivenY_Nay=[float(v1)/float(v2) if v2>0 else 0 for v1,v2 in zip(PYXarr[3:6],[PYarr[1],PYarr[1],PYarr[1]])]
    PXgivenY_Abstain=[float(v1)/float(v2) if v2>0 else 0 for v1,v2 in zip(PYXarr[6:9],[PYarr[2],PYarr[2],PYarr[2]])]
    
    PXgivenYarr=PXgivenY_Yae+PXgivenY_Nay+PXgivenY_Abstain
    
    
    PYgivenX_Yae=[float(v1)/float(v2) if v2>0 else 0 for v1,v2 in zip(PXYarr[0:3],[PXarr[0],PXarr[0],PXarr[0]])]
    PYgivenX_Nay=[float(v1)/float(v2) if v2>0 else 0 for v1,v2 in zip(PXYarr[3:6],[PXarr[1],PXarr[1],PXarr[1]])]
    PYgivenX_Abstain=[float(v1)/float(v2) if v2>0 else 0 for v1,v2 in zip(PXYarr[6:9],[PXarr[2],PXarr[2],PXarr[2]])]

    PYgivenXarr=PYgivenX_Yae+PYgivenX_Nay+PYgivenX_Abstain

    PXarr=[PXarr[0]]+[PXarr[0]]+[PXarr[0]]+[PXarr[1]]+[PXarr[1]]+[PXarr[1]]+[PXarr[2]]+[PXarr[2]]+[PXarr[2]]
    PYarr=[PYarr[0]]+[PYarr[0]]+[PYarr[0]]+[PYarr[1]]+[PYarr[1]]+[PYarr[1]]+[PYarr[2]]+[PYarr[2]]+[PYarr[2]]
    
    #HX=(-1)*sum([ float(v)*log(float(v),2) if (v>0) else 0  for v in PXarr]) 
    #HY=(-1)*sum([ float(v)*log(float(v),2) if (v>0) else 0  for v in PYarr])

    HXgivenY=  (-1)*sum([float(v1)*float(v2)*log(float(v2),2) if (v2>0) else 0 for v1,v2 in zip(PYarr,PXgivenYarr)])
    #HXgivenY=  (-1)*sum([float(v1)*float(v2) if (v2>0) else 0 for v1,v2 in zip(PYarr,PXgivenYarr)])
    HYgivenX=  (-1)*sum([float(v1)*float(v2)*log(float(v2),2) if (v2>0) else 0 for v1,v2 in zip(PXarr,PYgivenXarr)])
    #HYgivenX=  (-1)*sum([float(v1)*float(v2) if (v2>0) else 0 for v1,v2 in zip(PXarr,PYgivenXarr)])
    #mutualInformation = HXY - (HYgivenX+HXgivenY)
    

    
    
    distance = math.copysign(float(HYgivenX+HXgivenY)/float(HXY),1)  if not (HXY==0) else 0
        
            
    
    
    
    
    return distance


