# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class MovieItem(Item):
    # define the fields for your item here like:
    # name = Field()
	rank = Field()
	rating = Field()
	title = Field()
	votes = Field()
	director = Field()
