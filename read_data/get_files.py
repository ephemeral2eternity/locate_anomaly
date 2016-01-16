import calendar
import datetime
import time
import re
import ntpath
import glob
from time_str import *

def get_file_ts_by_name(file_name):
    base_file_name = re.sub(r'\.json$', '', file_name)
    f_ts_str = base_file_name.split('_')[-1]
    f_ts = timestr2utcts(f_ts_str, '%m%d%H%M')
    return f_ts


def get_file_ts_by_prefix(file_path, file_prefix):
    files_ts = {}
    avail_files = glob.glob(file_path + file_prefix + "*")
    for cur_file in avail_files:
        user_file_name = ntpath.basename(cur_file)
        file_name = re.sub(r'\.json$', '', user_file_name)
        f_ts_str = file_name.split('_')[-1]
        # print f_ts_str
        f_ts = timestr2utcts(f_ts_str, '%m%d%H%M')
        files_ts[f_ts] = user_file_name
    return files_ts


def find_cur_file(file_path, file_prefix, ts):
    files_ts = get_file_ts_by_prefix(file_path, file_prefix)
    sorted_file_ts = sorted(files_ts.keys(), key=float, reverse=True)
    # print sorted_file_ts, ts
    selected_file = None

    for f_ts in sorted_file_ts:
        if f_ts <= ts:
            selected_file = files_ts[f_ts]
            break

    if selected_file is None:
        print "[Error] No files for prefix: ", file_prefix, " is available before time: ", \
        ts2timestr(ts, '%Y-%m-%d %H:%M:%S')
    # else:
        # print "Find file: ", selected_file
    return selected_file


def find_files_in_range(file_path, file_prefix, ts_range):
    files_ts = get_file_ts_by_prefix(file_path, file_prefix)
    sorted_file_ts = sorted(files_ts.keys(), key=float, reverse=True)

    files_in_range = []
    for f_ts in sorted_file_ts:
        if f_ts <= ts_range[1]:
            files_in_range.append(files_ts[f_ts])
        elif f_ts <= ts_range[0]:
            files_in_range.append(files_ts[f_ts])
            break

    return files_in_range
