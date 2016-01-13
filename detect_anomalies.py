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
from time_str import *


def merge_events(anomaly_pts, time_win):
    anomaly_events = {}

    event_no = 0
    if len(anomaly_pts) > 0:
        for srv in anomaly_pts.keys():
            anomaly_events[srv] = []
            sorted_anomaly_pts = sorted(anomaly_pts[srv])

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
                    anomaly_events[srv].append([event_start, event_end])
                    event_start = ts
                    event_end = ts
                    prePts = ts

            event_no += 1
            anomaly_events[srv].append([event_start, event_end])
            # print anomaly_events[srv]

    return anomaly_events, event_no


def add_anomaly_points(usr_anomaly_pts, new_anomaly_pts):
    for srv in new_anomaly_pts.keys():
        if srv in usr_anomaly_pts.keys():
            usr_anomaly_pts[srv] = usr_anomaly_pts[srv] + new_anomaly_pts[srv]
        else:
            usr_anomaly_pts[srv] = list(new_anomaly_pts[srv])
    return usr_anomaly_pts


def detect_anomaly_points(user_qoe, SLA, qoeType):
    anomalies = {}
    chunk_ids = sorted(user_qoe.keys(), key=int)
    ## Ignore the first two chunks that has bad QoE as it is impacted by the startup logic.
    for ch_id in chunk_ids[5:]:
        ch_qoe = float(user_qoe[ch_id][qoeType])
        ch_srv = user_qoe[ch_id]["Server"]
        if ch_qoe < SLA:
            if ch_srv not in anomalies.keys():
                anomalies[ch_srv] = []
            anomalies[ch_srv].append(float(user_qoe[ch_id]['TS']))
    return anomalies


def detect_anomaly(qoeFolder, SLA, qoeType):
    anomaly_user_pts = {}
    all_qoe_files = glob.glob(qoeFolder + "*.json")
    ## Detect anomaly users
    for qoe_file in all_qoe_files:
        # print qoe_file
        cur_user_qoe = json.load(open(qoe_file))
        anomaly_pts = detect_anomaly_points(cur_user_qoe, SLA, qoeType)

        user_file_name = ntpath.basename(qoe_file)
        user_name = user_file_name.split('_')[0]
        if user_name not in anomaly_user_pts.keys():
            anomaly_user_pts[user_name] = {}
        anomaly_user_pts[user_name] = add_anomaly_points(anomaly_user_pts[user_name], anomaly_pts)

    ## Filter anomaly points to events using time window
    anomaly_events = {}
    total_number_anomaly_events = 0
    anomaly_user_num = 0
    for user in anomaly_user_pts.keys():
        cur_anomaly_events, user_event_num = merge_events(anomaly_user_pts[user], timeWin)
        anomaly_events[user] = {}
        anomaly_events[user].update(cur_anomaly_events)
        total_number_anomaly_events += user_event_num
        if len(cur_anomaly_events.keys()) > 0:
            anomaly_user_num+=1
        print "Anomaly Events for user : ", user
        print cur_anomaly_events
        print "Anomaly User: ", user, " # of anomaly events : ", user_event_num

    return anomaly_events, anomaly_user_num, total_number_anomaly_events


def filter_events(anomaly_events, ts_range):
    filtered_events = {}
    all_users = anomaly_events.keys()
    total_number_anomaly_events = 0
    anomaly_user_num = 0
    for user in all_users:
        user_event_cnt = 0
        filtered_events[user] = {}
        for srv in anomaly_events[user].keys():
            cur_usr_srv_events = anomaly_events[user][srv]
            for cur_anomaly_ts_range in anomaly_events[user][srv]:
                if (cur_anomaly_ts_range[0] > ts_range[0]) and (cur_anomaly_ts_range[1] < ts_range[1]):
                    if srv not in filtered_events[user].keys():
                        filtered_events[user][srv] = []
                    filtered_events[user][srv].append(list(cur_anomaly_ts_range))
                    user_event_cnt += 1
                    total_number_anomaly_events += 1
        if user_event_cnt > 0:
            anomaly_user_num += 1

    return filtered_events, anomaly_user_num, total_number_anomaly_events


if __name__ == "__main__":
    ## Default data folder
    qoeFolder = "D://Data/cdn-monitor-data/azure-0112/qoe/"
    rstsFolder = "D://Data/cdn-monitor-data/azure-0112/anomaly/"

    SLA = 1.0
    timeWin = 30
    qoeType = "QoE2"
    # ts_range = [1452315600, 1452319200]         # AWS-0109 data
    ts_range = [1452571200, 1452574800]             # Azure-0112 data

    anomaly_events, anomaly_user_num, total_number_anomaly_events = detect_anomaly(qoeFolder, SLA, qoeType)

    print "Total number of users: ", len(anomaly_events.keys())
    print "Number of anomaly users: ", anomaly_user_num
    print "Total number of anomaly events: ", total_number_anomaly_events
    writeJson(rstsFolder, "anomaly-events", anomaly_events)

    anomaly_cnts = count_events_per_user(anomaly_events)
    draw_event_cnts(anomaly_cnts, toSave=False)
    plot_event_cnts(anomaly_cnts, toSave=False)

    anomaly_events, anomaly_user_num, total_number_anomaly_events = filter_events(anomaly_events, ts_range)
    print "Total number of users: " , len(anomaly_events.keys())
    print "Filtered number of anomaly users: ", anomaly_user_num
    print "Total number of anomaly events: ", total_number_anomaly_events

    anomaly_cnts = count_events_per_user(anomaly_events)
    draw_event_cnts(anomaly_cnts, toSave=False)
    plot_event_cnts(anomaly_cnts, toSave=False)

    filter_ts_str = ts2timestr(ts_range[0]) + "-" + ts2timestr(ts_range[1])

    writeJson(rstsFolder, "anomaly-events-" + filter_ts_str, anomaly_events)