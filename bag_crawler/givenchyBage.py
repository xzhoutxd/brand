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

class GivenchyBag():
    '''A class of givenchy bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.givenchy.com'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'givenchy'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return
       
        tab_list = []
        m = re.search(r'<p>女装配饰</p>\s+<ul class="menu-level-4">(.+?)</ul>', page, flags=re.S)
        if m:
            tabs_list_info = m.group(1)

            p = re.compile(r'<li class="submenu-item">\s+<a.+?href="(.+?)">\s+<span lang="fr" class="lang-fr">(.+?)</span>(.+?)</a>\s+</li>', flags=re.S)
            for tab in p.finditer(tabs_list_info):
                tab_list.append((tab.group(2)+tab.group(3).strip(),tab.group(1)))

        for tab in tab_list:
            tab_name,tab_url = tab
            print '# tab:',tab_name,tab_url
            tab_page = self.crawler.getData(tab_url, url)

            m = re.search(r'<div id="layer-1".+?>\s+<a href="(.+?)" class="layer-links">.+?</a>', tab_page, flags=re.S)
            if m:
                ajax_url = self.home_url + m.group(1) + "?ajax=true&fragment=true"
                ajax_data = self.crawler.getData(ajax_url, tab_url)

                if ajax_data:
                    #data = json.loads(ajax_data)
                    #if data and data.has_key("html"):
                    #    print data["html"].decode("unicode-escape")
                    r_data = ajax_data.decode("unicode-escape")
                    if r_data:
                        m = re.search(r'"html":"(.+?)"}', r_data, flags=re.S)
                        if m:
                            data_html = m.group(1).replace("\/","/")
                            #print data_html
                            #break
                            p = re.compile(r'<li class="lookbook-item line" data-idlook="\d+">\s+<div class="disp-n">.+?<div class="look-info article">\s+<p>(.+?)</p>.+?<p class="look-ref">(.+?)</p>.+?</div>.+?</div>\s+<a href="(.+?)".+?>.+?<img .+?data-src="(.+?)".*?/>\s+</li>', flags=re.S)
                            for item in p.finditer(data_html):
                                i_url, i_img, s_number, i_name = self.home_url+item.group(3), item.group(4), item.group(2), re.sub(r'<.+?>','',item.group(1)).strip()
                                i_number = ''
                                m = re.search(r'<span class="look-ref-sku">\s*<span.+?>(.+?)</span>\s*</span>', s_number, flags=re.S)
                                if m:
                                    i_number = m.group(1)
                                print i_url, i_img, i_name, i_number
                                if Common.isBag(i_name):
                                    self.link_list.append((tab_name, tab_url, i_name, i_url, i_img, i_number))
                                    #i = BagItem(self.home_url, self.brand_type)
                                    #i.initItem(tab_name, '', i_name, '', '', '', i_url, i_img, i_number)
                                    #self.items.append(i.outItem())
                
    def bagItems(self):
        #for link in self.link_list: self.itemPage(link)
        max_th = 10
        if len(self.link_list) > max_th:
            m_itemsObj = BagItemM(self.home_url, self.brand_type, max_th)
        else:
            m_itemsObj = BagItemM(self.home_url, self.brand_type, len(self.link_list))
        m_itemsObj.createthread()
        m_itemsObj.putItems(self.link_list)
        m_itemsObj.run()
        self.items.extend(m_itemsObj.items)

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = GivenchyBag()
    b_url = 'http://www.givenchy.com/cn/'
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'givenchy_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
 
