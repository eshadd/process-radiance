#pylint: skip-file

import subprocess
import os

#INPUT

wthr_fnm = 'OAKLAND_724930_CZ2010'
lat = '37.72'
long = '-122.22'
month = '6'
day = '11'
hour = '7'
time_zn = '-8.0'
dir_nrm_rad = '504'     #idx = 14
diff_horiz_rad = '81'   #idx = 15
hoy = 0

#SETUP

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
            'skyfunc glow ground_glow\n' + \
            '0\n' + \
            '0\n' + \
            '4\n' + \
            '1 .8 .5 0\n' + \
            'ground_glow source ground\n' + \
            '0\n' + \
            '0\n' + \
            '4\n' + \
            '0 0 -1 180\n'

os.chdir('C:/Determinant_J/Projects/T2419 CASE/Analysis/El 15 20 25/dataPoint4/19-UserScript-0/radiance')

#MAIN

dist_func_cmd = 'gendaylit ' + month + ' ' + day + ' ' + hour + \
                ' -a ' + lat + ' -o ' + str(-float(long)) + ' -m ' + str(-float(time_zn) * 15) + ' -i 60' + \
                ' -W ' + dir_nrm_rad + ' ' + diff_horiz_rad

sky_scene_fnm = wthr_fnm + '-' + format(hoy, '04d') + '-sky.rad'
with open(sky_scene_fnm, 'wb') as f_w:
    f_w.write(subprocess.check_output(dist_func_cmd)  + str.encode(mat_surf))

with open('scene.oct', 'wb') as f_w:
    f_w.write(subprocess.check_output('oconv materials/materials.rad model.rad ' + sky_scene_fnm))

with open('glare.hdr', 'wb') as f_w:
    f_w.write(subprocess.check_output('rpict -av .3 .3 .3 -x 100 -y 100 -ab 3 -vth -vp 19.115 8.534 10.333 -vd 0.000 -1.000 0.000 -vu 0 0 1 -vh 180 -vv 180 scene.oct'))

dgp = subprocess.check_output('evalglare glare.hdr').decode('utf-8').split(' ')[1]
print(str(dgp))

pass