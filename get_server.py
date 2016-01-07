# Get the user's server at a certain time
# Chen Wang, chenw@cmu.edu
# 2016-01-04
import json
from utils import *
from get_files import *


def get_server(qoe_folder, user, ts):
    user_qoe_file = find_cur_file(qoe_folder, user, ts)
    user_qoe = json.load(open(qoe_folder + user_qoe_file))
    srv = user_qoe['0']['Server']
    return srv


def get_srv_hop_id(srv, cur_route, rtt):
    hop_ids = sorted(cur_route.keys(), key=int, reverse=True)
    last_hop_id = hop_ids[0]
    if srv != cur_route[last_hop_id]['IP']:
        srv_id = str(int(last_hop_id) + 1)
        cur_route[srv_id] = {'IP' : srv, 'Addr' : srv, 'Time' : rtt}
    else:
        srv_id = last_hop_id

    return srv_id, cur_route

