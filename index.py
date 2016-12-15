from __future__ import print_function
import requests
from BeautifulSoup import BeautifulSoup


def lambda_handler(event, context):
	print("event.session.application.applicationId=" +
		  event['session']['application']['applicationId'])
	if event['session']['new']:
		on_session_started({'requestId': event['request']['requestId']},
						   event['session'])

	if event['request']['type'] == "LaunchRequest":
		return on_launch(event['request'], event['session'])
	elif event['request']['type'] == "IntentRequest":
		return on_intent(event['request'], event['session'])
	elif event['request']['type'] == "SessionEndedRequest":
		return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
	print("on_session_started requestId=" + session_started_request['requestId']
		  + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
	print("on_launch requestId=" + launch_request['requestId'] +
		  ", sessionId=" + session['sessionId'])
	return get_welcome_response()


def on_intent(intent_request, session):
	print("on_intent requestId=" + intent_request['requestId'] +
		  ", sessionId=" + session['sessionId'])

	intent = intent_request['intent']
	intent_name = intent_request['intent']['name']

	if intent_name == "BusRoutesIntent":
		return getRoutes(intent, session)
	elif intent_name == "stopTimeIntent":
		return findStopTime(intent, session)
	elif intent_name == "getStopsIntent":
		return getStopsForRoute(intent, session)
	elif intent_name == "AMAZON.HelpIntent":
		return get_welcome_response()
	elif intent_name == "AMAZON.StopIntent":
		return handle_session_end_request()
	else:
		raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
	print("on_session_ended requestId=" + session_ended_request['requestId'] +
		  ", sessionId=" + session['sessionId'])


# --------------- Helper functions that will allow us to find info about the busses -----------------

def getRouteList():
	routes = {}
	r = requests.get('https://www.usfbullrunner.com/simple/routes')
	html = r.text
	soup = BeautifulSoup(html)
	for link in soup.findAll('a'):
		routes.update({link.text.replace("Route ", ""): link.get('href').replace("/simple/routes/", "").replace("/direction", "")})

	return routes

def getRoutes(intent, session):
	routes = getRouteList()
	speech_output = "There are " + routes.len + " routes running. Please say the name of the route you'd like, or say, list, for a list of all running routes"
	reprompt_text = "Please say a route name, or say list to get a list of all running routes."
	should_end_session = False
	session_attributes = {}

	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def getStopList(route):
	stops = {}
	r = requests.get('https://www.usfbullrunner.com/simple/routes/' + route + '/stops')
	html = r.text
	soup = BeautifulSoup(html)
	for link in soup.findAll('a'):
		if 'stop' in link.get('href'):
			stops.update({link.text: link.get('href').replace("/simple/routes/"+route+"/stops/", "")})
	return stops

def getStopTime(route,stop):
	routes = getRouteList()
	
	r = requests.get('https://www.usfbullrunner.com/simple/routes/' + route + '/stops/' + stop)
	print ('https://www.usfbullrunner.com/simple/routes/' + route + '/stops/' + stop)
	html = r.text
	soup = BeautifulSoup(html)
	for link in soup.findAll('li'):
		if 'arrives in ' in link.text:
			return link.text
		elif 'Arrival predictions are not available at this time.' in link.text:
			return "That bus is currently not running it's usual route, so there is no prediction available."

def f(x):
	return {
		'jp': "Juniper-Poplar",
		'juniper poplar hall': "Juniper-Poplar",
		'juniper poplar': "Juniper-Poplar",
		"baseball stadium":"Baseball Field",
		"communications building":"Alumni Center",
		"cooper":"Cooper Hall",
		"cwy":"CW Young Hall",
		"cypress":"Cypress Apartments",
		"fine arts":"Fine Arts Studio",
		"fourty fifty":"40FIFTY Lofts",
		"greek village":"Greek Housing",
		"holly at magnolia":"Holly at Magnolia Drive",
		"jp":"Juniper-Poplar",
		"library":"Cambridge Woods Drive",
		"lot 34":"The WELL (Lot 34)",
		"maple at holly":"Maple Suites at Holly",
		"maple":"Maple Suites",
		"math building":"Math & Engineering",
		"msc":"Marshall Student Center",
		"park and ride 43 east":"Park and Ride 43 East",
		"park and ride 43 west":"Park and Ride Lot 43 West",
		"park and ride eightteen at baptist":"Park and Ride Lot 18 at Baptist Student Center",
		"park and ride eightteen elm":"Park and Ride Lot 18 at Elm Drive",
		"park and ride eightteen midway":"Park and Ride Lot 18 midway",
		"public health":"College of Public Health",
		"r and d":"Business North",
		"school of music":"School of Music North",
		"softball fields":"Softball Stadium",
		"juniper":"Juniper-Poplar",
		"club lib":"Library LIB",
		"the well":"The WELL (Lot 34)",
		"the library": "Library LIB"
		"engineering building":"Math & Engineering",
		"park and ride at bsc":"Park and Ride Lot 18 at Baptist Student Center",
		"park and ride at elm":"Park and Ride Lot 18 at Elm Drive",
		"park and ride at midway":"Park and Ride Lot 18 midway",
		"poplar":"Juniper-Poplar",
		"juniper popular": "Juniper-Poplar",
		"juniper popular hall": "Juniper-Poplar",
		"popular": "Juniper-Poplar",
		"JB": "Juniper-Poplar",
		"j. p.": "Juniper-Poplar",
		"m. s. c.": "Marshall Student Center",
		"c. w. y.": "CW Young Hall"
	}.get(x, x) 


# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
	session_attributes = {}
	card_title = "Welcome - USF Bullrunners"
	speech_output = "Welcome to the Bull Runner Alexa Skill! " \
					"You can ask me about bus routes and times for USF Bull Runners. " \
					"Go Bulls!"

	reprompt_text = "Ask me something like, What time will the bus on route A be at Juniper Poplar?" 
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, speech_output, reprompt_text, should_end_session))

