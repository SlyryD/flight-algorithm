import os
import pdb
import random
import re
import requests


origins = { "SEA": ["SEA"], "WAS": ["DCA", "IAD", "BWI"], "PIT": ["PIT"], "PVD": ["PVD", "BOS"], "MSP": ["MSP"], "NYC": ["LGA", "EWR", "JFK"], "DEN": ["DEN"]}
destinations = { "Colorado": ["DEN"], "Seattle": ["SEA"], "San Francisco": ["SFO", "SJC"], "LA": ["LAX"], "San Diego": ["SAN"], "Maryland": ["DCA", "IAD", "BWI"], "New York": ["LGA", "EWR", "JFK"] }


def get_key():
	key = ""
	with open("key", "r") as h:
		key = h.read().strip()
	return key


def get_price(response):
	if u"trips" in response:
		trips = response[u"trips"]
		if u"tripOption" in trips:
			tripOption = trips[u"tripOption"]
			if len(tripOption) > 0:
				firstOption = tripOption[0]
				if u'saleTotal' in firstOption:
					saleTotal = firstOption[u'saleTotal']
	                return float(re.search(r'[\d.]+', saleTotal).group())
	return -1


def make_request(origin, destination, outbounddate="2017-02-17", returndate="2017-02-19"):
	# Build one request
	searchurl = "https://www.googleapis.com/qpxExpress/v1/trips/search"

	passengers = { "kind": "qpxexpress#passengerCounts", "adultCount": 1 }

	outboundflight = { "kind": "qpxexpress#sliceInput", "origin": origin, "destination": destination, "date": outbounddate }
	returnflight = { "kind": "qpxexpress#sliceInput", "origin": destination, "destination": origin, "date": returndate }
	slicelist = [outboundflight, returnflight]

	solutions = 1

	request = { "passengers": passengers, "slice": slicelist, "solutions": solutions }

	# Make request
	headers = { "Content-Type": "application/json" }
	payload = { "key": get_key() }
	data = { "request": request }
	r = requests.post(searchurl, headers=headers, params=payload, json=data)

	# Parse result
	if r.status_code != 200:
		print origin, "= request failed with status", r.status_code

	return r.json()


def get_row(prices_dest, origs):
	for orig in origs:
		yield ("%.2f" % prices_dest[orig])


def main():
	total_prices = {}
	min_prices = {}
	prices = {}
	for dest, destairports in destinations.iteritems():
		print "Prices for flights to", dest
		min_prices[dest] = {} # Min prices for dest
		total_price = 0.0     # Total price for dest
		for orig, origairports in origins.iteritems():
			min_price = float("inf") # Min price for dest-orig pair
			for destination in destairports:
				if destination not in prices:
					prices[destination] = {} # Prices for destination
				for origin in origairports:
					if destination == origin:
						price = 0.0 # Price for destination-origin pair
					else:
						response = make_request(origin, destination)
						price = get_price(response)
						# price = random.randint(0, 100)
					if price >= 0.0 and price < min_price:
						min_price = price
					prices[destination][origin] = price
			min_prices[dest][orig] = min_price
			print orig, "=", ("%.2f" % min_price), "({})".format(",".join([origin for origin in origairports]))
			total_price += min_price
		print "Total price =", ("%.2f" % total_price),"\n"
		total_prices[dest] = total_price

	dests = [airport for lst in destinations.values() for airport in lst]
	origs = [airport for lst in origins.values()      for airport in lst]
	with open('all_flights.csv', 'w') as h:
		h.write(",{}\n".format(",".join(origs)))
		for dest in dests:
			h.write("{},{}\n".format(dest, ",".join(get_row(prices[dest], origs))))

	dests = [dest for dest in destinations.keys()]
	origs = [orig for orig in origins.keys()]
	with open('best_flights.csv', 'w') as h:
		h.write(",{},Total\n".format(",".join(origs)))
		for dest in dests:
			h.write("{},{},{}\n".format(dest, ",".join(get_row(min_prices[dest], origs)), total_prices[dest]))


if __name__ == '__main__':
	main()
