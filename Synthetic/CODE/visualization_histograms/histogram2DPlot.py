'''
Created on 14 nov. 2016

@author: Adnene
'''

import unicodedata

import matplotlib.pyplot as plt
import numpy as np


def drawHistogram2D(dictOfElements,title,xlabel,ylabel):
    colors = ['#4db6ac' ,'#4fc3f7' ,'#7986cb' ,'#ba68c8' ,'#e57373','#1a237e' ,'#607d8b' ,'#ff9800' ,'#4caf50' ,'#673ab7' ,'#e91e63' ,'#37474f' ,'#bcaaa4' ,'#880e4f' ,'#ff6f00' ,'#006064' ,'#0d47a1','#16A085','#F41F4D','#fff176' ,'#867DA5','#BFE8AB','#F68249','#758C20','#B06142','#3D8EB9']
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
    arrP = []
    for key in sorted(dictOfElements):
        value=dictOfElements[key]
        p = plt.bar(left=np.array(pos.tolist()[i]), height=[value['value']], width=width,color=colors[i%len(colors)]) # 
        arrP.append(p[0])
        i+=1
    plt.ylabel(unicodedata.normalize('NFD', unicode(str(ylabel),'iso-8859-1')).encode('ascii', 'ignore'))
    plt.xlabel(unicodedata.normalize('NFD', unicode(str(xlabel),'iso-8859-1')).encode('ascii', 'ignore'))
    plt.title(unicodedata.normalize('NFD', unicode(str(title),'iso-8859-1')).encode('ascii', 'ignore'))
    

    rects = ax.patches
    i=0
    valuesDict = []
    for key in sorted(dictOfElements) :
        valuesDict.append(dictOfElements[key])
    for rect, value in zip(rects, valuesDict):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2, height + 5, str(value['label']), ha='center',fontsize=10)

    #plt.legend(arrP, dictOfElements.keys()) ####IMPORTANT FOR COLOR LEGEND ! 
  
    return plt


