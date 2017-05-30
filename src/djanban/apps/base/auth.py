
from django.conf import settings
from django.http import Http404

from djanban.apps.boards.models import Board


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
    return user and user.is_authenticated() and\
           (user.groups.filter(name=settings.ADMINISTRATOR_GROUP).exists() or user.is_superuser)


# Informs if one user is a member
def user_is_member(user):
    return hasattr(user, "member") and user.member


# Informs if one user is a visitor
def user_is_visitor(user, board=None):
    if board is None:
        return user.is_authenticated() and not user_is_member(user)
    return board.visitors.filter(id=user.id).exists()


# Return the boards of an user
def get_user_boards(user, is_archived=False):
    # Get all boards
    if user_is_administrator(user):
        if is_archived is True or is_archived is False:
            return Board.objects.filter(is_archived=is_archived).order_by("name")
        return Board.objects.all().order_by("name")

    # For a member, return all his/her boards
    if user_is_member(user):
        return get_member_boards(user.member, is_archived=is_archived)

    # If user is visitor, return his/her boards
    if user_is_visitor(user):
        if is_archived is True or is_archived is False:
            return user.boards.filter(is_archived=is_archived).order_by("name")
        return user.boards.all().order_by("name")

    raise ValueError(u"This user is not valid")


# Return the boards of a member
def get_member_boards(member, is_archived=False):
    # Get all boards if the member belongs to an administrator
    if user_is_administrator(member.user):
        if is_archived is True or is_archived is False:
            return Board.objects.filter(is_archived=is_archived).order_by("name")
        return Board.objects.all().order_by("name")

    # Member is an standard member
    if is_archived is None:
        return member.boards.all().order_by("name")
    return member.boards.filter(is_archived=is_archived).order_by("name")


# Get user board or a 404 exception
def get_user_board_or_404(user, board_id, is_archived=False):
    try:
        return get_user_boards(user=user, is_archived=is_archived).get(id=board_id)
    except Board.DoesNotExist as e:
        raise Http404
