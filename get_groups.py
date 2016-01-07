# Get group of users denoted by a given user
# Can discover the last mile group of users, who share the same local ISP to the given user
# Can discover the first mile group of users, who share the same streaming server with the given user.
# Chen Wang, chenw@cmu.edu
# 2016-01-05
import glob
import csv
import json
import ntpath
import re
import calendar, time, datetime
from get_clients_info import *
from get_files import *


def get_user_srv(qoe_file_path, given_user, ts):
    selected_file = find_cur_file(qoe_file_path, given_user, ts)
    if selected_file is not None:
        qoe_tr = json.load(open(qoe_file_path + selected_file))
        user_srv = qoe_tr['0']['Server']
        return user_srv

    return None


def get_first_mile_peers(qoe_file_path, given_user, ts):
    user_groups = get_first_mile_groups(qoe_file_path, True)
    given_user_srv = get_user_srv(qoe_file_path, given_user, ts)
    first_mile_peers = user_groups[given_user_srv]
    return first_mile_peers


def get_last_mile_peers(qoe_file_path, given_user):
    user_groups = get_last_mile_groups(qoe_file_path, True)
    given_user_info = read_user_info(given_user)
    if given_user_info:
        given_user_as = given_user_info['AS']
        last_mile_peers = user_groups[given_user_as]
    else:
        last_mile_peers = []

    return last_mile_peers


if __name__ == "__main__":
    ## Default data folder
    qoeFolder = "D://Data/cdn-monitor-data/azure-0105/qoe/"
    givenUser = "75-130-96-12.static.oxfr.ma.charter.com"
    ts = 1451968805.434049
    first_mile_peers = get_first_mile_peers(qoeFolder, givenUser, ts)
    print "First mile peers: ", first_mile_peers
    last_mile_peers = get_last_mile_peers(qoeFolder, givenUser)
    print "Last mile peers: ", last_mile_peers

