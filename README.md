# django-associations

Django-associations creates _relationships_ between arbitrary models.
A relationship associates two model instances.
It was inspired in many ways by
[django-tagging](https://pypi.org/project/django-tagging/).

Let's explain this with an example.
We have two kinds of associations: _parentOf_ and _livesAt_.
The "parentOf" association relates _parents_ and their
_children_ and the "livesAt" association relates persons to their
address.

Assume we have the following two models.
```python
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
```

Now suppose we want to make the following associations.

Parent | Child
------ | -----
Joe | Bob
Sue | Bob
Joe | Ann
Sue | Ann
Ann | Flo
Jay | Flo

In words, Joe and Sue are a parent of both Ann and Bob.
Also, Ann and Jay are a parent of Flo.

We also want to track where these persons live.

Person | Address
------ | -------
Joe | 123 Main
Sue | 123 Main
Bob | 123 Main
Ann | 213 Church
Jay | 213 Church
Flo | 213 Church

To create the above associations, first define the _association kind_

```python
from tests.models import Person
from tests.models import Adddress
from Associations.models import AssociationKind

parentOfKind = AssociationKind.objects.define('parentOf', Person, Person)
livesAtKind = AssociationKind.objects.define(livesAt', Person, Address)
```

The 'parentOf' association kind describes a relationship between two
persons, whereas 'livesAt' associates a person with an address.
Add an association as follows.

```python
joe = Person.objects.get(name='Joe')
bob = Person.objects.get(name='Ann')

Association.objects.define(parentOfKind, joe, bob)
```

The above association is read as "Joe is a parent of Ann."
The order is import.
The code below completes the associations in the first tables.

```python
sue = Person.objects.get(name='Sue')
ann = Person.objects.get(name='ann')
jay = Person.objects.get(name='Jay')
flo = Person.objects.get(name='Flo')

Association.objects.define(parentOfKind, sue, bob)
Association.objects.define(parentOfKind, joe, ann)
Association.objects.define(parentOfKind, sue, ann)
Association.objects.define(parentOfKind, ann, flo)
Association.objects.define('parentOf', jay, flo)
```

The last definition uses the name of the kind instead of
the kind object.

The following defines the livesAt associations.

```python
main = Address.objects.get(street='123 Main')
church = Address.objects.get(street=213 Church')

Association.objects.define(livesAtKind, joe, main)
Association.objects.define(livesAtKind, sue, main)
Association.objects.define(livesAtKind, bob, main)
Association.objects.define(livesAtKind, ann, church)
Association.objects.define(livesAtKind, jay, church)
Association.objects.define(livesAtKind, flo, church)
```

This example is coded in the tests directory.

Now that we have defined the parentOf and livesAt associations, here
are some uses.
Joe's children:

```
>>> joe.linked('parentOf')
```

returns

```
<QuerySet [<Person: Bob>, <Person: Ann>]>
```

To get Flo's parents find the association in which Flo is on the
right-hand side.

```python
>>> flo.linked('parentOf', side='right')
```

returns

```
<QuerySet [<Person: Ann>, <Person: Jay>]>
```

We can also find instances that are _related_ to an instance.
Two model instances are related if they each are association with the
same instance.
For example, Joe is related to Bob via the livesAt association.

  * Joe lives at 123 Main
  * Bob lives at 123 Main

Joe is related to Sue via both the parentOf and the livesAt
association.

  * Joe lives at 123 Main
  * Sue lives at 123 Main
  * Joe is parent of Bob
  * Sue is parent of Bob
  * Joe is parent of Ann
  * Sue is parent of Ann

The related query is raw--it returns a raw query instead of a query
set.

```python
>>> raw = joe.related('livesAt')
>>> raw
<RawQuerySet: SELECT DISTINCT m.id FROM tests_person m, associations_association a, associations_association b WHERE b.kind_id=a.kind_id AND a.left_id=1 AND b.left_id=m.id AND a.right_id=b.right_id AND b.left_id != a.left_id and a.kind_id=2>
>>> [p for p in raw]
[<Person: Bob>, <Person: Sue>]
>>> [p for p in joe.related('parentOf')]
[<Person: Sue>]
```





