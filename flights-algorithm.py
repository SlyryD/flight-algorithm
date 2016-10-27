import os
import pdb
import re
import requests

searchurl = "https://www.googleapis.com/qpxExpress/v1/trips/search"
key = ""


def read_key():
	with open("key", "r") as h:
		key = h.read().strip()


origins = { "SEA": ["SEA"], "WAS": ["DCA", "IAD", "BWI"], "PIT": ["PIT"], "PVD": ["PVD", "BOS"], "MSP": ["MSP"], "NYC": ["LGA", "EWR", "JFK"], "DEN": ["DEN"]}
destinations = { "Colorado": ["DEN"], "Seattle": ["SEA"], "San Francisco": ["SFO", "SJC"], "LA": ["LAX", "BUR"], "San Diego": ["SAN"], "Maryland": ["DCA", "IAD", "BWI"], "New York": ["LGA", "EWR", "JFK"] }


def get_price(response):
	if u"trips" in trips:
		trips = response[u"trips"]
		if u"tripOption" in tripOption:
			tripOption = trips[u"tripOption"]
			if len(tripOption) > 0:
				firstOption = tripOption[0]
				if u'saleTotal' in saleTotal:
					saleTotal = firstOption[u'saleTotal']
	                return float(re.search(r'[\d.]+', saleTotal).group())
	return -1


def make_request(origin, destination, outbounddate="2017-02-17", returndate="2017-02-19"):
	# Build one request
	passengers = { "kind": "qpxexpress#passengerCounts", "adultCount": 1 }

	outboundflight = { "kind": "qpxexpress#sliceInput", "origin": origin, "destination": destination, "date": outbounddate }
	returnflight = { "kind": "qpxexpress#sliceInput", "origin": destination, "destination": origin, "date": returndate }
	slicelist = [outboundflight, returnflight]

	solutions = 1

	request = { "passengers": passengers, "slice": slicelist, "solutions": solutions }

	# Make request
	headers = { "Content-Type": "application/json" }
	payload = { "key": key }
	data = { "request": request }
	r = requests.post(searchurl, headers=headers, params=payload, json=data)

	# Parse result
	if r.status_code != 200:
		print origin, "= request failed with status", r.status_code
	return r.json()


def main():
	for dest, destairports in destinations.iteritems():
		print "Prices for flights to", dest
		total_price = 0.0
		for orig, origairports in origins.iteritems():
			min_price = float("inf")
			for destination in destairports:
				for origin in origairports:
					response = make_request(origin, destination)
					price = get_price(response)
					if price > 0.0 and price < min_price:
						min_price = price
			print orig, "=", ("%.2f" % min_price)
			total_price += min_price
		print "Total price =", ("%.2f" % total_price),"\n"


if __name__ == '__main__':
	read_key()
	main()
