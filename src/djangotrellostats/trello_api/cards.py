from djangotrellostats.trello_api.connector import TrelloConnector

from trello import Card as TrelloCard
from trello import List as TrelloList
from collections import namedtuple


# Creates a new card
def new_card(card, member, labels=None):
    # Getting trello board
    trello_board = _get_trello_board(card.board, member)
    trello_list = trello_board.get_list(list_id=card.list.uuid)
    # Creation trello card
    trello_labels = []
    if labels:
        TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
        trello_labels = [TrelloLabelUuid(id=label.uuid) for label in labels]
    trello_card = trello_list.add_card(card.name, desc=card.description, labels=trello_labels, due="null", source=None)
    return trello_card


# Move the card to other list
def move_card(card, member, destination_list):
    trello_card = _get_trello_card(card, member)
    trello_card.change_list(destination_list.uuid)


# Add comment to a card
def add_comment_to_card(card, member, content):
    trello_card = _get_trello_card(card, member)
    return trello_card.comment(content)


# Edit comment content
def edit_comment_of_card(card, member, comment, new_content):
    if member.uuid != comment.author.uuid:
        raise AssertionError(u"You can only edit your comments")
    trello_card = _get_trello_card(card, member)
    return trello_card.update_comment(comment.uuid, new_content)


# Delete comment of card
def delete_comment_of_card(card, member, comment):
    trello_card = _get_trello_card(card, member)
    return trello_card.delete_comment({"id": comment.uuid})


# Add a labels to a card
def add_label_to_card(card, member, label):
    trello_card = _get_trello_card(card, member)
    TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
    return trello_card.add_label(TrelloLabelUuid(id=label.uuid))


# Add a labels to a card
def remove_label_of_card(card, member, label):
    trello_card = _get_trello_card(card, member)
    TrelloLabelUuid = namedtuple("TrelloLabelUuid", ["id"])
    return trello_card.remove_label(TrelloLabelUuid(id=label.uuid))


# Return the trello card of a given Card object.
# The member is used to establish the connection.
def _get_trello_card(card, member):
    trello_board = _get_trello_board(card.board, member)
    trello_card = TrelloCard(parent=trello_board, card_id=card.uuid)
    return trello_card


# Return the trello board of a given Board object.
def _get_trello_board(board, member):
    trello_connector = TrelloConnector(member)
    trello_board = trello_connector.trello_client.get_board(board.uuid)
    return trello_board
