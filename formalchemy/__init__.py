# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from formalchemy.tables import *
from formalchemy.forms import *
from formalchemy.fields import query_options

__all__ = ["FieldSet", "AbstractFieldSet", "Table", "TableConcat", "TableCollection", "form_data", "query_options"]
__version__ = "0.3"

__doc__ = """
=Concepts=

FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models)
in a HTML forms environment.

FormAlchemy eliminates boilerplate by autogenerating HTML input fields from a given
model. FormAlchemy will try to
figure out what kind of HTML code should be returned by introspecting the
model's properties and generate ready-to-use HTML code that will fit the
developer's application. 

Of course, FormAlchemy can't figure out everything,
i.e, the developer might want to display only a few columns from the given
model. Thus, FormAlchemy is also highly customizable.

=Features=

  * Generates HTML form fields from SQLAlchemy mapped classes
  * Handles object relationships (including many-to-many), not just simple data types
  * Eliminates boilerplate in templates and controllers
  * Pre-fills input fields with current or default value
  * Highly customizable HTML output
  * Validates input and displays errors in-line
  * Syncs model instances with input data
  * Easy-to-use API
  * SQLAlchemy 0.4 (0.4.1 or later) and 0.5 compatible
  * Elixir compatible (?)
  
=Quickstart=

To get started, you only need to know about one class, `FieldSet`, and a
handful of methods:

  * `render`: returns a string containing the form input html
  * `bind`: returns a new FieldSet bound to a model instance and user input data
  * `validate`: true if the form passes its validations; otherwise, false
  * `sync`: syncs the model instance that was bound to the input data

This quickstart illustrates these four methods. For full details on
customizing `FieldSet` behavior, see FormAlchemyDocumentation03.

We'll start with two simple SQLAlchemy models with a one-to-many relationship
(each User can have many Orders):

{{{
>>> from sqlalchemy import *
>>> from sqlalchemy.orm import *
>>> from sqlalchemy.ext.declarative import declarative_base
>>> engine = create_engine('sqlite://')
>>> Session = scoped_session(sessionmaker(autoflush=True, bind=engine))
>>> Base = declarative_base(engine, mapper=Session.mapper)

>>> class Order(Base):
...     __tablename__ = 'orders'
...     id = Column('id', Integer, primary_key=True)
...     user_id = Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
...     quantity = Column('quantity', Integer, nullable=False)
...     def __str__(self):
...        return 'Quantity: %s' % self.quantity

>>> class User(Base):
...     __tablename__ = 'users'
...     id = Column('id', Integer, primary_key=True)
...     name = Column('name', Unicode(30))
...     orders = relation(Order, backref='user')
...     def __str__(self):
...         return self.name

>>> Base.metadata.create_all()
>>> session = Session()

>>> bill = User(name='Bill')
>>> john = User(name='John')
>>> order1 = Order(user=bill, quantity=10)
>>> session.commit()

}}}

Now, let's render a form for editing the order we've created:

{{{
>>> from formalchemy import FieldSet
>>> from formalchemy.test import _pretty_html # obviously unnecessary in production
>>> fs = FieldSet(order1)
>>> print _pretty_html(fs.render())
<div>
 <label class="field_req" for="quantity">
  Quantity
 </label>
 <input id="quantity" name="quantity" type="text" value="10" />
</div>
<script type="text/javascript">
 //<![CDATA[
document.getElementById("quantity").focus();
//]]>
</script>
<div>
 <label class="field_req" for="user_id">
  User
 </label>
 <select id="user_id" name="user_id">
  <option value="1" selected="selected">
   Bill
  </option>
  <option value="2">
   John
  </option>
 </select>
</div>

}}}

Note how the options for the User input are automatically loaded from the
database.

Now let's process some user input. In a real application, you'd get the post
data from your request object; here we'll just hardcode some:

{{{
>>> fs = fs.bind(order1, data={'quantity': 7, 'user_id': 2})
>>> if fs.validate():
...     fs.sync()

>>> order1.quantity
7
>>> order1.user_id
2
>>> session.commit()

}}}

=FormAlchemy's current state=

FormAlchemy is in alpha stage and the API is in constant evolution. We think it's useful enough to release, but 
your code may break from one version to another until FormAlchemy 1.0 is released.

=Usage=

In the following examples, we will make the use of a arbitrary `user` model.

==Imports==
All FormAlchemy's objects live under the `formalchemy` module.

{{{
from formalchemy import FieldSet
}}}

==Binding==
Before you can render anything, you will have to bind FormAlchemy's classes to
your models. All classes that needs a model for introspecting come with a
`bind()` method:

{{{
fs = FieldSet()
fs.bind(user)
}}}

You can also bind `user` while instantiating the class:
{{{
fs = FieldSet(bind=user)
}}}

==Rendering==
All FormAlchemy objects meant for generating HTML output come with a `render`
method. This is the method that will return the appropriate HTML.

{{{
html = fs.render()
}}}

`html` now holds a string representing the HTML code.

That's about it for rendering. There's nothing more you need to do to generate
HTML output from your mapped classes.

=Available FormAlchemy classes=

The available form related classes are:
  * `FieldSet`: Used for rendering input form fields from a model, wrapping the fields in a <fieldset> and <legend> HTML tag.
  * `MultiFields`: Like FieldSet, but without the <fieldset> and <legend> HTML tags.
  * `Field`: Used for rendering a single column from a model, returning a single HTML <label> and <input> pair.

FormAlchemy has derived a little from its original goal and other, non-form
related classes have been extended to the module:
  * `Table`: Used for rendering an HTML table from a model.
  * `TableCollection`: Used for rendering a collection of models into a table.

All classes require to be bound to a model to generate HTML code. Although,
some class might require extra configuration to produce code:
  * Column level classes need to have the column name to render. This can be set using the `set_column()` method or directly while instantiating the class, passing the column's name as keyword argument `column="my_column"`.
  * Collection classes need to have a collection of models to render. This can be set using the `set_collection()` method or directly while instantiating the class, passing the collection as keyword argument `collection=my_collection_list`.

=FormAlchemy Options=
FormAlchemy has some default behaviour set. It is configured to render the most
exhaustive HTML code possible to reflect from a bound model. Although, you can
pass options to FormAlchemy to behave differently, thus altering the rendered
HTML code. This can be done in many ways:

  * By passing keyword options to the `render()` method:

{{{
fs.render(pk=False, fk=False, exclude=["private_column"])
}}}

  The options given at the render method are NOT persistant. You will need to
  pass these options everytime you call `render` to reproduce the same output
  or FormAlchemy will fallback to its default behaviour. Passing keyword
  options is usually meant to alter the HTML output on the fly.

  * At the SQLAlchemy mapped class level, by creating a `FormAlchemy` subclass, it is possible to setup attributes which names and values correspond to the keyword options passed to `render`:

{{{
class User(object):
    class FormAlchemy:
        pk = False
        fk = False
        exclude = ["private_column"]
}}}

  These attributes are persistant and will be used as FormAlchemy's default
  behaviour.

  * By passing the keyword options to FormAlchemy's `configure()` method. These options are persistant and will be used as FormAlchemy's default behaviour.

{{{
fs.configure(pk=False, fk=False, exclude=["private_column"])
}}}

  Note: In any case, options set at the SQLAlchemy mapped class level or via
  the `configure()` method will be overridden if these same keyword options are
  passed to the `render()` method.

Here are the available keyword options that can be passed to FormAlchemy:

  * `pk=True` - Won't return primary key columns if set to `False`.
  * `fk=True` - Won't return foreign key columns if set to `False`.
  * `exclude=[]` - An iterable containing column names to exclude.
  * `password=[]` - An iterable of column names that should be set as password fields.
  * `hidden=[]` - An iterable of column names that should be set as hidden fields.
  * `readonly_pk=False` - Will prohibit changes to primary key columns if set to `True`.
  * `readonly_fk=False` - Will prohibit changes to foreign key columns if set to `True`.
  * `readonly=[]` - An iterable containing column names to set as readonly.
  * `dropdown={}` - Select menus. A dict holding column names as keys, dicts as values. These dicts have at least a `opts` key used for options. `opts` holds either:
    * an iterable of option names: `["small", "medium", "large"]`. Options will have the same name and value.
    * an iterable of paired option name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`
    * a dict where dict keys are option names and dict values are option values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`
    The keys that can also be set:
    * `selected=value`: a string or a container of strings (when multiple values are selected) that will set the "selected" HTML tag to matching value options. It defaults to the model's current value, if not `None`, or the column's default.
    * Other keys passed as standard HTML attributes, like `multiple=<bool>`, `size=<integer>` and so on.

    Here is an example of how the `dropdown` option can be used:

{{{
{"meal":
    {"opts":[("Hamburger", "HB"),
             ("Cheeseburger", "CB"),
             ("Bacon Burger", "BB"),
             ("Roquefort Burger", "RB"),
             ("Pasta Burger", "PB"),
             ("Veggie Burger", "VB")],
     "selected":["CB", "BB"],    ## Or just "CB"
     "multiple":True,
     "size":3,
    }
}
}}}

  * `radio={}` - Radio buttons. A dict holding column names as keys and an iterable as values. The iterable can hold:
    * input names: `["small", "medium", "large"]`. Inputs will have the same name and value.
    * paired name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`
    * a dict where dict keys are input names and dict values are input values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`
  * `prettify` - A function through which all text meant to be displayed to the user will go. Defaults to: `"my_label".replace("_", " ").capitalize()`
  * `alias={}` - A dict holding the field name as the key and the alias name as the value. Note that aliases are beeing `prettify`ed as well.
  * `error={}` - A dict holding the field name as the key and the error message as the value.
  * `doc={}` - A dict holding the field name as the key and the help message as the value.
  * `cls_req="field_req"` - Sets the HTML class for fields that are not nullable (required).
  * `cls_opt="field_opt"` - Sets the HTML class for fields that are nullable (optional).
  * `cls_err="field_err"` - Sets the HTML class for fields that are errornous (Not implemented).
  * `span_err="span_err"` - Sets the HTML class for <span> error messages. (Not implemented)
  * `span_doc="span_doc"` - Sets the HTML class for <span> help messages. (Not implemented)

"""
