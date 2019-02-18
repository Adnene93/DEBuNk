'''
Created on 21 avr. 2017

@author: Adnene
'''
#!/usr/bin/env python

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors,markers
import six
import ntpath
from os.path import basename, splitext, dirname


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

# The test result file contains is a csv file containing 4 columns
# progName
# nbObject
# nbDistinctObject
# nbClosed
# execTimes separated by ';'
# plot by numObjects ignoring the filenames
FONTSIZE = 25
LEGENDFONTSIZE = 15
MARKERSIZE = 10
LINEWIDTH = 8
FIGSIZE=(8, 6)
BAR_LOG_SCALE=True
TIME_LOG_SCALE=True
LEGEND=True
SHOWPLOT=False
TIMETHRESHOLD=7000


if False : 
    optNames={(True,True,1):"Consent",(True,True,2):"Dissent",(True,False):"CLOSED",(False,True,1):"UB1",(False,True,2):"UB2",(False,False):"BASELINE"}
    optNamesReversed={v:k for k,v in optNames.iteritems()}
    colorByOptBars =  {"Consent":"green","Dissent":"red", "CLOSED" : "blue", "UB1":"red","UB2":"magenta", "BASELINE":"orange"}
    colorByOptLines =  {"Consent":"green","Dissent":"red", "CLOSED" : "blue", "UB1":"red","UB2":"magenta", "BASELINE":"orange"}
    colorByOptEdge =  {"Consent":None,"Dissent":None, "CLOSED" : "blue", "UB1":"red","UB2":"magenta", "BASELINE":"orange"}
    markerByOpt = {"Consent":"o","Dissent":"o", "CLOSED" : "^", "UB1":"o","UB2":"o", "BASELINE":"o"}
    lineTypeByOpt = {"Consent":"-","Dissent":"-", "CLOSED" : "-", "UB1":"--","UB2":"--", "BASELINE":"-"}
    hatchTypeByOpt = {"Consent":"///","Dissent":"o", "CLOSED" : "....", "UB1":"///","UB2":"///", "BASELINE":"x"}
else:
    optNames={(True,True,1):"DSC+UB1",(True,True,2):"DSC+UB2",(True,False):"CLOSED",(False,True,1):"UB1",(False,True,2):"UB2",(False,False):"BASELINE"}
    optNamesReversed={v:k for k,v in optNames.iteritems()}
    colorByOptBars =  {"DSC+UB1":"green","DSC+UB2":"cyan", "CLOSED" : "blue", "UB1":"red","UB2":"magenta", "BASELINE":"orange"}
    colorByOptLines =  {"DSC+UB1":"green","DSC+UB2":"cyan", "CLOSED" : "blue", "UB1":"red","UB2":"magenta", "BASELINE":"orange"}
    colorByOptEdge =  {"DSC+UB1":None,"DSC+UB2":None, "CLOSED" : None, "UB1":None,"UB2":None, "BASELINE":None}
    markerByOpt = {"DSC+UB1":"D","DSC+UB2":"D", "CLOSED" : "^", "UB1":"o","UB2":"o", "BASELINE":"o"}
    lineTypeByOpt = {"DSC+UB1":"-","DSC+UB2":"-", "CLOSED" : "-", "UB1":"--","UB2":"--", "BASELINE":"-"}
    hatchTypeByOpt = {"DSC+UB1":"","DSC+UB2":"", "CLOSED" : "....", "UB1":"///","UB2":"///", "BASELINE":"x"}
dict_map={'attr_items':'#attr_items','attr_users':'#attr_users','attr_aggregate':'#attr_group','#attr_items':'#attr_objects','#items':'#objects','#users1':'#users' ,'#users2':'#users','sigma_context':'thres_objects','sigma_u1':'thres_users','sigma_u2':'thres_users','sigma_quality':'thres_quality'}


