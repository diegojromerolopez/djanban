from __future__ import unicode_literals, absolute_import


class Fetcher(object):
    FETCH_LOCK_FILE_PATH = u"/tmp/django-trello-stats-fetch-board-{0}-lock.txt"

    def __init__(self, board):
        super(Fetcher, self).__init__()
        self.board = board
        self.cycle_lists = board.cycle_time_lists()
        self.lead_lists = board.lead_time_lists()
        self.lists = board.lists.all()
        self.members = board.members.all()
        self.creator = board.creator

        self.fetch_start_time = None
        self.fetch_end_time = None
