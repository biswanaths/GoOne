from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from GoOne.items import EventfulItem
from GoOne.utils.unix_timestamp_convertor import TimestampUtil
from GoOne.utils.geocoding_coordinates_fetcher import GeoCodingUtil

class EventfulSpider(CrawlSpider):

	name = 'Eventful'
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
		eventfulItem = EventfulItem()
                eventfulItem["name"] = (hxs.select('//*[@class="ellipsis"]/text()').extract())[0].strip()
		try:
			eventfulItem["performer"] = (hxs.select('//*[@itemprop="performer"]/a/text()').extract())[0].strip()
		except Exception, ex:
	    		eventfulItem["performer"] = ""
                eventfulItem["date"] = (hxs.select('//*[@itemprop="startDate"]/text()').extract())[1].strip()
                eventfulItem["time"] = " ".join((hxs.select('//*[@itemprop="startDate"]/p/text()').extract())[0].split())
		eventfulItem["place"] = (hxs.select('//*[@itemprop="location"]/h6/a/text()').extract())[0].strip()
                eventfulItem["address"] = (hxs.select('//*[@itemprop="location"]/p/span[1]/text()').extract())[0].strip()+',' 
		eventfulItem["address"] +=	(hxs.select('//*[@itemprop="location"]/p/span[2]/text()').extract())[0].strip()+',' 
		eventfulItem["address"] += (hxs.select('//*[@itemprop="location"]/p/span[3]/text()').extract())[0].strip()
		eventfulItem["location"] = (hxs.select('//*[@itemprop="location"]/p/span[2]/text()').extract())[0].strip()
		if eventfulItem["date"]:
			if " - " in eventfulItem["date"]:
				eventfulItem["date"] = eventfulItem["date"].split("-")[0]
			date = eventfulItem["date"].split(",")
			if eventfulItem["time"]:
				time = eventfulItem["time"].split()
				hour, min = TimestampUtil.get_time(time[1],time[2])
				eventfulItem["timestamp"] = TimestampUtil.get_unix_timestamp(int(date[1]),int(TimestampUtil.get_month(date[0].split()[0])),int(date[0].split()[1]),hour,min,0)
			else: 
				 eventfulItem["timestamp"] = TimestampUtil.get_unix_timestamp(int(date[1]),int(TimestampUtil.get_month(date[0].split()[0])),int(date[0].split()[1]),0,0,0)	
		if eventfulItem["timestamp"] and not TimestampUtil.is_within_range(eventfulItem["timestamp"]): return None
		lat,lng = GeoCodingUtil.get_latlng(eventfulItem["address"])
		if lat!=0 and lng!=0:
			eventfulItem["latitude"] = lat
			eventfulItem["longitude"] = lng
		return eventfulItem
	
