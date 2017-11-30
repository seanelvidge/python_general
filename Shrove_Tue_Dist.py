#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Find the distribution of Pancake Day/Shrove Tuesday.

Related webpage: http://seanelvidge.com/2017/02/distribution-of-pancake-day

Created February 2017

@author: sean@seanelvidge.com
"""
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Define a function to return the date which Easter falls on for a given year.
# This computus comes from: https://en.wikipedia.org/wiki/Computus#Software
def easter(year):
    a = year % 19
    b = year >> 2
    c = b // 25 + 1
    d = (c * 3) >> 2
    e = ((a * 19) - ((c * 8 + 5) // 25) + d + 15) % 30
    e += (29578 - a - e * 32) >> 10
    e -= ((year % 7) + b - d + e + 2) % 7
    d = e >> 5
    day = e - d * 31
    month = d + 3
    return dt.date(year, month, day)

# Loop through the years 1900 to 9999 finding the date of Easter and then
# subtracting 47 days to find Shrove Tuesday (Pancake day)
tue = np.empty(0)
dates = np.empty(0)
for i in np.arange(1900,10000):
    east = easter(i)
    tue = np.append(tue,np.int((east - dt.timedelta(days=47)).strftime('%m%d')))
    
# Put the data in a Pandas dataframe
df = pd.DataFrame(tue, columns=['date'], dtype='int')
    
# Get min and max dates for plotting:
tuemin = np.int(tue.min()) # 203 - Feb 3rd
tuemax = np.int(tue.max()) # 309 - March 9th

# Numbers define month and day, MDD
rng = np.concatenate((np.arange(tuemin,230),np.arange(301,tuemax+1)))
daterng = np.empty(0, dtype='datetime64[D]')
for rn in rng:
    daterng = np.append(daterng, dt.datetime.strptime('1904'+np.str(rn),
                                            '%Y%m%d')-dt.timedelta(hours=12))

values = np.empty(0)
for rn in rng:
    values = np.append(values, len(np.where(df['date'] == rn)[0]))

# Convert numbers into percentages
percent = 100*values/tue.shape[0]

# Set this up for plotting
months = mdates.MonthLocator() # Every month
# Every 3rd day
days = mdates.DayLocator(range(1, 31), interval=3)
daysFmt = mdates.DateFormatter("%b %d")

fig, ax = plt.subplots()

# Bar plot
plt.bar(daterng, percent, width=1.0, align='center', alpha=0.75)

ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(daysFmt)
ax.autoscale_view()

ax.set_ylabel('% of Pancake Days',size=20)
ax.set_title('Distribution of Pancake Days \nfrom year 1900 to 9999',size=20)

for tick in ax.xaxis.get_majorticklabels():
    tick.set_horizontalalignment("right")

# Set some tick parameters
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='on') # labels along the bottom edge are off

fig.autofmt_xdate(rotation=45)
plt.tick_params(axis='both', which='major', labelsize=20)

fig.tight_layout()
    