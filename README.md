## A python flask webapp wrapper for Starhealth sms module

This app receives accomplishes the following
* Receives HTTP calls from the SMS provider
* Sends an HTTP call to AWS Lambda which triggers an event
* The event triggered is to query a cloud search using the keywords in the sms
* The search query is recived as a response and then an sms is send back and logs the message on sqlite db

### To run this app
* Create a virtual environment
* fire up your terminal
* clone this repo
* Inside the virtual environment run `pip install -r requirements.txt`
* Run ` export FLASK_APP=app/app.py ` to tell your terminal which application to work with
* Finally run `flask run ` to start the app

### Usage
Once the app is running on the home page you will see a form that will mimic the processing of receiving an sms from the sms provider:
* A madatory texbox for the number doing the search.
* A mandatory text box for the search query

If you fill the above text boxes with the required data and submit the form, the app will understand it as a received sms and send the query to AWS lambda for quering on CloudSearch and wait for a reponse of the search results which will be send as an sms to the number provided.

## IMPORTANT
Most of the above features are currently road maps and many of them might not have been implemenented as of now but check back soon to see the stable version in all its glory.
