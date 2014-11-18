# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YahooItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
#Item for yahoo answer:
#	Question:
#		subject, question subject
#		pubtime, publish time
#		postuser, user_id who post the question
#	Answer:
#	User:
class Question(scrapy.Item):
    subject = scrapy.Field()
    pubtime = scrapy.Field()
    answercount = scrapy.Field()
    postuser = scrapy.Field()
    qid = scrapy.Field()
# answer
class Answer(scrapy.Item):
    qid = scrapy.Field()
    content = scrapy.Field()
    answeruser = scrapy.Field()
    supportnum = scrapy.Field()
    opposenum = scrapy.Field()
    answertime = scrapy.Field()


