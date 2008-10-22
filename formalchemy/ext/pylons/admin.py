# standard pylons controller imports
import logging
log = logging.getLogger(__name__)

from pylons import request, response, session
try:
    from pylons import tmpl_context as c
except:
    from pylons import c
from pylons.controllers.util import redirect_to, url_for
import pylons.controllers.util as h

from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm import class_mapper
from formalchemy import *
from formalchemy.fields import _pk
from mako.template import Template


__all__ = ['FormAlchemyAdminController']


# templates
css = """
<style type="text/css">
.admin-flash {
    font-size:16pt; 
    font-weight: bold;
    background-color: #00FF00;
}

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

table {
  	border-collapse: collapse;
}

th, td {
    padding-left: 0.5em;
    padding-right: 0.5em;
}

th {
    background-color: #bbbbbb;
    border-bottom: 1px solid #8e8e8e;
    vertical-align: top;
}

</style>
"""

_flash_snippet = """
<%
 from pylons import session
 flashes = session.get('_admin_flashes', [])
 if flashes:
   session['_admin_flashes'] = []
   session.save()
%>
% for flash in flashes:
  <div class='admin-flash'>${flash}</div>
% endfor
"""

index_mako = """
<html>
  <head>
""" + css + _flash_snippet + """
  </head>
  <body>
    <h1>Models</h1>
    <ul>
    % for modelname in c.modelnames:
      <li><a href="${h.url_for(controller='admin', modelname=modelname, action='list')}">${modelname}</a></li>
    % endfor
    </ul>
  </body>
</html>
"""
index_template = Template(index_mako)

list_mako = """
<html>
  <head>
""" + css + _flash_snippet + """
  </head>
  <body>
    <h1>Related types</h1>
      <ul>
      % for field in c.grid._fields.itervalues():
        % if field.is_relation():
          <% clsname = field.relation_type().__name__ %>
          <li><a href="${h.url_for(controller='admin', modelname=clsname, action='list')}">${clsname}</a></li>
        % endif
      % endfor
      </ul>
    <h1>Existing objects</h1>
    <table>
      ${c.grid.render()}
    </table>
    <h1>New object</h1>
    <a href="${h.url_for(controller='admin', modelname=c.modelname, action='edit')}">Create form</a>
  </body>
</html>
"""
list_template = Template(list_mako)

edit_mako = """
<html>
  <head>
""" + css + _flash_snippet + """
  </head>
  <body>
    <form method="post">
      ${c.fs.render()}
      <input type="submit">
    </form>
  </body>
</html>
"""
edit_template = Template(edit_mako)


def flash(msg):
    """Add 'msg' to the users flashest list in the users session"""
    flashes = session.setdefault('_admin_flashes', [])
    flashes.append(msg)
    session.save()


def get_forms(controller, model_module, forms):
    """scan model and forms"""
    if forms is not None:
        model_fieldsets = dict((form.model.__class__.__name__, form)
                               for form in forms.__dict__.itervalues()
                               if isinstance(form, FieldSet))
        model_grids = dict((form.model.__class__.__name__, form)
                           for form in forms.__dict__.itervalues()
                           if isinstance(form, Grid))
    else:
        model_fieldsets = dict()
        model_grids = dict()

    # generate missing forms, grids
    for key, obj in model_module.__dict__.iteritems():
        try:
            class_mapper(obj)
        except UnmappedClassError:
            continue
        if not isinstance(obj, type):
            continue
        if key not in model_fieldsets:
            model_fieldsets[key] = FieldSet(obj)
        if key not in model_grids:
            model_grids[key] = Grid(obj)
    # add Edit + Delete link to grids
    for modelname, grid in model_grids.iteritems():
        def get_linker(action, modelname=modelname):
            return lambda item: '<a href="%s">%s</a>' % (h.url_for(controller=controller,
                                                                   modelname=modelname,
                                                                   action=action,
                                                                   id=_pk(item)),
                                                         action)
        old_include = grid.render_fields.values() # grab this now, or .add will change it if user didn't call configure yet
        for action in ['edit', 'delete']:
            grid.add(Field(action, types.String, get_linker(action)))
        grid.configure(include=old_include + [grid.edit, grid.delete], readonly=True)

    return {'_model_fieldsets':model_fieldsets, '_model_grids':model_grids}


class AdminController(object):
    """Base class to generate administration interface in Pylons"""

    def index(self):
        c.modelnames = sorted(self._model_grids.keys())
        return index_template.render(c=c, h=h)

    def list(self, modelname):
        c.modelname = modelname
        grid = self._model_grids[modelname]
        S = self.Session()
        instances = S.query(grid.model.__class__).all()
        c.grid = grid.bind(instances)
        return list_template.render(c=c, h=h)

    def edit(self, modelname, id=None):
        fs = self._model_fieldsets[modelname]
        S = self.Session()
        if id:
            instance = S.query(fs.model.__class__).get(id)
            c.fs = fs.bind(instance)
        else:
            c.fs = fs.bind(fs.model.__class__)
        if request.method == 'POST':
            c.fs = c.fs.bind(data=request.params)
            log.debug('saving %s w/ %s' % (c.fs.model.id, request.POST))
            if c.fs.validate():
                c.fs.sync()
                S.flush()
                S.refresh(c.fs.model)
                S.commit()
                flash('%s %s %s'
                      % (id == None and 'Created' or 'Modified',
                         modelname,
                         _pk(c.fs.model)))
                redirect_to(url_for(controller='admin', modelname=modelname, action='list', id=None))
        return edit_template.render(c=c, h=h)

    def delete(self, modelname, id):
        fs = self._model_fieldsets[modelname]
        S = self.Session()
        instance = S.query(fs.model.__class__).get(id)
        key = _pk(instance)
        S.delete(instance)
        S.commit()
        flash('Deleted %s %s'
              % (modelname, key))
        redirect_to(url_for(controller='admin', modelname=modelname, action='list', id=None))

def FormAlchemyAdminController(cls):
    """
    Generate a controller that is a subclass of `AdminController`
    and the Pylons BaseController `cls`
    """
    controller = cls.__name__.lower().split('controller')[0]
    kwargs = get_forms(controller, cls.model, cls.forms)
    log.info('creating admin controller with args %s' % kwargs)
    return type(cls.__name__, (cls, AdminController), kwargs)
