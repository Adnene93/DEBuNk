'''
Created on 25 nov. 2016

@author: Adnene
'''


import cx_Oracle
import timeit
#service name

CONNECTIONSTRING='c##parltrack/mdppt16@134.214.143.94:1521/contentcheck_db_pdorcl'


def call_procedure(procedure_name,procedure_parameters):
    '''
    @note procedure_parameters:   the procedure parameters must be an array containing the attributes in an ordered fashion
    @note example : ['EXPORT_DIR_PARLTRACK','fromPython.csv','5','01/01/1000','01/01/9999']
    '''
    con = cx_Oracle.connect(CONNECTIONSTRING)
    cur = con.cursor()
    cur.callproc(procedure_name, procedure_parameters)
    cur.close()
    con.close()  


def call_function_table_iter(function_name,function_parameters):
    con = cx_Oracle.connect(CONNECTIONSTRING)
    cur = con.cursor()
    function_string = function_name+'('
    for param in function_parameters:
        function_string+=param+','
    function_string=function_string[:-1]
    function_string+=')'
    cur.execute('select * from table('+function_string+')')
    header = [desc[0] for desc in cur.description]
    for row in cur : 
        obj = {k:v for k,v in zip(header,row)}
        yield obj
    cur.close()
    con.close()  
    
def call_function_table(function_name,function_parameters): #add projection
    dataset=[]
    con = cx_Oracle.connect(CONNECTIONSTRING)
    cur = con.cursor()
    function_string = function_name+'('
    for param in function_parameters:
        if type(param) is str :
            function_string+="'"+param+"'"+','
        else :    
            function_string+=str(param)+','
        
    function_string=function_string[:-1]
    function_string+=')'
    #zprint('select * from table('+function_string+')')
    cur.execute('select * from table('+function_string+')')
    header = [desc[0] for desc in cur.description]
    for row in cur : 
        obj = {k:v for k,v in zip(header,row)}
        dataset.append(obj)
    cur.close()
    con.close()
    return dataset,header

def get_dossierid_of_theme(mandat,theme):
    iter_dossiers = call_function_table_iter('get_dossiers_of_theme_mandat_'+str(mandat),[theme])
    dossiers_ids=[]
    for row in iter_dossiers : 
        dossiers_ids.append(row['DOSSIER_ID'])
    return dossiers_ids

def get_stats_of_theme(mandat,theme):
    iter_dossiers = call_function_table_iter('get_stats_by_theme_of_mandat_'+str(mandat),[theme])
    stats=[]
    for row in iter_dossiers : 
        stats.append(row)
    return stats


#################################################################################### 
###############################WorkflowStages####################################### 
#################################################################################### 

def workflowStage_parltrack_database( #iterator  for a repository
    inputs={},
    configuration={},
    outputs={},
    workflow_stats={}
    ) :
    
    '''
    {
    
        'id':'stage_id',
        'type':'parltrack_database',
        'inputs': {
            'functionName': 'name of stored function',
            'parameters' : [] #orderer array of parameters (the same order as declared in the stored function/procedure in oracle)
            #functionName | procedureName
        },
        'configuration': {
            'projection':{
                'key':'expresion in function of attribute of records of dataset'
            }
        },
        'outputs':{
            'dataset':[], # the oracle stored function return a dataset anyway which is a list of dictionnaries 
            'header':[]
        }
    }
    '''
    
    
    localInputs={}
    localInputs['functionName'] = inputs.get('functionName',None)
    localInputs['procedureName'] = inputs.get('procedureName',None)
    localInputs['parameters']  = inputs.get('parameters',[])
    
    if localInputs['functionName'] :
        dataset,header = call_function_table(localInputs['functionName'], localInputs['parameters'])
        outputs['header']=header
        outputs['dataset']=dataset
    elif localInputs['procedureName'] :
        call_procedure(localInputs['procedureName'], localInputs['parameters'])
    return outputs

    
##Add useful functions were the dataset results must be in an array of dictionnaries