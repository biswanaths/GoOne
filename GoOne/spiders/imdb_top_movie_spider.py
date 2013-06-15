from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from GoOne.items import MovieItem

class ImdbTopMovieSpider(CrawlSpider):

	name = 'ImdbTop250'
	allowed_domains = ["imdb.com"]
	start_urls = [
		"http://www.imdb.com/chart/top"]
		
	rules = (
		# Extract links matching for individual movie and parse them with the spider's method parse_movie
		Rule(SgmlLinkExtractor(allow=('title/tt.*/', )),callback='parse_movie'),
	)

	def parse_movie(self, response):
		self.log('This is a movie page! %s' % response.url)
		hxs = HtmlXPathSelector(response)
		movieItem = MovieItem()		
		movieItem["title"] = (hxs.select("//div[@id='title-overview-widget']/table/tbody/tr/td[@id='overview-top']/h1/span[1]/text()").extract())[0]
		movieItem["rating"] = (hxs.select("//div[@class='star-box-details']/strong/span/text()").extract())[0]
		movieItem["director"] = (hxs.select("//*[@id='overview-top']/div[4]/a/span/text()").extract())[0]		
		return movieItem