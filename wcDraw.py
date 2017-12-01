#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Simulate multiple draws for the World Cup 2018 group stage. Finding the 
probability of different teams being in the same group as 'your' team. 

Related webpage: http://seanelvidge.com/2017/11/probabilityWorldCupGroup

Created November 2017

(Many thanks for comments provided by Julien Guyon)

@author: sean@seanelvidge.com
"""
# In case you're on Python2.7 (I am)
from __future__ import print_function
import numpy as np
import datetime as dt
from collections import Counter
time = dt.datetime.now()

# How many draw simulations?
sims = 100000    # 10,000 = ~20s

# Which team are you interested in?
pickedTeam = "England"

# Define some objects to hold the team and group information
class Team():
    def __init__(self, name, pot, fed):
        self.name = name
        self.pot = pot
        self.fed = fed
        # This will tell us what group the team is in
        self.selected = ''
        # This tells us how many times this team was picked with our team of 
        # interest throughout the simulations
        self.picked = 0
    
class Group():
    def __init__(self, gName):
        self.name = gName
        self.team1 = ''
        self.team2 = ''
        self.team3 = ''
        self.team4 = ''
        # These are max number of allowed confederation members per group
        self.feds = Counter(conmebol=1,concacaf=1,afc=1,uefa=2,caf=1)
        

# Define all teams, speciying name, pot number and confederation
rus = Team("Russia",1,"uefa")
ger = Team("Germany",1,"uefa")
bra = Team("Brazil",1,"conmebol")
por = Team("Portugal",1,"uefa")
arg = Team("Argentina",1,"conmebol")
bel = Team("Belgium",1,"uefa")
pol = Team("Poland",1,"uefa")
fra = Team("France",1,"uefa")
spa = Team("Spain",2,"uefa")
per = Team("Peru",2,"conmebol")
swi = Team("Switzerland",2,"uefa")
eng = Team("England",2,"uefa")
col = Team("Colombia",2,"conmebol")
mex = Team("Mexico",2,"concacaf")
uru = Team("Uruguay",2,"conmebol")
cro = Team("Croatia",2,"uefa")
den = Team("Denmark",3,"uefa")
ice = Team("Iceland",3,"uefa")
cos = Team("Costa Rica",3,"concacaf")
swe = Team("Sweden",3,"uefa")
tun = Team("Tunisa",3,"caf")
egy = Team("Egypt",3,"caf")
sen = Team("Senegal",3,"caf")
ira = Team("Iran",3,"afc")
ser = Team("Serbia",4,"uefa")
nig = Team("Nigeria",4,"caf")
aus = Team("Australia",4,"afc")
jap = Team("Japan",4,"afc")
mor = Team("Morocco",4,"caf")
pan = Team("Panama",4,"concacaf")
kor = Team("Korea Republic",4,"afc")
sau = Team("Saudi Arabia",4,"afc") 

teams = [rus,ger,bra,por,arg,bel,pol,fra,spa,per,swi,eng,col,mex,uru,cro,den,
         ice,cos,swe,tun,egy,sen,ira,ser,nig,aus,jap,mor,pan,kor,sau]

# Obvious but needed:
groupOrder = ['A','B','C','D','E','F','G','H']

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
    # And the team we are interested in:
    if team.name == pickedTeam:
        pickTeam = team

# Check numbers, should have (13+1) UEFA, 5 CAF, 5 AFC, 5 CONMEBOL, 3 CONCACAF
# and 8 in each pot
if (uefa != 14) or (caf != 5) or (afc != 5) or (conmebol != 5) or (concacaf != 3):
    raise ValueError('Something has gone wrong with the Federation definition')
if (len(pot1) != 8) or (len(pot2) != 8) or (len(pot3) != 8) or (len(pot4) != 8):
    raise ValueError('Pot numbers have gone wrong')

# A similar structure is called multiple times in the loop, 
# so we use a function:
def addToGroups(groups, pot, team):
    randomPot = np.random.choice(pot,size=8,replace=False)
    for pick in randomPot:
        # Team should go in the next available group in alphabetical order.
        # However we have to keep an eye on "the future" to make sure we don't
        # enter an impossible position
        for group in groups:
            if ((group.feds[pick.fed] > 0) and 
                (getattr(group,team) == '')):
                # Team can go here. We don't 'formally' select the group yet
                # we need to check what would happen if we did
                setattr(group, team, pick)
                group.feds[pick.fed] -= 1
                pick.selected = group.name
                # Will it make things impossible in the future?
                # We check this by looking at remaining spaces and teams left
                # to be picked:
                spaces = Counter(conmebol=0,concacaf=0,afc=0,uefa=0,caf=0)
                teamsToPick = Counter(conmebol=0,concacaf=0,afc=0,uefa=0,
                                      caf=0)
                # This slows down everything because we are going to run
                # through every team in every group
                for tmpG in groups:
                    if getattr(tmpG, team) == '':
                        confeds = tmpG.feds.copy()
                        if confeds['uefa'] == 2:
                            confeds['uefa'] -= 1
                        spaces = spaces + confeds
                # Now we have to see what teams are still left to be picked
                for t in randomPot:
                    if getattr(t, 'selected') == '':
                        teamsToPick[getattr(t, 'fed')] += 1
                # Subtract these two dictionaries from each other. If there are
                # any negative values then this selection would be impossible
                remainingDict = spaces.copy()
                remainingDict.subtract(teamsToPick)
                if (np.array(remainingDict.values()) < 0).any():
                    # Then this wasn't a valid pick. So undo pick and try the
                    # next group
                    setattr(group, team, '')
                    group.feds[pick.fed] += 1
                    pick.selected = ''
                else:
                    # Break out of this for loop and move to next pick
                    break
                
    return groups
            

# Run through the simulations
for drawNum in np.arange(sims):
    # In each group at most 2 UEFA teams, 1 CAF, 1 AFC, 1 CONMEBOL and 1 
    # CONCACAF are allowed

    # 8 groups
    groupA,groupB,groupC,groupD=Group('A'),Group('B'),Group('C'),Group('D')
    groupE,groupF,groupG,groupH=Group('E'),Group('F'),Group('G'),Group('H')
    groups = [groupA,groupB,groupC,groupD,groupE,groupF,groupG,groupH]
    
    # Team A1 has to be Russia
    groups[0].team1 = rus
    groups[0].feds['uefa'] -= 1
    teams[0].selected = groups[0].name
    
    # Shrink pot1 to exclude Russia. Russia should be first team in pot1, but
    # add a quick error check just in case
    if pot1[0].name != 'Russia': raise ValueError()
    
    # Draw rest of pot 1 teams and place them in groups (in order)
    # Can't put someone else in Group A yet
    randomPot1 = np.random.choice(pot1[1:],size=7,replace=False)
        
    for n,group in enumerate(groups[1:]):
        if randomPot1[n].name == pickedTeam:
            pickedGroup = n+1
        group.team1 = randomPot1[n]
        group.feds[randomPot1[n].fed] -= 1
        randomPot1[n].selected = group.name

    # Now pot 2
    groups = addToGroups(groups, pot2, 'team2')

    # Now pot 3
    groups = addToGroups(groups, pot3, 'team3')
        
    # Now pot 4
    groups = addToGroups(groups, pot4, 'team4')

    # Still can get impossible situations (~1% of the time). These arise from 
    # the way I have counted possibilites (by adding together 'spaces'). There 
    # is a work a round, but it makes the code a *lot* slower, whilst having no
    # impact on the probabilities. Exclude those cases:
    fail = False
    for t in teams:
        if t.selected == '':
            fail = True
            
    if fail == False:
        # Which group is our interested team in?
        intGroup = groups[np.where(np.array(groupOrder) == pickTeam.selected)[0][0]]
        # Who else is with them?
        for team in ['team1','team2','team3','team4']:
            getattr(intGroup,team).picked += 1
    else:
        sims -= 1
        
    # Clean the team selected flag
    for t in teams:
        t.selected = ''


# Finally print out the results
for n,pot in enumerate([pot1,pot2,pot3,pot4]):
    print('Pot',n+1,':')
    for team in pot:
        print('   ',team.name,':',np.round(team.picked*100./sims,decimals=2),
              '%')
        
print(sims)
print(dt.datetime.now()-time)