import pymongo as pm
import pprint as pp
import numpy as np
import matplotlib.pyplot as plt
import datetime, time
import os

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

citiesTimezone = {"Milano": -1, "Frankfurt": -1, "New York City": 5}

for city in citiesTimezone:
    addTime = citiesTimezone[city]*60*60
    resultQuery = Car2goPermanentBook.aggregate([
        {"$match":  # stage 1 of the pipeline
             {"$and": [{"city": city},
                       {"init_time": {"$gte": first_oct_day + addTime}},
                       {"init_time": {"$lte": last_oct_day + addTime}}
                       ]}
        }, {"$project": {
            "_id": 0,
            "durationBook": {"$divide": [{"$subtract": ["$final_time", "$init_time"]}, 60]},
            # week returns the number of week (1,2,3,4) in october
            "hourUnix": {"$floor": {"$divide": ["$init_time", 3600]}},
            "moved": {"$ne": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]},
                              {"$arrayElemAt": ["$origin_destination.coordinates", 1]}]}
            }
        },{"$match":  # stage 1 of the pipeline
                                  {"$and": [{"moved": True},
                                            {"durationBook": {"$gte": 5}},
                                            {"durationBook": {"$lte": 180}}
                                            ]}
        },{"$group": {
              "_id": {"hourUnix": "$hourUnix"},
              "totalBooking": {"$sum": 1}}
         },{"$sort": {
              "_id.hourUnix": 1
              }
         }
    ])
    booking = {}
    lastHourUnix = 0
    for item in resultQuery:

        hourUnix = item["_id"]["hourUnix"]
        totalBookingCount = item["totalBooking"]
        if lastHourUnix == 0:
            lastHourUnix = hourUnix - 1

        while (hourUnix - lastHourUnix) > 1:
            booking[hourUnix] = 0
            lastHourUnix += 1

        lastHourUnix = hourUnix
        booking[hourUnix] = totalBookingCount

    fig = plt.figure(1, figsize=(20, 10))
    x = np.linspace(1, 31, len(booking))
    plt.xticks(np.arange(32))
    plt.grid(True, which='both')
    plt.plot(x, list(booking.values()), label=city)
    plt.xlim(0.5, 31.5)
    plt.xlabel('Days')
    plt.ylabel('Number of Bookings')
    plt.title(' Bookings per Hour of the Day October 2017 (filtered)')
    plt.legend()
    fig.savefig(folder + '/booking-filter.pdf')
