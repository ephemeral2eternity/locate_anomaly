# Get the user's server at a certain time
# Chen Wang, chenw@cmu.edu
# 2016-01-04
import json
from utils import *
from get_files import *


def get_all_servers(user_qoe_file):
    all_srvs = []
    user_qoe = json.load(open(user_qoe_file))
    for ch_id in sorted(user_qoe.keys(), key=int):
        srv = user_qoe[ch_id]['Server']
        if srv not in all_srvs:
            all_srvs.append(srv)
    return all_srvs


def get_srv_hop_id(srv, cur_route, rtt):
    hop_ids = sorted(cur_route.keys(), key=int, reverse=True)
    last_hop_id = hop_ids[0]
    if srv != cur_route[last_hop_id]['IP']:
        srv_id = str(int(last_hop_id) + 1)
        cur_route[srv_id] = {'IP' : srv, 'Addr' : srv, 'Time' : rtt}
    else:
        srv_id = last_hop_id

    return srv_id, cur_route

