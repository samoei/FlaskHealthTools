from flask import render_template, redirect, url_for, current_app, request, flash
from random import shuffle
from . import main
from .forms import SubmissionForm
from werkzeug.useragents import UserAgent
from africastalking.AfricasTalkingGateway import (AfricasTalkingGateway as SMSGateway, AfricasTalkingGatewayException as SMSGatewayException)
from .. import db
from ..models import Doctor, Qualification
import re

doctors = [
	{
		"name": "Philemon Kipkorir Samoei",
		"reg_no": "B120"
	},
	{
		"name": "Bilha Mariana Kweyu",
		"reg_no": "B121"
	},
	{
		"name": "Kevin Chesa",
		"reg_no": "B122"
	},
	{
		"name": "Ann Njeri Kemunto",
		"reg_no": "B123"
	},
	{
		"name": "Mercy Chepleting",
		"reg_no": "B124"
	},
	{
		"name": "Zablon Amanaka",
		"reg_no": "B125"
	},
	{
		"name": "Ramjesh Shah",
		"reg_no": "B126"
	},
	{
		"name": "koothrappali Ramjesh",
		"reg_no": "B127"
	},
	{
		"name": "Kamau James Mwangi",
		"reg_no": "B128"
	},
	{
		"name": "Allan Oriri",
		"reg_no": "B129"
	},
	{
		"name": "Leah Jemator Kiptui",
		"reg_no": "B130"
	},
	{
		"name": "Elvis Khamala",
		"reg_no": "B131"
	},
	{
		"name": "Winnie Wanzetse",
		"reg_no": "B132"
	},
	{
		"name": "Wacheke Murumbi",
		"reg_no": "B133"
	},
	{
		"name": "Festus Omondi",
		"reg_no": "B134"
	},
	{
		"name": "Isaac Sambu",
		"reg_no": "B135"
	},
	{
		"name": "Prof, John Onyango",
		"reg_no": "B136"
	},
	{
		"name": "Howard Wolowitz",
		"reg_no": "B137"
	},
	{
		"name": "Sheldon Cooper",
		"reg_no": "B138"
	},
	{
		"name": "Samson Kamau",
		"reg_no": "B139"
	},
	{
		"name": "Samoei Joshua",
		"reg_no": "B140"
	},
	{
		"name": "Valentine Samoei",
		"reg_no": "B141"
	},
]

years = ["1991","1992","1993","1994","1995","1996","1997","1998","1991","1999","2000","2001","2002","2003","2004","2005","2006",]
where = ["Edinbrugh", "Nairobi", "Liverpool", "Eldoret", "London", "Dar es salaam", "Kampala", "Massachusetts"]
what = ["BDS", "MCHD", "MSc", "MDS", "MPH", "MBChB"]


@main.route('/', methods=['POST', 'GET'])
def index():
	form = SubmissionForm()
	source_ip = request.remote_addr
	user_agent = UserAgent(request.headers.get('User-Agent'))
	doctors = db.session.query(Doctor).all()
	shuffle(doctors)
	if form.validate_on_submit():

		# Extract the phone_number from the form
		phone_no = form.phone_no.data
		# Clean the phone number
		phone_no = phone_no.strip()
		query = form.query.data
		msg = process_query(query)
		try:
			send_reply_sms(phone_no, msg)
			flash("Messsge sent successfuly")
		except:
			flash("An Error Occured")
		return redirect(url_for('.index'))

	return render_template('index.html', form=form, doctors=doctors)

@main.route('/load-data')
def load_data():
	for doc in doctors:
		doc_obj = Doctor(reg_no=doc["reg_no"], names=doc["name"])
		shuffle(what)
		shuffle(where)
		shuffle(years)
		qual_obj = Qualification(what=what[0], where=where[0], when=years[0], doc=doc_obj)
		db.session.add_all([doc_obj, qual_obj])
		db.session.commit()
	return redirect(url_for('.index'))



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