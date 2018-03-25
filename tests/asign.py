#!/usr/bin/env python3
import sys
sys.path.append('./')
import datetime
date = datetime.datetime(2018,3,23)
from fg.models import *
c = Carpool.objects.get(pk=1)
res = c.getDriverConfiguration(date)
print(res)
