from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

import datetime
import copy

WEEKDAYS = (
    ('mon', "Monday"),
    ('tue', "Tuesday"),
    ('wen', "Wendsday"),
    ('thu', "Thursday"),
    ('fri', "Friday"),
    ('sat', "Saturady"),
    ('sun', "Sunday"),
)

CAR_TYPE = (
    ("MI", "Mini Car"),
    ("SP", "Sports Car"),
    ("SE", "Sedan"),
    ("VA", "Van"),
    ("SU", "SUV")
)

# Create your models here.
class Carpool(models.Model):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=500)
    loc_a = models.CharField(max_length=250)
    loc_b = models.CharField(max_length=250)

    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

    def getDriverConfiguration(self, date):
        """
        @param date a DateTime Object
        @return A list of Drive Configurations for the given day
        """
        allMemberships = self.membership_set.all()
        availableMembers = []
        availableMembersWithCars = []
        dayConv = list(x[0] for x in WEEKDAYS)

        # Filter Available Members
        for member in allMemberships:
            if dayConv[date.weekday()] in member.days:  # Check if member selected this day
                availableMembers.append(member)

        # Filter member with and without cars
        for member in availableMembers:
            car = member.user.car_set.filter(isActive=True)
            if car:
                availableMembersWithCars.append(member)
                availableMembers.remove(member)

        requiredSeats = len(availableMembers)

        cars = []

        # Filter out drivers that need to drive
        # Only compare members with cars
        for member in availableMembersWithCars:
            tripAMatched = False
            tripBMatched = False
            for comp in availableMembersWithCars:
                if comp == member:
                    continue

                if member.checkOverlap(comp, True):
                    tripAMatched = True

                if member.checkOverlap(comp, False):
                    tripBMatched = True

                if tripAMatched and tripBMatched:
                    break

            if not tripAMatched or not tripBMatched:
                # Member needs to drive on his own because:
                # he can either drive there with nobody or
                # he can not drive back with someone
                # --> car[0] == driver
                cars.append([member])

        for car in cars:
            availableMembersWithCars.remove(car[0])

        # sort them by a category
        availableMembersWithCars = sorted(availableMembersWithCars, key=lambda x: x.user.username)
        availableMembers = sorted(availableMembers, key=lambda x: x.user.username, reverse=True)

        notAssignableMembers = []

        carsA = copy.deepcopy(cars)     # Cars for tripA
        carsB = copy.deepcopy(cars)     # Cars for tripB

        level0 = availableMembersWithCars
        level1 = []
        level2 = availableMembers
        level3 = []
        level4 = []

        level = 0
        i = 0

        while level < 6:
# +++++++++++++++++++++++++++++++++
# level 0
# +++++++++++++++++++++++++++++++++
            if level is 0:

                if i >= len(level0):
                    i = 0
                    level1 = level0
                    level = 1
                    continue

                tripAnyMatched = False
                for car in carsA:
                    if level0[i].checkOverlap(car, True) or level0[i].checkOverlap(car, False):
                        tripAnyMatched = True
                        break

                if not tripAnyMatched:
                    carsA.append(level0[i])
                    carsB.append(level0[i])
                    level0.remove((level0[i]))
                    continue
                else:
                    i += 1
                    continue

# +++++++++++++++++++++++++++++++++
# level 1
# +++++++++++++++++++++++++++++++++
            elif level is 1:
                if i >= len(level1):
                    i = 0
                    level3 = level1
                    level = 2
                    continue

                tripAMatched = False
                tripBMatched = False
                for car in carsA:
                    if level1[i].checkOverlap(car, True):
                        tripAMatched = True
                    if level1[i].checkOverlap(car, False):
                        tripBMatched = True
                    if tripAMatched and tripBMatched:
                        break

                if not tripAMatched or not tripBMatched:
                    carsA.append(level1[i])
                    carsB.append(level1[i])
                    level1.remove(level1[i])
                    continue
                else:
                    i += 1
                    continue

