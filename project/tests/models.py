from django.db import models
from associations.registry import register


class Person(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        ordering = ('pk', )

    def __str__(self):
        return self.name


class Address(models.Model):
    street = models.CharField(max_length=32)

    class Meta:
        ordering = ('pk', )

    def __str__(self):
        return self.street


register(Person)
register(Address)
