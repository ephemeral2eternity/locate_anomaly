# Locate anomalies via user QoE and their route info
# Chen Wang, chenw@cmu.edu
# 2016-01-04
import glob
import json
import os
import shutil
import ntpath
from utils import *
from get_hops import *
from ipinfo.host2ip import *
from ipinfo.ipinfo import *
from get_groups import *
from get_files import *
from get_server import *

def load_qoe_in_range(qoe_file, ts_range):
    qoes = {}
    # TO_BE_DONE
    qoe_trace = json.load(open(qoe_file))
    chunk_ids = sorted(qoe_trace.keys(), key=int)
    for ch_id in chunk_ids:
        cur_ts = float(qoe_trace[ch_id]['TS'])
        if (cur_ts >= ts_range[0]) and (cur_ts < ts_range[1]):
            qoes[cur_ts] = qoe_trace[ch_id]['QoE2']

    if qoes:
        new_range = [min(qoes.keys(), key=float), max(qoes.keys(), key=float)]
    else:
        new_range = ts_range
    return qoes, new_range


def check_status(qoe_file, QoE_SLA, ts_range, percent=0.95):
    qoes, new_range = load_qoe_in_range(qoe_file, ts_range)
    qoe_values = qoes.values()
    total_num = len(qoe_values)
    if total_num > 0:
        abnormal_vals = [x for x in qoe_values if x <= QoE_SLA]
        if len(abnormal_vals) > 0:
            status = False
        else:
            status = True
    else:
        status = False

    return status, new_range


def label_route(tr_folder, peer, ts_range):
    normal_hops = {}
    route_file = find_cur_file(tr_folder, "TR_" + peer, ts_range[0])
    route_dict = json.load(open(tr_folder + route_file))
    route = route_dict['Hops']
    hop_ids = sorted(route.keys(), key=int)
    for i in hop_ids:
        hop_ip = route[i]['IP']
        if (is_ip(hop_ip)) and (not is_reserved(hop_ip)) and (hop_ip not in normal_hops.keys()):
            normal_hops[hop_ip] = []
            if peer not in normal_hops[hop_ip]:
                normal_hops[hop_ip].append(peer)

    return normal_hops

def merge_normal_hops(normal_hops, new_normal_hops):
    for ip in new_normal_hops.keys():
        if ip in normal_hops.keys():
            normal_hops[ip] = list(set(normal_hops[ip]) | set(new_normal_hops[ip]))
        else:
            normal_hops[ip] = new_normal_hops[ip]

    return normal_hops


def get_all_normal_hops(peers, qoe_folder, tr_folder, search_range, QoE_SLA):
    normal_hops = {}
    for peer in peers:
        qoe_files = find_files_in_range(qoe_folder, peer, search_range)
        for cur_file in qoe_files:
            route_status, sub_range = check_status(qoe_folder+cur_file, QoE_SLA, search_range)
            if route_status:
                cur_normal_hops = label_route(tr_folder, peer, sub_range)
                normal_hops = merge_normal_hops(normal_hops, cur_normal_hops)
                # print "Total number of normal hops: ", len(normal_hops.keys())
    return normal_hops


