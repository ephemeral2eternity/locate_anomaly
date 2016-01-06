# Locate anomalies via user QoE and their route info
# Chen Wang, chenw@cmu.edu
# 2016-01-04
import glob
import json
import os
import shutil
import ntpath
from utils import *
from get_clients_info import *
from draw_graphs import *

def merge_events(anomaly_pts, time_win):
    anomaly_events = {}

    if len(anomaly_pts) > 0:
        event_no = 0
        sorted_anomaly_pts = sorted(anomaly_pts)
        prePts = sorted_anomaly_pts[0]
        event_start = prePts
        event_end = prePts
        for ts in sorted_anomaly_pts[1:]:
            if ts - prePts < time_win:
                prePts = ts
                event_end = ts
                continue
            else:
                event_no += 1
                event_end = prePts
                anomaly_events[event_no] = [event_start, event_end]
                event_start = ts

        event_no += 1
        anomaly_events[event_no] = [event_start, event_end]

    return anomaly_events


def detect_anomaly_points(user_qoe, SLA, qoeType):
    anomalies = []
    chunk_ids = sorted(user_qoe.keys(), key=int)
    ## Ignore the first two chunks that has bad QoE as it is impacted by the startup logic.
    for ch_id in chunk_ids[2:]:
        ch_qoe = float(user_qoe[ch_id][qoeType])
        if ch_qoe < SLA:
            anomalies.append(float(user_qoe[ch_id]['TS']))
    return anomalies

def detect_anomaly(qoeFolder, SLA, qoeType):
    anomaly_user_pts = {}
    all_qoe_files = glob.glob(qoeFolder + "*.json")
    ## Detect anomaly users
    for qoe_file in all_qoe_files:
        cur_user_qoe = json.load(open(qoe_file))
        anomaly_pts = detect_anomaly_points(cur_user_qoe, SLA, qoeType)

        user_file_name = ntpath.basename(qoe_file)
        user_name = user_file_name.split('_')[0]
        if user_name not in anomaly_user_pts.keys():
            anomaly_user_pts[user_name] = []
        anomaly_user_pts[user_name] += anomaly_pts


    ## Filter anomaly points to events using time window
    anomaly_events = {}
    total_number_anomaly_events = 0
    anomaly_user_num = 0
    for user in anomaly_user_pts.keys():
        cur_anomaly_events = merge_events(anomaly_user_pts[user], timeWin)
        anomaly_events[user] = cur_anomaly_events
        total_number_anomaly_events += len(cur_anomaly_events.keys())
        if len(cur_anomaly_events.keys()) > 0:
            anomaly_user_num+=1
        ## print "Anomaly Events for user : ", user
        ## print cur_anomaly_events
        ## print "Anomaly User: ", user, " # of anomaly events : ", len(cur_anomaly_events.keys())

    return anomaly_events, anomaly_user_num, total_number_anomaly_events

def count_event(anomaly_events):
    anomaly_cnts = {}
    for client in anomaly_events.keys():
        anomaly_cnts[client] = len(anomaly_events[client].keys())

    return anomaly_cnts

if __name__ == "__main__":
    ## Default data folder
    qoeFolder = "D://Data/cdn-monitor-data/azure-0105/qoe/"
    rstsFolder = "D://Data/cdn-monitor-data/azure-0105/anomaly/"

    SLA = 1.0
    timeWin = 30
    qoeType = "QoE2"

    anomaly_events, anomaly_user_num, total_number_anomaly_events = detect_anomaly(qoeFolder, SLA, qoeType)

    print "Total number of users: ", len(anomaly_events.keys())
    print "Number of anomaly users: ", anomaly_user_num
    print "Total number of anomaly events: ", total_number_anomaly_events

    anomaly_cnts = count_event(anomaly_events)
    draw_event_cnts(anomaly_cnts, isDraw=False)
    plot_event_cnts(anomaly_cnts, isDraw=True)

    writeJson(rstsFolder, "anomaly-user", anomaly_events)