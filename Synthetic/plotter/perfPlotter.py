import sys
import pandas as pd
import numpy as np
from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import colors,markers
import six
import ntpath
from os.path import basename, splitext, dirname
from math import log,pi


usedFontSize=22
#usedColors=["blue","red","black","green","purple"]
#usedMarkers=["s","o","v","p","<"]
usedMarkerSize=10
usedLineWidth=4
unitTimeFactor=1


rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
rc('text', usetex=True)

CONFIGURATION="Q3"
Y_SCALE_BARS="nb_candidates_subgroups"

if CONFIGURATION=="Q1": #HMT TO ITEMSET
	FONTSIZE = 50
	LEGENDFONTSIZE = 35
	MARKERSIZE = 10
	LINEWIDTH = 8
	FIGSIZE=(18.5, 9)
	LOG_SCALE_X=False
	WIDTHOFBARS=0.6
	NB_VALUES_TO_PINCH=100
	XAXISVALUE_REDUCEPRECISION=False
	Y_SCALE_BARS="nb_visited_subgroups"
	TIME_NORMALIZE=False

if CONFIGURATION=="Q2": #COMAPRING ALGORITHMS
	FONTSIZE = 50
	LEGENDFONTSIZE = 35
	MARKERSIZE = 10
	LINEWIDTH = 8
	FIGSIZE=(18.5, 7)
	LOG_SCALE_X=False
	WIDTHOFBARS=0.6
	NB_VALUES_TO_PINCH=100
	XAXISVALUE_REDUCEPRECISION=False
	Y_SCALE_BARS="nb_candidates_subgroups"
elif CONFIGURATION=="Q3": #SCALING
	FONTSIZE = 50
	LEGENDFONTSIZE = 35
	MARKERSIZE = 10
	LINEWIDTH = 8
	FIGSIZE=(13, 6)
	LOG_SCALE_X=True
	WIDTHOFBARS=0.3
	NB_VALUES_TO_PINCH=1000
	XAXISVALUE_REDUCEPRECISION=True
	Y_SCALE_BARS="nb_candidates_subgroups"
	#Y_SCALE_BARS="nb_visited_subgroups"
elif CONFIGURATION=="Q4": #Sampling
	FONTSIZE = 40
	LEGENDFONTSIZE = 32
	MARKERSIZE = 8
	LINEWIDTH = 7
	FIGSIZE=(13, 6)#(15, 8)
	LOG_SCALE_X=False
	WIDTHOFBARS=0.3
	NB_VALUES_TO_PINCH=5
	XAXISVALUE_REDUCEPRECISION=False
	Y_SCALE_BARS="nb_candidates_subgroups"


LEGEND=False
SHOWPLOT=False
TIMETHRESHOLD=7000


