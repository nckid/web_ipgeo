# web_ipgeo

DIYish IP GeoLocation tool

Uses http://software77.net/geo-ip/multi-lookup/

...since it allows a large number of lookups

...2000 ips at a time


#####UPDATES:

- Removed unneeded loop for args and added default values (Thanks Mike)

- Fixed IO and OS Errors in clean() by adding exception handling

- Corrected top comments, since the site doesn't allow unlimited lookups


#####TO-DO:

- Single IP lookups

- Verbose switch

- Progress bar


######example without switch:

	python web_ipgeo.py
	

######example with custom output switch:

	python web_ipgeo.py -o ip_geo.txt
	

######example with both switches:

	python web_ipgeo.py -i my_ips.txt -o ip_geo.txt
	

_UNTESTED ON WINDOWS_

