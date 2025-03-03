# from lxml import etree
import requests
import os
import time
import re
from bs4 import BeautifulSoup
from parsel import Selector
import config
import yaml
import push
import sys
sys.path.append('/app/grpc')
import grpc
import Dvrpc_pb2
import Dvrpc_pb2_grpc
PATH=r'.\Dvspider'


# 我是一个数据结构，存放了爬到的文本数据，以及url
class Animate:
    def __init__(self,title,poster_url,marks,introduce,tags,roles_cvs_dict,picture_url,detail_dict,comments):
        self.title=title
        self.poster_url=poster_url
        self.marks=marks
        self.introduce=introduce
        self.tags=tags
        self.roles_cvs_dict=roles_cvs_dict
        self.picture_url=picture_url
        self.detail_dict=detail_dict
        self.comments=comments


def to_yaml(animate,save_path):
    data = {
        'title':animate.title,
        'marks':animate.marks,
        'introduce':animate.introduce,
        'tags':animate.tags,
        'roles_cvs_dict':animate.roles_cvs_dict,
        'detail_dict':animate.detail_dict,
        'comments':animate.comments,
    }
    with open(save_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)
    print("YAML 文件已保存。")


#我们两个负责保存源码和读取源码用于爬虫的开发阶段
def write_data(context):
    with open('data.txt', "w") as file:
        # 写入内容
        file.write(context)
def read_data():
    with open('data.txt', "r") as file:
        data=file.read()
        return data
def remove_data():
    if os.path.exists("data.txt"):
        os.remove("data.txt")
# 我负责创建目录并下载图片海报等，下载大量的图片，调用download_img
def download_imgs(ip,animate):
    PATH = f'./{ip}__{animate.title}/'
    print(PATH)
    os.makedirs(f'./{ip}__{animate.title}',exist_ok=True)
    poster_path=f'{PATH}/{animate.title}.jpg'
    download_img(animate.poster_url,poster_path)
    for role,picture_url in zip(animate.roles_cvs_dict.keys(),animate.picture_url):
        picture_path=f'{PATH}/{role}.jpg'
        download_img(picture_url,picture_path)
    yaml_path=f'{PATH}/{animate.title}.yaml'
    to_yaml(animate,yaml_path)
    remove_data()
    return PATH



# 我负责作为一个worker，每次调用下载一个图片
def download_img(url,save_path):
    try:
        # 此处是http的请求和回应
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"图片已成功下载并保存到 {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载图片时发生错误: {e}")

# 将爬取到的源码保存到本地叫data
def animate_get(url):
    if not os.path.exists("data.txt"):
    # response = requests.get(url)
        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'Cookie':'chii_sec_id=rW4C7u%2FzvUHR%2BETR9njzXlRAANNe6pJ9i2A1kvaj; chii_theme=light; chii_sid=WWsgo1',
            'Accept-Encoding':'gzip, deflate, br, zstd',
            'Accept-Language':'zh-CN,zh;q=0.9',
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding='utf-8'
            html_content = response.text
            print('等待写入')
            write_data(html_content)
            print('写入完成')
            ret = html_content
        except Exception as e:
            print(f'其他失败{e}')
    else:
        ret = read_data()
    return ret

# 将数据抽取出来保存为animate对象
def parse_data(context):
    selector = Selector(text=context)

    # title
    title = selector.css('h1.nameSingle a::text').get().strip()
    # 评分
    marks= selector.css('span.number::text').get()
    #简介
    introduce = ''.join([i.strip() for i in selector.css('div#subject_summary::text').getall()])
    # 标签
    tags = selector.css('div.subject_tag_section div.inner a.l span::text').getall()
    # role_csv_dict角色cv对应字典
    roles = list(i for i in map(lambda x:x.strip(),selector.css('div.subject_section.clearit ul#browserItemList li.user div.info span.tip::text').getall()) if i !='')
    cvs = list(i for i in map(lambda x:x.strip(),selector.css('div.subject_section.clearit ul#browserItemList li.user div.info a::text').getall()) if i !='')
    roles_cvs_dict = dict(zip(roles, cvs))
    # detail_dict时间等详细信息。
    detail_meta=selector.css('div.infobox_container ul#infobox span.tip::text').getall()
    detail_detail=selector.css('div.infobox_container ul#infobox li::text').getall()
    detail_dict=dict(zip(detail_meta, detail_detail))
    # 评论的爬取
    comments = selector.css('div.subject_section div.content_inner.clearit div#entry_list div.item.clearit div.entry div.content::text').getall()
    # 演员照片
    pattern = r"url\(['\"]?([^'\"]+)['\"]?\)"
    picture_url= [f'https:{i[0]}' for i in [re.findall(pattern,i) for i in selector.css('div.subject_section.clearit ul#browserItemList li.user span.userImage span.avatarNeue.avatarSize48.ll::attr(style)').getall()]]
    # 动画海报
    poster_url=f"https:{selector.css('div.mainWrapper div.columns.clearit div#columnSubjectHomeA div#bangumiInfo div.infobox div a img::attr(src)').get()}"
    animate=Animate(title,poster_url,marks,introduce,tags,roles_cvs_dict,picture_url,detail_dict,comments)
    return animate

# 这里需要有一个可以函数构建客户端请求，发送url
def logURL(response,url):
    if response.success:
        try:
            channel =grpc.insecure_channel(f'url-manager:8001')
            stub = Dvrpc_pb2_grpc.URLManagerStub(channel)
            stub.URLToDB(Dvrpc_pb2.URLToDBRequest(url=url))
        except grpc.RpcError as e:
            print(f"记录已爬取的站点失败: {e.details()}")


def main(ip,url):
    data=animate_get(url)
    animate = parse_data(data)
    path=download_imgs(ip,animate)
    response=push.push(path)
    logURL(response,url)
    config.thread_current -= 1

# main('localhost','https://bgm.tv/subject/428735')














