import scrapy
from scraper.items import DocsItem, NhifItem


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

class NhifSpider(scrapy.Spider):
	name = 'nhif_spider'
	start_urls = ['http://www.nhif.or.ke/healthinsurance/medicalFacilities']
	allowed_domains = ['http://www.nhif.or.ke']

	def parse(self, response):
		base_xpath = '//div[contains(@class,"panel") and contains(@class, "panel-default")]'
		for region in response.xpath(base_xpath):
			region_base = './div[contains(@class,"panel-collapse") and contains(@class, "collapse")]/div[@class="panel-body"]/div[@class="tabs-section"]/div[@class="tab-content"]/div[contains(@class,"tab-pane") and contains(@class, "fade")]/div[@class="row"]//table/tbody/tr'
			for r_base in region.xpath(region_base):
				nhif_item = NhifItem()
				code = './/td[1]/text()'
				hospital = './/td[2]/text()'
				nhif_branch = './/td[3]/text()'
				cover = './/td[4]/text()'

				nhif_item['code'] = r_base.xpath(code).extract()
				nhif_item['hospital'] = r_base.xpath(hospital).extract()
				nhif_item['nhif_branch'] = r_base.xpath(nhif_branch).extract()
				nhif_item['cover'] = r_base.xpath(cover).extract()

				yield nhif_item
