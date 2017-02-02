# -*- coding: utf-8 -*-
import scrapy


class DocsItem(scrapy.Item):
	name = scrapy.Field()
	reg_date = scrapy.Field()
	reg_no = scrapy.Field()
	address = scrapy.Field()
	qualifications = scrapy.Field()
	specialty = scrapy.Field()
	sub_speciality = scrapy.Field()


class NhifItem(scrapy.Item):
	code = scrapy.Field()
	hospital = scrapy.Field()
	nhif_branch = scrapy.Field()
	cover = scrapy.Field()
