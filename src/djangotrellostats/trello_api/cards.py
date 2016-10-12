from djangotrellostats.trello_api.connector import TrelloConnector

from trello import Card as TrelloCard


# Move the card to other list
def move_card(card, member, destination_list):
    trello_card = _get_trello_card(card, member)
    trello_card.change_list(destination_list.uuid)


# Add comment to a card
def add_comment_to_card(card, member, content):
    trello_card = _get_trello_card(card, member)
    return trello_card.comment(content)


# Delete comment of card
def delete_comment_of_card(card, member, comment):
    trello_card = _get_trello_card(card, member)
    return trello_card.delete_comment({"id": comment.uuid})


# Return the trello card of a given Card object.
# The member is used to establish the connection.
def _get_trello_card(card, member):
    trello_connector = TrelloConnector(member)
    trello_board = trello_connector.trello_client.get_board(card.board.uuid)
    trello_card = TrelloCard(parent=trello_board, card_id=card.uuid)
    return trello_card
