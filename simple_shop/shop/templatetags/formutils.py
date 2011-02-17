'''
inspired by  http://opensource.washingtontimes.com/blog/post/jsoares/2009/01/im-lazier-then-django-forms/
'''

from django import template


register = template.Library()

class FormOptions():
    """
    FormOptions class gives Form extra properties 
    so we can build a generic form template and
    relieve the need to re-create a form, even more
    lazier then newforms.
    """
    (id, method, action, enctype, accept,
    accept_charset, cssclass, has_reset,
    include_help_text, submit_label, reset_label) = (None, None, 
    None, None, None, None, None, None, None, None, None)

    def __new__(self, id=None, method='POST', action='.', enctype=None, accept=None,
                 accept_charset=None, cssclass='form_wrapper', has_reset=False,
                 include_help_text=False, submit_label='Submit', reset_label='Reset'):

        if not action:
            raise ValueError('Action is not defined.')

        (self.id, self.method, self.action, self.enctype,
         self.accept, self.accept_charset, self.cssclass,
         self.has_reset, self.submit_label, self.reset_label,
         self.include_help_text) = (id, method, action, enctype,
         accept, accept_charset, cssclass,
         has_reset, submit_label, reset_label,
         include_help_text)
         
         
form_options = dict( id=None, method='POST', action='.', enctype=None, accept=None,
                 accept_charset=None, cssclass='form_wrapper', has_reset=False,
                 include_help_text=False, submit_label='Submit', reset_label='Reset'                
                )

@register.inclusion_tag('formutils/form.html')
def build_form(form):
    form.form_options = form_options.update(getattr(form, 'options', {}))
    return { 'form': form }