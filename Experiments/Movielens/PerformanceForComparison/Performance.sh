pypy ..//..//..//DSC_Project//main.py ..//movielens.json -p performance_nb_reviewees.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --nb_obj 100 250 500 750 1000 1500 1750 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//movielens.json -p performance_nb_reviewers.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --nb_obj 2000 --nb_ind 100 250 500 750 1000 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//movielens.json -p performance_nb_attr_desc_reviewees.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 1 2 --nb_attr_desc_ind 3 --nb_obj 1750 --nb_ind 1000 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//movielens.json -p performance_nb_attr_desc_reviewers.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 2 --nb_attr_desc_ind 1 2 3 --nb_obj 1750 --nb_ind 1000 --timebudget 36000 -v;