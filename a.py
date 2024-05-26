import time
import os
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
import threading
from queue import Queue
import eventlet
eventlet.monkey_patch()

###urls城市根据自己所处的地理位置修改
urls = [
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIGNpdHk9cWluaHVhbmdkYW8%3D",#秦皇岛
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIGNpdHk9InRhbmdzaGFuIg%3D%3D",#唐山
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIHJlZ2lvbj0iaGViZWki",#河北
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIGNpdHk9ImxhbmdmYW5nIg%3D%3D",#廊坊
    #"https://fofa.info/result?qbase64=InVkcHh5IiAmJiBhc249IjQxMzQiICYmIHJlZ2lvbj0iaGViZWki"#河北
]


def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/status"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)

    return modified_urls


def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=0.5)
        if response.status_code == 200:
            return url
    except requests.exceptions.RequestException:
        pass
    return None


results = []

for url in urls:
    try:
        # 创建一个Chrome WebDriver实例
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    
        driver = webdriver.Chrome(options=chrome_options)
        # 使用WebDriver访问网页
        driver.get(url)  # 将网址替换为你要访问的网页地址
        time.sleep(10)
        # 获取网页内容
        page_content = driver.page_source
    
        # 关闭WebDriver
        driver.quit()
    
        # 查找所有符合指定格式的网址
        pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
        urls_all = re.findall(pattern, page_content)
        # urls = list(set(urls_all))  # 去重得到唯一的URL列表
        urls = set(urls_all)  # 去重得到唯一的URL列表
        x_urls = []
        for url in urls:  # 对urls进行处理，ip第四位修改为1，并去重
            url = url.strip()
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_dot_start = url.find(".") + 1
            ip_dot_second = url.find(".", ip_dot_start) + 1
            ip_dot_three = url.find(".", ip_dot_second) + 1
            base_url = url[:ip_start_index]  # http:// or https://
            ip_address = url[ip_start_index:ip_dot_three]
            port = url[ip_end_index:]
            ip_end = "1"
            modified_ip = f"{ip_address}{ip_end}"
            x_url = f"{base_url}{modified_ip}{port}"
            x_urls.append(x_url)
        urls = set(x_urls)  # 去重得到唯一的URL列表

        valid_urls = []
        #   多线程获取可用url
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for url in urls:
                url = url.strip()
                modified_urls = modify_urls(url)
                for modified_url in modified_urls:
                    futures.append(executor.submit(is_url_accessible, modified_url))

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    valid_urls.append(result)    
        
        for url in valid_urls:
            print(f"可用url:{url}")
            # 创建一个Chrome WebDriver实例
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        
            driver = webdriver.Chrome(options=chrome_options)
            # 使用WebDriver访问网页
            driver.get(url)  # 将网址替换为你要访问的网页地址
            time.sleep(10)
            # 获取网页内容
            page_content = driver.page_source
        
            # 关闭WebDriver
            driver.quit()
        
            # 查找所有符合指定格式的网址
            #if "<td>1</td>" or "<td>2</td>" or "<td>3</td>" or "<td>4</td>"  or "<td>5</td>" or "<td>6</td>" or "<td>7</td>" or "<td>8</td>" in page_content:
            if "0.0" in page_content:
                print(url)
                udpxy_urls = []# 修改文件转发地址
                ip_start_index = url.find("//") + 2
                ip_dot_start = url.find(".") + 1
                ip_index_second = url.find("/", ip_dot_start)
                base_url = url[:ip_start_index]  # http:// or https://
                ip_address = url[ip_start_index:ip_index_second]
                url_x = f"{base_url}{ip_address}"
                udpxy_url = f"{url_x}"
                results.append(udpxy_url)
                
    except:
        continue
channels = []
with open("iptv.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        #print(line)
        line = line.strip()
        if line:
            channel_name,channel_url = line.split(",")
            for udpxy_url in results:
                #print(udpxy_url)
                channel = f"{channel_name},{udpxy_url}/{channel_url}"
                channels.append(channel)


result_counter = 8  # 每个频道需要的个数
with open("itvlist.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视(电信),#genre#\n')
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
    file.write('数字(电信),#genre#\n')
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
    file.write('卫视(电信),#genre#\n')
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
    file.write('其他(电信),#genre#\n')
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
                        
                     
