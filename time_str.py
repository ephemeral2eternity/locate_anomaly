import calendar
import datetime
import time


def timestr2utcts(time_str):
    time_tpl = datetime.datetime.strptime('2016'+time_str, '%Y%m%d%H%M').timetuple()
    utc_now = datetime.datetime.utcnow()
    now = datetime.datetime.now()
    utc_diff = time.mktime(utc_now.timetuple()) - time.mktime(now.timetuple())
    time_ts_local = time.mktime(time_tpl)
    time_ts = time_ts_local - utc_diff
    # print time_str, time_ts_local, time_ts
    return time_ts


def ts2timestr(ts):
    utc_dt  = datetime.datetime.utcfromtimestamp(ts)
    time_str = utc_dt.strftime("%m%d%H%M")
    return time_str

if __name__ == "__main__":
    ts = 1451970600.0
    print ts2timestr(ts)