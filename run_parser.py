import os

run_folder_parent_path = analysis_path
out_folder_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Output/'
az_set_a = [[90, 180, 270], [90, 135, 180, 235, 270]]
view_config_a = ['WN', 'SL']
clrstry_config_a = ['NC', 'WN', 'LL', '3M']
shade_config_a = ['NS', 'LS', 'DS']
cz_a = [3, 7, 12, 14, 16]

def join_fmtd_a_nums(array):
    return ' '.join([format(num, '03d') for num in array])

for az_set in az_set_a:
    az_set_fmtd = join_fmtd_a_nums(az_set)
    for view_config in view_config_a:
        for shade_config in shade_config_a:
            for clrstry_config in clrstry_config_a:
                for shade_config in shade_config_a:
                    for cz in cz_a:
                        run_nm = ' '.join([az_set_fmtd, view_config, shade_config, clrstry_config, shade_config, format(cz, '02d')])
                        if os.path.isdir(run_folder_parent_path + run_nm):
                            subfolder = view_config + ' ' + clrstry_config
                            print(run_folder)

