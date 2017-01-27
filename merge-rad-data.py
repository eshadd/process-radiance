import json
import csv

glare_json_fn = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Test 16/run/0-UserScript/radiance/output/glare.json'
glare_csv_fp = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/Test 16/run/0-UserScript/radiance/output/'
spc_field = 'T2419_CASE_Spc'
glare_case_fields = ['Bad_Case_Glare_Sensor', 'Good_Case_Glare_Sensor']

with open(glare_json_fn) as glare_f:
    glare_d = json.load(glare_f).pop(spc_field)

#NOT USED currently
glare_view_a = [glare_case.pop('view_definitions') for glare_case in glare_d.values()]

glare_cases_a_by_d = {glare_case: [[int(hour), view, glare_data['dgp'], glare_data['raw']] for hour, views in glare_d[glare_case].items() for view, glare_data in views.items()] for glare_case in glare_case_fields}
#good_glare_a = [[hour, view, glare_data['dgp'], glare_data['raw']] for hour, views in glare_d[good_glare_field].items() for view, glare_data in views.items()]

for glare_case_nm in glare_case_fields:
    with open(glare_csv_fp+glare_case_nm.lower()+'.csv', 'w', newline='') as f_w:
        csv.writer(f_w, dialect='excel').writerows(sorted(glare_cases_a_by_d[glare_case_nm]))

