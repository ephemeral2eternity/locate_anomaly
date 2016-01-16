import re
import socket
from ipinfo import *

def is_hostname(hop_name):
    ch_pattern = re.compile('[a-zA-Z]')
    # print hop_name
    chars = re.findall(ch_pattern, hop_name)
    if (len(chars) > 0) and ('.' in hop_name):
        return True
    else:
        return False

def is_ip(ip_addr):
    re_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    if re_ip.match(ip_addr):
        return True
    else:
        return False

def host2ip(hop_name):
    try:
        ip = socket.gethostbyname(hop_name)
    except socket.error:
        # print "[Error]The hostname : ", hop_name, " can not be resolved!"
        ip = "*"
    return ip


def get_ip_and_hostname(ip_or_hostname):
    ip = None
    name = None
    if is_hostname(ip_or_hostname):
        name = ip_or_hostname
        ip = host2ip(ip_or_hostname)
    elif is_ip(ip_or_hostname):
        ip = ip_or_hostname
        ip_info = ipinfo(ip_or_hostname)
        if "hostname" not in ip_info.keys():
            name = ip_or_hostname
        else:
            name = ip_info["hostname"]
            if '.' not in name:
                name = ip_or_hostname
    else:
        print "[Error] Input argument in function get_ip_and_hostname(): ", ip_or_hostname, " is neither an ip nor a hostname!"
        exit(-1)

    return ip, name


def read_hop_info(hopinfo_path, hop_ip):
    default_hop_path = hopinfo_path + hop_ip + ".json"
    if os.path.exists(default_hop_path):
        try:
            hop_info = json.load(open(default_hop_path))
        except:
            os.remove(default_hop_path)
            if is_ip(hop_ip):
                hop_info = ipinfo(hop_ip)
                save_ipinfo(hopinfo_path, hop_info)
            else:
                hop_info = {}
    else:
        if not is_ip(hop_ip):
            hop_ip = host2ip(hop_ip)

        if is_ip(hop_ip):
            hop_info = ipinfo(hop_ip)
            save_ipinfo(hopinfo_path, hop_info)
        else:
            hop_info = {}
    return hop_info


def verify_hostname(ip_or_hostname, hops_folder):
    name = None
    if is_hostname(ip_or_hostname):
        name = ip_or_hostname
    elif is_ip(ip_or_hostname):
        ip_info = read_hop_info(hops_folder, ip_or_hostname)
        if "hostname" not in ip_info.keys():
            name = ip_or_hostname
        else:
            name = ip_info["hostname"]
            if '.' not in name:
                name = ip_or_hostname
    else:
        print "[Error] Input argument in function get_ip_and_hostname(): ", ip_or_hostname, " is neither an ip nor a hostname!"
        exit(-1)

    return name



if __name__ == "__main__":
    hop_name = "et-5-0-0.120.rtr.eqny.net.internet2.edu"
    if is_hostname(hop_name):
        ip = host2ip(hop_name)
    else:
        ip = hop_name

    # print ip