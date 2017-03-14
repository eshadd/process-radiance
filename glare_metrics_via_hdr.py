#pylint: skip-file

color = ' -av .3 .3 .3 '
acc = ' -ab 2 -ad 512 -as 256 -dj 1 -dp 1 -dt 0 -dc 1 -lw 0.001 '
res = ' -x 100 -y 100 '
pos

with open('scene.oct', 'wb') as f_w:
    f_w.write(subprocess.check_output('oconv materials/materials.rad model.rad ' + sky_scene_fn))

with open('glare.hdr', 'wb') as f_w:
    f_w.write(subprocess.check_output('rpict -vth' + acc + color + res + pos + \
       ' -vth -vp 19.115 8.534 10.333 -vd 0.000 -1.000 0.000 -vu 0 0 1 -vh 180 -vv 180 ' + accuracy + ' scene.oct'))

glare_params = [params.split(' ') for params in subprocess.check_output('evalglare -d glare.hdr').decode('utf-8').replace('\r','').split('\n')]
print(str(glare_params[-2][1]))
print(str(glare_params[-2][3]))
print(str(float(glare_params[-2][1]) - float(glare_params[-2][3])*.0000587 - 0.16 ))

pass