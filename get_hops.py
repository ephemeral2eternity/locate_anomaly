# Load all user's traceroute info to a server through time
# Chen Wang, chenw@cmu.edu
# 2016-01-04
import glob
import json
import ntpath
from utils import *
from ipinfo.host2ip import *
from ipinfo.ipinfo import *


def read_hop_info(hopinfo_path, hop_ip):
    default_hop_path = hopinfo_path + hop_ip + ".json"
    if os.path.exists(default_hop_path):
        try:
            hop_info = json.load(open(default_hop_path))
        except:
            os.remove(default_hop_path)
            if is_ip(hop_ip):
                hop_info = ipinfo(hop_ip)
                save_ipinfo(hopinfo_path, hop_info)
            else:
                hop_info = {}
    else:
        if not is_ip(hop_ip):
            hop_ip = host2ip(hop_ip)

        if is_ip(hop_ip):
            hop_info = ipinfo(hop_ip)
            save_ipinfo(hopinfo_path, hop_info)
        else:
            hop_info = {}
    return hop_info


def load_all_hops(trFolder):
    all_hops = {}

    total_hops = 0

    ## Get all traceroute files
    tr_files = glob.glob(trFolder + "*")

    for cur_tr in tr_files:
        print cur_tr
        tr_file_name = ntpath.basename(cur_tr)
        cur_user = tr_file_name.split('@')[1]
        if cur_user not in all_hops.keys():
            all_hops[cur_user] = {}

        srvs_hops = json.load(open(cur_tr))
        for srv in srvs_hops.keys():
            for hop_id in srvs_hops[srv].keys():
                cur_hop_name = srvs_hops[srv][hop_id]['Addr']
                if is_ip(cur_hop_name):
                    cur_hop_ip = cur_hop_name
                elif cur_hop_name == "*":
                    cur_hop_ip = "*"
                else:
                    cur_hop_ip = host2ip(cur_hop_name)

                if cur_hop_ip == "*":
                    continue
                elif is_reserved(cur_hop_ip):
                    continue

                if cur_hop_ip not in all_hops[cur_user].keys():
                    all_hops[cur_user][cur_hop_ip] = cur_hop_name
                    total_hops += 1

    print "Total number of hops: ", total_hops
    return all_hops


def load_usr_hops_on_srv(trFolder, srvName, user):
    out_tr_data = {}
    user_tr_files = glob.glob(trFolder + "tr@" + user + "@*")
    for cur_tr_file in user_tr_files:
        tr_file_name = ntpath.basename(cur_tr_file)
        tr_file_name_nosuffix = os.path.splitext(tr_file_name)[0]
        tr_file_ts = tr_file_name_nosuffix.split('@')[2]
        tr_data = json.load(open(cur_tr_file))
        hops_on_srv = tr_data[srvName]
        if hops_on_srv:
            out_tr_data[tr_file_ts] = hops_on_srv
    return out_tr_data


def find_cur_usr_hops(user_tr, denoted_ts):
    all_ts = sorted(user_tr.keys(), key=float, reverse=True)
    for ts in all_ts:
        if float(ts) < float(denoted_ts):
            return user_tr[ts]

    return user_tr[all_ts[-1]]


if __name__ == "__main__":
    # trFolder = "D://Data/cloud-monitor-data/gcloud-1219/tr/"
    # srvName = "agens-04"
    # user = "75-130-96-12.static.oxfr.ma.charter.com"
    # trData = load_usr_hops_on_srv(trFolder, srvName, user)
    # print trData

    # cur_ts = '1450488655.556846'
    # cur_hops = find_cur_usr_hops(trData, cur_ts)
    # print cur_hops
    # all_hops = load_all_hops(trFolder)
    # out_folder = "D://GitHub/locate_anomaly/data/"
    # writeJson(out_folder, "all_hops", all_hops)
    hopinfo_path = "D://Data/cdn-monitor-data/azure-hops/"
    hop_ip = "194.79.136.105"
    hop_info = read_hop_info(hopinfo_path, hop_ip)
    print hop_info