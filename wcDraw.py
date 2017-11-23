#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Simulate multiple draws for the World Cup 2018 group stage. Finding the 
probability of different teams being in the same group as 'your' team. 

Related webpage: http://seanelvidge.com/2017/11/probabilityWorldCupGroup

Created November 2017

@author: sean@seanelvidge.com
"""
# In case you're on Python2.7 (I am)
from __future__ import print_function
import numpy as np
import datetime as dt
time = dt.datetime.now()

# How many draw simulations?
sims = 100000 # ~70s

# Which team are you interested in?
pickedTeam = "England"

# Define some objects to hold the team and group information
class team():
    def __init__(self, name, pot, fed):
        self.name = name
        self.pot = pot
        self.fed = fed
        self.picked = 0
    
class group():
    def __init__(self, gName):
        self.name = gName
        self.team1 = ''
        self.team2 = ''
        self.team3 = ''
        self.team4 = ''
        # These are max number of allowed confederation members per group
        self.feds = dict(conmebol=1,concacaf=1,afc=1,uefa=2,caf=1)

# Define all teams, speciying name, pot number and confederation
rus = team("Russia",1,"uefa")
ger = team("Germany",1,"uefa")
bra = team("Brazil",1,"conmebol")
por = team("Portugal",1,"uefa")
arg = team("Argentina",1,"conmebol")
bel = team("Belgium",1,"uefa")
pol = team("Poland",1,"uefa")
fra = team("France",1,"uefa")
spa = team("Spain",2,"uefa")
per = team("Peru",2,"conmebol")
swi = team("Switzerland",2,"uefa")
eng = team("England",2,"uefa")
col = team("Colombia",2,"conmebol")
mex = team("Mexico",2,"concacaf")
uru = team("Uruguay",2,"conmebol")
cro = team("Croatia",2,"uefa")
den = team("Denmark",3,"uefa")
ice = team("Iceland",3,"uefa")
cos = team("Costa Rica",3,"concacaf")
swe = team("Sweden",3,"uefa")
tun = team("Tunisa",3,"caf")
egy = team("Egypt",3,"caf")
sen = team("Senegal",3,"caf")
ira = team("Iran",3,"afc")
ser = team("Serbia",4,"uefa")
nig = team("Nigeria",4,"caf")
aus = team("Australia",4,"afc")
jap = team("Japan",4,"afc")
mor = team("Morocco",4,"caf")
pan = team("Panama",4,"concacaf")
kor = team("Korea Republic",4,"afc")
sau = team("Saudi Arabia",4,"afc") 

teams = [rus,ger,bra,por,arg,bel,pol,fra,spa,per,swi,eng,col,mex,uru,cro,den,
         ice,cos,swe,tun,egy,sen,ira,ser,nig,aus,jap,mor,pan,kor,sau]

# Create pots and numbers from each Confederation
uefa = 0
caf = 0
afc = 0
conmebol = 0
concacaf = 0
pot1 = []
pot2 = []
pot3 = []
pot4 = []
for team in teams:
    if team.fed == 'uefa':
        uefa += 1
    if team.fed == 'caf':
        caf += 1
    if team.fed == 'afc':
        afc += 1
    if team.fed == 'conmebol':
        conmebol += 1
    if team.fed == 'concacaf':
        concacaf += 1
    if team.pot == 1:
        pot1.append(team)
    if team.pot == 2:
        pot2.append(team)
    if team.pot == 3:
        pot3.append(team)
    if team.pot == 4:
        pot4.append(team)

# Check numbers, should have (13+1) UEFA, 5 CAF, 5 AFC, 5 CONMEBOL, 3 CONCACAF
# and 8 in each pot
if (uefa != 14) or (caf != 5) or (afc != 5) or (conmebol != 5) or (concacaf != 3):
    raise ValueError('Something has gone wrong with the Federation definition')
if (len(pot1) != 8) or (len(pot2) != 8) or (len(pot3) != 8) or (len(pot4) != 8):
    raise ValueError('Pot numbers have gone wrong')

# At the end we want to work out what group 'our' team is in, so we track it
# through the draw process
pickedGroup = -1

# A similar structure is called multiple times in the loop, 
# so we use a function:
def addToGroups(groups, pot, team, pickedGroup):
    # Sometimes we get draws which can't happen, so loop around until 
    # every group is 'full'
    full = False
    while full != True:
        randomPot = np.random.choice(pot,size=8,replace=False)
        for n in np.arange(8):
            # The number of groups which each team is allowed to go into is no 
            # longer necessarily 8. Loop over groups:
            allowedGroupInd = []
            for g in np.arange(8):
                if ((groups[g].feds[randomPot[n].fed] > 0) and 
                    (getattr(groups[g],team) == '')):
                    allowedGroupInd.append(g)
            
            if len(allowedGroupInd) != 0:
                # Now pick a random one that is allowed
                randInd = np.random.choice(allowedGroupInd)
                if randomPot[n].name == pickedTeam:
                    pickedGroup = randInd
                setattr(groups[randInd], team, randomPot[n])
                # Update the number of feds in the group
                groups[randInd].feds[randomPot[n].fed] -= 1
            
        # Check that all groups have a team in:
        full = True
        for g in groups:
            if getattr(g,team) == '': 
                full=False
        
        if full == False:
            # A group isn't full, so reset the groups for this team pick
            for g in groups: 
                if getattr(g,team) != '':
                    # Update confeds info and set this team pick back to blank
                    g.feds[getattr(g,team).fed] += 1
                    setattr(g,team,'')
            
    return groups, pickedGroup
            

# Run through the simulations
for drawNum in np.arange(sims):
    # In each group at most 2 UEFA teams, 1 CAF, 1 AFC, 1 CONMEBOL and 1 
    # CONCACAF are allowed

    # 8 groups
    groupA,groupB,groupC,groupD=group('A'),group('B'),group('C'),group('D')
    groupE,groupF,groupG,groupH=group('E'),group('F'),group('G'),group('H')
    groups = [groupA,groupB,groupC,groupD,groupE,groupF,groupG,groupH]
    
    # Team A1 has to be Russia
    groups[0].team1 = rus
    if 'Russia' == pickedTeam:
        pickedGroup = 0
    
    # Shrink pot1 to exclude Russia. Russia should be first team in pot1, but
    # add a quick error check just in case
    if pot1[0].name != 'Russia': raise ValueError()
    
    # Draw rest of pot 1 teams into a random group
    # Can't put someone else in Group A yet
    randomPot1 = np.random.choice(pot1[1:],size=7,replace=False)
    randomGroupInd = np.random.choice(np.arange(1,8),size=7,replace=False)
    
    for n in np.arange(7):
        if randomPot1[n].name == pickedTeam:
            pickedGroup = randomGroupInd[n]
        groups[randomGroupInd[n]].team1 = randomPot1[n]
        groups[randomGroupInd[n]].feds[randomPot1[n].fed] -= 1

    # Now pot 2
    groups, pickedGroup = addToGroups(groups, pot2, 'team2', pickedGroup)

    # Now pot 3
    groups, pickedGroup = addToGroups(groups, pot3, 'team3', pickedGroup)
    
    # Now pot 4
    groups, pickedGroup = addToGroups(groups, pot4, 'team4', pickedGroup)
    
    # The team we are interested in is in 'pickedGroup'. 
    # Who else is with them?
    for team in ['team1','team2','team3','team4']:
        getattr(groups[pickedGroup],team).picked += 1


# Finally print out the results
for n,pot in enumerate([pot1,pot2,pot3,pot4]):
    print('Pot',n+1,':')
    for team in pot:
        print('   ',team.name,':',team.picked*100./sims,'%')
        
print(dt.datetime.now()-time)