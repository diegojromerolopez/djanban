# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import copy

import pygal
from django.db.models import Sum, Count
from django.utils import timezone
from isoweek import Week

from djanban.apps.base.auth import get_user_boards
from djanban.apps.boards.models import CardComment, Card
from djanban.apps.charts.models import CachedChart
from djanban.apps.dev_environment.models import Interruption
from djanban.apps.dev_times.models import DailySpentTime
from djanban.apps.members.models import Member
from djanban.utils.week import number_of_weeks_of_year, get_iso_week_of_year


# Show a chart with the task movements (backward or forward) by member
def task_movements_by_member(movement_type="forward", board=None):
    if movement_type != "forward" and movement_type != "backward":
        raise ValueError("{0} is not recognized as a valid movement type".format(movement_type))

    # Caching
    chart_uuid = "members.task_movements_by_member-{0}-{1}".format(movement_type, board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Task {0} movements as of {1}".format(movement_type, timezone.now())
    if board:
        chart_title += u" for board {0}".format(board.name)

    member_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True, print_zeroes=False,
                                       human_readable=True)

    report_filter = {}
    if board:
        report_filter["board_id"] = board.id

    members = Member.objects.all().order_by("id")

    for member in members:
        member_name = member.external_username

        member_report_filter = copy.deepcopy(report_filter)
        member_report_filter["member"] = member


        # Depending on if the member report is filtered by board or not we only have to get the forward and
        # backward movements of a report or sum all the members report of this user
        if board:
            forward_movements = member.forward_movements
            backward_movements = member.backward_movements
        else:
            forward_movements = member.get_forward_movements_for_board(board)
            backward_movements = member.get_backward_movements_for_board(board)

        if movement_type == "forward":
            member_chart.add(u"{0}'s tasks forward movements".format(member_name), forward_movements)

        elif movement_type == "backward":
            member_chart.add(u"{0}'s tasks backward movements".format(member_name), backward_movements)


    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=member_chart.render(is_unicode=True))
    return chart.render_django_response()


# Spent time by week by member
def spent_time_by_week(current_user, week_of_year=None, board=None):
    if week_of_year is None:
        now = timezone.now()
        today = now.date()
        week_of_year_ = get_iso_week_of_year(today)
        week_of_year = "{0}W{1}".format(today.year, week_of_year_)

    # Caching
    chart_uuid = "members.spent_time_by_week-{0}-{1}".format(current_user.id, week_of_year, board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    y, w = week_of_year.split("W")
    week = Week(int(y), int(w))
    start_of_week = week.monday()
    end_of_week = week.sunday()

    chart_title = u"Spent time in week {0} ({1} - {2})".format(week_of_year,
                                                               start_of_week.strftime("%Y-%m-%d"),
                                                               end_of_week.strftime("%Y-%m-%d"))
    if board:
        chart_title += u" for board {0}".format(board.name)

    spent_time_chart = pygal.HorizontalBar(title=chart_title, legend_at_bottom=True, print_values=True,
                                           print_zeroes=False, human_readable=True)

    report_filter = {"date__year": y, "week_of_year": w}
    if board:
        report_filter["board_id"] = board.id

    team_spent_time = 0

    if board is None:
        boards = get_user_boards(current_user)
    else:
        boards = [board]
    members = Member.objects.filter(boards__in=boards, is_developer=True).distinct().order_by("id")
    for member in members:
        member_name = member.external_username
        daily_spent_times = member.daily_spent_times.filter(**report_filter)
        spent_time = daily_spent_times.aggregate(Sum("spent_time"))["spent_time__sum"]
        if spent_time is None:
            spent_time = 0
        team_spent_time += spent_time

        if spent_time > 0:
            spent_time_chart.add(u"{0}'s spent time".format(member_name), spent_time)

    spent_time_chart.add(u"Team spent time", team_spent_time)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=spent_time_chart.render(is_unicode=True))
    return chart.render_django_response()