def PlotPerf(testResultFile, var_column, activated = list(optNames.values()), plot_bars = True, plot_time = True,show_legend=True,rotateDegree=0) :
    
    if not plot_bars and not plot_time : raise Exception("Are you kidding me ?")
    fileparent = dirname(testResultFile)
    filename = splitext(basename(testResultFile))[0]
    exportPath = (fileparent+"/" if len(fileparent) > 0 else "")+filename+".pdf"
    basedf = pd.read_csv(testResultFile,sep='\t',header=0)
    xAxis = np.array(sorted(set(basedf[var_column])))
    xAxisFixed = range(1,len(xAxis)+1)
    xAxisMapping = {x:i for (x,i) in zip(xAxis,xAxisFixed)}
    optCount = len(activated)
    barWidth = np.float64(0.7/optCount)
    offset = -barWidth*(optCount-1)/2
    fig, baseAx = plt.subplots(figsize=FIGSIZE)
    baseAx.set_xlabel(dict_map.get(var_column,var_column),fontsize=FONTSIZE)
    baseAx.set_xlim([0,max(xAxisFixed)+1])
    baseAx.tick_params(axis='x', labelsize=FONTSIZE)
    baseAx.tick_params(axis='y', labelsize=FONTSIZE)
    plt.xticks(rotation=rotateDegree)
    
    
    if plot_bars : 
        barsAx = baseAx
        barsAx.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0f'))
        barsAx.set_ylabel("#Explored x 10^6",fontsize=FONTSIZE)
        if BAR_LOG_SCALE : barsAx.set_yscale("log",basey=10)
        barsAx.set_xlabel(dict_map.get(var_column,var_column),fontsize=FONTSIZE)
        #barsAx.set_ylim([0,1.2*np.amax(basedf["#all_visited_context"])])
        barsAx.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))

    if plot_time :
        if plot_bars :
            timeAx = baseAx.twinx()
            timeAx.yaxis.tick_left()
            timeAx.yaxis.set_label_position("left")
            barsAx.yaxis.tick_right()
            barsAx.yaxis.set_label_position("right")
        else :
            timeAx = baseAx  
        timeAx.set_ylabel("Execution time (s)",fontsize=FONTSIZE)    
        if TIME_LOG_SCALE : timeAx.set_yscale("log",basey=10)
        timeAx.tick_params(axis='y', labelsize=FONTSIZE)
        timeAx.set_xlim([0,max(xAxisFixed)+1])
        
    
    plt.xticks(xAxisFixed,xAxis, rotation='vertical')
    
    for optName in activated:
        optConstraint = optNamesReversed[optName]
        df = basedf[basedf["closed"]==optConstraint[0]]
        df = df[df["prune"]==optConstraint[1]]
        if len(optConstraint) > 2 :
            df = df[df["upperbound_type"]==optConstraint[2]]
        varVector = np.array(df[var_column])
        #varVector= np.array([x for x in varVector if x<TIMETHRESHOLD])
        
        distinctVarVector = sorted(set(varVector))
        distinctVarVectorFixed = [xAxisMapping[x] for x in distinctVarVector]
        nbVisitedVector = np.array(map(np.mean, [df[df[var_column]==element]["#all_visited_context"] for element in distinctVarVector]))
        execTimeVector = np.array(map(np.mean, [df[df[var_column]==element]["#timespent"] for element in distinctVarVector]))
        execMeanTimeVector = execTimeVector
        execErrorTimeVector = 0
        if len(distinctVarVectorFixed)>0:
            if plot_bars : barsAx.bar(distinctVarVectorFixed+offset, np.array([x/10**6 for x in nbVisitedVector]), hatch= hatchTypeByOpt[optName], width = barWidth, align='center', color= colorByOptBars[optName],label=optName,edgecolor=colorByOptEdge[optName])
            if plot_time : timeAx.errorbar(distinctVarVectorFixed, execMeanTimeVector, yerr = execErrorTimeVector,fmt = lineTypeByOpt[optName]+markerByOpt[optName], linewidth=LINEWIDTH,markersize=MARKERSIZE,label=optName, color= colorByOptLines[optName])
            if show_legend : 
                legend = timeAx.legend(loc='upper right', shadow=True, fontsize=LEGENDFONTSIZE) if plot_time else barsAx.legend(loc='upper right', shadow=True, fontsize=LEGENDFONTSIZE) #'upper left' 'lower right'
        offset+=barWidth
    
    fig.tight_layout()
    
    plt.savefig(exportPath)
    if SHOWPLOT : plt.show()

if __name__ == "__main__" :
    PlotPerf(sys.argv[1],sys.argv[2],plot_bars=sys.argv[3]=="True",plot_time=sys.argv[4]=="True",activated=sys.argv[5:])
    #plot("nb_items.csv","#items",activated = ["DSC+UB1", "CLOSED"], plot_bars = True, plot_time = True)