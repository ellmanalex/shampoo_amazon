# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ShampooItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    asin = scrapy.Field()
    price_per = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    buy_box = scrapy.Field()
    list_price = scrapy.Field()
    merchant = scrapy.Field()
    product_title = scrapy.Field()
    brand = scrapy.Field()
    product_dims = scrapy.Field()
    shipping_weight = scrapy.Field()
    ingredients = scrapy.Field()
    description = scrapy.Field()

  
