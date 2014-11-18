# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import os

BASE_FOLD = 'data'
class YahooPipeline(object):
    def process_item(self, item, spider):
        return item

class yahooanswerPipeline(object):
    def __init__(self):
        self.file = codecs.open('yahooanswer_data.json', mode='w', encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item
    def close_spider(self, spider):
        # close file
        self.file.close()
class yahooDistributePipeline(object):
    def __init__(self):
        pass
    def process_item(self, item, spider):
        #
        path = os.path.join(BASE_FOLD, item['qid']+'.txt')
        f = codecs.open(path, mode='a+', encoding='utf-8')
        del item['qid']
        f.write(json.dumps(dict(item), ensure_ascii=False) + '\n')
        f.close()
        return item
    def close_spider(self, spider):
        print 'All Files closed!'
