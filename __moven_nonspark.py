import os
import datetime
from decimal import Decimal
import itertools
import csv
import matplotlib.pyplot as plt
import numpy
from calendar import monthrange

pat = '/home/dq/moven'
filename = 'Sample Data.txt'

def strToDate(s):
    ''' convert string s of format u'2014-04-10' to datetime.date format '''
    return datetime.date(*map(int, s.split('-')))
    
def dateFields(d):
    '''extract year, month, day, week information in a list'''
    return [d.year, d.month, d.day, d.weekday()+1] 
    
def toDayNumber(d, d0 = datetime.date(2014,4,10)):
    return (d-d0).days

def lineToDays(line):
    return [toDayNumber(line[0]), line[1]]


def shapeLine(line):
    ## process each line of input into a list
    line = line.replace('"','').split(';')
    line[0] = strToDate(line[0])
    line[3] = Decimal(line[3])
    return line

def selectCategory(line, category=None, subcategory=None):
    ## return true or false based on category type of field 1 and 2
    if category is None:
        flag1 = True
    else:
        flag1 = line[1] == category
    if subcategory is None:
        flag2 = True
    else:
        flag2 = line[2] == subcategory
    return flag1 and flag2
    
def timeAndMoney(line):
    return (line[0],line[3])


def toPeriod(day, period):
    ## convert day to period time, such as a week, or 10 days
    return day%period


def toDensity(time,spend,period):
    ## convert to spending density (probability to spend unit amount of money per day)
    T = [0 for i in range(period)]
    for i in range(len(time)):
        T[time[i]] += spend[i]
    To = sum(T)
    TT = [it/To for it in T]
    return range(period), TT

def toAccumulative(time,spend):
    ## take result of toDensity and calculate pdf
    cumulative = [0 for i in spend]
    cumulative[0] = spend[0]
    for i in range(1,len(time)):
        cumulative[i] = cumulative[i-1]+spend[i]
    return time, cumulative

def KS(time, cumulative, negative = False):
    ## calculate the K-S distance of cumulative distribution to uniform distribution
    l = len(cumulative)*1.0
    delta = 1/l
    m = 0
    for i in range(len(time)):
        value = cumulative[i] - Decimal((i+1)*delta)
        if negative:
            value = - value
        m = max(m, value)
    return m

def Kuiper(time, cumulative):
    return KS(time, cumulative)+KS(time, cumulative, negative=True)
    
def periodKS(time, spend, t=45):
    ## KS distance to uniform distribution, period 3 to t days
    timeframe = range(3,t+1)
    distKS = [0 for i in timeframe]
    distKp = [0 for i in timeframe]
    for i in range(len(timeframe)):
        pe = timeframe[i]
        ctime = map(lambda x: toPeriod(x,pe), time)
        T,D = toDensity(ctime, spend, pe)
        T,C = toAccumulative(T,D)
        distKS[i] = KS(T,C)
        distKp[i] = Kuiper(T, C)
    return timeframe, distKS, distKp

def periodNormedKS(time, spend, t=45):
    ss = [Decimal(1) for i in spend]
    return periodKS(time, ss, t)            

def otrj(time,spend):
    ## id outlier based on spending amount
    m = np.mean(spend)
    sigma = np.std(spend)
    score = abs(np.array(spend) - m)/sigma  
    time = np.array(time)
    spend = np.array(spend) 
    ## the value can be discussed, or based on a table
    sig = 2.75
    return time[score<sig],spend[score<sig]
    

category = 'Travel' # 'Shopping' #'Income'
subcategory = '' # 'Paycheck'

with open(os.path.join(pat, filename)) as fid:
    data0 = [row[0] for row in csv.reader(fid.read().splitlines())]
    data1 = itertools.imap(shapeLine, data0)
    data2 = itertools.ifilter( lambda x: selectCategory(x, category=category, subcategory=subcategory), data1)
    data3 = itertools.imap(timeAndMoney, data2)
    data4 = itertools.imap(lineToDays,data3)
    
    d = [item for item in data4]
    time,spend = zip(*d)
    
    period = max(time)
    
    ctime = map(lambda x: toPeriod(x,period), time)    
    T,D = toDensity(ctime, spend, period)
    T,C = toAccumulative(T,D)  
    
    
    import numpy as np
    
    spend2 = map(float, spend)
    
    ## outlier rejection
    cctime, cspend = otrj(ctime, spend)
    
    ## periodic spending
    '''
    plt.figure()
    plt.plot(cctime,cspend,'o')
    plt.xlabel('Time')
    plt.ylabel('Spend')
    plt.title('After outlier rejection')
    
    tt, ks, kp = periodNormedKS(time, spend, 60)
    
    f = plt.figure()
    axid = f.add_subplot(111) 
    plt.plot(tt, ks,'or')
    plt.plot(tt,kp,'xb')
    plt.xlabel('Period [days]')
    plt.ylabel('KS TEST SCORE O AND KUIPER TEST SCORE X')
    plt.title('Test of transaction uniformity over given period')

    ff = plt.figure()
    axid2 = ff.add_subplot(111)
    plt.plot(ctime,spend,'o')
    plt.xlabel('Time')
    plt.ylabel('Spend')
    plt.title('Before outlier rejection')
    plt.show()
    '''
    
    
def calcMonth(d1,d2):
    ## return the number of months between two days
    y1 = d1.year
    m1 = d1.month
    y2 = d2.year
    m2 = d2.month
    Nmon = 0
    while y1<=y2:
        Nmon+=1
        m1 += 1
        y1 += m1/13
        m1 = m1%12
        m1 = m1 or 12
        if y1==y2 and m1>m2:
            break
    return Nmon
        