# +++++++++++++++++++++++++++++++++
# level 2
# +++++++++++++++++++++++++++++++++
            elif level is 2:
                if len(level2) is 0:
                    i = 0
                    level = 3
                    continue
                i = 0
                average = 0
                position = 0
                positionCarA = 0
                positionCarB = 0
                # Try to find the optimal combination of cars for the member
                # Iterate through all members in the level2 list and for every member try every car
                while i < len(level2):
                    j = 0
                    a = 0
                    b = 0
                    positionA = 0
                    positionB = 0
                    while j < len(carsA):
                        tmpA = level2[i].checkOverlap(carsA[j], True)
                        if tmpA > a:
                            a = tmpA
                            positionA = j
                        tmpB = level2[i].checkOverlap(carsA[j], False)
                        if tmpB > b:
                            b = tmpB
                            positionB = j
                        j += 1
                    averageTMP = float(a+b) / 2

                    # Catch the case if one of the two borders isn't possible, but a high average is possible
                    if not a or not b:
                        averageTMP = 0
                    if averageTMP > average:
                        average = averageTMP
                        positionCarA = positionA
                        positionCarB = positionB
                        position = i
                    i += 1
                # if any average higher than 0 was found add to the cars
                # else add to level 4
                if average > 0:
                    carsA[positionCarA].append(level2[position])
                    carsB[positionCarB].append(level2[position])
                    level2.remove(level2[position])
                else:
                    level4.append(level2[position])
                    level2.remove(level2[position])

# +++++++++++++++++++++++++++++++++
# level 3
# +++++++++++++++++++++++++++++++++
            elif level is 3:
                if len(level3) is 0:
                    i = 0
                    level = 4
                    continue
                i = 0
                average = 0
                position = 0
                positionCarA = 0
                positionCarB = 0
                # Try to find the optimal combination of cars for the member
                # Iterate through all members in the level3 list and for every member try every car
                while i < len(level3):
                    j = 0
                    a = 0
                    b = 0
                    positionA = 0
                    positionB = 0
                    while j < len(carsA):
                        tmpA = level3[i].checkOverlap(carsA[j], True)
                        if tmpA > a:
                            a = tmpA
                            positionA = j
                        tmpB = level3[i].checkOverlap(carsA[j], False)
                        if tmpB > b:
                            b = tmpB
                            positionB = j
                        j += 1
                    # If after iterating through all cars for one member and none was found
                    # -> callback to lower level to add member as new driver
                    if not tmpA or not tmpB:
                        if not tmpA and not tmpB:
                            level = 0
                            level0 = level3
                        else:
                            level = 1
                            level1 = level3
                        average = 100  # avoid the rest of the function to do any damage to the data
                        break
                    averageTMP = float(a+b) / 2
                    if averageTMP > average:
                        average = averageTMP
                        positionCarA = positionA
                        positionCarB = positionB
                        position = i
                    i += 1
                if average is 100:
                    continue
                # if no valid average greater than 0 is possible to find shall be catched earlier
                if average > 0:
                    carsA[positionCarA].append(level3[position])
                    carsB[positionCarB].append(level3[position])
                    level3.remove(level3[position])
                else:
                    raise Exception ("FUUUUUUUUUUUUU")

