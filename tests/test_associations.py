from django.test import TestCase

from associations.models import Association
from associations.models import AssociationKind
from tests.models import Person
from tests.models import Address
from django.db import IntegrityError


class KindTest(TestCase):
    fixtures = ['associations', ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_new(self):
        name = 'newkind'
        kind = AssociationKind.objects.define(name, Address, Address)
        self.assertEquals(AssociationKind, kind.__class__)
        self.assertEquals(name, kind.name)

        # do it again; return previous
        kind1 = AssociationKind.objects.define('newkind', Address, Address)
        self.assertEquals(kind.id, kind1.id)

        # remove it
        kind.delete()
        self.assertRaises(AssociationKind.DoesNotExist,
                          AssociationKind.objects.get,
                          name=name)

    def test_lookup(self):
        name = 'parentOf'
        kind = AssociationKind.objects.get(name=name)
        self.assertEqual(name, kind.name)

        name = 'doesnotexist'
        self.assertRaises(AssociationKind.DoesNotExist,
                          AssociationKind.objects.get,
                          name=name)

    def test_same_name_different_models(self):
        name = 'newkind'
        kind = AssociationKind.objects.define(name, Person, Person)
        with self.assertRaises(IntegrityError):
            AssociationKind.objects.define(name, Person, Address)
        # clean up for next test
        kind.delete()

    def test_fetch(self):
        kinds = AssociationKind.objects.all()
        self.assertEquals(2, len(kinds))


class AssociationTest(TestCase):
    fixtures = ['associations', 'tests', ]

    def setUp(self):
        kinds = AssociationKind.objects.all()
        self.kinds = {}
        for k in kinds:
            self.kinds[k.name] = k
        self.persons = Person.objects.all()
        self.addresses = Address.objects.all()

    def tearDown(self):
        pass

    def test_new(self):
        assn = Association.objects.define(
            self.kinds['parentOf'],
            self.persons[0],
            self.persons[0])
        self.assertEquals(self.kinds['parentOf'], assn.kind)
        self.assertEquals(self.persons[0], assn.left)
        self.assertEquals(self.persons[0], assn.right)

    def test_lookup(self):
        kind_name = 'parentOf'
        kind = self.kinds[kind_name]
        assns = Association.objects.filter(kind=kind)
        self.assertEquals(6, len(assns))

    def test_dup(self):
        kind_name = 'parentOf'
        kind = self.kinds[kind_name]

        # define new association
        assn = Association.objects.define(
            kind, self.persons[0], self.persons[0])
        # define again
        assn1 = Association.objects.define(
            kind, self.persons[0], self.persons[0])
        self.assertEquals(assn.id, assn1.id)

        # clean up
        assn.delete()

        # test
        with self.assertRaises(Association.DoesNotExist):
            Association.objects.get_by_objects(kind=kind,
                                               left=self.persons[0],
                                               right=self.persons[0])

    def test_linked_left(self):
        kind = self.kinds['parentOf']

        # use string for kind
        items = Association.objects.get_linked(
            self.persons[0],
            'parentOf',
            'left')
        self.assertEquals(2, len(items))

        # use object for kind
        items1 = Association.objects.get_linked(
            self.persons[0],
            kind,
            'left')
        self.assertEquals(2, len(items1))

        for n in range(len(items)):
            self.assertEquals(items[n].id, items1[n].id)

    def test_linked_right(self):
        kind = self.kinds['parentOf']

        # use string for kind
        items = Association.objects.get_linked(
            self.persons[1],
            'parentOf',
            'right')
        self.assertEquals(2, len(items))

        # use object for kind
        items1 = Association.objects.get_linked(
            self.persons[1],
            kind,
            'right')
        self.assertEquals(2, len(items1))

        for n in range(len(items)):
            self.assertEquals(items[n].id, items1[n].id)

    def test_linked_address_right(self):
        kind = self.kinds['livesAt']

        # use string for kind
        items = Association.objects.get_linked(
            self.addresses[1],
            'livesAt',
            'right')
        self.assertEquals(3, len(items))

        # use object for kind
        items1 = Association.objects.get_linked(
            self.addresses[1],
            kind,
            'right')
        self.assertEquals(3, len(items1))

        for n in range(len(items)):
            self.assertEquals(items[n].id, items1[n].id)

    def test_linked_bad(self):
        # bad kind
        with self.assertRaises(AssociationKind.DoesNotExist):
            Association.objects.get_linked(
                self.persons[0],
                'doesnotexist',
                'left')
        # incorrect object -- left
        with self.assertRaises(AttributeError):
            Association.objects.get_linked(
                self.addresses[0],
                'parentOf',
                'left')
        # incorrect object -- right
        with self.assertRaises(AttributeError):
            Association.objects.get_linked(
                self.addresses[0],
                'parentOf',
                'right')
        # invalid side
        with self.assertRaises(AttributeError):
            Association.objects.get_linked(
                self.persons[0],
                'parentOf',
                'upside')

    def test_related(self):
        kind = self.kinds['livesAt']

        # by string
        q = Association.objects.get_related(
            self.persons[0],
            'livesAt')
        items = [item for item in q]
        self.assertEquals(2, len(items))

        # by kind
        q = Association.objects.get_related(
            self.persons[0],
            kind)
        items1 = [item for item in q]
        self.assertEquals(2, len(items1))

        # with explicit parameter
        q = Association.objects.get_related(
            self.persons[0],
            'livesAt',
            side='left')
        items2 = [item for item in q]
        self.assertEquals(2, len(items2))

        # check
        for n in range(2):
            self.assertEquals(items[n].id, items1[n].id)
            self.assertEquals(items[n].id, items2[n].id)

    def test_related_right(self):
        kind_name = 'parentOf'

        q = Association.objects.get_related(
            self.persons[1],
            kind_name,
            side='right')
        items = [item for item in q]
        self.assertEquals(1, len(items))

        # sanity check -- see the side parameter gives different results
        q = Association.objects.get_related(
            self.persons[1],
            kind_name,
            side='left')
        items = [item for item in q]
        self.assertEquals(0, len(items))