# Spent time by weekday by member
def avg_spent_time_by_weekday(current_user, board=None):

    # Caching
    chart_uuid = "members.avg_spent_time_by_weekday-{0}-{1}".format(current_user, board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Average spent time by weekday by member"
    if board:
        chart_title += u" for board {0}".format(board.name)

    spent_time_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                  print_zeroes=False, human_readable=True)

    report_filter = {}
    if board:
        report_filter["board_id"] = board.id

    team_spent_time = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

    if board is None:
        boards = get_user_boards(current_user)
    else:
        boards = [board]

    spent_time_chart.x_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    members = Member.objects.filter(boards__in=boards, is_developer=True).distinct().order_by("id")
    for member in members:
        member_name = member.external_username
        daily_spent_times = member.daily_spent_times.filter(**report_filter)

        # For each week day we got his/her average number of hours he/she works
        member_weekday_spent_time = []
        for weekday_i in range(1, 8):
            # Number of different dates with this weekday this member has worked
            num_weekday_i = daily_spent_times.filter(weekday=weekday_i).aggregate(num_weekday_i=Count('date', distinct=True))["num_weekday_i"]

            # Sum of spent time this member has worked in this weekday
            member_sum_spent_time_in_weekday = daily_spent_times.filter(weekday=weekday_i).aggregate(avg_spent_time=Sum("spent_time"))["avg_spent_time"]

            # If the member has no work in some weekday (for example Saturday or Sunday)
            if member_sum_spent_time_in_weekday is None:
                member_sum_spent_time_in_weekday = 0

            # Avoid division by zero
            if num_weekday_i == 0:
                member_weekday_spent_time.append(0)

            else:
                member_weekday_spent_time.append(member_sum_spent_time_in_weekday/num_weekday_i)
                team_spent_time[weekday_i] += member_sum_spent_time_in_weekday/num_weekday_i

        spent_time_chart.add(u"{0}".format(member_name), member_weekday_spent_time)

    num_members = members.count()
    if num_members > 0:
        spent_time_chart.add(
            u"All members",
            [weekday_spent_time/num_members for weekday_i, weekday_spent_time in team_spent_time.items()]
        )

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=spent_time_chart.render(is_unicode=True))
    return chart.render_django_response()


# Evolution of spent time by member
def spent_time_by_week_evolution(board, show_interruptions=False):

    # Caching
    chart_uuid = "members.spent_time_by_week_evolution-{0}-{1}".format(board.id, "with_interruptions" if show_interruptions else "without_interruptions")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Evolution of each member's spent time by week"
    if show_interruptions:
        chart_title += u", including interruptions suffered by the team, "
    chart_title += u" for board {0} (fetched on {1})".format(board.name, board.get_human_fetch_datetime())

    evolution_chart = pygal.Line(title=chart_title, legend_at_bottom=True, print_values=False,
                                 print_zeroes=False, fill=False,
                                 human_readable=True, x_label_rotation=45)

    start_working_date = board.get_working_start_date()
    end_working_date = board.get_working_end_date()
    if start_working_date is None or end_working_date is None:
        return evolution_chart.render_django_response()

    start_week = get_iso_week_of_year(start_working_date)
    end_week = get_iso_week_of_year(end_working_date)

    members = board.members.filter(is_developer=True).order_by("id")

    member_values = {member.id:[] for member in members}
    member_values["all"] = []

    interruptions = []

    x_labels = []

    week_i = copy.deepcopy(start_week)
    year_i = start_working_date.year
    while year_i < end_working_date.year or (year_i == end_working_date.year and week_i < end_week):

        week_i_start_date = Week(year_i, week_i).monday()
        week_i_end_date = Week(year_i, week_i).sunday()

        there_is_data = board.daily_spent_times.filter(date__year=year_i, week_of_year=week_i).exists()
        if there_is_data:
            x_labels.append(u"{0}W{1}".format(year_i, week_i))

            team_spent_time = 0
            for member in members:
                daily_spent_times = member.daily_spent_times.filter(board=board, date__year=year_i, week_of_year=week_i)
                spent_time = daily_spent_times.aggregate(Sum("spent_time"))["spent_time__sum"]
                if spent_time is None:
                    spent_time = 0
                team_spent_time += spent_time

                if spent_time > 0:
                    member_values[member.id].append(spent_time)

            member_values["all"].append(team_spent_time)

            if show_interruptions:
                num_interruptions = Interruption.objects.filter(
                    datetime__year=year_i,
                    datetime__date__gte=week_i_start_date,
                    datetime__date__lte=week_i_end_date
                ).count()
                if num_interruptions > 0:
                    interruptions.append(num_interruptions)

        week_i += 1
        if week_i > number_of_weeks_of_year(year_i):
            week_i = 1
            year_i += 1

    evolution_chart.x_labels = x_labels
    for member in members:
        evolution_chart.add(member.external_username, member_values[member.id])

    evolution_chart.add("All members", member_values["all"])
    if show_interruptions:
        evolution_chart.add("Interruptions", interruptions)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=evolution_chart.render(is_unicode=True))
    return chart.render_django_response()


