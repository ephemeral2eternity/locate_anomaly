# Get users that connect to the same server
# Chen Wang, chenw@cmu.edu
# 2016-01-04
import glob
import csv
import json
import os
import shutil
import ntpath
import re
from utils import *
from ipinfo.host2ip import *
from ipinfo.ipinfo import *
from get_server import *

## Get user QoE files
def get_node_ips(inputList, outputFolder, outputName):
    with open(inputList, 'rb') as f:
        nodes = {}
        for node in f.readlines():
            curNode = node.rstrip()
            nodeIP = host2ip(curNode)
            if nodeIP != '*':
                nodes[curNode] = nodeIP
                ## print curNode, nodeIP
        writeJson(outputFolder, outputName, nodes)


def get_node_details(node_ip_file, outputFolder):
    nodes = json.load(open(node_ip_file))
    for user in nodes.keys():
        user_ip = nodes[user]
        user_info = ipinfo(user_ip)
        ## print user_info
        writeJson(outputFolder, user, user_info)

def user2as(user_file_path, as_file_path):
    user_files = glob.glob(user_file_path + "*")
    as_info = {}
    for cur_user_file in user_files:
        user_file_name = ntpath.basename(cur_user_file)
        user_name = re.sub(r'\.json$', '', user_file_name)
        user_info = json.load(open(cur_user_file))
        if 'AS' in user_info.keys():
            curAS = user_info['AS']
            curISP = user_info['ISP']
            if curAS not in as_info.keys():
                as_info[curAS] = {}
                as_info[curAS]['ISP'] = curISP
                as_info[curAS]['users'] = []
            as_info[curAS]['users'].append(user_name)

    writeJson(as_file_path, 'ases', as_info)

def read_user_info(user_name):
    default_user_path = "./clientsInfo/nodes/"
    fileName = default_user_path + user_name + ".json"
    if os.path.exists(fileName):
        user_info = json.load(open(fileName))
    else:
        user_ip = host2ip(user_name)
        if is_ip(user_ip):
            user_info = ipinfo(user_ip)
            writeJson(default_user_path, user_name, user_info)
        else:
            user_info = {}
    return user_info


# The first server may not be the server through the whole streaming session in CloudFront
def get_first_mile_groups(inputFolder, silent_mode=True, outputFolder=os.getcwd() + "/data/", outputFileName="firstmile_group"):
    ## Get user QoE files
    qoe_files = glob.glob(inputFolder + "*")

    users = {}
    srv_info = {}

    ## Process each user QoE file
    for user_qoe_file in qoe_files:
        user_file_name = ntpath.basename(user_qoe_file)
        user_name = user_file_name.split('_')[0]
        ## print user_file_name
        srvs = get_all_servers(user_qoe_file)

        for srv in srvs:
            if srv not in users.keys():
                users[srv] = []

            if user_name not in users[srv]:
                users[srv].append(user_name)

        if silent_mode:
            continue

        if srv not in srv_info.keys():
            cur_srv_info = ipinfo(srv)
            srv_info[srv] = cur_srv_info

    if not silent_mode:
        writeJson(outputFolder, outputFileName, users)

    return users


def get_last_mile_groups(inputFolder, silent_mode=True, outputFolder=os.getcwd() + "/data/", outputFileName="lastmile_group"):
    ## Get user QoE files
    default_as_file = "./clientsInfo/ases.json"
    qoe_files = glob.glob(inputFolder + "*")

    users = {}

    ## Process each user QoE file
    for user_qoe_file in qoe_files:
        user_file_name = ntpath.basename(user_qoe_file)
        user_name = user_file_name.split('_')[0]
        user_info = read_user_info(user_name)

        if 'AS' in user_info.keys():
            user_as = user_info['AS']

            # print last_mile_user_group

            if user_as not in users.keys():
                users[user_as] = []
            else:
                if user_name not in users[user_as]:
                    users[user_as].append(user_name)

            if silent_mode:
                continue
        else:
            continue

    if not silent_mode:
        writeJson(outputFolder, "lastmile_group", users)

    return users

if __name__ == "__main__":

    ## Default data folder
    inFolder = "D://Data/cdn-monitor-data/aws-0109/qoe/"
    outFolder = "D://Data/cdn-monitor-data/aws-0109/peers/"
    get_first_mile_groups(inFolder, silent_mode=False, outputFolder=outFolder)
    get_last_mile_groups(inFolder, silent_mode=False, outputFolder=outFolder)

    '''
    ## Default data folder
    inputFolder = "D://Data/cdn-monitor-data/azure-0105/qoe/"
    outputFolder = "D://Data/cdn-monitor-data/azure-0105/last-mile-group/"
    get_last_mile_groups(inputFolder, outputFolder)
    '''