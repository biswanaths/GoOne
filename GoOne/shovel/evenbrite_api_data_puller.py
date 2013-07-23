import time
import datetime
import json 
import requests
import sys
import calendar
from shovel import task

json_object = []
no_of_days = 10
day_map = {"mon":0,"tue":1,"wed":2,"thu":3,"fri":4,"sat":5,"sun":6}
period_map = {"first":0,"second":1,"third":2,"fourth":3,"fifth":5,"last":-1}

@task
def eventbrite_extractor(city_ids):
	api_key = 'U2WO5RH3T3XPZBBMAH'
	paging_size = 10
	baseurl = "https://www.eventbrite.com/json/event_search?app_key=%s&max=%s" % (api_key,paging_size)
	now_date = datetime.datetime.now()
	global no_of_days
	date_query_string = "&date=%s %s" % ((now_date + datetime.timedelta(1)).strftime("%Y-%m-%d"),(now_date + datetime.timedelta(no_of_days)).strftime("%Y-%m-%d"))
	urlformat = baseurl + date_query_string + "&city=%s" 
	start_urls = [ urlformat % city_id for city_id in open(city_ids)]
	print 'Pulling data - %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

	for url in start_urls:
		page_no = 1
		no_events = 0
		total_events = sys.maxint
		paging_url = (url + "&page=%s") % page_no 	
               	json_data = get_json_from_url(paging_url)
		no_events,total_events = get_summary(json_data)
		if no_events == 0:
			return
		dump_json_data(json_data,no_events)		

		while no_events < total_events:
			page_no+=1
			paging_url = (url + "&page=%s") % page_no
			json_data = get_json_from_url(paging_url)
	                num_showing,total_events = get_summary(json_data)
			no_events+=num_showing
			dump_json_data(json_data, num_showing)
		
		global json_object
		with open('eventbrite_events.json', 'w') as outfile:
  			json.dump(json_object, outfile)

def get_json_from_url(url):
	response = requests.get(url)
        return json.loads(response.content)

def get_summary(json_data):
	try:
        	total_events = json_data["events"][0]["summary"]["total_items"]
		num_showing = json_data["events"][0]["summary"]["num_showing"]
		return num_showing, total_events
        except Exception, ex:
		return 0,0

def dump_json_data(json_data,no_events):
	global json_object
	for i in range(1,no_events+1):
		json_string = {}
		json_string["name"] = json_data["events"][i]["event"]["title"]
		json_string["category"] = json_data["events"][i]["event"]["category"]
		json_string["organizer"] = json_data["events"][i]["event"]["organizer"]["name"]
		json_string["latitude"] = json_data["events"][i]["event"]["venue"]["latitude"]
		json_string["longitude"] = json_data["events"][i]["event"]["venue"]["longitude"]
		json_string["location"] = json_data["events"][i]["event"]["venue"]["city"]
		json_string["place"] = json_data["events"][i]["event"]["venue"]["name"]
		json_string["region"] = json_data["events"][i]["event"]["venue"]["region"]
		json_string["address"] = json_data["events"][i]["event"]["venue"]["address"]+","+json_string["place"]+","+json_string["location"]+","+json_string["region"]
		repeats = json_data["events"][i]["event"]["repeats"]
		if repeats == "no":
			json_string["timestamp"] = get_unix_timestamp(json_data["events"][i]["event"]["start_date"],"%Y-%m-%d %H:%M:%S")
			json_object.append(json_string)
		else:
			repeat_schedule = json_data["events"][i]["event"]["repeat_schedule"]	
			if "custom" in repeat_schedule:
                        	json_string["timestamp"] = get_unix_timestamp(json_data["events"][i]["event"]["start_date"],"%Y-%m-%d %H:%M:%S")
                        	json_object.append(json_string)
			else:
				for timestamp in get_timestamp_array(repeat_schedule,json_data["events"][i]["event"]["start_date"]):
					json_string["timestamp"] = timestamp
					json_object.append(json_string)

def get_unix_timestamp(date_string,format):
	return int(time.mktime(datetime.datetime.strptime(date_string, format).timetuple()))

def get_timestamp_array(repeat_schedule, start_date):
	timestamp_array = []
	global no_of_days
	now_datetime = datetime.datetime.now()
	start_datetime = datetime.datetime.strptime(start_date,"%Y-%m-%d %H:%M:%S")
	begin_period = now_datetime if now_datetime > start_datetime else start_datetime
	split_schedule = repeat_schedule.split("-")
	
	last_datetime = now_datetime + datetime.timedelta(no_of_days)
	end_datetime = datetime.datetime.strptime(split_schedule[-1],"%m/%d/%Y")
	end_period = end_datetime if end_datetime < last_datetime else last_datetime
	date = datetime.datetime.combine(begin_period.date(), start_datetime.time())
	
	if "daily" in repeat_schedule:
		while date < end_period:
			timestamp_array.append(int(time.mktime(date.timetuple())))	
			date = date + datetime.timedelta(1)

	elif "weekly" in repeat_schedule:
		schedule =  split_schedule[-2].split(",")
		while date < end_period:
			if schedule[date.weekday()] == "Y":
				 timestamp_array.append(int(time.mktime(date.timetuple())))
			date = date + datetime.timedelta(1)	

	else:
		if "/" in split_schedule[-2]:
			period,day = split_schedule[-2].split("/")
			periodic_date = get_datetime_from_day(period,day,now_datetime)	
			if periodic_date and periodic_date >= begin_period.date() and periodic_date <= end_period.date():
				date = datetime.datetime.combine(periodic_date, start_datetime.time())
				timestamp_array.append(int(time.mktime(date.timetuple())))	

		else:
			given_date = split_schedule[-2]
			periodic_date = get_datetime_from_date(given_date,now_datetime) 
			if periodic_date and periodic_date >= begin_period.date() and periodic_date <= end_period.date():
                                date = datetime.datetime.combine(periodic_date, start_datetime.time())
                                timestamp_array.append(int(time.mktime(date.timetuple())))

	return timestamp_array
					

def get_datetime_from_day(period,day,now):
	global day_map, period_map
	month_range = calendar.Calendar(0).monthdatescalendar(now.year, now.month)
	try:
		date1 = month_range[period_map[period]][day_map[day]]
		if date1.month == now.month-1 or (date1.month == 12 and now.month == 1):
			date1 = date1 + datetime.timedelta(7)
		
		if date1 < now.date():
			try:	
				month_range2 = calendar.Calendar(0).monthdatescalendar(now.year, now.month+1)
		                date2 = month_range2[period_map[period]][day_map[day]]
		                if date2.month == now.month or (date2.month == 1 and now.month == 12):
                		        date2 = date2 + datetime.timedelta(7)
				return date2
			except Exception, ex:
				return None
		return date1
	except Exception, ex:
		return None

def get_datetime_from_date(date,now):
	try:
		date1 = datetime.date(now.year, now.month, date)
		if date1 < now.date():
			date2 = datetime.date(now.year, now.month, date)
			return date2

		return date1
	except Exception, ex:
		return None			



