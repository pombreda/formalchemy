# Quick tutorial #
```
from sqlalchemy import *
from sqlalchemy.orm import *
from formalchemy import FieldSet

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

Ok, this is _**very basic**_ SQLAlchemy stuff. If you don't understand the code, please visit [SQLAlchemy's documentation](http://www.sqlalchemy.org/docs) first.

Let's have a quick look at the columns we have declared in `user_table`:
  * `id` - the table's primary key.
  * `email` - a required 40 characters limited field.
  * `password` - a required 20 characters field.
  * `first_name` - an optional 20 characters field.
  * `last_name` - an optional 20 characters field.
  * `description` - an optional non-limited characters field.
  * `active` - a boolean field that defaults to True.

Now the fun and easy part:

```
>>> print FieldSet(user).render()
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
```

Nice! As you can see, `FielSet` was instantiated passing it the `user` SQLAlchemy mapped class as argument and the `render()` method was called on the fly, thus generating some HTML code.

Now let's have a closer look at the generated HTML.

First, we can see that no HTML 

&lt;form&gt;

 tags are present. Just HTML 

&lt;label&gt;

 and 

&lt;input&gt;

 fields. It is the programmer's responsability to wrap formalchemy's output in his own HTML 

&lt;form&gt;

 tags.

Each field is structured as followed:

```
<div>
  <label [attributes]>Column's name</label>
  <input [attributes] />
</div>
```

Notice that:
  * non-nullable columns (required) had their 

&lt;label&gt;

 tag set with a `class="field_req"`.
  * nullable columns (optional) had their 

&lt;label&gt;

 tag set `class="field_opt"`.
  * Unicode columns with limited character length have their 

&lt;input&gt;

 tag set with a `maxlength` attribute holding the appropriate column's length.
  * column names have been formated to nice human readable text: "first\_name" -> "First name".
  * the Boolean column has its 

&lt;input&gt;

 tag set as `type="checkbox"`.
  * it also has its default state set as `checked` as declared in the `user_table`.

Great! But this is FormAlchemy's default behaviour. What if we want to change the output to fit our needs better. FormAlchemy states to be "customizable" as well.

So let's change FormAlchemy's behaviour taking these in consideration:
  * don't generate the `id` field, as parimary keys are generally handled by the database itself, not the user.
  * have the `password` field masked (i.e., a series of asterisks).
  * set my own required / optionnal classes: "must\_fill" and "can\_fill".
  * don't generate the `active` neither, we don't want the user to touch that.

This is just a matter of setting a few options the `render()` method.

Here we go:

```
>>> fields = FieldSet(user).render(
...     pk=False,
...     password=["password"],
...     cls_req="must_fill",
...     cls_opt="can_fill",
...     exclude=["active"]
... )
>>>
>>> print fields
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
```

That's it! The options passed to `render()` pretty much speaks by itself:
  * `pk=False`: don't generate primary keys.
  * `password=["password"]`: A list of fields to be set as masked.
  * `cls_req="must_fill"`: the class for non-nullable columns.
  * `cls_opt="can_fill"`: the class for nullable columns.
  * `exclude=["active"]`: a list of one or more fields to be excluded from the HTML. We could have `id` in here, but `pk=False` it better suited.

And there is much more you can do with FormAlchemy's possibilities, e.g., configuring FormAlchemy's behaviour directly from your SQLAlchemy mapped class. [Check out the documentation.](http://code.google.com/p/formalchemy/wiki/Documentation)