import os
import datetime

filepath = '/home/dq/moven'
filename = 'Sample Data.txt'
fname = os.path.join(filepath,filename)

## load file into spark
rdd0 = sc.textFile(fname)

## number of records
rdd0.count()
>>> 1837

## sample the first line of data
rdd0.take(1)

>>>[u'"2014-04-10;""Account Transfers"";""Transfer"";1.74;""ODP TRANSFER FROM SAVINGS 000002"";""Credit"""']

## define query condition
Location = u'BLOOMINGT' ## locations contains "BLOOMINGT"
Store = u'KILROY BAR AND GRILL'

## convert string to list
rdd1 = rdd0.map(lambda x: x.replace('"','').split(';'))
rdd1.take(1)
>>>[[u'2014-04-10', u'Account Transfers', u'Transfer', u'1.74', u'ODP TRANSFER FROM SAVINGS 000002', u'Credit']]

## filter out the target content
rdd2 = rdd1.filter(lambda x: Location in x[4] and Store in x[4])
rdd2.count()
>>>67
rdd2.take(1)
>>>[[u'2014-04-10', u'Dining Out', u'Restaurants', u'7.50', u'KILROYS BAR AND GRILL BLOOMINGTO', u'Debit']]

## make key-value pair
rdd3 = rdd2.map(lambda x: ((x[4],x[1]), (1, float(x[3])) ) )
rdd3.take(1)
>>>[((u'KILROYS BAR AND GRILL BLOOMINGTO', u'Dining Out'), (1, 7.5))]

## result aggregation
rdd4 = rdd3.reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1]) )
rdd4.collect()

## return the results, Geographic information, Store information and Category information are in the key, value contains frequency and total amount
>>>[((u'KILROYS BAR AND GRILL BLOOMINGTO', u'Dining Out'), (64, 568.0)), ((u'KILROYS BAR AND GRILL                    502 E KIRKWOO BLOOMINGTON                               US', u'Dining Out'), (3, 421.0))]

## it seems there are two different formats for transaction in the same restaurant, why?
## Could it be different payment methods? Or a software difference such as they upgraded their system for a period of time? Or the amount is different?

rdd2.map(lambda x: (x[1],x[2],x[4],x[5]) ).distinct().collect()
>>>[(u'Dining Out', u'Restaurants', u'KILROYS BAR AND GRILL BLOOMINGTO', u'Debit'), (u'Dining Out', u'', u'KILROYS BAR AND GRILL                    502 E KIRKWOO BLOOMINGTON                               US', u'Debit')]

## both are debit cards, field is mising too

## is it correlated with time and amount?
values = rdd2.map(lambda x: (int(len(x[2])>0), [x[0],float(x[3])]))
