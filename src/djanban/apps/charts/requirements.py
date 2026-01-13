import copy
from datetime import timedelta

import pygal
from django.db.models import Sum

from djanban.apps.charts.models import CachedChart


# Burndown chart for each requirement
def burndown(board, requirement=None):
    if requirement is not None:
        return _requirement_burndown(board, requirement)
    return _burndown_by_requirement(board)


# Burndown for a particular requirement
def _requirement_burndown(board, requirement):
    # Caching
    chart_uuid = f"requirements._requirement_burndown-{requirement.id}"
    svg_chart = CachedChart.get(board=board, uuid=chart_uuid)
    if svg_chart:
        return svg_chart

    board = requirement.board

    chart_title = f"Burndown of requirement {requirement.code}"
    chart_title += f" for board {board.name} as of {board.get_human_fetch_datetime()}"

    burndown_chart = pygal.Line(
        title=chart_title,
        legend_at_bottom=True,
        print_values=True,
        x_labels_major_count=30,
        show_minor_x_labels=False,
        print_zeroes=False,
        fill=False,
        human_readable=True,
        x_label_rotation=65,
    )

    # Estimated number of hours
    estimated_number_of_hours = requirement.estimated_number_of_hours

    # Remaining hours
    remaining_time = estimated_number_of_hours
    daily_spent_times = board.daily_spent_times.filter(
        card__requirements=requirement, spent_time__gt=0
    ).order_by("date")

    # Start working date in this board
    start_working_date = board.get_working_start_date()
    if start_working_date is None:
        return burndown_chart.render_django_response()

    # End working date in this board
    end_working_date = board.get_working_end_date()
    if end_working_date is None:
        return burndown_chart.render_django_response()

    # Remaining time values
    remaining_time_values = [remaining_time]

    # Dates where there is some work in this requirement
    x_labels = ["Start"]

    date_i = copy.deepcopy(start_working_date)
    remaining_time_i = copy.deepcopy(remaining_time)
    while date_i <= end_working_date:
        spent_time = daily_spent_times.filter(date=date_i).aggregate(
            spent_time_sum=Sum("spent_time")
        )["spent_time_sum"]
        if spent_time is not None and spent_time > 0:
            remaining_time_i -= spent_time
            remaining_time_values.append(remaining_time_i)
            x_labels.append(date_i.strftime("%Y-%m-%d"))
        date_i += timedelta(days=1)

    burndown_chart.add(
        f"Initial estimation for {requirement.code}",
        [remaining_time for i in range(0, len(x_labels))],
    )
    burndown_chart.x_labels = x_labels
    burndown_chart.add(f"Burndown of {requirement.code}", remaining_time_values)

    chart = CachedChart.make(
        board=board, uuid=chart_uuid, svg=burndown_chart.render(is_unicode=True)
    )
    return chart.render_django_response()


# Burndown for all requirements
def _burndown_by_requirement(board):

    # Caching
    chart_uuid = f"requirements._burndown_by_requirement-{board.id}"
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = f"Burndown for board {board.name}"
    chart_title += f" as of {board.get_human_fetch_datetime()}"

    burndown_chart = pygal.Line(
        title=chart_title,
        legend_at_bottom=True,
        print_values=True,
        x_labels_major_count=30,
        show_minor_x_labels=False,
        print_zeroes=False,
        fill=False,
        human_readable=True,
        x_label_rotation=45,
    )

    # Estimated number of hours
    estimated_number_of_hours = board.requirements.aggregate(
        estimated_number_of_hours=Sum("estimated_number_of_hours")
    )["estimated_number_of_hours"]

    # Remaining hours
    remaining_time = estimated_number_of_hours
    daily_spent_times = (
        board.daily_spent_times.filter(
            card__requirements__board=board, spent_time__gt=0
        )
        .distinct()
        .order_by("date")
    )

    # Start working date in this board
    start_working_date = board.get_working_start_date()
    if start_working_date is None:
        return burndown_chart.render_django_response()

    # End working date in this board
    end_working_date = board.get_working_end_date()
    if end_working_date is None:
        return burndown_chart.render_django_response()

    # Remaining time values
    remaining_time_values = [remaining_time]

    # Dates where there is some work in this requirement
    x_labels = ["Start"]

    date_i = copy.deepcopy(start_working_date)
    remaining_time_i = copy.deepcopy(remaining_time)
    while date_i <= end_working_date:
        spent_time = daily_spent_times.filter(date=date_i).aggregate(
            spent_time_sum=Sum("spent_time")
        )["spent_time_sum"]
        if spent_time is not None and spent_time > 0:
            remaining_time_i -= spent_time
            remaining_time_values.append(remaining_time_i)
            x_labels.append(date_i.strftime("%Y-%m-%d"))
        date_i += timedelta(days=1)

    burndown_chart.add(
        f"{board.name} requirements estimation",
        [remaining_time for i in range(0, len(x_labels))],
    )
    burndown_chart.x_labels = x_labels
    burndown_chart.add(
        f"Burndown according to {board.name} requirements", remaining_time_values
    )

    chart = CachedChart.make(
        board=board, uuid=chart_uuid, svg=burndown_chart.render(is_unicode=True)
    )
    return chart.render_django_response()
