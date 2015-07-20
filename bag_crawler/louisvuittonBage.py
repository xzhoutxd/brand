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

class LouisvuittonBag():
    '''A class of louisvuitton bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.louisvuitton.cn'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'louisvuitton'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return

        tab_list_info = ''
        m = re.search(r'<li class="mega-menu-item">\s*<div.+?data-megaMenu="women".*?>\s*<span class="onlyML">手袋</span>.+?</div>\s*<div class="mega-menu-content">.+?<ul class="level3">(.+?)</ul>', page, flags=re.S)
        if m:
            tab_list_info = m.group(1).strip()

        tab_list = []
        p = re.compile(r'<li class="mm-block">.+?<a.+?href="(.+?)">\s*<p class="mm-push-p">(.+?)</p>\s*</a>.+?</li>', flags=re.S)
        for tab_info in p.finditer(tab_list_info):
            tab_list.append((tab_info.group(2).strip(),self.home_url+tab_info.group(1)))
            print tab_info.group(2).strip(),self.home_url+tab_info.group(1)

        i = 0
        for tab in tab_list:
            refers = url
            tab_name, tab_url = tab
            print '# tab:',tab_name, tab_url
            tab_page = self.crawler.getData(tab_url, refers)
            m = re.search(r'<button.+?class="pl-next".+?data-next="(.+?)">',tab_page,flags=re.S)
            while m:
                refers = tab_url
                tab_url = re.sub(r'/to-\d+', '', tab_url)  + "/to-%s"%m.group(1)
                tab_page = self.crawler.getData(tab_url, refers)
                m = re.search(r'<button.+?class="pl-next".+?data-next="(.+?)">',tab_page,flags=re.S)

            p = re.compile(r'<a id="sku_.*?" href="(.+?)".+?>.+?<div class="description">\s*<div class="productName toMinimize">(.+?)</div>\s*<div class="productPrice.+?data-htmlContent="(.+?)">\s*</div>\s*</div>', flags=re.S)
            for item in p.finditer(tab_page):
                i_url, i_name, s_price = item.group(1),item.group(2),item.group(3)
                print self.home_url+i_url, i_name, s_price
                i_unit = ""
                if s_price.find("¥") != -1:
                    i_unit = "CNY"
                i_price = s_price.replace('¥','').strip()
                
                if i_url and i_url != '':
                    if Common.isBag(i_name):
                        self.link_list.append((tab_name,tab_url,i_name,self.home_url+i_url,i_price,i_unit))
                else:
                    if Common.isBag(i_name):
                        i = BagItem(self.brand_type)
                        i.initItem(tab_name, '', i_name, i_price, i_unit, '', i_url, '')
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
        serie_title, refers, i_name, i_url, i_price, i_unit = val
        if i_url == '': return
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<div class="productName title" id="productName">\s*<h1 itemprop="name">(.+?)</h1>\s*</div>', page, flags=re.S)
        if m:
            i_name = m.group(1).strip()

        m = re.search(r'<table class="priceButton">\s*<tr>\s*<td class="priceValue price-sheet">(.+?)</td>', page, flags=re.S)
        if m:
            i_price = m.group(1).strip()
            if i_price.find("¥") != -1:
                i_unit = "CNY"
    
        m = re.search(r'<noscript>\s*<img src="(.+?)".+?itemprop="image".*?/>\s*</noscript', page, flags=re.S)
        if m:
            i_img = m.group(1)

        i_size = ''
        m = re.search(r'<div class="textClientInfo exp_content".*?>\s*<div class="innerContent functional-text">(.+?)</div>', page, flags=re.S)
        if m:
            s_content = m.group(1).replace('&nbsp;','').strip()
            if s_content.find('宽)') != -1:
                s_size = s_content.split('宽)')[0]
                self.item_size = re.sub('<.+?>','',s_size) + "宽)"
            elif s_content.find('高)') != -1:
                s_size = s_content.split('高)')[0]
                self.item_size = re.sub('<.+?>','',s_size) + "高)"
            else:
                s_size = ''.join(s_content.split())

        i_number
        m = re.search(r'<h2 class="sku reading-and-link-text">(.+?)</h2>', page, flags=re.S)
        if m:
            i_number = m.group(1).strip()
        else:
            m = re.search(r'<meta itemprop="identifier" content="sku:(.+?)"/>', page, flags=re.S)
            if m:
                i_number = m.group(1).strip()

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
    b = LouisvuittonBag()
    b_url = "http://www.louisvuitton.cn/zhs-cn/homepage"
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'louisvuitton_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
