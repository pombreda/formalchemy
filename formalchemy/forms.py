# Copyright (C) 2007 Alexandre Conrad, aconrad(dot.)tlv(at@)magic(dot.)fr
#
# This module is part of FormAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import logging
logger = logging.getLogger('formalchemy.' + __name__)

import base, fields
from validators import ValidationError

from tempita import Template as TempitaTemplate # must import after base


__all__ = ['AbstractFieldSet', 'FieldSet', 'form_data']


def form_data(fieldset, params):
    """ 
    deprecated.  moved the "pull stuff out of a request object" stuff
    into relevant_data().  until this is removed it is a no-op.
    """
    return params


class AbstractFieldSet(base.EditableRenderer):
    """
    `FieldSets` are responsible for generating HTML fields from a given
    `model`.

    You can derive your own subclasses from `FieldSet` or `AbstractFieldSet`
    to provide a customized `render` and/or `configure`.

    `AbstractBaseSet` encorporates validation/errors logic and provides a default
    `configure` method.  It does *not* provide `render`.
    
    You can write `render` by manually sticking strings together if that's what you want,
    but we recommend using a templating package for clarity and maintainability.
    !FormAlchemy includes the Tempita templating package as formalchemy.tempita;
    see http://pythonpaste.org/tempita/ for documentation.  
    
    `formalchemy.forms.template_text_tempita` is the default template used by `FieldSet.`
    !FormAlchemy also includes a Mako version, `formalchemy.forms.template_text_mako`,
    and will use that instead if Mako is available.  The rendered HTML is identical
    but (we suspect) Mako is faster.
    """
    def __init__(self, *args, **kwargs):
        base.EditableRenderer.__init__(self, *args, **kwargs)
        self.validator = None
        self._errors = []

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None):
        """
        `global_validator` should be a function that performs validations that need
        to know about the entire form.  The other parameters are passed directly
        to `ModelRenderer.configure`.
        """
        base.EditableRenderer.configure(self, pk, exclude, include, options)
        self.validator = global_validator

    def validate(self):
        """
        Validate attributes and `global_validator`.
        If validation fails, the validator should raise `ValidationError`.
        """
        if self.data is None:
            raise Exception('Cannot validate without binding data')
        success = True
        for field in self.render_fields.itervalues():
            success = field._validate() and success
        if self.validator:
            self._errors = []
            try:
                self.validator(self)
            except ValidationError, e:
                self._errors = e.args
                success = False
        return success
    
    def errors(self):
        """
        A dictionary of validation failures.  Always empty before `validate()` is run.
        Dictionary keys are attributes; values are lists of messages given to `ValidationError`.
        Global errors (not specific to a single attribute) are under the key `None`.
        """
        errors = {}
        if self._errors:
            errors[None] = self._errors
        errors.update(dict([(field, field.errors)
                            for field in self.render_fields.itervalues() if field.errors]))
        return errors
    errors = property(errors)
    
    
template_text_mako = r"""
<% _focus_rendered = False %>\

% for error in fieldset.errors.get(None, []):
<div class="fieldset_error">
  ${error}
</div>
% endfor

% for field in fieldset.render_fields.itervalues():
  % if isinstance(field.renderer, fields.HiddenFieldRenderer):
${field.render()}
  % else:
<div>
  <label class="${field.is_required() and 'field_req' or 'field_opt'}" for="${field.renderer.name}">${field.label_text or fieldset.prettify(field.key)}</label>
  ${field.render()}
  % for error in field.errors:
  <span class="field_error">${error}</span>
  % endfor
</div>

% if (fieldset.focus == field or fieldset.focus is True) and not _focus_rendered:
<script type="text/javascript">
//<![CDATA[
document.getElementById("${field.renderer.name}").focus();
//]]>
</script>
<% _focus_rendered = True %>\
% endif

% endif
% endfor
""".strip()

