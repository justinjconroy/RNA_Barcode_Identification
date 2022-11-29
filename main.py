##11/28/2022##

from fastq_config import fastq_config

import sys
import os
from pathlib import Path

from tkinter import Tk as tk
from tkinter import filedialog as fd

import pandas as pd
import matplotlib.pyplot as plt

from processing import isGZFile, unzipGZ, processFastQ, plotFreqGraph

import time


#check python and pandas versions
if not ((sys.version_info[0] >= 3) and (sys.version_info[1] >= 10)):
	print("Error: Python version needs to be 3.10 and above")		#need Python 3.10 and newer for new int.bit_count() method introduced that is used in processing.combineNearestNeighbors() function
	sys.exit(False)

if not((int(pd.__version__[0]) >= 1) and (int(pd.__version__[2]) >= 2)):	#Pandas 1.2 introduced read_csv with chunksize that returns a context manager which is used in processing.processFastQ() function
	print("Error: Pandas version needs to be 1.2 and above")
	sys.exit(False)



#check if different config file was specified as first command line argument. This would be if running from an external script
if len(sys.argv) > 1:
	pathConfig = sys.argv[1]
else:
	pathConfig = "config_default.json" #otherwise load defaults

if not (Path(pathConfig).is_file()):
	print("Error: No config file found for path:", pathConfig)
	sys.exit(False)						#If something went wrong then return false which is important if this is being run from an external script
	
currentConfig = fastq_config(pathConfig)



#two different ways to input files to program:
#1. File path is passed via input_path in the config file. This enables easy scripting from another program or process
#2. If input_path is empty then query the user with an open dialog

root = tk()
root.withdraw() #hide main TK window as we only want the open/saveas dialogs

if currentConfig.input_path != "":
	pathFastQ = currentConfig.input_path
else:

	pathFastQ = fd.askopenfilename(initialdir= os.getcwd(),title= "Please select a FastQ file:", filetypes=currentConfig.file_types)
	root.update()

if not (Path(pathFastQ).is_file()):
	print("Error: Supplied path to FastQ file doesn't exist")
	sys.exit(False)


if currentConfig.output_csv_path != "":
	pathCSV = currentConfig.output_csv_path
else:
	pathCSV = fd.asksaveasfilename(initialdir= os.getcwd(),title= "Specify CSV output file for results:", filetypes=(("Comma-Separated Values files .csv", "*.csv"),))
	root.update()

if currentConfig.output_graph_path != "":
	pathGraph = currentConfig.output_graph_path
else:
	pathGraph = fd.asksaveasfilename(initialdir= os.getcwd(),title= "Specify graph output file", filetypes=((".png", "*.png"),))
	root.update()



#check if it needs to be unzipped or not
if isGZFile(pathFastQ):
	tempFilePath = pathFastQ + ".temp"
	if unzipGZ(pathFastQ, tempFilePath):
		pathFastQ = tempFilePath
	else:
		sys.exit(False)				
elif (pathFastQ[-3:] == ".gz"):
	print("Error: Corrupted .gz file")
	sys.exit(False)
else:
	tempFilePath = ""

#Get the result
startTime = time.time()
dfResult = processFastQ(pathFastQ, currentConfig)
if dfResult.empty:
	print("Error: no usable data processed from FastQ file")
	sys.exit(False)					

dfMatchedBarcodes = dfResult.iloc[:currentConfig.num_cells_seq]
print("Top Unique Barcode Candidates:")
print(dfMatchedBarcodes.to_string())
print("FastQ file finished processing in:", round(time.time() - startTime,2), "secs")

dfMatchedBarcodes.to_csv(pathCSV)
print("Results saved to:", pathCSV)

#create a cumulative sum graph of frequency count to show a visual verification on how close the result is 
resultsGraph = plotFreqGraph(dfResult, currentConfig)
plt.savefig(pathGraph)
print("Graph saved to:", pathGraph)

if currentConfig.show_graph:					#you'd likely want to turn this off if running from external script
	plt.show()


#check to see if we want to delete the temp unzipped file at end or not
if (tempFilePath != "") and currentConfig.delete_temp_files:
	os.remove(tempFilePath)	

root.destroy()

sys.exit(True)					#If being run from external script need to tell it that it was executed successfully at end