# +++++++++++++++++++++++++++++++++
# level 4
# +++++++++++++++++++++++++++++++++
            elif level is 4:
                if len(level4) is 0:
                    i = 0
                    level = 5
                    break
                average = 0
                position = 0
                positionCarA = 0
                positionCarB = 0
                # Try to find the optimal combination of cars for the member
                # Iterate through all members in the level4 list and for every member try every car
                while i < len(level4):
                    j = 0
                    a = 0
                    b = 0
                    positionA = 0
                    positionB = 0
                    while j < len(carsA):
                        tmpA = level4[i].checkOverlap(carsA[j], True)
                        if tmpA > a:
                            a = tmpA
                            positionA = j
                        tmpB = level4[i].checkOverlap(carsA[j], False)
                        if tmpB > b:
                            b = tmpB
                            positionB = j
                        j += 1
                    # If after iterating through all cars for one member and none was found
                    # -> assign to
                    if not tmpA or not tmpB:
                        notAssignableMembers.append(level4[i])
                        level4.remove(level4[i])
                        continue
                    averageTMP = float(a+b) / 2
                    if averageTMP > average:
                        average = averageTMP
                        positionCarA = positionA
                        positionCarB = positionB
                        position = i
                    i += 1
                if average is 100:
                    continue
                # if no valid average greater than 0 is possible to find shall be catched earlier
                if average > 0:
                    carsA[positionCarA].append(level3[position])
                    carsB[positionCarB].append(level3[position])
                    level3.remove(level3[position])
                else:
                    raise Exception ("FUUUUUUUUUUUUU")

        """
        while len(availableMembers) > 0 or len(availableMembersWithCars) > 0:

            changed = False
            # Sort all users to cars
            iCar = 0
            iNoCar = 0
            while iCar < len(availableMembersWithCars) or iNoCar < len(availableMembers):
                tripAMatched = (0, None)
                tripBMatched = (0, None)
                j = 0

                # TODO: Intelligenz
                while j < len(carsA):
                    car = carsA[j]
                    a = 0
                    b = 0
                    if level is 2 and (len(availableMembers) > 0 or len(availableMembersWithCars)):
                        a = car[0].checkOverlap(availableMembers[iNoCar], True)
                        b = car[0].checkOverlap(availableMembers[iNoCar], False)
                    else:
                        a = car[0].checkOverlap(availableMembersWithCars[iCar], True)
                        b = car[0].checkOverlap(availableMembersWithCars[iCar], False)

                    if tripAMatched[0] < a:
                        tripAMatched = (a, carsA[j])

                    if tripBMatched[0] < b:
                        tripBMatched = (b, carsB[j])

                    j+=1

                # Level 0 -> No matches will become drivers
                if not tripAMatched[0] and not tripBMatched[0]:
                    level = 0
                    carsA.append([availableMembersWithCars[iCar]])
                    carsB.append([availableMembersWithCars[iCar]])
                    availableMembersWithCars.remove(availableMembersWithCars[iCar])
                    changed = True
                    continue

                # Level 1 -> Single matches will become drivers
                elif not tripAMatched[0] or not tripBMatched[0]:
                    if level < 1:
                        iCar += 1
                        continue
                    else:
                        level = 1
                        carsA.append([availableMembersWithCars[iCar]])
                        carsB.append([availableMembersWithCars[iCar]])
                        availableMembersWithCars.remove(availableMembersWithCars[iCar])
                        changed = True
                        continue
                # Level 2 -> Assign Members without cars to cars
                else:
                    if level < 2:
                        iCar += 1
                        continue
                    else:
                        level = 2
                        if len(availableMembers) > 0:
                            if tripAMatched[0] and tripBMatched[0]:
                                tripAMatched[1].append(availableMembers[iNoCar])
                                tripBMatched[1].append(availableMembers[iNoCar])
                            else:
                                notAssignableMembers.append((availableMembers[iNoCar]))
                            availableMembers.remove(availableMembers[iNoCar])
                        else:
                            tripAMatched[1].append(availableMembersWithCars[iCar])
                            tripBMatched[1].append(availableMembersWithCars[iCar])
                            availableMembersWithCars.remove((availableMembersWithCars[iCar]))
                        changed = True
                        continue

                iCar += 1

            if not changed:
                level += 1
                if level > 2:
                    raise Exception("Algorithm Broke again...")"""



        config = {}
        config["date"] = date
        config["tripA"] = carsA
        config["tripB"] = carsB
        config["Not assignable"] = notAssignableMembers
        return config

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pool = models.ForeignKey(Carpool, on_delete=models.CASCADE)

    tripABegin = models.TimeField(default=datetime.time(8))
    tripAEnd = models.TimeField(default=datetime.time(8, 30))

    tripBBegin = models.TimeField(default=datetime.time(16))
    tripBEnd = models.TimeField(default=datetime.time(17))

    days = MultiSelectField(choices=WEEKDAYS, default=[])

    def __str__(self):
        return "User {0} is member of {1}".format(self.user.username, self.pool.name)

    def checkOverlap(self, member, tripA):
        """
            Check if member overlaps with this membership
            @param member array of other members to check
            @param tripA if True, check tripA else tripB
            @return Returns the (relative) change in the total time span, if
            the nodes not match it return 0 (false)
        """

        if tripA:
            beginSelf = self.tripABegin.hour * 60 + self.tripABegin.minute
            endSelf = self.tripAEnd.hour * 60 + self.tripAEnd.minute

            beginOther = 0
            endOther = 1441  # 1440 = 24*60
            for mem in member:
                tmp = mem.tripABegin.hour * 60 + mem.tripABegin.minute
                if(tmp > beginOther):
                    beginOther = tmp
                tmp = mem.tripAEnd.hour * 60 + mem.tripAEnd.minute
                if(tmp < endOther):
                    endOther = tmp
        else:
            beginSelf = self.tripBBegin.hour * 60 + self.tripBBegin.minute
            endSelf = self.tripBEnd.hour * 60 + self.tripBEnd.minute

            beginOther = 0
            endOther = 1441  # 1440 = 24*60
            for mem in member:
                tmp = mem.tripBBegin.hour * 60 + mem.tripBBegin.minute
                if(tmp > beginOther):
                    beginOther = tmp
                tmp = mem.tripBEnd.hour * 60 + mem.tripBEnd.minute
                if(tmp < endOther):
                    endOther = tmp

        begin = max(beginSelf, beginOther)
        end = min(endSelf, endOther)

        diff = end - begin
        if diff < 0:
            diff = 0
        elif diff == 0:
            diff = 1

        if endOther is beginOther:
            endOther += 1

        return diff / (endOther - beginOther)



class Car(models.Model):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=2, choices=CAR_TYPE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seats = models.IntegerField(default=5)
    isActive = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name) +" by "+str(self.user.username)
