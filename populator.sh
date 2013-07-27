#!/bin/sh

cd /home/ec2-user/GoOne/GoOne
PATH=$PATH:/usr/local/bin
export PATH
echo "Starting to crawl eventful"
scrapy crawl Eventful -a city_ids=./lists/eventful.list  -t json -o /home/ec2-user/GoOne/GoOne/eventful_events.json
echo "Importing eventful to mongoDb"
mongoimport --db events --collection events --type json --file  /home/ec2-user/GoOne/GoOne/eventful_events.json --jsonArray
rm  /home/ec2-user/GoOne/GoOne/eventful_events.json

echo "Starting to crawl eventbrite"
shovel evenbrite_api_data_puller.eventbrite_extractor lists/eventbrite.list
echo "Importing eventbrite to mongoDb"
mongoimport --db events --collection events --type json --file  /home/ec2-user/GoOne/GoOne/eventbrite_events.json --jsonArray
rm  /home/ec2-user/GoOne/GoOne/eventbrite_events.json



