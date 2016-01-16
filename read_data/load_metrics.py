import json
import glob
import re
import copy
from time_str import *
from utils import *
from ipinfo.host2ip import *


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


def get_all_srvs_in_range(qoe_folder, user_list, ts_range):
    all_user_srvs = []
    for usr in user_list:
        user_files = find_files_in_range(qoe_folder, usr, ts_range)
        for user_file in user_files:
            user_srvs = load_srvs_in_range(qoe_folder+user_file, ts_range)
            uniq_usr_srvs = list(set(user_srvs.values()))
            all_user_srvs = list(set(all_user_srvs) | set(uniq_usr_srvs))

    return all_user_srvs



def load_srvs_in_range(qoe_file, ts_range):
    srvs = {}
    # TO_BE_DONE
    qoe_trace = json.load(open(qoe_file))
    chunk_ids = sorted(qoe_trace.keys(), key=int)
    for ch_id in chunk_ids:
        cur_ts = float(qoe_trace[ch_id]['TS'])
        if (cur_ts >= ts_range[0]) and (cur_ts < ts_range[1]):
            srv = qoe_trace[ch_id]['Server']
            srvs[cur_ts] = srv

    return srvs


def load_srv_qoe_in_range(qoe_file, ts_range, qoe_type="QoE2"):
    qoes = {}
    # TO_BE_DONE
    qoe_trace = json.load(open(qoe_file))
    chunk_ids = sorted(qoe_trace.keys(), key=int)
    for ch_id in chunk_ids:
        cur_ts = float(qoe_trace[ch_id]['TS'])
        if (cur_ts >= ts_range[0]) and (cur_ts < ts_range[1]):
            srv = qoe_trace[ch_id]['Server']
            if srv not in qoes.keys():
                qoes[srv] = []
            qoes[srv].append(qoe_trace[ch_id][qoe_type])

    return qoes


def load_user_anomalies(anomaly_events_file, user_list, ts_range):
    user_anomalies = {}
    all_anomaly_events = json.load(open(anomaly_events_file))

    for user in user_list:
        cur_user_anomalies = all_anomaly_events[user]
        if user not in user_anomalies.keys():
            user_anomalies[user] = {}
        for srv in cur_user_anomalies.keys():
            cur_user_srv_anomalies = cur_user_anomalies[srv]
            # print cur_user_srv_anomalies
            for event in cur_user_srv_anomalies:
                if ((event[0] <= ts_range[1]) and (event[0] >= ts_range[0])) or \
                        ((event[1] >= ts_range[0]) and (event[1] <= ts_range[1])):
                    if srv not in user_anomalies[user].keys():
                        user_anomalies[user][srv] = []
                    user_anomalies[user][srv].append(event)

    return user_anomalies


def extract_logs(logFile, ts_range):
    all_cdn_logs = json.load(open(logFile))
    extracted_logs = {}
    for ts_str in all_cdn_logs.keys():
        ts = float(ts_str)
        if (ts <= ts_range[1]) and (ts >= ts_range[0]):
            extracted_logs[ts_str] = copy.deepcopy(all_cdn_logs[ts_str])

    return extracted_logs


def read_log_file(logfile):
    log_dict = {}
    logReader = open(logfile, 'r')
    log_lines = logReader.readlines()
    for line in log_lines:
        if line.startswith('#'):
            line_content = re.sub(r'^\#', '', line)
            pair = line_content.split(':')
            pair_key = pair[0]
            if pair_key == "Fields":
                fields = pair[1].split()
                # print fields
        else:
            line_items = line.split()
            ts_str = line_items[0] + ' ' + line_items[1]
            ts = timestr2utcts(ts_str, '%Y-%m-%d %H:%M:%S')
            log_dict[ts] = {}
            for i in range(len(line_items)):
                log_dict[ts][fields[i]] = line_items[i]

    #print log_dict
    return log_dict


def merge_logs(logs, new_log):
    logs_ts = sorted(logs.keys(), key=float)
    new_log_ts = sorted(new_log.keys(), key=float)
    for ts in new_log_ts:
        write_ts = ts
        while write_ts in logs_ts:
            write_ts = float(write_ts) + 0.1
            # print write_ts, ts

        logs[write_ts] = copy.deepcopy(new_log[ts])
    return logs


### try to read the cdn logs
def load_cdnlogs(log_folder):
    logs = {}
    all_logs = glob.glob(log_folder + "*")
    for log_file in all_logs:
        log = read_log_file(log_file)
        logs = merge_logs(logs, log)

    return logs


if __name__ == "__main__":
    cdn_log_folder = "D://Data/cdn-monitor-data/aws-0109/cdn-monitor/"
    cdn_log_json_folder = "D://Data/cdn-monitor-data/aws-0109/"
    cdn_logs_json = load_cdnlogs(cdn_log_folder)
    writeJson(cdn_log_json_folder, "cdn-logs", cdn_logs_json)
    # print cdn_logs
