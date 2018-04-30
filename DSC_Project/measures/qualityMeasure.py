'''
Created on 3 fevr. 2017

@author: Adnene
'''
from itertools import izip
from math import isnan, copysign, sqrt




def quality_norm_eloignement(original_model,pattern_model,threshold_pair_comparaison,ret_ub_array=False):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
 
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            if all_p>=threshold_pair_comparaison:
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                min_sim_expected=agg_min/threshold_pair_comparaison
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)**2
                
        qpsmax_per_row_append(qpsmax_of_actual_row)
        
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)    
        

    quality=sqrt(sum(x**2 for x in qps))#/float(nb_users_voted)
    
    borne_max_quality=sqrt(sum(qpsmax_per_row))#/float(nb_users_voted)

    
    
    if not ret_ub_array :
        return quality,borne_max_quality
    else :
        return quality,borne_max_quality,qpsmax_per_row


def quality_norm_rapprochement(original_model,pattern_model,threshold_pair_comparaison):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    
    flat_matrix_general=[x for row in original_model for x in row]
    flat_matrix_pattern=[x for row in pattern_model for x in row]
    
    for (agg_o,all_o),(agg_p,all_p) in izip(flat_matrix_general,flat_matrix_pattern)  :
        if all_p>=threshold_pair_comparaison:    
            agg_max=float(min(agg_p,threshold_pair_comparaison))
            qp=max((agg_p/all_p)-(agg_o/all_o),0)
            max_sim_expected=agg_max/threshold_pair_comparaison
            diff_p_max_expected=max(max_sim_expected-(agg_o/all_o),0)
            qps_append(copysign(qp,1))
            qps_max_append(copysign(diff_p_max_expected,1))
            
    quality=sqrt(sum(x**2 for x in qps))#/float(nb_users_voted)
    borne_max_quality=sqrt(sum(x**2 for x in qps_max))#/float(nb_users_voted)
    
    return quality,borne_max_quality

def quality_correlation_eloignement(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted):
    
    flat_matrix_general=[x for row in original_model for x in row]
    flat_matrix_pattern=[x for row in pattern_model for x in row]
    
    norm_flat_matrix_general=sqrt(sum([(agg_o/all_o)**2 for (agg_o,all_o) in flat_matrix_general]))
    norm_flat_matrix_pattern=sqrt(sum([(agg_p/all_p)**2 for (agg_p,all_p) in flat_matrix_pattern]))
    scalarProduct=sum((agg_o/all_o)*(agg_p/all_p) if all_p>=threshold_pair_comparaison else 0 for (agg_o,all_o),(agg_p,all_p) in zip(flat_matrix_general,flat_matrix_pattern))
    
                
    quality=1-(scalarProduct/(norm_flat_matrix_general*norm_flat_matrix_pattern))
    #print quality
    borne_max_quality=1.
    return quality,borne_max_quality



