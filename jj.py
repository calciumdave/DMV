import datetime
import random
import matplotlib.pyplot as plt


month = 12
year = 2015
day = range(7)

dday = [datetime.datetime(year,month,d+1) for d in day]

show = [random.randint(2,10) for d in day]

plt.plot(day,show)
plt.show()
