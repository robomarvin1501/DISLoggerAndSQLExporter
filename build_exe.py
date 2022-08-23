import PyInstaller.__main__

PyInstaller.__main__.run([
    "logger.py",
    "--hidden-import=pyodbc",
    "--exclude-module=gevent",
    "--exclude-module=tkinter",
    # "--add-data=***REMOVED***/GeneralStructs.csv;csv",
    "--onefile"
])
