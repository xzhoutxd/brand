#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(r'../')
import re
import json
import time
from urllib import unquote
import base.Common as Common
import base.Config as Config
#from base.MyCrawler import MyCrawler
from base.RetryCrawler import RetryCrawler
from bagItem import BagItem
from bagItemM import BagItemM

import warnings
warnings.filterwarnings("ignore")

class FerragamoBag():
    '''A class of ferragamo bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.ferragamo.cn'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'ferragamo'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return

        tab_name = '女士手袋'
        self.parse_item(page,tab_name,url)

    def parse_item(self, tab_page, tab_name, tab_url):
        m = re.search(r'<div class="view-content">.+?<div class="page-wrapper-product">(.+?)</script>\s*</div>\s*</div>', tab_page, flags=re.S)
        if m:
            items_info = m.group(1)
            self.run_items(items_info, tab_name, tab_url)
 
    def run_items(self, items_info, tab_name, tab_url):
        p = re.compile(r'<div class="large.+?columns.+?">\s*<a href="(.+?)">\s*<img.*?src="(.+?)".*?/><span class="prodcaption">(.+?)</br>(.+?)</span>\s*</a>', flags=re.S)
        for item in p.finditer(items_info):
            i_url, i_img, i_name, s_price = item.group(1),item.group(2),item.group(3),item.group(4)
            i_price, i_unit = '', ''
            if s_price.find("¥") != -1 or s_price.find("￥") != -1:
                i_unit = "CNY"
            i_price = s_price.replace('¥','').replace('￥','').strip()
            
            if i_url and i_url != '':
                print self.home_url+i_url, i_img, i_name, i_price, i_unit
                self.link_list.append((tab_name,tab_url,i_name,self.home_url+i_url,i_img,i_price,i_unit))
            else:
                print self.home_url+i_url, i_img, i_name, i_price, i_unit
                i = BagItem(self.brand_type)
                i.initItem(tab_name, '', i_name, i_price, i_unit, '', i_url, i_img)
                self.items.append(i.outItem())

    def bagItems(self):
        """
        i = 0
        for link in self.link_list:
            self.itemPage(link)
            i += 1
            if i == 1:
                break
        """
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
        serie_title, refers, i_name, i_url, i_img, i_price, i_unit = val
        if i_url == '': return
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return

        m = re.search(r'<div class="product-title">(.+?)</div>', page, flags=re.S)
        if m:
            i_name = ' '.join(m.group(1).strip().split())

        m = re.search(r'<div class="product-prices">(.+?)</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            if s_price.find("¥") != -1 or s_price.find("￥") != -1:
                i_unit = "CNY"
            i_price = s_price.replace('¥','').replace('￥','').strip()
    
        m = re.search(r'<div class="item-list">\s*<ul.+?>\s*<li class="first">.+?<img.+?src="(.+?)".*?/>', page, flags=re.S)
        if m:
            i_img = m.group(1)

        i_size = ''
        i_number = ''
        m = re.search(r'<div class="product-code">(.+?)型号代码(.+?)</div>', page, flags=re.S)
        if m:
            i_size, i_number = m.group(1).strip(), m.group(2).strip()

        i = BagItem(self.brand_type)
        i.initItem(serie_title, '', i_name, i_price, i_unit, i_size, i_url, i_img, i_number)
        print '# itemPage:',i.outItem()
        #self.items.append(i.outItem()) 

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = FerragamoBag()
    b_url = "http://www.ferragamo.cn/woman/handbags/"
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'ferragamo_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
