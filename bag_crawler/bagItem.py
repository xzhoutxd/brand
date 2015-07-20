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
from base.MyCrawler import MyCrawler

import warnings
warnings.filterwarnings("ignore")

class BagItem():
    '''A class of bag'''
    def __init__(self, home_url, brand_type):
        # 抓取设置
        self.crawler     = MyCrawler()

        self.crawling_time = Common.now() # 当前爬取时间
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_time)) # 本次爬取日期
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_time)) # 本次爬取小时

        # 品牌官网链接
        self.home_url    = home_url

        # 品牌type
        self.brand_type = brand_type

        self.serie_title = ''
        self.item_title  = ''
        self.item_name   = ''
        self.item_price  = ''
        self.item_unit   = ''
        self.item_size   = ''
        self.item_url    = ''
        self.item_img    = ''
        self.item_number = ''

    def initItem(self, serie_title, i_title, i_name, i_price, i_unit, i_size, i_url, i_img, i_number):
        self.serie_title = serie_title
        self.item_title  = i_title
        self.item_name   = i_name
        self.item_price  = i_price
        self.item_unit   = i_unit
        self.item_size   = i_size
        self.item_url    = i_url
        self.item_img    = i_img
        self.item_number = i_number

    def chanelItemPage(self, val):
        #self.price_url = 'http://ws.chanel.com/pricing/zh_CN/fashion/%s/?i_client_interface=fsh_v3_misc&i_locale=zh_CN&format=json&callback=localJsonpPricingCallback%s'
        self.price_url = 'http://ws.chanel.com/pricing/zh_CN/fashion/%s/?i_division=FSH&i_project=fsh_v3&i_client_interface=fsh_v3_misc&i_locale=zh_CN&format=json&callback=localJsonpPricingCallback&callback=localJsonpPricingCallback%s'
        self.serie_title, self.item_title, refers, self.item_name, self.item_url = val
        
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<div class="product-details details".*?>.+?<p class="description info.*?">(.+?)</p>', page, flags=re.S)
        if m: self.item_name = re.sub(r'<.+?>', '', m.group(1)).strip()
        else:
            m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
            if m: self.item_name = m.group(1).split('-')[0].strip()
        
        m = re.search(r'<div class="productimage.*?"><img src="(.+?)" alt=".+?"/>', page, flags=re.S)
        if m: self.item_img  = self.home_url + m.group(1)

        #m = re.search(r'<p class="size info">(.+?)</p>', page, flags=re.S)
        #if m: self.item_size = m.group(1)
        p = re.compile(r'<p class="size info">(.+?)</p>', flags=re.S)
        for size in p.finditer(page):
            if self.item_size != '': self.item_size += '-' + size.group(1)
            else: self.item_size = size.group(1)
                
        #m = re.search(r'<div class="ref info">\s*<p>(.+?)</p>', page, flags=re.S)
        #if m:
        #    self.item_number = m.group(1)
        p = re.compile(r'<div class="ref info">\s*<p>(.+?)</p>', flags=re.S)
        for number in p.finditer(page):
            item_number = number.group(1)
            if self.item_number != '':
                self.item_number += '-' + item_number
            else:
                self.item_number = item_number
            refs = item_number.split(' ')[:-1]
            ref_price = ''.join(refs)

            p_url = self.price_url % (ref_price, ref_price)
            data = self.crawler.getData(p_url, self.item_url)
            if not data or data == '': return
            
            # 抽取json报文
            r = re.search(r'\(\[(.+?)\]\)', data, flags=re.S)
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
                    if price: self.item_price += '-' + price
                else:
                    if price: self.item_price = price
                    if unit: self.item_unit  = unit
     

    def diorItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img = val
        
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<h2 class="" itemprop="name">(.+?)<br />(.+?)</h2>', page, flags=re.S)
        if m:
            self.item_title = m.group(1).strip()

        m = re.search(r'<li class="firstThumbnails">\s+<a href="#" class="active".+?>\s+<img src="(.+?)".*?/>', page, flags=re.S)
        if m: 
            self.item_img = self.home_url + m.group(1)

        m = re.search(r'<div class="modText">\s+<h4.+?>说明</h4>\s+<p>(.+?)</p>\s+</div>', page, flags=re.S)
        if m: 
            s_desc = m.group(1)
            m = re.search(r'尺寸：(.+?)<br />', s_desc, flags=re.S)
            if m:
                self.item_size = m.group(1).strip()
            else:
                m = re.search(r'尺寸：(.+?)$', s_desc, flags=re.S)
                if m: self.item_size = m.group(1).strip()

        m = re.search(r'<div class="columns-wrapper">.+?<div class="column">.+?<div class="reference">\s*<p>(.+?)</p>\s*</div>', page, flags=re.S)
        if m:
            s_number = m.group(1)
            self.item_number = s_number.split('-')[1].strip()

    def givenchyItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img, self.item_number  = val


    def armaniItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img, self.item_price, self.item_unit  = val
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return

        m = re.search(r'<h2 class="productName">(.+?)</h2>', page, flags=re.S)
        if m:
            self.item_name = m.group(1).strip()

        m = re.search(r'<div id="zoomImageWrapper">\s*<img.+?src="(.+?)".*?/>\s*</div>', page, flags=re.S)
        if m:
            self.item_img = m.group(1)
        else:
            m = re.search(r'<div id="thumbsWrapper">.+?<div class="thumbElement".+?>\s*<img.+?src="(.+?)".*?/>\s*</div>', page, flags=re.S)
            if m:
                self.item_img = m.group(1)

        m = re.search(r'<span class="currency">(.+?)</span>.*?<span class="priceValue">(.+?)</span>', page, flags=re.S)
        if m:
            currency, self.item_price = m.group(1), re.sub(r'<.*>','',m.group(2))
            if currency.find("¥") != -1:
                self.item_unit = "CNY"
            else:
                self.item_unit = currency

        m = re.search(r'<div class="attributes">(.+?)</div>', page, flags=re.S)
        if m:
            size_str = re.sub(r'<.*?>','',m.group(1))
            self.item_size = re.sub(r'\s+','',size_str)

        m = re.search(r'<h3 class="articleName"><span>.+?</span><span class="MFC">(.+?)</span></h3>', page, flags=re.S)
        if m:
            self.item_number = m.group(1)


    def bottegavenetaItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img = val

        # 先选国家
        refers_page = self.crawler.getData(refers,'')
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<h1 class="producTitle".+?>\s*<div class="modelName".+?>\s*<span class="modelName">(.+?)</span>', page, flags=re.S)
        if m:
            self.item_name = m.group(1).strip()

        m = re.search(r'<div class="mainImage".+?>\s*<img.+?src="(.+?)".*?/>\s*</div>', page, flags=re.S)
        if m:
            self.item_img = m.group(1)
        else:
            m = re.search(r'<section id="bgItem">\s*<img.+?src="(.+?)".*?/>\s*</section>', page, flags=re.S)
            if m:
                self.item_img = m.group(1)

        self.item_size = ''
        m = re.search(r'<div class="localizedAttributes">.*?<div class="height">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>', page, flags=re.S)
        if m:
            self.item_size += m.group(1) + ":" + m.group(2) + ";"
        m = re.search(r'<div class="localizedAttributes">.*?<div class="depth">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>', page, flags=re.S)
        if m:
            self.item_size += m.group(1) + ":" + m.group(2) + ";"
        m = re.search(r'<div class="localizedAttributes">.*?<div class="length_of_strap">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>', page, flags=re.S)
        if m:
            self.item_size += m.group(1) + ":" + m.group(2) + ";"
        m = re.search(r'<div class="localizedAttributes">.*?<div class="width">.+?<span class="text">(.+?)</span>\s*<span class="value">(.+?)</span>\s*</div>\s*</div>', page, flags=re.S)
        if m:
            self.item_size += m.group(1) + ":" + m.group(2) + ";"

        m = re.search(r' <div class="modelFabricColorWrapper">\s*<div class="inner".*?>\s*<span class="modelTitle">.+?</span>.+?<span.*?class="value">(.+?)</span>\s*</div>\s*</div>\s*</div>', page, flags=re.S)
        if m:
            self.item_number = m.group(1)

    def louisvuittonItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_price, self.item_unit = val 
    
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<div class="productName title" id="productName">\s*<h1 itemprop="name">(.+?)</h1>\s*</div>', page, flags=re.S)
        if m:
            self.item_name = m.group(1).strip()

        m = re.search(r'<table class="priceButton">\s*<tr>\s*<td class="priceValue price-sheet">(.+?)</td>', page, flags=re.S)
        if m:
            self.item_price = m.group(1).replace('¥','').strip()
            if self.item_price.find("¥") != -1:
                self.item_unit = "CNY"
    
        m = re.search(r'<noscript>\s*<img src="(.+?)".+?itemprop="image".*?/>\s*</noscript', page, flags=re.S)
        if m:
            s_img = re.sub(r'\s+','',m.group(1))
            self.item_img = s_img.replace('Frontview','Front%20view')

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

        m = re.search(r'<h2 class="sku reading-and-link-text">(.+?)</h2>', page, flags=re.S)
        if m:
            self.item_number = m.group(1).strip()
        else:
            m = re.search(r'<meta itemprop="identifier" content="sku:(.+?)"/>', page, flags=re.S)
            if m:
                self.item_number = m.group(1).strip()


    def dolcegabbanaItemPage(self, val):
        self.serie_title, self.item_title, refers, self.item_name, self.item_url, self.item_img, self.item_price, self.item_unit = val
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return
        
        m = re.search(r'<div id="itemTechSheet">\s*<h1>(.+?)</h1>', page, flags=re.S)
        if m:
            self.item_name = m.group(1).strip()

        m = re.search(r'<div id="itemTechSheet">.+?<div class="price">(.+?)</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            if s_price.find("¥") != -1:
                self.item_unit = "CNY"
            self.item_price = re.sub(r'<.+?>','',s_price).replace('¥','').strip()
            
        m = re.search(r'<div id="itemImagesBox".*?>\s*<img.+?class="mainImage" src="(.+?)">', page, flags=re.S)
        if m:
            self.item_img = m.group(1)

        m = re.search(r'<div class="scrollCnt">\s*<ul>.+?<li>(尺寸.+?)</li>', page, flags=re.S)
        if m:
            self.item_size = m.group(1)
        else:
            m = re.search(r'<div class="scrollCnt">\s*<ul>.+?<li>(尺码.+?)</li>', page, flags=re.S)
            if m:
                self.item_size = m.group(1)

        m = re.search(r'<div id="itemTechSheet">.+?<p class="prodCode">(.+?)</p>', page, flags=re.S)
        if m:
            self.item_number = m.group(1).split('：')[1].strip()


    def yslItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img, self.item_price, self.item_unit = val
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return

        m = re.search(r'<div id="itemInfo">.+?<h1><span class="customItemDescription" itemprop="name">(.+?)</span></h1>', page, flags=re.S)
        if m:
            self.item_name = m.group(1).strip()

        m = re.search(r'<div id="itemPrice".+?><div.*?class="newprice">(.+?)</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            s_price = re.sub(r'<.+?>','',s_price)
            if s_price.find("¥") != -1:
                self.item_unit = "CNY"
                self.item_price = s_price.replace('¥','').strip()
            else:
                self.item_price = s_price
    
        m = re.search(r'<div id="mainImageContainer"><img.+?src="(.+?)".*?/></div>', page, flags=re.S)
        if m:
            self.item_img = m.group(1)

        m = re.search(r'<div class="itemDimensions">.+?<span class="dimensions">(.+?)</span></div>', page, flags=re.S)
        if m:
            self.item_size = m.group(1)

        m = re.search(r'<div class="styleIdDescription">货号.+?<span.*?>(.+?)</span></div>', page, flags=re.S)
        if m:
            self.item_number = m.group(1)


    def bossItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img, self.item_price, self.item_unit = val
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return

        m = re.search(r'<h1 class="product-name">(.+?)</h1>', page, flags=re.S)
        if m:
            self.item_name = ' '.join(m.group(1).strip().split())

        m = re.search(r'<div class="product-prices">.+?<dd class="saleprice">(.+?)</dd>.+?</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            if s_price.find("¥") != -1 or s_price.find("￥") != -1:
                self.item_unit = "CNY"
            self.item_price = s_price.replace('¥','').replace('￥','').strip()
    
        m = re.search(r'<div class="image">.+?<div class="container".*?>\s*<table.+?>\s*<tr>\s*<td>\s*<a.+?>\s*<img.+?class="thumb".+?big="(.+?)".*?/>\s*</a>\s*</td>', page, flags=re.S)
        if m:
            self.item_img = m.group(1)

        m = re.search(r'<div class="tabpage inc".+?>.+?<span.*?>(尺寸大小.+?)</span>', page, flags=re.S)
        if m:
            s_size = m.group(1)
            self.item_size = s_size.split('：')[1]
        if self.item_size == '':
            m = re.search(r'<span.+?>尺寸大小：</span>(.+?)</span>', page, flags=re.S)
            if m:
                self.item_size = re.sub(r'<.+?>','',m.group(1))

        m = re.search(r'<div class="base">\s*<div class="sku-brand">.+?<dl class="hidden"><dt>商品货号: </dt><dd>(.+?)</dd></dl>\s*</div>', page, flags=re.S)
        if m:
            self.item_number = m.group(1)

    def ferragamoItemPage(self, val):
        self.serie_title, refers, self.item_name, self.item_url, self.item_img, self.item_price, self.item_unit = val
        if self.item_url == '': return
        page = self.crawler.getData(self.item_url, refers)
        if not page or page == '': return

        m = re.search(r'<div class="product-title">(.+?)</div>', page, flags=re.S)
        if m:
            self.item_name = ' '.join(m.group(1).strip().split())

        m = re.search(r'<div class="product-prices">(.+?)</div>', page, flags=re.S)
        if m:
            s_price = m.group(1).strip()
            if s_price.find("¥") != -1 or s_price.find("￥") != -1:
                self.item_unit = "CNY"
            self.item_price = s_price.replace('¥','').replace('￥','').strip()
    
        m = re.search(r'<div class="item-list">\s*<ul.+?>\s*<li class="first">.+?<img.+?src="(.+?)".*?/>', page, flags=re.S)
        if m:
            self.item_img = m.group(1)

        m = re.search(r'<div class="product-code">(.+?)型号代码(.+?)</div>', page, flags=re.S)
        if m:
            self.item_size, self.item_number = m.group(1).strip(), m.group(2).strip()

    def antPage(self, val):
        if self.brand_type == 'chanel':
            self.chanelItemPage(val)
        elif self.brand_type == 'dior':
            self.diorItemPage(val)
        elif self.brand_type == 'givenchy':
            self.givenchyItemPage(val)
        elif self.brand_type == 'armani':
            self.armaniItemPage(val)
        elif self.brand_type == 'bottegaveneta':
            self.bottegavenetaItemPage(val)
        elif self.brand_type == 'louisvuitton':
            self.louisvuittonItemPage(val)
        elif self.brand_type == 'dolcegabbana':
            self.dolcegabbanaItemPage(val)
        elif self.brand_type == 'ysl':
            self.yslItemPage(val)
        elif self.brand_type == 'boss':
            self.bossItemPage(val)
        elif self.brand_type == 'ferragamo':
            self.ferragamoItemPage(val)

    def outItem(self):
        s = '%s|%s|%s|%s|%s|%s|%s|%s|%s' %(self.serie_title, self.item_title, self.item_name, self.item_price, self.item_unit, self.item_size, self.item_url, self.item_img, self.item_number)
        return s

    def outTuple(self):
        return (Common.time_s(self.crawling_time), self.brand_type, self.serie_title, self.item_title, self.item_name, self.item_price, self.item_unit, self.item_size, self.item_url, self.item_img, self.item_number, self.crawling_beginDate, self.crawling_beginHour)

