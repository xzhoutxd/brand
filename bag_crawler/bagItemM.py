#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(r'../')
import time
import random
import traceback
import threading
import base.Config as Config
import base.Common as Common
from db.MysqlAccess import MysqlAccess
from base.MyThread  import MyThread
from Queue import Empty
from bagItem import BagItem

import warnings
warnings.filterwarnings("ignore")

class BagItemM(MyThread):
    '''A class of jhs item thread manager'''
    def __init__(self, home_url, brand_type, thread_num=10):
        # parent construct
        MyThread.__init__(self, thread_num)

        # db
        self.mysqlAccess  = MysqlAccess() # mysql access

        # thread lock
        self.mutex        = threading.Lock()

        self.home_url     = home_url

        self.brand_type   = brand_type

        # activity items
        self.items        = []

        # give up item, retry too many times
        self.giveup_items = []

    def push_back(self, L, v):
        if self.mutex.acquire(1):
            L.append(v)
            self.mutex.release()

    def putItem(self, _item):
        self.put_q((0, _item))

    def putItems(self, _items):
        for _item in _items: self.put_q((0, _item))

    # To crawl retry
    def crawlRetry(self, _data):
        if not _data: return
        _retry, _val = _data
        _retry += 1
        if _retry < Config.crawl_retry:
            _data = (_retry, _val)
            self.put_q(_data)
        else:
            self.push_back(self.giveup_items, _val)
            print "# retry too many times, no get item:", _val

    # To crawl item
    def crawl(self):
        while True:
            _data = None
            try:
                try:
                    # 取队列消息
                    _data = self.get_q()
                except Empty as e:
                    # 队列为空，退出
                    #print '# queue is empty', e
                    break

                _val = _data[1]
                item = BagItem(self.home_url, self.brand_type)
                item.antPage(_val)
                self.push_back(self.items, item.outItem())

                sql = item.outTuple()
                self.mysqlAccess.insert_item(sql)

                # 延时
                time.sleep(0.1)
                # 通知queue, task结束
                self.queue.task_done()

            except Exception as e:
                print 'Unknown exception crawl item :', e
                Common.traceback_log()
                self.crawlRetry(_data)
                # 通知queue, task结束
                self.queue.task_done()
                time.sleep(5)

if __name__ == '__main__':
    pass

