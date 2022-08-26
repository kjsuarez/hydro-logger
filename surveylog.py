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
import pdb

class SurveyLog:

    # x = SurveyLog("C:/Users/super/Documents/survey_project/OPR-W386-TJ-22", "H13609", "179", "2903")
    def __init__(self, drive_path, sheet_number, day_number, vessel, year=datetime.date.today().year):
        self.drive_path = drive_path
        self.sheet_number = sheet_number
        self.day_number = day_number
        self.sanitize_dn()
        self.year = year
        self.date_from_day_number = datetime.datetime.strptime(f'{year}-{day_number}','%Y-%j')
        self.date_month = self.date_from_day_number.month
        self.date_day = self.date_from_day_number.day
        self.vessel = vessel
        self.project_name = drive_path.split('/')[-1]

        # excel stuff
        today = datetime.date.today()
        self.date_string = f"{today.month}/{today.day}/{today.year}"

        self.date_cell = 'B9'
        self.project_cell = 'F9'
        self.sheet_cell = 'J9'
        self.day_number_cell = 'N9'
        self.vessel_cell = 'R9'
        self.first_hic_cell = 'B13'
        self.second_hic_cell = 'F13'
        self.initial_SVP_column = 'B'
        self.initial_SVP_row = 25
        self.initial_SVP_max_size = 4
        self.svp_cell_width = 9
        self.first_pos_cell = 'B21'; self.last_pos_cell = 'L21'
        self.first_mbes_cell = 'B33'; self.last_mbes_cell = 'B34'

        # filepath stuff
        self.year_day = f"{self.year}-{self.day_number}"
        self.vessel_year_sonar = f"{self.vessel}_{self.year}_EM2040"
        self.pos_path = f"{self.drive_path}/{self.sheet_number}/Data/Positioning/{self.vessel_year_sonar}/{self.year_day}" #drive_path+"/position"
        self.log_path = f"{self.drive_path}/{self.sheet_number}/Data/Acquisition_Logs/{self.vessel_year_sonar}/{self.year_day}"
        self.svp_path = f"{self.drive_path}/{self.sheet_number}/Data/SVP/{self.vessel_year_sonar}/SVP/{self.year_day}"
        self.mbes_path = f"{self.drive_path}/{self.sheet_number}/Data/MBES/{self.vessel_year_sonar}/{self.year_day}"

        base_excel_path = path.abspath(path.join(path.dirname(__file__), f'HXXXXX_VesselXXXX_DNXXX_Log_{self.year}.xlsm'))
        existing_excel_path = path.abspath(f"{self.log_path}/{self.sheet_number}_Vessel{self.vessel}_DN{self.day_number}_Log_{self.year}.xlsm")
        if path.isfile(existing_excel_path):
            workbook_to_use = existing_excel_path
        else:
            workbook_to_use = base_excel_path
        self.base_log_workbook = load_workbook(filename = workbook_to_use, keep_vba = True)
        self.base_log_sheet = self.base_log_workbook.active

    def sanitize_dn(self):
        day_number = str(self.day_number)
        off_by = 3 - len(day_number)
        zeros = "0" * off_by
        self.day_number = zeros + day_number

    def set_pos_filenames(self):
        position_nodes = listdir(self.pos_path)
        pos_pattern = re.compile('^.+\.\d{3}$')
        self.pos_filenames = [s for s in position_nodes if pos_pattern.match(s)]
        self.pos_filenames.sort()
        return self.pos_filenames

    def set_svp_filenames(self):
        svp_nodes = listdir(self.svp_path)
        svp_pattern = re.compile(f'^(mvp_{self.year}-0*{self.date_month}-0*{self.date_day}_\d+\.svp)|({self.year}_{self.day_number}_\d+\.svp)$')
        self.svp_filenames = [s for s in svp_nodes if svp_pattern.match(s)]
        self.svp_filenames.sort()
        return self.svp_filenames

    def set_first_and_last_mbes_lines(self):
        mbes_nodes = listdir(self.mbes_path)
        mbes_pattern = re.compile('^(XL_)*\d{4}_\d+_\d+_2903_EM2040\.all$')
        self.mbes_filenames = [s for s in mbes_nodes if mbes_pattern.match(s)]
        sorted(self.mbes_filenames, key=lambda filename: filename.replace("XL_", ""))
        self.first_mbes_line = ""
        self.last_mbes_line = ""
        if len(self.mbes_filenames) > 0:
            self.first_mbes_line = self.mbes_filenames[0].replace("XL_", "").split("_")[0]
            self.last_mbes_line = self.mbes_filenames[-1].replace("XL_", "").split("_")[0]
        return [self.first_mbes_line, self.last_mbes_line]

    def test(self):
        self.set_first_and_last_mbes_lines()

    # build excel sheet
    def build_log(self):
        # Basics
        self.base_log_sheet[self.date_cell] = self.date_string
        self.base_log_sheet[self.project_cell] = self.project_name
        self.base_log_sheet[self.sheet_cell] = self.sheet_number
        self.base_log_sheet[self.day_number_cell] = self.day_number
        self.base_log_sheet[self.vessel_cell] = self.vessel

        # POS files
        self.set_pos_filenames()
        try:
            self.base_log_sheet[self.first_pos_cell] = self.pos_filenames[0]
        except IndexError:
            self.base_log_sheet[self.first_pos_cell] = ""
        try:
            self.base_log_sheet[self.last_pos_cell] = self.pos_filenames[-1]
        except IndexError:
            self.base_log_sheet[self.last_pos_cell] = ""

        # SVP files
        self.set_svp_filenames()
        # for each svp_file add one to initial_SVP_cell, up to limit, then shift to next colomn
        needed_svp_rows = len(self.svp_filenames) - self.initial_SVP_max_size
        svp_colomns = ['B', 'K', 'T', 'AC']
        for i in range(len(self.svp_filenames)):
            colomn_number = (math.ceil((i + 1)/self.initial_SVP_max_size)) - 1
            # throw error if number of casts is bigger than column array length * max column length
            row_number = ((i)%self.initial_SVP_max_size)
            cell = svp_colomns[colomn_number] + str(self.initial_SVP_row + row_number)#initial_SVP_column + str(initial_SVP_row + i)
            print(f"index {i} writing svp {self.svp_filenames[i]} at cell {cell}")
            self.base_log_sheet[cell] = self.svp_filenames[i]

        # MBES
        self.set_first_and_last_mbes_lines()
        self.base_log_sheet[self.first_mbes_cell] = self.first_mbes_line
        self.base_log_sheet[self.last_mbes_cell] = self.last_mbes_line

        self.base_log_workbook.save(filename = f"{self.log_path}/{self.sheet_number}_Vessel{self.vessel}_DN{self.day_number}_Log_{self.year}.xlsm")

# x = SurveyLog("C:/Users/super/Documents/survey_project/OPR-W386-TJ-22", "H13609", "179", "2903")
