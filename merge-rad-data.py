import json
import csv
import sqlite3

#INPUT

run_name = 'Test 16'

glare_json_fn = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/0-UserScript/radiance/output/glare.json'
glare_csv_fp = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/0-UserScript/radiance/output/'
spc_field = 'T2419_CASE_Spc'
glare_case_fields = ['Bad_Case_Glare_Sensor', 'Good_Case_Glare_Sensor']

sql = 'C:/Determinant_J/Projects/T2419 CASE/Analysis/' + run_name + '/run/0-UserScript/radiance/sql/eplusout.sql'    
sql_tbl = 'ReportVariableWithTime '
sql_field = 'Value'
sql_filter_col = 'Name'
sql_filter_a = ['Site Solar Azimuth Angle', 'Site Solar Altitude Angle']

#SETUP

with open(glare_json_fn) as glare_f:
    glare_d = json.load(glare_f).pop(spc_field)

# Connect to the database file
conn = sqlite3.connect(sql)
c = conn.cursor()

#MAIN

#read in glare metrics
glare_view_a = [glare_case.pop('view_definitions') for glare_case in glare_d.values()]#NOT USED currently

glare_cases_a_by_d = {glare_case: sorted([[int(hour), view, glare_data['dgp'], glare_data['raw']] for hour, views in glare_d[glare_case].items() for view, glare_data in views.items()]) for glare_case in glare_case_fields}

#for glare_case_nm in glare_case_fields:
#    with open(glare_csv_fp+glare_case_nm.lower()+'.csv', 'w', newline='') as f_w:
#        csv.writer(f_w, dialect='excel').writerows(glare_cases_a_by_d[glare_case_nm])

#import solar position
solar_pos = []
for sql_filter in sql_filter_a:
    c.execute('SELECT {fd} FROM {tn} WHERE {cn}="{ft}"'.format(fd=sql_field,tn=sql_tbl,cn=sql_filter_col,ft=sql_filter))
    solar_pos.append(c.fetchall())

solar_pos = [[solar_pos[j][i][0] for j in range(len(solar_pos))] for i in range(len(solar_pos[0]))]

conn.close()
