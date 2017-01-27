import scrapy


class DocsSpider(scrapy.Spider):
	name = 'doctors_spider'
	start_urls = ['http://medicalboard.co.ke/online-services/retention/']

	def parse(self, response):
		base_xpath = '//table/tbody/tr'
		for doc in response.xpath(base_xpath):
			name = './/td[1]/text()'
			reg_date = './/td[2]/text()'
			reg_no = './/td[3]/text()'
			address = './/td[4]/text()'
			qualifications = './/td[5]/text()'
			specialty = './/td[6]/text()'
			sub_speciality = './/td[7]/text()'
			yield {
				'name': doc.xpath(name).extract(),
				'reg_date': doc.xpath(reg_date).extract(),
				'reg_no': doc.xpath(reg_no).extract(),
				'address': doc.xpath(address).extract(),
				'qualifications': doc.xpath(qualifications).extract(),
				'specialty': doc.xpath(specialty).extract(),
				'sub_speciality': doc.xpath(sub_speciality).extract(),
			}

		# next_page = response.xpath('//div[@id = "tnt_pagination"]/span[@class = "active_tnt_link"]/text()').extract_first()
		# print "TYPE OF NEXT PAGE IS {}".format(type(next_page))
		next_page_list = response.xpath('//div[@id = "tnt_pagination"]/a//@href').extract()
		next_page = next_page_list[-1]
		print "############ NEXT PAGE: {}".format(next_page)
		if next_page is not None:
			next_page = response.urljoin(next_page)
			print "############ WORKING ON PAGE: {}".format(next_page)
			# next_page = int(next_page) + 1
			# print "############ NEXT PAGE: {}".format(next_page)
			# next_page = "http://medicalboard.co.ke/online-services/retention/?currpage={}".format(str(next_page))
			yield scrapy.Request(next_page, callback=self.parse)