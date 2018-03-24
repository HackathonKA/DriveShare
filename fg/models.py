from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User

import datetime

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

class Car(models.Model):
    name = models.CharField(max_length=50)
    kind = models.CharField(max_length=2, choices=CAR_TYPE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name) +" by "+str(self.user.username)
