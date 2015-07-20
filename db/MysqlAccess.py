#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(r'../')
import base.Common as Common
import traceback
import MysqlPool

class MysqlAccess():
    '''A class of mysql db access'''
    def __init__(self):
        self.brand_db = MysqlPool.g_brandDbPool

    def __del__(self):
        self.brand_db = None

    def insert_item(self, args):
        try:
            sql = 'replace into nd_brand_parser_item(crawl_time,brand_name,serie_title,item_type,item_name,item_price,item_unit,item_size,item_url,item_img_url,item_number,c_begindate,c_beginhour) values(%s)' % Common.aggregate(13)
            self.brand_db.execute(sql, args)
        except Exception, e:
            print '# insert brand item exception:', e

if __name__ == '__main__':
    my = MysqlAccess()