def quality_mepwise_eloignement(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    
    qps_row=[];qps_row_append=qps_row.append
    qps_max_row=[];qps_max_row_append=qps_max_row.append
    for row_o,row_p in izip(original_model,pattern_model):
        qps_row_append([]);qps_row_actual_append=qps_row[-1].append
        qps_max_row_append([]);qps_max_row_actual_append=qps_max_row[-1].append
        
        for (agg_o,all_o),(agg_p,all_p) in zip(row_o,row_p):
            if all_p>=threshold_pair_comparaison:    
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                min_sim_expected=agg_min/threshold_pair_comparaison
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_row_actual_append(copysign(qp,1))
                qps_max_row_actual_append(copysign(diff_p_max_expected,1))
        
        qps_row[-1]=sum(x for x in qps_row[-1])/(float(nb_users_voted)/2)
        qps_max_row[-1]=sum(x for x in qps_max_row[-1])/(float(nb_users_voted)/2)
    
    quality=max(qps_row)
    borne_max_quality=max(qps_max_row)
    
    return quality,borne_max_quality

def quality_peer_eloignement(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    
    flat_matrix_general=[x for row in original_model for x in row]
    flat_matrix_pattern=[x for row in pattern_model for x in row]
    
    for (agg_o,all_o),(agg_p,all_p) in izip(flat_matrix_general,flat_matrix_pattern)  :
        if all_p>=threshold_pair_comparaison:    
            agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
            qp=max((agg_o/all_o)-(agg_p/all_p),0)
            min_sim_expected=agg_min/threshold_pair_comparaison
            diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
            qps_append(copysign(qp,1))
            qps_max_append(copysign(diff_p_max_expected,1))
                
    quality=max(qps)
    borne_max_quality=max(qps_max)
    
    return quality,borne_max_quality


def quality_norm_eloignement_new(original_model,pattern_model,threshold_pair_comparaison,nb_users_voted,bound_model=[]):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    
    flat_matrix_general=[x for row in original_model for x in row]
    flat_matrix_pattern=[x for row in pattern_model for x in row]
    flat_matrix_bounds=[x for row in bound_model for x in row]
    
    for (agg_o,all_o),(agg_p,all_p),min_sim_expected in izip(flat_matrix_general,flat_matrix_pattern,flat_matrix_bounds)  :
        if all_p>=threshold_pair_comparaison:    
            #agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
            qp=max((agg_o/all_o)-(agg_p/all_p),0)
            #min_sim_expected=agg_min/threshold_pair_comparaison
            diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
            qps_append(copysign(qp,1))
            qps_max_append(copysign(diff_p_max_expected,1))
    quality=sqrt(sum(x**2 for x in qps))/float(nb_users_voted)
    borne_max_quality=sqrt(sum(x**2 for x in qps_max))/float(nb_users_voted)
    #quality=sum(qps)/float(nb_users_voted)
    #borne_max_quality=sum(qps_max)/float(nb_users_voted)
    return quality,borne_max_quality




####################################COEFFICIENTS########################################

# def coeff_fix_nbvoters_frobenius(qpsmax_per_row,nb_alluser1,nb_alluser2):
#     ub = 
    


####################################COEFFICIENTS########################################


def quality_disagreement_frobenius(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(nb_rows):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(nb_column):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            if all_p>=threshold_pair_comparaison:
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                min_sim_expected=agg_min/threshold_pair_comparaison
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)**2
                
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)  
    qpsmax_per_row=[sqrt(sum(qpsmax_per_row[:i])) for i in range(1,nb_rows+1)]
    quality=sqrt(sum(x**2 for x in qps))*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    return quality,borne_max_quality



def quality_disagreement_frobenius_u1_u2(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    ub_matrix=[];ub_matrix_append=ub_matrix.append
    
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    
    
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(nb_rows):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        ub_matrix_append([]);ub_matrix_actual_row_append=ub_matrix[-1].append
        qpsmax_of_actual_row=0.
        for j in range(nb_column):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            diff_p_max_expected=0
            if all_p>=threshold_pair_comparaison:
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                min_sim_expected=agg_min/threshold_pair_comparaison
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1)**2)
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)**2
            
            ub_matrix_actual_row_append(diff_p_max_expected**2)
                
        qpsmax_per_row_append((i,qpsmax_of_actual_row))
        
    
    
        
    
    
    qpsmax_per_column=[(j,sum(ub_matrix[k][j] for k in range(nb_rows))) for j in range(nb_column)]   
    
    qpsmax_per_column = sorted(qpsmax_per_column,key=lambda x : x[1],reverse=True) 
    qpsmax_per_row    = sorted(qpsmax_per_row,key=lambda x : x[1],reverse=True) 
    
    columns_sorted_mapping=[x[0] for x in qpsmax_per_column]
    rows_sorted_mapping=[x[0] for x in qpsmax_per_row]
    
#     print [[ub_matrix[rows_sorted_mapping[i]][columns_sorted_mapping[j]] for j in range(nb_column)] for i in range(nb_rows)]
#     raw_input('...')
    
    ub_matrix_new=[ub_matrix[i][j] for i in range(nb_rows) for j in range(nb_column)]
    ub_matrix_new=sorted(ub_matrix_new, reverse = True)
    ub_matrix_new=[[ub_matrix_new[i+j] for j in range(nb_column)] for i in range(nb_rows)]
    
    #qpsmax_per_row=[sqrt(sum(qpsmax_per_row[:i])) for i in range(1,nb_rows+1)]
    quality=sqrt(sum(x**2 for x in qps))*coeff(nb_rows,nb_column)
    borne_max_quality=sqrt(sum(x for x in qps_max))
    SUMS=[[coeff(i+1,j+1)*sqrt(sum([ub_matrix[rows_sorted_mapping[k1]][columns_sorted_mapping[k2]] for k1 in range(i+1) for k2 in range(j+1)])) for j in range(nb_column)] for i in range(nb_rows)]
    #SUMS=[[coeff(i+1,j+1)*sqrt(sum([ub_matrix_new[k1][k2] for k1 in range(i+1) for k2 in range(j+1)])) for j in range(nb_column)] for i in range(nb_rows)]
    
    
    borne_max_quality=max(max(SUMS[i]) for i in range(nb_rows)) if nb_rows>0 and nb_column>0 else 0 
    
    #borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    return quality,borne_max_quality


