# -*- coding: utf-8 -*-
"""
Program for creating XKCD style plot looking at the correlation between
Apollo astronaut names and Apollo mission number.

Modification History
-------
Created on Dec 15 by Sean
Contact: sean@seanelvidge.com
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

order = np.linspace(1,21,num=21)
# Apollo mission number ordered by alphabetical astronaut name
miss = np.array([11,11,12,17,11,12,16,17,12,13,15,13,16,14,14,17,15,14,13,15,16])

# Construct regression line
slope,intercept,r_value,p_value,std_err = stats.linregress(order,miss)
line = slope*order + intercept

# Print the correlation coefficient
print np.corrcoef(miss,order)[0,1]

# Create the XCKD style plot
with plt.xkcd(scale=1,length=90,randomness=4):
    plt.plot(order,miss,'b*',label='Missions Flown',markersize=13)
    plt.plot(order,line,'red',label='Regression Line')
     
    plt.tick_params(direction='inout',top='off',right='off',bottom='off',
                    labelbottom='off',labelsize=15)
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_position('zero')    
    plt.gca().spines['bottom'].set_position(('data',10))

    plt.xlim(-1,22)
    plt.ylim(9.5,18)
    
    T = np.array(range(7))+11
    plt.yticks(T)

    plt.ylabel('Apollo missions',fontsize=20)
    plt.xlabel('Apollo astronauts in alphabetical order\n(Aldrin, Armstrong, '+
               'Bean, ...)',fontsize=20)

    plt.text(16.6,17.6,'Regression Line')
    plt.plot([18.8,19.3],[17.4,15.4],'-k')
    
    plt.arrow(0,17.4,0,0.1,head_width=1.5,overhang=1,head_length=0.5,
              color='black',lw=1.5)
    plt.arrow(21.4,10,0.1,0,head_width=0.7,overhang=1,head_length=0.5,
                  color='black',lw=1.5)
    
    # Uncomment to save the plot
#    plt.savefig('~/apollo_az.png', dpi=plt.gcf().dpi)

