import pymongo as pm
import pprint as pp
import numpy as np
import matplotlib.pyplot as plt

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

# query = {"city":"Torino", "init_fuel": {"$gt":0}} # query about cars in torino with init fuel greater that 0
# result = Car2goPermanentBook.find(query).count(True) # searching for vehicles in Turin with fuel greater than 14
#
# # ---------How many documents are present in each collection?-----------------------------------------------1
# r = Car2goPermanentBook.count()
# print(r)
#
# r = Car2goActiveBook.count()
# print(r)
#
# r = Car2goPermanentPark.count()
# print(r)
#
# r = Car2goActivePark.count()
# print(r)
#
# r = enjoyActivePark.count()
# print(r)
#
# r = enjoyActiveBook.count()
# print(r)
#
# r = enjoyPermanentPark.count()
# print(r)
#
# r = enjoyPermanentBook.count()
# print(r)
#
# # -----------For which cities the system is collecting data--------------------------------------------------3
# car2goCities = Car2goPermanentBook.distinct("city")
# enjoyCities = enjoyPermanentBook.distinct("city")
# print(car2goCities)
# print(enjoyCities)

# --------When the collection started? ended?----------------------------------------------------------------4
# started:
# cursor_start = Car2goPermanentBook.find({}, {"init_time":1, "init_date":1, "_id":0}).sort("init_time", pm.ASCENDING)
# pprint(cursor_start[0])
# # result: "init_time" : 1481650703, ISODate("2016-12-13T18:38:23.000Z") 65 macchine
#
# # ended:
# cursor_end= Car2goPermanentBookpermanentBook.find({}, {"init_time":1, "init_date":1, "_id":0}).sort("init_time",pm.DESCENDING)
# pprint(cursor_end[0])
# result: "init_time" : 1517404293, ISODate("2018-01-31T08:11:33.000Z")


# ---------------What about the timezone of the timestamps?--------------------------------------------------5
# the timezone is GTM (Greenwitch)


# --------How many cars are available in each city?----------------------------------------------------------6
# quale database?
# resultFr = permanentBook.find({"city":"Frankfurt"}).count()
# resultMil = permanentBook.find({"city":"Milano"}).count()
# resultNy = permanentBook.find({"city": "New York City"}).count()
# print("Frankfurt, Milano, New York City: ", resultFr, resultMil, resultNy)


# ------How many bookings recorded on the December 2017 in each city?----------------------------------------7
# result: Milano: 213364; Frankfurt:53944; NYC:74325 for newyork 5 ore indietro! calcolo del timestamp
# locale per 1/12/17 e 31/12/17 e poi per new york ricalcolo tenendo conto del fuso orario di 5 ore indietro
# query = {"city":"New York City", "init_time":{
#             "$gte": 1512068399, # 1/12/17 at 00:00:00; per new York usa --> 1512068399
#             "$lte": 1514743199 # 31/12/2017 at 23:59:59; per New York usa --> 1514743199
#             }
#         }
# result = permanentBook.find(query).count()
# print(result)


# --------How many bookings have also the alternative transportation modes recorded in each city? -----------8
# database key: "public_transport" , "walking"
# cursors = permanentBook.find({
#     "$and": [
#         {"city":"Milano"},{"$or":[{"walking.duration": {"$ne":-1}}, {
#         "public_transport.duration": {"$ne":-1}
#                 }
#             ]
#         }
#     ]}).count()

# second parameter in find(): {"walking":1, "_id":0, "public_transport":1},
#useful if you want to check duration of walking and public transpor

#print(cursors)
# results: Milano:728653, Frankfurt: 0, New York City: 0

# --------How many bookings have also the alternative transportation modes recorded in each city? -----------8
# database key: "public_transport" , "walking"
# cursors = permanentBook.find({
#     "$and": [
#         {"city":"Milano"},
#         {"$or":[
#             {"walking.duration": {"$ne":-1}}, {"public_transport.duration": {"$ne":-1}}
#         ]
#         }
#     ]}).count()
#
# print(cursors)
# results: Milano:728653, Frankfurt: 0, New York City: 0



###############################################################################
# -------------------------------STEP 2----------------------------------------
###############################################################################

# -------------Derive the CDF of booking/parking duration, and plot them.----------------------------------1-1c
# filter: october 2017
# for New york: first_oct_day=1506801600, last_oct_day = 1509494400
# for Milano-Frankfurt: first_oct_day: 1506816000 last_oct_day:1509408000
first_oct_day = 1506816000
last_oct_day = 1509408000
city = "Frankfurt"
book_duration = []
book_week_1 = []
book_week_2 = []
book_week_3 = []
book_week_4 = []
book_week_5 = []

