from __future__ import unicode_literals

import re
from django.apps import apps
from django.core.serializers import serialize
from django.utils import timezone


class Anonymizer(object):

    def __init__(self, *args, **kwargs):
        super(Anonymizer, self).__init__(*args, **kwargs)

    @staticmethod
    def anonymize_string(string):
        return re.sub("\w", "x", string)

    @staticmethod
    def anonymize(klass, objects):
        for object_ in objects:
            for field in klass._meta.fields:
                field_name = field.name
                field_type = field.__class__.__name__
                if field_type in ("CharField", "TextField"):
                    field_value = getattr(object_, field_name)
                    if field_value:
                        anoymized_field_value = Anonymizer.anonymize_string(field_value)
                        setattr(object_, field_name, anoymized_field_value)

    @staticmethod
    def anonymize_objects(klass):
        objects = klass.objects.all()
        Anonymizer.anonymize(klass, objects)
        return objects

    @staticmethod
    def serialize(klass):
        objects = Anonymizer.anonymize_objects(klass)
        return serialize("json", objects)

    def run(self):
        filename = "anonymized_data-{0}.json".format(timezone.now().isoformat())

        out = open(filename, "w")

        for app_name in ["boards", "hourly_rates", "journal", "dev_times", "dev_environment", "forecasters", "members",
                         "notifications", "reporter", "reports", "repositories", "requirements",
                         "visitors", "workflows"]:
            models = apps.get_app_config(app_name).get_models()
            for model in models:
                objects = Anonymizer.serialize(model)
                out.write(objects)

        out.close()

        return filename
