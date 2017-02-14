# encoding=utf8
from flask import render_template, redirect, url_for, current_app, request, flash, jsonify
from . import main
from .forms import SubmissionForm
from werkzeug.useragents import UserAgent
from africastalking.AfricasTalkingGateway import (AfricasTalkingGateway as SMSGateway, AfricasTalkingGatewayException as SMSGatewayException)
from .. import db
from ..models import Doc, QueryLog, Nhif
import re
import csv
from datetime import datetime
from sqlalchemy.exc import IntegrityError, InvalidRequestError

import sys
import os
import urllib2
import json
import requests

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
	nhif_count = db.session.query(Nhif).count()
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

	return render_template('index.html', form=form, doctors_count=doctors_count, nhif_count=nhif_count)


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
	if request.args.get('phoneNumber') and request.args.get('message'):
		phoneNumber = (request.args.get('phoneNumber')).strip()
		message = (request.args.get('message')).strip()
		msg = build_query_response(message)
		if current_app.config['SEND_SMS']:
			send_reply_sms(phoneNumber, msg[0])
		return jsonify(msg)
	return "Missing Url Parameters"


# @main.route('/sms')
# def sms_query():
# 	# source_ip = request.remote_addr
# 	if request.headers.getlist("X-Forwarded-For"):
# 		source_ip = request.headers.getlist("X-Forwarded-For")[0]
# 	else:
# 		source_ip = request.environ['REMOTE_ADDR']
# 	user_agent = UserAgent(request.headers.get('User-Agent'))
# 	channel = "sms-endpoint"
# 	if request.args.get('phoneNumber') and request.args.get('message'):
# 		phoneNumber = (request.args.get('phoneNumber')).strip()
# 		message = (request.args.get('message')).strip()
# 		msg = process_query(message)
# 		print msg
# 		try:
# 			send_reply_sms(phoneNumber, msg)
# 			flash("Messsge sent successfuly")
# 			log_query(phoneNumber, message, source_ip, user_agent, channel)
# 		except:
# 			flash("An Error Occured", "error")
# 		return redirect(url_for('.index'))
# 	else:
# 		flash("Mandatory parameters missing", 'error')
# 		return redirect(url_for('.index'))


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


@main.route('/load-nhifdata')
def load_nhifdata():
	file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'scraper/nhif.csv'))
	with open(file_path, 'rb') as f:
		reader = csv.reader(f)
		reader.next()
		for row in reader:
			nhif = Nhif()
			nhif.hospital =  unicode((row[0]).strip())
			nhif.code = (row[1]).strip()
			nhif.cover = (row[2]).strip()
			nhif.location = (row[3]).strip()
			db.session.add(nhif)
			try:

				db.session.commit()
			except IntegrityError:
				pass
			except InvalidRequestError:
				db.session.rollback()
			except Exception:
				db.session.rollback()
	return redirect(url_for('.index'))


def find_keyword_in_query(query, keywords):
	regex = re.compile(r'\b(?:%s)\b' % '|'.join(keywords), re.IGNORECASE)
	return re.search(regex, query)


def build_query_response(query):
	query = clean_query(query)
	docs_keywords = current_app.config['DOC_KEYWORDS']
	clinicalofficers_keywords = current_app.config['CO_KEYWORDS']
	nurse_keywords = current_app.config['NO_KEYWORDS']
	nhif_keywords = current_app.config['NHIF_KEYWORDS']
	hf_keywords = current_app.config['HF_KEYWORDS'] # Health facilities keywords
	# Start by looking for doctors keywords
	if find_keyword_in_query(query, docs_keywords):
		search_terms = find_keyword_in_query(query, docs_keywords)
		query = query[:search_terms.start()] + query[search_terms.end():]
		end_point = current_app.config['DOCTORS_SEARCH_URL']
		r = requests.get(end_point, params={'q': query})
		msg = construct_docs_response(parse_cloud_search_results(r))
		print msg
		return [msg, r.json()]
	# Looking for Nurses keywords
	elif find_keyword_in_query(query, nurse_keywords):
		search_terms = find_keyword_in_query(query, nurse_keywords)
		query = query[:search_terms.start()] + query[search_terms.end():]
		end_point = current_app.config['NURSE_SEARCH_URL']
		r = requests.get(end_point, params={'q': query})
		msg = construct_nurse_response(parse_cloud_search_results(r))
		print msg
		return [msg, r.json()]
	# Looking for clinical officers Keywords
	elif find_keyword_in_query(query, clinicalofficers_keywords):
		search_terms = find_keyword_in_query(query, clinicalofficers_keywords)
		query = query[:search_terms.start()] + query[search_terms.end():]
		end_point = current_app.config['CO_SEARCH_URL']
		r = requests.get(end_point, params={'q': query})
		msg = construct_co_response(parse_cloud_search_results(r))
		print msg
		return [msg, r.json()]
	# Looking for nhif hospitals
	elif find_keyword_in_query(query, nhif_keywords):
		search_terms = find_keyword_in_query(query, nhif_keywords)
		query = query[:search_terms.start()] + query[search_terms.end():]
		end_point = current_app.config['NHIF_SEARCH_URL']
		r = requests.get(end_point, params={'q': query})
		msg = construct_nhif_response(parse_cloud_search_results(r))
		print msg
		return [msg, r.json()]
	# Looking for health facilities
	elif find_keyword_in_query(query, hf_keywords):
		search_terms = find_keyword_in_query(query, hf_keywords)
		query = query[:search_terms.start()] + query[search_terms.end():]
		end_point = current_app.config['HF_SEARCH_URL']
		r = requests.get(end_point, params={'q': query})
		msg = construct_hf_response(parse_cloud_search_results(r))
		print msg
		return [msg, r.json()]
	# If we miss the keywords then reply with the prefered query formats
	else:
		msg_items = []
		msg_items.append("We could not understand your request.")
		msg_items.append("Example query for doctors: DR SAMUEL AMAI")
		msg_items.append("Example query for clinical officers: CO SAMUEL AMAI")
		msg_items.append("Example query for nurse officers: NO SAMUEL AMAI")
		msg = " ".join(msg_items)
		print msg
		return [msg, {'error':" ".join(msg_items)}]

