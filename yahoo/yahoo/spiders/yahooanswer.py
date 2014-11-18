# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from yahoo.items import Question, Answer
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle

BASE_URL = u'https://answers.yahoo.com/xhr-q-otherAnswers.php?qid=%s&qs=OPEN&la=en-US&lo=0&tvc=0&icba=&myQ=0&canCba=0&iqlock=0&canAnswer=0&visitorImageUrl=&tac=%d&haveAnswerQuota=0&isNewUser=0&isShowMoreLinkShown=%d&page=%d&sort=1&vs=%d&prevOac=%d' # for other answer 
REFER_BASE = 'https://answers.yahoo.com/question/index?qid=%s'

class YahooanswerSpider(CrawlSpider):
    name = "yahooanswer"
    allowed_domains = ["yahoo.com"]
    start_urls = [
    ] #20141112060200AAap18o 20141014071709AAUHDS6 # 'https://answers.yahoo.com/dir/index?sid=396545012'
    # Link Extractor Rules
    rules = [
          
    ]
    #Rule(sle(allow=("/question/index\?qid=[a-zA-Z0-9]{6,}$")), follow=True, callback='parse_1'),
    #Rule(sle(allow=("/question/index\?qid=[a-zA-Z0-9]{6,}$")), follow=True, callback='parse_1'),
    #Rule(sle(allow=("/xhr-q-otherAnswers.php\?qid=[a-zA-Z0-9]{6,}.*")), callback='parse_1'),   
    #Rule(sle(allow=("/xhr-q-otherAnswers.php\?qid=[a-zA-Z0-9]{6,}.*")), callback='parse_1')
    #Rule(sle(allow=("/dir/index\?sid=\d{,9}$")), follow=False, callback='parse_2'),
    # handle show more links
    showlinks = {}
    def __init__(self, *a, **kw):
        super(YahooanswerSpider, self).__init__(*a, **kw)
        # load seed file, initialize start_urls
        f = open('seed.cfg', 'r')
        lines = f.readlines()
        f.close()
        self.start_urls.extend([l.strip() for l in lines])
    # parse
    # parser for category page
    def parse_2(self, response):
        print 'category:', str(response.url)
        #return response.url 
    # parser for question-answer thread page
    def parse_1(self, response):
        current_url = response.url.split('&')[0]
        qid = current_url[current_url.find(u'qid=')+len(u'qid='):]
        question = self.parseQuestion(response, qid)
        yield question
        ba = self.parseBestAnswer(response, qid)
        yield ba
        answers = self.parseAnswers(response, qid)
        for answer in answers:
            yield answer
        # handle answer_number > 30, in yahoo answer, if answer number is bigger than 30, it will be cut to sevaral page. 
        # here make new request for extend answer pages.
        if not question['subject']:
            answer_number = 0
        else:
            answer_number = int(question['answercount'].encode('utf-8'))
        reqs = self.getMultiPage(answer_number, response) 
        for req in reqs:
            yield req
        pass
    def getMultiPage(self, answer_number, response):
        param_list = response.url.split('&')
        qid = param_list[0].split('=')[1]
        if response.url.find('xhr-q-otherAnswers.php') == -1:
            pnum = int(round(float(answer_number)/30.0))
            for p in xrange(2, pnum+1):
                new_url = BASE_URL % (qid, answer_number, 0, p, int(p*1000), int(30*(p-1)))
                new_request = self.make_requests_from_url(new_url)
                yield new_request
        else:
            tac = int(param_list[11].split('=')[1])
            showmorelink = int(param_list[-5].split('=')[1])
            page = int(param_list[-4].split('=')[1])
            vs = int(param_list[-2].split('=')[1])
            prevOac = int(param_list[-1].split('=')[1])
            pnum = int(round(float(tac)/30.0))
            # check show more link 
            if tac > page * 30:
                if self.hasShowmoreLink(response):
                    prevOac = 0
                    if qid in self.showlinks:
                        showmorelink = 1 #self.showlinks[qid] + 1
                    self.showlinks[qid] = showmorelink
                    for p in xrange(page+1, pnum):
                        new_url = BASE_URL % (qid, tac, showmorelink, p, vs+1000, prevOac+30)
                        new_request = self.make_requests_from_url(new_url)
                        yield new_request                    
            else:
                if qid in self.showlinks:
                    del self.showlinks[qid]            
    def make_requests_from_url(self, url):
        # make cookies for request
        if url.find('xhr-q-otherAnswers.php') == -1:
            return Request(url=url, callback=self.parse_1) #, callback=self.parse_1
        temp_header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Encoding': 'gzip,deflate',
                       'Accept-Language': 'en',
                       'User-Agent': 'Scrapy/0.24.4 (+http://scrapy.org)',
                      }
        # get qid, constructure Referer
        temp_url = url.split('&')[0]
        qid = temp_url[temp_url.find(u'qid=')+len(u'qid='):]
        ref_url = REFER_BASE % (qid)
        temp_header['Referer'] = ref_url
        return Request(url=url, headers=temp_header, dont_filter=True, callback=self.parse_1) #, callback=self.parse_2
    def parseQuestion(self, response, qid):
        # get question info from response
        question = Question()
        yan_question = response.xpath("//div[@id='yan-question']")
        qa_container = yan_question.xpath("div[@class='qa-container']")
        # question post user profile
        temp_list = yan_question.xpath("div[@class='profile']/attribute::id").extract()
        question['postuser'] = ''.join(temp_list)
        # question info, including subject, post time, answer count
        temp_list = qa_container.xpath("div[@class='q-title mb10']/h1/text()").extract()
        question['subject'] = ' '.join(temp_list)
        temp_list = qa_container.xpath("time/attribute::datetime").extract()
        question['pubtime'] = ' '.join(temp_list)
        temp_list = qa_container.xpath("meta/attribute::content").extract()
        question['answercount'] = ' '.join(temp_list)
        question['qid'] = qid
        return question
    def parseAnswers(self, response, qid):
        # get other answers except best answer
        if response.url.find(u'xhr-q-otherAnswers.php') == -1:
            sels = response.xpath("//div[@id='ya-oac']/div[@id='ya-oa']/ul/li")
        else:
            sels = response.xpath("//ul[@class='shown']/li")
        for sel in sels:
            answer = Answer()
            answersel = sel.xpath("div[@class='answer']")
            # get answer user
            temp_list = answersel.xpath("div[@class='profile']/attribute::id").extract()
            if not temp_list:
                answer['answeruser'] = 'anonymous'
            else:
                answer['answeruser'] = ' '.join(temp_list)
            # get answer info, including answer content, support number, oppose number
            qa_container = answersel.xpath("div[@class='qa-container']/div[@class='ya-oa-cont']")
            temp_list = qa_container.xpath("div/text() | div/br").extract()
            answer['content'] = ' '.join(temp_list)
            temp_list = qa_container.xpath("ul/li[@id='unlock']/div[@id='tup']/attribute::count").extract()
            answer['supportnum'] = ' '.join(temp_list)
            temp_list = qa_container.xpath("ul/li[@id='unlock']/div[@id='tdn']/attribute::count").extract()
            answer['opposenum'] = ' '.join(temp_list)
            answer['qid'] = qid
            yield answer
    def parseBestAnswer(self, response, qid):
        # get best answer info in current thread
        # Exception: some threads have no best answer
        ba_list = response.xpath("//div[@id='ya-ba']")
        if not ba_list:
            return None
        ba = ba_list[0]
        # get answer detail
        answer = Answer()
        temp_list = ba.xpath("div[@class='profile pl14']/attribute::id").extract()
        if not temp_list:
            answer['answeruser'] = 'anonymous'
        else:
            answer['answeruser'] = ' '.join(temp_list)
        yaba_cont = ba.xpath("div[@class='qa-container pr14 pl14']/div[@id='ya-ba-cont']")
        temp_list = yaba_cont.xpath("div/text() | div/br").extract()
        answer['content'] = ' '.join(temp_list)
        temp_list = yaba_cont.xpath("ul/li[@id='unlock']/div[@id='tup']/attribute::count").extract()
        answer['supportnum'] = ' '.join(temp_list)
        temp_list = yaba_cont.xpath("ul/li[@id='unlock']/div[@id='tdn']/attribute::count").extract()
        answer['opposenum'] = ' '.join(temp_list)
        answer['qid'] = qid
        return answer
    def hasShowmoreLink(self, response):
        temp_list = response.xpath("//div[@id='more-answers']").extract()
        print temp_list
        if len(temp_list) == 0:
            return False
        else:
            return True
