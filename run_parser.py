import os
import csv

import distill_rad_data as distilry

analysis_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/'
out_path = analysis_path + '/Output/'
az_set_a = [[90, 180, 270], [90, 135, 180, 235, 270]]
view_config_a = ['WN', 'SL']
clrstry_config_a = ['NC', 'WN', 'LL', '3M']
shade_config_a = ['NS', 'LS', 'DS']
cz_a = [3, 7, 12, 14, 16]

def join_fmtd_a_nums(array):
    return ' '.join([format(num, '03d') for num in array])

ill_by_shd = []
for az_set in az_set_a:

    az_set_fmtd = join_fmtd_a_nums(az_set)
    ill_by_config = []
    
    for view_config in view_config_a:
        for clrstry_config in clrstry_config_a:
            for wn_shade_config in shade_config_a:
                run_nm = ' '.join([az_set_fmtd, view_config, wn_shade_config, clrstry_config, wn_shade_config])
                has_ill_dat = False
                for cz in cz_a:

                    run_nm = run_nm + ' ' + format(cz, '02d')
                    if os.path.isdir(analysis_path + run_nm):
                        ill_by_shd.extend(distilry.run_distillr(run_nm, analysis_path))
                        has_ill_dat = True
                    run_nm = run_nm[:-3]

                #OUTPUT

                if has_ill_dat:
                    ill_dir = out_path + view_config + ' ' + clrstry_config + '/'
                    if not os.path.exists(ill_dir):
                        os.makedirs(ill_dir)
                    with open(ill_dir + wn_shade_config + '.csv', 'w', newline='') as f_w:
                        csv.writer(f_w, dialect='excel').writerows(ill_by_shd)