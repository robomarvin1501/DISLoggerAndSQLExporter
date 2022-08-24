DataExporter
=============

Welcome to the DataExporter, and Logger of the ***REMOVED***.  

This code was created by ***REMOVED***, with version 1.0 being released on 2022.08.23.  
The purpose is to provide logging of a simulation, following the DIS standard, and to replace the logger from MAK, and the LoggerSQLExporter created to export said files.  
----------------------------

##Starting a new experiment
I shall take you through this procedure, to grant you the knowledge of with what you are dealing, and how to do so.

1. DataExporterConfig.json
   - One must set all the fields within this file. The message length field can usually be ignored.
2. Run update_pduencoder.py on a machine that has ***REMOVED***. This:
   1. Creates the PduEncoder.json file
   2. Creates the SQL code to make the SQL tables
   3. Makes the SQL tables
3. Put the generated sub-directory of `encoders` into the `encoders` directory on the target machine
4. You may now run logger.exe/LoggerSQLExporter

----------------------------
##Using logger.exe
When using the logger, one simply runs it and waits.  
To stop it, one clicks within the window, presses CTRL+c, and waits. The window will close itself.

----------------------------

##Building logger.exe
In order to build a distributable exe, one simply runs build_exe.py. Hopefully this will not need to be done regularly.  
build_exe.py makes use of PyInstaller, which can be a pain in the backside. If it no longer builds, and you don't know why, I wish you luck. It took me most of a day before it built for the first time.