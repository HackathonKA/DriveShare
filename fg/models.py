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

        # Sort by criteria
        availableMembers = sorted(availableMembers, key=lambda x: x.user.username)
        requiredSeats = len(availableMembers)

        driveBack = []
        others = []
        for member in availableMembers:
            for driver in driveBack:
                if member.checkOverlap(driver[0]):
                    others.append(member)
                    break
            else:
                driveBack.append([member])

        # Now we have a 2D Array with every drive who does not
        # overlap with others on the way back -> they have to drive
        # Now, fill the other drivers in, element 0 will be the driver
        driveThere = copy.deepcopy(driveBack)
        for member in others:
            for driver in driveBack:
                if driver[0].checkOverlap(member):
                    driver.append(member)
                    break;
            else:
                raise Exception("The algorithm is broken, have no matching return driver")

        for member in others:
            for driver in driveThere:
                if driver[0].checkOverlap(member):
                    driver.append(member)
                    break;
            else:
                # We found a driver who does not fit to any of the
                # ones who drive back, so he needs to drive there on
                # his/her own (TODO: that could may be fixed ^^)
                # If he drives on his own, he has to drive back to
                # or his car gets lost ^^
                driveThere.append(member)
                for driver in driveBack:
                    for d in driver:
                        if d == member:
                            driver.remove(member) # remove from car
                driveBack.append([member]) # create new car

        # Now we have a some what matching Configuration
        # TODO: Make sure that the people will actually
        #       fit in the car ^^
        config = {}
        config["date"] = date
        config["tripA"] = driveThere
        config["tripB"] = driveBack
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

    def checkOverlap(self, member, tripA=True):
        """
            Check if member overlaps with this membership
            @param member other member to check
            @param tripA if True, check tripA else tripB
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

        return (beginSelf <= endOther) and (beginOther <= endSelf)


class Car(models.Model):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=2, choices=CAR_TYPE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) +" by "+str(self.user.username)
