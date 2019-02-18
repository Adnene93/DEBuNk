'''
Created on 14 nov. 2016

@author: Adnene
'''
from math import sqrt
import math


def getMatrixWithoutRower(matrix):
    ret = [[matrix[j][k] for k in range(1,len(matrix[0]))] for j in range(len(matrix))]
    return ret

def getMatrixWithRower(matrix,matrixSourceWithRower):
    ret = [[matrixSourceWithRower[j][0]]+[matrix[j][k] for k in range(len(matrix[0]))] for j in range(len(matrix))]
    return ret

def distanceMatrix(matrix1,matrix2): #same size 
    newMatrix1=getMatrixWithoutRower(matrix1)
    newMatrix2=getMatrixWithoutRower(matrix2)
    ret = [[(newMatrix1[j][k]-newMatrix2[j][k]) for k in range(len(newMatrix1[0]))] for j in range(len(newMatrix1))]
    ret = getMatrixWithRower(ret,matrix1) 
    return ret




def adaptSquareMatrices(matrix1,matrix2): #when the matrices aren't the same size (unique values on row(0)) keep the header
    if (len(matrix1)>len(matrix2)):
        mat1=[x[:] for x in matrix1]
        mat2=[x[:] for x in matrix2]
    else : 
        mat2=[x[:] for x in matrix1]
        mat1=[x[:] for x in matrix2]
    
    mapMatrix2 = [row[0] for row in iter(mat2)]    
    newMatrix1=[]
    newMatrix2=[]
    mapIndexToEP_ID=[]
    
    for row in iter(mat1):
        if row[0] in mapMatrix2 :
            mapIndexToEP_ID.append(row[0])
    
    for i in range(len(mat1)):
        if (mat1[i][0] in mapIndexToEP_ID)  : 
            newMatrix1.append([])
            newMatrix2.append([])
            rowid=mat1[i][0]
            iInMat2=mapMatrix2.index(rowid)
            for j in range(1,len(mat1[0])):
                if (mat1[j-1][0] in mapIndexToEP_ID):
                    jInMat2=mapMatrix2.index(mat1[j-1][0])+1
                    newMatrix1[len(newMatrix1)-1]=newMatrix1[len(newMatrix1)-1]+[mat1[i][j]]
                    newMatrix2[len(newMatrix2)-1]=newMatrix2[len(newMatrix2)-1]+[mat2[iInMat2][jInMat2]]
            newMatrix1[len(newMatrix1)-1].insert(0,mat1[i][0])
            newMatrix2[len(newMatrix2)-1].insert(0,mat2[iInMat2][0])           
    return newMatrix1,newMatrix2,mapIndexToEP_ID


def frobeniusNorm(matrix1,matrix2):
    distMat = getMatrixWithoutRower(distanceMatrix(matrix1,matrix2))
    squareFrobenius=sum([v**2 for v in [item for sublist in distMat for item in sublist]])
    squareFrobenius=sqrt(squareFrobenius)
    return squareFrobenius

def maximumNorm(matrix1,matrix2):
    distMat = getMatrixWithoutRower(distanceMatrix(matrix1,matrix2))
    maximumnorm=max([v for v in [item for sublist in distMat for item in sublist]])
    return maximumnorm

def maximumRowNorm(matrix1,matrix2):
    distMat = getMatrixWithoutRower(distanceMatrix(matrix1,matrix2))
    #maximumrownorm=min([sum(row) for row in iter(distMat)])
    maximumrownorm=max([(1.0/(len(row)-1))*sum([math.copysign(val,1) for val in row]) for row in iter(distMat)])
    return maximumrownorm
    #maximumrownorm=max([sum([math.copysign(val,1) for val in row]) for row in iter(distMat)])

# def adaptSquareMatrices2(matrix1,matrix2): #when the matrices aren't the same size (unique values on row(0)) keep the header
#     mapMatrix2 = [row[0] for row in iter(matrix2)]    
#     newMatrix1=[]
#     newMatrix2=[]
#     mapIndexToEP_ID=[]
#     
#     for row in iter(matrix1):
#         if row[0] in mapMatrix2 :
#             mapIndexToEP_ID.append(row[0])
#             
#     for i in range(len(matrix1)):
#         if (matrix1[i][0] in mapIndexToEP_ID)  : 
#             newMatrix1.append([])
#             for j in range(1,len(matrix1[0])):
#                 if (matrix1[j-1][0] in mapIndexToEP_ID):
#                     newMatrix1[len(newMatrix1)-1]=newMatrix1[len(newMatrix1)-1]+[matrix1[i][j]]
#             newMatrix1[len(newMatrix1)-1].insert(0,matrix1[i][0]) 
#                 
#     
#     for i in range(len(matrix2)):
#         if (matrix2[i][0] in mapIndexToEP_ID)  : 
#             newMatrix2.append([])
#             for j in range(1,len(matrix2[0])):
#                 if (matrix2[j-1][0] in mapIndexToEP_ID):
#                     newMatrix2[len(newMatrix2)-1]=newMatrix2[len(newMatrix2)-1]+[matrix2[i][j]]
#             newMatrix2[len(newMatrix2)-1].insert(0,matrix2[i][0]) 
#             
#     return newMatrix1,newMatrix2,mapIndexToEP_ID

