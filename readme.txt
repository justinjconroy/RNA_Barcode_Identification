11/28/2022

PREREQUISITES:
-Needs Python 3.10 or newer
-Needs Pandas 1.2 or newer
-Needs Matplotlib

HOW TO RUN PROGRAM:
-main.py is the python file to run the program
-The program uses the config_default.json file to store all input config parameters. A custom one can be used instead if its path is supplied as a command line argument. This is useful for automating from an external script.  
-Two different ways to input FastQ files to program:
  #1. If input_path is empty in the config file then it will query the user with an open dialog (Default)
  #2. File path is passed via input_path in the config file. This enables easy scripting from another program or process
-When the program exits at the end it will return 1 if successful or 0 if it failed. This would allow an external script to verify that it ran successfully

LIST OF CONFIG PARAMETERS:
file_types
input_path
num_seq_per_chunk
delete_temp_files
fields 
fields_to_delete
barcode_field
barcode_len
separator_len
hamming_dist
dropout_count_per100K
anchor_seq
output_csv_path
output_graph_path
show_graph
num_cells_seq

-- file_types --   
List of List. FastQ file types to show in the open dialog when input_path is ""

-- input_path --
A string with the path to the FastQ file to process. If "" then program launches an open dialog to query user

-- num_seq_per_chunk --
Integer. The number of sequnce records to read and process from the FastQ file in one chunk. Larger FastQ files will be broken up into multiple chunks. Larger chunk sizes can be faster for processing but require more memory

-- delete_temp_files --
Boolean value. If the FastQ data was from a zipped file, does the program delete the temp unzipped file at the end

-- fields --
A list of strings of all named fields (lines) for each sequence record in the FastQ file

-- fields_to_delete --
A list of strings of named fields which will not be used in the program and should be deleted to save memory

-- barcode_field -- 
A string with the name of the field which contains the sequence with the barcode

-- barcode_len --
Integer. How large is the barcode

-- separator_len --
Integer. How many characters between the anchor sequence and the barcode

-- hamming_dist --
Integer. k-nearest-neighbors to use in the search and combine function 

-- dropout_count_per100k --
Integer. Processing speed optimization parameter. If after searching and combining nearest neighbors, there are still barcodes with very low frequency counts, just delete them. More important for optimizing processing of large files in multiple chunks. However, need to be careful not to set this too high.

-- anchor_seq --
A string holding the anchor sequence to search for

-- output_csv_path --
A string with the path for where to store the list of barcodes found. If "" then program launches a saveas dialog to query user

-- output_graph_path --
A string with the path for where to store a png of a graph showing cumulative sum of the frequency counts vs. rank. The number of cells sequenced is shown by a vertical dashed line. This is a good visual verification reality check to see if the number of cells intersects near the top of the plateau as expected. If "" then program launches a saveas dialog to query user

-- show_graph --
Boolean. Whether we show that graph at the end of processing. Should be set to 0 if running from an external script

-- num_cells_seq --
Integer. The number of cells sequenced 