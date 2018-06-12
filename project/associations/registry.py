"""
Registery for associations. Inspired by Fantomas42/django-tagging
"""
# from .managers import AssociationDescriptor
from .models import linked_to, related_to

registry = []


class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model more than once.
    """
    pass


def register(model, linked_attr='linked', related_attr='related'):
    """
    Sets the given model class up for working with association
    """
    if model in registry:
        raise AlreadyRegistered(
            "The model '%s' has already been registered." %
            model._meta.object_name)
    if hasattr(model, linked_attr):
        raise AttributeError(
            "'%s' already has an attribute '%s'. You must "
            "provide a custom linked_attr to register." % (
                model._meta.object_name,
                linked_attr, ))
    if hasattr(model, related_attr):
        raise AttributeError(
            "'%s' already has an attribute '%s'. You must "
            "provide a custom related_attr to register." % (
                model._meta.object_name,
                related_attr, ))

    # Add linked_method
    setattr(model, linked_attr, linked_to)

    # Add related_method
    setattr(model, related_attr, related_to)

    # Finally register in registry
    registry.append(model)
