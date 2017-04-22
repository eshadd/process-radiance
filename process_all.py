#pylint: skip-file

import process_pat

import os
import csv

#INPUT

pat_path_stem = 'E:/Fixed Slats 00 '
out_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Test Lab/'
run_d = ['90 WN 90 WN']#, '10 3.500 25 1.750', '10 2.500 25 1.500', '10 2.000 25 1.375', '10 1.750 25 1.250', '15 2.500 30 1.500', '15 2.000 30 1.375', '15 1.750 30 1.250', '15 1.500 30 1.125', '20 2.125 35 1.375', '20 1.750 35 1.250', '20 1.500 35 1.125', '20 1.375 35 1.050', '25 1.750 40 1.250', '25 1.500 40 1.125', '25 1.375 40 1.050', '25 1.250 40 1.000']
merge_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Test Lab/'
merged_results_fn = 'merged_FS_results.csv'

# pat_path_stem = 'E:/Clerestory 00 '
# out_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Test Lab/'
# run_d = ['90 CL 90 CL', '90 LL 90 LL']
# merge_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Test Lab/'
# merged_results_fn = 'merged_CL_results.csv'

run_cz_a = [3, 4, 6, 7, 8, 9, 10, 12]

#SETUP

pat_path_a = [pat_path_stem + format(cz,'02d') +'/' for cz in run_cz_a]

rad_dat_hdr = ['Weather', 'Case', 'Az', 'WWR', 'Bad Shade Hrs', 'Good Shade Hrs', 'Zone', 'Ctrl', 'Setpt', 'TDV']

# MAIN

results_fn_a = []
for pat_path in pat_path_a:
    results_fn = process_pat.process_pat(pat_path, run_d, out_path)
    results_fn_a.append(results_fn)

with open(merge_dir + merged_results_fn, 'w', newline='') as merged_results_fw:
    csv.writer(merged_results_fw, dialect='excel').writerow(rad_dat_hdr)
    for results_fn in results_fn_a:
        with open(merge_dir + results_fn) as result_fr:
            result_hr_g = csv.reader(result_fr)
            next(result_hr_g)
            for result_hr in result_hr_g:
                csv.writer(merged_results_fw, dialect='excel').writerow(result_hr)