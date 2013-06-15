from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from GoOne.items import MovieItem

class ImdbSpider(BaseSpider):
	name = "Imdb"
	allowed_domains = ["imdb.com"]
	start_urls = [
		"http://www.imdb.com/chart/top"]

	def parse(self,response):
		hxs = HtmlXPathSelector(response)
		sites = hxs.select("//div[@id='main']/table[@border='1']/tr")
		movieItems = []		
		for site in sites[1:]:
			movieItem = MovieItem()
			ranks = site.select("td[1]/font/b/text()").extract()
			movieItem["rank"] = ranks[0]
			rating = site.select("td[2]/font/text()").extract()
			movieItem["rating"] = rating[0]
			title = site.select("td[3]/font/a/text()").extract()
			movieItem["title"] =  title[0]
			votes = site.select("td[4]/font/text()").extract()
			movieItem["votes"] =  votes[0]
			movieItems.append(movieItem)
		return movieItems