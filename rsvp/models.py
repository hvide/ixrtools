from django.db import models

# Create your models here.


# class Path(models.Model):
#     name = models.CharField(max_length=200)
#     hopes = models.CharField(max_length=500)


class Device(models.Model):
    hostname = models.CharField(max_length=200)
    ip = models.CharField(max_length=50)

    def __str__(self):
        return self.hostname