def getStopsForRoute(intent, session):
	if 'Route' in intent['slots']:
		try:
			routeName = intent['slots']['Route']['value']
			routeName = routeName.capitalize()
		except:
			speech_output = "For what Route?"
			should_end_session = False
			card_title = None,
			reprompt_text = "What route would you like me to list the stops for?"

			return build_response(session_attributes, build_speechlet_response(
				card_title, None, speech_output, reprompt_text, should_end_session))

	routeList = getRouteList()
	routeID = routeList[routeName]

	stopList = getStopList(routeID)

	session_attributes = {}
	card_title = "USF Bullrunner - Stop List for Route " + routeName 
	reprompt_text = ""
	should_end_session = True
	speech_output = "The stops for Route " + routeName + " are "
	for key in stopList.iterkeys():
		speech_output += key + ", "

	return build_response(session_attributes, build_speechlet_response(
				card_title, speech_output, speech_output, reprompt_text, should_end_session))

def findStopTime(intent, session):
	if 'Route' in intent['slots'] and not "Route" in session.get('attributes', {}):
		try:
			routeName = intent['slots']['Route']['value'].title()
			routeList = getRouteList()
			routeID = routeList[routeName]
		except KeyError:
			if 'Stop' in intent['slots']:
				speech_output = "What Route?"
				try:
					session_attributes = set_stop_to_session(intent['slots']['Stop']['value'])
				except KeyError:
					if not "Stop" in session.get('attributes', {}):
						session_attributes = {}
						speech_output = "Please Specify a Route and Stop."
				
				should_end_session = False
				card_title = None
				reprompt_text = ""

				return build_response(session_attributes, build_speechlet_response(
					card_title, None, speech_output, reprompt_text, should_end_session))
				
	elif "Route" in session.get('attributes', {}):
		routeName = session['attributes']['Route']
		routeList = getRouteList()
		routeID = routeList[routeName]

	if 'Stop' in intent['slots'] and not "Stop" in session.get('attributes', {}):
		try:
			stopList = getStopList(routeID)
			stopName = intent['slots']['Stop']['value']
		except KeyError:
			if 'Route' in intent['slots'] and not "Route" in session.get('attributes', {}):
				speech_output = "What Stop?"
				session_attributes = set_route_to_session(routeName)
				should_end_session = False
				reprompt_text = ""
				card_title = None
				return build_response(session_attributes, build_speechlet_response(
					card_title, None, speech_output, reprompt_text, should_end_session))

		else:
			try:
				stopName = f(stopName)
				stopID = stopList[stopName]
			except:
				speech_output = "Route " + routeName + " does not stop at " + stopName
				should_end_session = True
				reprompt_text = ""
				session_attributes = {}
				card_title = "USF Bullrunner"
				return build_response(session_attributes, build_speechlet_response(
					card_title, speech_output, speech_output, reprompt_text, should_end_session))

	elif "Stop" in session.get('attributes', {}):
		stopName = session['attributes']['Stop']
		stopList = getStopList(routeID)
		try:
			stopName = f(stopName)
			stopID = stopList[stopName]
		except:
			speech_output = "Route " + routeName + " does not stop at " + stopName
			should_end_session = True
			reprompt_text = ""
			session_attributes = {}
			card_title = ""
			return build_response(session_attributes, build_speechlet_response(
				card_title, None, speech_output, reprompt_text, should_end_session))
	print(stopID)
	print(routeID)
	if stopID and routeID:
		speech_output = getStopTime(routeID, stopID)
		print (speech_output)
		should_end_session = True
		return build_response(None, build_speechlet_response(
				"USF BullRunner", speech_output, speech_output, None, should_end_session))

def handle_session_end_request():
	card_title = None
	speech_output = None
	should_end_session = True
	return build_response({}, build_speechlet_response(None, None,
		speech_output, None, should_end_session))

def set_route_to_session(route_name):
	return {"Route": route_name}

def set_stop_to_session(stop_name):
	return {"Stop": stop_name}


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(card_title, card_text, output, reprompt_text, should_end_session):
	if card_title is None:
		return {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'reprompt': {
				'outputSpeech': {
					'type': 'PlainText',
					'text': reprompt_text
				}
			},
			'shouldEndSession': should_end_session
		}
	else:
		return {
			'outputSpeech': {
				'type': 'PlainText',
				'text': output
			},
			'card': {
				'type': 'Simple',
				'title': card_title,
				'content': card_text
			},
			'reprompt': {
				'outputSpeech': {
					'type': 'PlainText',
					'text': reprompt_text
				}
			},
			'shouldEndSession': should_end_session
		}

def build_response(session_attributes, speechlet_response):
	return {
		'version': '1.0',
		'sessionAttributes': session_attributes,
		'response': speechlet_response
	}