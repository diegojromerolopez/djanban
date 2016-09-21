
from __future__ import unicode_literals

import pygal
from django.db.models import Min, Max, Sum
from django.utils import timezone

from djangotrellostats.apps.repositories.models import PylintMessage, PhpMdMessage


# Number of code errors by month
def number_of_code_errors_by_month(board, repository, language="python"):
    return _number_of_code_errors_by_month(board, repository=repository, language=language, per_loc=False)


# Number of code errors by month
def number_of_code_errors_per_loc_by_month(board, repository, language="python"):
    return _number_of_code_errors_by_month(board, repository=repository, language=language, per_loc=True)


# Return the number of PHP/Python code errors by month
def _number_of_code_errors_by_month(board, repository=None, language="python", per_loc=False):
    repository_text = " "
    repository_filter = {}
    if repository:
        repository_filter = {"repository": repository}
        repository_text = u", repository {0}, ".format(repository.name)

    if not per_loc:
        chart_title = u"Errors in {0} code by month in project {1}{2}{3}".format(language, board.name, repository_text, timezone.now())
    else:
        chart_title = u"Errors in {0} code per LOC by month in project {1}{2}{3}".format(language, board.name, repository_text, timezone.now())

    chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                       print_zeroes=False,
                       human_readable=False)

    if language.lower() == "php":
        error_messages = board.phpmd_messages.filter(**repository_filter)
        message_types = PhpMdMessage.RULESETS
        message_type_label = "ruleset"
    elif language.lower() == "python":
        error_messages = board.pylint_messages.filter(**repository_filter)
        message_types = dict(PylintMessage.TYPE_CHOICES).keys()
        message_type_label = "type"
    else:
        raise ValueError(u"Programming language {0} not recognized".format(language))

    project_locs = board.commit_files.filter(**repository_filter).aggregate(locs=Sum("lines_of_code"))["locs"]
    if project_locs is None:
        return chart.render_django_response()

    min_creation_datetime = board.commits.filter(**repository_filter).aggregate(
        min_creation_datetime=Min("creation_datetime"))["min_creation_datetime"]
    if min_creation_datetime is None:
        return chart.render_django_response()

    max_creation_datetime = board.commits.filter(**repository_filter).aggregate(
        max_creation_datetime=Max("creation_datetime"))["max_creation_datetime"]

    max_month_i = max_creation_datetime.month
    max_year_i = max_creation_datetime.year

    for message_type in message_types:
        month_i = min_creation_datetime.month
        year_i = min_creation_datetime.year
        number_of_messages_by_month = []
        chart.x_labels = []
        while year_i <= max_year_i or (year_i == max_year_i and month_i < max_month_i):

            error_message_filter = {
                message_type_label: message_type,
                "commit__creation_datetime__year": year_i, "commit__creation_datetime__month": month_i
            }
            month_i_messages = error_messages.filter(**error_message_filter)

            number_of_errors = month_i_messages.count()
            if per_loc:
                number_of_errors /= float(project_locs)
            number_of_messages_by_month.append(number_of_errors)
            chart.x_labels.append(u"{0}-{1}".format(year_i, month_i))
            month_i += 1
            if month_i > 12:
                month_i = 1
                year_i += 1

        chart.add(message_type, number_of_messages_by_month)

    return chart.render_django_response()