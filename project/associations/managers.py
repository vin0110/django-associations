"""
Custom managers for association. Inspired by /Fantomas42/django-tagging
"""
from django.db import models
from associations.models import Association


class ModelAssociationItemManager(models.Manager):
    """
    A manager for retrieving model instances based on their associations
    """
    def linked_to(self, obj, kind, side="left"):
        return Association.objects.get_linked(obj, kind, side)
