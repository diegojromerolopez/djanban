
from __future__ import unicode_literals

import pygal
from django.db.models import Min, Max, Sum
from django.utils import timezone

from djanban.apps.charts.models import CachedChart
from djanban.apps.repositories.models import PylintMessage, PhpMdMessage


# Number of code errors by commit
def number_of_code_errors(grouped_by, board, repository, language="python"):
    if grouped_by == "commit":
        return _number_of_code_errors_by_commit(board, repository=repository, language=language, per_loc=False)
    elif grouped_by == "month":
        return _number_of_code_errors_by_month(board, repository=repository, language=language, per_loc=False)
    raise ValueError(u"Value {0} not recognized".format(grouped_by))


# Number of code errors by commit
def number_of_code_errors_per_loc(grouped_by, board, repository, language="python"):
    if grouped_by == "commit":
        return _number_of_code_errors_by_commit(board, repository=repository, language=language, per_loc=True)
    elif grouped_by == "month":
        return _number_of_code_errors_by_month(board, repository=repository, language=language, per_loc=True)
    raise ValueError(u"Value {0} not recognized".format(grouped_by))


# Return the number of PHP/Python code errors by commit
def _number_of_code_errors_by_commit(board, repository=None, language="python", per_loc=False):

    # Caching
    chart_uuid = "repositories._number_of_code_errors_by_commit-{0}-{1}-{2}-{3}".format(
        board.id, repository.id if repository else "None", language, "per_loc" if per_loc else "global"
    )
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    repository_text = " "
    repository_filter = {}
    if repository:
        repository_filter = {"repository": repository}
        repository_text = u", repository {0}, ".format(repository.name)

    if not per_loc:
        chart_title = u"Errors in {0} code by commit in project {1}{2}{3}".format(language, board.name, repository_text, timezone.now())
    else:
        chart_title = u"Errors in {0} code per LOC by commit in project {1}{2}{3}".format(language, board.name, repository_text, timezone.now())

    def formatter(x):
        if per_loc:
            return '{0:.2f}'.format(x)
        return "{0}".format(x)

    chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                       print_zeroes=False, value_formatter=formatter,
                       human_readable=False)

    if language.lower() == "php":
        error_messages = board.phpmd_messages.filter(commit__has_been_assessed=True).filter(**repository_filter)
        message_types = PhpMdMessage.RULESETS
        message_type_label = "ruleset"
    elif language.lower() == "python":
        error_messages = board.pylint_messages.filter(commit__has_been_assessed=True).filter(**repository_filter)
        message_types = dict(PylintMessage.TYPE_CHOICES).keys()
        message_type_label = "type"
    else:
        raise ValueError(u"Programming language {0} not recognized".format(language))

    project_locs = board.commit_files.filter(**repository_filter).aggregate(locs=Sum("lines_of_code"))["locs"]
    if project_locs is None:
        return chart.render_django_response()

    commits = board.commits.filter(has_been_assessed=True).filter(**repository_filter)
    if not commits.exists():
        return chart.render_django_response()

    for message_type in message_types:
        number_of_messages_by_commit = []
        chart.x_labels = []
        for commit in commits:
            error_message_filter = {
                message_type_label: message_type,
                "commit": commit
            }
            month_i_messages = error_messages.filter(**error_message_filter)

            number_of_errors = month_i_messages.count()
            if per_loc:
                number_of_errors /= float(project_locs)
            number_of_messages_by_commit.append(number_of_errors)
            chart.x_labels.append(commit.commit[:8])

        chart.add(message_type, number_of_messages_by_commit)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=chart.render(is_unicode=True))
    return chart.render_django_response()


# Return the number of PHP/Python code errors by month
def _number_of_code_errors_by_month(board, repository=None, language="python", per_loc=False):
    # Caching
    chart_uuid = "repositories._number_of_code_errors_by_month-{0}-{1}-{2}-{3}".format(
        board.id, repository.id if repository else "None", language, "per_loc" if per_loc else "global"
    )
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    repository_text = " "
    repository_filter = {}
    if repository:
        repository_filter = {"repository": repository}
        repository_text = u", repository {0}, ".format(repository.name)

    if not per_loc:
        chart_title = u"Errors in {0} code by month in project {1}{2}{3}".format(language, board.name, repository_text, timezone.now())
    else:
        chart_title = u"Errors in {0} code per LOC by month in project {1}{2}{3}".format(language, board.name, repository_text, timezone.now())

    def formatter(x):
        if per_loc:
            return '{0:.2f}'.format(x)
        return "{0}".format(x)

    chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                       print_zeroes=False, value_formatter=formatter,
                       human_readable=False)

    if language.lower() == "php":
        error_messages = board.phpmd_messages.filter(commit__has_been_assessed=True).filter(**repository_filter)
        message_types = PhpMdMessage.RULESETS
        message_type_label = "ruleset"
    elif language.lower() == "python":
        error_messages = board.pylint_messages.filter(commit__has_been_assessed=True).filter(**repository_filter)
        message_types = dict(PylintMessage.TYPE_CHOICES).keys()
        message_type_label = "type"
    else:
        raise ValueError(u"Programming language {0} not recognized".format(language))

    project_locs = board.commit_files.filter(**repository_filter).aggregate(locs=Sum("lines_of_code"))["locs"]
    if project_locs is None:
        return chart.render_django_response()

    min_creation_datetime = board.commits.filter(has_been_assessed=True).filter(**repository_filter).aggregate(
        min_creation_datetime=Min("creation_datetime"))["min_creation_datetime"]
    if min_creation_datetime is None:
        return chart.render_django_response()

    max_creation_datetime = board.commits.filter(has_been_assessed=True).filter(**repository_filter).aggregate(
        max_creation_datetime=Max("creation_datetime"))["max_creation_datetime"]

    max_month_i = max_creation_datetime.month
    max_year_i = max_creation_datetime.year

    for message_type in message_types:
        month_i = min_creation_datetime.month
        year_i = min_creation_datetime.year
        number_of_messages_by_month = []
        chart.x_labels = []
        while year_i < max_year_i or (year_i == max_year_i and month_i <= max_month_i):
            error_message_filter = {
                message_type_label: message_type,
                "commit__has_been_assessed": True,
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

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=chart.render(is_unicode=True))
    return chart.render_django_response()
