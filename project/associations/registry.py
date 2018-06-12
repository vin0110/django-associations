"""
Registery for associations. Inspired by Fantomas42/django-tagging
"""
# from .managers import AssociationDescriptor
from .managers import ModelAssociationItemManager

registry = []


class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model more than once.
    """
    pass


def register(model, association_item_manager_attr='associations'):
    """
    Sets the given model class up for working with association
    """
    if model in registry:
        raise AlreadyRegistered(
            "The model '%s' has already been registered." %
            model._meta.object_name)
    if hasattr(model, association_item_manager_attr):
        raise AttributeError(
            "'%s' already has an attribute '%s'. You must "
            "provide a custom association_item_manager_attr to register." % (
                model._meta.object_name,
                association_item_manager_attr,
            )
        )

    # Add custom manager
    ModelAssociationItemManager().contribute_to_class(
        model, association_item_manager_attr)

    # Finally register in registry
    registry.append(model)
