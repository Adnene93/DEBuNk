python ..//..//..//DSC_Project//main.py performance_nb_entities.csv -f --x_axis_attribute nb_objects --fig_algos DSC+CLOSED+UB2 
python ..//..//..//DSC_Project//main.py performance_nb_individuals.csv -f --x_axis_attribute nb_users --fig_algos DSC+CLOSED+UB2 
python ..//..//..//DSC_Project//main.py performance_nb_items_entities.csv -f --x_axis_attribute nb_attrs_objects_in_itemset --fig_algos DSC+CLOSED+UB2 
python ..//..//..//DSC_Project//main.py performance_nb_items_individuals.csv -f --x_axis_attribute nb_attrs_users_in_itemset --fig_algos DSC+CLOSED+UB2 

python ..//..//..//DSC_Project//main.py performance_sigma_entities.csv -f --x_axis_attribute threshold_objects --fig_algos DSC+CLOSED+UB2 
python ..//..//..//DSC_Project//main.py performance_sigma_individuals.csv -f --x_axis_attribute threshold_nb_users_1 --fig_algos DSC+CLOSED+UB2 
python ..//..//..//DSC_Project//main.py performance_sigma_varphi_consent.csv -f --x_axis_attribute CONSENTquality_threshold --fig_algos DSC+CLOSED+UB2 
python ..//..//..//DSC_Project//main.py performance_sigma_varphi_dissent.csv -f --x_axis_attribute quality_threshold --fig_algos DSC+CLOSED+UB2 



Pause