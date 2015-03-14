# Terminology #

**model**: a SQLAlchemy mapped class.

# Concepts #

FormAlchemy was designed to ease the developer's work when dealing with
SQLAlchemy mapped classes (models) in a web environement where HTML forms are
often used. The basic concept is to generate HTML input fields from a given
model that will match the model's columns definition. FormAlchemy will try to
figure out what kind of HTML code should be returned by introspecting the
model's properties and generate ready-to-use HTML code that will fit with the
developer's application. Of course, FormAlchemy can't figure out everything,
i.e, the developer might want to display only a few columns from the given
model. Thus, FormAlchemy was design to be hightly customizable as well.

During development, FormAlchemy has derived from its initial goal and also
features HTML table rendering from a single model or a collection.

# FormAlchemy's current state #

FormAlchemy is in alpha stage and the API is in constant evolution. So chances
are that your code might break from a version to another, this until FormAlchemy
1.0 is released.

# Usage #

In the following examples, we will make the use of a arbitrary SQLAlchemy
`user` model. The setup is defined as followed:

```
from sqlalchemy import *
from sqlalchemy.orm import *

meta = MetaData()

user_table = Table('users', meta,
    Column('id', Integer, primary_key=True),
    Column('email', Unicode(40), unique=True, nullable=False),
    Column('password', Unicode(20), nullable=False),
    Column('first_name', Unicode(20)),
    Column('last_name', Unicode(20)),
    Column('description', Unicode),
    Column('active', Boolean, default=True),
)

class User(object):
    pass

mapper(User, user_table)

user = User()
```

> ## Imports ##
All FormAlchemy's objects live under the `formalchemy` package.

```
# Form related classes
from formalchemy import FieldSet, Field

# Table related classes
from formalchemy import Table, TableConcat, TableCollection
```

These two combined imports are equivalent to:
```
from formalchemy import *
```

> ## Binding ##
Before you can render anything, you will have to bind your models to
FormAlchemy's classes. All classes come with a `bind()` method:

```
fs = FieldSet()
fs.bind(user)
```

You can also bind the model as a `bind` keyword argument passed during class
instantiation:
```
fs = FieldSet(bind=user)
```

or as an argument if passed in first position:
```
fs = FieldSet(user)
```

> ## Rendering ##
All FormAlchemy classes come with a `render()` method. This is the method
responsible for returning the appropriate generated HTML code.

```
html = fs.render()
```

`html` now holds a string representing the HTML code. Just `print html` to see
the rendered code:

```
<fieldset>
  <legend>User</legend>
  <div>
    <label class="field_req" for="id">Id</label>
    <input id="id" name="id" type="text" />
  </div>
  <div>
    <label class="field_req" for="email">Email</label>
    <input id="email" maxlength="40" name="email" type="text" />
  </div>
  <div>
    <label class="field_req" for="password">Password</label>
    <input id="password" maxlength="20" name="password" type="text" />
  </div>
  <div>
    <label class="field_opt" for="first_name">First name</label>
    <input id="first_name" maxlength="20" name="first_name" type="text" />
  </div>
  <div>
    <label class="field_opt" for="last_name">Last name</label>
    <input id="last_name" maxlength="20" name="last_name" type="text" />
  </div>
  <div>
    <label class="field_opt" for="description">Description</label>
    <input id="description" name="description" type="text" />
  </div>
  <div>
    <label class="field_opt" for="active">Active</label>
    <input checked="checked" id="active" name="active" type="checkbox" value="True" />
  </div>
</fieldset>
```

You can also generate HTML by directly printing `fs`:

```
# Same as fs.render()
print fs
```

That's about it for rendering. There's nothing more you need to do to generate
HTML output from your mapped classes.

# FormAlchemy options #
In the previous section, we learned to generate HTML code from a given model.
But the user might want to have a different output. As FormAlchemy was designed
with customization in mind, it is possible to alter the rendered HTML.

FormAlchemy has some default behaviour set: it is configured to render the most
exhaustive HTML code possible to reflect from a bound model. Although, you can
pass keyword arguments to FormAlchemy's classes to behave differently, thus
altering the rendered HTML code. In FormAlchemy terms, these keyword arguments
are usually designated as "options". Passing options can be done in many ways.

> ## Options via the `render()` method ##
The most straightforward way is by passing keyword arguments to the `render()`
method:

```
fs.render(pk=False, fk=False, exclude=["private_column"])
```

The options given at the render method are NOT persistant. You will need to
pass these options everytime you call `render` to reproduce the same output
or FormAlchemy will fallback to its default behaviour. Passing keyword
options is usually meant to alter the HTML output on-the-fly.

> ## Options at the SQLAlchemy class level ##
By creating a `FormAlchemy` subclass at the model level, i.e. the SQLAlchemy
mapped class, it is possible to setup attributes which names and values
correspond to the keyword arguments passed to `render()`:

