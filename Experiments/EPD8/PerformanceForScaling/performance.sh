pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_entities.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 100 250 500 1000 1500 2000 3000 4500 --nb_ind 1000 --nb_items_desc_ind 500 --nb_items_desc_obj 500 --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_individuals.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 6 --nb_obj 4500 --nb_ind 50 100 250 500 1000 --nb_items_desc_ind 500 --nb_items_desc_obj 500 --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_items_entities.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 4500 --nb_ind 1000 --nb_items_desc_ind 500 --nb_items_desc_obj 50 100 150 200 250 500  --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_items_individuals.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 4500 --nb_ind 1000  --nb_items_desc_ind 25 50 100 150 200 250 --nb_items_desc_obj 500 --timebudget 36000 -v ;

pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_sigma_entities.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 4500 --nb_ind 1000  --nb_items_desc_ind 500 --nb_items_desc_obj 500 --sigma_obj 10 25 50 100 200 500 --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_sigma_individuals.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 4500 --nb_ind 1000  --nb_items_desc_ind 500 --nb_items_desc_obj 500 --sigma_ind 10 25 50 100 200 250 --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_sigma_varphi_dissent_NEW.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 4500 --nb_ind 1000  --nb_items_desc_ind 500 --nb_items_desc_obj 500 --sigma_qual 0.5 0.6 0.7 0.8 0.9 0.95 --quality_measure DISAGR_SUMDIFF --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_sigma_varphi_consent_NEW.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 10 --nb_obj 4500 --nb_ind 1000  --nb_items_desc_ind 500 --nb_items_desc_obj 500 --sigma_qual 0.25 0.35 0.5 0.7 0.8 0.9 0.95 --quality_measure AGR_SUMDIFF --timebudget 36000 -v ;




