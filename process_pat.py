#pylint: skip-file

import distill_rad_data

import csv
import sqlite3
import os

#INPUT

def process_pat(pat_path, run_a, sensor_grid_d, out_path):

    tdv_fref = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Input/2019 TDV Factors-V2-02.13.2017 - NRE30.csv'

    #TEMP
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

    case_d = {tc: {'none': tc + ' NS', 'good': tc + ' DS'} for tc in run_a}

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
        rad_dat = distill_rad_data.run_distillr(case, setpt_a, sensor_grid_d, shade_case_d, run_path_d, pat_path, wthr_fn, tdv_fref)
        results_by_shd.setdefault(rad_dat[0], [rad_dat_hdr]).extend(rad_dat[1])

    for cz, results in results_by_shd.items():
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        results_fn = format(cz, '02d') + '.csv'
        with open(out_path + results_fn, 'w', newline='') as f_w:
            csv.writer(f_w, dialect='excel').writerows(results)
            
    return results_fn

