#pylint: skip-file

import subprocess
import os

#INPUT

wthr_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Input/Weather/'
wthr_fns = ['CZ01.epw', 'CZ02.epw', 'CZ03.epw', 'CZ04.epw', \
            'CZ05.epw', 'CZ06.epw', 'CZ07.epw', 'CZ08.epw', \
            'CZ09.epw', 'CZ10.epw', 'CZ11.epw', 'CZ12.epw', \
            'CZ13.epw', 'CZ14.epw', 'CZ15.epw','CZ16.epw']

#SETUP

os.chdir(wthr_dir)

mat_surf =  'skyfunc glow sky_mat\n' + \
            '0\n' + \
            '0\n' + \
            '4\n' + \
            '1 1 1 0\n' + \
            'sky_mat source sky\n' + \
            '0\n' + \
            '0\n' + \
            '4\n' + \
            '0 0 1 180\n' + \
            'skyfunc glow groundglow\n' + \
            '0\n' + \
            '0\n' + \
            '4\n' + \
            '1 .8 .5 0\n' + \
            'groundglow source ground\n' + \
            '0\n' + \
            '0\n' + \
            '4\n' + \
            '0 0 -1 180'

#MAIN

for wthr_fn in wthr_fns:

    with open(wthr_fn) as f_r:
        wthr = f_r.read().split('\n')
    
    loc = wthr[0].split(',')
    lat = loc[6]
    long = loc[7]
    time_zn = loc[8]
    wthr = wthr[8:8768]

    wthr_fn_root = wthr_fn[0:-4]
    out_path = './' + wthr_fn_root + '-rad-skies'
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    for hoy, wthr_day in enumerate(wthr):
        wthr_day = wthr_day.split(',')
        dist_func_cmd = 'gendaylit ' + wthr_day[1] + ' ' + wthr_day[2] + ' ' + str(float(wthr_day[3]) - .001) + \
                        ' -a ' + lat + ' -o ' + str(-float(long)) + ' -m ' + str(-float(time_zn) * 15) + ' -i 60 -w ' + \
                        ' -W ' + wthr_day[14] + ' ' + wthr_day[15]

        sky_scene_fn = out_path + '/' + wthr_fn_root + '-' + format(hoy + 1, '04d') + '-sky.rad'
        with open(sky_scene_fn, 'wb') as f_w:
            f_w.write(subprocess.check_output(dist_func_cmd)  + str.encode(mat_surf))