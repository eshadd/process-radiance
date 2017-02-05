import os
import csv

import distill_rad_data as distilry

#INPUTS 

analysis_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/'
out_path = analysis_path + '/Output/'
az_set_a = [[90, 180, 270], [90, 135, 180, 235, 270]]
view_config_a = ['WN', 'SL']
clrstry_config_a = ['NC', 'WN', 'LL', '3M']
shd_type_a = ['NS', 'LS', 'DS']
cz_a = [3, 7, 12, 14, 16]

#SETUP

def join_fmtd_a_nums(array):
    return ' '.join([format(num, '03d') for num in array])

#MAIN

for cz in cz_a:
    for view_shd_type in shd_type_a:

        #this is the output file array.
        ill_dat = []

        for view_config in view_config_a:
            for clrstry_shd_type in shd_type_a:
                for clrstry_config in clrstry_config_a:
                    for az_set in az_set_a:

                        az_set_fmtd = join_fmtd_a_nums(az_set)                   
                        run_nm = ' '.join([az_set_fmtd, view_config, view_shd_type, clrstry_config, clrstry_shd_type, format(cz, '02d')])

                        if os.path.isdir(analysis_path + run_nm):
                            ill_dat.extend(distilry.run_distillr(run_nm, cz, view_config, clrstry_config, analysis_path))

            #OUTPUT

            if ill_dat:
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                with open(out_path + ' '.join([format(cz, '02d'), view_shd_type]) + '.csv', 'w', newline='') as f_w:
                    csv.writer(f_w, dialect='excel').writerows(ill_dat)