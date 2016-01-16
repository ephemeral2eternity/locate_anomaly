
from draw_utils import *

def remove_normal_users(anomaly_cnts):
    updated_anomaly_cnts = {}
    for client in anomaly_cnts.keys():
        if anomaly_cnts[client] > 0:
            updated_anomaly_cnts[client] = anomaly_cnts[client]
    return updated_anomaly_cnts


def plot_event_cnts_cdf(ax, anomaly_cnts, toSave=False, figName="anomaly_cnts_plt", label="CDN", lnSty = "-b"):
    sorted_cnts = sorted(anomaly_cnts.values())
    yvals = np.arange(len(sorted_cnts))/float(len(sorted_cnts))

    # fig, ax = plt.subplots()
    plt.plot(sorted_cnts, yvals, lnSty, linewidth=3.0, label=label)
    ax.set_ylabel('The percentage of users', fontsize=15)
    ax.set_xlabel('The number of anomaly events per user', fontsize=15)


def draw_event_cnts(anomaly_cnts, toSave=True, figName="anomaly_cnts_bar"):
    anomaly_user_cnts = remove_normal_users(anomaly_cnts)
    user_num = len(anomaly_user_cnts.keys())

    ind = np.arange(user_num)
    width = 0.4
    sorted_users = sorted(anomaly_user_cnts, key=lambda k:anomaly_cnts[k], reverse=True)
    sorted_cnts = sorted(anomaly_user_cnts.values(), reverse=True)

    fig, ax = plt.subplots()
    ax.bar(ind, sorted_cnts, width, color='b')
    ax.set_xticks(ind + width/2)
    ax.set_xticklabels(sorted_users)
    ax.set_ylabel('The number of anomaly events!')
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.show()

    if toSave:
        save_fig(fig, figName)


def draw_anomaly_location_types(anomaly_locs, toSave=False, figName="anomaly_loc_typ_cnts"):
    ## Initialize the count of events in each type of anomaly location.
    anomaly_loc_cnts = {}
    uniq_anomaly_loc_cnts = {}
    loc_typs = ["client", "client_net", "transit_net", "cloud_net", "server", "unknown"]
    for cur_typ in loc_typs:
        anomaly_loc_cnts[cur_typ] = 0
        uniq_anomaly_loc_cnts[cur_typ] = 0

    all_event_ids = anomaly_locs.keys()
    for event_id in all_event_ids:
        cur_event_locs = anomaly_locs[event_id]['anomaly-hops']
        uniq_hop_typs = list(set(cur_event_locs.values()))
        for anomaly_loc_typ in uniq_hop_typs:
            anomaly_loc_cnts[anomaly_loc_typ] += 1
            if len(uniq_hop_typs) <= 1:
                uniq_anomaly_loc_cnts[anomaly_loc_typ] += 1
            elif (len(uniq_hop_typs) <= 2) and ("client" in uniq_hop_typs) and (anomaly_loc_typ != "client"):
                uniq_anomaly_loc_cnts[anomaly_loc_typ] += 1

    ind = np.arange(len(anomaly_loc_cnts.keys()))
    anomaly_loc_cnts_list = [anomaly_loc_cnts[x] for x in loc_typs]
    uniq_anomaly_loc_cnts_list = [uniq_anomaly_loc_cnts[x] for x in loc_typs]
    width = 0.4
    uniq_ind = ind + width
    fig, ax = plt.subplots()
    ax.barh(ind, anomaly_loc_cnts_list, width, color='b', label="Anomalies located in the segment", hatch="o", alpha=0.4)
    ax.barh(uniq_ind, uniq_anomaly_loc_cnts_list, width, color='r', label="Anomalies uniquely located in the segment", hatch="+", alpha=0.4)
    ax.set_yticks(ind + width)
    ax.set_yticklabels(loc_typs, minor=False, fontsize=15)
    ax.set_xlabel('The number of anomaly events \n located in the denoted segment', fontsize=15, multialignment='center')
    ax.set_ylabel('The segment located \n for the anomaly event', fontsize=15, multialignment='center')

    for i, v in enumerate(anomaly_loc_cnts_list):
        ax.text(v + 3, i + width/2, str(v), color='blue', fontweight='bold')

    for i, v in enumerate(uniq_anomaly_loc_cnts_list):
        ax.text(v + 3, i + width + width/2, str(v), color='red', fontweight='bold')

    plt.legend(fontsize=15)
    fig.tight_layout()
    plt.show()

    if toSave:
        save_fig(fig, figName)


def draw_anomalies(ax, usr_anomalies, color='r', alpha=0.5):
    srv_id = 0
    for srv in usr_anomalies.keys():
        for event in usr_anomalies[srv]:
            if event[1] - event[0] < 5:
                ax.axvspan(event[1] - 5, event[1], facecolor=color, alpha=alpha)
            else:
                ax.axvspan(event[0], event[1], facecolor=color, alpha=alpha)

        srv_id += 1


def plot_qoe(ax, user_qoes, marker_sty, qoe_lable, color='r'):
    ## Plot Server QoE Scores
    sorted_ts = sorted(user_qoes.keys(), key=float)
    qoe_vals = [user_qoes[cur_ts] for cur_ts in sorted_ts]
    # ax.scatter(sorted_ts, qoe_vals, marker=marker_sty, c=color, label=qoe_lable, markersize=10)
    ax.scatter(sorted_ts, qoe_vals, marker=marker_sty, c=color)



if __name__ == "__main__":
    '''
    ## Default anomaly detection results file
    anomaly_file = "D://Data/cdn-monitor-data/aws-0109/anomaly/anomaly-events-01090500-01090600.json"
    anomaly_events = json.load(open(anomaly_file))
    anomaly_cnts = count_events_per_user(anomaly_events)
    plot_event_cnts(anomaly_cnts, toSave=True, figName="anomaly_cnts_plt_aws_0109")
    '''

    ## Default anomaly localization results file
    anomaly_loc_file = "D://Data/cdn-monitor-data/aws-0109/anomaly/anomaly-locations-01090500-01090600.json"
    trace_folder = "D://Data/cdn-monitor-data/aws-0109/tr/"
    anomaly_locations = json.load(open(anomaly_loc_file))
    aws_loc_precision = get_localization_precision(anomaly_locations, trace_folder)
    draw_anomaly_location_types(anomaly_locations, toSave=False, figName="anomaly_loc_typ_aws_0109")


    trace_folder = "D://Data/cdn-monitor-data/azure-0112/tr/"
    anomaly_loc_file = "D://Data/cdn-monitor-data/azure-0112/anomaly/anomaly-locations-01120400-01120500.json"
    anomaly_locations = json.load(open(anomaly_loc_file))
    az_loc_precision = get_localization_precision(anomaly_locations, trace_folder)
    draw_anomaly_location_types(anomaly_locations, toSave=False, figName="anomaly_loc_typ_azure_0112")


    fig, ax = plt.subplots()
    draw_cdf(aws_loc_precision, 'k-', 'AWS CloudFront')
    draw_cdf(az_loc_precision, 'b-.', 'Azure CDN')
    ax.set_ylabel(r'Anomaly Localization Precision', fontsize=20)
    ax.set_xlabel(r'The percentage of anomaly events', fontsize=20)
    ax.set_title('The CDF of localization precision', fontsize=20)
    plt.legend(loc=0)

    plt.show()
    save_fig(fig, "Anomaly_localization_precision_comparison")


    #precision_over_peernum = get_precision_over_peernum(anomaly_locations, trace_folder)
    #fig, ax = plt.subplots()
    #plot_scatter(precision_over_peernum[:, 1], precision_over_peernum[:, 0])