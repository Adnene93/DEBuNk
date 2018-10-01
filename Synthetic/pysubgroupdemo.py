import pysubgroup as ps
import pandas as pd
import csv
import timeit
import sys

def writeCSVwithHeader(data,destination,selectedHeader=None,delimiter='\t',flagWriteHeader=True):
	header=selectedHeader if selectedHeader is not None else data[0].keys()
	print(header)
	# if flagWriteHeader : 
	# 	with open(destination, 'w') as f:
	# 		f.close()
	list_of_rows=[]
	#with open(destination, 'w') as f:
	f = open(destination,'w',newline='')
	writer2 = csv.writer(f,delimiter='\t',lineterminator='\n')
	if flagWriteHeader:
		#writer2.writerow(header)
		list_of_rows.append(header)
	for elem in iter(data):
		row=[]
		for i in range(len(header)):
			row.append(elem[header[i]])
		list_of_rows.append(row)
		#writer2.writerow(row)
	writer2.writerows(list_of_rows)

			
def compute_support(data,selector):
	all_columns=[]
	for column in data.iloc[[0]]:
		all_columns.append(column)

	sup=(data.query(selector))
	# for row in data.query(selector):
	# 	print(row)
	#print(sup)
	#print (data.idi.unique().tolist())
	#print ('idi',sup.idi.unique().tolist())
	#print ('ide',sup.ide.unique().tolist())
	if 'idi_1' not in all_columns: #'Majority stuffs'

		record={
			'context':str(selector),
			'g_1':str(selector),
			'g_2':str(selector),
			'context_extent':[str(x) for x in sup.ide.unique().tolist()],
			'g_1_extent':[str(x) for x in sup.idi.unique().tolist()],
			'g_2_extent':[str(x) for x in data.idi.unique().tolist()],
			'sim_ref':0.,
			'sim_context':0.,
			'quality':0.
		}
	else:
		#print ('here my baby')
		record={
			'context':str(selector),
			'g_1':str(selector),
			'g_2':str(selector),
			'context_extent':[str(x) for x in sup.ide.unique().tolist()],
			'g_1_extent':[str(x) for x in sup.idi_1.unique().tolist()],
			'g_2_extent':[str(x) for x in sup.idi_2.unique().tolist()],
			'sim_ref':0.,
			'sim_context':0.,
			'quality':0.
		}
	 

	# sup=[]
	# for row_index in range(len(data)):
	# 	row_attrs=data.iloc[[row_index]]
	# 	row_attrs_values=set([row_attrs[column].tolist()[0] for column in row_attrs])
	# 	print(row_attrs_values,selector)
	# 	input()
	# 	if set(selector) in row_attrs_values:
	# 		sup.append(row_index)
	# print(len(sup))
	return sup,record

data = pd.read_csv(sys.argv[1],sep='\t')
all_columns=[]
for column in data.iloc[[0]]:
	all_columns.append(column)
#print(all_columns)
#input('....')

#print(set([data.iloc[[0]][column].tolist()[0] for column in data.iloc[[0]]]))
target = ps.NominalTarget ('EQ_VOTE', '-')
# searchspace = ps.createSelectors(data, ignore=['EQ_VOTE'])
# task = ps.SubgroupDiscoveryTask (data,target,searchspace,resultSetSize=10,depth=2,qf=ps.WRAccQF())
# result = ps.BeamSearch().execute(task)


#target = ps.NominalTarget ('class', b'bad')
searchSpace = ps.createNominalSelectors(data, ignore=['EQ_VOTE','ide','idi','idi_1','idi_2'])
#task = ps.SubgroupDiscoveryTask (data, target, searchSpace, resultSetSize=10, depth=6, qf=ps.StandardQF(0.0))
all_columns=[]
for column in data.iloc[[0]]:
	all_columns.append(column)
if 'idi_1' not in all_columns: #'Majority stuffs'
	task = ps.SubgroupDiscoveryTask (data, target, searchSpace, depth=6,qf=ps.StandardQF(0.),resultSetSize=50)
	print( '---------------')
	print( 'EXHAUSTIVE PYSUBGROUP')
	print('---------------')
	result = ps.BSD().execute(task)

else: #Cartesian Product Stuff
	task = ps.SubgroupDiscoveryTask (data, target, searchSpace, depth=6,qf=ps.StandardQF(0.),resultSetSize=25)
	print( '---------------')
	print( 'EXHAUSTIVE PYSUBGROUP')
	print('---------------')
	result = ps.BSD().execute(task)
	# task = ps.SubgroupDiscoveryTask (data, target, searchSpace, depth=3,qf=ps.StandardQF(0.),resultSetSize=20)
	# print( '---------------')
	# print('BEAMSEARCH PYSUBGROUP')
	# print( '---------------')
	# result = ps.BeamSearch(beamWidth=20).execute(task)
print(len(data))
#result = ps.BeamSearch(beamWidth=50).execute(task)

toWrite=[]
for (q, sg) in result:
	#print (str(q) + ":\t" + str(sg.subgroupDescription))
	#print (sg.subgroupDescription.selectors[0])
	selector_values='&'.join([str(sg.subgroupDescription.selectors[x]).split('=')[0]+'=="'+str(sg.subgroupDescription.selectors[x]).split('=')[1]+'"' for x in range(len(sg.subgroupDescription.selectors))])
	#print(selector_values)
	#input()
	sup,record=compute_support(data,selector_values)
	# print (len(sup),[x for x,k in enumerate(sg.covers(data)) if k])
	# print(sup)
	#input()
	record['quality']=q
	#print(record)
	toWrite.append(record)
	#print (sg)





writeCSVwithHeader(toWrite,sys.argv[2],selectedHeader=['context','g_1','g_2','context_extent','g_1_extent','g_2_extent','sim_ref','sim_context','quality'],delimiter='\t',flagWriteHeader=True)

# print(result)
# raw_input('....')