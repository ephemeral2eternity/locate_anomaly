import glob
import ntpath
import re
import json
import copy
from ipinfo.host2ip import *
from ipinfo.ipinfo import *
import networkx as nx
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from draw_utils import *
# from pylab import *

def draw_network(graph_obj, srv_nodes, user_nodes, hopsPath, isLabel=False, toSave=False, figName="localization_eg"):
    # pos=nx.spring_layout(graph_obj, k=0.6, iterations=400)
    pos = nx.graphviz_layout(graph_obj, prog="neato", args="-Tps -Gsplines=true -Goverlap=scalexy -Gepsilon=5")
    # pos = nx.graphviz_layout(graph_obj, prog="neato", args="-Tps -Gsplines=true -Goverlap=scalexy -Gepsilon=5")

    if isLabel:
        labels = {}
        #for labeling outside the node
        offset =0.05
        pos_labels = {}
        keys = pos.keys()
        for key in keys:
            x, y = pos[key]
            pos_labels[key] = (x+offset, y+offset)
            if key in srv_nodes:
                labels[key] = verify_hostname(key, hopsPath)
            elif key in user_nodes:
                labels[key] = verify_hostname(key, hopsPath)
            else:
                labels[key] = ''
        nx.draw_networkx_labels(graph_obj, pos=pos_labels, labels=labels, fontsize=2, font_color='k')

    #Get all distinct node classes according to the node shape attribute
    nodeShapes = set((aShape[1]["node_shape"] for aShape in graph_obj.nodes(data = True)))

    f, ax = plt.subplots()
    p_handlers = {}
    for aShape in nodeShapes:
        curNodesDict = [sNode for sNode in filter(lambda x: x[1]["node_shape"] == aShape,graph_obj.nodes(data = True))]
        curNodes = [cNode[0] for cNode in curNodesDict]
        nodesizelist = [cNode[1]["node_size"] for cNode in curNodesDict]
        # print nodesizelist
        nodecolorlist = [cNode[1]["node_color"] for cNode in curNodesDict]
        # print nodecolorlist
        p_handlers[aShape] = nx.draw_networkx_nodes(graph_obj, pos, node_shape = aShape, nodelist=curNodes, node_size=nodesizelist, node_color=nodecolorlist, alpha = 0.5)
        # nx.draw_networkx_nodes(graph_obj, pos, node_shape=aShape, nodelist=curNodes, alpha = 0.5)

    edge_colors = [curEdge[2]["edge_color"] for curEdge in graph_obj.edges(data = True)]
    nx.draw_networkx_edges(graph_obj, pos, edge_color=edge_colors)
    # nx.draw_networkx_edges(graph_obj, pos)
    # print graph_obj.edges(data = True)

    red_patch = mpatches.Patch(color='r', label='Anomaly', alpha=0.5)
    green_patch = mpatches.Patch(color='g', label='Normal', alpha=0.5)
    p_lg = [p_handlers[x] for x in ['^', 'o', 's']]
    p_lg.append(green_patch)
    p_lg.append(red_patch)
    plt.legend(p_lg, ["Clients","Routers", "Servers", "Normal", "Anomaly"], loc=4)
    plt.axis('off')
    plt.show()

    if toSave:
        save_fig(f, figName)

# def read_routes():
#    return
def color_graph(route_graph, routes, users_status, hops_folder, anomaly_user=None):
    node_status = {}
    for user in routes.keys():
        cur_user_routes = routes[user]
        for srv in cur_user_routes.keys():
            print "Color route from ", user, " to server:", srv
            cur_route = cur_user_routes[srv]
            cur_clean_route = simplify_route(cur_route, user, srv, hops_folder)
            if srv not in users_status[user].keys():
                continue
            cur_route_status = users_status[user][srv]

            route_ids = sorted(cur_clean_route.keys(), key=int)

            '''
            client_node = cur_clean_route[route_ids[0]]
            if client_node in node_status.keys():
                node_status[client_node] = cur_route_status & node_status[client_node]
            else:
                node_status[client_node] = cur_route_status
            '''

            for cur_id in route_ids:
                cur_node = cur_clean_route[cur_id]
                if cur_node in node_status.keys():
                    node_status[cur_node] = cur_route_status | node_status[cur_node]
                else:
                    node_status[cur_node] = cur_route_status

    node_colors = {}
    for node in node_status.keys():
        if node_status[node]:
            node_colors[node] = 'g'
        else:
            node_colors[node] = 'r'
            print node

    if anomaly_user:
        anomaly_user_ip = host2ip(anomaly_user)
        node_colors[anomaly_user_ip] = 'r'

    edge_colors = {}
    for (u, v) in route_graph.edges():
        cur_edge = (u, v)
        if node_status[u] and node_status[v]:
            edge_colors[cur_edge] = 'g'
        else:
            edge_colors[cur_edge] = 'r'

    nx.set_node_attributes(route_graph, "node_color", node_colors)
    nx.set_edge_attributes(route_graph, "edge_color", edge_colors)

    return route_graph


def simplify_route(cur_route, user, srv, hops_folder):
    updated_route = {}

    if not is_ip(user):
        user_ip = host2ip(user)
    else:
        user_ip = user
    if not is_ip(srv):
        srv_ip = host2ip(srv)
    else:
        srv_ip = srv

    updated_id = 0
    hop_ids = sorted(cur_route.keys(), key=int)
    first_hop_id = hop_ids[0]
    if user_ip != cur_route[first_hop_id]['IP']:
        start_hop_id = 0
    else:
        start_hop_id = 1
    updated_route[updated_id] = user_ip
    updated_id += 1

    for hop_id in hop_ids[start_hop_id:]:
        cur_hop_ip = cur_route[hop_id]['IP']
        if (cur_hop_ip == "*") or is_reserved(cur_hop_ip):
            continue
        else:
            updated_route[updated_id] = cur_route[hop_id]['IP']
            updated_id += 1

    last_hop_id = hop_ids[-1]
    if cur_route[last_hop_id]['IP'] != srv_ip:
        updated_route[updated_id] = srv_ip

    return updated_route


