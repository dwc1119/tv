import time
import requests
import re
import cv2  # 导入OpenCV库

###urls城市根据自己所处的地理位置修改
urls = [
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIGNpdHk9ImNoZW5nZHUi",#成都电信
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIGNpdHk9Imxlc2hhbiI%3D",#乐山电信
    #"https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIGNpdHk9ImxhbmdmYW5nIg%3D%3D",
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIHJlZ2lvbj0i5Zub5bedIg%3D%3D"#四川电信
   
]

def extract_unique_ip_ports(url):
    try:
        response = requests.get(url)
        time.sleep(10)
        html_content = response.text
        # 使用正则表达式匹配IP地址和端口号
        ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
        unique_ips_ports = list(set(ips_ports))  # 去除重复的IP地址和端口号
        return unique_ips_ports

    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    try:
        # 构造完整的视频URL
        video_url = f"http://{ip_port}{urls_udp}"
        # 用OpenCV读取视频
        cap = cv2.VideoCapture(video_url)
        
        # 检查视频是否成功打开
        if not cap.isOpened():
            print(f"视频URL {video_url} 无效")
            return None
        else:
            # 读取视频的宽度和高度
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"视频URL {video_url} 的分辨率为 {width}x{height}")
            # 检查分辨率是否大于0
            if width > 0 and height > 0:
                return ip_port  # 返回有效的IP和端口
            # 关闭视频流
            cap.release()
    except Exception as e:
        print(f"访问 {ip_port} 失败: {e}")
    return None           

# 定义组播地址和端口
urls_udp = "/udp/239.93.0.184:5140"

# 提取唯一的IP地址和端口号
ip_ports = []
valid_ips = []
for url in urls:
    print(url)
    ip_ports = extract_unique_ip_ports(url)
    if ip_ports:
        print(ip_ports)
        #测试每个IP地址和端口号，直到找到一个可访问的视频流
        for ip_port in ip_ports:
            valid_ip = check_video_stream_connectivity(ip_port, urls_udp)
            if valid_ip:
                print(f"找到可访问的视频流服务: {valid_ip}")
                valid_ips.append(valid_ip)
        
        
channels = []
with open("iptv3.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        #print(line)
        line = line.strip()
        if line:
            channel_name,channel_url = line.split(",")
            for valid_ip in valid_ips:
                #print(udpxy_url)
                channel = f"{channel_name},http://{valid_ip}/{channel_url}"
                channels.append(channel)



result_counter = 16  # 每个频道需要的个数
with open("itvlist.txt", 'a', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视(备用),#genre#\n')
    for channel in channels:
        channel_name,channel_url = channel.split(",")
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(channel + "\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(channel + "\n")
                channel_counters[channel_name] = 1
    channel_counters = {}  
    file.write('数字(备用),#genre#\n')
    for channel in channels:
        channel_name, channel_url = channel.split(",")
        if '天元' in channel_name or '风云' in channel_name or '球' in channel_name or '影' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('卫视(备用),#genre#\n')
    for channel in channels:
        channel_name,channel_url = channel.split(",")
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(channel + "\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(channel + "\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('其他(备用),#genre#\n')
    for channel in channels:
        channel_name,channel_url = channel.split(",")
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(channel + "\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(channel + "\n")
                channel_counters[channel_name] = 1

with open("itvlist.m3u", 'a', encoding='utf-8') as file:
    channel_counters = {}
    file.write('#EXTM3U\n')
    for channel in channels:
        channel_name,channel_url = channel.split(",")
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"央视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    #file.write('卫视频道,#genre#\n')
    for channel in channels:
        channel_name,channel_url = channel.split(",")
        if '卫视' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"卫视频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    #file.write('其他频道,#genre#\n')
    for channel in channels:
        channel_name,channel_url = channel.split(",")
        if 'CCTV' not in channel_name and '卫视' not in channel_name and '测试' not in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                    file.write(f"{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"#EXTINF:-1 group-title=\"其他频道\",{channel_name}\n")
                file.write(f"{channel_url}\n")
                channel_counters[channel_name] = 1                     
                        
                     
