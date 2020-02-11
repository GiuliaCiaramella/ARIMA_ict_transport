import pymongo as pm
import pprint as pp
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-deep')
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
        {"$match":
             {"$and": [{"city": city},
                       {"init_time": {"$gte": first_oct_day + addTime}},
                       {"init_time": {"$lte": last_oct_day + addTime}},
                       {"walking.duration": {"$ne": -1}}
                       # {"public_transport.duration": {"$ne": -1}}
                       ]}
         }, {"$project": {
            "_id": 0,
            "durationBook": {"$divide": [{"$subtract": ["$final_time", "$init_time"]}, 60]},
            "interval": {"$floor": {"$divide": [{"$subtract": ["$final_time", "$init_time"]}, 300]}},
            "day": {"$dayOfMonth": "$init_date"},
            "moved": {"$ne": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]},
                              {"$arrayElemAt": ["$origin_destination.coordinates", 1]}]},
            "WalkingDuration": {"$divide": ["$walking.duration", 60]},
            "publicDuration": {"$divide": ["$public_transport.duration", 60]}
        }
        },{"$match":
                                  {"$and": [{"moved": True},
                                            {"durationBook": {"$gte": 5}},
                                            {"durationBook": {"$lte": 180}}
                                            ]}
        }
        # , {"$group": {
        #     "_id": {"interval": "$interval"},
        #     "totalBooking": {"$sum": 1}}
        # }, {"$sort": {
        #     "_id.interval": 1
        # }
        # }
    ])

    bookingDuration = []
    walkingDuration = []
    publicDuration = []
    for item in resultQuery:
        durationBooking = item["durationBook"]
        durationWalking = item["WalkingDuration"]
        durationPublic = item["publicDuration"]
        bookingDuration.append(durationBooking)
        walkingDuration.append(durationWalking)
        publicDuration.append(durationPublic)

    bins = np.arange(5, 100, 5)
    fig = plt.figure(1)
    plt.figure(1, figsize=(10, 5))
    plt.title(city + " histo")
    plt.xlabel("Duration[min]")
    plt.ylabel("Number of Bookings")
    plt.xticks(bins)
    plt.grid(True)
    # plt.hist([walkingDuration, publicDuration], bins, label=["# booking vs walking Duration", "# booking vs public Transport Duration"])
    # plt.hist(walkingDuration, bins, label="# booking vs walking Duration")
    plt.hist(publicDuration, bins, label="# booking vs public Transport Duration")
    plt.legend()
    fig.show()
    fig.savefig(folder + '/histoPublic.pdf')