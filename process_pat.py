import distill_rad_data

import sqlite3
import os

pat_path = 'C:/Users/Suyeyasu/Desktop/05 to 01 Shades - Copy/'
pat_db = 'project.osp'

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

for run_name, run_path in run_path_a:
    run_idx = int(run_path.split('/')[-1].replace('dataPoint', ''))
    out_path = run_path + '/' + str(9 * (run_idx - 1)) + '-Userscript-0/radiance/output/'
    out_path = out_path.replace('C:/Determinant_J/Projects/T2419 CASE/Analysis', 'C:/Users/Suyeyasu/Desktop')
    if os.path.exists(out_path):
        rad_dat = distill_rad_data.run_distillr(wthr_fn, run_name, out_path)
pass

