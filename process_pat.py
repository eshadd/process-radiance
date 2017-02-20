#pylint: skip-file

import distill_rad_data

import csv
import sqlite3
import os

#INPUT

pat_path = 'E:/05 to 01 Shades - 12/'
out_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Output/'
tdv_fref = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Input/2019 TDV Factors-V2-02.13.2017 - NRE30.csv'

setpt_a = [50,  200, 300, 500, 750, 1000]

shade_case_d = {
    'bad': {'threshold': 0.4, 'min_period': 21*24, 'check_times': [8], 'occ_hrs': [8, 17], 'shaded': 0, 'shaded_hrs': 0}, 
    'good': {'threshold': 0.6, 'min_period': 1, 'check_times': [8, 12], 'occ_hrs': [8, 17], 'shaded': 0, 'shaded_hrs': 0}
    }

rad_dat_hdr = ['Weather', 'Case', 'Shade', 'Az', 'WWR', 'Ann Hr', 'Day Type', \
    'Month', 'Day', 'Hr', 'Sensor', 'DGP', 'Bad Shaded?', 'Good Shaded?', '1ry Daylt', '2ry Daylt', 'TDV']

pat_db = 'project.osp'

#SETUP

case_hdr_a = []
for shade_case in (' b', ' g'):
    for zn in ['1 ', '2 ']:
        for ctrl in ['Dim', 'Multi', 'Bi']:
            case_hdr_a.extend([str(sp) + shade_case + zn + ctrl for sp in setpt_a])

# Connect to the database file
pat_db_conn = sqlite3.connect(pat_path + pat_db)
pat_db_crsr = pat_db_conn.cursor()

pat_db_crsr.execute('SELECT name, directory FROM DataPointRecords')
run_path_a = pat_db_crsr.fetchall()

pat_db_crsr.execute('SELECT weatherFileReferenceRecordId FROM AnalysisRecords')
wthr_file_idx = pat_db_crsr.fetchone()[0]
pat_db_crsr.execute('SELECT displayName FROM FileReferenceRecords WHERE id = {wfi}'.format(wfi=wthr_file_idx))
wthr_fn = pat_db_crsr.fetchone()[0]

pat_db_conn.close()

results_by_shd = {}
for run_name, run_path in run_path_a:
    dat_pt = run_path.split('/')[-1]
    run_idx = int(dat_pt.replace('dataPoint', ''))
    rad_out_path = pat_path + dat_pt + '/' + str(9 * (run_idx - 1)) + '-Userscript-0/radiance/output/'
    if os.path.exists(rad_out_path):
        rad_dat = distill_rad_data.run_distillr(run_name, setpt_a, shade_case_d, rad_out_path, wthr_fn, tdv_fref)
        results_by_shd.setdefault(rad_dat[0], [rad_dat_hdr + case_hdr_a]).extend(rad_dat[1])

for wn_shd, results in results_by_shd.items():
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    with open(out_path + wn_shd + '.csv', 'w', newline='') as f_w:
        csv.writer(f_w, dialect='excel').writerows(results)

