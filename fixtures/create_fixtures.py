'''
to create fixtures:

rm db.sqlite3
./manage.py migrate
./manage.py shell < tests/create_fixtures.py
./manage.py dumpdata --indent 2 tests associations > persons.json
'''

from tests.models import Person
from tests.models import Address

from associations.models import Association
from associations.models import AssociationKind

Person.objects.create(name='Joe')
Person.objects.create(name='Bob')
Person.objects.create(name='Sue')
Person.objects.create(name='Ann')
Person.objects.create(name='Jay')
Person.objects.create(name='Flo')

Address.objects.create(street='123 Main')
Address.objects.create(street='213 Church')

AssociationKind.objects.define('parentOf', Person, Person)
AssociationKind.objects.define('livesAt', Person, Address)

persons = Person.objects.all()
addresses = Address.objects.all()

# Joe, Sue are parents of Bob, Ann
Association.objects.define('parentOf', persons[0], persons[1])
Association.objects.define('parentOf', persons[2], persons[1])
Association.objects.define('parentOf', persons[0], persons[3])
Association.objects.define('parentOf', persons[2], persons[3])

# Ann and Jay are parents of Flo
Association.objects.define('parentOf', persons[3], persons[5])
Association.objects.define('parentOf', persons[4], persons[5])

# Joe, Sue, Bob live on Main
Association.objects.define('livesAt', persons[0], addresses[0])
Association.objects.define('livesAt', persons[1], addresses[0])
Association.objects.define('livesAt', persons[2], addresses[0])

# Ann, Jay, and Flo live on Church
Association.objects.define('livesAt', persons[3], addresses[1])
Association.objects.define('livesAt', persons[4], addresses[1])
Association.objects.define('livesAt', persons[5], addresses[1])


