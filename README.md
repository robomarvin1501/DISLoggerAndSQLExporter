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
4. You may now run logger.exe or the DataExporter

----------------------------
##Using logger.exe
When using the logger, one simply runs it and waits.  
To stop it, one clicks within the window, presses CTRL+c, and waits. The window will close itself.

----------------------------

##Building logger.exe
In order to build a distributable exe, one simply runs build_exe.py. Hopefully this will not need to be done regularly.  
build_exe.py makes use of PyInstaller, which can be a pain in the backside. If it no longer builds, and you don't know why, I wish you luck. It took me most of a day before it built for the first time.

----------------------------
#Overall explanation

##logger.py
The logger.py file is home to two classes, `DISReceiver`, and `DataWriter`.  
These should be used with the python `with` statement.  

`DISReceiver` was designed as an iterable so that even if what you do with the received data takes longer than it takes for the next piece of data to be received, you will still receive it.  
`DataWriter` was designed this way to ensure that no matter what, the file and ports will be properly closed when you are done with them.  


##LoggerSQLExporter.py
This file is home to 4 classes: `Exporter`, `LoggerPDU`, `EventReportInterpreter`, and `LoggerSQLExporter`.  
`Exporter`: This class has numerous generated instances throughout the code. An instance is generated for every table to which data is being exported, and it dumps the data it receives to that table on a seperate thread from the main thread.  
`LoggerPDU`: This is a wrapper on all the PDU classes from the opendis library. It adds the necessary fields of `packet_time` and `world_time`.  
`EventReportInterpreter`: This interprets any given event report from the received bytes into useful data, based off the data in the PDUEncoder. This standardised format can then be exported as necessary.  
`LoggerSQLExporter`: This class manages all the conversion of data into formats that SQL understands, and passes them on to the relevant instances of `Exporter`, to be sent to SQL.  

----------------------------

##Necessary directories
`***REMOVED***` houses the code that creates encoders based off what is found in ***REMOVED***. It also houses the `GeneralStructs.csv` file, for building such things.     
`encoders` houses the encoders that have been generated.  
`logs` These are the generated logs by the logger.

These are all necessary for running the code, even if the code is a standalone exe. `***REMOVED***` however, does not need all the code, just the `GeneralStructs.csv` file.  
This is because the target computer does not have ***REMOVED*** installed, and should *_NOT_* be trying to generate the PDUEncoder, or the SQL database 