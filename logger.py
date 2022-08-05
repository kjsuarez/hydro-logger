# py .\logger.py C:\Users\super\Documents\survey_project\OPR-W386-TJ-22 H13609 179 2903
# C:/Users/super/Documents/survey_project/OPR-W386-TJ-22
#

# take location of opr dir, sheet number, day and launch as inputs
# for each relevant sub dir (svp, mbes, pos) pull all file names, filter through a regex and store in a param
# generate an excel doc populated with the correct outputs
from sys import argv
from os import listdir, path
import re
import datetime
from openpyxl import load_workbook
from pathlib import Path
import math

# path = "C:\Users\super\Documents\survey project\OPR-W386-TJ-22"
script, drive_path, sheet_number, day_number, vessel = argv

today = datetime.date.today()
current_year = today.year
date_string = f"{today.month}/{today.day}/{today.year}"
project_name = drive_path.split('/')[-1]

# excel stuff
base_log_workbook = load_workbook(filename = f'HXXXXX_VesselXXXX_DNXXX_Log_{current_year}.xlsm', keep_vba = True)
base_log_sheet = base_log_workbook.active
date_cell = 'B9'
project_cell = 'F9'
sheet_cell = 'J9'
day_number_cell = 'N9'
vessel_cell = 'R9'
first_hic_cell = 'B13'
second_hic_cell = 'F13'
initial_SVP_column = 'B'
initial_SVP_row = 25
initial_SVP_max_size = 4
svp_cell_width = 9

first_pos_cell = 'B21'; last_pos_cell = 'L21'
first_mbes_cell = 'B33'; last_mbes_cell = 'B34'

year_day = f"{current_year}-{day_number}"
# filepath stuff
vessel_year_sonar = f"{vessel}_{current_year}_EM2040"
pos_path = f"{drive_path}/{sheet_number}/Data/Positioning/{vessel_year_sonar}/{year_day}" #drive_path+"/position"
log_path = f"{drive_path}/{sheet_number}/Data/Acquisition_Logs/{vessel_year_sonar}/{year_day}"
svp_path = f"{drive_path}/{sheet_number}/Data/SVP/{vessel_year_sonar}/SVP/{year_day}"
mbes_path = f"{drive_path}/{sheet_number}/Data/MBES/{vessel_year_sonar}/{year_day}"
print(pos_path)

# pos files
position_nodes = listdir(pos_path)
pos_pattern = re.compile('^.+\.\d{3}$')
pos_filenames = [s for s in position_nodes if pos_pattern.match(s)]
pos_filenames.sort()

#svp files
svp_nodes = listdir(svp_path)
svp_pattern = re.compile(f'{current_year}_{day_number}_\d+\.svp')
svp_filenames = [s for s in svp_nodes if svp_pattern.match(s)]
svp_filenames.sort()

#mbes files
mbes_nodes = listdir(mbes_path)
mbes_pattern = re.compile('^(XL_)*\d{4}_\d+_\d+_2903_EM2040\.all$')
mbes_filenames = [s for s in mbes_nodes if mbes_pattern.match(s)]
sorted(mbes_filenames, key=lambda filename: filename.replace("XL_", ""))

print(f"position files found: {pos_filenames}")
print(f"first and last: {pos_filenames[0] }, {pos_filenames[-1]}")

print(f"mbes nodes found: {mbes_nodes}")

# build excel sheet

# Basics
base_log_sheet[date_cell] = date_string
base_log_sheet[project_cell] = project_name
base_log_sheet[sheet_cell] = sheet_number
base_log_sheet[day_number_cell] = day_number
base_log_sheet[vessel_cell] = vessel

# POS files
base_log_sheet[first_pos_cell] = pos_filenames[0]
base_log_sheet[last_pos_cell] = pos_filenames[-1]

# SVP files
# for each svp_file add one to initial_SVP_cell, up to limit, then shift to next colomn
needed_svp_rows = len(svp_filenames) - initial_SVP_max_size
svp_colomns = ['B', 'K', 'T', 'AC']
for i in range(len(svp_filenames)):
    colomn_number = (math.ceil((i + 1)/initial_SVP_max_size)) - 1
    # throw error if number of casts is bigger than column array length * max column length
    row_number = ((i)%initial_SVP_max_size)
    cell = svp_colomns[colomn_number] + str(initial_SVP_row + row_number)#initial_SVP_column + str(initial_SVP_row + i)
    print(f"index {i} writing svp {svp_filenames[i]} at cell {cell}")
    base_log_sheet[cell] = svp_filenames[i]

# MBES
base_log_sheet[first_mbes_cell] = mbes_filenames[0].replace("XL_", "").split("_")[0]
base_log_sheet[last_mbes_cell] = mbes_filenames[-1].replace("XL_", "").split("_")[0]

base_log_workbook.save(filename = f"{log_path}/{sheet_number}_Vessel{vessel}_DN{day_number}_Log_{current_year}.xlsm")
