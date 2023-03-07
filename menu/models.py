from django.db import models
from vendor.models import Vendor

class Category(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
