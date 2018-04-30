pypy ..//..//..//DSC_Project//main.py ..//yelp.json -p performance_nb_reviewees.csv --algos DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --nb_obj 100 1000 10000 30000 80000 130000 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//yelp.json -p performance_nb_reviewers.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --nb_obj 25000 --nb_ind 3 7 13 18 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//yelp_nb_attr.json -p performance_nb_attr_desc_reviewees.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 1 2 --nb_attr_desc_ind 3 --nb_obj 25000 --nb_ind 20 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//yelp.json -p performance_nb_attr_desc_reviewers.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 2 --nb_attr_desc_ind 1 2 3 --nb_obj 25000 --nb_ind 20 --timebudget 36000 -v;

