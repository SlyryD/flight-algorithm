import os
import pdb
import random
import re
import requests
import sys

from datetime import date
from datetime import timedelta


def get_dict_from_file(places_dict, places_file):
	with open(places_file, "r") as h:
		curr_key = "Unknown"
		for line in h:
			stripped_line = line.strip()
			if stripped_line == "":
				continue
			elif stripped_line[0] == '+':
				place = stripped_line[1:].strip()
				places_dict[curr_key].append(place)
			else:
				curr_key = stripped_line
				places_dict[curr_key] = []
	return places_dict


def get_origins(origins_file):
	return get_dict_from_file({}, origins_file)


def get_destinations(destinations_file):
	return get_dict_from_file({}, destinations_file)


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


def make_request(origin, destination, outbounddate, returndate):
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


def get_arguments(args):
	key_file = "key"
	origins_file = "origins.txt"
	destinations_file = "destinations.txt"
	start_date = (date.today() + timedelta(16)).strftime("%Y-%m-%d") # Magic number
	end_date = (date.today() + timedelta(20)).strftime("%Y-%m-%d") # Magic number

	i = 0
	while (i < len(args)):
		if args[i] == "-key":
			if i >= len(args) - 1:
				print_arguments_message_and_exit()
			key_file = str(args[i + 1])
			i += 1
		elif args[i] == "-origins":
			if i >= len(args) - 1:
				print_arguments_message_and_exit()
			origins_file = str(args[i + 1])
			i += 1
		elif args[i] == "-destinations":
			if i >= len(args) - 1:
				print_arguments_message_and_exit()
			destinations_file = str(args[i + 1])
			i += 1
		elif args[i] == "-start":
			if i >= len(args) - 1:
				print_arguments_message_and_exit()
			start_date = str(args[i + 1])
			i += 1
		elif args[i] == "-end":
			if i >= len(args) - 1:
				print_arguments_message_and_exit()
			end_date = str(args[i + 1])
			i += 1
		i += 1

	return (key_file, origins_file, destinations_file, start_date, end_date)


def print_arguments_message_and_exit():
	print "Unable to parse command line arguments"
	print "Valid example:"
	print "    python flights-algorithm.py -start 2017-04-28 -end 2017-04-30 -key key -origins origins.txt -destinations destinations.txt"
	sys.exit()


def main():
	# Get command line arguments
	(key_file, origins_file, destinations_file, start_date, end_date) = get_arguments(sys.argv)

	# Parse origins and destinations files
	origins = get_origins(origins_file)
	destinations = get_destinations(destinations_file)

	# Print parameters
	print "Start date = {}".format(start_date)
	print "End date = {}".format(end_date)
	print "Origins = {}".format(origins.keys())
	print "Destinations = {}".format(destinations.keys())

	# Create dictionaries to store response information (written to files in working directory)
	total_prices = {}
	min_prices = {}
	prices = {}
	responses = {}

	# Make requests for pairs of airports
	for dest, destairports in destinations.iteritems():
		print "Prices for flights to", dest
		min_prices[dest] = {} # Min prices for dest
		total_price = 0.0     # Total price for dest
		for orig, origairports in origins.iteritems():
			min_price = float("inf") # Min price for dest-orig pair
			for destination in destairports:
				if destination not in prices:
					prices[destination] = {} # Prices for destination
				if destination not in responses:
					responses[destination] = {} # Responses for destination
				for origin in origairports:
					price = 0.0
					response = "_NO_RESPONSE_"
					if destination != origin:
						response = make_request(origin, destination, start_date, end_date)
						# pdb.set_trace()
						price = get_price(response)
					if price >= 0.0 and price < min_price:
						min_price = price
					prices[destination][origin] = price
					responses[destination][origin] = response
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

	dests = [airport for lst in destinations.values() for airport in lst]
	origs = [airport for lst in origins.values()      for airport in lst]
	with open('responses.csv', 'a') as h:
		h.write("origin,destination,response\n")
		for dest in dests:
			for orig in origs:
				h.write("{},{},{}\n".format(orig, dest, str(responses[dest][orig]).replace(",", ";")))


if __name__ == '__main__':
	main()
