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

class DiorBag():
    '''A class of dior bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.dior.cn'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'dior'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return
       
        tab_list = []
        m = re.search(r'<ul class="tabsList collections">(.+?)</ul>', page, flags=re.S)
        if m:
            tabs_list_info = m.group(1)

            p = re.compile(r'<li class=".+?">\s+<a href="(.+?)" data-magento_call_page="(.+?)".+?>(.+?)</a>\s+</li>', flags=re.S)
            for tab in p.finditer(tabs_list_info):
                tab_list.append((tab.group(3).strip(),self.home_url+tab.group(2),url+tab.group(1)))

        for tab in tab_list:
            tab_name,tab_data_url,tab_url = tab
            print '# tab:',tab_name,tab_data_url,tab_url
            tab_page = self.crawler.getData(tab_data_url, url)

            p = re.compile(r'<li class="li-product.+?>\s+<a href="(.*?)" class="linkProduct">.+?<img src="(.+?)".+?/>.+?<span class="description".+?>.+?<span class="title">(.+?)</span>.+?</span>\s+</a>\s+</li>', flags=re.S)
            for item in p.finditer(tab_page):
                i_url, i_img, i_name = self.home_url+item.group(1), self.home_url+item.group(2), item.group(3)
                print i_url, i_img, i_name
                if i_url and i_url != '':
                    self.link_list.append((tab_name,tab_url,i_name,i_url,i_img))
                else:
                    i = BagItem(self.brand_type)
                    i.initItem(tab_name, '', i_name, '', '', '', i_url, self.home_url+i_img)
                    self.items.append(i.outItem())
                
    def bagItems(self):
        #for link in self.link_list: self.itemPage(link)
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
        serie_title, refers, i_name, i_url = val
        
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return
        
        i_title, i_img, i_size, i_price, i_unit = '', '', '', '', ''
        
        m = re.search(r'<h2 class="" itemprop="name">(.+?)<br />(.+?)</h2>', page, flags=re.S)
        if m:
            i_title = m.group(1).strip()

        m = re.search(r'<li class="firstThumbnails">\s+<a href="#" class="active".+?>\s+<img src="(.+?)" alt="" />\s+</a>\s+</li>', page, flags=re.S)
        if m: i_img  = self.home_url + m.group(1)

        m = re.search(r'<div class="modText">\s+<h4.+?>说明</h4>\s+<p>(.+?)</p>\s+</div>', page, flags=re.S)
        if m: 
            i_desc = m.group(1)
            m = re.search(r'尺寸：(.+?)<br />', i_desc, flags=re.S)
            if m:
                i_size = m.group(1).strip()
            else:
                m = re.search(r'尺寸：(.+?)$', i_desc, flags=re.S)
                if m: i_size = m.group(1).strip()

        i_number = ''
        m = re.search(r'<div class="columns-wrapper">.+?<div class="column">.*?<div class="reference">\s*<p>(.+?)</p>\s*</div>', page, flags=re.S)
        if m:
            s_number = m.group(1)
            i_number = s_number.split('-')[1].strip()
                
        i = BagItem()
        i.initItem(serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img, i_number)
        self.items.append(i.outItem)    
        print '# itemPage :', serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = DiorBag()
    b_url = 'http://www.dior.cn/couture/zh_cn/%E5%A5%B3%E5%A3%AB%E6%97%B6%E8%A3%85/%E7%9A%AE%E5%85%B7'
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'dior_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