#332288, 88CCEE, 44AA99, 117733, 999933, DDCC77, CC6677, 882255, AA4499, #117733
optNames={(True,True,1):"DSC+CLOSED+UB1",(True,True,2):"DSC+CLOSED+UB2",(True,False):"DSC+CLOSED",(False,True,1):"UB1",(False,True,2):"UB2",(False,False):"DSC"}
optNamesReversed={v:k for k,v in optNames.iteritems()}
colorByOptBars =  {"DISSENT":"#D64541","CONSENT":"#117733","ITEMSET":"#D64541","HMT":"#44AA99","DSC+CLOSED+UB1":"#88CCEE","DSC+CLOSED+UB2":"#44AA99", "DSC+CLOSED" : "#CC6677", "UB1":"red","UB2":"magenta", "DSC":"#DDCC77", "DSC+RandomWalk":"#AA4499","DSC+SamplingPeers+RandomWalk":"#AA4499"}
colorByOptLines =  {"DISSENT":"#D64541","CONSENT":"#117733","ITEMSET":"#D64541","HMT":"#44AA99","DSC+CLOSED+UB1":"#88CCEE","DSC+CLOSED+UB2":"#44AA99", "DSC+CLOSED" : "#CC6677", "UB1":"red","UB2":"magenta", "DSC":"#DDCC77", "DSC+RandomWalk":"#AA4499","DSC+SamplingPeers+RandomWalk":"#AA4499"}
colorByOptEdge =  {"DISSENT":None,"CONSENT":None,"ITEMSET":None,"HMT":None,"DSC+CLOSED+UB1":None,"DSC+CLOSED+UB2":None, "DSC+CLOSED" : None, "UB1":None,"UB2":None, "DSC":None,"DSC+RandomWalk":None,"DSC+SamplingPeers+RandomWalk":None}
markerByOpt = {"DISSENT":"D","CONSENT":"D","ITEMSET":"D","HMT":"D","DSC+CLOSED+UB1":"D","DSC+CLOSED+UB2":"D", "DSC+CLOSED" : "^", "UB1":"o","UB2":"o", "DSC":"o","DSC+RandomWalk":'D',"DSC+SamplingPeers+RandomWalk":'D'}
lineTypeByOpt = {"DISSENT":"-","CONSENT":"-","ITEMSET":"-","HMT":"-","DSC+CLOSED+UB1":"-","DSC+CLOSED+UB2":"-", "DSC+CLOSED" : "-", "UB1":"--","UB2":"--", "DSC":"-","DSC+RandomWalk":'-',"DSC+SamplingPeers+RandomWalk":'-'}
hatchTypeByOpt = {"DISSENT":"","CONSENT":"","ITEMSET":"","HMT":"","DSC+CLOSED+UB1":"","DSC+CLOSED+UB2":"", "DSC+CLOSED" : "....", "UB1":"///","UB2":"///", "DSC":"x","DSC+RandomWalk":"","DSC+SamplingPeers+RandomWalk":""}
dict_map={
	'nb_objects':'\#entites',
	'nb_users':'\#individuals',
	'nb_attrs_objects':'\#attributes\_entities',
	'nb_attrs_users':'\#attributes\_individuals',
	'attr_items':'#attr_items',
	'attr_users':'#attr_users',
	'attr_aggregate':'#attr_group',
	'#attr_items':'#attr_objects',
	'#items':'#objects',
	'#users1':'#users' ,
	'#users2':'#users',
	'sigma_context':'thres_objects',
	'sigma_u1':'thres_users',
	'sigma_u2':'thres_users',
	'sigma_quality':'thres_quality',
	'threshold_objects':'$\sigma_E$',
	'threshold_nb_users_1':'$\sigma_I$',
	'max_nb_tag_by_object':'max\_nb\_tag\_by\_object',
	'quality_threshold':'$\sigma_\\varphi$ - $\\varphi_{dissent}$',
	'CONSENTquality_threshold':'$\sigma_\\varphi$ - $\\varphi_{consent}$',
	'RATIOquality_threshold':'$\sigma_\\varphi$ - $\\varphi_{ratio}$',
	'tree_height':'tree\_height',
	'k_ary':'k\_ary',
	'DSC':'Baseline',
	'DSC+CLOSED':'Baseline+Closed',
	'DSC+CLOSED+UB2':'DEBuNk',
	'nb_attrs_objects_in_itemset':'nb\_items\_entities',
	'nb_attrs_users_in_itemset':'nb\_items\_individuals',

	'precision':'Precision',
	'recall':'Recall',
	'f1_score':'F1\_Score',

	'HMT':'DEBuNk - HMT',
	'ITEMSET':'DEBuNk - ITEMSET',


	'precision_jaccard':'Precision',
	'recall_jaccard':'Recall',
	'fscore_jaccard':'F1\_Score',
	'noise_rate_negative_examples':'Noise'


}



