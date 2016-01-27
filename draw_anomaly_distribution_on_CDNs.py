from draws.draw_utils import *
from draws.draw_qoe_related import *
from time_str import *

def read_anomaly_events(anomaly_event_file):
    anomaly_user_num = 0
    total_anomaly_event_num = 0
    anomalies = json.load(open(anomaly_event_file))
    for user in anomalies.keys():
        if anomalies[user]:
            anomaly_user_num += 1
            for srv in anomalies[user].keys():
                cur_srv_anomaly_cnt = len(anomalies[user][srv])
                total_anomaly_event_num += cur_srv_anomaly_cnt

    return anomalies, anomaly_user_num, total_anomaly_event_num

## ==================================================================================================
# Count the number of events
# @input : json_file_name --- json file name
# 		   json_var --- json variable
## ==================================================================================================
def count_anomaly_period_per_user(anomaly_events, chunk_period = 5):
    anomaly_period = {}
    for client in anomaly_events.keys():
        anomaly_period[client] = 0
    for client in anomaly_events.keys():
        for srv in anomaly_events[client].keys():
            cur_anomaly_range = anomaly_events[client][srv]
            cur_anomaly_period = cur_anomaly_range[1] - cur_anomaly_range[0]
            if cur_anomaly_period < chunk_period:
                cur_anomaly_period = chunk_period
            anomaly_period[client] += cur_anomaly_period
    return anomaly_period


def draw_anomaly_cnts_comparison(*args):
    fig, ax = plt.subplots()
    percentile_val = 0.9
    arg_id = 0
    line_styles = ['-b', '--k', ':r', '-m', '--y', ':g']
    color_styles = ['b', 'k', 'r', 'm', 'y', 'g']
    for anomaly_events in args:
        anomaly_cnts = count_events_per_user(anomaly_events)
        anomaly_cnt_percentile = plot_event_cnts_cdf(ax, anomaly_cnts, percentile=percentile_val, label="CDN " + str(arg_id+1), lnSty=line_styles[arg_id])
        ax.annotate(str(anomaly_cnt_percentile), xy=(anomaly_cnt_percentile, percentile_val), xytext=(anomaly_cnt_percentile+10, percentile_val-0.05), xycoords='data',
            color=color_styles[arg_id], arrowprops=dict(arrowstyle="->", color=color_styles[arg_id]))
        arg_id += 1

    ax.annotate(str(percentile_val*100) + '% users', xy=(180, percentile_val), xytext=(180, percentile_val+0.02), xycoords='data', color='r')
    plt.axhline(y=percentile_val, color='r')

    plt.legend(loc=0)
    plt.show()
    save_fig(fig, "anomalies_all_CDNs")


if __name__ == "__main__":
    ## Default data folder
    aws_anomaly_event_file = "D://Data/cdn-monitor-data/aws-0109/anomaly/anomaly-events-01090500-01090600.json"
    azure_anomaly_event_file = "D://Data/cdn-monitor-data/azure-0112/anomaly/anomaly-events-01120400-01120500.json"
    rs_anomaly_event_file = "D://Data/cdn-monitor-data/rs-0113/anomaly/anomaly-events-01131800-01131900.json"
    figName = "anomaly_cnts_plt_all_cdns"

    SLA = 1.0
    timeWin = 30

    aws_anomaly_events, aws_anomaly_user_num, aws_total_number_anomaly_events = read_anomaly_events(aws_anomaly_event_file)
    print "QoE based Anomaly detection for CDN: CloudFront!"
    print "Total number of users: ", len(aws_anomaly_events.keys())
    print "Number of anomaly users: ", aws_anomaly_user_num
    print "Total number of anomaly events: ", aws_total_number_anomaly_events

    azure_anomaly_events, azure_anomaly_user_num, azure_total_number_anomaly_events = read_anomaly_events(azure_anomaly_event_file)
    print "QoE based Anomaly detection for CDN: Azure!"
    print "Total number of users: ", len(azure_anomaly_events.keys())
    print "Number of anomaly users: ", azure_anomaly_user_num
    print "Total number of anomaly events: ", azure_total_number_anomaly_events

    rs_anomaly_events, rs_anomaly_user_num, rs_total_number_anomaly_events = read_anomaly_events(rs_anomaly_event_file)
    print "QoE based Anomaly detection for CDN: Rackspace!"
    print "Total number of users: ", len(rs_anomaly_events.keys())
    print "Number of anomaly users: ", rs_anomaly_user_num
    print "Total number of anomaly events: ", rs_total_number_anomaly_events

    draw_anomaly_cnts_comparison(aws_anomaly_events, azure_anomaly_events, rs_anomaly_events)