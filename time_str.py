import calendar
import datetime
import time

def timestr2ts(time_str, str_pattern):
    time_tpl = datetime.datetime.strptime(time_str, str_pattern).timetuple()
    time_ts = time.mktime(time_tpl)
    return time_ts


def timestr2utcts(time_str, str_pattern):
    if '%Y' not in str_pattern:
        str_pattern = '%Y' + str_pattern
        time_str = '2016' + time_str

    # time_tpl = datetime.datetime.strptime('2016'+time_str, '%Y%m%d%H%M').timetuple()
    time_tpl = datetime.datetime.strptime(time_str, str_pattern).timetuple()
    utc_now = datetime.datetime.utcnow()
    now = datetime.datetime.now()
    utc_diff = time.mktime(utc_now.timetuple()) - time.mktime(now.timetuple())
    time_ts_local = time.mktime(time_tpl)
    time_ts = time_ts_local - utc_diff
    # print time_str, time_ts_local, time_ts
    return time_ts


def ts2timestr(ts, str_pattern):
    utc_dt  = datetime.datetime.utcfromtimestamp(ts)
    # time_str = utc_dt.strftime("%m%d%H%M")
    time_str = utc_dt.strftime(str_pattern)
    return time_str

if __name__ == "__main__":
    ts = 1451970600.0
    print ts2timestr(ts, "%m%d%H%M")

    ts_str = "01050510"
    print timestr2utcts(ts_str, "%m%d%H%M")