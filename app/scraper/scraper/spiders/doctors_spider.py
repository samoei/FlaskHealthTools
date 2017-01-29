import scrapy
from scraper.items import DocsItem


class DocsSpider(scrapy.Spider):
	name = 'doctors_spider'
	start_urls = ['http://medicalboard.co.ke/online-services/retention/']
	allowed_domains = ['medicalboard.co.ke']

	def parse(self, response):
		base_xpath = '//table/tbody/tr'
		for doc in response.xpath(base_xpath):
			doc_item = DocsItem()
			name = './/td[1]/text()'
			reg_date = './/td[2]/text()'
			reg_no = './/td[3]/text()'
			address = './/td[4]/text()'
			qualifications = './/td[5]/text()'
			specialty = './/td[6]/text()'
			sub_speciality = './/td[7]/text()'

			doc_item['name'] = doc.xpath(name).extract()
			doc_item['reg_date'] = doc.xpath(reg_date).extract()
			doc_item['reg_no'] = doc.xpath(reg_no).extract()
			doc_item['address'] = doc.xpath(address).extract()
			doc_item['qualifications'] = doc.xpath(qualifications).extract()
			doc_item['specialty'] = doc.xpath(specialty).extract()
			doc_item['sub_speciality'] = doc.xpath(sub_speciality).extract()

			yield doc_item


		next_page_list = response.xpath('//div[@id = "tnt_pagination"]/a//@href').extract()
		next_page = next_page_list[-1]
		print "############ NEXT PAGE: {}".format(next_page)
		if next_page is not None:
			next_page = response.urljoin(next_page)
			print "############ WORKING ON PAGE: {}".format(next_page)
			yield scrapy.Request(next_page, callback=self.parse)
