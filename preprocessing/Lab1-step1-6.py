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

janurary = time.mktime((datetime.datetime(2017, 1, 1)).timetuple())
february = time.mktime((datetime.datetime(2017, 2, 1)).timetuple())
march = time.mktime((datetime.datetime(2017, 3, 1)).timetuple())
april = time.mktime((datetime.datetime(2017, 4, 1)).timetuple())
may = time.mktime((datetime.datetime(2017, 5, 1)).timetuple())
june = time.mktime((datetime.datetime(2017, 6, 1)).timetuple())
july = time.mktime((datetime.datetime(2017, 7, 1)).timetuple())
agust = time.mktime((datetime.datetime(2017, 8, 1)).timetuple())
september = time.mktime((datetime.datetime(2017, 9, 1)).timetuple())
october = time.mktime((datetime.datetime(2017, 10, 1)).timetuple())
november = time.mktime((datetime.datetime(2017, 11, 1)).timetuple())
december = time.mktime((datetime.datetime(2017, 12, 1)).timetuple())
janurary18 = time.mktime((datetime.datetime(2018, 1, 1)).timetuple())
februray18 = time.mktime((datetime.datetime(2018, 2, 1)).timetuple())
calender = [janurary,february,march,april,may,june, july,agust,september ,october,november,december,janurary18,februray18]
calenderName = ['janurary','february','march','april','may', 'june', 'july', 'agust','september' ,'october','november','december','janurary 18']
folder = os.path.dirname(os.path.abspath(__file__))

citiesTimezone = {"Milano": -1, "Frankfurt": -1, "New York City": 5}

for city in citiesTimezone:
    lista = [0] * 13
    index = 0
    for item in calender:
        if index!=len(lista):
            a = db.PermanentBookings.distinct("plate",
                                          {"city": city, "init_time": {"$gte": calender[index],
                                                                        "$lte": calender[index+1]}})
            lista[index] = len(a)
            index += 1

    fig = plt.figure(1, figsize=(20, 10))
    plt.xticks(np.arange(13),fontsize=12,rotation=45)
    plt.grid(True, which='both')
    plt.plot(calenderName, list(lista), label=city)
    plt.xlim(-0.5, 13)
    plt.xlabel('Months')
    plt.ylabel('Total Cars')
    plt.title('Number of total car with respect to month')
    # plt.legend()
    leg = plt.legend()
    for line in leg.get_lines():
        line.set_linewidth(2.0)
fig.savefig(folder + '/Images/NumCar.pdf')