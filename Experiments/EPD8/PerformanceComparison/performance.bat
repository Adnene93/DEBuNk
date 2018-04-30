pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_reviewees.csv --algos DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 4 --nb_obj 100 250 500 1000 1500 2000 3000 4500 --nb_ind 500 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_reviewers.csv --algos DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 4 --nb_obj 2000 --nb_ind 50 100 250 500 1000 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//parliament2.json -p performance_nb_attr_desc_reviewees.csv --algos DSC DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 1 2 3 --nb_attr_desc_ind 4 --nb_obj 2000 --nb_ind 500 --timebudget 36000 -v;
pypy ..//..//..//DSC_Project//main.py ..//parliament.json -p performance_nb_attr_desc_reviewers.csv --algos DSC+CLOSED DSC+CLOSED+UB1 DSC+CLOSED+UB2 --nb_attr_desc_obj 10 --nb_attr_desc_ind 1 2 3 4 5 6 --nb_obj 2000 --nb_ind 500 --timebudget 36000 -v;


Pause