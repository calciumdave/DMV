import datetime
from decimal import Decimal
from operator import add

def str2date(s):
    ''' convert string s of format u'2014-04-10' to datetime.date format '''
    return datetime.date(*map(int, s.split('-')))
    
def datefields(d):
    '''extract year, month, day, week information in a list'''
    return [d.year, d.month, d.day, d.weekday()+1] 

def spendMeter(rdd, day0 = None, day1 = None, category=None, subcategory=None, period = 'Day'):
    ''' calculate the current moven spend meter from an rdd (spack database) rdd0 is the spark data base, each element in the format of [u'2014-04-10', u'Account Transfers', u'Transfer', u'1.74', u'ODP TRANSFER FROM SAVINGS 000002', u'Credit'], category is the category, if none will summarize over all categories, subcategory follow the same. the function returns day-spending over the period of time; day0 and day1 are starting and ending dates, in datetime.date format, period reserved for further.'''
    if category or category == '': ## empty field exist
       rdd = rdd.filter(lambda x: x[1] == category)
    if subcategory or subcategory == '': ## empty subcategory field, not none
       rdd = rdd.filter(lambda x:x[2] == subcategory)
    ## convert to date, use the key 
    rdd = rdd.map(lambda x: (str2date(x[0]) , Decimal(x[3]) ) )
    if day0:
       rdd = rdd.filter(lambda x: x[0]>=day0)
    if day1:
       rdd = rdd.filter(lambda x: x[0]<=day1)
    
    D = {'year':0, 'month':1, 'day':2, 'week':3}
    Nfield = D.get(period.lower(),1)
    
    ## convert to month unit if asked by user
    if Nfield == 1: ## monthly spending is studied
        rdd = rdd.map(lambda x: (datetime.date(x.year, x.month, 1), x[1]) )
        
    ## sum up spending per every day or per every month, no year option yer
    rdd = rdd.reduceByKey(add)
    
    ## calculate average per day, per weekday, or per month over period of time     
    rdd1 = rdd.map(lambda x: (datefields(x[0])[Nfield], (1, x[1])))
    result = rdd1.reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1])).map(lambda x: (x[0], x[1][1]/x[1][0]).collect()
    
    ## sort by day, weekday, or month (Monday = 0)
    s_result = sorted(result, key=lambda x:x[0])
    
    ## calculate accumulative spending in a month, week, or year
    for i in range(1,len(s_result)):
        s_result[i] = (s_result[i][0], s_result[i][1]+s_result[i-1][1])
    return s_result
