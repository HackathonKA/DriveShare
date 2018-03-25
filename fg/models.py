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

        dayConv = list(x[0] for x in WEEKDAYS)

        # Filter Available Members
        for member in allMemberships:
            if dayConv[date.weekday()] in member.days: # Check if member selected this day
                availableMembers.append(member)

        requiredSeats = len(availableMembers)

        cars = []

        # Filter out drivers that need to drive
        for member in availableMembers:
            tripAMatched = False
            tripBMatched = False
            for comp in availableMembers:
                if comp == member:
                    continue

                if member.checkOverlap(comp, True):
                    tripAMatched = True

                if member.checkOverlap(comp, False):
                    tripBMatched = True

                if tripAMatched and tripBMatched:
                    break;

            if not tripAMatched or not tripBMatched:
                # Member needs to drive on his own because:
                # he can either drive there with nobody or
                # he can not drive back with someone
                # --> car[0] == driver
                cars.append([member])

        for car in cars:
            availableMembers.remove(car[0])

        # sort them by a category
        availableMembers = sorted(availableMembers, key=lambda x: x.user.username)


        carsA = copy.deepcopy(cars)     # Cars for tripA
        carsB = copy.deepcopy(cars)     # Cars for tripB
        level = 0
        while len(availableMembers) > 0:

            changed = False
            # Sort all users to cars
            i = 0
            while i < len(availableMembers):
                tripAMatched = (0, None)
                tripBMatched = (0, None)
                j = 0
                while j < len(carsA):
                    car = carsA[j]
                    a = car[0].checkOverlap(availableMembers[i], True)
                    if tripAMatched[0] < a:
                        tripAMatched = (a, carsA[j])

                    b = car[0].checkOverlap(availableMembers[i], False)
                    if tripBMatched[0] < b:
                        tripBMatched = (b, carsB[j])

                    j+=1

                # Level 0 -> No Matchers will become drivers
                if not tripAMatched[0] and not tripBMatched[0]:
                    level = 0
                    carsA.append([availableMembers[i]])
                    carsB.append([availableMembers[i]])
                    availableMembers.remove(availableMembers[i])
                    changed = True
                    continue

                # Level 1 -> Single matchers will become drivers
                elif not tripAMatched[0] or not tripBMatched[0]:
                    if level < 1:
                        i += 1
                        continue
                    else:
                        level = 1
                        carsA.append([availableMembers[i]])
                        carsB.append([availableMembers[i]])
                        availableMembers.remove(availableMembers[i])
                        changed = True
                        continue
                # Level 2 -> Asign Members to Cars
                else:
                    if level < 2:
                        i += 1
                        continue
                    else:
                        level = 2
                        tripAMatched[1].append(availableMembers[i])
                        tripBMatched[1].append(availableMembers[i])
                        availableMembers.remove(availableMembers[i])
                        changed = True
                        continue

                i += 1

            if not changed:
                level += 1
                if level > 2:
                    raise Exception("Algorithm Broke again...")



        config = {}
        config["date"] = date
        config["tripA"] = carsA
        config["tripB"] = carsB
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
            @param member other member to check
            @param tripA if True, check tripA else tripB
            @return Returns the (relative) change in the total time span, if
            the nodes not match it return 0 (false)
        """
        if tripA:
            beginSelf = self.tripABegin
            beginOther = member.tripABegin
            endSelf = self.tripAEnd
            endOther = member.tripAEnd
        else:
            beginSelf = self.tripBBegin
            beginOther = member.tripBBegin
            endSelf = self.tripBEnd
            endOther = member.tripBEnd

        begin = max([beginSelf, beginOther])
        end = min([endSelf, endOther])

        def diffTime(end, start):
            s = start.hour * 60 + start.minute
            e = end.hour * 60 + end.minute
            return e - s

        diff = diffTime(end, begin)
        if diff < 0:
            diff = 0
        elif diff == 0:
            diff = 1 #TODO: Make less ugly

        relChange = diff / diffTime(endSelf, beginSelf)

        return relChange



class Car(models.Model):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=2, choices=CAR_TYPE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) +" by "+str(self.user.username)
