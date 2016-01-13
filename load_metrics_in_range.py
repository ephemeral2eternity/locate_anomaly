import json


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

### try to read the cdn logs
def load_cdnlogs(log_folder):
    return