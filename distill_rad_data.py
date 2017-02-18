#pylint: skip-file
import csv
import sqlite3
import os

def run_distillr(run_name, setpt_a, out_path, wthr_fn, tdv_fref):

    #INPUT

    nglr_hdr_rows = 3
    nmap_hdr_rows = 4
    ntdv_hdr_rows = 3
    
    bad_glare_threshold = 0.4
    good_glare_threshold = 0.6
    bad_min_shade_period = 21*24
    good_min_shade_period = 1
    bad_shade_check_times = [8]
    good_shade_check_times = [8, 12]
    bad_occ_start = 8
    good_occ_start = 8
    bad_occ_end = 17
    good_occ_end = 17
    bad_shaded = 0
    bad_shaded_hrs = 0
    good_shaded = 0
    good_shaded_hrs = 0

    day_type_a = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'] 

    min_lamp_pwr = 0.2
    pwr_slope = 1
    #office sched
    day_type_ltg_sched = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 1, 'Sun': 2}
    ltg_sched_a = [
        [0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.3, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.35, 0.3, 0.3, 0.2, 0.2, 0.1, 0.05],
        [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.3, 0.3, 0.3, 0.3, 0.15, 0.15, 0.15, 0.15, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
            ]

    
    #SETUP

    config = run_name.split(' ')
    wn_case = config[0]
    wn_shd = config[1] if len(config) > 1 else 'NS'
    rad_set = [wthr_fn, wn_case, wn_shd]
    
    ill_dir_a = [ref for ref in os.walk(out_path + 'ts/')][2::2]
    ill_fref_a = [[fn_a[0], path + '/' + fn_a[0], path + '/' + fn_a[1]] for path, blank, fn_a in ill_dir_a]

    cz_spos = wthr_fn.find('CZ') + 2
    cz = int(wthr_fn[cz_spos:cz_spos+2])

    #MAIN

    #Loop through radiance data files
    rad_dat = []
    rad_hr_dat = []
    for glr_fnm, glr_fref, map_fref in ill_fref_a:        

        spc_form_a = glr_fnm[:-3].split('_')
        spc_az = int(spc_form_a[0])
        spc_wwr = spc_form_a[1]

        with open(glr_fref) as csvfile:
            glr_rdr = csv.reader(csvfile)
            for hdr_rw in range(nglr_hdr_rows):
                next(glr_rdr)
            with open(map_fref) as fr:
                map_rdr = csv.reader(fr)
                for hdr_rw in range(nmap_hdr_rows):
                    next(map_rdr)
                
                with open(tdv_fref) as fr:
                    tdv_rdr = csv.reader(fr)
                    for hdr_rw in range(ntdv_hdr_rows):
                        next(tdv_rdr)
                
                    #aggregate data
                    for ann_hr, glr_rw in enumerate(glr_rdr):
                    
                        #weather, configuration
                        rad_hr_dat.extend(rad_set)
                        rad_hr_dat.append(spc_az)
                        rad_hr_dat.append(spc_wwr)

                        rad_hr_dat.append(ann_hr)
                        day_type = day_type_a[ann_hr % 7]
                        rad_hr_dat.append(day_type)

                        #glare
                        rad_hr_dat.extend(glr_rw[:5])

                        time_of_day = int(glr_rw[2].replace(':00:00',''))
                        bad_dgp = float(glr_rw[4])
                        good_dgp = float(glr_rw[4])

                        if time_of_day >= bad_occ_start and time_of_day <= bad_occ_end:
                            if bad_dgp > bad_glare_threshold:
                                bad_shaded = 1
                                bad_shaded_hrs += 1
                            else:
                                #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                                if bad_shaded == 0 or (bad_shaded_hrs >= bad_min_shade_period and day_type not in ['Sat', 'Sun', 'Hol'] and time_of_day in bad_shade_check_times):
                                    bad_shaded = 0
                                    bad_shaded_hrs = 0
                                else:
                                    bad_shaded = 1
                                    bad_shaded_hrs += 1
                        else:
                            if bad_shaded == 1:
                                bad_shaded_hrs +=1
                            else:
                                bad_shaded = 0
                                bad_shaded_hrs = 0

                        rad_hr_dat.append(bad_shaded)

                        if time_of_day >= good_occ_start and time_of_day <= good_occ_end:
                            if good_dgp > good_glare_threshold:
                                good_shaded = 1
                                good_shaded_hrs += 1
                            else:
                                #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                                if good_shaded == 0 or (good_shaded_hrs >= good_min_shade_period and day_type not in ['Sat', 'Sun ', 'Hol'] and time_of_day in good_shade_check_times):
                                    good_shaded = 0
                                    good_shaded_hrs = 0
                                else:
                                    good_shaded = 1
                                    good_shaded_hrs += 1
                        else:
                            if good_shaded == 1:
                                good_shaded_hrs +=1
                            else:
                                good_shaded = 0
                                good_shaded_hrs = 0
                    
                        rad_hr_dat.append(good_shaded)

                        #sensors
                        map_a = next(map_rdr)
                        prim_zn_ill = float(map_a[6])
                        secd_zn_ill = float(map_a[-1])
                        rad_hr_dat.append(prim_zn_ill)
                        rad_hr_dat.append(secd_zn_ill)

                        #tdv
                        ltg_sched = ltg_sched_a[day_type_ltg_sched[day_type]]
                        tdv = float(next(tdv_rdr)[cz]) * ltg_sched[time_of_day - 1]
                        rad_hr_dat.append(tdv)
                        rad_hr_dat.extend([max(min(pwr_slope * prim_zn_ill/sp, 1), min_lamp_pwr) * tdv for sp in setpt_a])
                        rad_hr_dat.extend([max(min(pwr_slope * secd_zn_ill/sp, 1), min_lamp_pwr) * tdv for sp in setpt_a])

                        #append and reset
                        rad_dat.append(rad_hr_dat)
                        rad_hr_dat = []

    return (wn_shd, rad_dat)
    
def run_distillr_expanded(run_name, climate_zone, view_config, clrstry_config, analysis_path):

    #INPUT

    glare_fref = analysis_path + run_name + '/90-UserScript-0/radiance/output/radout.json'

    bad_glare_field = 'Bad_Glare_Snsr'
    #good_glare_field = 'Good_Glare_Snsr'
    bad_glare_threshold = 0.4
    good_glare_threshold = 0.6
    bad_min_shade_period = 21*24
    good_min_shade_period = 1
    bad_shade_check_times = [8]
    good_shade_check_times = [8, 12]
    bad_occ_start = 8
    good_occ_start = 8
    bad_occ_end = 17
    good_occ_end = 17

    sql = analysis_path + run_name + '/90-UserScript-0/radiance/sql/eplusout.sql'    
    sql_tbl = 'ReportVariableWithTime '
    sql_field = 'Value'
    sql_filter_col = 'Name'
    sql_filter_a = ['Site Solar Azimuth Angle', 'Site Solar Altitude Angle', 'Site Sky Diffuse Solar Radiation Luminous Efficacy', 'Site Beam Solar Radiation Luminous Efficacy']
    sql_time = 'TimeIndex, Month, Day, Hour, DayType'

    #SETUP

    with open(glare_fref) as ill_f:
        ill_raw_d = json.load(ill_f)
        ill_raw_a = ill_raw_d.pop('all_hours')

    #reformat so main loop can loop by space.
    ill_d = {spc_nm: [] for spc_nm in ill_raw_a[0].keys()}
    for hr_dat in ill_raw_a:
         for spc_nm, spc_dat in hr_dat.items():
            ill_d[spc_nm].append([spc_dat[0], spc_dat[2]])

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
    ill_dat = [['CZ', 'View', 'Clrstry', 'Az', 'WWR', 'Ann Hr', 'Month', 'Day', 'Hr', 'Day Type', 'Bad DGP', 'Good DGP', 'Bad Shaded?', 'Good Shaded?', '1ry Daylt', '2ry Daylt']]
    for spc_nm, spc_ill_dat in ill_d.items():

        form_dat = spc_nm.split('_')

        bad_shaded_hrs = 0
        good_shaded_hrs = 0
        bad_shaded = 0
        good_shaded = 0
        for hr, hour_dat in enumerate(spc_ill_dat):

            grid_ill_dat = hour_dat[0]
            sensor_glare_dat = hour_dat[1]
        
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

            if time_of_day >= bad_occ_start and time_of_day <= bad_occ_end:
                if bad_dgp > bad_glare_threshold:
                    bad_shaded = 1
                    bad_shaded_hrs += 1
                else:
                    #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                    if bad_shaded == 0 or (bad_shaded_hrs >= bad_min_shade_period and day_type not in ['Sat', 'Sun', 'Hol'] and time_of_day in bad_shade_check_times):
                        bad_shaded = 0
                        bad_shaded_hrs = 0
                    else:
                        bad_shaded = 1
                        bad_shaded_hrs += 1
            else:
                if bad_shaded == 1:
                    bad_shaded_hrs +=1
                else:
                    bad_shaded = 0
                    bad_shaded_hrs = 0

            if time_of_day >= good_occ_start and time_of_day <= good_occ_end:
                if good_dgp > good_glare_threshold:
                    good_shaded = 1
                    good_shaded_hrs += 1
                else:
                    #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                    if good_shaded == 0 or (good_shaded_hrs >= good_min_shade_period and day_type not in ['Sat', 'Sun ', 'Hol'] and time_of_day in good_shade_check_times):
                        good_shaded = 0
                        good_shaded_hrs = 0
                    else:
                        good_shaded = 1
                        good_shaded_hrs += 1
            else:
                if good_shaded == 1:
                    good_shaded_hrs +=1
                else:
                    good_shaded = 0
                    good_shaded_hrs = 0

            hr_ill_dat = [climate_zone, view_config, clrstry_config, int(form_dat[0]), int(form_dat[1]), solar[0][hr][0], solar[0][hr][1], solar[0][hr][2], time_of_day, day_type, 
                            bad_dgp, good_dgp, bad_shaded, good_shaded, grid_ill_dat[0], grid_ill_dat[13]]

            ill_dat.append(hr_ill_dat)

    return ill_dat