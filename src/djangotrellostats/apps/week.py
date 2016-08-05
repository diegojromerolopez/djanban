

# Return the iso week of year of a date
def get_iso_week_of_year(date):
    iso_calendar_date = date.isocalendar()
    week_of_year = iso_calendar_date[1]
    return week_of_year


def get_week_of_year(date):
    week_of_year = get_iso_week_of_year(date)
    return u"{0}W{1}".format(date.year, week_of_year)