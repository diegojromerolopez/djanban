
from django.conf import settings


def member_is_administrator(member):
    """
    Check if the member is an administrator of this platform.
    Parameters
    ----------
    member: member.Member to be checked.

    Returns
    -------
    True if the associated user to this member is an administrator, False otherwise.
    """
    return user_is_administrator(member.user)


def user_is_administrator(user):
    """
    Check if an user is an administrator of this platform.
    Parameters
    ----------
    user: auth.User to be checked.

    Returns
    -------
    True if the user belongs to administrator groups, False otherwise.
    """
    return user and user.is_authenticated() and user.groups.filter(name=settings.ADMINISTRATOR_GROUP).exists()