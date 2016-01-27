from draws.draw_network import *
from draws.draw_utils import *
from draws.draw_qoe_related import *
from draws.draw_cdn_metrics import *
from read_data.load_metrics import *
from locate_anomaly import *
'''
## Cloud Network example
users_to_graph = ["planetlab2.cs.purdue.edu",
            "planetlab1.cs.purdue.edu",
            "planetlab3.wail.wisc.edu",
            "planetlab-2.cse.ohio-state.edu",
            "plink.cs.uwaterloo.ca",
            "planetlab2.unl.edu",
            "planetlab1.unl.edu",
            "pl2.ucs.indiana.edu"]

'''

## Network issues example
users_to_graph = ["cs-planetlab3.cs.surrey.sfu.ca",
            "cs-planetlab4.cs.surrey.sfu.ca",
            "planetlab02.cs.washington.edu",
            "planetlab4.cs.uoregon.edu",
            "planetlab3.cs.uoregon.edu",
            "planetlab1.cs.uoregon.edu"
        ]

'''
# Server anomaly issue example 2
users_to_graph = ["planetlab2.utdallas.edu",
            "planetlab1.arizona-gigapop.net",
            "pl2.cs.unm.edu",
            "planetlab3.arizona-gigapop.net",
            "planetlab2.arizona-gigapop.net",
            "pl3.cs.unm.edu"
        ]

## Server Issues
users_to_graph = ["planetlab-1.scie.uestc.edu.cn",
            "planetlab-2.sjtu.edu.cn",
            "ple2.ait.ac.th",
            "planetlab-2.scie.uestc.edu.cn",
            "pl1.pku.edu.cn",
            "pl2.pku.edu.cn",
            "planetlab-1.sjtu.edu.cn",
            "pl2.6test.edu.cn",
            "pl1.6test.edu.cn",
            "pl2.zju.edu.cn",
            "ple1.ait.ac.th"]

# Client Issues.
users_to_graph = ["planetlab2.rutgers.edu",
            "pl1.rcc.uottawa.ca",
            "planetlab3.rutgers.edu",
            "ebb.colgate.edu",
            "planetlab-03.cs.princeton.edu",
            "planetlab-01.cs.princeton.edu",
            "planetlab1.rutgers.edu",
            "planetlab1.temple.edu"
        ]
'''
qoe_folder = "D://Data/cdn-monitor-data/aws-0109/qoe/"
tr_folder = "D://Data/cdn-monitor-data/aws-0109/tr/"
hops_folder = "D://Data/cdn-monitor-data/aws-hops/"
figure_name="transit_anomaly_eg"

# anomaly_ts = [1452316804.122265, 1452316826.285391]           ## Client Anomalies
# anomaly_ts = [1452317401.70892, 1452317401.70892]           ## Server anomaly group 1
# anomaly_ts = [1452316350.693311,1452316401.794489]      ## Server anomaly group 2
anomaly_ts = [1452319093.334355, 1452319133.491066]      ## Client/Transit network anomaly group 2
# anomaly_ts = [1452315966.511148, 1452315966.511148]         ## Cloud Network example
# anomaly_user = "planetlab2.cs.purdue.edu"             ## Cloudnet anomaly user
# anomaly_user = "planetlab2.utdallas.edu"              ## Server example2 anomaly user
anomaly_user = "cs-planetlab3.cs.surrey.sfu.ca"

status_window = 30
if anomaly_ts[1] - anomaly_ts[0] < status_window:
    search_range = [anomaly_ts[1] - status_window, anomaly_ts[1]]
else:
    search_range = anomaly_ts
QoE_SLA = 1
route_files = []
users_status = {}
for user in users_to_graph:
    user_tr_file = find_cur_file(tr_folder, "TR_" + user, anomaly_ts[1])
    route_files.append(user_tr_file)
    user_qoe_file = find_cur_file(qoe_folder, user, anomaly_ts[1])
    cur_user_status = check_status(qoe_folder + user_qoe_file, QoE_SLA, search_range)
    users_status[user] = cur_user_status
print users_status

routes = read_route_info(tr_folder, route_files, info_name="Hops")
route_graph, srv_nodes, user_nodes = route2graph(routes, hops_folder, route_status=users_status)
colored_route_graph = color_graph(route_graph, routes, users_status, hops_folder, anomaly_user=anomaly_user)
draw_network(colored_route_graph, srv_nodes, user_nodes, hops_folder, isLabel=False, toSave=True, figName=figure_name)
