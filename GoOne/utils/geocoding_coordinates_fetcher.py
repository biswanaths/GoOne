import requests
import json

class GeoCodingUtil(object):

	base_url = "http://maps.google.com/maps/api/geocode/json"

	@staticmethod
	def get_latlng(address):
		response = requests.get(GeoCodingUtil.base_url, params={'address':address,'sensor':"false"})
		json_data = response.json()
		if (json_data["status"] != "OK"):
			return 0,0
		return json_data["results"][0]["geometry"]["location"]["lat"],json_data["results"][0]["geometry"]["location"]["lng"]