template_text_tempita = r"""
{{py:_focus_rendered = False}}

{{for error in fieldset.errors.get(None, [])}}
<div class="fieldset_error">
  {{error}}
</div>
{{endfor}}

{{for field in fieldset.render_fields.itervalues()}}
{{if isinstance(field.renderer, fields.HiddenFieldRenderer)}}
{{field.render()}}                                                                              
{{else}}                                                                                       
<div>                                                                                          
  <label class="{{field.is_required() and 'field_req' or 'field_opt'}}" for="{{field.renderer.name}}">{{field.label_text or fieldset.prettify(field.key)}}</label>
  {{field.render()}}                                                                            
  {{for error in field.errors}}
  <span class="field_error">{{error}}</span>
  {{endfor}}
</div>                                                                                         

{{if (fieldset.focus == field or fieldset.focus is True) and not _focus_rendered}}
<script type="text/javascript">
//<![CDATA[
document.getElementById("{{field.renderer.name}}").focus();
//]]>
</script>
{{py:_focus_rendered = True}}
{{endif}}

{{endif}}                                                                                      
{{endfor}}                                                                                     
""".strip()
render_tempita = TempitaTemplate(template_text_tempita, name='fieldset_template').substitute

try:
    from mako.template import Template as MakoTemplate
except ImportError:
    render = render_tempita
else:
    render_mako = MakoTemplate(template_text_mako).render


class FieldSet(AbstractFieldSet):
    """
    A `FieldSet` is bound to a SQLAlchemy mapped instance (or class, for
    creating new instances) and can render a form for editing that instance,
    perform validation, and sync the form data back to the bound instance.
    
    There are three parts you can customize in a `FieldSet` subclass short
    of writing your own render method.  These are `default_renderers`, `prettify`, and
    `_render`.  As in,
    
    {{{
    class MyFieldSet(FieldSet):
        default_renderers = {
            types.String: fields.TextFieldRenderer,
            types.Integer: fields.IntegerFieldRenderer,
            # ...
        }
        prettify = staticmethod(myprettify)
        _render = staticmethod(myrender)
    }}}
    
    `default_renderers` is a dict of callables returning a FieldRenderer.  Usually these
    will be FieldRenderer subclasses, but this is not required.  For instance,
    to make Booleans render as select fields with Yes/No options by default,
    you could write:

    {{{
    class BooleanSelectRenderer(fields.SelectFieldRenderer):
        def render(self, **kwargs):
            kwargs['options'] = [('Yes', True), ('No', False)]
            return fields.SelectFieldRenderer.render(self, **kwargs)

    FieldSet.default_renderers[types.Boolean] = BooleanSelectRenderer
    }}}
    
    `prettify` is a function that, given an attribute name ('user_name')
    turns it into something usable as an HTML label ('User name').
    
    `_render` should be a template rendering method, such as
    `Template.render` from a mako Template or `Template.substitute` from a
    Tempita Template.
    
    `_render` should take as parameters:
      * `fieldset`:
            the `FieldSet` to render
      * `fields`:
            a reference to the `formalchemy.fields` module (you can of
            course perform other imports in your template, if it supports
            Python code blocks)
    
    You can also override these on a per-`FieldSet` basis:
    
    {{{
    fs = FieldSet(...)
    fs.prettify = myprettify
    ...
    }}}
    """
    _render = staticmethod('render_mako' in locals() and render_mako or render_tempita)
    
    def __init__(self, *args, **kwargs):
        AbstractFieldSet.__init__(self, *args, **kwargs)
        self.focus = True

    def configure(self, pk=False, exclude=[], include=[], options=[], global_validator=None, focus=True):
        """ 
        Besides the options in `AbstractFieldSet.configure`,
        `FieldSet.configure` takes the `focus` parameter, which should be the
        attribute (e.g., `fs.orders`) whose rendered input element gets focus. Default value is
        True, meaning, focus the first element. False means do not focus at
        all. 
        """
        AbstractFieldSet.configure(self, pk, exclude, include, options, global_validator)
        self.focus = focus

    def render(self):
        # We pass a reference to the 'fields' module because a relative import
        # in the template won't work in production, and an absolute import
        # makes testing more of a pain. Additionally, some templating systems
        # (notably Django's) make it difficult to perform imports directly in
        # the template itself. If your templating weapon of choice does allow
        # it, feel free to perform such imports in the template.
        return self._render(fieldset=self, fields=fields)
