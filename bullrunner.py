import requests
from BeautifulSoup import BeautifulSoup

def getRouteList():
	routes = {}
	r = requests.get('https://www.usfbullrunner.com/simple/routes')
	html = r.text
	soup = BeautifulSoup(html)
	for link in soup.findAll('a'):
		routes.update({link.text: link.get('href').replace("/simple/routes/", "").replace("/direction", "")})

	print routes
	return routes

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
	r = requests.get('https://www.usfbullrunner.com/simple/routes/' + route + '/stops/' + stop)
	html = r.text
	soup = BeautifulSoup(html)
	for link in soup.findAll('li'):
		if 'arrives in ' in link.text:
			return link.text

