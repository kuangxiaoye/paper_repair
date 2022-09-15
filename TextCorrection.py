# -*- coding:utf-8 -*-
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json
import requests


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


class WebsocketDemo:
    def __init__(self,APPId,APISecret,APIKey,Text):
        self.appid = APPId
        self.apisecret = APISecret
        self.apikey = APIKey
        self.text = Text
        self.url = 'https://api.xf-yun.com/v1/private/s9a87e3ec'

    # calculate sha256 and encode to base64
    def sha256base64(self,data):
        sha256 = hashlib.sha256()
        sha256.update(data)
        digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
        return digest


    def parse_url(self,requset_url):
        stidx = requset_url.index("://")
        host = requset_url[stidx + 3:]
        schema = requset_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise AssembleHeaderException("invalid request url:" + requset_url)
        path = host[edidx:]
        host = host[:edidx]
        u = Url(host, path, schema)
        return u


    # build websocket auth request url
    def assemble_ws_auth_url(self,requset_url, method="POST", api_key="", api_secret=""):
        u = self.parse_url(requset_url)
        host = u.host
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        #print(date)
        # date = "Thu, 12 Dec 2019 01:57:27 GMT"
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        #print(signature_origin)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        #print(authorization_origin)
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }

        return requset_url + "?" + urlencode(values)


    def get_body(self):
        body =  {
            "header": {
                "app_id": self.appid,
                "status": 3,
                #"uid":"your_uid"
            },
            "parameter": {
                "s9a87e3ec": {
                    #"res_id":"your_res_id",
                    "result": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "json"
                    }
                }
            },
            "payload": {
                "input": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 3,
                    "text": base64.b64encode(self.text.encode("utf-8")).decode('utf-8')
                }
            }
        }
        return body

    def get_result(self):
        request_url = self.assemble_ws_auth_url(self.url, "POST", self.apikey, self.apisecret)
        headers = {'content-type': "application/json", 'host':'api.xf-yun.com', 'app_id':self.appid}
        body = self.get_body()
        response = requests.post(request_url, data = json.dumps(body), headers = headers)
        print('onMessage：\n' + response.content.decode())
        tempResult = json.loads(response.content.decode())
        print('text字段解析：\n' + base64.b64decode(tempResult['payload']['result']['text']).decode())



if __name__ == '__main__':
    #控制台获取
    APPId = "30923d39"
    APISecret = "M2Q5ZTBmNDg1NTkxMzJlZjc4OWJkMDAx"
    APIKey = "ada531a118c987f01b841dc9ea9cf6e9"

    #需纠错文本
    Text="由于传统课堂标注学生行为存在一定的弊端，部分研究者开始尝试利用人工智能技术来解决学生行为的识别问题。刘清堂等人提出了基于人工智能的课堂教学行为分析方法[3]，阐述了人工智能时代使用自动化与智能化识别方法的重要性；吴勇等人提出了学生课堂行为数据集[4]，该数据集由11个教室的128个班级的视频组成，动作识别部分包含4276个样本，填补了课堂行为数据集的空白；唐龙宇等人提出使用YOLOV5目标检测模型的课堂行为检测方法[5]，可以识别倾听、向下看、躺下和站立四种行为；Aasim等人提出了使用3D卷积神经网络进行学生行为智能识别的方法[6]。可以发现，当前学生行为智能识别的研究均围绕于数据集、目标检测、行为识别。不过随着研究的深入，一些问题逐渐出现。目前提出的课堂行为专用数据集数量较少，且开源性差，专业的课堂行为数据集依然是当前研究的需要；当前研究大多停留在单帧图片的特征分类，而视频理解技术中的3D模型能够学习到连续的长时间序列信息，结合注意力机制，理论上在课堂行为识别上具有更好的表现；在课堂行为的识别中，学生目标的检测是基本的前提，密集拥挤的学生分布让检测变得困难，行为识别效率自然下降，故需要一种学生分布密集场景下的目标检测方法。综上所述，本文提出了一种基于视频理解技术的学生课堂行为识别方法，如图1。具体工作内容如下"
    demo = WebsocketDemo(APPId,APISecret,APIKey,Text)
    result = demo.get_result()

    #



