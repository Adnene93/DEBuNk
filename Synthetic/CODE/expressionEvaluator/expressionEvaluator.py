'''
Created on 5 dec. 2016

@author: Adnene
'''

#from copy import deepcopy

from simpleeval import SimpleEval
import simpleeval
from bitarray import bitarray

def toArray(item):
    return [item]

def transformToArray(item):
    return list(item)

def transformToSet(item):
    return set(item)

def transformToBitwiseArray(array):
    return bitarray(array)

def mysorted(item):
    returned=sorted(item)
    return returned

def cover(arr_1,arr_2): #arr_1 and arr_2 are boolean array representing the elements of a set
    
    if arr_1 is None or arr_2 is None :
        return 0
    else :
        
        arr_1_inter_arr_2 = [x and y for x,y in zip(arr_1,arr_2)]
        arr2_count=arr_2.count(True)
        if arr2_count==0:
            return 0
        else :
            return float(arr_1_inter_arr_2.count(True)) / arr2_count

def intersection(set_1,set_2): #arr_1 and arr_2 are boolean array representing the elements of a set
    return set_1 & set_2


def union(set_1,set_2): #arr_1 and arr_2 are boolean array representing the elements of a set
    return set_1 | set_2



FUNCTIONS_MAP={
    'str':str,
    'len':len,
    'int':int,
    'float':float,
    'type':type,
    'list':toArray,
    'toArray':transformToArray,
    'toSet':transformToSet,
    'toBitarray':transformToBitwiseArray,
    'sorted':mysorted,
    'cover':cover,
    'max':max,
    'min':min,
    'intersection':intersection,
    'union':union
}




evaluator = SimpleEval(functions=FUNCTIONS_MAP)





def evaluateExpression(expression,record,workflow_stats={},others=None) : #data may be a simple record
    evalResults=None
    evaluator.names=record
    evaluator.names.update(workflow_stats)
    if others is not None:
        evaluator.names.update(others)
    try :
        try: #BRICOLAAAGE!
            int(expression)
            evalResults=expression    
            #evalResults=evaluator.eval(expression)
        except: #BRICOLAAAGE!
            evalResults=evaluator.eval(expression)
        
    except Exception:
        evalResults=expression
    
    
    
    return evalResults