from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from GoOne.items import EventItem

class EventfulSpider(CrawlSpider):

	name = 'CityEvents'
	allowed_domains = ["eventful.com"]
	
	rules = (
		# Extract the events but deny the categories links for scrapping the events
		Rule(SgmlLinkExtractor(allow=('/events/', ),deny=('/categories')), callback='parse_event'),
   	)		

	def __init__(self,city_ids):
		super(EventfulSpider,self).__init__()
		urlformat = "http://eventful.com/v2/tools/events/faceted_search?type=synch&location_type=city_id&location_id=%s" \
			    "&return_facets=1&when=future&page_number=1&sort=date&page_size=100&worldwide=0"
		self.start_urls = [ urlformat % city_id for city_id in open(city_ids)]


	def parse_event(self, response):
		self.log('This is a event page! %s' % response.url)
		hxs = HtmlXPathSelector(response)
		eventItem = EventItem()
                eventItem["name"] = (hxs.select('//*[@class="ellipsis"]/text()').extract())[0].strip()
                eventItem["date"] = (hxs.select('//*[@itemprop="startDate"]/text()').extract())[1].strip()
                eventItem["time"] = " ".join((hxs.select('//*[@itemprop="startDate"]/p/text()').extract())[0].split())
		eventItem["place"] = (hxs.select('//*[@itemprop="location"]/h6/a/text()').extract())[0].strip()
                eventItem["address"] = (hxs.select('//*[@itemprop="location"]/p/span[1]/text()').extract())[0].strip()+',' 
		eventItem["address"] +=	(hxs.select('//*[@itemprop="location"]/p/span[2]/text()').extract())[0].strip()+',' 
		eventItem["address"] += (hxs.select('//*[@itemprop="location"]/p/span[3]/text()').extract())[0].strip()
		eventItem["location"] = (hxs.select('//*[@itemprop="location"]/p/span[2]/text()').extract())[0].strip()
		return eventItem