def parse_cloud_search_results(response):
	result_list = []
	result_to_send_count = current_app.config['SMS_RESULT_COUNT']
	data_dict = response.json()
	fields_dict = (data_dict['hits'])
	hits = fields_dict['hit']
	result_list = []
	search_results_count = len(hits)
	print "FOUND {} RESULTS".format(search_results_count)
	for item in hits:
		result = item['fields']
		if len(result_list) < result_to_send_count:
			result_list.append(result)
		else:
			break
	return result_list


def process_query(query):
	# Clean Query
	cleaned_query = clean_query(query)

	# Get Doctors
	docs_found = []
	nhif_found = []
	docs = db.session.query(Doc).all()
	nhif_data = db.session.query(Nhif).all()
	terms = cleaned_query

	# Start with nhif/location based query
	for nhif in nhif_data:
		if len(nhif_found) < 5:
			if findWholeWord(terms)(nhif.location):
				nhif_found.append(nhif)
		else:
			break
	if len(nhif_found) > 0:
		return construct_nhif_message(nhif_found)
	else:
		# Search for docs and construct a message
		for doc in docs:
			if len(docs_found) < 4:
				if findWholeWord(terms)(doc.names):
					docs_found.append(doc)
			else:
				break
		return construct_message(docs_found)


def construct_nhif_message(docs_list):
	count = 1
	msg_items = []

	for nhif in docs_list:
		status = "".join([str(count), ".", nhif.hospital])
		count = count + 1
		msg_items.append(status)
	if len(docs_list) == 5:
		msg_items.append("Find the full list at http://health.the-star.co.ke")

	return "\n".join(msg_items)


def construct_message(docs_list):
	if len(docs_list) < 1:
		return "Could not find a doctor with that name or the location you provided is currently not served by an NHIF accredited hospital"

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


def construct_co_response(co_list):
	# Just incase we found ourselves here with an empty list
	if len(co_list) < 1:
		return "Could not find a clinical officer with that name"
	count = 1
	msg_items = []
	for co in co_list:
			status = " ".join([str(count), co['name'], "-", co['qualification']])
			msg_items.append(status)
			count = count + 1
	if len(co_list) == 5:
		msg_items.append("Find the full list at http://health.the-star.co.ke")
	print "\n".join(msg_items)
	return "\n".join(msg_items)



def construct_nurse_response(nurse_list):
	# Just incase we found ourselves here with an empty list
	if len(nurse_list) < 1:
		return "Could not find a nurse with that name"
	count = 1
	msg_items = []
	for nurse in nurse_list:
		status = " ".join([str(count)+".", nurse['name']+",", "VALID TO", nurse['valid_until']])
		msg_items.append(status)
		count = count + 1
	if len(nurse_list) == 5:
		msg_items.append("Find the full list at http://health.the-star.co.ke")

	return "\n".join(msg_items)


def construct_hf_response(hf_list):
	# Just incase we found ourselves here with an empty list
	if len(hf_list) < 1:
		return "Could not find a nurse with that name"
	count = 1
	msg_items = []
	for hf in hf_list:
		status = " ".join([str(count) + ".", hf['name']+" -", hf['keph_level_name']])
		msg_items.append(status)
		count = count + 1
	if len(hf_list) == 5:
		msg_items.append("Find the full list at http://health.the-star.co.ke")

	return "\n".join(msg_items)


def construct_nhif_response(nhif_list):
	# Just incase we found ourselves here with an empty list
	if len(nhif_list) < 1:
		return "Could not find a nurse with that name"
	count = 1
	msg_items = []
	for nhif in nhif_list:
		status = " ".join([str(count) + ".", nhif['name']])
		msg_items.append(status)
		count = count + 1
	if len(nhif_list) == 5:
		msg_items.append("Find the full list at http://health.the-star.co.ke")

	return "\n".join(msg_items)


def construct_docs_response(docs_list):
	# Just incase we found ourselves here with an empty list
	if len(docs_list) < 1:
		return "Could not find a doctor with that name"
	count = 1
	msg_items = []

	for doc in docs_list:
		# Ignore speciality if not there, dont display none
		if doc['specialty'] == "None":
			status = " ".join([str(count), doc['name'], "-", doc['registration_number'], "-", doc['qualification']])
		else:
			status = " ".join([str(count), doc['name'], "-", doc['registration_number'], "-", doc['qualification'], doc['specialty']])
		msg_items.append(status)
		count = count + 1
	if len(docs_list) == 4:
		msg_items.append("Find the full list at http://health.the-star.co.ke")

	return "\n".join(msg_items)


def clean_query(query):
	query = query.lower().strip().replace(".","")
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
