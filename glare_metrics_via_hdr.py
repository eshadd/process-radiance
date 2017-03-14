#pylint: skip-file

import subprocess
import os

#INPUT

#max_el_check = 90
occ_hrs = [8, 17]
day_type_a = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'] 
    
#rpict specs
color = '-av .3 .3 .3'
accuracy = '-ab 2 -ad 512 -as 256 -dj 1 -dp 1 -dt 0 -dc 1 -lw 0.001'
res = '-x 400 -y 400'

azs = ['090', '180', '270']
wwrs = ['10', '20', '30', '40']
sensr_tag = '_Wn_Spc_Bad_Glare_Snsr_gs.vfv'
pos = '-vp -19.115 0.610 10.333 -vd 0.000 1.000 0.000 -vu 0 0 1'

rad_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/090 180 270 WN UN NC NS/run/1-UserScript-0/radiance'
sky_scene_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Input/Weather/'
sky_scene_roots = ['CZ01', 'CZ02', 'CZ03', 'CZ04', \
                   'CZ05', 'CZ06', 'CZ07', 'CZ08', \
                   'CZ09', 'CZ10', 'CZ11', 'CZ12', \
                   'CZ13', 'CZ14', 'CZ15','CZ16']

#SETUP

spc_strs = [az + '_' + wwr for az in azs for wwr in wwrs]

os.chdir(rad_dir)

#MAIN

#get the glare sensor position
az_lbl = azs[1]
sensr_spc = az_lbl + '_' + wwrs[1]
#finds either vfh or vfv; doesn't matter.
sensr_fn = [fn for fn in os.listdir('./views') if sensr_spc in fn and 'Bad_Glare_Snsr' in fn][0] 

with open('./views/' + sensr_fn) as f_r:
    view = f_r.read().split(' ')
pos = ' '.join(view[2:14])

az = float(az_lbl)
az_bounds = [az - 90, az + 90]
#only 1/2 of year for now to check resolution sensitivity. 
#hoy = range(1,8761)[3898]
hoy = range(1,4381)[3898]
dow = 'Thu'

sky_scene_root = sky_scene_roots[11]
sky_scene_cz_dir = sky_scene_dir + sky_scene_root + '-rad-skies/'
sky_scene_fp = sky_scene_cz_dir + '-'.join([sky_scene_root, format(hoy, '04d'), 'sky.rad'])

with open(sky_scene_fp) as f_r:

    tod = round(float(f_r.readline().split(' ')[4]))
    f_r.readline()
    sol_az = float(f_r.readline().split(' ')[6]) + 180

    #only check if it's the right day, time and if direct beam can enter space (e.g. sun's azimuth is in window's view)
    if dow not in ['Sat', 'Sun'] and tod >= occ_hrs[0] and tod <= occ_hrs[1] and sol_az >= az_bounds[0] and sol_az <= az_bounds[1]:
        with open('scene.oct', 'wb') as f_w:
            f_w.write(subprocess.check_output('oconv materials/materials.rad model.rad ' + '"' + sky_scene_fp + '"'))

        with open('glare.hdr', 'wb') as f_w:
            f_w.write(subprocess.check_output('rpict ' + ' '.join([color, accuracy, res, pos]) + ' -vth -vh 180 -vv 180 scene.oct'))

        dgp = subprocess.check_output('evalglare glare.hdr').decode('utf-8').split(' ')[1]
    else:
        dgp = 0

print(dgp)