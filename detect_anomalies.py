# Locate anomalies via user QoE and their route info
# Chen Wang, chenw@cmu.edu
# 2016-01-04
from draws.draw_utils import *
from draws.draw_qoe_related import *
from time_str import *


def merge_events(anomaly_pts, time_win):
    anomaly_events = {}

    event_no = 0
    if len(anomaly_pts) > 0:
        for srv in anomaly_pts.keys():
            anomaly_events[srv] = []
            sorted_anomaly_pts = sorted(anomaly_pts[srv])

            prePts = sorted_anomaly_pts[0]
            event_start = prePts
            event_end = prePts
            for ts in sorted_anomaly_pts[1:]:
                if ts - prePts < time_win:
                    prePts = ts
                    event_end = ts
                    continue
                else:
                    event_no += 1
                    event_end = prePts
                    anomaly_events[srv].append([event_start, event_end])
                    event_start = ts
                    event_end = ts
                    prePts = ts

            event_no += 1
            anomaly_events[srv].append([event_start, event_end])
            # print anomaly_events[srv]

    return anomaly_events, event_no


def add_anomaly_points(usr_anomaly_pts, new_anomaly_pts):
    for srv in new_anomaly_pts.keys():
        if srv in usr_anomaly_pts.keys():
            usr_anomaly_pts[srv] = usr_anomaly_pts[srv] + new_anomaly_pts[srv]
        else:
            usr_anomaly_pts[srv] = list(new_anomaly_pts[srv])
    return usr_anomaly_pts


def detect_anomaly_points(user_qoe, SLA, qoeType):
    anomalies = {}
    chunk_ids = sorted(user_qoe.keys(), key=int)
    ## Ignore the first two chunks that has bad QoE as it is impacted by the startup logic.
    # for ch_id in chunk_ids:
    for ch_id in chunk_ids[5:]:
        ch_qoe = float(user_qoe[ch_id][qoeType])
        ch_srv = user_qoe[ch_id]["Server"]
        if ch_qoe < SLA:
            if ch_srv not in anomalies.keys():
                anomalies[ch_srv] = []
            anomalies[ch_srv].append(float(user_qoe[ch_id]['TS']))
    return anomalies


def detect_anomaly(qoeFolder, SLA, qoeType):
    anomaly_user_pts = {}
    all_qoe_files = glob.glob(qoeFolder + "*.json")
    ## Detect anomaly users
    for qoe_file in all_qoe_files:
        # print qoe_file
        cur_user_qoe = json.load(open(qoe_file))
        anomaly_pts = detect_anomaly_points(cur_user_qoe, SLA, qoeType)

        user_file_name = ntpath.basename(qoe_file)
        user_name = user_file_name.split('_')[0]
        if user_name not in anomaly_user_pts.keys():
            anomaly_user_pts[user_name] = {}
        anomaly_user_pts[user_name] = add_anomaly_points(anomaly_user_pts[user_name], anomaly_pts)

    ## Filter anomaly points to events using time window
    anomaly_events = {}
    total_number_anomaly_events = 0
    anomaly_user_num = 0
    for user in anomaly_user_pts.keys():
        cur_anomaly_events, user_event_num = merge_events(anomaly_user_pts[user], timeWin)
        anomaly_events[user] = {}
        anomaly_events[user].update(cur_anomaly_events)
        total_number_anomaly_events += user_event_num
        if len(cur_anomaly_events.keys()) > 0:
            anomaly_user_num+=1
        # print "Anomaly Events for user : ", user
        # print cur_anomaly_events
        # print "Anomaly User: ", user, " # of anomaly events : ", user_event_num

    return anomaly_events, anomaly_user_num, total_number_anomaly_events


def filter_events(anomaly_events, ts_range):
    filtered_events = {}
    all_users = anomaly_events.keys()
    total_number_anomaly_events = 0
    anomaly_user_num = 0
    for user in all_users:
        user_event_cnt = 0
        filtered_events[user] = {}
        for srv in anomaly_events[user].keys():
            cur_usr_srv_events = anomaly_events[user][srv]
            for cur_anomaly_ts_range in anomaly_events[user][srv]:
                if ((cur_anomaly_ts_range[0] <= ts_range[1]) and (cur_anomaly_ts_range[0] >= ts_range[0])) \
                        or ((cur_anomaly_ts_range[1] >= ts_range[0]) and (cur_anomaly_ts_range[1] <= ts_range[1])):
                    if srv not in filtered_events[user].keys():
                        filtered_events[user][srv] = []
                    filtered_events[user][srv].append(list(cur_anomaly_ts_range))
                    user_event_cnt += 1
                    total_number_anomaly_events += 1
        if user_event_cnt > 0:
            anomaly_user_num += 1

    return filtered_events, anomaly_user_num, total_number_anomaly_events


