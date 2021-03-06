#pylint: skip-file
import csv
import sqlite3
import os
import bisect as bs

def run_distillr(case, setpt_a, shade_case_d, run_path_a, pat_path, wthr_fn, tdv_fref):

    #INPUT

    nglr_hdr_rows = 3
    nmap_hdr_rows = 4
    ntdv_hdr_rows = 3
    
    day_type_a = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'] 

    min_lamp_pwr = 0.2
    pwr_slope = 1
    #Table 130.1-A 2016
    multi_level_a = [min_lamp_pwr, 0.4, 0.7, 0.85, 1]
    bi_level_a = [min_lamp_pwr, 0.7, 1]

    #office sched
    day_type_ltg_sched = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 1, 'Sun': 2}
    ltg_sched_a = [
        [0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.3, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65, 0.35, 0.3, 0.3, 0.2, 0.2, 0.1, 0.05],
        [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.3, 0.3, 0.3, 0.3, 0.15, 0.15, 0.15, 0.15, 0.15, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        [0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
            ]

    
    #SETUP

    ill_dir_d = {}
    for shd_case, run_path in run_path_a.items():

        dat_pt = run_path.split('/')[-1]
        if dat_pt:
            run_idx = int(dat_pt.replace('dataPoint', ''))
            rad_out_path = pat_path + dat_pt + '/' + str(9 * (run_idx - 2) + 1) + '-Userscript-0/radiance/output/'

            ill_dir_d[shd_case] = [ref for ref in os.walk(rad_out_path + 'ts/')][2::2]

    ill_fref_a = [[fn_a[0], path + '/' + fn_a[0], path + '/' + fn_a[1]] for path, blank, fn_a in ill_dir_d.get('none', {})]
    if ill_fref_a and ill_dir_d['good']:
        ill_fref_a = [nsfref + [ill_dir_d['good'][spc_idx][0] + '/' + ill_dir_d['good'][spc_idx][2][1]] for spc_idx, nsfref in enumerate(ill_fref_a)]
    else:
        ill_fref_a = []

    #rad_set = [wthr_fn, case]
    
    cz_spos = wthr_fn.find('CZ') + 2
    cz = int(wthr_fn[cz_spos:cz_spos+2])

    #MAIN

    #Loop through radiance data files
    rad_dat = []
    #rad_hr_dat = []
    for glr_fnm, glr_fref, map_fref, gd_shd_map_fref in ill_fref_a:        

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
                
                with open(gd_shd_map_fref) as fr:
                    gd_shd_map_rdr = csv.reader(fr)
                    for hdr_rw in range(nmap_hdr_rows):
                        next(gd_shd_map_rdr)
                
                    with open(tdv_fref) as fr:
                        tdv_rdr = csv.reader(fr)
                        for hdr_rw in range(ntdv_hdr_rows):
                            next(tdv_rdr)
                
                        #init blinds/shades
                        for shd_case in ('bad', 'good'):
                            shade_case_d[shd_case]['shaded'] = 0
                            shade_case_d[shd_case]['shaded_hrs'] = 0

                        #init ctrl TDV
                        ctrl_init = [0 for sp in setpt_a]
                        pdim_a = ctrl_init
                        sdim_a = ctrl_init
                        pmulti_a = ctrl_init
                        smulti_a = ctrl_init
                        pbi_a = ctrl_init
                        sbi_a = ctrl_init

                        #aggregate data
                        for ann_hr_idx, glr_rw in enumerate(glr_rdr):
                            ann_hr = ann_hr_idx + 1

                            #weather, configuration
                            #rad_hr_dat.extend(rad_set)
                            #rad_hr_dat.append(spc_az)
                            #rad_hr_dat.append(spc_wwr)

                            #rad_hr_dat.append(ann_hr)
                            day_type = day_type_a[int(ann_hr/24) % 7]
                            #rad_hr_dat.append(day_type)

                            #sensors
                            map_a = next(map_rdr)
                            prim_zn_ill = float(map_a[6])
                            secd_zn_ill = float(map_a[-1])
                            #rad_hr_dat.append(prim_zn_ill)
                            #rad_hr_dat.append(secd_zn_ill)

                            gd_shd_map = next(gd_shd_map_rdr)
                            gd_shd_pzn_ill = float(gd_shd_map[6])
                            gd_shd_szn_ill = float(gd_shd_map[-1])

                            #glare
                            #rad_hr_dat.extend(glr_rw[:5])

                            time_of_day = int(glr_rw[2].replace(':00:00',''))
                            dgp = float(glr_rw[4])

                            #tdv
                            ltg_sched = ltg_sched_a[day_type_ltg_sched[day_type]]
                            tdv = float(next(tdv_rdr)[cz]) * ltg_sched[time_of_day - 1]
                            #rad_hr_dat.append(tdv)

                            for shd_case in ('bad', 'good'): #not dict iter so preserve this order.

                                shading = shade_case_d[shd_case]

                                if time_of_day >= shading['occ_hrs'][0] and time_of_day <= shading['occ_hrs'][1]:
                                    if dgp > shading['threshold']:
                                        shading['shaded'] = 1
                                        shading['shaded_hrs'] += 1
                                        if shd_case == 'bad':
                                            pzn_ill = 0.0
                                            szn_ill = 0.0
                                        else:
                                            pzn_ill = gd_shd_pzn_ill
                                            szn_ill = gd_shd_szn_ill
                                    else:
                                        #if not glarey now, then if unshaded on last loop, or shaded but is now time to check...
                                        if shading['shaded'] == 0 or (shading['shaded_hrs'] >= shading['min_period'] and day_type not in ['Sat', 'Sun', 'Hol'] and time_of_day in shading['check_times']):
                                            shading['shaded'] = 0
                                            shading['shaded_hrs'] = 0
                                            pzn_ill = prim_zn_ill
                                            szn_ill = secd_zn_ill
                                        else:
                                            shading['shaded'] = 1
                                            shading['shaded_hrs'] += 1
                                            if shd_case == 'bad':
                                                pzn_ill = 0.0
                                                szn_ill = 0.0
                                            else:
                                                pzn_ill = gd_shd_pzn_ill
                                                szn_ill = gd_shd_szn_ill
                                else:
                                    if shading['shaded'] == 1:
                                        shading['shaded_hrs'] +=1
                                        if shd_case == 'bad':
                                            pzn_ill = 0.0
                                            szn_ill = 0.0
                                        else:
                                            pzn_ill = gd_shd_pzn_ill
                                            szn_ill = gd_shd_szn_ill
                                    else:
                                        shading['shaded'] = 0
                                        shading['shaded_hrs'] = 0
                                        pzn_ill = prim_zn_ill
                                        szn_ill = secd_zn_ill

                                #rad_hr_dat.append(shading['shaded'])

                                # power limits
                                pzn_rat_a = [max(min(1 - pwr_slope * pzn_ill/sp, 1), min_lamp_pwr) for sp in setpt_a]
                                szn_rat_a = [max(min(1 - pwr_slope * szn_ill/sp, 1), min_lamp_pwr) for sp in setpt_a]

                                #the below control calcs use the average of the cases.
                            
                                # dimming
                                pdim_a = [pdim_a[idx] + curr for idx, curr in enumerate([rat * tdv/2 for rat in pzn_rat_a])]
                                sdim_a = [sdim_a[idx] + curr for idx, curr in enumerate([rat * tdv/2 for rat in szn_rat_a])]

                                # multi-level
                                pmulti_a = [pmulti_a[idx] + curr for idx, curr in enumerate([multi_level_a[bs.bisect_left(multi_level_a, rat)] * tdv/2 for rat in pzn_rat_a])]
                                smulti_a = [smulti_a[idx] + curr for idx, curr in enumerate([multi_level_a[bs.bisect_left(multi_level_a, rat)] * tdv/2 for rat in szn_rat_a])]

                                # bi-level
                                pbi_a = [pbi_a[idx] + curr for idx, curr in enumerate([bi_level_a[bs.bisect_left(bi_level_a, rat)] * tdv/2 for rat in pzn_rat_a])]
                                sbi_a = [sbi_a[idx] + curr for idx, curr in enumerate([bi_level_a[bs.bisect_left(bi_level_a, rat)] * tdv/2 for rat in szn_rat_a])]

                        spc_info = [wthr_fn, case, spc_az, spc_wwr]
                        rad_dat.extend([spc_info + [1, 'dim', setpt_a[idx], tdv] for idx, tdv in enumerate(pdim_a)])
                        rad_dat.extend([spc_info + [2, 'dim', setpt_a[idx], tdv] for idx, tdv in enumerate(sdim_a)])
                        rad_dat.extend([spc_info + [1, 'multi', setpt_a[idx], tdv] for idx, tdv in enumerate(pmulti_a)])
                        rad_dat.extend([spc_info + [2, 'multi', setpt_a[idx], tdv] for idx, tdv in enumerate(smulti_a)])
                        rad_dat.extend([spc_info + [1, 'bi', setpt_a[idx], tdv] for idx, tdv in enumerate(pbi_a)])
                        rad_dat.extend([spc_info + [2, 'bi', setpt_a[idx], tdv] for idx, tdv in enumerate(sbi_a)])

    return (cz, rad_dat)