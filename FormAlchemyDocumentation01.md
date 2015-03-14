# Documentation #

## The `FieldSet` class ##

> This is the class responsible for generating HTML form fields. It needs
> to be instantiate with a SQLAlchemy mapped class as argument `model`.

> The one method to use is `render`. This is the method that returns
> generated HTML code from the `model` object.

> FormAlchemy has some default behaviour set. It is configured to generate
> the most HTML possible that will reflect the `model` object. Although,
> you can configure FormAlchemy to behave differently, thus altering the
> generated HTML output by many ways:

  * By passing keyword options to the `render` method:

```
        render(pk=False, fk=False, exclude=["private_column"])
```

> These options are NOT persistant. You'll need to pass these options
> everytime you call `render` or FormAlchemy will fallback to its
> default behaviour. Passing keyword options is usually meant to alter
> the HTML output on the fly.

  * At the SQLAlchemy mapped class level, by creating a `FormAlchemy`
> subclass, it is possible to setup attributes which names and values
> correspond to the keyword options passed to `render`:

```
        class MyClass(object):
            class FormAlchemy:
                pk = False
                fk = False
                exclude = ["private_column"]
```

> These attributes are persistant and will be used as FormAlchemy's
> default behaviour.

  * By passing the keyword options to FormAlchemy's `configure` method.
> These options are persistant and will be used as FormAlchemy's default
> behaviour.

```
        configure(pk=False, fk=False, exclude=["private_column"])
```

> Note: In any case, options set at the SQLAlchemy mapped class level or
> via the `configure` method will be overridden if these same keyword
> options are passed to `render`.

## The `__init__(model)` method ##

> Construct the `Formalchemy` class.

> Arguments are:

> `model`
> > A SQLAlchemy mapped class. This is the `model` object that will be
> > instrospected by `render` for HTML generation.

## The `configure(**options)` method ##


> This will update FormAlchemy's default behaviour with the given
> keyword options. Any other previously set options will be kept intact.


## The `reconfigure(**options)` method ##

> This will clear any previously set option and update FormAlchemy's
> default behaviour with the given keyword options.

## The `render(**options)` method ##

> Return HTML fields generated from the `model` object.

> By default, generated fields are text input fields. In some obvious
> cases, FormAlchemy will figure out the correct of input, e.g., a checkbox
> for a boolean column. But you might want to have other kind of fields
> displayed in your form. Fields can be customized by passing options
> to `render`.

  * `pk=True` - Won't return primary key columns if set to `False`.
  * `fk=True` - Won't return foreign key columns if set to `False`.
  * `exclude=[]` - An iterable containing column names to exclude.
  * `readonly_pk=False` - Will prohibit changes to primary key columns if set to `True`.
  * `readonly_fk=False` - Will prohibit changes to foreign key columns if set to `True`.
  * `readonly=[]` - An iterable containing column names to set as readonly.
  * `password=[]` - An iterable of column names that should be set as password fields.
  * `hidden=[]` - An iterable of column names that should be set as hidden fields.
  * `dropdown={}` - A dict holding column names as keys, dicts as values. These dicts have at least a `opts` key used for options. `opts` holds either:
> > - an iterable of option names: `["small", "medium", "large"]`. Options will have the same name and value.
> > - an iterable of paired option name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`.
> > - a dict where dict keys are option names and dict values are option values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`.
> > The `selected` key can also be set:
> > > `selected=value`: a string or a container of strings (when multiple values are selected) that will set the "selected" HTML tag to matching value options. It defaults to the SQLAlchemy mapped class's current value (if not None) or column default.

> > Other keys can be given to be passed as standard HTML attributes, like multiple=

&lt;bool&gt;

, size=

&lt;integer&gt;

 and so on.


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

  * `radio={}` - A dict holding column names as keys and an iterable as values. The iterable can hold:
    * input names: `["small", "medium", "large"]`. Inputs will have the same name and value.
    * paired name/value: `[("small", "$0.99"), ("medium", "$1.29"), ("large", "$1.59")]`.
    * a dict where dict keys are input names and dict values are input values: `{"small":"$0.99", "medium":"$1.29", "large":"$1.59"}`.


  * `prettify` - A function through which all label names will go. Defaults to: `"my_label".replace("_", " ").capitalize()`
  * `alias={}` - A dict holding the field name as the key and the alias name as the value. Note that aliases are beeing `prettify`ed as well.
  * `error={}` - A dict holding the field name as the key and the error message as the value.
  * `doc={}` - A dict holding the field name as the key and the help message as the value.
  * `cls_req="field_req"` - Sets the HTML class for fields that are not nullable (required).
  * `cls_opt="field_opt"` - Sets the HTML class for fields that are nullable (optional).
  * `cls_err=field_err` - Sets the HTML class for error messages.
  * `cls_doc="field_doc"` - Sets the HTML class for help messages.