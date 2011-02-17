from os.path import join
from django import forms
from django.conf import settings

from cms.plugin_pool import plugin_pool
from cms.plugins.text.settings import USE_TINYMCE
from cms.plugins.text.widgets.wymeditor_widget import WYMEditor

from models import Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
              
    def _media(self):
        media = forms.Media(js=(join(settings.ADMIN_MEDIA_PREFIX, 'js/jquery.js'),))
        return media + self._get_media()
    
    media = property(_media)
        
    def get_widget(self, plugins):
        """
        Returns the Django form Widget to be used for
        the text area
        """
        if USE_TINYMCE and "tinymce" in settings.INSTALLED_APPS:
            from cms.plugins.text.widgets.tinymce_widget import TinyMCEEditor
            return TinyMCEEditor(installed_plugins=plugins)
        else:
            return WYMEditor(installed_plugins=plugins)    
        
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        plugins = plugin_pool.get_text_enabled_plugins(placeholder=None, page=None)
        widget = self.get_widget(plugins)
        self.fields['description'].widget = widget
