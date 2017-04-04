#pylint: skip-file

import os
import csv

#INPUT

pat_path_a = ['C:/Test Lab/Clerestory 00 '+ format(cz,'02d') +'/' for cz in [4]]
out_path = out_path = 'C:/Test Lab/Output/'

merge_dir = 'C:/Test Lab/Output/'
merged_results_fn = 'merged_results.csv'

#SETUP

results_fn_a = [f for f in os.listdir(merge_dir) if f[-4:] == '.csv' and f != merged_results_fn]
rad_dat_hdr = ['Weather', 'Case', 'Az', 'WWR', 'Bad Shade Hrs', 'Good Shade Hrs', 'Zone', 'Ctrl', 'Setpt', 'TDV']

# MAIN

with open(merge_dir + merged_results_fn, 'w', newline='') as merged_results_fw:
    csv.writer(merged_results_fw, dialect='excel').writerow(rad_dat_hdr)
    for results_fn in results_fn_a:
        with open(merge_dir + results_fn) as result_fr:
            result_hr_g = csv.reader(result_fr)
            next(result_hr_g)
            for result_hr in result_hr_g:
                csv.writer(merged_results_fw, dialect='excel').writerow(result_hr)