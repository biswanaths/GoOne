import time
import datetime

class TimestampUtil(object):

 	month_map = {"January":1,"February":2,"March":3,"April":4,"May":5,"June":6,"July":7,"August":8,"September":9,"October":10,"November":11,"December":12}

	@staticmethod
 	def get_unix_timestamp(year,month,day,hour=0,minute=0,second=0):
 	 	dt = datetime.datetime(year,month,day,hour,minute,second)
		return int(time.mktime(dt.timetuple()))

	@staticmethod
	def get_month(month):
  		return TimestampUtil.month_map[month]

	@staticmethod
	def get_time(time_value,period):
 		hour_value = 12 if "PM" in period else 0 
		hour_string = time_value.split(":")
		return int(hour_string[0])+hour_value,int(hour_string[1])
