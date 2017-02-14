import csv
import distill_rad_data

proj_path = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Runs - Copy/'
proj = 'dataPoint11'

ill_dat = distill_rad_data.run_distillr(proj, 7, '2.0Sl NS', 'NC', proj_path)
                
with open(proj_path + proj + '.csv', 'w', newline='') as f_w:
    csv.writer(f_w, dialect='excel').writerows(ill_dat)