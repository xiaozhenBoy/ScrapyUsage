# -*- coding: utf-8 -*-
# middleware for crawler
# Proxy and Agent are two method for avoding sites banning.
# here implementation of Proxy and Agent

from useragents import * # agent alternatives
import random
from scrapy import log
from httpproxy import *
# generating a UserAgent randomly from candidate list.
class UserAgentMiddleWare(object):
    def process_request(self, request, spider):
        agent = random.choice(USER_AGENTS)
        request.headers['User-Agent'] = agent
# set proxy
class HttpProxyMiddleWare(object):
    def process_request(self, request, spider):
        if self.user_proxy(request):
            new_proxy = random.choice(HTTP_PROXIES)
            try:
                request.meta['proxy'] = "http://%s" % new_proxy['ip_port']
            except Exception, e:
                log.msg('Exception: %s' % e, _level=log.CRITICAL)
    def user_proxy(self, request):
        if "depth" in request.meta and int(request.meta["depth"]) <= 2:
            return False
        i = random.randint(1, 10)
        return i <= 2
