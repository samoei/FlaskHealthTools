from flask import render_template, redirect, url_for, current_app, request
from . import main
from .forms import SubmissionForm
from werkzeug.useragents import UserAgent
from africastalking.AfricasTalkingGateway import (AfricasTalkingGateway as SMSGateway, AfricasTalkingGatewayException as SMSGatewayException)
from .. import db
from ..models import Doctor, Qualification
import re


@main.route('/', methods=['POST', 'GET'])
def index():
	form = SubmissionForm()
	source_ip = request.remote_addr
	user_agent = UserAgent(request.headers.get('User-Agent'))
	if form.validate_on_submit():

		# Extract the phone_number from the form
		phone_no = form.phone_no.data
		# Clean the phone number
		phone_no = phone_no.strip()
		query = form.query.data
		msg = process_query(query)
		print msg


		send_reply_sms(phone_no, msg)
		return redirect(url_for('.index'))

	return render_template('index.html', form=form)


def process_query(query):
	# print query
	# Clean Query
	cleaned_query = clean_query(query)
	# print cleaned_query

	# Get Doctors
	docs_found = []
	docs  = db.session.query(Doctor).all()
	terms = cleaned_query.split()

	for doc in docs:
		if len(docs_found) < 4:
			for term in terms:
				if findWholeWord(term)(doc.names):
					# print doc.names
					docs_found.append(doc)
					break
		else:
			break
	return construct_message(docs_found)

	#
def construct_message(docs_list):
	if len(docs_list) < 1:
		return "Could not find a doctor with that name"

	messge = ""
	count = 1
	msg_items = []

	for doc in docs_list:
		# print doc.names
		# print doc.reg_no
		status = "".join([str(count),". Dr. ",doc.names, "-", doc.reg_no])
		for qual in doc.qualifications:
			status_qua = "".join([status,"-",qual.what, "(", qual.where, ")", qual.when])
			# print qual.what
			# print qual.when
			# print qual.where
		count = count + 1
		msg_items.append(status_qua)

	return " ".join(msg_items)


def clean_query(query):
	# print type(query)
	query = query.lower().strip()
	# print type(query)
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