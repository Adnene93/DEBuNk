'''
Created on 11 nov. 2016

@author: Adnene
'''

import distanceMeasures
import similarityMeasures

AGREEMENT_MEASURES = 'AGREEMENT'
AGREEMENT_ABST_MEASURES = 'AGREEMENT_ABST'
RAJSKI_MEASURES='RAJSKI'

SIMDIST_MAP={
    'AGREEMENT':(similarityMeasures.computeSimilarityYY_NN,distanceMeasures.computeDistanceYY_NN),
    'AGREEMENT_ABST':(similarityMeasures.computeSimilarityYY_NN_AA,distanceMeasures.computeDistanceYY_NN_AA),
    'RAJSKI':(similarityMeasures.computeSimilarityRajski,distanceMeasures.computeDistanceRajski),
    'AGREEMENT_STRICT':(similarityMeasures.computeSimilarityStrict_YY_NN,distanceMeasures.computeDistanceStrict_YY_NN),
    'SIMPLE':(similarityMeasures.computeSimpleSimilarity,distanceMeasures.computeSimpleDistance),
    'VECTORS':(similarityMeasures.computeSimilarityVectors,distanceMeasures.computeDistanceVectors)

}




def measures(measurename):
    '''

    @note AGREEMENT : YY_NN Similarity and distance
    @note AGREEMENT_ABST : YY_NN_AA Similarity and distance
    @note AGREEMENT_STRICT : YY_NN Similarity and distance
    @note RAJSKI : Rajski SImilarity and distance
    '''
    return SIMDIST_MAP[measurename]
    #RAJSKI IS FALSE
