'''
Created on 14 nov. 2016

@author: Adnene
'''

import unicodedata

import matplotlib.pyplot as plt
import numpy as np


def drawHistogram3D(dictOfElements,title,xlabel,ylabel):
    colors = ['#4db6ac' ,'#4fc3f7' ,'#7986cb' ,'#ba68c8' ,'#e57373','#1a237e' ,'#607d8b' ,'#ff9800' ,'#4caf50' ,'#673ab7' ,'#e91e63' ,'#37474f' ,'#bcaaa4' ,'#880e4f' ,'#ff6f00' ,'#006064' ,'#0d47a1','#fff176' ,'#16A085','#F41F4D','#867DA5','#BFE8AB','#F68249','#758C20','#B06142','#3D8EB9']
    pos = np.arange(len(dictOfElements.keys()))+0.5
    width = 0.5
    ax = plt.axes()
    ax.set_xlim([0,pos.tolist()[len(pos.tolist())-1]+1])
    ax.set_ylim([0,110])
    ax.set_xticks(pos + (width / 2))
    ax.set_yticks(np.array([10,20,30,40,50,60,70,80,90,100]))
    
    
    labelsToSetInX = [ unicodedata.normalize('NFD', unicode(str(label),'iso-8859-1')).encode('ascii', 'ignore') for label in sorted(dictOfElements)]
    
    ax.set_xticklabels(labelsToSetInX,rotation=30, rotation_mode="anchor",ha='right',fontsize=6)
    i=0;
    j=0;
    arrP = []
    colorsKeys=[]
    colorsMap={}
    dim1Rectangle=[]
    for key in sorted(dictOfElements):    
        value=dictOfElements[key]
        newbottom=0
        for key2 in value['composition'] :
            key2_decoded=unicodedata.normalize('NFD', unicode(str(key2),'iso-8859-1')).encode('ascii', 'ignore')
            if colorsMap.has_key(str(key2_decoded)) :
                p = plt.bar(left=np.array(pos.tolist()[i]), height=[value['composition'][key2]], bottom=[newbottom],width=width,color=colorsMap[str(key2_decoded)])
                newbottom+=value['composition'][key2]
                j+=1
            else :
                p = plt.bar(left=np.array(pos.tolist()[i]), height=[value['composition'][key2]], bottom=[newbottom],width=width,color=colors[j%len(colors)])
                colorsMap[str(key2_decoded)]=colors[j%len(colors)]
                colorsKeys.append(key2_decoded)
                arrP.append(p[0])
                newbottom+=value['composition'][key2]
                j+=1

        dim1Rectangle.append({'pos':pos.tolist()[i],'height':newbottom})
        i+=1


    plt.ylabel(unicodedata.normalize('NFD', unicode(str(ylabel),'iso-8859-1')).encode('ascii', 'ignore'))
    plt.xlabel(unicodedata.normalize('NFD', unicode(str(xlabel),'iso-8859-1')).encode('ascii', 'ignore'))
    plt.title(unicodedata.normalize('NFD', unicode(str(title),'iso-8859-1')).encode('ascii', 'ignore'))
    valuesDict = []
    for key in sorted(dictOfElements) :
        valuesDict.append(dictOfElements[key])
    i=0
    for rect, value in zip(dim1Rectangle, valuesDict):
        height = rect['height']
        ax.text(rect['pos'] + width/2, height + 5, str(value['label']), ha='center',fontsize=10)

    lgd = plt.legend(arrP, colorsKeys,fontsize=7,bbox_to_anchor=(1.05, 1), loc=2) ####IMPORTANT FOR COLOR LEGEND ! 
  
    return plt,lgd


