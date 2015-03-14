# Models #

In the following examples, we will make the use of the SQLAlchemy
`User` and `Order` models defined in the
[QuickStart](http://code.google.com/p/formalchemy/).


# Imports #

All FormAlchemy's objects live under the `formalchemy` package.

```
# Form related classes
from formalchemy import FieldSet, Field

# helper functions
from formalchemy import form_data, query_options

# validation
from formalchemy import validators, ValidationException

# for manual Field definition
from formalchemy import types

# Collection rendering
from formalchemy import Grid

# Advanced customization
from formalchemy import FieldRenderer, AbstractFieldSet
```

The above imports are equivalent to
```
from formalchemy import *
```


# Configuring and rendering forms #

## Binding ##

FormAlchemy `FieldSet` constructors take three parameters:

  * `model`:
> > a SQLAlchemy mapped class or instance
  * `session=None`:
> > the session to use for queries (for relations). If `model` is
> > associated with a session, that will be used by
> > default. (Objects mapped with a
> > [http://www.sqlalchemy.org/docs/04/session.html#unitofwork_contextual
> > scoped\_session] will always have a session. Other objects will
> > also have a session if they were loaded by a Query.)
  * `data=None`:
> > dictionary of user-submitted data to validate and/or sync to
> > the `model`. Scalar attributes should have a single value in
> > the dictionary; multi-valued relations should have a list,
> > even if there are zero or one values submitted.

Only the `model` parameter is required.

After binding, the `FieldSet`.model attribute will always be an instance.
If you bound to a class, FormAlchemy will call its constructor with no
arguments to create an appropriate instance.  (This instance will not
be added to the current session, even if you are using Session.mapper.)

All of these parameters may be overridden by the `bind` or `rebind`
methods.  The `bind` method returns a new instance bound as specified,
while `rebind` modifies the current `FieldSet` and has no
return value. (You may not `bind` to a different type of SQLAlchemy
model than the initial one -- if you initially bind to a `User`, you
must subsequently bind `User`s to that `FieldSet`.)

Typically, you will configure a `FieldSet` once in a common
form library, then `bind` specific instances later for editing.  (The
`bind` method is thread-safe; `rebind` is not.)  Thus:

```
# library.py
fs = FieldSet(User)
fs.configure(...)

# controller.py
from library import fs
user = session.query(User).get(id)
fs2 = fs.bind(user)
fs2.render()
```


## Fields ##

Each `FieldSet` will have a `Field` created for each attribute of
the bound model.  Additional `Field`s may be added manually; see below.
A `Field` knows how to render itself, and most customization is done
by telling a `Field` to modify itself appropriately.

`Field`s are accessed simply as attributes of the `FieldSet`:

```
>>> fs = FieldSet(bill)
>>> fs.name.value
'Bill'
```

If you have an attribute name that conflicts with a built-in `FieldSet`
attribute, you can use the `fs.fields` dictionary instead.  So these
are equivalent:

```
fs.name == fs.fields['name']
```


## Field Modification ##

Field rendering can be modified with the following methods:

  * `validate(self, validator)`:
> > Add the `validator` function to the list of validation
> > routines to run when the `FieldSet`'s `validate` method is
> > run. Validator functions take one parameter: the value to
> > validate. This value will have already been turned into the
> > appropriate data type for the given `Field` (string, int, float,
> > etc.). It should raise `ValidationException` if validation
> > fails with a message explaining the cause of failure.
  * `required(self)`:
> > Convenience method for `validate(validators.required)`.  By
> > default, NOT NULL columns are required.  You can only add
> > required-ness, not remove it.
  * `label(self)`:
> > Change the label associated with this field.  By default, the
> > field name is used, modified for readability (e.g.,
> > 'user\_name' -> 'User name').
  * `disabled(self)`:
> > Render the field disabled.
  * `readonly(self)`:
> > Render the field readonly.
  * `hidden(self)`:
> > Render the field hidden.  (Value only, no label.)
  * `password(self)`:
> > Render the field as a password input, hiding its value.
  * `textarea(self, size=None)`:
> > Render the field as a textarea.
  * `radio(self, options=None)`:
> > Render the field as a set of radio buttons.
  * `checkbox(self, options=None)`:
> > Render the field as a set of checkboxes.
  * `dropdown(self, options=None, multiple=False, size=5)`:
> > Render the field as an HTML select field.
> > (With the `multiple` option this is not really a 'dropdown'.)

Methods taking an `options` parameter expect either an iterable of
(description, value) or a dictionary whose keys are descriptions and whose
values are the values to associate with them.

Options can be "chained" indefinitely because each modification returns a new
`Field` instance, so you can write

```
fs.add(Field('foo').dropdown(options=[('one', 1), ('two', 2)]).radio())
```

or

```
fs.configure(options=[fs.name.label('Username').readonly()])
```


## Adding Fields ##

You can add additional fields not in your SQLAlchemy model with the `add`
method, which takes a Field object as parameter.

The Field constructor takes these parameters:

  * `name`:
> > field name
  * `type=types.String`:
> > data type, from formalchemy.types (Integer, Float, String, Binary, Boolean, Date, DateTime, Time) or a custom type
  * `value=None`:
> > default value.  If value is a callable, it will be passed the current bound model instance when the value is read.  This allows creating a Field whose value depends on the model once, then binding different  instances to it later.

Other modification of manually created Fields must be done with the
methods described above, under "Field Modification."


## Fields to render ##

The `configure` method specifies a set of attributes to be rendered.
By default, all attributes are rendered except primary keys and
foreign keys.  But, relations _based on_ foreign keys _will_ be
rendered.  For example, if an `Order` has a `user_id` FK and a `user`
relation based on it, `user` will be rendered (as a select box of
`User`s, by default) but `user_id` will not.

Parameters:
  * `pk=False`:
> > set to True to include primary key columns
  * `exclude=[]`:
> > an iterable of attributes to exclude.  Other attributes will
> > be rendered normally
  * `include=[]`:
> > an iterable of attributes to include.  Other attributes will
> > not be rendered
  * `options=[]`:
> > an iterable of modified attributes.  The set of attributes to
> > be rendered is unaffected
  * `global_validator=None`:
> > `global_validator` should be a function that performs
> > validations that need to know about the entire form.
  * `focus=True`:
> > the attribute (e.g., `fs.orders`) whose rendered input element
> > gets focus. Default value is True, meaning, focus the first
> > element. False means do not focus at all.
  * `readonly=False`:

> if true, the fieldset will be rendered as a table (tbody)
> > instead of a group of input elements.  Opening and closing
> > table tags are not included.

Only one of {`include`, `exclude`} may be specified.

Note that there is no option to include foreign keys.  This is
deliberate.  Use `include` if you really need to manually edit FKs.

If `include` is specified, fields will be rendered in the order given
in `include`.  Otherwise, fields will be rendered in order of declaration,
with table fields before mapped properties.  (However, mapped property order
is sometimes ambiguous, e.g. when backref is involved.  In these cases,
FormAlchemy will take its best guess, but you may have to force the
"right" order with `include`.)

Examples: given a `FieldSet` `fs` bound to a `User` instance as a
model with primary key `id` and attributes `name` and `email`, and a
relation `orders` of related Order objects, the default will be to
render `name`, `email`, and `orders`. To render the orders list as
checkboxes instead of a select, you could specify

```
fs.configure(options=[fs.orders.checkbox()]) 
```

To render only name and email,

```
fs.configure(include=[fs.name, fs.email]) 
# or
fs.configure(exclude=[fs.options]) 
```

Of course, you can include modifications to a field in the `include`
parameter, such as here, to render name and options-as-checkboxes:

```
fs.configure(include=[fs.name, fs.options.checkbox()]) 
```


## Rendering ##

Once you've configured your `FieldSet`,
just call the `render` method to get an HTML string suitable for
including in your page.

```
>>> fs = FieldSet(bill)
>>> print fs.render() 
    <div>
     <label class="field_opt" for="name">
      Name
     </label>
     <input id="name" maxlength="30" name="name" type="text" value="Bill" />
    </div>
    <script type="text/javascript">
     //<![CDATA[
    document.getElementById("name").focus();
    //]]>
    </script>
    <div>
     <label class="field_opt" for="orders">
      Orders
     </label>
     <select id="orders" multiple="multiple" name="orders" size="5">
      <option value="1" selected="selected">
       Quantity: 10
      </option>
     </select>
    </div>
```

Note that there is no `form` element!  You must provide that yourself.

You can also render individual fields for more fine-grained control:

```
>>> fs = FieldSet(bill)
>>> print fs.name.render()

    <input id="name" maxlength="30" name="name" type="text" value="Bill" />
```


# Validation #

To validate data, you must bind it to your `FieldSet` along with the
SQLAlchemy model.  Normally, you will retrieve `data` with the
`form_data` convenience method:

```
fs.rebind(bill, data=form_data(request.params))
```

Validation is performed simply by invoking `fs.validate()`, which
returns True if validation was successful, and False otherwise.
Validation functions are added with the `validate` method, described above.

If validation fails, `fs.errors` will be populated.  `errors` is a
dictionary of validation failures, and is always empty before `validate()`
is run.  Dictionary keys are attributes; values are lists of messages
given to `ValidationException`.  Global errors (not specific to a
single attribute) are under the key `None`.

Rendering a `FieldSet` with errors will result in error messages
being displayed inline.  Here's what this looks like for a required
field that was not supplied with a value:

```
<div>
 <label class="field_req" for="foo">
  Foo
 </label>
 <input id="foo" name="foo" type="text" value="" />
 <span class="field_error">
  Please enter a value
 </span>
</div>
```

If validation succeeds, you can have FormAlchemy put the submitted
data back into the bound model object with `fs.sync`.

```
>>> fs = FieldSet(bill, data={'name': 'Sam'})
>>> if fs.validate(): fs.sync()
>>> bill.name
'Sam'
```


# Validation Functions #

A validation function is simply a function that, given a value, raises
a ValidationError if it is invalid.

`formalchemy.validators` contains two types of functions: validation
functions that can be used directly, and validation function _generators_
that _return_ a validation function satisfying some conditon.  E.g.,
`validators.maxlength(30)` will return a validation function that can then
be passed to `validate`.

Validation functions:

  * `required(value)`:
> > Successful if value is neither None nor the empty string (yes, including empty lists)
  * `integer(value)`:
> > Successful if value is an int
  * `float(value)`:
> > Successful if value is a float
  * `currency(value)`:
> > Successful if value looks like a currency amount (has exactly two digits after a decimal point)
  * `email(value)`:
> > Successful if value is a valid RFC 822 email address.  Ignores the more subtle intricacies of what is legal inside a quoted region, and thus may accept some technically invalid addresses, but will never reject a valid address (which is a much worse problem).

Function generators:

  * `maxlength(length)`:
> > Returns a validator that is successful if the input's length is at most the given one.
  * `minlength(length)`:
> > Returns a validator that is successful if the input's length is at least the given one.
  * `regex(exp, errormsg='Invalid input')`:
> > Returns a validator that is successful if the input matches (that fulfils the semantics of re.match) the given expression. Expressions may be either a string or a Pattern object of the sort returned by re.compile.


# Including data from more than one class #

FormAlchemy only supports binding to a single class, but a single class can itself
include data from multiple tables.  Example:

```
class Order__User(Base):
    __table__ = join(Order.__table__, User.__table__).alias('__orders__users')
```

Such a class can then be used normally in a `FieldSet`.

See http://www.sqlalchemy.org/docs/05/mappers.html#advdatamapping_mapper_joins for full details on mapping multiple tables to a single class.


# Non-SQLAlchemy forms (experimental) #

You can create a `FieldSet` from non-SQLAlchemy, new-style (inheriting
from `object`) classes, like this:

```
class Manual(object):
    a = Field()
    b = Field(type=types.Integer).dropdown([('one', 1), ('two', 2)])

fs = FieldSet(Manual)
```

Field declaration is the same as for adding fields to a
SQLAlchemy-based `FieldSet`, except that you do not give the Field a
name (the attribute name is used).

You can still validate and sync a non-SQLAlchemy class instance, but
obviously persisting any data post-sync is up to you.


# Rendering collections #

Besides `FieldSet`, FormAlchemy provides `Grid` for editing and
rendering multiple instances at once.  Most of what you know about
`FieldSet` applies to `Grid`, with the following differences to
accomodate being bound to multiple objects:

## Binding ##

The `Grid` constructor takes the following arguments:
  * `cls`:
> > the class type that the `Grid` will render (NOT an instance)
  * `instances=[]`:
> > the instances/rows to render
  * `session=None`:
> > as in `FieldSet`
  * `data=None`:
> > as in `FieldSet`

`bind` and `rebind` take the last 3 arguments (`instances`, `session`,
and `data`); you may not specify a different class type than the one
given to the constructor.

## Configuration ##

The `Grid` `configure` method takes the same arguments as `FieldSet`
(`pk`, `exclude`, `include`, `options`, `readonly`), except there is
no `focus` argument.

## Validation and Sync ##

These are the same as in `FieldSet`, except that you can also call
`sync_one(instance)` to sync a single one of the instances that are
bound to the `Grid`.

The `Grid` `errors` attribute is a dictionary keyed by bound instance,
whose value is similar to the `errors` from a `FieldSet`, that is, a
dictionary whose keys are `Field`s, and whose values are
`ValidationError` instances.

# Customization: CSS #

FormAlchemy uses the following CSS classes:

  * `fieldset_error`: class for a div containing a "global" error
  * `field_error`: class for a span containing an error from a single `Field`
  * `field_req`: class for a label for a required field
  * `field_opt`: class for a label for an optional field
  * `field_readonly`: class for the td of the 'label' for a field in a readonly `FieldSet` table
  * `grid_error`: class for a span containing an error from a single `Field` in a `Grid`

Here is some basic CSS for aligning your forms nicely:

```
label {
    float: left;
    text-align: right;
    margin-right: 1em;
    width: 10em;
}

form div {
    margin: 0.5em;
    float: left;
    width: 100%;
}

form input[type="submit"] {
    margin-top: 1em;
    margin-left: 9em;
}
```


# Advanced Customization: Renderers #

You can write your own `FieldRenderer`s to customize the widget (input element[s](s.md)) used
to edit different types of fields..

  1. Subclass `FieldRenderer`.
    1. Override `render` to return a string containing the HTML input elements desired.  Use `self.name` to get a unique name and id for the input element.  `self._value` may also be useful if you are not rendering multiple input elements.
    1. If you are rendering a custom type (any class you defined yourself), you will need to override `deserialize` as well.  `render`	turns the user-submitted data into a Python value.  (The raw data will be available in self.field.parent.data, or you can use `_serialized_value` if it is convenient.)  For SQLAlchemy collections, return a list of primary keys, and FormAlchemy will take care of turning that into a list of objects.  For manually added collections, return a list of values.
    1. If you are rendering a builtin type with multiple input elements, override `_serialized_value` to return a single string combining the multiple input pieces.  See the source for DateFieldRenderer for an example.
  1. Update `FieldSet.default_renderers`.
> > `default_renderers` is a dict of callables returning a FieldRenderer.  Usually these
> > will be FieldRenderer subclasses, but this is not required.  The default
> > contents of default\_renderers is
```
    default_renderers = {
        types.String: fields.TextFieldRenderer,
        types.Integer: fields.IntegerFieldRenderer,
        types.Boolean: fields.BooleanFieldRenderer,
        types.DateTime: fields.DateTimeFieldRendererRenderer,
        types.Date: fields.DateFieldRenderer,
        types.Time: fields.TimeFieldRenderer,
        types.Binary: fields.FileFieldRenderer,
        'dropdown': fields.SelectFieldRenderer,
        'checkbox': fields.CheckBoxSet,
        'radio': fields.RadioSet,
        'password': fields.PasswordFieldRenderer,
        'textarea': fields.TextAreaFieldRenderer,
    }
```

For instance, to make `Boolean`s render as select fields with Yes/No
options by default, you could write:

```
    class BooleanSelectRenderer(SelectFieldRenderer):
        def render(self, **kwargs):
            kwargs['options'] = [('Yes', True), ('No', False)]
            return SelectFieldRenderer.render(self, **kwargs)

    FieldSet.default_renderers[types.Boolean] = BooleanSelectRenderer
```

Of course, you can subclass `FieldSet` if you don't want to change the defaults globally.

One more example, this one to use the
[JQuery UI DatePicker](http://docs.jquery.com/UI/Datepicker)
to render `Date` objects:

```
    class DatePickerFieldRenderer(FieldRenderer):
	def render(self):
	    vars = dict(name=self.name, value=self.value if self.value else '')
	    return """
	    <input id="%(name)s" name="%(name)s" type="text" value="%(value)s">
	    <script type="text/javascript">
		$('#%(name)s').datepicker({dateFormat: 'yy-mm-dd'})
	    </script>
	    """ % vars
```

(Obviously the page template will need to add references to the jquery library and css.)


# Advanced Customization: Form Templates #

There are two parts you can customize in a
`FieldSet` subclass short of writing your own `render` method.  These
are `prettify` and `_render`.  As in,

```
class MyFieldSet(FieldSet):
    prettify = staticmethod(myprettify)
    _render = staticmethod(myrender)
```

`prettify` is a function that, given an attribute name ('user\_name')
turns it into something usable as an HTML label ('User name').

`_render` should be a template rendering method, such as
`Template.render` from a mako Template or `Template.substitute` from a
Tempita Template.


`_render` should take as parameters:
  * `fieldset`
> > the `FieldSet` object to render

Your template will be particularly interested in these `FieldSet` attributes:
  * `render_fields`:
> > the list of fields the user has configured for rendering
  * `errors`:
> > a dictionary of validation failures, keyed on field.  `errors[None]` are errors applying to the form as a whole rather than a specific field.
  * `prettify`:
> > as above
  * `focus`:
> > the field to focus

You can also override `prettify` and `_render` on a per-`FieldSet` basis:

```
fs = FieldSet(...)
fs.prettify = myprettify
fs._render = ...
```

The default template is `formalchemy.forms.template_text_tempita`.


## Customizing Grid ##

Overriding `Grid` rendering is similar to `FieldSet`.  The differences are:

  * The default templates take a `collection` parameter instead of `fieldset`, which is the instance of `Grid` to render
  * The instances given to the collection are available in `collection.rows`; to access the fields of each single row, call `_set_active(row)`, then access `render_fields`.

The default templates are `formalchemy.tables.template_grid_readonly` and `formalchemy.tables.template_grid`.


# Really advanced customization #

You can derive your own subclasses from `FieldSet` or `AbstractFieldSet`
to provide a customized `render` and/or `configure`.

`AbstractBaseSet` encorporates validation/errors logic and provides a default
`configure` method.  It does _not_ provide `render`.

You can write `render` by manually sticking strings together if that's
what you want, but we recommend using a templating package for clarity
and maintainability.  FormAlchemy includes the Tempita templating
package as formalchemy.tempita; see http://pythonpaste.org/tempita/
for documentation.

`formalchemy.forms.template_text_tempita` is the default template used
by `FieldSet.` FormAlchemy also includes a Mako version,
`formalchemy.forms.template_text_mako`, and will use that instead if
Mako is available.  The rendered HTML is identical but (we suspect)
Mako is faster.