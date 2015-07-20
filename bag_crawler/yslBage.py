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

class YslBag():
    '''A class of ysl bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.ysl.com'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'ysl'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return

        tab_list = []
        m = re.search(r'<ul class="shopGender sep"><li class="shopWoman level1".+?>(.+?)</li><li class="shopMan level1"', page, flags=re.S)
        if m:
            tab_list_info = m.group(1)
            p = re.compile(r'<li data-dept=".+?".*?><a href="(.+?)">(.+?)</a>.*?</li>', flags=re.S)
            for tab_info in p.finditer(tab_list_info):
                tab_url, tab_name = tab_info.group(1), tab_info.group(2).strip()
                print tab_url, tab_name
                tab_list.append((tab_name, tab_url))
                if tab_name == '手提袋':
                    break


        #tab_list = [("手提袋","http://www.ysl.com/wy/shop-product/%E5%A5%B3%E5%A3%AB/%E6%89%8B%E6%8F%90%E8%A2%8B")]
        i = 0
        for tab in tab_list:
            refers = url
            tab_name, tab_url = tab
            print '# tab:',tab_name, tab_url
            tab_page = self.crawler.getData(tab_url, refers)
            self.parse_item(tab_page,tab_name,tab_url)
            m = re.search(r'<div class="pagnum".+?>(.+?)</div>', tab_page, flags=re.S)
            if m:
                pagelist_info = m.group(1)
                p = re.compile(r'<a href="(.+?)">\d+</a>', flags=re.S)
                page_list = []
                for page in p.finditer(pagelist_info):
                    page_info = self.crawler.getData(page.group(1), tab_url)
                    #print page.group(1)
                    self.parse_item(page_info,tab_name,tab_url)

    def parse_item(self, tab_page, tab_name, tab_url):
        items_info = ''
        m = re.search(r'<div id="productsContainer".+?>(.+?)</div>\s*</div>\s*</div>', tab_page, flags=re.S)
        if m:
            items_info = m.group(1)
            self.run_items(items_info, tab_name, tab_url)
        else:
            m = re.search(r'<div class="productsFromGrid.+?>(.+?)</div>\s*</div>\s*</div>\s*</div>', tab_page, flags=re.S)
            if m:
                items_info = m.group(1)
                self.run_items(items_info, tab_name, tab_url)
        
    def run_items(self, items_info, tab_name, tab_url):
        p = re.compile(r'<.+?>\s*<a.+?>\s*<img.+?src="(.+?)".*?>\s*</a><a href="(.+?)">.+?<div class="infoDescription">(.+?)</div>\s*(<div class="infoPrice">.+?</div>).+?</a>\s*<.+?>', flags=re.S)
        for item in p.finditer(items_info):
            i_img, i_url, s_name, price_info = item.group(1),item.group(2),item.group(3),item.group(4)
            i_name = re.sub(r'<.+?>','',s_name)
            i_price, i_unit = '', ''
            m = re.search(r'<div.+?class="newprice">(.+?)</div>', price_info, flags=re.S)
            if m:
                s_price = re.sub(r'<.+?>','',m.group(1))
                if s_price.find("¥") != -1:
                    i_unit = "CNY"
                i_price = s_price.replace('¥','').strip()
            
            if i_url and i_url != '':
                if Common.isBag(i_name) or Common.isBag(unquote(i_url)):
                    print self.home_url+i_url, i_img, i_name, i_price, i_unit
                    self.link_list.append((tab_name,tab_url,i_name,self.home_url+i_url,i_img,i_price,i_unit))
            else:
                if Common.isBag(i_name) or Common.isBag(unquote(i_url)):
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
            m_itemsObj = BagItemM(self.home_url, self.brand_type, max_th)
        else:
            m_itemsObj = BagItemM(self.home_url, self.brand_type, len(self.link_list))
        m_itemsObj.createthread()
        m_itemsObj.putItems(self.link_list)
        m_itemsObj.run()
        self.items.extend(m_itemsObj.items)

    def itemPage(self, val):
        serie_title, refers, i_name, i_url, i_img, i_price, i_unit = val
        if i_url == '': return
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return

        m = re.search(r'<div id="itemInfo">.+?<h1><span class="customItemDescription" itemprop="name">(.+?)</span></h1>', page, flags=re.S)
        if m:
            i_name = m.group(1).strip()

        m = re.search(r'<div id="itemPrice".+?><div.*?class="newprice">(.+?)</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            s_price = re.sub(r'<.+?>','',s_price)
            if s_price.find("¥") != -1:
                i_unit = "CNY"
                i_price = s_price.replace('¥','').strip()
            else:
                i_price = s_price
    
        m = re.search(r'<div id="mainImageContainer"><img.+?src="(.+?)".*?/></div>', page, flags=re.S)
        if m:
            i_img = m.group(1)

        i_size = ''
        m = re.search(r'<div class="itemDimensions">.+?<span class="dimensions">(.+?)</span></div>', page, flags=re.S)
        if m:
            i_size = m.group(1)

        i_number
        m = re.search(r'<div class="styleIdDescription">货号.+?<span.*?>(.+?)</span></div>', page, flags=re.S)
        if m:
            i_number = m.group(1)

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
    b = YslBag()
    b_url = "http://www.ysl.com/wy/shop-product/%E5%A5%B3%E5%A3%AB"
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'ysl_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
