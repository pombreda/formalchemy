import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

from BeautifulSoup import BeautifulSoup # required for html prettification

from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

from fields import Field, SelectFieldRenderer, FieldRenderer, TextFieldRenderer
import fatypes as types

engine = create_engine('sqlite://')
Session = scoped_session(sessionmaker(autoflush=True, bind=engine))
Base = declarative_base(engine, mapper=Session.mapper)

class One(Base):
    __tablename__ = 'ones'
    id = Column('id', Integer, primary_key=True)

class Two(Base):
    __tablename__ = 'twos'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Integer, default='133', nullable=True)

class Three(Base):
    __tablename__ = 'threes'
    id = Column('id', Integer, primary_key=True)
    foo = Column('foo', Text, nullable=True)
    bar = Column('bar', Text, nullable=True)
    
class CheckBox(Base):
    __tablename__ = 'checkboxes'
    id = Column('id', Integer, primary_key=True)
    field = Column('field', Boolean, nullable=False)

class Binaries(Base):
    __tablename__ = 'binaries'
    id = Column('id', Integer, primary_key=True)
    file = Column('file', Binary, nullable=True)

vertices = Table('vertices', Base.metadata, 
    Column('id', Integer, primary_key=True),
    Column('x1', Integer),
    Column('y1', Integer),
    Column('x2', Integer),
    Column('y2', Integer),
    )

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __composite_values__(self):
        return [self.x, self.y]            
    def __eq__(self, other):
        return other.x == self.x and other.y == self.y
    def __ne__(self, other):
        return not self.__eq__(other)

class Vertex(object):
    pass

Session.mapper(Vertex, vertices, properties={
    'start':composite(Point, vertices.c.x1, vertices.c.y1),
    'end':composite(Point, vertices.c.x2, vertices.c.y2)
})

class VertexFieldRenderer(FieldRenderer):
    def render(self, **kwargs):
        import helpers as h
        data = self.field.parent.data
        x_name = self.name + '-x'
        y_name = self.name + '-y'
        x_value = (data is not None and x_name in data) and data[x_name] or str(self._value and self._value.x or '')
        y_value = (data is not None and y_name in data) and data[y_name] or str(self._value and self._value.y or '')
        return h.text_field(x_name, value=x_value) + h.text_field(y_name, value=y_value)
    def deserialize(self):
        data = self.field.parent.data.getone(self.name + '-x'), self.field.parent.data.getone(self.name + '-y')
        return Point(*[int(i) for i in data])
    

# todo: test a CustomBoolean, using a TypeDecorator --
# http://www.sqlalchemy.org/docs/04/types.html#types_custom
# probably need to add _renderer attr and check
# isinstance(getattr(myclass, '_renderer', type(myclass)), Boolean)
# since the custom class shouldn't really inherit from Boolean

class OTOChild(Base):
    __tablename__ = 'one_to_one_child'
    id = Column('id', Integer, primary_key=True)
    baz = Column('foo', Text, nullable=False)
    