```
class User(object):
    class FormAlchemy:
        pk = False
        fk = False
        exclude = ["private_column"]
```

These attributes are persistant and will be used as FormAlchemy's default
behaviour.

> ## Options via the `configure()` method ##
All classes come with a `configure()` and a `reconfigure()` method. Passing
the keyword arguments to these methods will alter the behaviour as well. These
options are persistant and will be used as FormAlchemy's default behaviour.

```
fs.configure(pk=False, fk=False, exclude=["private_column"])
```

The `configure()` method updates the class' default behaviour. Any other
previously set option will be kept intact. As opposed, the `reconfigure()`
method will clear any previously set option before reconfiguration. If no
option is passed, all set options will simply be removed.

> ## Overriding options ##
In any case, persistant options set at the SQLAlchemy class level or via the
`configure()` method will be overridden if those same options are passed to
the `render()` method.

# Alerting the output #

Back to where we were. Let's alter the output by removing the model's "id"
primary key column by passing a keyword argument:

```
print fs.render(pk=False)
<fieldset>
  <legend>User</legend>
  <div>
    <label class="field_req" for="email">Email</label>
    <input id="email" maxlength="40" name="email" type="text" />
  </div>
  <div>
    <label class="field_req" for="password">Password</label>
    <input id="password" maxlength="20" name="password" type="text" />
  </div>
  <div>
    <label class="field_opt" for="first_name">First name</label>
    <input id="first_name" maxlength="20" name="first_name" type="text" />
  </div>
  <div>
    <label class="field_opt" for="last_name">Last name</label>
    <input id="last_name" maxlength="20" name="last_name" type="text" />
  </div>
  <div>
    <label class="field_opt" for="description">Description</label>
    <input id="description" name="description" type="text" />
  </div>
  <div>
    <label class="field_opt" for="active">Active</label>
    <input checked="checked" id="active" name="active" type="checkbox" value="True" />
  </div>
</fieldset>
```

So the "id" column of our model has been excluded from rendering. By passing
`pk=False` results in not rendering the "id" primary key. In fact, if our model
had more than a single primary key, none of them would have been rendered.

So this is how you can alter the output of FormAlchemy. Multiple options can
be passed to the `render()` method:

```
print fs.render(
    pk=False,
    exclude="active",
    password="password",
    legend="This a user form",
    cls_req="must_fill",
    cls_opt="can_fill"
)
<fieldset>
  <legend>This a user Form</legend>
  <div>
    <label class="must_fill" for="email">Email</label>
    <input id="email" maxlength="40" name="email" type="text" />
  </div>
  <div>
    <label class="must_fill" for="password">Password</label>
    <input id="password" maxlength="20" name="password" type="password" />
  </div>
  <div>
    <label class="can_fill" for="first_name">First name</label>
    <input id="first_name" maxlength="20" name="first_name" type="text" />
  </div>
  <div>
    <label class="can_fill" for="last_name">Last name</label>
    <input id="last_name" maxlength="20" name="last_name" type="text" />
  </div>
  <div>
    <label class="can_fill" for="description">Description</label>
    <input id="description" name="description" type="text" />
  </div>
</fieldset>
```

Notice that the rendered HTML is a little different from the previous example:
  * `exclude` is a string (or a list of strings) containing column names to exclude. `exclude=["id", "active"]` would have returned the same content but `pk=False` is better suited for removing primary key columns.
  * `password` is a string (or a list of strings) containing column names to be masked.
  * `legend` is a string that will fill the `<legend>` tag.
  * `cls_req` and `cls_opt` are strings which are HTML classes to be set for required and optional fields respectivly.

The options given to the `render()` method are not persistant. If you call
`render()` again without passing any option, you will get unaltered HTML code.

# Available FormAlchemy classes #

The available form related classes are:
  * `FieldSet`: Used for rendering input form fields from a model, wrapping the fields in a `<fieldset>` and `<legend>` HTML tag.
  * `Field`: Used for rendering a column, returning a single HTML `<label>` and `<input>` pair.

FormAlchemy has derived a little from its original goal and other, non-form
related classes have been extended to the module:
  * `Table`: Used for rendering an HTML table from a single model.
  * `TableConcat`: Same as `Table`, but used for concatenating different types of models in the same table.
  * `TableCollection`: Used for rendering a collection of models into a table.

All classes require to be bound to a model to generate HTML code. Although,
some class might require extra configuration to produce code:
  * Column level classes need to have the column name to render. This can be set using the `set_column()` method or directly while instantiating the class, passing the column's name as keyword argument `column="my_column"`.
  * Collection classes need to have a collection of models to render. This can be set using the `set_collection()` method or directly while instantiating the class, passing the collection as keyword argument `collection=my_collection_list`.

# Available options #

Here are the available keyword options that can be passed to FormAlchemy:

> ## Column related options ##
  * `pk=True` - Won't return primary key columns if set to `False`.
  * `fk=True` - Won't return foreign key columns if set to `False`.
  * `exclude=[]` - A string or an iterable containing column names to exclude.
  * `include=[]` - A string or an iterable containing column names to include. This option will ignore passed 'pk', 'fk' and 'exclude' options.
  * `prettify` - A function through which all text meant to be displayed to the user will go. Defaults to: `"my_label".replace("_", " ").capitalize()`
  * `alias={}` - A dict holding the field name as the key and the alias name as the value. Note that aliases are beeing `prettify`ed as well.

> ## Form related options ##
  * `password=[]` - An iterable of column names that should be set as password fields.
  * `textarea={}` - A dict holding column names as keys and a string or tuple specifying the dimensions of the textarea as value. `{"comments":"25x10"}` or `{"comments":(25, 10)}`
  * `hidden=[]` - An iterable of column names that should be set as hidden fields. Note: A primary key or a foreign key column set as 'hidden' will be generated even if 'pk=False' or 'fk=False' options were set.
  * `readonly_pk=False` - Will prohibit changes to primary key columns if set to `True`.
  * `readonly_fk=False` - Will prohibit changes to foreign key columns if set to `True`.
  * `readonly=[]` - A string or iterable containing column names to set as readonly.
  * `disable_pk=True` - Will grey out field of primary key columns if set to `True`.
  * `disable_fk=True` - Will grey out field of foreign key columns if set to `True`.
  * `disable=[]`  - A string or iterable containing column names to set as disabled.
  * `date_as="%Y-%m-%d"` - Display Date columns as the given format codes. Please read more about [format codes](http://www.python.org/doc/current/lib/module-time.html#l2h-2816) and their [behaviour](http://www.python.org/doc/current/lib/strftime-behavior.html#strftime-behavior).
  * `time_as="%H:%M:%S"` - Display Time columns as the given format codes.
  * `datetime_as="%s %s" % (date_as, time_as)` - Display DateTime columns as the given format codes.
  * `dropdown={}` - Select menus. A dict holding column names as keys, dicts as values. These dicts have at least a `opts` key used for options. `opts` holds either:
    * an iterable of option names: `["small", "medium", "large"]`. Options will have the same name and value.
    * an iterable of paired option name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`
    * a dict where dict keys are option names and dict values are option values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`
> > The keys that can also be set:
    * `selected=value`: a string or a container of strings (when multiple values are selected) that will set the "selected" HTML tag to matching value options. It defaults to the model's current value, if not `None`, or the column's default.
    * Other keys passed as standard HTML attributes, like `multiple=<bool>`, `size=<integer>` and so on.


> Here is an example of how the `dropdown` option can be used:

```
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
```

  * `radio={}` - Radio buttons. A dict holding column names as keys and an iterable as values. The iterable can hold:
    * input names: `["small", "medium", "large"]`. Inputs will have the same name and value.
    * paired name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`
    * a dict where dict keys are input names and dict values are input values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`
  * `bool_as_radio=[]` - Boolean columns will render as 'True' / 'False' radio buttons rather than a checkbox.
  * `make_label=True` - Will not render the `<label>` tag, neither the container `<div>` tag if set to `False`. Just the raw `<input>` field.
  * `legend=True` - Set the HTML legend text. If a string is passed, this will fill the `<legend>` tag with the given string. If `True` (default), it will take the model's class name and prettify it. If set to `False`, it won't render the `<legend>` tag.
  * `fieldset=True` - If set to `False`, it won't render the `<fieldset>` tag. The `legend` option is then ignored.
  * `focus_on=True` - A string holding the column name be focus on. By default, it will set the focus on the first rendered field. Setting it to `False` won't set any focusing.
  * `error={}` - A dict holding the field name as the key and the error message as the value.
  * `doc={}` - A dict holding the field name as the key and the help message as the value.
  * `cls_req="field_req"` - Set the HTML class for fields that are not nullable (required).
  * `cls_opt="field_opt"` - Set the HTML class for fields that are nullable (optional).
  * `cls_err="field_err"` - (Not implemented) Set the HTML class for fields that are errornous
  * `span_err="span_err"` - (Not implemented) Set the HTML class for `<span>` error messages.
  * `span_doc="span_doc"` - (Not implemented) Set the HTML class for `<span>` help messages.

> ## Table related options ##
  * `caption=True` - Set the HTML table caption text when a model is rendered as table. If a string is passed, this will fill the `<caption>` tag with the given string. If `True` (default), it will take the model's class name and prettify it. If set to `False`, it won't render the `<caption>` tag.
  * `caption_collection=True` - Same as `caption`, but displayed when a collection of models are rendered in a table.
  * `collection_size=True` - Render the size of the collection in the caption.
  * `extra_col=None` - (Not implemented) Insert an extra column that can be filled through the "display" attribute using "extra" as the column name.

> ## Validation related options ##
  * `validate={}` - (Not implemented) A dict holding column names as keys and a validating functions (or a list of function) as values.