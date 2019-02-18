'''
Created on 11 nov. 2016

@author: Adnene
'''

import os

##################################POSSIBLE HEADERS#################################
VOTES_EXPORTS_HEADER=['VOTEID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID',
              'COUNTRY','DOSSIERID','VOTE_DATE','USER_VOTE']

STATS_HEADER=['MEP1','MEP1_NAME','MEP1_PARTY','MEP1_GROUP','MEP1_COUNTRY',
              'MEP2','MEP2_NAME','MEP2_PARTY','MEP2_GROUP','MEP2_COUNTRY',
              'NB_VOTES','YY','NN','AA','YN','YA','NY','NA','AY','AN']

COMPARAISON_HEADER=['MEP1','MEP1_NAME','MEP1_PARTY','MEP1_GROUP','MEP1_COUNTRY',
                    'MEP2','MEP2_NAME','MEP2_PARTY','MEP2_GROUP','MEP2_COUNTRY',
                    'SIMILARITY','DISTANCE','TOTAL_VOTES']

META_HEADER=['ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY']

CLUSTERING_HEADER=['ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','CLUSTER']
##################################POSSIBLE HEADERS#################################


def printTimeSpent(whatWasDone,start,stop):
    print ('\n\n----------------------------------------------------------------')        
    print ('Time spent '+whatWasDone+' : ', stop - start) 
    print ('----------------------------------------------------------------\n\n')
    
def utilPrint(whatWasDone):
    print ('\n\n----------------------------------------------------------------')        
    print (whatWasDone) 
    print ('----------------------------------------------------------------\n\n')

    

def listFiles(path):
    files = (file for file in os.listdir(path) 
         if os.path.isfile(os.path.join(path, file)))
    listOfRetrievedFiles=[f for f in files]
    return listOfRetrievedFiles




