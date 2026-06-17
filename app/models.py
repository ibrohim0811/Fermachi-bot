from django.db import models



class Milk(models.Model):
    litr = models.DecimalField(max_digits=100, decimal_places=3)
    date = models.DateField()

    def __str__(self):
        return self.date
    


class CowBorn(models.Model):
    parent = models.CharField(max_length=350)
    date = models.DateField()

    def __str__(self):
        return self.parent