from django.db import models
class RichTextUploadingField(models.TextField):
    def __init__(self, *args, **kwargs):
        # Remove kwarg specific to RichTextUploadingField that TextField doesn't accept if any?
        # extra_plugins, external_plugin_resources?
        # Usually harmless or handle explicitly
        # For now pass everything to super, assuming kwargs are compatible or ignored by Mock logic if I used mock. 
        # But this is real django model. 
        # config_name is common in ckeditor.
        kwargs.pop('config_name', None)
        kwargs.pop('external_plugin_resources', None)
        kwargs.pop('extra_plugins', None)
        super(RichTextUploadingField, self).__init__(*args, **kwargs)
