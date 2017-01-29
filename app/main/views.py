# encoding=utf8
from flask import render_template, redirect, url_for, current_app, request, flash
from . import main
from .forms import SubmissionForm
from werkzeug.useragents import UserAgent
from africastalking.AfricasTalkingGateway import (AfricasTalkingGateway as SMSGateway, AfricasTalkingGatewayException as SMSGatewayException)
from .. import db
from ..models import Doc, QueryLog
import re
import csv
from datetime import datetime
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')
basedir = os.path.abspath(os.path.dirname(__file__))


@main.route('/', methods=['POST', 'GET'])
def index():
	form = SubmissionForm()
	if request.headers.getlist("X-Forwarded-For"):
		source_ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
		source_ip = request.environ['REMOTE_ADDR']
	user_agent = UserAgent(request.headers.get('User-Agent'))
	channel = "form"
	doctors_count = db.session.query(Doc).count()
	if form.validate_on_submit():

		# Extract the phone_number from the form
		phone_no = form.phone_no.data
		# Clean the phone number
		phone_no = phone_no.strip()
		query = form.query.data
		msg = process_query(query)
		print msg
		try:
			send_reply_sms(phone_no, msg)
			flash("Messsge sent successfuly")
			log_query(phone_no, query, source_ip, user_agent, channel)
		except Exception as e:
			flash("An Error Occured")
			raise e
		return redirect(url_for('.index'))

	return render_template('index.html', form=form, doctors_count=doctors_count)


def log_query(phone_no, query, source_ip, user_agent, channel):
	query_log = QueryLog(phoneNumber=phone_no, query=query, ip_address=source_ip, browser=user_agent.browser, operating_system=user_agent.platform, channel=channel)
	db.session.add(query_log)
	try:
		db.session.commit()
	except Exception as e:
		db.session.rollback()
		raise e


@main.route('/sms')
def sms_query():
	# source_ip = request.remote_addr
	if request.headers.getlist("X-Forwarded-For"):
		source_ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
		source_ip = request.environ['REMOTE_ADDR']
	user_agent = UserAgent(request.headers.get('User-Agent'))
	channel = "sms-endpoint"
	if request.args.get('phoneNumber') and request.args.get('message'):
		phoneNumber = (request.args.get('phoneNumber')).strip()
		message = (request.args.get('message')).strip()
		msg = process_query(message)
		print msg
		try:
			send_reply_sms(phoneNumber, msg)
			flash("Messsge sent successfuly")
			log_query(phoneNumber, message, source_ip, user_agent, channel)
		except:
			flash("An Error Occured", "error")
		return redirect(url_for('.index'))
	else:
		flash("Mandatory parameters missing", 'error')
		return redirect(url_for('.index'))


@main.route('/load-data')
def load_data():
	file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'scraper/items.csv'))
	with open(file_path, 'rb') as f:
		reader = csv.reader(f)
		reader.next()
		for row in reader:
			doc = Doc()
			doc.names =  unicode((row[0]).strip())
			doc.reg_no = (row[1]).strip()
			doc.qualifications = (row[2]).strip()
			doc.specialty = (row[3]).strip()
			doc.reg_date = datetime.strptime((row[4]).strip() , '%Y-%m-%d')
			doc.address = (row[5]).strip()
			doc.sub_speciality = (row[6]).strip()
			db.session.add(doc)
			try:

				db.session.commit()
			except IntegrityError:
				pass
			except InvalidRequestError:
				db.session.rollback()
			except Exception:
				db.session.rollback()
	return redirect(url_for('.index'))


def process_query(query):
	# Clean Query
	cleaned_query = clean_query(query)

	# Get Doctors
	docs_found = []
	docs = db.session.query(Doc).all()
	terms = cleaned_query

	# Search for docs and construct a message
	for doc in docs:
		if len(docs_found) < 4:
			if findWholeWord(terms)(doc.names):
				docs_found.append(doc)
		else:
			break
	return construct_message(docs_found)


def construct_message(docs_list):
	if len(docs_list) < 1:
		return "Could not find a doctor with that name"

	count = 1
	msg_items = []

	for doc in docs_list:
		if doc.specialty == "NONE":
			status = "".join([str(count), ".", " ", doc.names, " ", "-", doc.reg_no, " ", "-", " ", doc.qualifications, "\n"])
		else:
			status = "".join([str(count), ".", " ", doc.names, " ", "-", doc.reg_no, "-", " ", doc.qualifications, " ", doc.specialty, "\n"])
		count = count + 1
		msg_items.append(status)
	if len(docs_list) == 4:
		msg_items.append("Find the full list at http://health.the-star.co.ke")

	return " ".join(msg_items)


def clean_query(query):
	query = query.lower().strip()
	if query.startswith(u'dr'):
		return query[2:].strip()
	elif query.startswith(u'doctor'):
		return query[6:].strip()
	else:
		return query


def findWholeWord(w):
	return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def send_reply_sms(to, msg):
	gateway = SMSGateway(current_app.config['SMS_PROVIDER_USERNAME'], current_app.config['SMS_PROVIDER_KEY'])
	try:
		# Thats it, hit send and we'll take care of the rest.

		results = gateway.sendMessage(to, msg)

		for recipient in results:
			# status is either "Success" or "error message"
			print 'number=%s;status=%s;messageId=%s;cost=%s' %(recipient['number'],
			recipient['status'],
			recipient['messageId'],
			recipient['cost'])
	except SMSGatewayException, e:
		print 'Encountered an error while sending: %s' % str(e)
