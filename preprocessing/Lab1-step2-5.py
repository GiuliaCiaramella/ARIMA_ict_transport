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

citiesTimezone = {"Milano": -1}

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
            "hourInDay": {"$hour": "$init_date"},
            "day": {"$dayOfMonth": "$init_date"},
            "moved": {"$ne": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]},
                              {"$arrayElemAt": ["$origin_destination.coordinates", 1]}]}
            }
        },{"$match":  # stage 1 of the pipeline
                                  {"$and": [{"moved": True},
                                            {"durationBook": {"$gte": 5}},
                                            {"durationBook": {"$lte": 180}}
                                            ]}
        }, {"$sort": {
              "day": 1,
              "hourInDay": 1
              }
         }
    ])
    booking = {}
    avg = []
    med = []
    std = []
    per = []
    for item in resultQuery:
        day = item["day"]
        durationBooking = item["durationBook"]
        if day not in booking:
            booking[day] = []
        booking[day].append(float(durationBooking))

    for key in booking.keys():
        value = booking[key]
        avg.append(np.mean(value))
        med.append(np.median(value))
        std.append(np.std(value))
        per.append(np.percentile(value, 80))

    fig = plt.figure(1, figsize=(10, 5))
    plt.title(city)
    plt.xlabel("Days")
    plt.ylabel("Duration")
    plt.xlim(1, 31)
    x = np.linspace(1, 31, len(avg))
    plt.grid(True)
    plt.plot(x, avg, label="Avg")
    plt.plot(x, med, label="Med")
    plt.plot(x, std, label="Std")
    plt.plot(x, per, label="per")
    plt.xticks(np.arange(32))
    plt.legend(loc=2)
    fig.show()
    fig.savefig(folder + '/med' + city + '.png')
