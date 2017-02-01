import json
import csv
import sqlite3

#INPUT

run_name = '090 180 270 SL NS NC NS 03'

ill_json_fn = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/1-UserScript-0/radiance/output/radout.json'
rad_csv_fp = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/Output/'
spc_field = 'T2419_CASE_Spc'

bad_glare_field = 'Bad_Glare_Snsr'
#good_glare_field = 'Good_Glare_Snsr'
bad_glare_threshold = 0.4
good_glare_threshold = 0.6
bad_min_shade_period = 21*24
good_min_shade_period = 1
bad_shade_check_times = [8]
good_shade_check_times = [8, 12]
bad_latest_adj_time = 17
good_latest_adj_time = 17

sql = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/1-UserScript-0/radiance/sql/eplusout.sql'    
sql_tbl = 'ReportVariableWithTime '
sql_field = 'Value'
sql_filter_col = 'Name'
sql_filter_a = ['Site Solar Azimuth Angle', 'Site Solar Altitude Angle', 'Site Sky Diffuse Solar Radiation Luminous Efficacy', 'Site Beam Solar Radiation Luminous Efficacy']
sql_time = 'TimeIndex, Month, Day, Hour, DayType'

#SETUP

with open(ill_json_fn) as ill_f:
    ill_d = json.load(ill_f)
    ill_d = ill_d.pop('all_hours')
    
#reformat so main loop can loop by space.
ill_fmtd_d = {}
for hour_dat in ill_d:
    for spc_nm, spc_ill_dat in hour_dat.items():
        ill_fmtd_d.setdefault(spc_nm, []).extend([spc_ill_dat[0], spc_ill_dat[2]])

# Connect to the database file
sql_conn = sqlite3.connect(sql)
sql_crsr = sql_conn.cursor()

#MAIN

#get solar data
solar = []
sql_crsr.execute('SELECT {tm} FROM {tn} WHERE {cn}="{ft}"'.format(tm=sql_time,tn=sql_tbl,cn=sql_filter_col,ft=sql_filter_a[0]))
solar.append(sql_crsr.fetchall())
for sql_filter in sql_filter_a:
    sql_crsr.execute('SELECT {fd} FROM {tn} WHERE {cn}="{ft}"'.format(fd=sql_field,tn=sql_tbl,cn=sql_filter_col,ft=sql_filter))
    solar.append(sql_crsr.fetchall())
sql_conn.close()

#get illuminance map and glare metrics by space
ill_dat = {}
for spc_nm, spc_ill_dat in hour_dat.items():

    bad_shaded_hrs = 0
    good_shaded_hrs = 0
    bad_shaded = 0
    good_shaded = 0
    for hr, hour_dat in enumerate(ill_fmt_d):

        grid_ill_dat = spc_ill_dat[0]
        sensor_glare_dat = spc_ill_dat[2]
        
        glare_field_a = list(sensor_glare_dat.keys())
        bad_glare_idx = glare_field_a.index([bs for bs in list(sensor_glare_dat.keys()) if bad_glare_field in bs][0])
        bad_glare = sensor_glare_dat[glare_field_a[bad_glare_idx]]
        good_glare = sensor_glare_dat[glare_field_a[int(not bad_glare_idx)]]
        
        #assumes only one view
        bad_glare_metrics = bad_glare[list(bad_glare.keys())[0]]
        good_glare_metrics = good_glare[list(good_glare.keys())[0]]

        bad_dgp = bad_glare_metrics['dgp']
        good_dgp = good_glare_metrics['dgp']

        day_type = solar[0][hr][4]
        time_of_day = solar[0][hr][3]

        if hr <= bad_latest_adj_time:
            if bad_dgp > bad_glare_threshold:
                bad_shaded = 1
                bad_shaded_hrs += 1
            else:
                #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                if bad_shaded == 0 or (bad_shaded_hrs >= bad_min_shade_period and day_type not in ['Saturday', 'Sunday', 'Holiday'] and time_of_day in bad_shade_check_times):
                    bad_shaded = 0
                    bad_shaded_hrs = 0
                else:
                    bad_shaded = 1
                    bad_shaded_hrs += 1
        else:
            if bad_shaded == 1:
                bad_shaded = 1
                bad_shaded_hrs +=1
            else:
                bad_shaded = 0
                bad_shaded_hrs = 0

        if hr <= good_latest_adj_time:
            if good_dgp > good_glare_threshold:
                good_shaded = 1
                good_shaded_hrs += 1
            else:
                #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                if good_shaded == 0 or (good_shaded_hrs >= good_min_shade_period and day_type not in ['Saturday', 'Sunday', 'Holiday'] and time_of_day in good_shade_check_times):
                    good_shaded = 0
                    good_shaded_hrs = 0
                else:
                    good_shaded = 1
                    good_shaded_hrs += 1
        else:
            if bad_shaded == 1:
                bad_shaded = 1
                bad_shaded_hrs +=1
            else:
                bad_shaded = 0
                bad_shaded_hrs = 0

        hour_ill_dat = [solar[0][hr][0], solar[0][hr][1], solar[0][hr][2], time_of_day, day_type, \
            bad_dgp, bad_shaded, good_dgp, good_shaded]
        hour_ill_dat.extend(grid_ill_dat)

        ill_dat.setdefault(spc_nm, []).append(hour_ill_dat)

#OUTPUT

for spc_nm, spc_dat in ill_dat.items():
    with open(rad_csv_fp+run_name+'_'+spc_nm.lower()+'.csv', 'w', newline='') as f_w:
        csv.writer(f_w, dialect='excel').writerows(spc_dat)

