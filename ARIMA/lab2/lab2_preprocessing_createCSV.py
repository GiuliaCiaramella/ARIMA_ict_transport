import pymongo as pm
import pprint as pp
import numpy as np
import matplotlib.pyplot as plt
import datetime, time
import pandas as pd
import os

#Here we set the client
client = pm.MongoClient('bigdatadb.polito.it', ssl=True,
         authSource = 'carsharing', tlsAllowInvalidCertificates=True)

#Here we access to a specific collection of the client
db = client['carsharing']
db.authenticate('ictts', 'Ictts16!', mechanism='SCRAM-SHA-1') #authentication

#Collection for Car2go
permanentBook = db['PermanentBookings']
permanentPark = db['PermanentParkings']
activeBook = db['ActiveBookings']
activePark = db['ActiveParkings']

first_oct_day = time.mktime((datetime.datetime(2017, 10, 1, 0, 0)).timetuple())
last_oct_day = time.mktime((datetime.datetime(2017, 11, 1, 0, 0)).timetuple())
folder = os.path.dirname(os.path.abspath(__file__))

citiesTimezone = {"Milano": -1, "Frankfurt": -1, "New York City": 5}

for city in citiesTimezone:
    addTime = citiesTimezone[city]*60*60
    resultQuery = permanentBook.aggregate([
        {"$match":
             {"$and": [{"city": city},
                       {"init_time": {"$gte": first_oct_day + addTime}},
                       {"init_time": {"$lte": last_oct_day + addTime}}
                       ]}
        }, {"$project": {
            "_id": 0,
            "durationBook": {"$divide": [{"$subtract": ["$final_time", "$init_time"]}, 60]},
            "hour": {"$floor": {"$divide": ["$init_time", 3600]}},
            "moved": {"$ne": [{"$arrayElemAt": ["$origin_destination.coordinates", 0]},
                              {"$arrayElemAt": ["$origin_destination.coordinates", 1]}]}
            }
        },{"$match":
                  {"$and": [{"moved": True},
                            {"durationBook": {"$gte": 5}},
                            {"durationBook": {"$lte": 180}}
                            ]}
        },
        # {"$project":{
        #     "durationBook":1,
        #     "hour":1,
        #     "city":1
        # }
        {"$group": {
              "_id":  "$hour",
              "totalBooking": {"$sum": 1}}
         },{"$sort": {
              "_id.hourUnix": 1
              }
         }
    ])
    # fitting missing data: if in a certain hour there are no rentals, mongodb does not return 0.
    # so we create manually the 0, writing the hour that is missing because we want to have continuous
    # time series
    # print(len(resultQuery))
    list_ = list(resultQuery)
    df = pd.DataFrame(data=list_)
    df.columns = ['hour', 'rentals']
    df = df.sort_values(by=['hour'])
    for i in range(len(df)):
        Hour = df.iloc[i]['hour']
        NextHour = df.iloc[i+1]['hour']
        if Hour == NextHour - 1:
            pass
        else:
            dfA = df.iloc[:i+1, ]
            dfB = df.iloc[i+1:, ]
            new_row = {'hour': Hour+1, 'rentals': 0}
            df = dfA.append(new_row,ignore_index=True).append(dfB).reset_index(drop=True)

    df.to_csv(city + '.csv', index=False)