import requests
from urllib import parse
from bs4 import BeautifulSoup
import re
import json
import os

COMMENT_REQUEST_URL = "https://comment.bilibili.com/"
MAIN_HOST_URL = "https://www.bilibili.com/video/"
CHAT_RESOURCE_DIR = "chat_xml_res/"
PACKAGE_NAME = "bilibili_crawler"
DEFAULT_DIR = ''


def find_cid_with_aid(av_number):
    """
    用bilibili的av號，查找出對應的cid(commend_id)
    回傳cid_list
    """
    m = re.match('av[0-9]+',av_number)
    if m == None:
        raise Exception("av號格式錯誤")
    av_number = m.group(0)
    req = requests.get(parse.urljoin(MAIN_HOST_URL, av_number))
    bf = BeautifulSoup(req.text, 'html.parser')
    scripts_tag = bf.find_all("script")

    start = re.escape("window.__INITIAL_STATE__=")
    end = re.escape(
        ";(function(){var s;(s=document.currentScript||document.scripts[document.scripts.length-1]).parentNode.removeChild(s);}());")
    m = re.match(start + "(.+)" + end, scripts_tag[3].string)
    results = json.loads(m.group(1))
    ret_list = list()
    for video in results["videoData"]["pages"]:
        ret_list.append(str(video["cid"]))
    return ret_list


def cid_xml_file(cid):
    """
    用cid在目錄下瀉入檔案(cid).xml
    """
    fd_name = str(cid) + ".xml"
    req = requests.get(COMMENT_REQUEST_URL + fd_name)
    req.encoding = 'utf-8'
    with open(fd_name, 'w', encoding="utf-8") as f:
        f.write(req.text)


def get_comment_data(av_numbers, store="chat_xml_res/"):
    """
    可以下載xml檔案給api讀取
    預設目錄是 current work dir 的 chat_xml_res/
    """
    try:
        os.mkdir(store)
    except FileExistsError as identifier:
        pass
    os.chdir(store)
    exist = os.listdir('.')
    request_list = [i for i in av_numbers if i not in exist]
    if len(request_list) == 0:
        raise Exception("不需要爬取資料，資料已存在或沒有輸入av號", request_list)
    for av_number in request_list:
        req_cids = find_cid_with_aid(av_number)
        os.mkdir("./" + av_number)
        os.chdir(av_number)
        for req_cid in req_cids:
            cid_xml_file(req_cid)
        os.chdir("..")
    os.chdir('..')
