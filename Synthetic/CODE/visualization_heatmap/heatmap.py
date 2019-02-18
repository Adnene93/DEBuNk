'''
Created on 14 nov. 2016

@author: Adnene
'''
import csv
import math
import unicodedata

from  scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster import hierarchy
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import numpy as np
import pandas as pd
import scipy.spatial.distance as ssd
from util.csvProcessing import readCSV
from util.matrixProcessing import getInnerMatrix

def show_values(pc, fmt="%d", **kw):
    from itertools import izip
    pc.update_scalarmappable()
    ax = pc.axes
    for p, color, value in izip(pc.get_paths(), pc.get_facecolors(), pc.get_array()):
        x, y = p.vertices[:-2, :].mean(0)
        if np.all(color[:3] > 0.5):
            color = (0.0, 0.0, 0.0)
        else:
            color = (1.0, 1.0, 1.0)
        ax.text(x, y, fmt % (value*100)+ ' %', ha="center", va="center", color=color,fontsize=60, fontweight='bold', **kw)
        
def generateHeatMap(dataset,destination,color='RdYlGn',vmin=None,vmax=None,organize=False,title=None,showvalues_text=False,only_heatmap=True):
    '''
    @note : color = 'RdYlGn' or 'RdYlGn_r'
    '''
    #dataset = readCSV(source, delimiter=',')
    innerMatrix,rower,header=getInnerMatrix(dataset)
    
    rower=[unicodedata.normalize('NFD', unicode(str(rower[k]),'iso-8859-1')).encode('ascii', 'ignore') for k in sorted(rower)]
    header=[unicodedata.normalize('NFD', unicode(str(header[k]),'iso-8859-1')).encode('ascii', 'ignore')  for k in sorted(header)]  
   
    
    nba=pd.DataFrame(innerMatrix,index=rower,columns=header,dtype=float)
    matrixSimilairty=nba.as_matrix()
    header_new=header[:]
    rower_new=rower[:]
    
    ##########################################################################
    if organize :
        matrix=nba.as_matrix()
        matrix=[[1-x for x in row] for row in matrix]
        isSquare=True
        if len(matrix)<>len(matrix[0]):
            isSquare=False
        if isSquare:
            for index,row in enumerate(matrix) :
                for column,val in enumerate(row) :
                    if not innerMatrix[column][index] == matrix[index][column] :
                        if (math.isnan(matrix[index][column])) :
                            matrix[index][column]=1.
                        #print innerMatrix[index][column],'-',innerMatrix[column][index] ##ERREURE d'ARRONDIE
                        else :
                            matrix[index][column]=matrix[column][index] ##ERREURE d'ARRONDIE
                    if index==column:
                        matrix[index][column]=0.
        
        
        
        
            distArray = ssd.squareform(matrix)    
            linkageMatrix=linkage(distArray, 'average')
            
            cuttreeclusters=sorted([(i,t) for (i,t) in enumerate(hierarchy.fcluster(linkageMatrix,0.2,'distance'))],key=lambda x : x[1])
            clusters={}
            for i,c in cuttreeclusters:
                if not clusters.has_key(c):
                    clusters[c]=[]
                clusters[c].append(i)
            #print clusters
                
            cuttreeclustersSorted=[]
             
            pairs=[]
            for i in range(len(matrix)):
                row = matrix[i]
                for j in range(len(row)):
                    pairs.append((i,j,row[j]))
            pairs=sorted(pairs,key=lambda x : x[2])
            visited=[]
            for c,c_elems in clusters.iteritems():
                for i,j,d in pairs:
                    if i in c_elems and j in c_elems:
                        if i not in visited:
                            visited.append(i)
                            cuttreeclustersSorted.append((i,c))
                        if j not in visited:
                            visited.append(j)
                            cuttreeclustersSorted.append((j,c))
            rower_new=[rower[t[0]] for t in cuttreeclustersSorted]
            header_new=[header[t[0]] for t in cuttreeclustersSorted]
            nba=nba.reindex(index=rower_new,columns=header_new)
        else:
            cuttreeclustersSorted=[]
            pairs=[]
            for i in range(len(matrix)):
                row = matrix[i]
                for j in range(len(row)):
                    pairs.append((i,sum(row)))
            pairs=sorted(pairs,key=lambda x : x[1])       
            visited=[]     
            for i,d in pairs:
                if i not in visited:
                    visited.append(i)
                    cuttreeclustersSorted.append((i,0))         
        
            rower_new=[rower[t[0]] for t in cuttreeclustersSorted]
            header_new=header[:]
            nba=nba.reindex(index=rower_new,columns=header_new)
    
    
    
    ##########################################################################
    
    
    fig, ax = plt.subplots()
    #fig.gca().set_position((.4, .4, .8, .8))
    masked_array = np.ma.array (nba, mask=np.isnan(nba))
    heatmap = ax.pcolor(masked_array, cmap=plt.cm.get_cmap(name=color), alpha=1,vmax=vmax,vmin=vmin)
    if showvalues_text :
        show_values(heatmap)
    fig = plt.gcf()
    
    if not only_heatmap:
        fig.subplots_adjust(bottom=0.2,top=0.87,right=1.)
    fig.set_size_inches(40, 40) #40, 40
    
    ax.set_frame_on(False)
    ax.set_yticks(np.arange(nba.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(nba.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    if not only_heatmap:
        fig.suptitle(title, fontsize=25, fontweight='bold')
    xlabels= header_new#header[:]
    ylabels=rower_new#rower
    
    ax.set_xticklabels(xlabels, minor=False,fontsize=60)
    ax.set_yticklabels(ylabels, minor=False,fontsize=60)

    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    #plt.colorbar(heatmap)
    ax.grid(False)

    ax = plt.gca()
    
    
    
    #ax.set_position((.1, .3, .8, .6))
    if not only_heatmap:
        plt.figtext(0.12, .1,'Details about :\n * the pattern \n * dossiers \n * compared MEPs',fontsize=40)
    
    
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    if not only_heatmap:
        plt.colorbar(heatmap)
    #fig.tight_layout()
    plt.tight_layout()
    plt.savefig(destination,dpi=100)
    fig.clf()
    plt.clf()
    plt.gcf().clear()
    plt.cla()
    plt.close('all')
    
    

def generateHeatMapFromNoHeaderMat(source,destination,color='RdYlGn_r'):
    '''
    @note : color = 'RdYlGn' or 'RdYlGn_r'
    '''
    nba = pd.read_csv(source,sep=",", index_col=0,header=None)
    rower=[]
    with open(source, 'rb') as csvfile:
        readfile = csv.reader(csvfile, delimiter=',')
        for row in readfile :
            rower.append(row[0])
    
    
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(nba, cmap=plt.cm.get_cmap(name=color), alpha=0.8,vmax=1.0,vmin=-1.0)
    fig = plt.gcf()
    fig.set_size_inches(40, 40)
    ax.set_frame_on(False)
    ax.set_yticks(np.arange(nba.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(nba.shape[1]) + 0.5, minor=False)
    ax.invert_yaxis()
    ax.xaxis.tick_top()
    
    ylabels=rower
    
    
    rangeLoop = range(len(ylabels))
    rangeLoop.reverse()
    for i in rangeLoop:
        if (not (i+1==len(ylabels))) and (ylabels[i]==ylabels[i+1]): 
            ylabels[i+1]=' '
    
    
    

    
    deb=0
    fin=0
    for i in range(len(ylabels)):
        if (not (i+1 == len(ylabels))) and  (ylabels[i+1]==' '):
            fin+=1
        else : 
            ylabels[int((fin+deb))/2]=ylabels[deb]
            if not (fin == deb):
                ylabels[deb]=' '
            deb=fin+1
            fin=deb
    
    
    ax.set_xticklabels(ylabels, minor=False)
    ax.set_yticklabels(ylabels, minor=False)

    plt.xticks(rotation=90)

    ax.grid(False)

    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    #plt.colorbar(heatmap)    
    plt.savefig(destination,dpi=100)
    plt.clf()
    plt.gcf().clear()
    
    
    

#################################################################################### 
###############################WorkflowStages####################################### 
#################################################################################### 




def workflowStage_heatmapGenerator(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'heatmap_visualization',
        'inputs': {
            'dataset':[],
            'destinationFile' : 'file_path'
        },
        'configuration': {
            'color'='RdYlGn', || RdYlGn_r,
            'organize'=False,
            'vmin'=None,
            'vmax'=None
        },
        'outputs':{
        
        }
    }
    '''
    
    
    
    localConfiguration={}
    localConfiguration['color']=configuration.get('color','RdYlGn') 
    localConfiguration['vmin']=configuration.get('vmin',None) 
    localConfiguration['vmax']=configuration.get('vmax',None)
    localConfiguration['organize']=  configuration.get('organize',False)
    localConfiguration['title']=  configuration.get('title','#Pattern + #Quality (#Comparaison_Measure_used ,#Quality_measure_used)')
    generateHeatMap(inputs['dataset'], inputs['destinationFile'], color=localConfiguration['color'], vmin=localConfiguration['vmin'], vmax=localConfiguration['vmax'],organize=localConfiguration['organize'],title=localConfiguration['title'])
    
    return outputs