class OTOParent(Base):
    __tablename__ = 'one_to_one_parent'
    id = Column('id', Integer, primary_key=True)
    oto_child_id = Column('oto_child_id', Integer, ForeignKey('one_to_one_child.id'), nullable=False)
    child = relation(OTOChild, uselist=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column('quantity', Integer, nullable=False)
    def __str__(self):
        return 'Quantity: %s' % self.quantity
    
class User(Base):
    __tablename__ = 'users'
    id = Column('id', Integer, primary_key=True)
    email = Column('email', Unicode(40), unique=True, nullable=False)
    password = Column('password', Unicode(20), nullable=False)
    name = Column('name', Unicode(30))
    orders = relation(Order, backref='user')
    def __str__(self):
        return self.name
    
class NaturalOrder(Base):
    __tablename__ = 'natural_orders'
    id = Column('id', Integer, primary_key=True)
    user_email = Column('user_email', String, ForeignKey('natural_users.email'), nullable=False)
    quantity = Column('quantity', Integer, nullable=False)
    def __str__(self):
        return 'Quantity: %s' % self.quantity
    
class NaturalUser(Base):
    __tablename__ = 'natural_users'
    email = Column('email', Unicode(40), primary_key=True)
    password = Column('password', Unicode(20), nullable=False)
    name = Column('name', Unicode(30))
    orders = relation(NaturalOrder, backref='user')
    def __str__(self):
        return self.name

# test property order for non-declarative mapper
addresses = Table('email_addresses', Base.metadata,
    Column('address_id', Integer, Sequence('address_id_seq', optional=True), primary_key = True),
    Column('address', String(40)),
)
users2 = Table('users2', Base.metadata,
    Column('user_id', Integer, Sequence('user_id_seq', optional=True), primary_key = True),
    Column('address_id', Integer, ForeignKey(addresses.c.address_id)),
    Column('name', String(40), nullable=False)
)
class Address(object): pass
class User2(object): pass
mapper(Address, addresses)
mapper(User2, users2, properties={'address': relation(Address)})


class Manual(object):
    a = Field()
    b = Field(type=types.Integer).dropdown([('one', 1), ('two', 2)])


class Order__User(Base):
    __table__ = join(Order.__table__, User.__table__).alias('__orders__users')

Base.metadata.create_all()

session = Session()

bill = User(email='bill@example.com', 
            password='1234',
            name='Bill')
john = User(email='john@example.com', 
            password='5678',
            name='John')
order1 = Order(user=bill, quantity=10)
order2 = Order(user=john, quantity=5)

nbill = NaturalUser(email='nbill@example.com', 
                    password='1234',
                    name='Natural Bill')
njohn = NaturalUser(email='njohn@example.com', 
                    password='5678',
                    name='Natural John')
norder1 = NaturalOrder(user=nbill, quantity=10)
norder2 = NaturalOrder(user=njohn, quantity=5)

session.commit()


from forms import FieldSet as DefaultFieldSet, render_tempita, render_readonly
try:
    import mako
except ImportError:
    pass
from fields import Field, query_options
from validators import ValidationError

def pretty_html(html):
    soup = BeautifulSoup(html)
    return soup.prettify().strip()

class FieldSet(DefaultFieldSet):
    def render(self):
        if self.readonly:
            return pretty_html(DefaultFieldSet.render(self))
        html = pretty_html(DefaultFieldSet.render(self))
        if 'mako' in globals():
            # FS will use mako by default, so test tempita for equivalence here
            F_ = lambda s: s
            html_tempita = pretty_html(render_tempita(fieldset=self, F_=F_))
            assert html == html_tempita
        return html

def configure_and_render(fs, **options):
    fs.configure(**options)
    return fs.render()

if not hasattr(__builtins__, 'sorted'):
    # 2.3 support
    def sorted(L, key=None):
        assert key
        L = list(L)
        L.sort(lambda a, b: cmp(key(a), key(b)))
        return L


two = Two()
fs_2 = FieldSet(two, data={'Two--foo': ''})
fs_2.foo.value

__doc__ = r"""
# some low-level testing first
>>> fs = FieldSet(order1)
>>> fs._raw_fields()
[AttributeField(id), AttributeField(user_id), AttributeField(quantity), AttributeField(user)]
>>> fs.user.name
'user_id'

>>> fs = FieldSet(bill)
>>> fs._raw_fields()
[AttributeField(id), AttributeField(email), AttributeField(password), AttributeField(name), AttributeField(orders)]
>>> fs.orders.name
'orders'

>>> fs = FieldSet(User2)
>>> fs._raw_fields()
[AttributeField(user_id), AttributeField(address_id), AttributeField(name), AttributeField(address)]

>>> fs = FieldSet(One)
>>> fs.configure(pk=True, focus=None)
>>> fs.id.is_required()
True
>>> print fs.render()
<div>
 <label class="field_req" for="One--id">
  Id
 </label>
 <input id="One--id" name="One--id" type="text" />
</div>

>>> fs = FieldSet(Two)
>>> fs.configure(pk=True)
>>> print fs.render()
<div>
 <label class="field_req" for="Two--id">
  Id
 </label>
 <input id="Two--id" name="Two--id" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--id").focus();
//]]>
</script>
<div>
 <label class="field_opt" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>

>>> fs = FieldSet(Two)
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> fs.configure(options=[fs.foo.label('A custom label')])
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
  A custom label
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert fs.render() == configure_and_render(fs, include=[fs.foo])
>>> assert fs.render() == configure_and_render(fs, exclude=[fs.id])

>>> fs = FieldSet(Two) 
>>> fs.configure(include=[fs.foo.hidden()])
>>> print fs.render()
<input id="Two--foo" name="Two--foo" type="hidden" value="133" />

>>> fs = FieldSet(Two)
>>> fs.configure(include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])])
>>> print fs.render()
<div>
 <label class="field_opt" for="Two--foo">
  Foo
 </label>
 <select id="Two--foo" name="Two--foo">
  <option value="value1">
   option1
  </option>
  <option value="value2">
   option2
  </option>
 </select>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Two--foo").focus();
//]]>
</script>

>>> fs = FieldSet(Two)
>>> assert configure_and_render(fs, include=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) == configure_and_render(fs, options=[fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')])]) 
>>> print pretty_html(fs.foo.render(onblur='test()'))
<select id="Two--foo" name="Two--foo" onblur="test()">
 <option value="value1">
  option1
 </option>
 <option value="value2">
  option2
 </option>
</select>
>>> print fs.foo.reset().render(onblur='test')
<input id="Two--foo" name="Two--foo" onblur="test" type="text" value="133" />

# test sync
>>> print session.query(One).count()
0
>>> fs_1 = FieldSet(One, data={})
>>> fs_1.sync()
>>> session.flush()
>>> print session.query(One).count()
1
>>> session.rollback()

>>> cb = CheckBox()
>>> fs_cb = FieldSet(cb)
>>> print fs_cb.field.dropdown().render()
<select id="CheckBox--field" name="CheckBox--field"><option value="True">Yes</option>
<option value="False">No</option></select>
>>> fs_cb.rebind(data={})
>>> print fs_cb.field.render()
<input id="CheckBox--field" name="CheckBox--field" type="checkbox" value="True" />
>>> fs_cb.field.renderer #doctest: +ELLIPSIS
<formalchemy.fields.CheckBoxFieldRenderer object at ...>
>>> fs_cb.field.renderer._serialized_value() == None
True
>>> fs_cb.validate()
True
>>> fs_cb.errors
{}
>>> fs_cb.sync()
>>> cb.field
False
>>> fs_cb.rebind(data={'CheckBox--field': 'True'})
>>> fs_cb.validate()
True
>>> fs_cb.sync()
>>> cb.field
True
>>> fs_cb.configure(options=[fs_cb.field.dropdown()])
>>> fs_cb.rebind(data={'CheckBox--field': 'False'})
>>> fs_cb.sync()
>>> cb.field
False

>>> fs = FieldSet(Two)
>>> print fs.foo.dropdown(options=['one', 'two']).radio().render() 
<input id="Two--foo_one" name="Two--foo" type="radio" value="one" />one<br /><input id="Two--foo_two" name="Two--foo" type="radio" value="two" />two
>>> assert fs.foo.radio(options=['one', 'two']).render() == fs.foo.dropdown(options=['one', 'two']).radio().render()
>>> print fs.foo.radio(options=['one', 'two']).dropdown().render()
<select id="Two--foo" name="Two--foo"><option value="one">one</option>
<option value="two">two</option></select>
>>> assert fs.foo.dropdown(options=['one', 'two']).render() == fs.foo.radio(options=['one', 'two']).dropdown().render()
>>> print fs.foo.dropdown(options=['one', 'two'], multiple=True).checkbox().render() 
<input id="Two--foo" name="Two--foo" type="checkbox" value="one" />one<br /><input id="Two--foo" name="Two--foo" type="checkbox" value="two" />two

>>> fs = FieldSet(User)
>>> print fs.render()
<div>
 <label class="field_req" for="User--email">
  Email
 </label>
 <input id="User--email" maxlength="40" name="User--email" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("User--email").focus();
//]]>
</script>
<div>
 <label class="field_req" for="User--password">
  Password
 </label>
 <input id="User--password" maxlength="20" name="User--password" type="text" />
</div>
<div>
 <label class="field_opt" for="User--name">
  Name
 </label>
 <input id="User--name" maxlength="30" name="User--name" type="text" />
</div>
<div>
 <label class="field_opt" for="User--orders">
  Orders
 </label>
 <select id="User--orders" multiple="multiple" name="User--orders" size="5">
  <option value="1">
   Quantity: 10
  </option>
  <option value="2">
   Quantity: 5
  </option>
 </select>
</div>
>>> FieldSet(User).render() == FieldSet(User, session).render()
True

>>> fs = FieldSet(bill)
>>> print fs.orders.render()
<select id="User-1-orders" multiple="multiple" name="User-1-orders" size="5"><option value="1" selected="selected">Quantity: 10</option>
<option value="2">Quantity: 5</option></select>
>>> print fs.orders.radio().render()
<input id="User-1-orders_1" name="User-1-orders" type="radio" value="1" />Quantity: 10<br /><input id="User-1-orders_2" name="User-1-orders" type="radio" value="2" />Quantity: 5
>>> print fs.orders.radio(options=query_options(session.query(Order).filter_by(id=1))).render()
<input id="User-1-orders_1" name="User-1-orders" type="radio" value="1" />Quantity: 10

>>> fs = FieldSet(Two)
>>> print fs.foo.render()
<input id="Two--foo" name="Two--foo" type="text" value="133" />

>>> fs = FieldSet(Two)
>>> print fs.foo.dropdown([('option1', 'value1'), ('option2', 'value2')]).render()
<select id="Two--foo" name="Two--foo"><option value="value1">option1</option>
<option value="value2">option2</option></select>

>>> fs = FieldSet(Order, session)
>>> print fs.render()
<div>
 <label class="field_req" for="Order--quantity">
  Quantity
 </label>
 <input id="Order--quantity" name="Order--quantity" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Order--quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="Order--user_id">
  User
 </label>
 <select id="Order--user_id" name="Order--user_id">
  <option value="1">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

# this seems particularly prone to errors; break it out in its own test
>>> fs = FieldSet(order1)
>>> fs.user.value
1

# test re-binding
>>> fs = FieldSet(Order)
>>> fs.configure(pk=True, options=[fs.quantity.hidden()])
>>> fs.rebind(order1)
>>> fs.quantity.value
10
>>> fs.session == object_session(order1)
True
>>> print fs.render()
<div>
 <label class="field_req" for="Order-1-id">
  Id
 </label>
 <input id="Order-1-id" name="Order-1-id" type="text" value="1" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("Order-1-id").focus();
//]]>
</script>
<input id="Order-1-quantity" name="Order-1-quantity" type="hidden" value="10" />
<div>
 <label class="field_req" for="Order-1-user_id">
  User
 </label>
 <select id="Order-1-user_id" name="Order-1-user_id">
  <option value="1" selected="selected">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

>>> fs = FieldSet(One)
>>> fs.configure(pk=True)
>>> print fs.render()
<div>
 <label class="field_req" for="One--id">
  Id
 </label>
 <input id="One--id" name="One--id" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("One--id").focus();
//]]>
</script>
>>> fs.configure(include=[])
>>> print fs.render()
<BLANKLINE>
>>> fs.configure(pk=True, focus=None)
>>> print fs.render()
<div>
 <label class="field_req" for="One--id">
  Id
 </label>
 <input id="One--id" name="One--id" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.rebind(Two) #doctest: +ELLIPSIS
Traceback (most recent call last):
...
ValueError: ...

>>> fs = FieldSet(Two)
>>> fs.configure()
>>> fs2 = fs.bind(Two)
>>> [fs2 == field.parent for field in fs2._render_fields.itervalues()]
[True]

>>> fs = FieldSet(OTOParent, session)
>>> print fs.render()
<div>
 <label class="field_req" for="OTOParent--oto_child_id">
  Child
 </label>
 <select id="OTOParent--oto_child_id" name="OTOParent--oto_child_id">
 </select>
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("OTOParent--oto_child_id").focus();
//]]>
</script>

# validation + sync
>>> two = Two()
>>> fs_2 = FieldSet(two, data={'Two--foo': ''})
>>> fs_2.foo.value # '' is deserialized to None, so default of 133 is used
'133'
>>> fs_2.validate()
True
>>> fs_2.configure(options=[fs_2.foo.required()], focus=None)
>>> fs_2.validate()
False
>>> fs_2.errors
{AttributeField(foo): ['Please enter a value']}
>>> print fs_2.render()
<div>
 <label class="field_req" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="133" />
 <span class="field_error">
  Please enter a value
 </span>
</div>
>>> fs_2.rebind(two, data={'Two--foo': 'asdf'})
>>> fs_2.data
{'Two--foo': 'asdf'}
>>> fs_2.validate()
False
>>> fs_2.errors
{AttributeField(foo): [ValidationError('Value is not an integer',)]}
>>> print fs_2.render()
<div>
 <label class="field_req" for="Two--foo">
  Foo
 </label>
 <input id="Two--foo" name="Two--foo" type="text" value="asdf" />
 <span class="field_error">
  Value is not an integer
 </span>
</div>
>>> fs_2.rebind(two, data={'Two--foo': '2'})
>>> fs_2.data
{'Two--foo': '2'}
>>> fs_2.validate()
True
>>> fs_2.errors
{}
>>> fs_2.sync()
>>> two.foo
2
>>> session.flush()
>>> print fs_2.render() #doctest: +ELLIPSIS
Traceback (most recent call last):
...
Exception: Primary key of model has changed since binding, probably due to sync()ing a new instance.  You can solve this by either binding to a model with the original primary key again, or by binding data to None.
>>> session.rollback()

>>> one = One()
>>> fs_1 = FieldSet(one, data={'One--id': '1'})
>>> fs_1.configure(pk=True)
>>> fs_1.validate()
True
>>> fs_1.sync()
>>> one.id
1
>>> fs_1.rebind(one, data={'One-1-id': 'asdf'})
>>> fs_1.id.renderer.name
'One-1-id'
>>> fs_1.validate()
False
>>> fs_1.errors
{AttributeField(id): [ValidationError('Value is not an integer',)]}

>>> fs_u = FieldSet(User, data={})
>>> fs_u.configure(include=[fs_u.orders])
>>> fs_u.validate()
True
>>> fs_u.sync()
>>> fs_u.model.orders
[]
>>> fs_u.rebind(User, session, data={'User--orders': [str(order1.id), str(order2.id)]})
>>> fs_u.validate()
True
>>> fs_u.sync()
>>> fs_u.model.orders == [order1, order2]
True
>>> session.rollback()

>>> fs_3 = FieldSet(Three, data={'Three--foo': 'asdf', 'Three--bar': 'fdsa'})
>>> fs_3.foo.value
'asdf'
>>> print fs_3.foo.textarea().render()
<textarea id="Three--foo" name="Three--foo">asdf</textarea>
>>> print fs_3.foo.textarea("3x4").render()
<textarea cols="3" id="Three--foo" name="Three--foo" rows="4">asdf</textarea>
>>> print fs_3.foo.textarea((3,4)).render()
<textarea cols="3" id="Three--foo" name="Three--foo" rows="4">asdf</textarea>
>>> fs_3.bar.value
'fdsa'
>>> def custom_validator(fs):
...   if fs.foo.value != fs.bar.value:
...     fs.foo.errors.append('does not match bar')
...     raise ValidationError('foo and bar do not match')
>>> fs_3.configure(global_validator=custom_validator, focus=None)
>>> fs_3.validate()
False
>>> fs_3.errors
{None: ('foo and bar do not match',), AttributeField(foo): ['does not match bar']}
>>> print fs_3.render()
<div class="fieldset_error">
 foo and bar do not match
</div>
<div>
 <label class="field_opt" for="Three--foo">
  Foo
 </label>
 <input id="Three--foo" name="Three--foo" type="text" value="asdf" />
 <span class="field_error">
  does not match bar
 </span>
</div>
<div>
 <label class="field_opt" for="Three--bar">
  Bar
 </label>
 <input id="Three--bar" name="Three--bar" type="text" value="fdsa" />
</div>

# natural PKs
>>> fs_npk = FieldSet(NaturalOrder, session)
>>> print fs_npk.render()
<div>
 <label class="field_req" for="NaturalOrder--quantity">
  Quantity
 </label>
 <input id="NaturalOrder--quantity" name="NaturalOrder--quantity" type="text" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("NaturalOrder--quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="NaturalOrder--user_email">
  User
 </label>
 <select id="NaturalOrder--user_email" name="NaturalOrder--user_email">
  <option value="nbill@example.com">
   Natural Bill
  </option>
  <option value="njohn@example.com">
   Natural John
  </option>
 </select>
</div>
>>> fs_npk.rebind(norder2, session, data={'NaturalOrder-2-user_email': nbill.email, 'NaturalOrder-2-quantity': str(norder2.quantity)})
>>> fs_npk.user_email.renderer.name
'NaturalOrder-2-user_email'
>>> fs_npk.sync()
>>> fs_npk.model.user_email == nbill.email
True
>>> session.rollback()

# allow attaching custom attributes to wrappers
>>> fs = FieldSet(User)
>>> fs.name.baz = 'asdf'
>>> fs2 = fs.bind(bill)
>>> fs2.name.baz
'asdf'

# equality can tell an field bound to an instance is the same as one bound to a type
>>> fs.name == fs2.name
True

# Field
>>> fs = FieldSet(One)
>>> fs.add(Field('foo'))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <input id="One--foo" name="One--foo" type="text" />
</div>

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=2))
>>> fs.foo.value
2
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <input id="One--foo" name="One--foo" type="text" value="2" />
</div>
>>> fs.rebind(One, data={'One--foo': '4'})
>>> fs.sync()
>>> fs.foo.value
4

>>> fs = FieldSet(Manual)
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="Manual--a">
  A
 </label>
 <input id="Manual--a" name="Manual--a" type="text" />
</div>
<div>
 <label class="field_opt" for="Manual--b">
  B
 </label>
 <select id="Manual--b" name="Manual--b">
  <option value="1">
   one
  </option>
  <option value="2">
   two
  </option>
 </select>
</div>
>>> fs.rebind(Manual, data={'Manual--a': 'asdf'})
>>> print pretty_html(fs.a.render())
<input id="Manual--a" name="Manual--a" type="text" value="asdf" />

>>> print pretty_html(fs.a.render(readonly=True))
asdf

>>> print pretty_html(fs.a.render(disabled=True))
<input disabled="disabled" id="Manual--a" name="Manual--a" type="text" value="asdf" />

>>> fs = FieldSet(One)
>>> fs.add(Field('foo', types.Integer, value=2).dropdown(options=[('1', 1), ('2', 2)]))
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <select id="One--foo" name="One--foo">
  <option value="1">
   1
  </option>
  <option value="2" selected="selected">
   2
  </option>
 </select>
</div>

# test Field __hash__, __eq__
>>> fs.foo == fs.foo.dropdown(options=[('1', 1), ('2', 2)])
True

>>> fs2 = FieldSet(One)
>>> fs2.add(Field('foo', types.Integer, value=2))
>>> fs2.configure(options=[fs2.foo.dropdown(options=[('1', 1), ('2', 2)])], focus=None)
>>> fs.render() == fs2.render()
True
>>> print fs2.foo.with_renderer(FieldRenderer).render()
<input id="One--foo" name="One--foo" type="text" value="2" />

>>> fs_1 = FieldSet(One)
>>> fs_1.add(Field('foo', types.Integer, value=[2, 3]).dropdown(options=[('1', 1), ('2', 2), ('3', 3)], multiple=True))
>>> print configure_and_render(fs_1, focus=None)
<div>
 <label class="field_opt" for="One--foo">
  Foo
 </label>
 <select id="One--foo" multiple="multiple" name="One--foo" size="5">
  <option value="1">
   1
  </option>
  <option value="2" selected="selected">
   2
  </option>
  <option value="3" selected="selected">
   3
  </option>
 </select>
</div>
>>> fs_1.rebind(One, data={'One--foo': ['1', '2']})
>>> fs_1.sync()
>>> fs_1.foo.value
[1, 2]

# test attribute names
>>> fs = FieldSet(One)
>>> fs.add(Field('foo'))
>>> fs.foo == fs._fields['foo']
True
>>> fs.add(Field('add'))
>>> fs.add == fs._fields['add']
False

# change default renderer 
>>> class BooleanSelectRenderer(SelectFieldRenderer):
...     def render(self, **kwargs):
...         kwargs['options'] = [('Yes', True), ('No', False)]
...         return SelectFieldRenderer.render(self, **kwargs)
>>> d = dict(FieldSet.default_renderers)
>>> d[types.Boolean] = BooleanSelectRenderer
>>> fs = FieldSet(CheckBox)
>>> fs.default_renderers = d
>>> print fs.field.render()
<select id="CheckBox--field" name="CheckBox--field"><option value="True">Yes</option>
<option value="False">No</option></select>

# test setter rejection
>>> fs = FieldSet(One)
>>> fs.id = fs.id.required()
Traceback (most recent call last):
...
AttributeError: Do not set field attributes manually.  Use add() or configure() instead

# join
>>> fs = FieldSet(Order__User)
>>> fs._fields.values()
[AttributeField(orders_id), AttributeField(orders_user_id), AttributeField(orders_quantity), AttributeField(users_id), AttributeField(users_email), AttributeField(users_password), AttributeField(users_name)]
>>> fs.rebind(session.query(Order__User).filter_by(orders_id=1).one())
>>> print configure_and_render(fs, focus=None)
<div>
 <label class="field_req" for="Order__User-1-orders_quantity">
  Orders quantity
 </label>
 <input id="Order__User-1-orders_quantity" name="Order__User-1-orders_quantity" type="text" value="10" />
</div>
<div>
 <label class="field_req" for="Order__User-1-users_email">
  Users email
 </label>
 <input id="Order__User-1-users_email" maxlength="40" name="Order__User-1-users_email" type="text" value="bill@example.com" />
</div>
<div>
 <label class="field_req" for="Order__User-1-users_password">
  Users password
 </label>
 <input id="Order__User-1-users_password" maxlength="20" name="Order__User-1-users_password" type="text" value="1234" />
</div>
<div>
 <label class="field_opt" for="Order__User-1-users_name">
  Users name
 </label>
 <input id="Order__User-1-users_name" maxlength="30" name="Order__User-1-users_name" type="text" value="Bill" />
</div>
>>> fs.rebind(session.query(Order__User).filter_by(orders_id=1).one(), data={'Order__User-1-orders_quantity': '5', 'Order__User-1-users_email': bill.email, 'Order__User-1-users_password': '5678', 'Order__User-1-users_name': 'Bill'})
>>> fs.validate()
True
>>> fs.sync()
>>> session.flush()
>>> session.refresh(bill)
>>> bill.password == '5678'
True
>>> session.rollback()

>>> FieldSet.default_renderers[Vertex] = VertexFieldRenderer
>>> fs = FieldSet(Vertex)
>>> print pretty_html(fs.start.render())
<input id="Vertex--start-x" name="Vertex--start-x" type="text" value="" />
<input id="Vertex--start-y" name="Vertex--start-y" type="text" value="" />
>>> v = Vertex()
>>> v.start = Point(1,2)
>>> v.end = Point(3,4)
>>> fs.rebind(v)
>>> print pretty_html(fs.start.render())
<input id="Vertex--start-x" name="Vertex--start-x" type="text" value="1" />
<input id="Vertex--start-y" name="Vertex--start-y" type="text" value="2" />
>>> fs.rebind(v, data={'Vertex--start-x': '10', 'Vertex--start-y': '20', 'Vertex--end-x': '30', 'Vertex--end-y': '40'})
>>> fs.validate()
True
>>> fs.sync()
>>> session.flush()
>>> v.id
1
>>> session.refresh(v)
>>> v.start.x
10
>>> v.end.y
40
>>> session.rollback()

>>> t = FieldSet(bill)
>>> t.configure(readonly=True)
>>> t.readonly
True
>>> print pretty_html(t.render())
<tbody>
 <tr>
  <td class="field_readonly">
   Email:
  </td>
  <td>
   bill@example.com
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Password:
  </td>
  <td>
   1234
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Name:
  </td>
  <td>
   Bill
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Orders:
  </td>
  <td>
   Quantity: 10
  </td>
 </tr>
</tbody>

>>> t = FieldSet(bill)
>>> t.configure(options=[t.email.with_renderer(TextFieldRenderer)] ,readonly=True)
>>> print pretty_html(t.render())
<tbody>
 <tr>
  <td class="field_readonly">
   Email:
  </td>
  <td>
   <input id="User-1-email" maxlength="40" name="User-1-email" type="text" value="bill@example.com" />
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Password:
  </td>
  <td>
   1234
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Name:
  </td>
  <td>
   Bill
  </td>
 </tr>
 <tr>
  <td class="field_readonly">
   Orders:
  </td>
  <td>
   Quantity: 10
  </td>
 </tr>
</tbody>


"""

if __name__ == '__main__':
    import doctest
    doctest.testmod()
