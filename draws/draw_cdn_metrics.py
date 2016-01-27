import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import datetime
from draw_utils import *
from outlier_detection import *


def draw_outliers(ax, outliers, ave, three_sigma, text_loc, ts_delta=5):
    ax.axhline(y=ave, color='b')
    ax.annotate('Average Response Time = ' + str(ave), xy=(text_loc+10, ave),
                xytext=(text_loc+10, ave*1.1), xycoords='data', color='b')
    upper_bound = ave+three_sigma
    ax.axhline(y=upper_bound, color='r')
    ax.annotate('$3\sigma$ = ' + str(upper_bound), xy=(text_loc+10, upper_bound),
                xytext=(text_loc+10, upper_bound*1.05), xycoords='data', color='r')

    ## Label the outliers
    for ts in sorted(outliers.keys()):
        ax.axvspan(ts - ts_delta, ts + ts_delta, facecolor='r', alpha=0.5)


def plot_response_time(extracted_srv_logs, ts_range, label_win=60, toSave=False, figName="rsp_time"):
    all_ts = sorted(extracted_srv_logs.keys(), key=float)
    ts_float = []
    rsp_times = []
    rsp_dict = {}
    for ts_str in all_ts:
        cur_rsp_time = extracted_srv_logs[ts_str]["time-taken"]
        rsp_times.append(float(cur_rsp_time))
        ts_float.append(float(ts_str))
        rsp_dict[float(ts_str)] = float(cur_rsp_time)
    fig, ax = plt.subplots()
    p1 = ax.scatter(ts_float, rsp_times, marker='*', c='k', label='Logged Request Response Time')

    ## Compute the mean response time
    outliers, ave, three_sigma = three_sigma_detection(rsp_dict)
    draw_outliers(ax, outliers, ave, three_sigma, ts_range[0]+10)

    ## Get outlier clients
    anomaly_clients = get_outlier_clients(extracted_srv_logs, outliers)
    print anomaly_clients

    num_intvs = int((ts_range[1] - ts_range[0])/label_win) + 1
    ts_labels = [ts_range[0] + x*label_win for x in range(num_intvs)]
    str_ts = [datetime.datetime.fromtimestamp(x*label_win + ts_range[0]).strftime('%H:%M') for x in range(num_intvs)]
    plt.xticks(ts_labels, str_ts, fontsize=15)
    ax.set_xlim(ts_range)
    ax.set_xlabel("Time in a day", fontsize=20)
    ax.set_ylabel("Response Time (seconds)", fontsize=20)

    ## Draw legend
    red_patch = mpatches.Patch(color='r', label='Anomalies detected by $3\sigma$ method', alpha=0.5)
    plt.legend(handles=[p1, red_patch], loc=0)
    plt.show()

    if toSave:
        save_fig(fig, figName)


def plot_cache_miss(extracted_srv_logs, ts_range, label_win=60, toSave=False, figName="cache_miss"):
    all_ts = sorted(extracted_srv_logs.keys(), key=float)
    cache_miss = []
    cache_miss_ts = []
    cache_hit = []
    cache_hit_ts = []
    for ts_str in all_ts:
        cur_cache_miss = extracted_srv_logs[ts_str]["x-edge-response-result-type"]
        if cur_cache_miss == "Hit":
            cache_hit.append(1)
            cache_hit_ts.append(float(ts_str))
        elif cur_cache_miss == "Miss":
            cache_miss.append(-1)
            cache_miss_ts.append(float(ts_str))
        else:
            print "Unknown cache miss status: ", cur_cache_miss
            #cache_hit.append(0)
            #cache_hit_ts.append(float(ts_str))

    fig, ax = plt.subplots()
    ax.stem(cache_hit_ts, cache_hit, markerfmt='bo', linefmt='-b', label='Cache Hits')
    ax.stem(cache_miss_ts, cache_miss, markerfmt='rv', linefmt='--r', label='Cache Misses')

    ## Compute the mean response time
    num_intvs = int((ts_range[1] - ts_range[0])/label_win) + 1
    ts_labels = [ts_range[0] + x*label_win for x in range(num_intvs)]
    str_ts = [datetime.datetime.fromtimestamp(x*label_win + ts_range[0]).strftime('%H:%M') for x in range(num_intvs)]
    plt.xticks(ts_labels, str_ts, fontsize=15)

    str_hit = ['Miss', 'Hit']
    plt.yticks([-1, 1], str_hit, fontsize=15)

    ax.set_xlim(ts_range)
    ax.set_ylim([-1.5, 1.5])
    ax.set_xlabel("Time in a day", fontsize=20)
    ax.set_ylabel("Cache Miss/Hit", fontsize=20)

    ## Draw legend
    # red_patch = mpatches.Patch(color='r', label='Anomalies detected by $3\sigma$ method', alpha=0.5)
    # plt.legend(handles=p, loc=0)
    plt.show()

    if toSave:
        save_fig(fig, figName)