if __name__ == "__main__":
    ## Default data folder
    aws_qoeFolder = "D://Data/cdn-monitor-data/aws-0109/qoe/"
    aws_rstsFolder = "D://Data/cdn-monitor-data/aws-0109/anomaly/"

    rs_qoeFolder = "D://Data/cdn-monitor-data/rs-0113/qoe/"
    rs_rstsFolder = "D://Data/cdn-monitor-data/rs-0113/anomaly/"
    figName = "anomaly_cnts_plt_all_cdns"

    azure_qoeFolder = "D://Data/cdn-monitor-data/azure-0112/qoe/"
    azure_rstsFolder = "D://Data/cdn-monitor-data/azure-0112/anomaly/"
    # figName = "anomaly_cnts_plt_azure_0112"

    SLA = 1.0
    timeWin = 30
    qoeType = "QoE2"
    aws_ts_range = [1452315600, 1452319200]         # AWS-0109 data
    azure_ts_range = [1452571200, 1452574800]             # Azure-0112 data
    rs_ts_range = [1452708000, 1452711600]

    aws_anomaly_events, aws_anomaly_user_num, aws_total_number_anomaly_events = detect_anomaly(aws_qoeFolder, SLA, qoeType)
    aws_anomaly_events, aws_anomaly_user_num, aws_total_number_anomaly_events = filter_events(aws_anomaly_events, aws_ts_range)
    print "QoE based Anomaly detection for CDN: CloudFront!"
    print "Total number of users: ", len(aws_anomaly_events.keys())
    print "Number of anomaly users: ", aws_anomaly_user_num
    print "Total number of anomaly events: ", aws_total_number_anomaly_events
    aws_filter_ts_str = ts2timestr(aws_ts_range[0], "%m%d%H%M") + "-" + ts2timestr(aws_ts_range[1], "%m%d%H%M")
    writeJson(aws_rstsFolder, "anomaly-events-"+aws_filter_ts_str, aws_anomaly_events)

    azure_anomaly_events, azure_anomaly_user_num, azure_total_number_anomaly_events = detect_anomaly(azure_qoeFolder, SLA, qoeType)
    azure_anomaly_events, azure_anomaly_user_num, azure_total_number_anomaly_events = filter_events(azure_anomaly_events, azure_ts_range)
    print "QoE based Anomaly detection for CDN: Azure!"
    print "Total number of users: ", len(azure_anomaly_events.keys())
    print "Number of anomaly users: ", azure_anomaly_user_num
    print "Total number of anomaly events: ", azure_total_number_anomaly_events
    azure_filter_ts_str = ts2timestr(azure_ts_range[0], "%m%d%H%M") + "-" + ts2timestr(azure_ts_range[1], "%m%d%H%M")
    writeJson(azure_rstsFolder, "anomaly-events-"+azure_filter_ts_str, azure_anomaly_events)

    rs_anomaly_events, rs_anomaly_user_num, rs_total_number_anomaly_events = detect_anomaly(rs_qoeFolder, SLA, qoeType)
    rs_anomaly_events, rs_anomaly_user_num, rs_total_number_anomaly_events = filter_events(rs_anomaly_events, rs_ts_range)
    print "QoE based Anomaly detection for CDN: Rackspace!"
    print "Total number of users: ", len(rs_anomaly_events.keys())
    print "Number of anomaly users: ", rs_anomaly_user_num
    print "Total number of anomaly events: ", rs_total_number_anomaly_events
    rs_filter_ts_str = ts2timestr(rs_ts_range[0], "%m%d%H%M") + "-" + ts2timestr(rs_ts_range[1], "%m%d%H%M")
    writeJson(rs_rstsFolder, "anomaly-events-"+rs_filter_ts_str, rs_anomaly_events)


    aws_anomaly_cnts = count_events_per_user(aws_anomaly_events)
    azure_anomaly_cnts = count_events_per_user(azure_anomaly_events)
    rs_anomaly_cnts = count_events_per_user(rs_anomaly_events)
    fig, ax = plt.subplots()
    percentile_val = 0.9
    aws_percentile = plot_event_cnts_cdf(ax, aws_anomaly_cnts, percentile=percentile_val, label="CDN A", lnSty='-b')
    azure_percentile = plot_event_cnts_cdf(ax, azure_anomaly_cnts, percentile=percentile_val, label="CDN B", lnSty='--k')
    rs_percentile = plot_event_cnts_cdf(ax, rs_anomaly_cnts, percentile=percentile_val, label="CDN C", lnSty=':r')

    plt.axhline(y=percentile_val, color='r')
    ax.annotate('90% users', xy=(180, percentile_val), xytext=(180, percentile_val+0.02), xycoords='data', color='r')

    ax.annotate(str(aws_percentile), xy=(aws_percentile, percentile_val), xytext=(aws_percentile+10, percentile_val-0.05), xycoords='data',
                color='b', arrowprops=dict(arrowstyle="->", color='b'))
    ax.annotate(str(azure_percentile), xy=(azure_percentile, percentile_val), xytext=(azure_percentile+10, percentile_val-0.10), xycoords='data',
                color='k', arrowprops=dict(arrowstyle="->", color='k'))
    ax.annotate(str(rs_percentile), xy=(rs_percentile, percentile_val), xytext=(rs_percentile + 10, percentile_val-0.15), xycoords='data',
                color='r', arrowprops=dict(arrowstyle="->", color='r'))


    plt.legend(loc=0)
    plt.show()
    save_fig(fig, "anomalies_all_CDNs")