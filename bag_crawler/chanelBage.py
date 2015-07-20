#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(r'../')
import re
import json
import time
import base.Common as Common
import base.Config as Config
#from base.MyCrawler import MyCrawler
from base.RetryCrawler import RetryCrawler
from bagItem import BagItem
from bagItemM import BagItemM

import warnings
warnings.filterwarnings("ignore")

class ChanelBag():
    '''A class of chanel bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.chanel.com'
        self.price_url  = 'http://ws.chanel.com/pricing/zh_CN/fashion/%s/?i_client_interface=fsh_v3_misc&i_locale=zh_CN&format=json&callback=localJsonpPricingCallback'
        self.refers     = None

        # 品牌type
        self.brand_type = 'chanel'

        # 抓取商品列表
        self.link_list = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return

        f_url = 'http://www.chanel.com/zh_CN/fashion/products/handbags/g.metiers-d-art-paris-salzburg-2014-15.c.15A.html'
        m = re.search(r'<div class="category-container category-black".+?>.+?<ul>\s*<li>\s*<a class="no-select" target="_blank" href="(.+?)" data-cat="查看系列">', page, flags=re.S)
        if m:
            f_url = self.home_url + m.group(1)

        page = self.crawler.getData(f_url, url)
        if not page or page == '': return

        tab_list = []
        m = re.search(r'<div class="mosaic-nav">\s*<ul class="nav">(.+?)</ul>', page, flags=re.S)
        if m:
            tab_list_info = m.group(1)
            p = re.compile(r'<li class="no-select nav-item">\s*<a.+?href="(.+?)">\s*<h2>(.+?)</h2>\s*</a>', flags=re.S)
            for tab_info in p.finditer(tab_list_info):
                tab_url, tab_name = tab_info.group(1), re.sub(r'<.+?>','',tab_info.group(2).replace('&nbsp;',' ').strip())
                if tab_url == '#':
                    tab_list.append((tab_name, f_url))
                else:
                    tab_list.append((tab_name, self.home_url+tab_url))

        refers = url
        for tab in tab_list:
            tab_name, tab_url = tab
            print '# tab:',tab_name, tab_url
            tab_page = self.crawler.getData(tab_url, refers)
            refers = tab_url
            m = re.search(r'"products":\s*(\[.+?\])\s*},\s*"deeplink"', page, flags=re.S)
            if m:
                prods   = m.group(1)
                js_items= json.loads(prods)

                for js_item in js_items:
                    i_title = js_item["title"].replace('&nbsp;',' ')
                    items = js_item["items"]
                    
                    for item in items:
                        if not item.has_key("title"): continue
                        
                        i_name = item["title"].replace('&nbsp;',' ')
                        i_url   = self.home_url + item["href"]
                         
                        print tab_name, i_title, i_name, i_url
                        self.link_list.append((tab_name, i_title, tab_url, i_name, i_url))
                
    def bagItems(self):
        #for link in self.links: self.itemPage(link)
        max_th = 10
        if len(self.link_list) > max_th:
            m_itemsObj = BagItemM(self.home_url,self.brand_type, max_th)
        else:
            m_itemsObj = BagItemM(self.home_url,self.brand_type, len(self.link_list))
        m_itemsObj.createthread()
        m_itemsObj.putItems(self.link_list)
        m_itemsObj.run()
        self.items.extend(m_itemsObj.items)

    def itemPage(self, val):
        serie_title, i_title, refers, i_name, i_url = val
        
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return
        
        i_name, i_img, ref_price, i_size, i_price, i_unit, i_number = '', '', '', '', '', '', ''
        

        m = re.search(r'<div class="product-details details".*?>.+?<p class="description info.*?">(.+?)</p>', page, flags=re.S)
        if m: i_name = re.sub(r'<.+?>', '', m.group(1)).strip()
        else:
            m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
            if m: i_name = m.group(1).split('-')[0].strip()
        
        m = re.search(r'<div class="productimage.*?"><img src="(.+?)".*?/>', page, flags=re.S)
        if m: i_img  = self.home_url + m.group(1)

        p = re.compile(r'<p class="size info">(.+?)</p>', flags=re.S)
        for size in p.finditer(page):
            if self.item_size != '': i_size += '-' + size.group(1)
            else: i_size = size.group(1)
                
        #m = re.search(r'<div class="ref info">\s*<p>(.+?)</p>', page, flags=re.S)
        #if m:
        p = re.compile(r'<div class="ref info">\s*<p>(.+?)</p>', flags=re.S)
        for number in p.finditer(page):
            item_number = number.group(1)
            if self.item_number != '': self.item_number += '-' + item_number
            else: self.item_number = item_number

            refs = item_number.split(' ')[:-1]
            ref_price = ''.join(refs)

            p_url = self.price_url %ref_price
            data = self.crawler.getData(p_url, i_url)
            if not data or data == '': return
            
            # 抽取json报文
            r = re.search(r'localJsonpPricingCallback\(\[(.+?)\]\)', data, flags=re.S)
            if r:
                price, unit = '', ''
                try:
                    js_data = json.loads(r.group(1))
                    price, unit = js_data["price"]["amount"], js_data["price"]["currency-symbol"]
                except Exception as e:
                    m = re.search(r'"amount":"(.+?)"', data, flags=re.S)
                    if m: price = m.group(1)
                    m = re.search(r'"currency-symbol":"(.+?)"', data, flags=re.S)
                    if m: unit = m.group(1)
                if self.item_price != '':
                    if price: i_price += '-' + price
                else:
                    if price: i_price = price
                    if unit: i_unit  = unit
        
        i = BagItem(self.brand_type)
        i.initItem(serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img, i_number)
        #print '# itemPage :', serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = ChanelBag()
    b_url = 'http://www.chanel.com/zh_CN/fashion/products/handbags.html'
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'chanel_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
