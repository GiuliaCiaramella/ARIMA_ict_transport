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

citiesTimezone = {"Milano": -1, 'Frankfurt':-1, 'New York City': 5}
Booking = {}
cumulative = {}
folder = os.path.dirname(os.path.abspath(__file__))

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
            "week": {"$divide": [{"$subtract": ["$init_time", 1506801599]}, 604800]}
            }
        }
    ])
    Booking[city] = {}
    cumulative[city] = {}

    for item in resultQuery:
        bookingDuration = item["durationBook"]
        bookingWeek = int(item["week"]) + 1
        if bookingWeek == 5:
            bookingWeek = 4

        if 'tot' not in Booking[city]:
            Booking[city]['tot'] = []

        Booking[city].setdefault(bookingWeek, []).append(bookingDuration)
        Booking[city]['tot'].append(bookingDuration)

    fig = plt.figure(city)

    bins = np.arange(np.floor(min(Booking[city]['tot'])), np.ceil(max(Booking[city]['tot'])))
    values, base = np.histogram(Booking[city]['tot'], bins=bins, density=1)
    #bins = np.arange(np.floor(min(Booking[city]['tot'])), 1000)
    #plt.hist(Booking[city]['tot'], bins=bins)
    print('tot', city, np.mean(Booking[city]['tot']))
    plt.show()

    cumulative[city]['tot'] = []
    cumulative[city]['tot'] = np.cumsum(values)

    plt.plot(base[:-1], cumulative[city]['tot'], 'b*', label="Month")
    plt.xlim(-10, 100)
    for j in [1, 2, 3, 4]:
        bins = np.arange(np.floor(min(Booking[city][j])), np.ceil(max(Booking[city][j])))
        values, base = np.histogram(Booking[city][j], bins=bins, normed=True, density=1)
        if j not in cumulative[city]:
            cumulative[city][j] = []
        print('week :', j, 'city: ', city, 'mean: ', np.mean(Booking[city][j]))
        cumulative[city][j] = np.cumsum(values)

        plt.plot(base[:-1], cumulative[city][j], label="Week" + str(j), linewidth=1)
        plt.xlabel('Minutes')
        plt.legend()

    plt.title("CDF booking/parking duration in "+city+", October 2017")
    fig.savefig(folder + '/cdf ' + city + '-parking.pdf')
    plt.legend(prop={'size': 20})
    plt.close(fig)