def quality_agreement_frobenius_u1_u2(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    #qps_max=[]
    ub_matrix=[];ub_matrix_append=ub_matrix.append
    
    qps_append=qps.append
    #qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    
    
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(nb_rows):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        ub_matrix_append([]);ub_matrix_actual_row_append=ub_matrix[-1].append
        qpsmax_of_actual_row=0.
        for j in range(nb_column):            
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            diff_p_max_expected=0
            if all_p>=threshold_pair_comparaison:
                agg_max=float(min(agg_p,threshold_pair_comparaison))
                qp=max((agg_p/all_p)-(agg_o/all_o),0)
                max_sim_expected=agg_max/threshold_pair_comparaison
                diff_p_max_expected=max(max_sim_expected-(agg_o/all_o),0)
                qps_append(copysign(qp,1))
                #qps_max_append(copysign(diff_p_max_expected,1)**2)
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)**2
            
            ub_matrix_actual_row_append(diff_p_max_expected**2)
                
        qpsmax_per_row_append((i,qpsmax_of_actual_row))
        
    
    
        
    
    
    qpsmax_per_column=[(j,sum(ub_matrix[k][j] for k in range(nb_rows))) for j in range(nb_column)]   
    
    qpsmax_per_column = sorted(qpsmax_per_column,key=lambda x : x[1],reverse=True) 
    qpsmax_per_row    = sorted(qpsmax_per_row,key=lambda x : x[1],reverse=True) 
    
    columns_sorted_mapping=[x[0] for x in qpsmax_per_column]
    rows_sorted_mapping=[x[0] for x in qpsmax_per_row]
    
#     print [[ub_matrix[rows_sorted_mapping[i]][columns_sorted_mapping[j]] for j in range(nb_column)] for i in range(nb_rows)]
#     raw_input('...')
    
    ub_matrix_new=[ub_matrix[i][j] for i in range(nb_rows) for j in range(nb_column)]
    ub_matrix_new=sorted(ub_matrix_new, reverse = True)
    ub_matrix_new=[[ub_matrix_new[i+j] for j in range(nb_column)] for i in range(nb_rows)]
    
    #qpsmax_per_row=[sqrt(sum(qpsmax_per_row[:i])) for i in range(1,nb_rows+1)]
    quality=sqrt(sum(x**2 for x in qps))*coeff(nb_rows,nb_column)
    #borne_max_quality=sqrt(sum(x for x in qps_max))
    SUMS=[[coeff(i+1,j+1)*sqrt(sum([ub_matrix[rows_sorted_mapping[k1]][columns_sorted_mapping[k2]] for k1 in range(i+1) for k2 in range(j+1)])) for j in range(nb_column)] for i in range(nb_rows)]
    #SUMS=[[coeff(i+1,j+1)*sqrt(sum([ub_matrix_new[k1][k2] for k1 in range(i+1) for k2 in range(j+1)])) for j in range(nb_column)] for i in range(nb_rows)]
    borne_max_quality=max(max(SUMS[i]) for i in range(nb_rows))
    
    #borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    return quality,borne_max_quality

def quality_disagreement_sumdifferences(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            
            if all_p>=threshold_pair_comparaison:
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                min_sim_expected=agg_min/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
        
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
    quality=sum(qps)*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])

    return quality,borne_max_quality 

def quality_disagreement_sumdifferences_withbound(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1,ponderations_items={}):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p,min_sim_expected=row_pattern[j] if len(row_pattern[j])==3 else list(row_pattern[j])+[0.]
            
            
            if all_p>=threshold_pair_comparaison and all_o>=threshold_pair_comparaison:
                #agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                #min_sim_expected=agg_min/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
        
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
#     qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
#     qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
#     borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    borne_max_quality=sum(qps_max)*coeff(nb_rows)
    quality=sum(qps)*coeff(nb_rows)
    
    return quality,borne_max_quality 



def quality_disagreement_sumdifferences_withbound_new(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1,ponderations_items={}):
    agg_o,all_o=original_model[0][0]
    agg_p,all_p,min_sim_expected=pattern_model[0][0] if len(pattern_model[0][0])==3 else list(pattern_model[0][0])+[0.]
    borne_max_quality=max((agg_o/all_o)-min_sim_expected,0)
    quality=max((agg_o/all_o)-(agg_p/all_p),0)
    return quality,borne_max_quality 


