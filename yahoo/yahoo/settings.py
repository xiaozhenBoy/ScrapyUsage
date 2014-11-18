# -*- coding: utf-8 -*-

# Scrapy settings for yahoo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'yahoo'

SPIDER_MODULES = ['yahoo.spiders']
NEWSPIDER_MODULE = 'yahoo.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'yahoo (+http://www.yourdomain.com)'

ITEM_PIPELINES = {
	'yahoo.pipelines.yahooanswerPipeline':300
} #'yahoo.pipelines.yahooanswerPipeline':300 #'yahoo.pipelines.yahooDistributePipeline':300
# UserAgent, Http Proxy middleware
DOWNLOADER_MIDDLEWARES={
	'yahoo.middleware.proxyagentware.UserAgentMiddleWare':400,
} #'yahoo.middleware.proxyagentware.HttpProxyMiddleWare':401,
