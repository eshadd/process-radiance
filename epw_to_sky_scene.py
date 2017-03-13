#pylint: skip-file

scene = "# weather file: " + locName + " LAT: " + lat + "\n" + \
        "!gendaylit " + `month` + ' ' + `day` + ' ' + `hour` + \
        " -a " + lat + " -o " + `-float(long)` + " -m " + `-float(timeZone) * 15` + \
        " -W " + `dirNrmRad` + " " + `difHorRad` + " -O " + `outputType` + \
        " | xform -rz " + str(north) + "\n" + \
        "skyfunc glow sky_mat\n" + \
        "0\n" + \
        "0\n" + \
        "4\n" + \
        "1 1 1 0\n" + \
        "sky_mat source sky\n" + \
        "0\n" + \
        "0\n" + \
        "4\n" + \
        "0 0 1 180\n" + \
        "skyfunc glow ground_glow\n" + \
        "0\n" + \
        "0\n" + \
        "4\n" + \
        "1 .8 .5 0\n" + \
        "ground_glow source ground\n" + \
        "0\n" + \
        "0\n" + \
        "4\n" + \
        "0 0 -1 180\n"

#with open(out_path + format(cz, '02d') + '.csv', 'w', newline='') as f_w:
#    csv.writer(f_w, dialect='excel').writerows(results)