def quality_agreement_sumdifferences_withbound_new(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1,ponderations_items={}):
    agg_o,all_o=original_model[0][0]
    agg_p,all_p,max_sim_expected=pattern_model[0][0] if len(pattern_model[0][0])==3 else list(pattern_model[0][0])+[1.]
    borne_max_quality=max(max_sim_expected-(agg_o/all_o),0)
    quality=max((agg_p/all_p)-(agg_o/all_o),0)
    return quality,borne_max_quality 

def quality_ratio_withbound_new(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1,ponderations_items={}):
    agg_o,all_o=original_model[0][0]
    agg_p,all_p,max_sim_expected=pattern_model[0][0] if len(pattern_model[0][0])==3 else list(pattern_model[0][0])+[1.]
    borne_max_quality=(max_sim_expected/(agg_o/all_o))#max(max_sim_expected-(agg_o/all_o),0)
    quality=((agg_p/all_p)/(agg_o/all_o))
    return quality,borne_max_quality 

def quality_disagreement_sumdifferences_withoutbound(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    #qps_max_append=qps_max.append
    #qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        #qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            
            if all_p>=threshold_pair_comparaison:
                #agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                #min_sim_expected=agg_min/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                #diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps_append(copysign(qp,1))
                #qps_max_append(copysign(diff_p_max_expected,1))
                #qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
        
        #qpsmax_per_row_append(qpsmax_of_actual_row)
    
    #qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    #qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
    quality=sum(qps)*coeff(nb_rows)
    #borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    borne_max_quality=quality
    return quality,borne_max_quality 


def quality_disagreement_maxdifferences_withbound(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=0.
    qps_max=0.
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p,min_sim_expected=row_pattern[j] if len(row_pattern[j])==3 else row_pattern[j]+[0.]
            
            
            if all_p>=threshold_pair_comparaison:
                #agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                
                #min_sim_expected=agg_min/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                qps=max(qps,copysign(qp,1))
                qps_max=max(qps_max,copysign(diff_p_max_expected,1))
                #qps_max_append(copysign(diff_p_max_expected,1))
                #qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
                #qps_max_append(copysign(diff_p_max_expected,1))
        
        #qpsmax_per_row_append(qpsmax_of_actual_row)
    
    #qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    #qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
#     quality=sum(qps)*coeff(nb_rows)
#     borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])

    return qps,qps_max 


def quality_agreement_sumdifferences_withbound(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1,ponderations_items={}):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p,max_sim_expected=row_pattern[j] if len(row_pattern[j])==3 else list(row_pattern[j])+[1.]
            
            
            if all_p>=threshold_pair_comparaison and all_o>=threshold_pair_comparaison:
                #agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_p/all_p)-(agg_o/all_o),0)#max((agg_o/all_o)-(agg_p/all_p),0) 
                #min_sim_expected=agg_min/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                #print max_sim_expected, (agg_p/all_p)
                diff_p_max_expected=max(max_sim_expected-(agg_o/all_o),0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
        
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
    quality=sum(qps)*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])

    return quality,borne_max_quality 




def quality_agreement_sumdifferences_withoutbound(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            
            if all_p>=threshold_pair_comparaison:
                #agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_p/all_p)-(agg_o/all_o),0)#max((agg_o/all_o)-(agg_p/all_p),0) 
                #min_sim_expected=agg_min/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                #print max_sim_expected, (agg_p/all_p)
                qps_append(copysign(qp,1))
        
         

    quality=sum(qps)*coeff(nb_rows)
    borne_max_quality=quality

    return quality,borne_max_quality
    

def quality_agreement_frobenius(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(nb_rows):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(nb_column):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            if all_p>=threshold_pair_comparaison:    
                agg_max=float(min(agg_p,threshold_pair_comparaison))
                qp=max((agg_p/all_p)-(agg_o/all_o),0)
                max_sim_expected=agg_max/threshold_pair_comparaison
                diff_p_max_expected=max(max_sim_expected-(agg_o/all_o),0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)**2
                
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)  
    qpsmax_per_row=[sqrt(sum(qpsmax_per_row[:i])) for i in range(1,nb_rows+1)]
    quality=sqrt(sum(x**2 for x in qps))*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    return quality,borne_max_quality


def quality_agreement_sumdifferences(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(nb_rows):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(nb_column):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            if all_p>=threshold_pair_comparaison:    
                agg_max=float(min(agg_p,threshold_pair_comparaison))
                qp=max((agg_p/all_p)-(agg_o/all_o),0)
                max_sim_expected=agg_max/threshold_pair_comparaison
                diff_p_max_expected=max(max_sim_expected-(agg_o/all_o),0)
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
                
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
    quality=sum(qps)*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])
    return quality,borne_max_quality



def quality_disagreement_sumdifferences_new(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1,minsim_model=[]):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    #interesting_keys=dict(vector_sumvotes[:15]).viewkeys()
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            
            if all_p>=threshold_pair_comparaison:
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                qp=max((agg_o/all_o)-(agg_p/all_p),0)
                
                
                #min_sim_expected=agg_min/threshold_pair_comparaison
                
                
                min_sim_expected=float(minsim_model[i][j])
                
                if (agg_o/all_o)-min_sim_expected<=0:
                    min_sim_expected=agg_min/threshold_pair_comparaison 
                
                diff_p_max_expected=max((agg_o/all_o)-min_sim_expected,0)
                
                
                
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
        
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
    quality=sum(qps)*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])

    return quality,borne_max_quality 


