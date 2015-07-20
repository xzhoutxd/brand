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

class DolcegabbanaBag():
    '''A class of dolcegabbana bag'''
    def __init__(self):
        # 抓取设置
        #self.crawler     = MyCrawler()
        self.crawler     = RetryCrawler()

        # 品牌官网链接
        self.home_url   = 'http://www.dolcegabbana.com.cn'
        self.price_url  = ''
        self.refers     = None

        # 品牌type
        self.brand_type = 'dolcegabbana'

        # 抓取商品列表
        self.link_list  = []
        self.items      = []
        
    def bagPage(self, url):
        page = self.crawler.getData(url, self.home_url)
        if not page or page == '': return

        serie_title = '包袋'
        p = re.compile(r'<li data-position="\d+\s*" class="product isAvailable".+?data-category="(.+?)".+?>\s*<div class="prodContent"><div class="imagesContainer".+?>.+?<img.+?data-original="(.+?)".+?>.+?</div>\s*<div class="\s*productDescription\s*">\s*<a href="(.+?)".+?><h2.+?>(.+?)</h2>\s*</a>\s*<div class="price">.+?<span class="currency">(.+?)</span>.*?<span class="priceValue">(.+?)</span>.+?</li>', flags=re.S)
        for item in p.finditer(page):
            tab_name, i_img, i_url, i_name, s_unit, s_price = item.group(1).strip(),item.group(2),item.group(3),item.group(4).strip(),item.group(5),item.group(6)
            i_unit = ""
            if s_unit.find("¥") != -1:
                i_unit = "CNY"
            i_price = re.sub(r'<.+?>','',s_price).strip()
            print tab_name, i_img, self.home_url+i_url, i_name, i_unit, i_price
            
            if i_url and i_url != '':
                self.link_list.append((serie_title,tab_name,url,i_name,self.home_url+i_url,i_img,i_price,i_unit))
            else:
                i = BagItem(self.brand_type)
                i.initItem(serie_title, tab_name, i_name, i_price, i_unit, '', i_url, i_img)
                self.items.append(i.outItem())
        page_num = 2
        ajax_url = "http://www.dolcegabbana.com.cn/yeti/api/DOLCEEGABBANA_CN/searchIndented.json?page=2&sortRule=PriorityDescending&format=full&authorlocalized=&macro=1147&micro=&color=&look=&size=&gender=D&season=P%2CE&department=&brand=&heel=&heeltype=&wedge=&washtype=&washcode=&colortype=&fabric=&waist=&family=&structure=&environment=&author=&textSearch=&minPrice=&maxPrice=&occasion=&salesline=&prints=&stone=&material=&agerange=&productsPerPage=20&gallery=&macroMarchio=&modelnames=&GroupBy=&style=&site=DOLCEEGABBANA&baseurl=http://www.dolcegabbana.com.cn/searchresult.asp"
        a_url = re.sub('page=\d+&', 'page=%d&'%page_num, ajax_url)
        a_page = self.crawler.getData(a_url, url)
        result = self.ajax_item(a_page, url)
        while result: 
            page_num += 1
            a_url = re.sub('page=\d+&', 'page=%d&'%page_num, ajax_url)
            a_page = self.crawler.getData(a_url, url)
            result = self.ajax_item(a_page, url)

    def ajax_item(self, page, refers):
        if not page or page == '': return False
        try:
            result = json.loads(page)
            if result.has_key("ApiResult"):
                r_ApiResult = result["ApiResult"]
                if r_ApiResult.has_key("Items"):
                    for item in r_ApiResult["Items"]:
                        tab_name, i_img, i_url, i_name, i_price = "", "", "", "", ""
                        if item.has_key("MicroCategory"):
                            tab_name = item["MicroCategory"].strip()
                        if item.has_key("DefaultCode10"):
                            item_code10 = item["DefaultCode10"]
                            if item.has_key("ImageTypes"):
                                if "12_f" in item["ImageTypes"]:
                                    i_img = "http://cdn.yoox.biz/55/%s_%s.jpg"%(item_code10,"12_f")
                                else:
                                    i_img = "http://cdn.yoox.biz/55/%s_%s.jpg"%(item_code10,max(item["ImageTypes"]))
                        if item.has_key("SingleSelectLink"):
                            i_url = self.home_url + item["SingleSelectLink"].strip()
                        if item.has_key("TitleAttribute"):
                            i_name = item["TitleAttribute"].strip()
                        if item.has_key("FullPrice"):
                            i_price = '{0:,}'.format(int(item["FullPrice"]))
                        i_unit = "CNY"
                        print tab_name,i_name,i_url,i_img,i_price,i_unit
                        if i_url and i_url != '':
                            self.link_list.append((tab_name,refers,i_name,i_url,i_img,i_price,i_unit))
                        else:
                            i = BagItem(self.brand_type)
                            i.initItem('', tab_name, i_name, i_price, i_unit, '', i_url, i_img)
                            self.items.append(i.outItem())
            if result.has_key("Page"):
                r_Page = result["Page"]
                if r_Page.has_key("CurrentSearchPage") and r_Page.has_key("TotalPages"):
                    if int(r_Page["CurrentSearchPage"]) < int(r_Page["TotalPages"]):
                        return True
            return False
        except Exception as e:
            print e
            return False

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
        item_title, refers, i_name, i_url, i_img, i_price, i_unit = val
        if i_url == '': return
        page = self.crawler.getData(i_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<div id="itemTechSheet">\s*<h1>(.+?)</h1>', page, flags=re.S)
        if m:
            i_name = m.group(1).strip()

        m = re.search(r'<div id="itemTechSheet">.+?<div class="price">(.+?)</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            if s_price.find("¥") != -1:
                i_unit = "CNY"
            i_price = re.sub(r'<.+?>','',s_price).replace('¥','').strip()
            
        m = re.search(r'<div id="itemImagesBox".*?>\s*<img.+?class="mainImage" src="(.+?)">', page, flags=re.S)
        if m:
            i_img = m.group(1)

        i_size = ''
        m = re.search(r'<div class="scrollCnt">\s*<ul>.+?<li>(尺寸.+?)</li>', page, flags=re.S)
        if m:
            i_size = m.group(1)
        else:
            m = re.search(r'<div class="scrollCnt">\s*<ul>.+?<li>(尺码.+?)</li>', page, flags=re.S)
            if m:
                i_size = m.group(1)

        i_number = ''
        m = re.search(r'<div id="itemTechSheet">.+?<p class="prodCode">(.+?)</p>', page, flags=re.S)
        if m:
            i_number = m.group(1).split('：')[1].strip()

        i = BagItem(self.brand_type)
        i.initItem('', item_title, i_name, i_price, i_unit, i_size, i_url, i_img, i_number)
        print '# itemPage:',i.outItem()
        #self.items.append(i.outItem()) 

    def outItems(self, f):
        s = '#系列名称|商品标签|商品名称|商品价格|金额单位|商品尺寸|商品链接|商品图片|商品编号'
        with open(f, 'w') as f_item:
            self.items.insert(0, s)
            f_item.write('\n'.join(self.items))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = DolcegabbanaBag()
    b_url = "http://www.dolcegabbana.com.cn/cn/dolce-gabbana/%E5%A5%B3%E5%A3%AB/onlinestore/%E5%8C%85%E8%A2%8B"
    b.bagPage(b_url)
    b.bagItems()
    
    f = Config.dataPath + 'dolcegabbana_%s.txt' %Common.today_ss()
    b.outItems(f)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
