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


def get_user_file_ts(file_path, file_prefix):
    files_ts = {}
    avail_files = glob.glob(file_path + file_prefix + "*")
    for cur_file in avail_files:
        user_file_name = ntpath.basename(cur_file)
        file_name = re.sub(r'\.json$', '', user_file_name)
        f_ts_str = file_name.split('_')[-1]
        f_ts = calendar.timegm(datetime.datetime.strptime('2016'+f_ts_str, '%Y%m%d%H%M').timetuple())
        files_ts[f_ts] = user_file_name
    return files_ts


def find_cur_file(file_path, file_prefix, ts):
    files_ts = get_user_file_ts(file_path, file_prefix)
    sorted_file_ts = sorted(files_ts.keys(), key=float, reverse=True)

    for f_ts in sorted_file_ts:
        if f_ts <= ts:
            selected_file = files_ts[f_ts]
            return selected_file

    print "[Error] No files for prefix: ", file_prefix, " is available before time: ", \
        datetime.datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M:%S')
    return None


def find_files_in_range(file_path, file_prefix, ts_range):
    files_ts = get_user_file_ts(file_path, file_prefix)
    sorted_file_ts = sorted(files_ts.keys(), key=float, reverse=True)

    files_in_range = []
    for f_ts in sorted_file_ts:
        if f_ts <= ts_range[1]:
            files_in_range.append(files_ts[f_ts])
        elif f_ts <= ts_range[0]:
            files_in_range.append(files_ts[f_ts])
            break

    return files_in_range


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
    given_user_as = given_user_info['AS']
    last_mile_peers = user_groups[given_user_as]

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

