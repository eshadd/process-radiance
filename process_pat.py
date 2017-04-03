#pylint: skip-file

import distill_rad_data

import csv
import sqlite3
import os

#INPUT

pat_path = 'C:/Test Lab/Fixed Slats 00 09/'
out_path = 'C:/Test Lab/Output/'
tdv_fref = 'C:/Test Lab/Input/2019 TDV Factors-V2-02.13.2017 - NRE30.csv'

run_d = ['90 WN 90 WN', '10 3.500 25 1.750', '10 2.500 25 1.500', '10 2.000 25 1.375', '10 1.750 25 1.250', '15 2.500 30 1.500', '15 2.000 30 1.375', '15 1.750 30 1.250', '15 1.500 30 1.125', '20 2.125 35 1.375', '20 1.750 35 1.250', '20 1.500 35 1.125', '20 1.375 35 1.050', '25 1.750 40 1.250', '25 1.500 40 1.125', '25 1.375 40 1.050', '25 1.250 40 1.000']
#run_d = ['90 CL 90 CL', '90 LL 90 LL']

shade_case_d = {
    'bad': {'threshold': 0.4, 'min_period': 21*24, 'check_times': [8], 'occ_hrs': [8, 17], \
        'shaded': 0, 'shaded_hrs': 0, 'tot_shaded_hrs': 0, \
        'unshd_run': 'NS', 'shd_run': 0.0}, 
    'good': {'threshold': 0.6, 'min_period': 1, 'check_times': [8, 12], 'occ_hrs': [8, 17], \
        'shaded': 0, 'shaded_hrs': 0, 'tot_shaded_hrs': 0, \
        'unshd_run': 'NS', 'shd_run': 'DS'}
    }

setpt_a = [100,  200, 300, 500, 750, 1000]

rad_dat_hdr = ['Weather', 'Case', 'Az', 'WWR', 'Bad Shade Hrs', 'Good Shade Hrs', 'Zone', 'Ctrl', 'Setpt', 'TDV']

pat_db = 'project.osp'

#SETUP

case_d = {tc: {'none': tc + ' NS', 'good': tc + ' DS'} for tc in run_d}

# Connect to the database file
pat_db_conn = sqlite3.connect(pat_path + pat_db)
pat_db_crsr = pat_db_conn.cursor()

pat_db_crsr.execute('SELECT name, directory FROM DataPointRecords')
#note inconsitency fix: some no shade cases had 'NS', some didn't
all_run_path_d = {rn if rn[-3]==' ' else rn + ' NS': rp for rn, rp in pat_db_crsr.fetchall()}
run_path_d = {case: {'none': all_run_path_d[runs['none']], 'good': all_run_path_d[runs['good']]} for case, runs in case_d.items()}

pat_db_crsr.execute('SELECT weatherFileReferenceRecordId FROM AnalysisRecords')
wthr_file_idx = pat_db_crsr.fetchone()[0]
pat_db_crsr.execute('SELECT displayName FROM FileReferenceRecords WHERE id = {wfi}'.format(wfi=wthr_file_idx))
wthr_fn = pat_db_crsr.fetchone()[0]

pat_db_conn.close()

results_by_shd = {}
for case, run_path_d in run_path_d.items():
    rad_dat = distill_rad_data.run_distillr(case, setpt_a, shade_case_d, run_path_d, pat_path, wthr_fn, tdv_fref)
    results_by_shd.setdefault(rad_dat[0], [rad_dat_hdr]).extend(rad_dat[1])

for cz, results in results_by_shd.items():
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    with open(out_path + format(cz, '02d') + '.csv', 'w', newline='') as f_w:
        csv.writer(f_w, dialect='excel').writerows(results)

