python ..//..//..//Debunk//DSC_Project//main.py .//yelp.json -q qualitative_results_choosed_new_sampling.csv --algos DSC+CLOSED+UB2 --sigma_obj 15 --sigma_ind 1 --sigma_qual 0.1 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --timebudget 90000 --verbose --edf --no_generality --first_run ;
python ..//..//..//Debunk//DSC_Project//main.py .//yelp.json -q qualitative_results_choosed_new_sampling.csv --algos DSC+SamplingPeers+RandomWalk --sigma_obj 15 --sigma_ind 1 --sigma_qual 0.1 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --timebudget 8000 --verbose --edf --no_generality  ;
python ..//..//..//Debunk//DSC_Project//main.py .//yelp.json -q qualitative_results_choosed_new_sampling.csv --algos DSC+SamplingPeers+RandomWalk --sigma_obj 15 --sigma_ind 1 --sigma_qual 0.1 --nb_attr_desc_obj 2 --nb_attr_desc_ind 3 --timebudget 8000 --verbose --edf --no_generality  --nrwc 0 ;
