#Data processing functions functions for the program

from fastq_config import fastq_config

import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
import gzip
import shutil


BINARY_CONV = {'A': '1000', 'G': '0100', 'C': '0010', 'T': '0001'}   #XOR operation and then counting bits will give 2 times the hamming distance when searching for neighbors

#Function to load a FastQ file and then process it
def processFastQ(sourcePath:str, currentConfig:fastq_config)->pd.DataFrame:
	
	dfTotal = pd.DataFrame()

	numDropOut = int(currentConfig.dropout_count_per100K * currentConfig.num_seq_per_chunk / 100000) 
	
	#read and process it in chunks since the FastQ files can be very large
	chunkSize = currentConfig.num_seq_per_chunk * currentConfig.num_fields
	
	with pd.read_csv(sourcePath, sep='\r', header=None, chunksize=chunkSize) as reader:
		cNum = 1
		for chunk in reader:
			print("Loading FastQ file chunk:", cNum)
			try:
				dfFastQ = pd.DataFrame(chunk.values.reshape(-1, currentConfig.num_fields), columns=currentConfig.fields)
			except ValueError:
				print("Error: Incorrect FastQ file format provided")
				return(pd.DataFrame())

			#delete fields which aren't going to be used
			for delete in currentConfig.fields_to_delete:		#more important to do this for very large files where we need to conserve space
				dfFastQ.drop(delete, axis=1, inplace=True)
			
			#find the barcodes with regex searching the string
			dfFastQ['barcode'] = dfFastQ['seq'].str.extract(pat=currentConfig.barcode_regex, expand=False)
			dfFastQ.dropna(inplace=True)   #drop out ones with no found anchor sequence
			
			#count the freq of same barcodes in that chunk
			dfFreq = dfFastQ['barcode'].value_counts().to_frame(name='count')
			dfFreq.index.rename('barcode', inplace=True) 
			dfFreq.reset_index(inplace=True)
			
			#add frequencies counted to previous chunks processed
			dfTotal = pd.concat([dfTotal, dfFreq])
			dfTotal = dfTotal.groupby('barcode')['count'].sum().reset_index()
			
			#check and combine near hamming distance neighors
			dfTotal = combineNearestNeighbors(dfTotal, currentConfig)
			
			#dropout any really low one-off type freq counts. This is a speed optimization but need to be really careful that this isn't set too high
			dfTotal = dfTotal[dfTotal['count'] > numDropOut]
			
			cNum += 1
	

	return(dfTotal)

	
#Function to search for nearest neighbors and then combine them
def combineNearestNeighbors(dfFreq:pd.DataFrame, currentConfig:fastq_config)->pd.DataFrame:
	
	#initially order them decending in count of freq so nested for loop logic below works effciently to start with
	dfFreq.sort_values(by = 'count', inplace = True, ascending = False, ignore_index = True)	
	#convert barcode to binary so we can use XOR logic to very quickly calculate hamming distance
	dfFreq['binary_int'] = dfFreq['barcode'].replace(BINARY_CONV, regex=True).apply(int, args=(2,))
	
	#create numpy lookup grid of all possible binary XOR calculations to very quickly determine hamming distance in the nested for loops below
	x, y = np.meshgrid(dfFreq.binary_int, dfFreq.binary_int)
	gridXOR = np.bitwise_xor(x, y) #huge speed benefit having numpy precalculate all at once if you have the memory! 
	##REMEMBER NOT TO CHANGE INDEX OF DATAFRAME AFTER THIS OR IT BREAKS THIS LOOKUP TABLE##
	print ("Memory used for nearest neighbor search:", gridXOR.nbytes//100000, "MB")


	freqLen = len(dfFreq.index)
	targetHam = currentConfig.hamming_dist
	countComb = 0
	#compare low freq counts to highest freq counts first as more likely to find a close match first and break out of nested loop and back to parent loop
	for rowLowFreq in range(freqLen-1, 0, -1):		#grab low freq from bottom of stack		
		print("Nearest Neighbors Search:", 100*(freqLen-rowLowFreq+1)//freqLen, "%", end="\r")
		for rowHighFreq in range(0, rowLowFreq, 1):		#and compare to high freq starting from top
						
			hamming = int(gridXOR[rowHighFreq][rowLowFreq]).bit_count() // 2 #need to divide by two since XOR of this 4 bit encoding and then counting bits is 2 for a hamming distance of 1. Encoding Used: {'A': '1000', 'G': '0100', 'C': '0010', 'T': '0001'}
			if (hamming <= targetHam) and (hamming > 0): 
				dfFreq.at[rowHighFreq, 'count'] += dfFreq.at[rowLowFreq, 'count'] #when we find one within the hamming distance then add them together
				dfFreq.drop(index=rowLowFreq, inplace=True)                    #and then delete low freq one
				countComb += 1
				break

	print("Number of similar barcode pairs combined:", countComb)
	dfFreq.sort_values(by='count', ascending = False, inplace = True, ignore_index = True)
	
	dfFreq.drop('binary_int', axis=1, inplace=True) #cleanup for memory purposes
	
	return(dfFreq)


#Function to produce graph showing cumulative sum of the frequency counts vs. rank. 
#The number of cells sequenced is shown by a vertical dashed line. 
#This is a good visual verification reality check to see if the number of cells intersects near the top of the plateau as expected.
def plotFreqGraph(dfFreq:pd.DataFrame, currentConfig:fastq_config)->plt.subplot:
	
	dfFreq['cum_sum'] = dfFreq['count'].cumsum()

	#Setup figure and axis for visual verification of result
	ax = plt.subplot()
	
	ax.plot(dfFreq.index, dfFreq["cum_sum"], color="black")
	ax.axvline(currentConfig.num_cells_seq, color="green", linestyle="dashed", label = "#Cells Sequenced")
	ax.set_xlabel("Rank")
	ax.set_ylabel("Cumulative Sum")
	ax.set_title("Visual Verification of Barcode Matching")
	plt.legend(loc='best')

	return(ax)


#Function to check if supplied file is a zipped (gz) file format
def isGZFile(filePath:str)->bool:
    with open(filePath, 'rb') as testFile:
        boolTest = (testFile.read(2) == b'\x1f\x8b')  #test if the magic number is 1f 8b which indicates it is a gz file

    return (boolTest)


#Function to to unzip a gz file
def unzipGZ(sourcePath:str, destPath:str, blockSize:int=65536)->bool:
    
    if not (Path(destPath).is_file()):			#make sure we haven't already unzipped it before

	    try:
	    	print("unzipping:", sourcePath)
	    	with gzip.open(sourcePath, 'rb') as sourceFile:
	    		with open(destPath, 'wb') as destFile:
	    			shutil.copyfileobj(sourceFile, destFile, blockSize)
	    	return(True)
	    except OSError:
	    	print("Error: File error unzipping:", sourcePath)
	    	return(False)
    else:
        print("Using previously unzipped file:", destPath)
        return(True)




	