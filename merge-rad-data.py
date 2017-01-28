import json
import csv
import sqlite3

#INPUT

run_name = 'Test 16'

ill_json_fn = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/0-UserScript/radiance/output/radout.json'
#n_illmap_xgrid = 15
#n_illmap_ygrid = 10
ill_csv_fp = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/0-UserScript/radiance/output/'
spc_field = 'T2419_CASE_Spc'
bad_glare_field = 'Bad_Case_Glare_Sensor'
good_glare_field = 'Good_Case_Glare_Sensor'

sql = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/0-UserScript/radiance/sql/eplusout.sql'    
sql_tbl = 'ReportVariableWithTime '
sql_field = 'Value'
sql_filter_col = 'Name'
sql_filter_a = ['Site Solar Azimuth Angle', 'Site Solar Altitude Angle']

#SETUP

with open(ill_json_fn) as ill_f:
    ill_d = json.load(ill_f)
    ill_d = ill_d.pop('all_hours')

# Connect to the database file
sql_conn = sqlite3.connect(sql)
sql_crsr = sql_conn.cursor()

#MAIN

#get illuminance map and glare metrics by space
ill_dat = {}
illum_hdr = ['bad_dgp', 'bad_raw', 'good_dgp', 'good_raw', 'ill_map']
for hour_dat in ill_d:
    for spc_nm, spc_ill_dat in hour_dat.items():

        grid_ill_dat = spc_ill_dat[0]
        sensor_glare_dat = spc_ill_dat[2]
        
        bad_glare = sensor_glare_dat[bad_glare_field]
        good_glare = sensor_glare_dat[good_glare_field]
        
        #assumes only one view
        bad_glare_metrics = bad_glare[list(bad_glare.keys())[0]]
        good_glare_metrics = good_glare[list(good_glare.keys())[0]]

        hour_ill_dat = [bad_glare_metrics['dgp'], bad_glare_metrics['raw'], good_glare_metrics['dgp'], good_glare_metrics['raw']]
        hour_ill_dat.extend(grid_ill_dat)

        ill_dat.setdefault(spc_nm, []).append(hour_ill_dat)

#get solar position
solar_pos = []
for sql_filter in sql_filter_a:
    sql_crsr.execute('SELECT {fd} FROM {tn} WHERE {cn}="{ft}"'.format(fd=sql_field,tn=sql_tbl,cn=sql_filter_col,ft=sql_filter))
    solar_pos.append(sql_crsr.fetchall())

#reformat it
solar_pos = [[solar_pos[j][i][0] for j in range(len(solar_pos))] for i in range(len(solar_pos[0]))]

sql_conn.close()

#combine data ill_dat and all_dat ;)
rad_dat = {}
for spc_nm, spc_ill_dat in ill_dat.items():
    for hr, ill_dat in enumerate(spc_ill_dat):
        all_dat = [hr]
        all_dat.extend(solar_pos[hr])
        all_dat.extend(ill_dat)
        rad_dat.setdefault(spc_nm, []).append(all_dat)

#OUTPUT

#for rad_case_nm in rad_case_fields:
#    with open(rad_csv_fp+rad_case_nm.lower()+'.csv', 'w', newline='') as f_w:
#        csv.writer(f_w, dialect='excel').writerows(rad_cases_a_by_d[rad_case_nm])

