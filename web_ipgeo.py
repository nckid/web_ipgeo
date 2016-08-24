# ---------------------------------------------------------------------------
# web_ipgeo.py
# DIYish IP GeoLocation tool
# Uses http://software77.net/geo-ip/multi-lookup/
# ...since it allows a large number of lookups
# ...2000 ips at a time
# Written by nckid, August 2016
#
# UPDATES:
# -Removed unneeded loop for args and added default values (Thanks Mike)
# -Fixed IO and OS Errors in clean() by adding exception handling
# -Corrected top comments, since the site doesn't allow unlimited lookups
#
# WANTS:
# -Single IP lookups
# -Verbose switch
# -Progress bar
# ---------------------------------------------------------------------------

# ---------------------HOW TO USE---------------------
# switches:
# -h		help
#
# -i		specify input file
# -o		specify output file
#
# default values:
# input: "ips_huge.txt"
# output: "ips_clean_geo.txt"
#
# example without switch:
# 	python web_ipgeo.py
#
# example with custom output switch:
# 	python web_ipgeo.py -o ip_geo.txt
#
# example with both switches:
# 	python web_ipgeo.py -i my_ips.txt -o ip_geo.txt
#
# UNTESTED ON WINDOWS :)
# ----------------------------------------------------

import sys
import os
import requests
import argparse
from fabric.colors import blue
from fabric.colors import green
from bs4 import BeautifulSoup as BS


def split(input_file):
	# partially stolen from stack overflow
	# splits a huge ip list into smaller pieces
	splitLen = 1999        # lines per file
	outputBase = 'output'  # output.1.txt, output.2.txt, etc.

	# this is shorthand and not friendly with memory..
	# ..on very large files, but it works.
	# THIS IS THE FILE YOU MIGHT HAVE TO CHANGE
	ips_input = open(input_file, 'r').read().split('\n')  # <-- INPUT FILE

	# initialize counter
	at = 1
	for lines in range(0, len(ips_input), splitLen):
		# first, get the list slice
		outputData = ips_input[lines:lines + splitLen]

		# next open the output file
		# join the new slice with newlines
		# write it out and close the file
		output = open(outputBase + str(at) + '.txt', 'w')
		output.write('\n'.join(outputData))
		output.close()

		# increment counter
		# this number is added to the base file name
		at += 1


def hit(ips):
	# stop script if too many IPs are loaded into function
	# should never be tripped
	# MAX 2000 IPS!
	if len(ips) > 2000:
		raise ValueError("[!] Too many IPs loaded into function...")

	# URL of lookup site
	url = "http://software77.net/geo-ip/multi-lookup/"
	# header info
	headers = {"User-Agent": "What it do?"}

	# establish a session with the site
	s = requests.Session()
	s.headers.update(headers)
	r = s.get(url)
	# parse the response
	soup = BS(r.content, "html.parser")

	# stops the script if the site has been hit too many times
	# the limit should be 250 hits every 3 hours
	if "Too many hits" in r.content:
		raise ValueError("[!] Maxed out the page...")

	elif "Too many hits" not in r.content:
		print (blue("[*] Getting token..."))
		# the token should be different for each request

		# find the hidden token (TKN) in the parsed data and load it into a variable
		token = soup.find("input", type="hidden")['value']

		# stores ips with URL encoded characters for Form Data
		# the URL encoded data is the seperator
		# the ips are the sequence
		multi_ip = "%0D%0A".join(ips)

		search_data = {
			"MULTI": multi_ip,
			"ORDER": "1",
			"CIDR_FORMAT": "1",
			"multi": "Lookup",
			"TKN": token
		}

		r = s.post(url, data=search_data)
		soup = BS(r.content, "html.parser")

		print "[:]", token
		print "[:]", r.status_code, r.url

		# SOMETHING IS CAUSING DUPLICATION ISSUES IN THE ips_sorted.txt FILE...
		# ADDED DEDUPE FEATURE IN clean() FOR NOW...

		for textarea in soup.findAll("textarea"):
			textsoup = BS(textarea.text, "html.parser")
		ips_sorted = open("ips_sorted.txt", 'a')
		ips_sorted.write(str(textsoup))
		ips_sorted.close()
	else:
		raise ValueError("[!] Weird error in hit function...")


