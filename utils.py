import json
import os
import socket

import numpy as np

from read_data.get_files import *


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


## ==================================================================================================
# Count the number of events
# @input : json_file_name --- json file name
# 		   json_var --- json variable
## ==================================================================================================
def count_events_per_user(anomaly_events):
	anomaly_cnts = {}
	for client in anomaly_events.keys():
		anomaly_cnts[client] = 0
	for client in anomaly_events.keys():
		for srv in anomaly_events[client].keys():
			# print "Anomaly event on client : ", client, " from server : ", srv, "is : ", anomaly_events[client][srv], \
			# 	"with length", len(anomaly_events[client][srv])
			anomaly_cnts[client] += len(anomaly_events[client][srv])
	return anomaly_cnts


## ==================================================================================================
# Count the hop precision of localization in the anomaly localization algorithm
# @input : anomaly_locs --- the located hops that can possible have an anomaly
# 		   trace_folder --- the tracefile folder
## ==================================================================================================
def get_localization_precision(anomaly_locs, trace_folder):
	## Initialize the count of events in each type of anomaly location.
	anomaly_precision = []

	all_event_ids = anomaly_locs.keys()
	for event_id in sorted(all_event_ids, key=int):
		cur_anomaly_hops = anomaly_locs[event_id]['anomaly-hops']
		anomaly_ts_range = anomaly_locs[event_id]['duration']
		anomaly_user = anomaly_locs[event_id]['user']
		anomaly_srv = anomaly_locs[event_id]['server']
		cur_route_file = find_cur_file(trace_folder, "TR_" + anomaly_user, anomaly_ts_range[1])
		user_routes = json.load(open(trace_folder+cur_route_file))
		user_srv_route = user_routes[anomaly_srv]

		anomaly_hop_num = len(cur_anomaly_hops.keys())
		total_hop = len(user_srv_route['Hops'].keys())
		if anomaly_srv not in user_srv_route['Hops'].keys():
			total_hop += 1
		if anomaly_user not in user_srv_route['Hops'].keys():
			total_hop += 1

		loc_precision = 1 - float(anomaly_hop_num - 1) / float(total_hop - 1)
		print event_id, total_hop, loc_precision
		anomaly_precision.append(loc_precision)
	return anomaly_precision


## ==================================================================================================
# Count the hop precision of localization over the number of peers
# @input : anomaly_locs --- the located hops that can possible have an anomaly
# 		   trace_folder --- the tracefile folder
## ==================================================================================================
def get_precision_over_peernum(anomaly_locs, trace_folder):
	## Initialize the count of events in each type of anomaly location.
	anomaly_precision_over_peernum = []

	all_event_ids = anomaly_locs.keys()
	for event_id in sorted(all_event_ids, key=int):
		cur_anomaly_hops = anomaly_locs[event_id]['anomaly-hops']
		anomaly_ts_range = anomaly_locs[event_id]['duration']
		anomaly_user = anomaly_locs[event_id]['user']
		anomaly_srv = anomaly_locs[event_id]['server']
		cur_route_file = find_cur_file(trace_folder, "TR_" + anomaly_user, anomaly_ts_range[1])
		user_routes = json.load(open(trace_folder+cur_route_file))
		user_srv_route = user_routes[anomaly_srv]

		anomaly_hop_num = len(cur_anomaly_hops.keys())
		total_hop = len(user_srv_route['Hops'].keys())
		if anomaly_srv not in user_srv_route['Hops'].keys():
			total_hop += 1
		if anomaly_user not in user_srv_route['Hops'].keys():
			total_hop += 1

		loc_precision = 1 - float(anomaly_hop_num - 1) / float(total_hop - 1)

		peer_num = len(anomaly_locs[event_id]['peers'])

		if peer_num == 0:
			print event_id, anomaly_user, anomaly_ts_range, loc_precision
		anomaly_precision_over_peernum.append([peer_num, loc_precision])

	anomaly_array = np.array(anomaly_precision_over_peernum)
	return anomaly_array