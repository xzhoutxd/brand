#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import base.Config as Config
import base.Common as Common
from base.Crawler import Crawler

class MyCrawler():
    '''A class to crawl web pages'''
    def __init__(self, timeout=(10,20)):
        # crawler
        self.crawler = Crawler()
 
        # forward
        self.forward       = False

        # cookie
        self.session_cookie= {}
        self.use_cookie    = False

        # vip http get超时时间
        self.timeout       = timeout

        # cookie
        self.crawl_cookie  = {}

        # 网页编码
        self.f_coder       = 'gbk'
        self.t_coder       = 'utf-8'

    def __del__(self):
        self.crawler = None

    def setCookie(self, _cookie):
        #print '# setCookie :', _cookie
        self.session_cookie = _cookie

    def useCookie(self, flag=False):
        self.use_cookie = flag

    def charset(self, data):
        coder = 'utf-8'
        if data and data != '':
            data = re.sub('"|\'|\ |\-', '', data.lower())
            if re.search(r'charset=gbk', data):
                coder = 'gbk'
            elif re.search(r'charset=gb2312', data):
                coder = 'gb2312'
        return coder

    def buildHeader(self, refers='', terminal='1'):
        # base header
        _header = None
        if terminal == '1':    # PC端
            _header = Config.g_httpHeader
            _header['User-agent'] = random.choice(Config.g_pcAgents)
        elif terminal == '2':  # wap端
            _header = Config.g_wapHeader
            _header['User-agent'] = random.choice(Config.g_wapAgents)
        elif terminal == '3':  # app端
            _header = Config.g_phoneHeader
            _header['User-agent'] = random.choice(Config.g_phoneAppAgents)
        elif terminal == '4':  # pad端
            _header = Config.g_padHeader
            _header['User-agent'] = random.choice(Config.g_padAppAgents)
        else:
            _header = Config.g_httpHeader
            _header['User-agent'] = random.choice(Config.g_pcAgents)

        # refers
        if refers and refers != '': _header['Referer'] = refers
        return _header

    # To check page
    def checkPage(self, url, data):
        # 异常处理1: 网站deny页
        m = re.search(r'<TITLE>403拒绝访问</TITLE>', data)
        if m:
            e = "# Deny page: 403拒绝访问错误, url=%s" %url
            raise Common.DenypageException(e)
        
        # 异常处理2: 页面不存在
        m = re.search(r'<div class=".+?">很抱歉，您查看的页面找不到了！</div>', data)
        if m:
            e = "# No page: 很抱歉，您查看的页面找不到了！, url=%s" %url
            raise Common.NoPageException(e)        

    def getData(self, url, refers='', decode=True, terminal='1'):
        # when null url, exit function
        if not url or not re.search(r'http://', url):
            return None

        # To build header
        _header = self.buildHeader(refers, terminal)

        # To forge vip cookie
        _cookie = self.session_cookie if self.use_cookie else self.crawl_cookie
       
        # 打开连接收取数据
        r = self.crawler.session.get(url, headers=_header, cookies=_cookie, timeout=self.timeout)

        # 网页内容
        data = r.content

        # 检查是否重定向
        self.forward = (len(r.history) > 0) 

        # 跟踪cookie
        if not self.use_cookie and len(r.cookies) > 0: self.crawl_cookie = Common.cookieJar2Dict(r.cookies)

        # 网页编码
        self.f_coder = self.charset(r.headers.get('content-type'))

        # 关闭结果
        r.close()

        # 网页编码归一化
        if decode and self.f_coder != self.t_coder: data = data.decode(self.f_coder,'ignore').encode(self.t_coder,'ignore')

        # pc/wap网页异常
        if terminal in ['1', '2']: self.checkPage(url, data)

        # 返回抓取结果
        return data

if __name__ == '__main__1':
    url     = 'http://www.vip.com'
    refers  = 'http://www.baidu.com'
    crawler = MyCrawler()
    data = crawler.getData(url, refers)
    print data

if __name__ == '__main__2':
    url     = 'http://m.vip.com'
    refers  = 'http://m.vip.com'
    crawler = MyCrawler()
    data = crawler.getData(url, refers, terminal='2')
    print data
