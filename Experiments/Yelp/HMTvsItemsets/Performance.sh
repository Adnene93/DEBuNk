pypy ..//..//..//DSC_Project//main.py ./yelp.json -p performance_HMT.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 1 --nb_attr_desc_ind 3  --nb_items_desc_obj 50 100 150 200 300 400 600 800 1000 1200 --sigma_obj 5 --sigma_ind 1 --sigma_qual 0.5 --timebudget 36000 -v ;
pypy ..//..//..//DSC_Project//main.py ./yelp.json -p performance_ITEMSET.csv --algos DSC+CLOSED+UB2 --nb_attr_desc_obj 1 --nb_attr_desc_ind 3  --nb_items_desc_obj 50 100 150 200 300 400 600 800 1000 1200 --sigma_obj 5 --sigma_ind 1 --sigma_qual 0.5 --timebudget 36000 --hmt_to_itemset -v ;