#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")

import re
import time
import random
import Common
from base.MyCrawler import MyCrawler

class RetryCrawler():
    '''A class of retry crawl data'''
    def __init__(self):
        # 抓取设置
        self.crawler = MyCrawler()
        # wait time
        self.w_time = 1

    def getData(self, url, refers='', max_retry=20):
        page = ''
        retry = 1
        while True:
            try:
                page = self.crawler.getData(url, refers)
                break
            except Common.InvalidPageException as e:
                if retry >= max_retry:
                    break
                retry += 1
                print '# Invalid page exception:',e
                time.sleep(random.uniform(10,30))
            except Common.DenypageException as e:
                if retry >= max_retry:
                    break
                retry += 1
                print '# Deny page exception:',e
                time.sleep(random.uniform(10,30))
            except Common.SystemBusyException as e:
                if retry >= max_retry:
                    break
                retry += 1
                print '# System busy exception:',e
                time.sleep(random.uniform(10,30))
            except Exception as e:
                print '# exception err in retry crawler:',e
                if str(e).find('Read timed out') != -1:
                    if retry >= max_retry:
                        break
                    retry += 1
                elif str(e).find('Name or service not known') != -1 or str(e).find('Temporary failure in name resolution'):
                    if retry >= max_retry:
                        break
                    retry += 1
                    time.sleep(random.uniform(10,30))
                else:
                    break

        return page