def plot_status_code(extracted_srv_logs, ts_range, label_win=60, toSave=False, figName="http_staus"):
    marker_formats = ['k^', 'bs', 'ro', 'gD', 'm*']
    line_formats = ['k--', 'b-', 'r-.', 'g-', 'm:']
    all_ts = sorted(extracted_srv_logs.keys(), key=float)
    http_status_codes = {}
    http_status_codes = {'1XX' : [], '200' : [], '3XX' : [], '4XX' : [], '5XX' : []}
    status_ts = {'1XX' : [], '200' : [], '3XX' : [], '4XX' : [], '5XX' : []}
    for ts_str in all_ts:
        cur_http_status = extracted_srv_logs[ts_str]["sc-status"]
        if cur_http_status.startswith('1'):
            http_status_codes['1XX'].append(1)
            status_ts['1XX'].append(float(ts_str))
        elif cur_http_status == "200":
            http_status_codes['200'].append(2)
            status_ts['200'].append(float(ts_str))
        elif cur_http_status.startswith('3'):
            http_status_codes['3XX'].append(3)
            status_ts['3XX'].append(float(ts_str))
        elif cur_http_status.startswith('4'):
            http_status_codes['4XX'].append(4)
            status_ts['4XX'].append(float(ts_str))
        elif cur_http_status.startswith('5'):
            http_status_codes['5XX'].append(5)
            status_ts['5XX'].append(float(ts_str))

    fig, ax = plt.subplots()
    code_id = 0
    for status_code in http_status_codes.keys():
        if http_status_codes[status_code]:
            ax.stem(status_ts[status_code], http_status_codes[status_code], markerfmt=marker_formats[code_id], linefmt=line_formats[code_id], label=status_code)
        code_id += 1

    ## Compute the mean response time
    num_intvs = int((ts_range[1] - ts_range[0])/label_win) + 1
    ts_labels = [ts_range[0] + x*label_win for x in range(num_intvs)]
    str_ts = [datetime.datetime.fromtimestamp(x*label_win + ts_range[0]).strftime('%H:%M') for x in range(num_intvs)]
    plt.xticks(ts_labels, str_ts, fontsize=15)

    str_hit = ['1XX', '200', '3XX', '4XX', '5XX']
    plt.yticks([1, 2, 3, 4, 5], str_hit, fontsize=15)

    ax.set_xlim(ts_range)
    ax.set_ylim([0, 5.5])
    ax.set_xlabel("Time in a day", fontsize=20)
    ax.set_ylabel("HTTP Status Code", fontsize=20)

    ## Draw legend
    # red_patch = mpatches.Patch(color='r', label='Anomalies detected by $3\sigma$ method', alpha=0.5)
    # plt.legend(handles=p, loc=0)
    plt.show()

    if toSave:
        save_fig(fig, figName)