def plotPerformanceSynthetic(testResultFile, var_column, activated = list(optNames.values()), plot_bars = False, plot_time = True,show_legend=True,rotateDegree=0,BAR_LOG_SCALE=False,TIME_LOG_SCALE=False) :
	PLOT_FIXED=True
	var_column_to_get_label=var_column
	if var_column[:7]=='CONSENT' or var_column[:5]=='RATIO':
		var_column='quality_threshold'

	if not plot_bars and not plot_time : raise Exception("Are you kidding me ?")
	fileparent = dirname(testResultFile)
	filename = splitext(basename(testResultFile))[0]
	exportPath = (fileparent+"/" if len(fileparent) > 0 else "")+filename+".pdf"
	basedf = pd.read_csv(testResultFile,sep='\t',header=0)
	xAxis = np.array(sorted(set(basedf[var_column])))
	xAxis_set=set(xAxis)
	if len(xAxis)>NB_VALUES_TO_PINCH:
		xAxis=np.array(sorted([xAxis[len(xAxis)-1-int(round((k/float(NB_VALUES_TO_PINCH))*len(xAxis)))] for k in range(NB_VALUES_TO_PINCH)]))
		xAxis_set=set(xAxis)
		print xAxis_set
	xAxisFixed = range(1,len(xAxis)+1)
	if PLOT_FIXED:
		xAxisMapping = {x:i for (x,i) in zip(xAxis,xAxisFixed)}
	else:
		xAxisMapping = {x:i for (x,i) in zip(xAxis,xAxis)}
	optCount = len(activated)
	barWidth = np.float64(WIDTHOFBARS/optCount) #Affects space between bars
	offset = -barWidth*(optCount-1)/2
	fig, baseAx = plt.subplots(figsize=FIGSIZE)
	baseAx.set_xlabel(dict_map.get(var_column_to_get_label,var_column),fontsize=FONTSIZE)
	baseAx.set_xlim([0,max(xAxisFixed)+1])
	baseAx.tick_params(axis='x', labelsize=FONTSIZE)
	baseAx.tick_params(axis='y', labelsize=FONTSIZE)
	plt.xticks(rotation=rotateDegree)
	
	
	if plot_bars : 
		barsAx = baseAx
		#barsAx.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0f'))
		
		if CONFIGURATION=="Q1":
			barsAx.set_ylabel(r'\#explored $\times 10^6$',fontsize=FONTSIZE)
		else:
			barsAx.set_ylabel(r'\#evaluated',fontsize=FONTSIZE)
		

		if BAR_LOG_SCALE : barsAx.set_yscale("log",basey=10)
		else: barsAx.set_yscale("linear")
		barsAx.set_xlabel(dict_map.get(var_column_to_get_label,var_column),fontsize=FONTSIZE)
		#barsAx.set_ylim([0,1.2*np.amax(basedf["#all_visited_context"])])
		#barsAx.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))

	if plot_time :
		if plot_bars :
			timeAx = baseAx.twinx()
			timeAx.yaxis.tick_left()
			timeAx.yaxis.set_label_position("left")
			barsAx.yaxis.tick_right()
			barsAx.yaxis.set_label_position("right")
		else :
			timeAx = baseAx 

		
		timeAx.set_ylabel("",fontsize=FONTSIZE) 


		if TIME_LOG_SCALE : timeAx.set_yscale("log",basey=10)
		else: timeAx.set_yscale("linear")
		timeAx.tick_params(axis='y', labelsize=FONTSIZE)
		if PLOT_FIXED:
			timeAx.set_xlim([0,max(xAxisFixed)+1])
		
	
	plt.xticks(xAxisFixed,xAxis, rotation='vertical')
	#varVectorX = np.array(basedf[basedf["algorithm"]==activated[-1]][var_column])
	distinctVarVectorX = sorted(set(xAxis))
	distinctVarVectorX_adapted=distinctVarVectorX
	if XAXISVALUE_REDUCEPRECISION:
		divide_by_exponent=0
		#divide_by_exponent=(int(log(float(distinctVarVectorX[-1]),10))/3)*3
		#distinctVarVectorX_adapted=[float("%.2f"% (float(x)/(10**divide_by_exponent))) for x in distinctVarVectorX]
		if divide_by_exponent>0:
			barsAx.set_xlabel(dict_map.get(var_column_to_get_label,var_column)+ r' $\times10^'+str(divide_by_exponent)+'$',fontsize=FONTSIZE)

		#r'$'+item+'^'+(('%.f'%((float(str(item))/exauhaustive_time_spent)*100))+'\%')+'$' 

	timeAx.set_xticklabels([r'$'+str(x if x!=int(x) else int(x))+'$'  for x in distinctVarVectorX_adapted])
	# if LOG_SCALE_X : 
	# 	timeAx.set_xscale("linear")
		#barsAx.set_xscale("linear")
	colors=[ '#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
	ind_color=0

	for optName in activated:
		for target in ['precision_jaccard','recall_jaccard','fscore_jaccard']: 
			target_label=dict_map.get(target,target)
			df = basedf[basedf["algorithm"]==optName]

			varVector = np.array(df[var_column])
			
			distinctVarVector = sorted(set(varVector))

			distinctVarVectorFixed = [xAxisMapping[x] for x in distinctVarVector]
			#print distinctVarVectorFixed

			nbVisitedVector = np.array(map(np.mean, [df[df[var_column]==element]["nb_patterns"] for element in distinctVarVector]))
			execTimeVector = np.array(map(np.mean, [df[df[var_column]==element][target] for element in distinctVarVector]))
		
			execMeanTimeVector = execTimeVector
			# print optName,target
			# raw_input('....')

			execErrorTimeVector = 0
			if len(distinctVarVectorFixed)>0:
				if plot_bars : 
					barsAx.bar(distinctVarVectorFixed+offset, np.array([x for x in nbVisitedVector]), hatch= hatchTypeByOpt[optName], width = barWidth, align='center', color= colorByOptBars[optName],label=optName,edgecolor=colorByOptEdge[optName],alpha=0.8)
				if plot_time : 
					#timeAx.errorbar(distinctVarVectorFixed, execMeanTimeVector, yerr = execErrorTimeVector,fmt = lineTypeByOpt[optName]+markerByOpt[optName], linewidth=LINEWIDTH+2,markersize=MARKERSIZE,label=optName, color= 'black')
					#timeAx.errorbar(distinctVarVectorFixed, execMeanTimeVector, yerr = execErrorTimeVector,fmt = lineTypeByOpt[optName]+markerByOpt[optName], linewidth=LINEWIDTH,markersize=MARKERSIZE,label=target, color= colorByOptLines[optName])
					timeAx.errorbar(distinctVarVectorFixed, execMeanTimeVector, yerr = execErrorTimeVector,fmt = lineTypeByOpt[optName]+markerByOpt[optName], linewidth=LINEWIDTH,markersize=MARKERSIZE,label=target_label,color=colors[ind_color])
					timeAx.set_ylim([-0.05,1.05])
					
					#timeAx.axvline(exauhaustive_time_spent, 0, 1,color="red",linewidth=2.5,linestyle="--",markersize=10)
					# timeAx.axvline(3600, 0, 1,color="green",linewidth=2.5,linestyle="--",markersize=10)
					# timeAx.axhline(0.8, 0, 1,color="green",linewidth=2.5,linestyle="--",markersize=10)


				if show_legend : 
					legend = timeAx.legend(loc='lower left', shadow=True, fontsize=LEGENDFONTSIZE, framealpha=0.7) if plot_time else barsAx.legend(loc='upper left', shadow=True, fontsize=LEGENDFONTSIZE, framealpha=0.7) #'upper left' 'lower right'
					timeAx.legend(loc='lower center', bbox_to_anchor=(0.5, 0.01),ncol=3,fancybox=True,fontsize=LEGENDFONTSIZE, framealpha=0.85)
			offset+=barWidth
			ind_color+=1
	
	plt.xticks(rotation=rotateDegree)
	fig.tight_layout()
	plt.savefig(exportPath)
	fig.tight_layout()
	if SHOWPLOT : plt.show()



def plot_radar_chart(workingrepo,method_recall_patterns={}):

	
	show_only_legend=False
	if show_only_legend:
		figsize=(38,1.5)
		bbox_to_anchorLegend=(0.56, 1.42)
		nb_col_legend=5
		framealpha=1.
	else:
		figsize=(9, 8)
		bbox_to_anchorLegend=(0.5, 0.22)
		nb_col_legend=2
		framealpha=0.85


	plt.figure(figsize=figsize) 
	# Set data
	# Set data
	df = pd.DataFrame({
	'group': ['A','B','C','D'],
	'var1': [0.73, 0.49, 0.11, 0.76],
	'var2': [0.26, 0.21, 0.48, 0.24],
	'var3': [0.94, 0.91, 0.16, 0.06],
	
	})
	x_ticks=["DEBuNk","Quick-DEBuNk","COSMIC","SD-Cartesian","SD-Majority"]
	if True:
		
		DIMENSIONS=[r'$\textbf{P}_{'+ r'\textbf{'+str((k+1))+'}}$' for k in range(len(method_recall_patterns.values()[0]))]
		GROUP=x_ticks
		

		INPUT_FOR_RADAR_CHART={'group': []}
		for d in DIMENSIONS:
			INPUT_FOR_RADAR_CHART[d]=[]

		for g in GROUP:
			INPUT_FOR_RADAR_CHART['group'].append(g)
			for d in range(len(DIMENSIONS)):
				INPUT_FOR_RADAR_CHART[DIMENSIONS[d]].append(method_recall_patterns[g][d])

		df = pd.DataFrame(INPUT_FOR_RADAR_CHART)
	 
	 
	 
	# ------- PART 1: Create background
	 
	# number of variable
	categories=DIMENSIONS#list(df)[1:]
	N = len(categories)
	 
	# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
	angles = [n / float(N) * 2 * pi for n in range(N)]
	angles += angles[:1]
	 
	# Initialise the spider plot
	ax = plt.subplot(111, polar=True)
	 
	# If you want the first axis to be on top:
	ax.set_theta_offset(pi / 2)
	ax.set_theta_direction(-1)
	 
	# Draw one axe per variable + add labels labels yet
	plt.xticks(angles[:-1], categories)
	 
	# Draw ylabels
	ax.set_rlabel_position(0)
	plt.yticks([0.2,0.4,0.6,0.8,1.], ["   20\%","   40\%","   60\%","   80\%",""], color="black", size=35)
	plt.ylim(0,1.)
	plt.xticks(size=35)
	 
	 
	# ------- PART 2: Add plots
	 
	# Plot each individual = each line of the data
	# I don't do a loop, because plotting more than 3 groups makes the chart unreadable
	 
	# Ind1
	
	# print values
	# print method_recall_patterns
	# raw_input('...')
	
	colors=[ '#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
	
	
	#MAPCOLOR={"Quick-DEBuNk":'#0E0DD5',"DEBuNk": '#187A1D',"SD-Majority": '#C7241B',"SD-Cartesian": '#38B8B5',"COSMIC": '#A616B0'}
	MAPCOLOR={"Quick-DEBuNk":'g',"DEBuNk": 'b',"SD-Majority": 'm',"SD-Cartesian": 'c',"COSMIC": 'r'}
	for i,v in enumerate(x_ticks):

		values=df.loc[i].drop('group').values.flatten().tolist()
		values += values[:1]
		
		if show_only_legend:
			plt.plot([], MAPCOLOR[v], label=r'\textbf{'+v+'}')
		else:
			ax.plot(angles, values, linewidth=2., linestyle='solid', label=r'\textbf{'+v+'}',markersize=35)
			ax.fill(angles, values, MAPCOLOR[v], alpha=0.3)
		
		print i,v,MAPCOLOR[v]
	# values=df.loc[0].drop('group').values.flatten().tolist()
	# values += values[:1]
	# ax.plot(angles, values, linewidth=1, linestyle='solid', label="group A")
	# ax.fill(angles, values, colors[0], alpha=0.1)
	 
	# #	Ind2
	# values=df.loc[1].drop('group').values.flatten().tolist()
	# values += values[:1]
	# ax.plot(angles, values, linewidth=1, linestyle='solid', label="group B")
	# ax.fill(angles, values, 'r', alpha=0.1)
	 
	# Add legendloc='upper center', bbox_to_anchor=(0.5, 1.1),ncol=3,fancybox=True,fontsize=LEGENDFONTSIZE, framealpha=0.85
	#plt.legend(loc='upper right', bbox_to_anchor=(0.2, 0.2))
	if show_only_legend:
		leg=plt.legend(loc='upper center', bbox_to_anchor=bbox_to_anchorLegend,ncol=nb_col_legend,fancybox=True, framealpha=framealpha,fontsize=50)
		for legobj in leg.legendHandles:
			legobj.set_linewidth(5)
	#plt.show()



	plt.tight_layout()
	plt.savefig(workingrepo+"//comparison_radar.pdf")




# def plot_boxplot_chart(workingrepo,method_f_score_patterns={}):
# 	colors=[ '#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
# 	data=[]
# 	ticks=[]
# 	tickslabel=[]
# 	for i,name in enumerate(sorted(method_f_score_patterns)):
# 		data.append(method_f_score_patterns[name])
# 		ticks.append((i+1))
# 		tickslabel.append(name)
# 	#data = [[np.random.rand(100)] for i in range(3)]
# 	plt.figure()
# 	plt.boxplot(data,colors)
# 	plt.xticks(ticks, tickslabel)
# 	plt.legend(loc='upper center', bbox_to_anchor=(0.5, 0.1),ncol=3,fancybox=True, framealpha=0.85)
# 	plt.savefig(workingrepo+"//boxplot.pdf")


def plot_boxplot_chart(workingrepo,method_f_score_patterns={}):
    colors=[ '#332288', '#88CCEE', '#44AA99', '#117733', '#999933', '#DDCC77', '#CC6677', '#882255', '#AA4499']
    x_ticks=["DEBuNk","Quick-DEBuNk","COSMIC","SD-Cartesian","SD-Majority"]
    #x_ticks=sortedmethod_f_score_patterns.keys()


    # if maxY==-1:
    #     maxY=max(max(dataSias)+max(dataCenergetics)+max(dataSubspace))*1.3
    
    #MAPCOLOR={"Quick-DEBuNk":'#0E0DD5',"DEBuNk": '#187A1D',"SD-Majority": '#C7241B',"SD-Cartesian": '#38B8B5',"COSMIC": '#A616B0'}
    MAPCOLOR={"Quick-DEBuNk":'g',"DEBuNk": 'b',"SD-Majority": 'm',"SD-Cartesian": 'c',"COSMIC": 'r'}
    def set_box_color(bp, color):
        plt.setp(bp['boxes'], color=color)
        plt.setp(bp['whiskers'], color=color)
        plt.setp(bp['caps'], color=color)
        plt.setp(bp['medians'], color=color)
    
    plt.figure(figsize=(13.05, 8))
    #plt.clf()
    for i,name in enumerate(x_ticks):

    	bpl = plt.boxplot(method_f_score_patterns[name],  positions=[i*3.0],sym='', widths=1.,medianprops={'linewidth': usedLineWidth},boxprops={'linewidth': usedLineWidth},whiskerprops={'linewidth': usedLineWidth},capprops={'linewidth': usedLineWidth},flierprops={'linewidth': usedLineWidth})
    	print name
    #bpr = plt.boxplot(dataCenergetics, positions=np.array(range(len(dataCenergetics)))*2.0+0, sym='', widths=0.3,medianprops={'linewidth': usedLineWidth},boxprops={'linewidth': usedLineWidth},whiskerprops={'linewidth': usedLineWidth},capprops={'linewidth': usedLineWidth},flierprops={'linewidth': usedLineWidth})
    #bpg = plt.boxplot(dataSubspace, positions=np.array(range(len(dataSubspace)))*2.0+0.4, sym='', widths=0.3,medianprops={'linewidth': usedLineWidth},boxprops={'linewidth': usedLineWidth},whiskerprops={'linewidth': usedLineWidth},capprops={'linewidth': usedLineWidth},flierprops={'linewidth': usedLineWidth})
    	set_box_color(bpl, MAPCOLOR[name]) # colors are from http://colorbrewer2.org/
    	plt.plot([], MAPCOLOR[name], label=r'\textbf{'+x_ticks[i]+'}')
    # set_box_color(bpr, '#2C7BB6')
    # set_box_color(bpg, '#16A085')
    
    # draw temporary red and blue lines and use them to create a legend
    
    # plt.plot([], c='#2C7BB6', label=legends[1])
    # plt.plot([], c='#16A085', label=legends[2])
    #leg=plt.legend(fontsize=usedFontSize,framealpha=0.7,loc=legendsLoc)
    if False:
	    leg=plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),ncol=5,fancybox=True, framealpha=0.85,fontsize=30)
	    for legobj in leg.legendHandles:
	        legobj.set_linewidth(usedLineWidth)
    

    plt.ylabel('FScore', fontsize=34)
    plt.yticks(fontsize=34)    
    plt.xticks(range(0, len(x_ticks) * 3, 3), x_ticks,fontsize=27)
    plt.tick_params(axis='y', labelsize=34)
    plt.xlim(-2, len(x_ticks)*3)
    

    plt.ylim(0, 1.)
    plt.tight_layout()
    plt.savefig(workingrepo+"//comparison_boxplot.pdf")
    
# dataSias = [[1,2,5], [5,7,2,2,5], [7,2,5]]
# dataCenergetics = [[6,4,2], [1,2,5,3,2], [2,3,5,1]]
# dataSubspace = [[6,4,2], [1,2,5,3,2], [2,3,5,1]]
# ticks = ['A', 'B', 'C']