def locate_anomaly(user, ts_range, all_peers, qoe_folder, tr_folder, hop_folder, QoE_SLA, search_win):
    locations = {}
    normal_hop_details = {}
    anomaly_start = ts_range[0]
    search_range = [anomaly_start - search_win, ts_range[1]]
    normal_hops = get_all_normal_hops(all_peers, qoe_folder, tr_folder, search_range, QoE_SLA)
    # print "All normal hops: ", normal_hops
    cur_route_file = find_cur_file(tr_folder, "TR_" + user, anomaly_start)
    cur_route_dict = json.load(open(tr_folder + cur_route_file))
    cur_route = cur_route_dict['Hops']
    cur_rtt = cur_route_dict['RTT']
    hop_ids = sorted(cur_route.keys(), key=int)

    ## Get info from the user
    user_info = read_user_info(user)
    if 'AS' not in user_info.keys():
        print "[Error]Do not detect anomalies for client : ", user, " as its hostname is wrong!"
        user = "planetlab1.research.nicta.com.au"
        user_info = read_user_info(user)

    user_id = '0'
    cur_route[user_id] = {'IP' : user_info['ip'], 'Addr' : user, 'Time' : 0.0}
    user_as = user_info['AS']

    ## Get info from the user
    srv = get_server(qoe_folder, user, anomaly_start)
    srv_id, cur_route = get_srv_hop_id(srv, cur_route, cur_rtt)
    srv_info = read_hop_info(hop_folder, srv)
    srv_as = srv_info['AS']

    hop_ids = sorted(cur_route.keys(), key=int)

    for id in hop_ids:
        hop_ip = cur_route[id]['IP']
        if (hop_ip == '*') or is_reserved(hop_ip):
            # print "Hop ", hop_ip, " ignored!"
            continue
        hop_info = read_hop_info(hop_folder, hop_ip)
        if hop_ip not in normal_hops.keys():
            if id == user_id:
                locations[hop_ip] = 'client'
            elif id == srv_id:
                locations[hop_ip] = 'server'
            else:
                if 'AS' not in hop_info.keys():
                    locations[hop_ip] = "unknown"
                    continue
                if hop_info['AS'] == user_as:
                    locations[hop_ip] = 'client_net'
                elif hop_info['AS'] == srv_as:
                    locations[hop_ip] = 'cloud_net'
                else:
                    locations[hop_ip] = 'transit_net'

            # print "[Anomaly hop]: ", hop_ip, " with info ", locations[hop_ip]
        else:
            normal_hop_details[hop_ip] = normal_hops[hop_ip]

    if not locations:
        print "[Bug] location is empty. client ip is excluded. There must be bugs in the program!"

    return locations, normal_hop_details


def locate_all_anomaly_events(anomaly_events, qoe_folder, tr_folder, hop_info_folder, QoE_SLA=2.0, search_win = 10):
    anomaly_locations = {}
    anomaly_users = anomaly_events.keys()
    total_event_id = 0
    for user in anomaly_users:
        last_mile_peers = get_last_mile_peers(qoe_folder, user)
        user_anomaly_events = anomaly_events[user]
        for event_id in sorted(user_anomaly_events.keys(), key=int):
            anomaly_ts_range = user_anomaly_events[event_id]
            print "Anomaly event ", event_id, "for user", user, " in time range ", anomaly_ts_range
            first_mile_peers = get_first_mile_peers(qoe_folder, user, anomaly_ts_range[0])
            all_peers = list(set(first_mile_peers) | set(last_mile_peers))
            # print "All peers for the event: ", all_peers
            locations, normal_hop_details = locate_anomaly(user, anomaly_ts_range, all_peers, qoe_folder, tr_folder, hop_info_folder, QoE_SLA, search_win)
            total_event_id += 1
            anomaly_locations[total_event_id] = {'user' : user, 'duration' : anomaly_ts_range, 'anomaly-hops' : locations, 'normal-hops' : normal_hop_details}

    return anomaly_locations

if __name__ == "__main__":
    ## Default data folder
    qoeFolder = "D://Data/cdn-monitor-data/azure-0105/qoe/"
    trFolder = "D://Data/cdn-monitor-data/azure-0105/tr/"
    hopinfoFolder = "D://Data/cdn-monitor-data/azure-hops/"
    anomaly_folder = "D://Data/cdn-monitor-data/azure-0105/anomaly/"
    anomaly_events_file = "D://Data/cdn-monitor-data/azure-0105/anomaly/anomaly-events.json"

    QoE_SLA = 1.0
    anomaly_events = json.load(open(anomaly_events_file))
    all_anomaly_events_locations = locate_all_anomaly_events(anomaly_events, qoeFolder, trFolder, hopinfoFolder, QoE_SLA)
    writeJson(anomaly_folder, "anomaly-locations", all_anomaly_events_locations)
