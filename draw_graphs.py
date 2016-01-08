import numpy as np
import matplotlib.pyplot as plt
import json
import os
from matplotlib.backends.backend_pdf import PdfPages


def remove_normal_users(anomaly_cnts):
    updated_anomaly_cnts = {}
    for client in anomaly_cnts.keys():
        if anomaly_cnts[client] > 0:
            updated_anomaly_cnts[client] = anomaly_cnts[client]
    return updated_anomaly_cnts


def plot_event_cnts(anomaly_cnts, toSave=True, figName="anomaly_cnts_plt"):
    user_num = len(anomaly_cnts.keys())
    sorted_cnts = sorted(anomaly_cnts.values(), reverse=True)

    fig, ax = plt.subplots()
    plt.plot(sorted_cnts, linewidth=1.0)
    ax.set_xlabel('User ID', fontsize=15)
    ax.set_ylabel('The number of anomaly events', fontsize=15)
    plt.show()

    if toSave:
        save_fig(fig, figName)


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
    plt.show()

    if toSave:
        save_fig(fig, figName)


def draw_anomaly_location_cnts(anomaly_locs, toSave=False, figName="anomaly_loc_typ_cnts"):
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

    plt.show()

    if toSave:
        save_fig(fig, figName)


def save_fig(fig, figName):
    pdf = PdfPages('./imgs/' + figName + '.pdf')
    pdf.savefig(fig)
    fig.savefig('./imgs/'+figName+'.png', dpi=300, format='png', bbox_inches='tight')
    pdf.close()


if __name__ == "__main__":

    ## Default data folder
    anomaly_loc_file = "D://Data/cdn-monitor-data/azure-0105/anomaly/anomaly-locations-01050440-01050510.json"

    anomaly_locations = json.load(open(anomaly_loc_file))
    draw_anomaly_location_cnts(anomaly_locations, toSave=True, figName="anomaly_loc_typ_cnts")