def quality_deviation_sumdifferences(original_model,pattern_model,threshold_pair_comparaison,coeff=lambda x : 1):
    qps=[]
    qps_max=[]
    qps_append=qps.append
    qps_max_append=qps_max.append
    qpsmax_per_row=[];qpsmax_per_row_append=qpsmax_per_row.append
    nb_rows=len(original_model)
    nb_column=len(original_model[0])
    
    for i in range(len(original_model)):
        row_original=original_model[i]
        row_pattern=pattern_model[i]
        qpsmax_of_actual_row=0.
        for j in range(len(row_original)):
            agg_o,all_o=row_original[j]
            agg_p,all_p=row_pattern[j]
            
            
            if all_p>=threshold_pair_comparaison:
                agg_min=(threshold_pair_comparaison-float(min(all_p-agg_p,threshold_pair_comparaison)))
                agg_max=float(min(agg_p,threshold_pair_comparaison))
                qp=copysign((agg_o/all_o)-(agg_p/all_p),1)
                min_sim_expected=agg_min/threshold_pair_comparaison
                max_sim_expected=agg_max/threshold_pair_comparaison
                #min_sim_expected=float(ubs_model[i][j])/(threshold_pair_comparaison)
                diff_p_max_expected_1=copysign((agg_o/all_o)-min_sim_expected,1)
                diff_p_max_expected_2=copysign((agg_o/all_o)-max_sim_expected,1)
                diff_p_max_expected=max(diff_p_max_expected_1,diff_p_max_expected_2)
                
                qps_append(copysign(qp,1))
                qps_max_append(copysign(diff_p_max_expected,1))
                qpsmax_of_actual_row+=copysign(diff_p_max_expected,1)
        
        qpsmax_per_row_append(qpsmax_of_actual_row)
    
    qpsmax_per_row=sorted(qpsmax_per_row,reverse=True)      
    qpsmax_per_row=[sum(qpsmax_per_row[:i]) for i in range(1,nb_rows+1)] 
    quality=sum(qps)*coeff(nb_rows)
    borne_max_quality=max([coeff(nb_voter)*qpsmax_per_row[nb_voter-1] for nb_voter in range(1,nb_rows+1)])

    return quality,borne_max_quality 

QUALITIES_DICTIONNARY={
    'DISAGR_FROBENIUS':quality_disagreement_frobenius,
    'DISAGR_FROBENIUS_U1_U2':quality_disagreement_frobenius_u1_u2,
    'AGR_FROBENIUS_U1_U2':quality_agreement_frobenius_u1_u2,
    'DISAGR_SUMDIFF':quality_disagreement_sumdifferences_withbound_new,
    'DISAGR_SUMDIFF_NUB':quality_disagreement_sumdifferences_withoutbound,
    'AGR_FROBENIUS':quality_agreement_frobenius,
    'AGR_SUMDIFF':quality_agreement_sumdifferences_withbound_new,
    'AGR_SUMDIFF_NUB':quality_agreement_sumdifferences_withoutbound,
    'DISAGR_MAXDIFF':quality_disagreement_maxdifferences_withbound,
    'DEVIATION_SUMDIFF':quality_deviation_sumdifferences,
    'RATIO':quality_ratio_withbound_new,
}

def compute_quality_and_upperbound(original_model,pattern_model,threshold_pair_comparaison,quality_measure,coeff=lambda x : 1,minsim_model=[]):
    return QUALITIES_DICTIONNARY[quality_measure](original_model,pattern_model,threshold_pair_comparaison,coeff)
    
    