def calcMonthDay(d1,d2):
    ## return month number and number of days in that month
    y1 = d1.year
    m1 = d1.month
    y2 = d2.year
    m2 = d2.month
    days = []
    mn = []
    Nmon = 0
    while y1<=y2:
        days.append(monthrange(y1,m1)[1])
        mn.append((y1,m1))
        Nmon +=1
        m1+=1
        y1+=m1/13
        m1%=12
        m1 = m1 or 12
        if y1==y2 and m1>m2:
            break
    days[0] = days[0] - d1.day + 1
    days[-1] = d2.day
    return mn, days
        
def calcMonthSpend(d):
    ## calculate (year, month) and total spending
    result = {}
    for item in d:
        key = (item[0].year, item[0].month)
        value = item[1]
        result[key] = result.get(key,0)+value
    month, spend = zip(*result.iteritems())
    return month, spend
    
    
    
         
## seasonal spending
category = 'Travel'
subcategory = None

with open(os.path.join(pat, filename)) as fid:
    data0 = [row[0] for row in csv.reader(fid.read().splitlines())]
    data1 = itertools.imap(shapeLine, data0)
    data2 = itertools.ifilter( lambda x: selectCategory(x, category=category, subcategory=subcategory), data1)
    data3 = itertools.imap(timeAndMoney, data2)
    
    d = [item for item in data3]
    time,spend = zip(*d)
    d1 = min(time)
    d2 = max(time)
    month, days = calcMonthDay(d1, d2)
    
    m2, spend = calcMonthSpend(d)
    
    averagespend = [sp/da for sp,da in zip(spend, days)]
    dates = map(lambda x: datetime.date(x[0],x[1],1), m2)
    
    dates, averagespend = otrj(dates, averagespend)
    
    sigma = np.std(averagespend)
    err = [sigma for i in averagespend]
    
    '''
    print err
    print dates
    print averagespend
    
    plt.errorbar((dates), averagespend, err, marker='o', ls='None')
    plt.xlabel('Month')
    plt.ylabel('Average Daily Spending [USD]')
    plt.title(category)
    
    plt.figure()
    plt.plot(dates, averagespend, 'o')
    plt.xlabel('Month')
    plt.ylabel('Average Daily Spending [USD]')
    plt.title(category)
    plt.show()
    '''

## within month spending

def spendMeter(time, spend):
    ## calculate spend meter, non-accumulatively
    spt = {}
    for i in range(len(time)):
        key = time[i]
        value = spend[i]
        spt[key] = spt.get(key,0)+value
    
    spendF = {}
    spendV = {}
    for key, value in spt.iteritems():
        key = key.day
        spendF[key] = spendF.get(key,0) + 1
        spendV[key] = spendV.get(key,0)+value
    print spendF
    print spendV
    for key in spendF:
        spendV[key] = spendV[key]/spendF[key] ## taking average
    day, avspend = zip(*spendV.iteritems())
    return day, avspend
    
category = 'Travel'
subcategory = None

with open(os.path.join(pat, filename)) as fid:
    data0 = [row[0] for row in csv.reader(fid.read().splitlines())]
    data1 = itertools.imap(shapeLine, data0)
    data2 = itertools.ifilter( lambda x: selectCategory(x, category=category, subcategory=subcategory), data1)
    data3 = itertools.imap(timeAndMoney, data2)
    
    d = [item for item in data3]
    time,spend = zip(*d) 
    day,avspend = spendMeter(time, spend)
    err = [np.std(avspend) for i in avspend]
    '''
    plt.errorbar(day, avspend, err, ls = 'None', marker = 'o')
    plt.xlabel('Day in month')
    plt.ylabel('Average spending per day')
    plt.title(str(category) + ':' + str(subcategory))
    plt.show()
    '''
    
    
## prediction, kernel
category = 'Payments'#'Shopping' #'Income' #'Shopping'
subcategory = ''

def mergeDay(time, spend):
    ## calculate spend meter, non-accumulatively
    spt = {}
    for i in range(len(time)):
        key = time[i]
        value = spend[i]
        spt[key] = spt.get(key,0)+value
    return zip(*spt.iteritems())

with open(os.path.join(pat, filename)) as fid:
    data0 = [row[0] for row in csv.reader(fid.read().splitlines())]
    data1 = itertools.imap(shapeLine, data0)
    data2 = itertools.ifilter( lambda x: selectCategory(x, category=category, subcategory=subcategory), data1)
    data3 = itertools.imap(timeAndMoney, data2)
    
    d = [item for item in data3]
    day, spend = mergeDay(*zip(*d))
    
    total = zip(day, spend)
    
    ti = sorted( total, key = lambda x: x[0])
    
    time, spend = zip(*ti)
    
    time, spend = otrj(time, spend)
    
    Xtime = time[10:]
    Yspend = spend[10:]
    
    pred = [0 for i in Yspend] ## prediction
    
    r0 = 7
    for i in range(len(pred)):
        wt = 0
        vt = 0
        for j in range(10):
            print Xtime[i]
            print type(Xtime[i]), type(time[i+j])
            Dff = toDayNumber(Xtime[i], time[i+j])
            w = np.exp( -(Dff%7)*(Dff%7)/r0/r0/2)*np.exp(-Dff/r0)
            wt += w
            vt += w*float(spend[i+j])
        pred[i] = vt/wt 
    
    plt.plot(Yspend,pred,'o')
    plt.xlabel('Reference value [usd]')
    plt.ylabel('If spend, spend value [usd]')
    plt.title(category)
    
    f = plt.figure()
    plt.plot(time,spend)
    plt.xlabel('time [Day]')
    plt.ylabel('Spending [usd]')
    plt.title(category)
    
    sp = [float(i) for i in spend]
    f = plt.figure()
    plt.hist(np.array(sp))
    plt.show()  
