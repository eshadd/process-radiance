#pylint: skip-file

import subprocess
import os
from  multiprocessing import Pool
import csv

#INPUT

n_processors = 4

#filters
occ_hrs = [8, 17]
day_type_a = ['Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Tue', 'Wed'] 
    
#rpict specs
color = '-av .3 .3 .3'
accuracy = '-ab 0 -ad 512 -as 256 -dj 1 -dp 1 -dt 0 -dc 1 -lw 0.001'
res = '-x 100 -y 100'

#model specs
az_lbl_a = ['090', '180', '270']
wwr_a = ['10', '20', '30', '40']
sensr_tag = '_Wn_Spc_Bad_Glare_Snsr_gs.vfv'

#radiance specs
rad_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/090 180 270 WN UN NC NS/run/1-UserScript-0/radiance'
sky_scene_dir = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Input/Weather/'
sky_scene_root_a = ['CZ09', 'CZ08', 'CZ03', 'CZ12', \
                    'CZ10', 'CZ06', 'CZ07', 'CZ04', \
                    'CZ13', 'CZ16', 'CZ02', 'CZ11', \
                    'CZ14', 'CZ15', 'CZ05','CZ01']

no_glare = [0, 0, 0, 0, 0, 0]

#SETUP

os.chdir(rad_dir)

def calc_glare_metrics(place):
    sky_scene_root, az_lbl, wwr = place
    spc = az_lbl + '_' + wwr

    #get the glare sensor position
    sensr_fn = [fn for fn in os.listdir('./views') if spc in fn and 'Bad_Glare_Snsr' in fn][0] #finds either vfh or vfv; doesn't matter.

    with open('./views/' + sensr_fn) as f_r:
        view = f_r.read().split(' ')
    pos = ' '.join(view[2:14])

    az = float(spc.split('_')[0])
    az_bounds = [az - 90, az + 90]

    glare_metrics_a = [['contrast_term', 'dgp', 'dgi', 'ugr', 'vcp', 'cgi']]
    for hoy in range(1,8761):
        dow = day_type_a[int(hoy/24) % 7]

        sky_scene_cz_dir = sky_scene_dir + sky_scene_root + '-rad-skies/'
        sky_scene_fp = sky_scene_cz_dir + '-'.join([sky_scene_root, format(hoy, '04d'), 'sky.rad'])

        with open(sky_scene_fp) as f_r:

            tod = round(float(f_r.readline().split(' ')[4]))
            f_r.readline()
            sol_az = float(f_r.readline().split(' ')[6]) + 180

            #only check if it's the right day, time and if direct beam can enter space (e.g. sun's azimuth is in window's view)
            if dow not in ['Sat', 'Sun'] and tod >= occ_hrs[0] and tod <= occ_hrs[1] and sol_az >= az_bounds[0] and sol_az <= az_bounds[1]:
                
                scene_fn = spc + '-scene.oct' 
                with open(scene_fn, 'wb') as f_w:
                    f_w.write(subprocess.check_output('oconv materials/materials.rad model.rad ' + '"' + sky_scene_fp + '"'))

                hdr_fn = spc + '-glare.hdr'
                with open(hdr_fn, 'wb') as f_w:
                    f_w.write(subprocess.check_output('rpict ' + ' '.join([color, accuracy, res, pos]) + ' -vth -vh 180 -vv 180 ' + scene_fn))

                glare_params = [params.split(' ') for params in subprocess.check_output('evalglare -d ' + hdr_fn).decode('utf-8').replace('\r','').split('\n')][-2]
                
                #calc the contrast term contribution and grab specific metrics
                dgp = float(glare_params[1])
                vert_eye_illum = float(glare_params[3])
                contrast_term = max(dgp - vert_eye_illum*.0000587 - 0.16, 0.0)

                glare_metrics = [contrast_term, dgp]
                glare_metrics.extend(glare_params[6:10])

                print(sky_scene_root + ' ' + spc + ' ' + str(hoy))
                print('dgp: ' + format(dgp, '.2f') + ' contrast term: ' + format(contrast_term, '.2f'))
            else:
                glare_metrics = no_glare
            
            glare_metrics_a.append(glare_metrics)

    with open('_'.join([sky_scene_root, spc]) + '_WN_UN_beam_glare_metrics.csv', 'w', newline='') as f_w:
        csv.writer(f_w, dialect='excel').writerows(glare_metrics_a)

#MAIN

if __name__ == '__main__':
    with Pool(n_processors) as pool:
        for sky_scene_root in sky_scene_root_a:
            place = [[sky_scene_root, az_lbl, wwr] for az_lbl in az_lbl_a for wwr in wwr_a]
            pool.map(calc_glare_metrics, place)
            #calc_glare_metrics(place[0])