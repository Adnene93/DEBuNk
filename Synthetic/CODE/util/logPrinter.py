'''
Created on 29 nov. 2016

@author: Adnene
'''


def printDataset(dictToPrint) :
    if dictToPrint :
        
        finalPrint='\n'
        header=dictToPrint[0].keys()
        pheader=''
        parr='\n'
        for key in header :
            pheader += str(key)+'\t'
        for obj in dictToPrint :
            prow=''
            for index in range(len(header)):
                prow+=str(obj[header[index]])+'\t'
            parr+=prow+'\n'
        finalPrint+=pheader+'\n'+parr+'\n'
    else :
        finalPrint='the dataset is empty'
    print finalPrint
    

def printMatrix(matrixToPrint) :
    toPrint='\n'
    for i in range(len(matrixToPrint)):
        for j in range(len(matrixToPrint[i])) :
            toPrint+=str(matrixToPrint[i][j]) +'\t'
        toPrint+='\n'
    print toPrint

def printDefault(data):
    print(data)

def breakWaitingForInput(data):
    raw_input('CLICK ANY BUTTON ...') 
    
POSSIBLE_PRINTER={
    'dataset' : printDataset,
    'matrix' : printMatrix,
    'default' : printDefault,
    'break' : breakWaitingForInput
}

def workflowStage_logPrinter(
        inputs={},
        configuration={},
        outputs={},
        workflow_stats={}
    ):
    
    '''
    {
    
        'id':'stage_id',
        'type':'log_printer',
        'inputs': {
            'data' :[]  
        },
        'configuration': {
           'printType':'default' # dataset | matrix
        },
        'outputs':{
        }
    }
    '''    
    
    
    localConfiguration={}
    localConfiguration['printType']=configuration.get('printType','default')
    
    typeOfPrint=(set([localConfiguration['printType']]) & set(POSSIBLE_PRINTER.keys())).pop()
    
    POSSIBLE_PRINTER[typeOfPrint](inputs['data'])
    
    return outputs
    