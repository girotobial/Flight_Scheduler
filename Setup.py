import sys
import shutil

from cx_Freeze import setup, Executable

#base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(name='FlightScheduler',version='0.3',executables = [Executable("Gui_ui.py",base = "Win32GUI",targetName="Flight Scheduler.exe",icon="FS 1.6 Icon.ico")])

shutil.copyfile("C:\\Users\Anders\\PycharmProjects\\FdbFrontEnd\\FlightDB.db","C:\\Users\\Anders\\PycharmProjects\\FdbFrontEnd\\build\\exe.win32-3.4\\FlightDB.db")