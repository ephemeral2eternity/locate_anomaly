import time
import json
import os
import shutil
import logging
import socket
import datetime

# ================================================================================
## Get Client Agent Name
# ================================================================================
def getMyName():
	hostname = socket.gethostname()
	return hostname

## ==================================================================================================
# Write JSON file to the dataQoE folder
# @input : json_file_name --- json file name
# 		   json_var --- json variable
## ==================================================================================================
def writeJson(file_folder, json_file_name, json_var):
	# Create a cache folder locally
	try:
		os.stat(file_folder)
	except:
		os.mkdir(file_folder)

	if json_var:
		trFileName = file_folder + json_file_name + ".json"
		with open(trFileName, 'w') as outfile:
			json.dump(json_var, outfile, sort_keys = True, indent = 4, ensure_ascii=True)