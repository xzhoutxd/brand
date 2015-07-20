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

class ArmaniBag():
    '''A class of armani bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.armani.cn'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'armani'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self):
        tab_list = [
                    ("giorgio armani","http://www.armani.cn/cn/giorgioarmani/%E5%A5%B3%E5%A3%AB/onlinestore/%E5%8C%85%E8%A2%8B"),
                    ("emporio armani","http://www.armani.cn/cn/emporioarmani/%E5%A5%B3%E5%A3%AB/onlinestore/%E5%8C%85%E8%A2%8B"),
                    ("armani jeans","http://www.armani.cn/cn/armanijeans/%E5%A5%B3%E5%A3%AB/onlinestore/%E5%8C%85%E8%A2%8B")]
        for tab in tab_list:
            tab_name,tab_data_url = tab
            print '# tab:',tab_name,tab_data_url
            tab_page = self.crawler.getData(tab_data_url, self.home_url)

            p = re.compile(r'<div class="item hproduct".+?>.+?<a href="(.+?)".+?class="url">\s*<div class="hproductPhotoCont">\s*<img.+?(src|data-original)="(.+?)".*?/>\s*</div>\s*</a>\s*<div class="itemDesc">\s*<a.+?>\s*<h3.+?>(.+?)</h3>\s*</a>.+?<div class="itemPrice">.+?<span class="prezzoProdottoSaldo".*?>(.+?)</span>\s*</div>.+?</div>', flags=re.S)
            for item in p.finditer(tab_page):
                i_url, i_img, i_name, s_price = self.home_url+item.group(1), item.group(2), item.group(4).strip(), item.group(5)
                print i_url, i_img, i_name, s_price
                i_unit = ""
                if s_price.find("¥") != -1:
                    i_unit = "CNY"
                i_price = s_price.replace('¥','').strip()
                if i_url and i_url != '':
                    self.link_list.append((tab_name,tab_data_url,i_name,i_url,i_img,i_price,i_unit))
                else:
                    i = BagItem(self.brand_type)
                    i.initItem(tab_name, '', i_name, i_price, i_unit, '', i_url, i_img)
                    self.items.append(i.outItem())
                
    def bagItems(self):
        #for link in self.link_list:
        #    self.itemPage(link)
        #    break
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
        
        m = re.search(r'<h2 class="productName">(.+?)</h2>', page, flags=re.S)
        if m:
            i_name = m.group(1).strip()

        m = re.search(r'<div id="zoomImageWrapper">\s*<img.+?src="(.+?)".*?/>\s*</div>', page, flags=re.S)
        if m:
            i_img = m.group(1)
        else:
            m = re.search(r'<div id="thumbsWrapper">.+?<div class="thumbElement".+?>\s*<img.+?src="(.+?)".*?/>\s*</div>', page, flags=re.S)
            if m:
                i_img = m.group(1)

        m = re.search(r'<span class="currency">(.+?)</span>.*?<span class="priceValue">(.+?)</span>', page, flags=re.S)
        if m:
            currency, i_price = m.group(1), re.sub(r'<.*>','',m.group(2))
            if currency.find("¥") != -1:
                i_unit = "CNY"
            else:
                i_unit = currency

        m = re.search(r'<div class="attributes">(.+?)</div>', page, flags=re.S)
        if m:
            size_str = re.sub(r'<.*?>','',m.group(1))
            #i_size = "".join(size_str.split())
            i_size = re.sub(r'\s*','',size_str)
            print "".join(i_size.split())

        i_number = ''
        m = re.search(r' <div class="modelFabricColorWrapper">\s*<div class="inner".*?>\s*<span class="modelTitle">.+?</span>.+?<span.*?class="value">(.+?)</span>\s*</div>\s*</div>\s*</div>', page, flags=re.S)
        if m:
            i_number = m.group(1)

        i = BagItem()
        i.initItem(serie_title, '', i_name, i_price, i_unit, i_size, i_url, i_img, i_number)
        self.items.append(i.outItem)    
        #print '# itemPage :', serie_title, i_name, i_price, i_unit, i_size, i_url, i_img

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = ArmaniBag()
    b.bagPage()
    b.bagItems()
    
    f = Config.dataPath + 'armani_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    
