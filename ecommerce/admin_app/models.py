from django.db import models
from user_app.models import Orders
# Create your models here.

class Sales(models.Model):
    date=models.DateField()
    orders=models.ManyToManyField(Orders)
    total_money=models.FloatField()
    class Meta:
        ordering = ['date']



