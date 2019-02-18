'''
Created on 11 nov. 2016

@author: Adnene
'''


import math
import unicodedata

from scipy.cluster import hierarchy
from  scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib
import matplotlib.pyplot as plt
#import matplotlib.pyplot as plt
import scipy.spatial.distance as ssd




HEADER_CLUSTER_RESULTS=['ID','ROW_ID','COLUMN_ID','EP_ID','NAME_FULL','NATIONAL_PARTY','GROUPE_ID','COUNTRY','CLUSTER']


HIERARCHICAL_SINGLE_LINKAGE='single'
HIERARCHICAL_AVERAGE_LINKAGE='average'
HIERARCHICAL_COMPLETE_LINKAGE='complete'
HIERARCHICAL_WEIGHTED_LINKAGE='weighted'
HIERARCHICAL_CENTROID_LINKAGE='centroid'
HIERARCHICAL_MEDIAN_LINKAGE='median'
HIERARCHICAL_WARD_LINKAGE='ward'

HIERARCHICAL_SIMPLE='simple'
HIERARCHICAL_FIXED_NUMBER_OF_CLUSERS='nb_clusters'


def getInnerMatrix(matrix):
    innerMatrix=[]
    mapRowsID={}
    mapHeaderID={}
    iterMatrix= iter(matrix)
    head=next(iterMatrix)[1:]
    for index,h_id in enumerate(head) :
        mapHeaderID[index]=h_id
    for index,row in enumerate(iterMatrix):
        mapRowsID[index]=row[0]
        innerMatrix.append(row[1:])
    
    return innerMatrix,mapRowsID,mapHeaderID  

def drawDendrogramme(mepsMeta,linkageMatrix,destination,objectLabel='NATIONAL_PARTY'):
    #matplotlib.use('Agg')
    #matplotlib.rcParams['lines.linewidth'] = 2.2
    
    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        linkageMatrix,
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=8.
    )
    ax = plt.axes()

    ax.set_ylim([-0.02,1.2])
    maptext = [int(str(v._text)) for v in ax.get_xticklabels()]
    mylabels = map(lambda y : unicodedata.normalize('NFD', unicode(mepsMeta[y][objectLabel],'iso-8859-1')).encode('ascii', 'ignore'), maptext)
    ax.set_xticklabels(mylabels,rotation=30, rotation_mode="anchor",ha='right',fontsize=6)
    #print 'hello ! '
    plt.savefig(destination,dpi=300)
    #plt.show()
    # plt.clf()
    # plt.gcf().clear()
    
    #print (cutree.tolist())
    




def applyHierarchiqueClusteringFromDataset(metadataDataset,distanceMatrixComplete,parameter=0.5,typeOfHierarchical=HIERARCHICAL_SIMPLE,method=HIERARCHICAL_AVERAGE_LINKAGE): #single;#average;#complete;#weighted;#centroid;#median;#ward
    clusteringResults=[dict(obj) for obj in metadataDataset]
    innerMatrix,mapRowsID,mapColumnsID=getInnerMatrix(distanceMatrixComplete)
    
#     for i in range (len(innerMatrix)) :
#         innerMatrix[i][i]=float(0)
#     
    for index,row in enumerate(innerMatrix) :
        for column,val in enumerate(row) :
            if not innerMatrix[column][index] == innerMatrix[index][column] :
                if (math.isnan(innerMatrix[index][column])) :
                    innerMatrix[index][column]=1.
                #print innerMatrix[index][column],'-',innerMatrix[column][index] ##ERREURE d'ARRONDIE
                else :
                    innerMatrix[index][column]=innerMatrix[column][index] ##ERREURE d'ARRONDIE
                    
    distArray = ssd.squareform(innerMatrix)

    linkageMatrix=linkage(distArray, method)
    
    if (typeOfHierarchical==HIERARCHICAL_FIXED_NUMBER_OF_CLUSERS):
        cutree = hierarchy.cut_tree(linkageMatrix, n_clusters=[parameter, parameter])
    elif (typeOfHierarchical==HIERARCHICAL_SIMPLE):
        cutree = hierarchy.cut_tree(linkageMatrix, height =[parameter, parameter])
    cuttreeclusters = [(k,v[0]) for k,v in enumerate(cutree.tolist())]
    clusters={}
    for value in iter(cuttreeclusters):
        clusteringResults[value[0]]['CLUSTER']=str(value[1])
        if not clusters.has_key(str(value[1])) :
            clusters[str(value[1])]=0
        clusters[str(value[1])]+=1
    
    
    return clusteringResults,clusters,linkageMatrix


def hierarchicalClusteringFromDataset(metadataDataset,distanceMatrixComplete,dendrogrammeDestination=None,parameter=0.5,typeOfHierarchical=HIERARCHICAL_SIMPLE,method=HIERARCHICAL_AVERAGE_LINKAGE,label_dendrogramme='NATIONAL_PARTY'):
    hierarchicalResults,clusters,linkageMatrix=applyHierarchiqueClusteringFromDataset(metadataDataset,distanceMatrixComplete,parameter,typeOfHierarchical,method)
    if (dendrogrammeDestination) :
        #print 'hello ! '
        drawDendrogramme(hierarchicalResults, linkageMatrix, dendrogrammeDestination,label_dendrogramme)
    return hierarchicalResults,clusters
    

