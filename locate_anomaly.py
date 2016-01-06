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

def load_qoe_in_range(qoe_file, ts_range):
    qoes = {}
    # TO_BE_DONE
    return qoes


def get_all_hop_states(peers, qoe_folder, tr_folder, hop_info_folder, search_range, QoE_SLA):

    hop_states = {}
    for peer in peers:
        qoe_files = find_files_in_range(qoe_folder, search_range)
        for cur_file in qoe_files:
            qoes = load_qoe_in_range(qoe_folder + cur_file, search_range)
            cur_file_ts = sorted(qoes.keys(), key=float)[0]
            route_file = find_cur_file(tr_folder, "TR_" + peer, cur_file_ts)
            route = json.load(open(tr_folder + route_file))

    # TO_BE_DONE
    return hop_states


def locate_anomaly(anomaly_events, qoe_folder, tr_folder, hop_info_folder, QoE_SLA=2.0, search_win = 10):
    anomaly_users = anomaly_events.keys()
    for user in anomaly_users:
        last_mile_peers = get_last_mile_peers(qoe_folder, user)
        user_anomaly_events = anomaly_events[user]
        for event_id in user_anomaly_events:
            anomaly_ts_range = user_anomaly_events[event_id]
            anomaly_start = anomaly_ts_range[0]
            first_mile_peers = get_first_mile_peers(qoe_folder, user, anomaly_start)
            all_peers = first_mile_peers + list(set(first_mile_peers) - set(last_mile_peers))
            search_range = [anomaly_start - search_win, anomaly_ts_range[1]]
            hop_states = get_all_hop_states(all_peers, qoe_folder, tr_folder, hop_info_folder, search_range, QoE_SLA)


if __name__ == "__main__":
    ## Default data folder
    qoeFolder = "D://Data/cdn-monitor-data/azure-0105/qoe/"
    trFolder = "D://Data/cdn-monitor-data/azure-0105/tr/"
    user_list_file = "D://Data/cloud-monitor-data/gcloud-1219/users/users_on_srv.json"
    srv = "104.154.83.246"
    srvName = "agens-04"

    users = json.load(open(user_list_file))
    users_on_srv = users[srv]

    print users_on_srv

    node_qoes = {}
    QoE_SLA = 2

    for user in users_on_srv:
        user_tr = load_usr_hops_on_srv(trFolder, srvName, user)

        user_qoe_files = glob.glob(qoeFolder + "/" + srv + "/" + user + "*")
        print user_qoe_files
        for cur_user_qoe_file in user_qoe_files:
            cur_user_qoe = json.load(open(cur_user_qoe_file))
            cur_ts = cur_user_qoe['0']['TS']
            user_hops = find_cur_usr_hops(user_tr, cur_ts)

            hop_ids = sorted(user_hops.keys(), key=int)

            for hop_id in hop_ids:
                cur_hop_name = user_hops[hop_id]['Addr']

                if is_hostname(cur_hop_name):
                    cur_ip = host2ip(cur_hop_name)
                else:
                    cur_ip = cur_hop_name

