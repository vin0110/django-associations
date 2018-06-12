from django.test import TestCase

from associations.models import AssociationKind
from tests.models import Person
from tests.models import Address


class ModelsTest(TestCase):
    fixtures = ['tests', 'associations', ]

    def setUp(self):
        kinds = AssociationKind.objects.all()
        self.kinds = {}
        for k in kinds:
            self.kinds[k.name] = k
        self.persons = Person.objects.all()
        self.children = [2, 0, 2, 1, 1, 0]
        self.addresses = Address.objects.all()

    def tearDown(self):
        pass

    def test_parent(self):
        for i in range(len(self.persons)):
            self.assertEquals(self.children[i],
                              len(self.persons[i].linked('parentOf')))

    def test_parent_by_kind(self):
        for i in range(len(self.persons)):
            self.assertEquals(
                self.children[i],
                len(self.persons[i].linked(self.kinds['parentOf'])))

    def test_address(self):
        for i in range(len(self.persons)):
            self.assertEquals(1, len(self.persons[i].linked('livesAt')))

    def test_address_right(self):
        for i in range(len(self.addresses)):
            self.assertEquals(
                3,
                len(self.addresses[i].linked('livesAt', side='right')))

    def test_related(self):
        for i in range(len(self.persons)):
            q = self.persons[i].related('livesAt')
            items = [item for item in q]
            self.assertEquals(2, len(items))

    def test_related_right(self):
        results = [0, 1, 0, 1, 0, 0]
        for i in range(len(self.persons)):
            q = self.persons[i].related('parentOf', side='right')
            items = [item for item in q]
            self.assertEquals(results[i], len(items))
