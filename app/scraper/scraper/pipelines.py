# -*- coding: utf-8 -*-
import sys
import os

from scrapy.exceptions import DropItem
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from ...models import Doc


class ScraperPipeline(object):
	def __init__(self):
		try:
			try:
				engine = create_engine(os.environ.get('DATABASE_URL'), echo=False)
			except AttributeError:
				engine = create_engine(os.environ.get('DEV_DATABASE_URL'), echo=False)

		except OperationalError:
			sys.stderr.write("PROBLEM IN CONNECTING TO THE DATABASE\n")
			sys.exit(1)

		self.Base = declarative_base()
		self.Session = sessionmaker(bind=engine, autoflush=False)

	def open_spider(self, spider):
		self.session = self.Session()
		self.doc = Doc()

	def close_spider(self, spider):
		self.session.close()

	def process_item(self, item, spider):
		print ">>>>>>>>> WE ARE EXECUTING THIS FOR ITEM {} SPIDER {}".format(item, spider)
		self.doc.names = item['name']
		self.doc.reg_date = item['reg_date']
		self.doc.reg_no = item['reg_no']
		self.doc.address = item['address']
		self.doc.qualifications = item['qualifications']
		self.doc.specialty = item['specialty']
		self.doc.sub_speciality = item['sub_speciality']
		try:
			self.session.add(self.doc)
			self.session.commit()
		except:
			self.session.rollback()
			raise
		return item
