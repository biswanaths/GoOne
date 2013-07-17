from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from GoOne.items import EventbriteItem
from GoOne.utils.unix_timestamp_convertor import TimestampUtil
from GoOne.utils.geocoding_coordinates_fetcher import GeoCodingUtil

class EventbriteSpider(CrawlSpider):

	name = 'Eventbrite'
	rules =	[
			Rule(SgmlLinkExtractor(allow=('/es2/', )), callback='parse_event'),
		 	Rule(SgmlLinkExtractor(allow=('(-es2.eventbrite.com)')), callback='parse_event'),
			Rule(SgmlLinkExtractor(allow=('(eventbrite.com\/directory)'), restrict_xpaths=('//*[@id="next"]')),follow=True,)
		]

	def __init__(self,city_ids):
		super(EventbriteSpider,self).__init__()
		urlformat = "http://www.eventbrite.com/directory?loc=%s&sort=date" 
		self.start_urls = [ urlformat % city_id for city_id in open(city_ids)]

	def parse_event(self, response):
		self.log('This is a event page! %s' % response.url)
		hxs = HtmlXPathSelector(response)
		eventbriteItem = EventbriteItem()
                try:
                	eventbriteItem["name"] = (hxs.select('//*[@id="event_header"]/h1/span/text()').extract())[0].strip()
		except Exception, ex:
                	eventbriteItem["name"] = (hxs.select('//*[@class="text-heading-epic"]/text()').extract())[0].strip()
                try:
			eventbriteItem["organizer"] = (hxs.select('//*[@id="event_header"]/h2[1]/a/text()').extract())[0].strip()
                except Exception, ex:
			eventbriteItem["organizer"] = (hxs.select('//*[@class="layout-stackable text-heading-secondary"]/text()').extract())[0].strip()
                try:
			eventbriteItem["place"] = (hxs.select('//*[@class="fn org"]/text()').extract())[0].strip()
		except Exception, ex:
                        eventbriteItem["place"] = ""
		eventbriteItem["address"] = ""
		try:
                	eventbriteItem["location"] = (hxs.select('//*[@id="event_network"]/h2/text()').extract())[0].strip().split(",")[0]  
		except Exception, ex:
                        return None

		try:
			eventbriteItem["address"] = (hxs.select('//*[@class="street-address"]/text()[1]').extract())[0].strip()+','
			eventbriteItem["address"] += (hxs.select('//*[@class="street-address"]/text()[2]').extract())[0].strip()+','
			eventbriteItem["address"] += eventbriteItem["location"] + ','
                	eventbriteItem["address"] += (hxs.select('//*[@class="region"]/text()').extract())[0].strip() 
                except Exception, ex:
                        pass

		return eventbriteItem	
