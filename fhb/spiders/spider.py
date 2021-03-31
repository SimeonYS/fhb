import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FhbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FhbSpider(scrapy.Spider):
	name = 'fhb'
	start_urls = ['https://www.fhb.com/en/about-us/newsroom']

	def parse(self, response):
		post_links = response.xpath('//div[@class="coh-container coh-style--fhb-action-items-container coh-ce-cpt_fhb_mol_card_feat_left_align-9aad2da0"]/a[@title="Sell All"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_year)

	def parse_year(self, response):
		articles = response.xpath('//div[contains(@class,"coh-column coh-component coh-component-instance-")]/div[contains(@class,"coh-wysiwyg coh-component coh-component-instance")]/p')
		for article in articles:
			date = article.xpath('.//strong/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('//p[@class="coh-paragraph fhb-hero--themable--text coh-style--fhb-hero--heading coh-ce-cpt__fhb_hero-f2f1b1f2"]/text()').get()
		content = response.xpath('//div[@class="coh-wysiwyg coh-component coh-component-instance-7053d247-c966-4fb0-9a35-5439b1b97679 contextual-component coh-ce-cpt__fhb_rich_text-6672e27a"]//text()[not (ancestor::p[@class="text-align-center"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FhbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
