from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from GoOne.items import EventItem

class EventfulLasvegasSpider(CrawlSpider):

	name = 'Event'
	allowed_domains = ["eventful.com"]
	start_urls = [
		"http://eventful.com/lasvegas/events/categories?page_number=1"]
	rules = (
        		Rule(SgmlLinkExtractor(allow = ('/events/categories?page_number=2', )),callback='parse_event',follow=True),
		       # Rule(SgmlLinkExtractor(allow=('lasvegas_nv/events/*', )), callback='parse_event'),
   		 )		


	def parse_event(self, response):
		self.log('This is a event page! %s' % response.url)
		hxs = HtmlXPathSelector(response)
		eventItem = EventItem()
                eventItem["name"] = (hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[1]/h1/span[1]/text()').extract())[0].strip()
                eventItem["date"] = (hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[2]/div[2]/div[1]/text()').extract())[1].strip()
                eventItem["time"] = " ".join((hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[2]/div[2]/div[1]/p/text()').extract())[0].split())
		eventItem["place"] = (hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[2]/div[2]/div[2]/div/h6/a/text()').extract())[0].strip()
                eventItem["address"] = (hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[2]/div[2]/div[2]/div/p/span[1]/text()').extract())[0].strip() 
		eventItem["address"] +=	(hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[2]/div[2]/div[2]/div/p/span[2]/text()').extract())[0].strip()+',' 
		eventItem["address"] += (hxs.select('//*[@id="inner-container"]/div[1]/div[1]/div[2]/div[2]/div[2]/div/p/span[3]/text()').extract())[0].strip()
		return eventItem
