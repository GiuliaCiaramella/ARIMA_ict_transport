import pymongo as pm
import pprint as pp
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Proj, transform
import datetime, time
import os
import csv
import pandas as pn

#Here we set the client
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
         authSource = 'carsharing', tlsAllowInvalidCertificates=True)

#Here we access to a specific collection of the client
db = client['carsharing']
db.authenticate('ictts', 'Ictts16!', mechanism='SCRAM-SHA-1') #authentication

#Collection for Car2go
Car2goPermanentBook = db['PermanentBookings']
Car2goPermanentPark = db['PermanentParkings']
Car2goActiveBook = db['ActiveBookings']
Car2goActivePark = db['ActiveParkings']

#Collection for enjoy
enjoyPermanentBook = db['enjoy_PermanentBookings']
enjoyPermanentPark = db['enjoy_PermanentParkings']
enjoyActiveBook = db['enjoy_ActiveBookings']
enjoyActivePark = db['enjoy_ActiveBookings']


ict_PermanentBook = db['ictts_PermanentBookings']
ict_enjoy_PermanentBook = db['ictts_enjoy_PermanentBookings']

first_oct_day = time.mktime((datetime.datetime(2017, 10, 1, 0, 0)).timetuple())
last_oct_day = time.mktime((datetime.datetime(2017, 11, 1, 0, 0)).timetuple())
folder = os.path.dirname(os.path.abspath(__file__))

city ="Milano"
citiesTimezone = -1
addTime = citiesTimezone*60*60

resultQuery = Car2goPermanentBook.aggregate([
        {"$match":  # stage 1 of the pipeline
             {"$and": [{"city": city},
                       {"init_time": {"$gte": first_oct_day + addTime}},
                       {"init_time": {"$lte": last_oct_day + addTime}}
                       ]}
        }, {"$project": {
            "_id": 0,
            "durationPark": {"$divide": [{"$subtract": ["$final_time", "$init_time"]}, 60]},
            "hourUnix": {"$floor": {"$divide": ["$init_time", 3600]}},
            "init_time":1,
            "latOrigin": {"$arrayElemAt": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]}, 1]},
            "lonOrogin": {"$arrayElemAt": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]}, 0]},
            "latDest": {"$arrayElemAt": [{"$arrayElemAt": ["$origin_destination.coordinates", 1]}, 1]},
            "lonDest": {"$arrayElemAt": [{"$arrayElemAt": ["$origin_destination.coordinates", 1]}, 0]},
            "moved": {"$ne": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]},
                              {"$arrayElemAt": ["$origin_destination.coordinates", 1]}]},
            "hourOfDay": {"$hour": "$final_date"},
            "weekend": {
                "$switch": {
                    "branches": [
                        {
                            "case": {
                                "$and": [ # $dayOfWeek : Returns the day of the week for a date as a number between 1 (Sunday) and 7 (Saturday)
                                    {"$eq": [{"$dayOfWeek": "$final_date"}, 6]},
                                    {"$gte": [{"$hour": "$final_date"}, 19]}
                                ]
                            },
                            "then": True
                        },
                        {
                            "case": {
                                "$or": [
                                    {"$eq": [{"$dayOfWeek": "$final_date"}, 1]},
                                    {"$eq": [{"$dayOfWeek": "$final_date"}, 7]}
                                ]
                            },
                            "then": True
                        }
                    ],
                    "default": False
                }
            }
            }
        },{"$match":
                  {"$and": [{"moved": True},
                            {"durationPark": {"$gte": 5}},
                            {"durationPark": {"$lte": 180}},
                            {"hourUnix": {"$lte": 418742}},
                            {"hourUnix": {"$gt": 418706}}
                            ]}
        },{"$project": {"moved": 0}}, {"$sort": {
              "_id.hourUnix": 1
              }
         }
    ], allowDiskUse=True)
inProj = Proj("+init=EPSG:4326", preserve_units=False)
outProj = Proj("EPSG:3003")

resultQuery = list(resultQuery)
with open('BookingCordinades1.csv', 'w') as outfile:
    fields = ['hourUnix', 'durationPark', 'init_time',
              'latOrigin', 'lonOrogin', 'latDest', 'lonDest', 'hourOfDay', 'weekend']
    write = csv.DictWriter(outfile, fieldnames=fields)
    write.writeheader()
    for item in resultQuery:
        item["lonOrogin"], item["latOrigin"] = transform(inProj, outProj, item["lonOrogin"], item["latOrigin"])
        item["lonDest"], item["latDest"] = transform(inProj, outProj, item["lonDest"], item["latDest"])
        write.writerow(item)




