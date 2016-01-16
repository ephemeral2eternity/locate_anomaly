from draws.draw_network import *
from draws.draw_utils import *
from draws.draw_qoe_related import *
from draws.draw_cdn_metrics import *
from read_data.load_metrics import *

# users_to_compare = ["pl2.cs.unm.edu", "pl3.cs.unm.edu", "pl4.cs.unm.edu"]

users_to_compare = ["planetlab-2.sjtu.edu.cn", "pl2.pku.edu.cn", "pl2.zju.edu.cn"]

anomaly_events_file = "D://Data/cdn-monitor-data/aws-0109/anomaly/anomaly-events-01090500-01090600.json"
cdn_log_file = "D://Data/cdn-monitor-data/aws-0109/cdn-logs.json"
qoe_folder = "D://Data/cdn-monitor-data/aws-0109/qoe/"
tr_folder = "D://Data/cdn-monitor-data/aws-0109/tr/"
hops_folder = "D://Data/cdn-monitor-data/aws-hops/"


ts_range = [1452317400, 1452318600]
# ts_range = [1452315600, 1452316800]
SLA = 1
route_files = []

line_styles = ['m-', 'b--', 'k-*', 'r->', 'y-s', 'k-h', 'g-^', 'b-o', 'r-*', 'm-d', 'y-<', 'g-o', 'b-8']
marker_styles = ['8', '>', 'h', '*', 's', 'o', 'v', 'D', 'd']
cors = ['m', 'b', 'k', 'r', 'y', 'g', 'k', 'b', 'r']
# usr_alpha = [-x*0.6/float(len(users_to_compare))+0.8 for x in range(len(users_to_compare))]
anomalies = load_user_anomalies(anomaly_events_file, users_to_compare, ts_range)

fig, ax_list = plt.subplots(len(users_to_compare), sharex=True)
user_id = 0
label_win = 120
for user in users_to_compare:
    # print user
    # user_qoe_file = find_cur_file(qoe_folder, user, ts_range[0])
    user_qoe_files = find_files_in_range(qoe_folder, user, ts_range)
    user_qoes = {}
    for user_qoe_file in user_qoe_files:
        cur_user_qoes, _ = load_qoe_in_range(qoe_folder + user_qoe_file, ts_range)
        user_qoes = dict(cur_user_qoes.items() + user_qoes.items())

    plot_qoe(ax_list[user_id], user_qoes, marker_styles[user_id], user, cors[user_id])
    # print corresponding_cors[user_id], usr_alpha[user_id]
    draw_anomalies(ax_list[user_id], anomalies[user])

    # user_tr_file = find_cur_file(tr_folder, "TR_" + user, ts_range[1])
    #route_files.append(user_tr_file)

    ## Change the time stamp ticks
    num_intvs = int((ts_range[1] - ts_range[0])/label_win) + 1
    ts_labels = [ts_range[0] + x*label_win for x in range(num_intvs)]
    str_ts = [datetime.datetime.fromtimestamp(x*label_win + ts_range[0]).strftime('%H:%M') for x in range(num_intvs)]
    plt.xticks(ts_labels, str_ts, fontsize=15)
    ax_list[user_id].axhline(y=SLA, color='r')

    ax_list[user_id].annotate('Expected QoE = 1', xy=(1452315740, 1), xytext=(1452315740, 1.1), xycoords='data', color='r')

    ax_list[user_id].set_xlim(ts_range)
    ax_list[user_id].set_ylim([0,5.5])

    ax_list[user_id].set_title(user)

    # plt.legend(4)
    # plt.legend(loc=(0.1, 0.4))
    user_id += 1

fig.text(0.04, 0.5, "Chunk QoE (0-5)", va='center', rotation='vertical', fontsize=20)
ax_list[-1].set_xlabel("Time in a day", fontsize=20)
# ax_list[-1].set_ylabel("Chunk QoE (0-5)", fontsize=20)

red_patch = mpatches.Patch(color='r', label='Anomaly', alpha=0.5)
plt.legend(handles=[red_patch], loc=(0.8, len(users_to_compare)+0.5))
plt.show()
save_fig(fig, "QoE_based_anomaly_detection_aws_0109_user_group2")


## Read the info from the logs file
extracted_srv_logs = extract_logs(cdn_log_file, ts_range)
# print extracted_srv_logs
plot_response_time(extracted_srv_logs, ts_range, toSave=True, figName="rsp_time_aws_0109", label_win=label_win)
plot_cache_miss(extracted_srv_logs, ts_range, toSave=True, figName="cache_miss_aws_0109", label_win=label_win)
plot_status_code(extracted_srv_logs, ts_range, toSave=True, figName="http_status_aws_0109", label_win=label_win)

#routes = read_route_info(tr_folder, route_files, info_name="Hops")
#route_graph, srv_nodes, user_nodes = route2graph(routes, hops_folder)
#draw_network(route_graph, srv_nodes, user_nodes, hops_folder)