def route2graph(user_routes, hops_folder, route_status=None):
    users = user_routes.keys()
    route_graph = nx.Graph()
    srv_nodes = []
    user_nodes = []
    for user in users:
        cur_user_routes = user_routes[user]
        if is_ip(user):
            user_ip = user
        else:
            user_ip = host2ip(user)
        if user_ip not in user_nodes:
            user_nodes.append(user_ip)

        for srv in cur_user_routes.keys():
            if route_status:
                if srv not in route_status[user].keys():
                    continue

            # print user, srv
            if is_ip(srv):
                srv_ip = srv
            else:
                srv_ip = host2ip(srv)

            if srv_ip not in srv_nodes:
                srv_nodes.append(srv_ip)

            cur_route = cur_user_routes[srv]
            cur_clean_route = simplify_route(cur_route, user, srv, hops_folder)
            print cur_clean_route
            route_ids = sorted(cur_clean_route.keys(), key=int)
            pre_node = cur_clean_route[route_ids[0]]
            route_graph.add_node(pre_node, node_shape='^', node_size=200, node_color='m')
            for cur_id in route_ids[1:]:
                cur_node = cur_clean_route[cur_id]
                if cur_node == srv_ip:
                    route_graph.add_node(cur_node, node_shape='s', node_size=300, node_color='b')
                else:
                    route_graph.add_node(cur_node, node_shape='o', node_size=50, node_color='grey')

                cur_edge = sorted([pre_node, cur_node])
                route_graph.add_edge(cur_edge[0], cur_edge[1], edge_color='k')
                pre_node = cur_node

    return route_graph, srv_nodes, user_nodes


def read_route_info(trace_folder, file_prefix_or_file_list, info_name=None):
    user_info = {}
    all_tr_files = []
    ## Input variable is a prefix strings or a list of files
    if type(file_prefix_or_file_list) == str:
        all_tr_files = glob.glob(trace_folder + file_prefix_or_file_list + "*")
    elif type(file_prefix_or_file_list) is list:
        for file_name in file_prefix_or_file_list:
            all_tr_files.append(trace_folder + file_name)

    for tr_file in all_tr_files:
        base_file_name = ntpath.basename(tr_file)
        tmp_file_name = re.sub(r'\.json$', '', base_file_name)
        if type(file_prefix_or_file_list) == str:
            user_name = re.sub(file_prefix_or_file_list, '', tmp_file_name)
        elif type(file_prefix_or_file_list) is list:
            user_name = tmp_file_name.split('_')[1]

        tr_info = json.load(open(tr_file))
        if user_name not in user_info.keys():
            user_info[user_name] = {}

        for srv in tr_info.keys():
            if info_name:
                user_info[user_name][srv] = copy.deepcopy(tr_info[srv][info_name])
            else:
                user_info[user_name][srv] = copy.deepcopy(tr_info[srv])

        # print user_name, user_pings[user_name].values()

    return user_info

def get_user_ave_rtts(srvs_tr_folder, tr_file_prefix):
    user_pings = read_route_info(srvs_tr_folder, tr_file_prefix, 'RTT')

    user_ave_rtts = {}
    for user in user_pings.keys():
        cur_user_rtts = user_pings[user]
        ave_rtt = sum(cur_user_rtts.values()) / float(len(cur_user_rtts.keys()))
        user_ave_rtts[user] = ave_rtt

    return user_ave_rtts


def user_info_selection(all_user_info, users_to_select):
    selected_user_info = {}
    for user in users_to_select:
        selected_user_info[user] = copy.deepcopy(all_user_info[user])

    return selected_user_info


def remove_nodes(org_list, nodes_to_remove):
    new_list = list(org_list)
    for node in nodes_to_remove:
        if node in new_list:
            new_list.remove(node)

    return new_list


def write_nodes_file(nodes, outputFile):
    outFile = open(outputFile, 'w')
    for node in nodes:
        outFile.write(node + "\n")
    outFile.close()


if __name__ == "__main__":
    srvs_tr_folder = "D://Data/cloud-monitor-data/srvs-0113/tr/"
    hops_folder = "D://Data/cloud-monitor-data/srvs-hops/"
    nodes_folder = "D://Data/cloud-monitor-data/srvs-0113/users/"
    tr_file_prefix = "USTR_"
    user_ave_rtts = get_user_ave_rtts(srvs_tr_folder, tr_file_prefix)
    sorted_users = [k for (k, v) in sorted(user_ave_rtts.items(), key=lambda (k, v): v )]

    fail_nodes = ["planetlab1.tsuniv.edu", "planetlab2.acis.ufl.edu", "planetlab2.cs.pitt.edu"]
    new_sorted_list = remove_nodes(sorted_users, fail_nodes)

    # sorted_users = sorted(user_ave_rtts.items(), key=lambda (k, v): v )
    write_nodes_file(new_sorted_list[:40], nodes_folder+"nodes40")
    write_nodes_file(new_sorted_list[:20], nodes_folder+"nodes20")
    write_nodes_file(new_sorted_list[:10], nodes_folder+"nodes10")

    user_routes = read_route_info(srvs_tr_folder, tr_file_prefix, "Hops")
    selected_user_routes = user_info_selection(user_routes, new_sorted_list[:20])

    route_graph, srv_nodes, user_nodes = route2graph(selected_user_routes, hops_folder)
    draw_network(route_graph, srv_nodes, user_nodes, hops_folder)


