from scrapy import Spider, Request
from shampoo.items import ShampooItem
import re
from datetime import date
from scrapy.shell import inspect_response

class AmazonSpider(Spider):
    name = 'amazon_spider'
    allowed_urls = ['https://www.amazon.com/']
    start_urls = ['https://www.amazon.com/s?k=toothpaste&i=beauty&rh=n%3A3778371&page=1&qid=1589072724&ref=sr_pg_1']

    def parse(self, response):
        page_urls = ['https://www.amazon.com/s?k=toothpaste&i=beauty&rh=n%3A3778371&page={}&qid=1589072724&ref=sr_pg_{}'.format(x,x) for x in range(1,201)]

        for page_url in page_urls:
            yield Request(url=page_url, callback=self.parse_result_page)

    def parse_result_page(self, response):
        product_urls = response.xpath('//a[@class="a-link-normal a-text-normal"]/@href').extract()[1:50]
        product_urls = ['https://www.amazon.com' + s for s in product_urls]

        #for x in product_urls:
        #    print(*''*50, x, '-'*50)   

        for product_url in product_urls:
            yield Request(url=product_url, callback=self.parse_product_page)


    def parse_product_page(self, response):
        
        try:
            asin = re.search('https://www\.amazon\.com/[A-Za-z0-9- %]+/dp/([A-Z0-9]+).*', response.url).group(1)
        except:
            asin = None

        #extract product info table and convert to list of elements

        try:
            if len(response.xpath('//div[@id = "detail-bullets_feature_div"]//text()').extract())>0:
                product_info = response.xpath('//div[@id = "detail-bullets_feature_div"]//text()').extract()
            if len(response.xpath('//div[@id = "detail-bullets"]//text()').extract())>0:
                product_info = response.xpath('//div[@id = "detail-bullets"]//text()').extract()
        except:
            None

        try:
            product_info = [i for i in product_info if re.search(r'[1-9a-zA-z]',i)]
            product_info = list(map(lambda x: re.sub('[\n()]','',x),product_info))
            product_info = [x.strip(' ') for x in product_info]
        except:
            None

        #extract product_dims
        try:
            product_dims = product_info[product_info.index('Product Dimensions:')+1]
        except:
            product_dims = None

        #extract shipping weight
        try:
            shipping_weight = product_info[product_info.index('Shipping Weight:')+1]
        except:
            shipping_weight = None

        #extract rating
        try:
            rating = product_info[product_info.index('Customer Reviews:')+1]
        except:
            rating = None

        #review count
        try:
            review_count = product_info[product_info.index('Customer Reviews:')+2]
            review_count = int(''.join(re.findall(r'[1-9]',review_count)))
        except:
            None

       # buy box
        try:
            buy_box = current_price = response.xpath('//span[@id = "priceblock_ourprice"]//text()').extract_first()
            buy_box = float(buy_box.replace('$',''))
        except:
            None

       #list price
        try:
            list_price = response.xpath('//span[@class="priceBlockStrikePriceString a-text-strike"]//text()').extract()
            list_price = float(list_price.replace('$',''))
        except: 
            None 

       # #product title
        product_title = response.xpath('//span[@id = "productTitle"]//text()').extract() 
        product_title = ''.join(product_title).replace('\n','').strip()

       # #merchant
        try:
            merchant = response.xpath('//div[@id = "merchant-info"]//text()').extract()
            merchant = ''.join(merchant).replace('\n','').strip()
        except:
            None

       # #brand
        brand = response.xpath('//a[@id = "bylineInfo"]//text()').extract_first()

        price_per = None
       # #price/ounce
        try:
            price_per = response.xpath('//span[@class = "a-size-small a-color-price"]//text()').extract()[0]
            price_per = re.sub('[\n()]','',price_per).strip()
        except:
            None

       # #important information        
        try:
            ingredients = response.xpath('//div[@id="important-information"]//text()').extract()
            ingredients = [i for i in ingredients if re.search(r'[1-9a-zA-z]',i)]
            ingredients = ingredients[ingredients.index('Ingredients')+1]
        except:
            None

       # # description
        try:
            description = response.xpath('//div[@id="feature-bullets"]/ul/li/span/text()').extract()
            description = [re.sub('[\n()]','',x).strip() for x in description]
        except:
            None

       # #review by feature
        try:
            review_feature = response.xpath('//div[@id="cr-summarization-attributes-list"]').extract()
        except:
            None

        #page number
        page_number = response.request


        item = ShampooItem()
        item['asin'] = asin
        item['price_per'] = price_per
        item['rating'] = rating
        item['review_count'] = review_count
        item['buy_box'] = buy_box
        item['list_price'] = list_price
        item['merchant'] = merchant
        item['product_title'] = product_title
        item['brand'] = brand
        item['product_dims'] = product_dims
        item['shipping_weight'] = shipping_weight
        item['ingredients'] = ingredients
        item['description'] = description

        yield item


