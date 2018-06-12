'''
Models for associations
'''

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AssociationKindManager(models.Manager):
    def define(self, name, left, right):
        left_type = ContentType.objects.get_for_model(left)
        right_type = ContentType.objects.get_for_model(right)

        obj, created = self.get_or_create(
            name=name,
            left_type=left_type,
            right_type=right_type)

        return obj


class AssociationKind(models.Model):
    name = models.CharField(max_length=16, unique=True)
    description = models.TextField(null=True, blank=True)

    left_type = models.ForeignKey(ContentType, models.CASCADE,
                                  related_name='leftk')
    right_type = models.ForeignKey(ContentType, models.CASCADE,
                                   related_name='rightk')

    objects = AssociationKindManager()

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class AssociationManager(models.Manager):
    def define(self, kind_, left, right):
        if isinstance(kind_, str):
            kind = AssociationKind.objects.get(name=kind_)
        else:
            kind = kind_

        left_type = ContentType.objects.get_for_model(left)
        right_type = ContentType.objects.get_for_model(right)

        obj, created = Association.objects.get_or_create(
            kind=kind,
            left_type=left_type,
            right_type=right_type,
            left_id=left.id,
            right_id=right.id)

        return obj

    def get_by_objects(self, kind, left, right):
        left_type = ContentType.objects.get_for_model(left)
        right_type = ContentType.objects.get_for_model(right)

        return Association.objects.get(
            kind=kind,
            left_type=left_type,
            right_type=right_type,
            left_id=left.id,
            right_id=right.id)

    def get_linked(self, obj, kind, side):
        if isinstance(kind, str):
            kind = AssociationKind.objects.get(name=kind)

        if side == 'left':
            kind_class = kind.left_type.model_class()
        else:
            kind_class = kind.right_type.model_class()
        if obj.__class__ != kind_class:
            raise AttributeError(
                "kind %s does not link to object %s" %
                (kind.name, obj.__class__._meta.model_name))

        if side is None or side == 'left':
            id_list = Association.objects.filter(
                kind=kind,
                left_id=obj.id).values_list('right_id')
            model = kind.right_type.model_class()
            return model.objects.filter(id__in=id_list)
        if side == 'right':
            id_list = Association.objects.filter(
                kind=kind,
                right_id=obj.id).values_list('left_id')
            model = kind.left_type.model_class()
            return model.objects.filter(id__in=id_list)
        raise AttributeError(
            'side parameter must be "left" or "right"; not %s' %
            (side, ))

    def get_related(self, obj, kind, side='left'):
        if kind:
            if isinstance(kind, str):
                kind = AssociationKind.objects.get(name=kind)
            if side == 'left':
                kind_class = kind.left_type.model_class()
            else:
                kind_class = kind.right_type.model_class()
            if obj.__class__ != kind_class:
                raise AttributeError(
                    "kind %s does not link to object %s" %
                    (kind.name, obj.__class__._meta.model_name))
            kind_sql = ' and a.kind_id={}'.format(kind.id)
        else:
            kind_sql = ''
        if side is None or side == 'left':
            model = kind.left_type.model_class()
            sql = 'SELECT DISTINCT m.id '\
                  'FROM {} m, '\
                  'associations_association a, '\
                  'associations_association b '\
                  'WHERE b.kind_id=a.kind_id '\
                  'AND a.left_id={} '\
                  'AND b.left_id=m.id '\
                  'AND a.right_id=b.right_id '\
                  'AND b.left_id != a.left_id{}'
            return model.objects.raw(sql.format(
                model._meta.db_table, obj.id, kind_sql))
        if side == 'right':
            model = kind.right_type.model_class()
            sql = 'SELECT DISTINCT m.id '\
                  'FROM {} m, '\
                  'associations_association a, '\
                  'associations_association b '\
                  'WHERE b.kind_id=a.kind_id '\
                  'AND a.right_id={} '\
                  'AND b.right_id=m.id '\
                  'AND a.left_id=b.left_id '\
                  'AND b.right_id != a.right_id{}'
            return model.objects.raw(sql.format(
                model._meta.db_table, obj.id, kind_sql))
        raise AttributeError(
            "side must be 'left' or 'right' not {}".format(side))


class Association(models.Model):
    kind = models.ForeignKey(AssociationKind, models.CASCADE)

    left_type = models.ForeignKey(ContentType, models.CASCADE,
                                  related_name='left')
    right_type = models.ForeignKey(ContentType, models.CASCADE,
                                   related_name='right')

    left_id = models.PositiveIntegerField(db_index=True)
    right_id = models.PositiveIntegerField(db_index=True)

    left = GenericForeignKey('left_type', 'left_id')
    right = GenericForeignKey('right_type', 'right_id')

    objects = AssociationManager()

    class Meta:
        unique_together = (('kind', 'left_type', 'right_type',
                            'left_id', 'right_id', ), )

    def __str__(self):
        return "%s[%s(%s),%s(%s)]" % (
            self.kind.name, self.left, self.left_type,
            self.right, self.right_type)

    def save(self, *args, **kwargs):
        if self.left_type.app_label != self.kind.left_type.app_label or\
           self.left_type.model != self.kind.left_type.model:
            raise KeyError('left is wrong type (%s:%s) should be (%s:%s)' %
                           (self.left_type.app_label, self.left_type.model,
                            self.kind.left_type.app_label,
                            self.kind.left_type.model,))
        if self.right_type.app_label != self.kind.right_type.app_label or\
           self.right_type.model != self.kind.right_type.model:
            raise KeyError('right is wrong type (%s:%s) should be (%s:%s)' %
                           (self.right_type.app_label, self.right_type.model,
                            self.kind.right_type.app_label,
                            self.kind.right_type.model,))
        super(Association, self).save(*args, **kwargs)


######################
# model instance method; added when model is registered
######################
def linked_to(self, kind, side='left'):
    '''
    Returns a query set of items that are linked to this instance
    via the specific aasociation kind. Side specifies which side of
    the association this instance is on.
    '''
    return Association.objects.get_linked(self, kind, side)


def related_to(self, kind=None, side='left'):
    '''
    Returns a list of items (of the same model type as this instance)
    that are related to this instance. Related items have a pair (or more)
    of associations connecting the two items: ie, both are linked to the
    the same item. Suppose`Ann parentOF Flo' and 'Tim parentOf Flo' then Ann
    is related to Tim.
    '''
    return Association.objects.get_related(self, kind, side)
