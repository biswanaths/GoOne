#!/bin/sh

cd /home/arjun/Desktop/GoOne
PATH=$PATH:/usr/local/bin
export PATH
echo "Starting to crawl"
scrapy crawl Eventful -a city_ids=./GoOne/location.list -t json -o  /home/arjun/Desktop/events.json
echo "Importing to mongoDb"
mongoimport --db events --collection events --type json --file  /home/arjun/Desktop/events.json --jsonArray
rm  /home/arjun/Desktop/events.json


