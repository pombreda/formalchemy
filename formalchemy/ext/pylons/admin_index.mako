<%inherit file="base.mako"/>\
<%
from pylons import url
%>\
<%def name="title()">
${F_('Models')}
</%def>
<table>
%for i, modelname in enumerate(modelnames):
  <tr class="${i % 2 and 'odd' or 'even'}"><td><a href="${url(controller=controller, modelname=modelname, action='list')}">${modelname}</a></td></tr>
%endfor
</table>