for item in Car2goPermanentBook.aggregate([
    {"$match": # stage 1 of the pipeline
         {"$and": [{"city":city},  {"init_time": {"$gte":first_oct_day}}, {"init_time": {"$lte": last_oct_day}}]}
    },
    {"$project":{
        "_id":0,
        "durationBook": {
            "$divide": [{"$subtract":["$final_time", "$init_time"]}, 60]
        },
        "week":{
            "$divide": [{"$subtract":["$init_time", 1506801599]}, 604800] # week returns the number of week (1,2,3,4) in october
        }
    }
    },
]):
    book_duration.append(item["durationBook"])
    if int(item["week"]) == 1:
        book_week_1.append(item["durationBook"])
    elif int(item["week"]) == 2:
        book_week_2.append(item["durationBook"])
    elif int(item["week"]) == 3:
        book_week_3.append(item["durationBook"])
    elif int(item["week"]) == 4:
        book_week_4.append(item["durationBook"])
    else:
        book_week_5.append(item["durationBook"])


book = sorted(book_duration)

park_duration = []
park_week_1 = []
park_week_2 = []
park_week_3 = []
park_week_4 = []
park_week_5 = []

for item in Car2goPermanentPark.aggregate([
    {"$match": # stage 1 of the pipeline
         {"$and": [{"city":city}, {"init_time": {"$gte":first_oct_day}}, {"init_time":{"$lte":last_oct_day}}]}
    },
    {"$project":{ # stage 2
         "_id":0,
         "durationPark":{
             "$divide":[{"$subtract":["$final_time", "$init_time"]}, 60]
         },
         "week":{
            "$divide": [{"$subtract":["$init_time", 1506801599]}, 604800] # week returns the number of week (1,2,3,4) in october
         }
    }
    }
]):
    park_duration.append(item["durationPark"])
    if int(item["week"]) == 1:
        park_week_1.append(item["durationPark"])
    elif int(item["week"]) == 2:
        park_week_2.append(item["durationPark"])
    elif int(item["week"]) == 3:
        park_week_3.append(item["durationPark"])
    elif int(item["week"]) == 4:
        park_week_4.append(item["durationPark"])
    else:
        park_week_5.append(item["durationPark"])


park_week_1=sorted(park_week_1)
park_week_2=sorted(park_week_2)
park_week_3=sorted(park_week_3)
park_week_4=sorted(park_week_4)
park_week_5=sorted(park_week_5)

book_week_1=sorted(book_week_1)
book_week_2=sorted(book_week_2)
book_week_3=sorted(book_week_3)
book_week_4=sorted(book_week_4)
book_week_5=sorted(book_week_5)

p1 = 1. * np.arange(len(park_week_1))/(len(park_week_1) - 1)
b1 = 1. * np.arange(len(book_week_1))/(len(book_week_1) - 1)
p2 = 1. * np.arange(len(park_week_2))/(len(park_week_2) - 1)
b2 = 1. * np.arange(len(book_week_2))/(len(book_week_2) - 1)
p3 = 1. * np.arange(len(park_week_3))/(len(park_week_3) - 1)
b3 = 1. * np.arange(len(book_week_3))/(len(book_week_3) - 1)
p5 = 1. * np.arange(len(park_week_5))/(len(park_week_5) - 1)
b5 = 1. * np.arange(len(book_week_5))/(len(book_week_5) - 1)
p4 = 1. * np.arange(len(park_week_4))/(len(park_week_4) - 1)
b4 = 1. * np.arange(len(book_week_4))/(len(book_week_4) - 1)



figWeek = plt.figure()
# plot cdf
plt.xscale("log")
plt.plot(park_week_1, p1, label="Book, w1", color="grey", alpha=0.8, linestyle="-")
plt.plot(book_week_1, b1, label="Park, w1", color="grey", alpha=0.8, linestyle="-.")
plt.plot(park_week_2, p2, label="Book, w2", color="blue", alpha = 0.8, linestyle="-")
plt.plot(book_week_2, b2, label="Park, w2", color="blue", alpha = 0.8, linestyle="-.")
plt.plot(park_week_3, p3, label="Book, w3", color="pink", alpha = 0.8, linestyle="-")
plt.plot(book_week_3, b3, label="Park, w3", color="pink", alpha = 0.8, linestyle="-.")
plt.plot(park_week_4, p4, label="Book, w4", color="red", alpha = 0.8, linestyle="-")
plt.plot(book_week_4, b4, label="Park, w4", color="red", alpha = 0.8, linestyle="-.")
plt.plot(park_week_5, p5, label="Book, w5", color="green", alpha = 0.8, linestyle="-")
plt.plot(book_week_5, b5, label="Park, w5", color="green", alpha = 0.8, linestyle="-.")


plt.legend()
plt.xlabel("Duration [min]")
plt.title( "CDF booking/parking duration in "+city+", October 2017", loc='center')
plt.grid(True, which='minor', axis="x")
plt.show()


fig = plt.figure()

park_duration = sorted(park_duration)
book_duration = sorted(book_duration)
p = 1. * np.arange(len(park_duration))/(len(park_duration) - 1)
b = 1. * np.arange(len(book_duration))/(len(book_duration) - 1)

plt.plot(park_duration, p, label="Book")
plt.plot(book_duration, b, label="Park")
plt.xscale("log")
plt.legend()
plt.xlabel("Duration [min]")
plt.title( "CDF booking/parking duration in "+city+", October 2017", loc='center')
plt.grid(True, which='minor', axis="x")
plt.show()

city= city.replace(" ", "")
#figWeek.savefig(city+'Weeks.pdf')
#fig.savefig(city+'.pdf')
