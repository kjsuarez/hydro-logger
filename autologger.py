import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
import datetime
from localStoragePy import localStoragePy
from surveylog import SurveyLog

localStorage = localStoragePy('hydro_logger', 'json')
# create the root window
root = tk.Tk()
root.title('Create survey log')
root.resizable(True, True)
root.geometry('550x250')

# The data SurveyLog uses to build log
transfer_drive_path_value = StringVar()
selected_day_number       = StringVar()
sheet_number_value        = StringVar()
vessel_value              = StringVar()

def select_dir():
    dir_path = fd.askdirectory(
        title='Open a directory',
        initialdir='/')
    transfer_drive_path_value.set(dir_path)
    localStorage.setItem("transfer_drive_path", dir_path)

def build_log():
    try:
        localStorage.setItem("sheet_number", sheet_number_value.get())
        localStorage.setItem("vessel", vessel_value.get())
        log = SurveyLog(
            transfer_drive_path_value.get(),
            sheet_number_value.get().strip(),
            selected_day_number.get(),
            vessel_value.get().strip()
        )
        log.build_log()
        messagebox.showinfo(
            title='Success',
            message="Survey log generated successfully"
        )
    except FileNotFoundError as e:
        messagebox.showerror(
            title=f'Log generation error: File expected at directory not found',
            message=str(e)
        )
    except Exception as e:
        messagebox.showerror(
            title=f'Unknown error',
            message=str(e)
        )
        raise e

def log_legal():
    return (len(sheet_number_value.get()) > 0 and
        len(vessel_value.get()) > 0 and
        len(transfer_drive_path_value.get()) > 0 and
        len(selected_day_number.get()) > 0)

def entry_callback(*args):
    if log_legal():
        submit_button.state(['!disabled'])
    else:
        submit_button.state(['disabled'])

# transfer drive dir
open_button = ttk.Button(
    root,
    text='select transfer drive path',
    command=select_dir
)
open_button.grid(column=0, row=0, sticky='w', padx=10, pady=10)
ttk.Label(root, textvariable=transfer_drive_path_value).grid(column=1, row=0)
transfer_drive_path_value.trace('w', entry_callback)
saved_path = localStorage.getItem("transfer_drive_path")
if saved_path != None:
    transfer_drive_path_value.set(saved_path)

# day number
ttk.Label(root, text="day number").grid(column=0, row=1)
day_number_options = range(1,365)
todays_day_of_year = datetime.date.today().timetuple().tm_yday
selected_day_number.set(day_number_options[todays_day_of_year - 1])
# localStorage.setItem("day_number", day_number_options[todays_day_of_year - 1])
w = OptionMenu(root, selected_day_number, *day_number_options)
w.grid(column=1, row=1, sticky='w')
selected_day_number.trace('w', entry_callback)

# sheet number
ttk.Label(root, text="sheet number").grid(column=0, row=2)
sheet_number_text = ttk.Entry(root, textvariable=sheet_number_value) #tk.Text(root, height=1, width=10)
sheet_number_text.grid(column=1, row=2, sticky='w')
sheet_number_value.trace('w', entry_callback)
saved_path = localStorage.getItem("sheet_number")
if saved_path != None:
    sheet_number_value.set(saved_path)

# vessel
ttk.Label(root, text="vessel").grid(column=0, row=3)
vessel_text = ttk.Entry(root, textvariable=vessel_value)#tk.Text(root, height=1, width=10)
vessel_text.grid(column=1, row=3, sticky='w')
vessel_value.trace('w', entry_callback)
saved_path = localStorage.getItem("vessel")
if saved_path != None:
    vessel_value.set(saved_path)

# submit
submit_button = ttk.Button(
    root,
    text='generate log',
    command=build_log
)
submit_button.state(['disabled'])
submit_button.grid(column=0, row=4, sticky='w', padx=10, pady=10)
entry_callback()

# run the application
root.mainloop()
