#!python3
# _a: array
# _b: boolean
# _k: key
# _i: instance of an object

import json
import csv

import argparse
import traceback, sys

##INPUT

#parser = argparse.ArgumentParser(description='Outputs file of sensor(s) illumination levels and shading schedules')
#parser.add_argument('ann_illum', type=str, help='CSV of annual illuminance')
#parser.add_argument('savgs_lkups_fref', type=str, help='CSV of the savings lookups table; output is updated table')
#parser.add_argument('inp_errs_fref', type=str, help='Relative path/name for CSV of the erroneous inputs')
#parser_ns = parser.parse_args(['io_specs.csv', 'savgs_lkups.csv', 'inp_errs.csv'])

lvl_setpts = [275, 137.5]
hot_spot_setpt = 2000
max_contrast_rat = 10

year_start_day = 4  #1 = Monday
wday_start_hr = 8   #0 = midnight
wday_end_hr = 17
shade_toggle_times = [1, 4, 8, 24*3, 24*7, 24*7*2, 24*7*4]   #hours shade stays shut

map_depth = 10

##SETUP

shade_scheds_fref = 'shade_sched.csv'
ann_illum_fref = 'Wing1_Side1_Class1_Spc_map.ill'#parser_ns.ann_illum
with open(ann_illum_fref) as f_r:
    ann_illum = list(csv.reader(f_r, dialect='excel'))[4:]

lvl_grid_hrs = [0, 0]
hot_spot_grid_hrs = 0
max_contrast_grid_hrs = 0

map_width = int((len(ann_illum[4])-6)/map_depth)
map_depth_max_idx = map_depth-1
map_width_max_idx = map_width-1

inv_max_contrast_rat = 1/max_contrast_rat

last_time_shade_closed = []
prev_hr_shade_scheds = []
for stt in shade_toggle_times:
    last_time_shade_closed.append(-9999)
    prev_hr_shade_scheds.append(0)

shade_scheds = []

##MAIN

for yr_hr, illum_map in enumerate(ann_illum):

    yr_day = yr_hr/24
    day = int(yr_day)
    hr = int(24*(yr_day - day))
    day_of_week = (year_start_day + day) % 7

    if day_of_week < 6 and hr >= wday_start_hr and hr <= wday_end_hr:
    
        illum_map = illum_map[5:]
        illum_map = [float(illum) for illum in illum_map]
        illum_map = [illum_map[row_start: row_start + map_width] for row_start in range(0, map_width_max_idx * (map_depth_max_idx + 1), map_width_max_idx)]

        def set_glare(grid_pt_lvl, depth, above_lidx, above_ridx, right_idx):
        
            global max_contrast_grid_hrs
            global hot_spot_grid_hrs

            #is there a hot spot here?
            glare_b = grid_pt_lvl >= hot_spot_setpt
        
            #if it's not a hot spot, is there contrast glare?
            if not glare_b:
                denom = []
                if above_ridx: denom.extend(illum_map[depth+1][above_lidx:above_ridx+1]) #adjacent above
                if right_idx: denom.append(illum_map[depth][right_idx]) #on right

                #any non-zero?
                if sum(denom):
                    glare_b = grid_pt_lvl/min(denom) >= max_contrast_rat or grid_pt_lvl/max(denom) <= inv_max_contrast_rat
                    if glare_b: max_contrast_grid_hrs += 1
            else:
                hot_spot_grid_hrs += 1

            for idx, lvl_setpt in enumerate(lvl_setpts):
                if grid_pt_lvl >= lvl_setpt: lvl_grid_hrs[idx] += 1

            return int(glare_b)

        #central gridpoints to one row before back of room. Covers most of area and likely to have glare.
        for d in range(map_depth_max_idx):
            for w in range(1, map_width_max_idx):
                glare = set_glare(illum_map[d][w], d, w-1, w+1, w+1)
                if glare: break
            if glare: break
        #left side and right side gridpoints to one row before back of room.
        if not glare:
            for d in range(map_depth_max_idx):
                glare = set_glare(illum_map[d][0], d, 0, 1, 1)
                if glare: break
                glare = set_glare(illum_map[d][map_width_max_idx], d, map_width_max_idx-1, map_width_max_idx, 0)
                if glare: break
        #back of room. Skip very last point
        if not glare:
            for w in range(map_width_max_idx):
                glare = set_glare(illum_map[map_depth_max_idx][w], map_depth_max_idx, 0, 0, w)
                if glare: break

        #handle sched for glare.
        shade_scheds.append([])
        for idx, shade_toggle_time in enumerate(shade_toggle_times):
            #take a look if it's past the waiting time
            if yr_hr - last_time_shade_closed[idx] >= shade_toggle_time:
                if glare:
                    shade_scheds[yr_hr].append(1)
                    last_time_shade_closed[idx] = yr_hr
                else:
                    #open shades if they've been closed long enough.
                    shade_scheds[yr_hr].append(0)
            else:
                shade_scheds[yr_hr].append(prev_hr_shade_scheds[idx])

    #off-hours then keep as before.
    else:
        shade_scheds.append(prev_hr_shade_scheds)
    
    prev_hr_shade_scheds = shade_scheds[yr_hr]

##OUTPUT

with open(shade_scheds_fref, 'w', newline='') as f_w:
    csv.writer(f_w, dialect='excel').writerow([hot_spot_setpt, max_contrast_rat, lvl_setpts[0], lvl_setpts[1]])
    csv.writer(f_w, dialect='excel').writerow([hot_spot_grid_hrs, max_contrast_grid_hrs, lvl_grid_hrs[0], lvl_grid_hrs[1]])
    csv.writer(f_w, dialect='excel').writerow(shade_toggle_times)
    csv.writer(f_w, dialect='excel').writerows(shade_scheds)