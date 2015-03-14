# Code has moved #

FormAlchemy is now hosted on [GitHub](https://github.com/FormAlchemy)

The full documentation is [here](http://docs.formalchemy.org/)


# Introduction #

FormAlchemy greatly speeds development with SQLAlchemy mapped classes (models)
in a HTML forms environment.

FormAlchemy eliminates boilerplate by autogenerating HTML input
fields from a given model. FormAlchemy will try to figure out what
kind of HTML code should be returned by introspecting the model's
properties and generate ready-to-use HTML code that will fit the
developer's application.

Of course, FormAlchemy can't figure out everything,
i.e, the developer might want to display only a few columns from the given
model. Thus, FormAlchemy is also highly customizable.


# Features #

  * Generates HTML form fields and tables from [SQLAlchemy](http://www.sqlalchemy.org) mapped classes or manually added Fields
  * Works with declarative or classic mapper definitions
  * Render and edits single objects or collections (grids)
  * Handles [object relationships](http://www.sqlalchemy.org/docs/05/ormtutorial.html#datamapping_relation) (including many-to-many), not just simple data types
  * [Synonym](http://www.sqlalchemy.org/docs/05/mappers.html#advdatamapping_mapper_overriding) support
  * [Composite and custom type](http://www.sqlalchemy.org/docs/05/mappers.html#advdatamapping_mapper_composite) support
  * Supports all composite primary keys and most CFKs
  * Pre-fills input fields with current or default value
  * Highly customizable HTML output
  * Validates input and displays errors in-line
  * Syncs model instances with input data
  * Easy-to-use, extensible API
  * SQLAlchemy 0.4 (0.4.5 or later) and 0.5 compatible


# Limitations #

  * Currently, only handles composite foreign keys of primitive Python types


# Installation #

Check out the instructions for InstallingFormAlchemy.


# Quick introduction #

To get started, you only need to know about two classes, `FieldSet` and
`Grid`, and a handful of methods:

  * `render`: returns a string containing the html
  * `validate`: true if the form passes its validations; otherwise, false
  * `sync`: syncs the model instance that was bound to the input data

This introduction illustrates these three methods. For full details on
customizing `FieldSet` behavior, see [the documentation](http://docs.formalchemy.org).

We'll start with two simple SQLAlchemy models with a one-to-many relationship
(each `User` can have many `Order`s), and fetch an `Order` object to edit:

```
  from formalchemy.tests import Session, User, Order
  session = Session()
  order1 = session.query(Order).first()
```

Now, let's render a form to edit the order we've loaded.

```
  from formalchemy import FieldSet, Grid
  fs = FieldSet(order1)
  print fs.render()
```

This results in the following form elements:

> ![http://wiki.formalchemy.googlecode.com/hg/example.png](http://wiki.formalchemy.googlecode.com/hg/example.png)

Note how the options for the User input were automatically loaded from the
database.  `str()` is used on the User objects to get the option descriptions.

To edit a new object, bind your `FieldSet` to the class rather than a specific instance:

```
  fs = FieldSet(Order)
```

To edit multiple objects, bind them to a `Grid` instead:

```
  orders = session.query(Order).all()
  g = Grid(Order, orders)
  print g.render()
```

Which results in:

> ![http://wiki.formalchemy.googlecode.com/hg/example-grid.png](http://wiki.formalchemy.googlecode.com/hg/example-grid.png)

Saving changes is similarly easy.  (Here we're using Pylons-style `request.params()`;
adjust for your framework of choice as necessary):

```
  fs = FieldSet(order1, data=request.params())
  if fs.validate():
      fs.sync()
      session.commit()
```

`Grid` works the same way.


# Full Documentation #

FormAlchemy's documentation is available [here](http://docs.formalchemy.org).  Some good starting points are
  * [Using Forms in Controllers](http://docs.formalchemy.org/current/pylons_sample.html#using-forms-in-controllers) -- a complete example for Pylons.  Other MVC frameworks should look similar.
  * [Configuring forms](http://docs.formalchemy.org/current/forms.html#configuring-and-rendering-forms) -- the gory details on getting what you want and only what you want in your form
  * A lot of people want the [Pylons admin interface](http://docs.formalchemy.org/current/ext/pylons.html#administration-interface)
  * If you are starting a new Pylons projects, FormAlchemy has [paster support](http://docs.formalchemy.org/current/pylons_sample.html#bootstrap-your-project) to set things up automagically


# Copyright and License #

Copyright (C) 2007 Alexandre Conrad, alexandre dot conrad at gmail dot com

FormAlchemy is released under the
[MIT License](http://www.opensource.org/licenses/mit-license.php).