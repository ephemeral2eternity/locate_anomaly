import glob
import ntpath
import re
import json
import copy
from ipinfo.host2ip import *
from ipinfo.ipinfo import *
import networkx as nx
import matplotlib.pyplot as plt
# from pylab import *


def draw_network(graph_obj, srv_nodes, user_nodes, hopsPath, isLabel=False):
    pos=nx.spring_layout(graph_obj, k=0.5, iterations=200)
    all_nodes = graph_obj.nodes()
    print all_nodes, srv_nodes

    nodesize = {}
    nodecolor = {}
    for node in graph_obj.nodes():
        if node in srv_nodes:
            nodesize[node] = 200
            nodecolor[node] = 'b'
        elif node in user_nodes:
            nodesize[node] = 200
            nodecolor[node] = 'g'
        else:
            nodesize[node] = 50
            nodecolor[node] = 'grey'

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
    nodeShapes = set((aShape[1]["s"] for aShape in graph_obj.nodes(data = True)))

    for aShape in nodeShapes:
        curNodes = [sNode[0] for sNode in filter(lambda x: x[1]["s"] == aShape,graph_obj.nodes(data = True))]
        nodesizelist = [nodesize[v] for v in curNodes]
        nodecorlorlist = [nodecolor[v] for v in curNodes]
        nx.draw_networkx_nodes(graph_obj, pos, node_shape = aShape, nodelist = curNodes, node_size=nodesizelist, node_color=nodecorlorlist, alpha = 0.5)

    nx.draw_networkx_edges(graph_obj, pos, edge_color='k')

    #p1 = Circle((0, 0), fc="b")
    #p2 = Circle((0, 0), fc="g")
    #p3 = Circle((0, 0), fc="grey")
    #plt.legend([p1,p2,p3], ["Server","Client","Router"])
    plt.show()

# def read_routes():
#    return

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


def route2graph(user_routes, hops_folder):
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
            if is_ip(srv):
                srv_ip = srv
            else:
                srv_ip = host2ip(srv)

            if srv_ip not in srv_nodes:
                srv_nodes.append(srv_ip)

            cur_route = cur_user_routes[srv]
            cur_clean_route = simplify_route(cur_route, user, srv, hops_folder)
            # print cur_clean_route
            route_ids = sorted(cur_clean_route.keys(), key=int)
            pre_node = cur_clean_route[route_ids[0]]
            route_graph.add_node(pre_node, s='^')
            for cur_id in route_ids[1:]:
                cur_node = cur_clean_route[cur_id]
                if cur_node == srv_ip:
                    route_graph.add_node(cur_node, s='s')
                else:
                    route_graph.add_node(cur_node, s='o')
                route_graph.add_edge(pre_node, cur_node)
                pre_node = cur_node

    '''
    print "The whole graph is:"
    for (u, v) in route_graph.edges():
        print '(%s, %s)' % (u, v)

    for node in route_graph.nodes():
        print "Node:", node
    '''

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


