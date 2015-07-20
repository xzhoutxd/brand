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

class BottegavenetaBag():
    '''A class of bottegaveneta bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.bottegaveneta.com'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'bottegaveneta'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return

        p = re.compile(r'<div id="slot_\d+".+?<a.+?href="(.+?)".+?>\s*<img.+?src="(.+?)".+?/>\s*<div class="iteminfo">\s*<div class="headgroup">\s*<div class="extra">\s*<h1 class="modelname">(.+?)</h1>', flags=re.S)
        for item in p.finditer(page):
            i_url, i_img, i_name = item.group(1),item.group(2),item.group(3)
            print i_url, i_img, i_name
            if i_url and i_url != '':
                self.link_list.append(('',url,i_name,i_url,i_img))
            else:
                i = BagItem(self.brand_type)
                i.initItem('',url,i_name,i_url,i_img)
                self.items.append(i.outItem())

        p = re.compile(r'<div class="slot lazySlot".+?data-slot="(.+?)".+?>',flags=re.S)
        for item in p.finditer(page):
            data_info = item.group(1)
            data_info_str = data_info.replace('&quot;','"')
            i_url, i_img, i_name = '', '', ''
            m = re.search(r'"Link":"(.+?)"', data_info_str, flags=re.S)
            if m:
                i_url = m.group(1)

            m = re.search(r'"ModelName":"(.+?)",', data_info_str, flags=re.S)
            if m:
                i_name = m.group(1)

            print i_url, i_img, i_name
            if i_url and i_url != '':
                self.link_list.append(('',url,i_name,i_url,i_img))
            else:
                i = BagItem(self.brand_type)
                i.initItem('',url,i_name,i_url,i_img)
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
        serie_title, refers, i_name, i_url, i_img = val
        if i_url == '': return
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<h1 class="producTitle".+?>\s*<div class="modelName".+?>\s*<span class="modelName">(.+?)</span>', page, flags=re.S)
        if m:
            i_name = m.group(1).strip()

        m = re.search(r'<div class="mainImage".+?>\s*<img.+?src="(.+?)".*?/>\s*</div>', page, flags=re.S)
        if m:
            i_img = m.group(1)
        else:
            m = re.search(r'<section id="bgItem">\s*<img.+?src="(.+?)".*?/>\s*</section>', page, flags=re.S)
            if m:
                i_img = m.group(1)
        
        i_size = ''
        m = re.search(r'<div class="localizedAttributes">.*?<div class="height">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>', page, flags=re.S)
        if m:
            i_size += m.group(1) + ":" + m.group(2) + ";"
        m = re.search(r'<div class="localizedAttributes">.*?<div class="depth">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>', page, flags=re.S)
        if m:
            i_size += m.group(1) + ":" + m.group(2) + ";"
        m = re.search(r'<div class="localizedAttributes">.*?<div class="length_of_strap">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>', page, flags=re.S)
        if m:
            i_size += m.group(1) + ":" + m.group(2) + ";"
        m = re.search(r'<div class="localizedAttributes">.*?<div class="width">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>\s*</div>', page, flags=re.S)
        if m:
            i_size += m.group(1) + ":" + m.group(2) + ";"

        i_number
        m = re.search(r' <div class="modelFabricColorWrapper">\s*<div class="inner".*?>\s*<span class="modelTitle">.+?</span>.+?<span.*?class="value">(.+?)</span>\s*</div>\s*</div>\s*</div>', page, flags=re.S)
        if m:
            i_number = m.group(1)

        i = BagItem(self.brand_type)
        i.initItem(serie_title, '', i_name, '', '', i_size, i_url, i_img, i_number)
        print '# itemPage:',i.outItem()
        #self.items.append(i.outItem())    
        #print '# itemPage :', serie_title, i_name, i_url, i_img, i_size

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = BottegavenetaBag()
    b_url = "http://www.bottegaveneta.com/wy/%E5%A5%B3%E5%A3%AB/onlineboutique/%E6%89%8B%E8%A2%8B"
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'bottegaveneta_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