# Number of total comments by member for this board or card
def number_of_comments(current_user, board=None, card=None):

    # Caching
    chart_uuid = "members.number_of_comments-{0}-{1}-{2}".format(current_user.id, board.id if board else "None", card.id if card else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Number of comments by member as of {0}".format(timezone.now())

    if board:
        chart_title += u" for board {0}".format(board.name)
        if card:
            chart_title += u" for card '{0}'".format(card.name)
        chart_title += " (fetched on {0})".format(board.get_human_fetch_datetime())

    number_of_comments_chart = pygal.Bar(
        title=chart_title, legend_at_bottom=True, print_values=False, print_zeroes=False, fill=False,
        margin=0, human_readable=True
    )

    card_comment_filter = {}
    if board:
        card_comment_filter["card__board"] = board
        if card:
            card_comment_filter["card"] = card
            number_of_comments_chart.show_minor_x_labels = True

    card_comments = CardComment.objects.filter(**card_comment_filter)

    # If there are no comments, render an empty chart
    if not card_comments.exists():
        return number_of_comments_chart.render_django_response()

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    members = Member.objects.filter(boards__in=boards).distinct().order_by("id")

    total_number_of_comments = 0
    for member in members:
        member_number_of_comments = card_comments.filter(author=member).count()
        total_number_of_comments += member_number_of_comments
        number_of_comments_chart.add(member.external_username, member_number_of_comments)

    number_of_comments_chart.add("Total number of comments", total_number_of_comments)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=number_of_comments_chart.render(is_unicode=True))
    return chart.render_django_response()


# Number of total cards by member for this board or card
def number_of_cards(current_user, board=None):

    # Caching
    chart_uuid = "members.number_of_cards-{0}-{1}".format(current_user.id, board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Number of cards by member as of {0}".format(timezone.now())

    if board:
        chart_title += u" for board {0}".format(board.name)
        chart_title += u" (fetched on {0})".format(board.get_human_fetch_datetime())

    number_of_cards_chart = pygal.Bar(
        title=chart_title, legend_at_bottom=True, print_values=False, print_zeroes=False, fill=False,
        margin=0, human_readable=True
    )

    card_comment_filter = {}
    if board:
        card_comment_filter["board"] = board

    cards = Card.objects.filter(**card_comment_filter)

    # If there are no cards, render an empty chart
    if not cards.exists():
        return number_of_cards_chart.render_django_response()

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    members = Member.objects.filter(boards__in=boards).distinct().order_by("id")

    total_number_of_cards = 0
    for member in members:
        number_of_cards_by_member = cards.filter(members=member).count()
        total_number_of_cards += number_of_cards_by_member
        number_of_cards_chart.add(member.external_username, number_of_cards_by_member)

    number_of_cards_chart.add("Total number of cards", total_number_of_cards)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=number_of_cards_chart.render(is_unicode=True))
    return chart.render_django_response()


# Spent time by member
def spent_time(current_user, board=None):

    # Caching
    chart_uuid = "members.spent_time-{0}-{1}".format(current_user.id, board.id if board else "None")
    chart = CachedChart.get(board=board, uuid=chart_uuid)
    if chart:
        return chart

    chart_title = u"Spent time by member as of {0}".format(timezone.now())

    if board:
        chart_title += u" for board {0}".format(board.name)
        chart_title += u" (fetched on {0})".format(board.get_human_fetch_datetime())

    if board:
        boards = [board]
    else:
        boards = get_user_boards(current_user)

    spent_time_chart = pygal.Bar(
        title=chart_title, legend_at_bottom=True, print_values=False, print_zeroes=False, fill=False,
        margin=0, human_readable=True
    )

    members = Member.objects.filter(boards__in=boards).distinct().order_by("id")

    spent_times = DailySpentTime.objects.filter(board__in=boards)

    total_spent_time_sum = 0
    for member in members:
        member_spent_time_sum = spent_times.filter(member=member).aggregate(sum=Sum("spent_time"))["sum"]
        if member_spent_time_sum is not None and member_spent_time_sum > 0:
            spent_time_chart.add(member.external_username, member_spent_time_sum)
            total_spent_time_sum += member_spent_time_sum

    spent_time_chart.add("Total spent time", total_spent_time_sum)

    chart = CachedChart.make(board=board, uuid=chart_uuid, svg=spent_time_chart.render(is_unicode=True))
    return chart.render_django_response()
