import numpy as np
from ipinfo.ipinfo import *

def three_sigma_detection(dataDict):
    vals = dataDict.values()
    # print vals
    val_ave = np.mean(vals)
    val_std = np.std(vals)
    three_sigma = val_std * 3

    outliers = {}
    for ts in sorted(dataDict.keys()):
        cur_val = dataDict[ts]
        if cur_val >= val_ave + three_sigma:
            outliers[ts] = cur_val

    return outliers, val_ave, three_sigma


def get_outlier_clients(extracted_srv_logs, outliers):
    outlier_ts = outliers.keys()
    outlier_clients = []
    for ts in outlier_ts:
       outlier_log = extracted_srv_logs[str(ts)]
       client_ip = outlier_log["c-ip"]
       client_hostname = ip2host(client_ip)
       outlier_clients.append(client_hostname)

    return outlier_clients


