#pylint: skip-file

import subprocess
import os

#INPUT
pos = '-vp -19.115 0.610 10.333 -vd 0.000 1.000 0.000 -vu 0 0 1'

alt_filt = 90
tod_filt = {'start': 8, 'end': 17}

#rpict specs
color = '-av .3 .3 .3'
accuracy = '-ab 2 -ad 512 -as 256 -dj 1 -dp 1 -dt 0 -dc 1 -lw 0.001'
res = '-x 400 -y 400'

azs = ['090', '180', '270']
wwrs = ['10', '20', '30', '40']

rad_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/090 180 270 WN UN NC NS/run/1-UserScript-0/radiance'
sky_scene_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Input/Weather/'
sky_scene_roots = ['CZ01', 'CZ02', 'CZ03', 'CZ04', \
                   'CZ05', 'CZ06', 'CZ07', 'CZ08', \
                   'CZ09', 'CZ10', 'CZ11', 'CZ12', \
                   'CZ13', 'CZ14', 'CZ15','CZ16']

#SETUP

spc_strs = [az + '_' + wwr for az in azs for wwr in wwrs]

os.chdir(rad_dir)

hoy = 3899
sky_scene_root = sky_scene_roots[11]
sky_scene_cz_dir = sky_scene_dir + sky_scene_root + '-rad-skies/'
sky_scene_fp = '"' + sky_scene_cz_dir + '-'.join([sky_scene_root, format(hoy, '04d'), 'sky.rad']) + '"'
with open('scene.oct', 'wb') as f_w:
    f_w.write(subprocess.check_output('oconv materials/materials.rad model.rad ' + sky_scene_fp))

with open('glare.hdr', 'wb') as f_w:
    f_w.write(subprocess.check_output('rpict ' + ' '.join([color, accuracy, res, pos]) + ' -vth -vh 180 -vv 180 scene.oct'))

dgp = subprocess.check_output('evalglare glare.hdr').decode('utf-8').split(' ')[1]
print(dgp)