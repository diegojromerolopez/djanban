import pygal
from django.db.models import Min, Max
from django.utils import timezone

from djangotrellostats.apps.repositories.models import PylintMessage, PhpMdMessage


# Number of code errors by month
def number_of_code_errors_by_month(board, language="python"):
    if language == "python":
        return _number_of_python_code_errors_by_month(board)
    elif language == "php":
        return _number_of_php_code_errors_by_month(board)
    else:
        raise ValueError(u"Only Python and PHP programming languages are supported")


# Return the number of PHP code errors by month
def _number_of_php_code_errors_by_month(board):
    chart_title = u"Errors in PHP code by month in project {0} {1}".format(board.name, timezone.now())

    chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                       print_zeroes=False,
                       human_readable=True)

    message_types = PhpMdMessage.RULESETS

    min_creation_datetime = board.commits.all().aggregate(min_creation_datetime=Min("creation_datetime"))[
        "min_creation_datetime"]
    if min_creation_datetime is None:
        return chart.render_django_response()

    max_creation_datetime = board.commits.all().aggregate(max_creation_datetime=Max("creation_datetime"))[
        "max_creation_datetime"]

    max_month_i = max_creation_datetime.month
    max_year_i = max_creation_datetime.year

    for phpmd_message_type in message_types:
        month_i = min_creation_datetime.month
        year_i = min_creation_datetime.year
        number_of_phpmd_messages_by_month = []
        chart.x_labels = []
        while year_i <= max_year_i or (year_i == max_year_i and month_i < max_month_i):
            month_i_pylint_messages = board.phpmd_messages.filter(ruleset=phpmd_message_type,
                                                                   commit__creation_datetime__year=year_i,
                                                                   commit__creation_datetime__month=month_i)

            number_of_phpmd_messages_by_month.append(month_i_pylint_messages.count())
            chart.x_labels.append(u"{0}-{1}".format(year_i, month_i))
            month_i += 1
            if month_i > 12:
                month_i = 1
                year_i += 1

        chart.add(phpmd_message_type, number_of_phpmd_messages_by_month)

    return chart.render_django_response()


# Return the number of Python code errors by month
def _number_of_python_code_errors_by_month(board):
    chart_title = u"Errors in Pytho code by month in project {0} {1}".format(board.name, timezone.now())

    chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=True,
                                          print_zeroes=False,
                                          human_readable=True)

    pylint_message_types = dict(PylintMessage.TYPE_CHOICES).keys()

    min_creation_datetime = board.commits.all().aggregate(min_creation_datetime=Min("creation_datetime"))[
        "min_creation_datetime"]
    if min_creation_datetime is None:
        return chart.render_django_response()

    max_creation_datetime = board.commits.all().aggregate(max_creation_datetime=Max("creation_datetime"))[
        "max_creation_datetime"]

    max_month_i = max_creation_datetime.month
    max_year_i = max_creation_datetime.year

    for pylint_message_type in pylint_message_types:
        month_i = min_creation_datetime.month
        year_i = min_creation_datetime.year
        number_of_pylint_messages_by_month = []
        chart.x_labels = []
        while year_i <= max_year_i or (year_i == max_year_i and month_i < max_month_i):
            month_i_pylint_messages = board.pylint_messages.filter(type=pylint_message_type,
                                                                   commit__creation_datetime__year=year_i,
                                                                   commit__creation_datetime__month=month_i)

            number_of_pylint_messages_by_month.append(month_i_pylint_messages.count())
            chart.x_labels.append(u"{0}-{1}".format(year_i, month_i))
            month_i += 1
            if month_i > 12:
                month_i = 1
                year_i += 1

        chart.add(dict(PylintMessage.TYPE_CHOICES)[pylint_message_type], number_of_pylint_messages_by_month)

    return chart.render_django_response()
