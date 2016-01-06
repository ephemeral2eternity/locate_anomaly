import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def remove_normal_users(anomaly_cnts):
    updated_anomaly_cnts = {}
    for client in anomaly_cnts.keys():
        if anomaly_cnts[client] > 0:
            updated_anomaly_cnts[client] = anomaly_cnts[client]
    return updated_anomaly_cnts


def plot_event_cnts(anomaly_cnts, isDraw=True, figName="anomaly_cnts_plt"):
    user_num = len(anomaly_cnts.keys())
    sorted_cnts = sorted(anomaly_cnts.values(), reverse=True)

    fig, ax = plt.subplots()
    plt.plot(sorted_cnts, linewidth=1.0)
    ax.set_xlabel('User ID', fontsize=20)
    ax.set_ylabel('The number of anomaly events', fontsize=20)
    plt.show()

    if isDraw:
        save_fig(fig, figName)


def draw_event_cnts(anomaly_cnts, isDraw=True, figName="anomaly_cnts_bar"):
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

    if isDraw:
        save_fig(fig, figName)

def save_fig(fig, figName):
    pdf = PdfPages('./imgs/' + figName + '.pdf')
    pdf.savefig(fig)
    pdf.close()