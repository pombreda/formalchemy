# -*- coding: utf-8 -*-
from formalchemy.forms import FieldSet as Base
from formalchemy.fields import Field as BaseField
from formalchemy import fields
from formalchemy import validators
from sqlalchemy.util import OrderedDict
import fatypes
from simplecouchdb import schema
from datetime import datetime


__all__ = ['Field', 'FieldSet']

class Field(BaseField):
    """"""
    def value(self):
        if not self.is_readonly() and self.parent.data is not None:
            v = self._deserialize()
            if v is not None:
                return v
        return getattr(self.model, self.name)
    value = property(value)

class FieldSet(Base):
    def __init__(self, model, session=None, data=None, prefix=None):
        self._fields = OrderedDict()
        self._render_fields = OrderedDict()
        self.model = self.session = None
        Base.rebind(self, model, data=data)
        self.prefix = prefix
        self.model = model
        self.readonly = False
        self.focus = True
        self._errors = []
        focus = True
        for k, v in model().iteritems():
            if not k.startswith('_'):
                try:
                    t = getattr(fatypes, v.__class__.__name__.replace('Property',''))
                except AttributeError:
                    raise NotImplementedError('%s is not mapped to a type' % v.__class__)
                else:
                    self.add(Field(name=k, type=t))
                    if v.required:
                        self._fields[k].validators.append(validators.required)

    def bind(self, model, session=None, data=None):
        """Bind to an instance"""
        if not (model or session or data):
            raise Exception('must specify at least one of {model, session, data}')
        if not model:
            if not self.model:
                raise Exception('model must be specified when none is already set')
            model = fields._pk(self.model) is None and type(self.model) or self.model
        # copy.copy causes a stacktrace on python 2.5.2/OSX + pylons.  unable to reproduce w/ simpler sample.
        mr = object.__new__(self.__class__)
        mr.__dict__ = dict(self.__dict__)
        # two steps so bind's error checking can work
        mr.rebind(model, session, data)
        mr._fields = OrderedDict([(key, renderer.bind(mr)) for key, renderer in self._fields.iteritems()])
        if self._render_fields:
            mr._render_fields = OrderedDict([(field.key, field) for field in
                                             [field.bind(mr) for field in self._render_fields.itervalues()]])
        return mr

    def rebind(self, model, session=None, data=None):
        if model:
            if isinstance(model, type):
                try:
                    model = model()
                except:
                    raise Exception('%s appears to be a class, not an instance, but FormAlchemy cannot instantiate it.  (Make sure all constructor parameters are optional!)' % model)
            self.model = model
        if data is None:
            self.data = None
        elif hasattr(data, 'getall') and hasattr(data, 'getone'):
            self.data = data
        else:
            try:
                self.data = SimpleMultiDict(data)
            except:
                raise Exception('unsupported data object %s.  currently only dicts and Paste multidicts are supported' % self.data)


def test_fieldset():
    class Pet(schema.Document):
        name = schema.StringProperty(required=True)
        type = schema.StringProperty(required=True)
        birthdate = schema.DateProperty(auto_now=True)
        weight_in_pounds = schema.IntegerProperty()
        spayed_or_neutered = schema.BooleanProperty()
        owner = schema.StringProperty()

    fs = FieldSet(Pet)
    p = Pet()
    p.name = 'dewey'
    p.type = 'cat'
    p.owner = 'gawel'
    p.owner = 'gawel'
    fs = fs.bind(p)
    assert fs.name.is_required() == True, fs.name.is_required()
    assert fs.owner.value == 'gawel'
    html = fs.render()
    assert 'class="field_req" for="Pet--name"' in html, html
    assert 'value="gawel"' in html, html

