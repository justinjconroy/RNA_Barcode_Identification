#Helper class to load in config file from json and manage settings

import json

class fastq_config:

	def __init__(self, jsonFormat:str):
        
		with open(jsonFormat, 'r') as fp:
			data = json.load(fp)

		self._file_types = tuple([tuple(t) for t in data['file_types']]) #Only used for open dialog if input_path is blank. Need to convert for tuple of tuples for tkinter open dialog
		self._input_path = data['input_path']
		self._num_seq_per_chunk = data['num_seq_per_chunk']
		self._delete_temp_files = data['delete_temp_files']
		self._fields = data['fields']
		self._fields_to_delete = data['fields_to_delete']
		self._barcode_field = data['barcode_field']
		self._barcode_len = data['barcode_len']
		self._separator_len = data['separator_len']
		self._anchor_seq = data['anchor_seq']
		self._hamming_dist = data['hamming_dist']
		self._dropout_count_per100K = data['dropout_count_per100K']
		self._output_csv_path = data['output_csv_path']
		self._output_graph_path = data['output_graph_path']
		self._show_graph = data['show_graph']
		self._num_cells_seq = data['num_cells_seq']
    
	@property
	def barcode_regex(self):
		return("(.{"+ str(self._barcode_len) + "}(?=" + ("." * self._separator_len) + self._anchor_seq + "))")  #Generate REGEX pattern to find anchor sequence and then slice out barecode_len number of characters to the left of it after seperator_len

	@property
	def file_types(self):
		return(self._file_types)

	@property
	def input_path(self):
		return(self._input_path)

	@property
	def num_seq_per_chunk(self):
		return(self._num_seq_per_chunk)

	@property
	def delete_temp_files(self):
		return(self._delete_temp_files)

	@property
	def fields(self):
		return(self._fields)

	@property
	def fields_to_delete(self):
		return(self._fields_to_delete)

	@property
	def num_fields(self):
		return(len(self._fields))

	@property
	def barcode_field(self):
		return(self._barcode_field)

	@property
	def barcode_len(self):
		return(self._barcode_len)

	@property
	def separator_len(self):
		return(self._separator_len)

	@property
	def anchor_seq(self):
		return(self._anchor_seq)

	@property
	def hamming_dist(self):
		return(self._hamming_dist)

	@property
	def dropout_count_per100K(self):
		return(self._dropout_count_per100K)

	@property
	def output_csv_path(self):
		return(self._output_csv_path)

	@property
	def output_graph_path(self):
		return(self._output_graph_path)

	@property
	def show_graph(self):
		return(self._show_graph)

	@property
	def num_cells_seq(self):
		return(self._num_cells_seq)