def clean(output_file):
	# opens text file that results will dump into
	try:
		clean_geo = open(output_file, "w")  # <-- OUTPUT FILE
		ip_sorted = open("ips_sorted.txt")

		# helps keep track of ips found, while cleaning up
		lines_seen = set()

		for line in ip_sorted:
			if line.startswith("#"):  # ignore top piece of web output
				pass
			elif line not in lines_seen:  # if new, write to file
				clean_geo.write(line)
				lines_seen.add(line)
			elif line in lines_seen:  # if old, ignore
				pass
			else:
				raise ValueError("[!] Passing ValueError through...")

		ip_sorted.close()
		clean_geo.close()
	except IOError:  # catch IOError and clean up correctly
		print "[:] Script quit sooner than excepted..."
		print "[:] Cleaning up a different way now..."
		pass
	except ValueError as e:
		print e
		raise ValueError("[!] Weird error in clean function...")

	# remove the output files
	for file_found in os.listdir("./"):
		if file_found.startswith("output"):
			os.remove(file_found)

	try:
		# remove the sorted ips file
		os.remove("ips_sorted.txt")
	except OSError:  # remove output_file instead of ip_sorted.txt
		print "[:] Removing %s since it was not used..." % output_file
		os.remove(output_file)
		pass

	print (blue("[*] Cleaning done..."))


if __name__ == "__main__":
	# clear the terminal screen
	# added cls for Windows
	clear = lambda: os.system('cls' if os.name == 'nt' else 'clear')
	clear()

	# take command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"-i",
		type=str,
		help="Input file - List of IPs you want to analyze.",
		default="ips_huge.txt"
	)
	parser.add_argument(
		"-o",
		type=str,
		help="Output file - Name of file you want results saved to.",
		default="ips_clean_geo.txt"
	)
	args = parser.parse_args()

	input_file = args.i
	output_file = args.o

	print "[:] ---------------------------------------------"
	print "[:] Input: ", input_file
	print "[:] Output: ", output_file
	print "[:] ---------------------------------------------"

	# split input file into usable chunks
	print (blue("[*] Splitting the raw IP file..."))
	print "[:] Using %s for the input file..." % input_file
	split(input_file)  # <-- FEED INPUT FILE

	print (green("[*] Looking for a GeoLocation info..."))

	print (blue("[*] Hitting the site..."))
	# hit the site using split files - loop
	for file_found in os.listdir("./"):
		if file_found.startswith("output"):

			print (blue("[*] Using list %s" % file_found))

			# clear out ips array at the start
			ips = []
			# troubleshooting the ip array
			# print "[:] IP list length before..", len(ips)

			# open list, strip each line, and add to array
			with open(file_found) as f:
				for line in f:
					ips.append(line.strip('\r\n'))
			try:
				hit(ips)
				# troubleshooting the ip array
				# print "[:] IP list length after..", len(ips)
			# stop the script and clean up junk files
			except KeyboardInterrupt:
				print "[*] Script stopping..."
				print (blue("[*] Cleaning up..."))
				try:
					print "[:] Using %s for the output file..." % output_file
					clean(output_file)
				except ValueError as e:
					print e
				print (green("[*] Script End."))
				sys.exit()
			except ValueError as e:
				print e
				print (blue("[*] Cleaning up..."))
				try:
					print "[:] Using %s for the output file..." % output_file
					clean(output_file)
				except ValueError as e:
					print e

				print (green("[*] Script End."))
				sys.exit()

	# merges results and deletes output files
	print (blue("[*] Cleaning up..."))
	try:
		print "[:] Using %s for the output file..." % output_file
		clean(output_file)
	except ValueError as e:
		print e

	print (green("[*] Script End."))
	sys.exit()
