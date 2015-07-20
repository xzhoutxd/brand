#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(r'../')
import re
import json
import base.Common as Common
import base.Config as Config
from base.MyCrawler import MyCrawler

import warnings
warnings.filterwarnings("ignore")

class ChanelBag():
    '''A class of chanel bag'''
    def __init__(self):
        # 抓取设置
        self.crawler     = MyCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.chanel.com'
        self.price_url  = 'http://ws.chanel.com/pricing/zh_CN/fashion/%s/?i_client_interface=fsh_v3_misc&i_locale=zh_CN&format=json&callback=localJsonpPricingCallback'
        self.refers     = None

        # 抓取商品列表
        self.links      = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return
       
        m = re.search(r'"products":\s*(\[.+?\])\s*},\s*"deeplink"', page, flags=re.S)
        if m:
            prods   = m.group(1)
            js_items= json.loads(prods)

            for js_item in js_items:
                serie_title = js_item["title"]
                serie_items = js_item["items"]
                
                for serie_item in serie_items:
                    if not serie_item.has_key("title"): continue
                    
                    i_title = serie_item["title"]
                    i_url   = self.home_url + serie_item["href"]
                     
                    self.links.append((serie_title, i_title, i_url))
                    print '# bagPage :', serie_title, i_title, i_url
                
    def bagItems(self):
        for link in self.links: self.itemPage(link)

    def itemPage(self, val):
        serie_title, i_title, i_url = val
        
        page = self.crawler.getData(i_url, self.refers)
        if not page or page == '': return
        
        i_name, i_img, ref_price, i_size, i_price, i_unit = '', '', '', '', '', ''
        
        m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
        if m: i_name = m.group(1)
        
        m = re.search(r'<div class="productimage.*?"><img src="(.+?)" alt=".+?"/>', page, flags=re.S)
        if m: i_img  = self.home_url + m.group(1)

        m = re.search(r'<p class="size info">(.+?)</p>', page, flags=re.S)
        if m: i_size = m.group(1)
                
        m = re.search(r'<div class="ref info">\s*<p>(.+?)</p>', page, flags=re.S)
        if m:
            refs = m.group(1).split(' ')[:-1]
            ref_price = ''.join(refs)

            p_url = self.price_url %ref_price
            data = self.crawler.getData(p_url, i_url)
            if not data or data == '': return
            
            # 抽取json报文
            r = re.search(r'localJsonpPricingCallback\(\[(.+?)\]\)', data, flags=re.S)
            if r:
                js_data = json.loads(r.group(1))
                i_price = js_data["price"]["amount"]
                i_unit  = js_data["price"]["currency-symbol"]
        
        s = '%s|%s|%s|%s|%s|%s|%s|%s' %(serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img)
        self.items.append(s)    
        print '# itemPage :', serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))


class McmBag():
    '''A class of mcm bag'''
    def __init__(self):
        # 抓取设置
        self.crawler     = MyCrawler()

        # 品牌官网链接
        self.home_url    = 'http://www.mcmworldwide.com'
        self.women_url   = self.home_url + '/en/women'
        self.bag_url     = self.women_url + '/bags'
        self.backpack_url= self.women_url + '/backpacks'
        self.leather_url = self.women_url + '/small-leather-goods'
        self.refers      = None

        # 抓取商品列表
        self.links       = []
        self.items       = []
        
    def bagPage(self):
        url = self.bug_url + '#start=0&sz=32&srule=New'
        page = self.crawler.getData(self.bag_url, self.women_url)
        if not page or page == '': return
        
        
        
        

if __name__ == '__main__':
    b = ChanelBag()

    b_url = 'http://www.chanel.com/zh_CN/fashion/products/handbags/g.spring-summer-2015.c.15S.html'
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'chanel_%s.txt' %Common.today_ss()
    print f
    b.outItems(f)
    
