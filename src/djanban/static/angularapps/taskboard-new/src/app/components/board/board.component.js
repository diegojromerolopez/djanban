"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
var core_1 = require("@angular/core");
var router_1 = require("@angular/router");
var board_1 = require("../../models/board");
var board_service_1 = require("../../services/board.service");
var router_2 = require("@angular/router");
var ng2_dragula_1 = require("ng2-dragula/ng2-dragula");
var list_1 = require("../../models/list");
var card_service_1 = require("../../services/card.service");
var member_service_1 = require("../../services/member.service");
var angular2_notifications_1 = require("angular2-notifications");
var BoardComponent = (function () {
    /** Constructor of BoardComponent: initialization of status and setting up the Dragula service */
    function BoardComponent(router, route, memberService, boardService, cardService, dragulaService, notificationsService) {
        var _this = this;
        this.router = router;
        this.route = route;
        this.memberService = memberService;
        this.boardService = boardService;
        this.cardService = cardService;
        this.dragulaService = dragulaService;
        this.notificationsService = notificationsService;
        // NotificationsService options
        this.notificationsOptions = {
            position: ["top", "right"],
            timeOut: 10000,
            pauseOnHover: true,
        };
        // Visibility of the closed cards
        this.closedItemsVisibility = "hidden";
        // Initialization of statuses
        this.newCardFormStatus = {};
        this.removeMemberStatus = {};
        this.addMemberStatus = {};
        this.moveAllCardsStatus = {};
        // Label filter: show only the cards that has a label here
        this.labelFilter = [];
        this.labelFilterHash = {};
        this.reloading = false;
        // Options of the drag and drop service
        dragulaService.setOptions('lists', {
            moves: function (el, container, handle) {
                return handle.className === 'move_list_handle' || handle.className == 'move_list_handle_icon';
            }
        });
        // Subscription to drop event 
        dragulaService.drop.subscribe(function (parameters) {
            // Card drop
            if (parameters[0] == "cards") {
                _this.onCardDrop(parameters);
            }
            else if (parameters[0] == "lists") {
                _this.onListDrop(parameters);
            }
        });
    }
    /** First thing we have to do is loading both the board and all available members */
    BoardComponent.prototype.ngOnInit = function () {
        this.reloadBoard();
    };
    /** Reload the board */
    BoardComponent.prototype.reloadBoard = function () {
        this.reloading = true;
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            that.loadBoard(board_id);
        });
        this.loadMembers();
    };
    /** Action of the drop card event */
    BoardComponent.prototype.onCardDrop = function (parameters) {
        var _this = this;
        console.log(parameters);
        // Source list
        var source_list_id = parameters[3]["dataset"]["list"];
        var source_list = this.board.getListById(parseInt(source_list_id));
        // Destination list
        var destination_list_id = parameters[2]["dataset"]["list"];
        var destination_list = this.board.getListById(parseInt(destination_list_id));
        // Card that has bee moved from source list to destination list
        var moved_card_id = parameters[1]["dataset"]["card"];
        var moved_card = destination_list.getCardById(parseInt(moved_card_id));
        var old_moved_card_position = moved_card.position;
        // Next card in order in destination
        var next_card_in_destination_id = null;
        // If next card is null, the moved card is the last one of the list
        var next_card = null;
        if (parameters[4] != null) {
            next_card_in_destination_id = parameters[4]["dataset"]["card"];
            next_card = destination_list.getCardById(parseInt(next_card_in_destination_id));
        }
        // Position of the moved card. It will be based on the next card on the destination list (if exists).
        // Otherwise, the position will be at the bottom of the list.
        var destination_position = "bottom";
        if (next_card != null) {
            destination_position = (next_card.position - 10).toString();
        }
        if (source_list_id == destination_list_id) {
            destination_list = null;
        }
        // Move card
        // - To another list
        // - In the same list up or down
        this.cardService.moveCard(moved_card, destination_list, destination_position)
            .then(function (board_response) {
            _this.prepareBoard(board_response);
            var sucessMessage = destination_list ? moved_card.name + " was moved to list " + destination_list.name + " sucessfully" : "Change position of " + moved_card.name + " sucessfully";
            _this.notificationsService.success("Card moved successfully", sucessMessage);
        }).catch(function (error_message) {
            _this.loadBoard(_this.board.id);
            _this.notificationsService.error("Error", "Couldn't move card " + moved_card.name + ". " + error_message);
        });
    };
    /** Action of the drop list event */
    BoardComponent.prototype.onListDrop = function (parameters) {
        var _this = this;
        // Moved list
        var moved_list_id = parameters[1]["dataset"]["list"];
        var moved_list = new list_1.List(this.board.getListById(parseInt(moved_list_id)));
        // Next list after the list has been moved
        var next_list_id = parameters[4]["dataset"]["list"];
        var next_list = null;
        var destination_position = "bottom";
        if (next_list_id) {
            next_list = new list_1.List(this.board.getListById(parseInt(next_list_id)));
            destination_position = (next_list.position - 10).toString();
        }
        // Call to list mover service
        this.boardService.moveList(this.board, moved_list, destination_position).then(function (list) {
            moved_list.position = list.position;
            // Sucess message
            // Show one message or another depending on if this is the last list or not
            var successNotificationMessage = null;
            if (next_list != null) {
                var successNotificationMessage_1 = moved_list.name + " was sucessfully moved at in front of " + next_list.name;
            }
            else {
                var successNotificationMessage_2 = moved_list.name + " was sucessfully moved at the end of the board";
            }
            _this.notificationsService.success("List moved successfully", successNotificationMessage);
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't move list " + moved_list.name + ". " + error_message);
        });
    };
    /** Prepare board attributes, status, etc. when fetching the board from the server */
    BoardComponent.prototype.prepareBoard = function (board_response) {
        this.board = new board_1.Board(board_response);
        var list_i = 0;
        var cards = [];
        for (var _i = 0, _a = this.board.lists; _i < _a.length; _i++) {
            var list = _a[_i];
            this.board.lists[list_i] = new list_1.List(list);
            this.newCardFormStatus[list.id] = { show: false, waiting: false };
            this.moveAllCardsStatus[list.id] = "hidden";
            cards = cards.concat(this.board.lists[list_i].cards);
            list_i += 1;
        }
        this.cardSearchOptions = [];
        for (var _b = 0, cards_1 = cards; _b < cards_1.length; _b++) {
            var card = cards_1[_b];
            this.cardSearchOptions.push({ value: card.id, label: card.name });
        }
    };
    /** Load board */
    BoardComponent.prototype.loadBoard = function (board_id) {
        var _this = this;
        this.boardService.getBoard(board_id).then(function (board_response) {
            _this.prepareBoard(board_response);
            _this.notificationsService.success("Loaded successfully", "Board loaded successfully", { timeOut: 3000 });
            _this.reloading = false;
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't load board. " + error_message);
        });
        ;
    };
    /** Load all available members */
    BoardComponent.prototype.loadMembers = function () {
        var _this = this;
        this.memberService.getMembers().then(function (members) {
            _this.members = members;
            for (var _i = 0, _a = _this.members; _i < _a.length; _i++) {
                var member = _a[_i];
                _this.removeMemberStatus[member.id] = { waiting: false };
            }
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't load members. " + error_message);
        });
    };
    /** Move to the card view */
    BoardComponent.prototype.onCardSelect = function (card) {
        this.router.navigate([this.board.id, 'card', card.id]);
    };
    /** Move to the card view */
    BoardComponent.prototype.onCardIdSelect = function (cardId) {
        this.router.navigate([this.board.id, 'card', cardId]);
    };
    /* Controls for card creation form */
    BoardComponent.prototype.onNewCardSubmit = function (list, name, position) {
        var _this = this;
        this.cardService.addCard(this.board, list, name, position).then(function (card_response) {
            list_1.List.addCardToList(list, card_response, position);
            _this.newCardFormStatus[list.id] = { "show": false, "waiting": false };
            _this.notificationsService.success("New card created", card_response.name + " was successfully created.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't add card to board " + list.name + " on board " + _this.board.name + ". " + error_message);
            _this.newCardFormStatus[list.id] = { "show": true, "waiting": false };
        });
    };
    /** Action of the move all cards submit form */
    BoardComponent.prototype.onMoveAllCardsSubmit = function (source_list_id, destination_list_id) {
        var _this = this;
        console.log(source_list_id, destination_list_id);
        var sourceList = this.board.lists.find(function (list_i) { return list_i.id == source_list_id; });
        var numberOfCardsToMove = sourceList.cards.length;
        var destinationList = this.board.lists.find(function (list_i) { return list_i.id == destination_list_id; });
        if (sourceList && destinationList) {
            this.cardService.moveAllListCards(this.board, sourceList, destinationList).then(function (board_response) {
                _this.prepareBoard(board_response);
                _this.notificationsService.success("Cards moved", numberOfCardsToMove + " cards from " + sourceList.name + " were moved to " + destinationList.name + ".");
            }).catch(function (error_message) {
                _this.notificationsService.error("Error", "Couldn't move all cards from " + sourceList.name + " to " + destinationList.name + " on board " + _this.board.name + ". " + error_message);
            });
        }
        else {
            this.notificationsService.error("Unable to move cards", "There is something wrong with " + sourceList.name + " or " + destinationList.name + ".");
        }
    };
    /* Member actions */
    BoardComponent.prototype.removeMember = function (member) {
        var _this = this;
        this.boardService.removeMember(this.board, member).then(function (deleted_member) {
            _this.board.removeMember(member);
            _this.removeMemberStatus[member.id] = { waiting: false };
            _this.notificationsService.success("Removed member", member.external_username + " was successfully removed from " + _this.board.name + ".");
        });
    };
    BoardComponent.prototype.onAddMemberSubmit = function (member_id, member_type) {
        var _this = this;
        var member = this.members.find(function (member_i) { return member_i.id == member_id; });
        if (member) {
            this.boardService.addMember(this.board, member, member_type).then(function (added_member) {
                _this.board.addMember(added_member);
                _this.addMemberStatus = { show: false, waiting: false };
                _this.notificationsService.success("Added member", member.external_username + " was successfully added to " + _this.board.name + ".");
            }).catch(function (error_message) {
                _this.notificationsService.error("Error", "Couldn't add a new member to board " + _this.board.name + ". " + error_message);
            });
        }
    };
    /* Label filter */
    BoardComponent.prototype.cardInLabelFilter = function (card) {
        // If there is no filter, card is always in the filter
        if (this.labelFilter.length == 0) {
            return true;
        }
        // Otherwise, check if any of the labels of the card is in the filter
        for (var _i = 0, _a = card.labels; _i < _a.length; _i++) {
            var label = _a[_i];
            if (label.id in this.labelFilterHash) {
                return true;
            }
        }
        // If none of the labels of the car is in the filter, this card is filtered out
        return false;
    };
    /** Return a list with the cards that are in the current label filter */
    BoardComponent.prototype.cardsInLabelFilter = function (cards, onlyActive) {
        var filteredCards = [];
        for (var _i = 0, cards_2 = cards; _i < cards_2.length; _i++) {
            var card = cards_2[_i];
            // A card is in the label filter if:
            // We are selected open cards and this card is not closed OR we are not selecting only active cards
            // and there is some label in the filter or the latter is empty.
            if (((onlyActive && !card.is_closed) || !onlyActive) && this.cardInLabelFilter(card)) {
                filteredCards.push(card);
            }
        }
        return filteredCards;
    };
    /** Return a list with the active cards */
    BoardComponent.prototype.activeCards = function (cards) {
        var activeCards = [];
        for (var _i = 0, cards_3 = cards; _i < cards_3.length; _i++) {
            var card = cards_3[_i];
            // Filter out closed cards
            if (!card.is_closed) {
                activeCards.push(card);
            }
        }
        return activeCards;
    };
    BoardComponent.prototype.addLabelToLabelFilter = function (label_id) {
        var label = this.board.getLabelById(label_id);
        if (this.labelFilter.findIndex(function (label_i) { return label_i.id == label_id; }) >= 0) {
            return;
        }
        this.labelFilter.push(label);
        this.labelFilterHash[label_id] = label;
    };
    BoardComponent.prototype.removeLabelFromLabelFilter = function (label_id) {
        var label = this.board.getLabelById(label_id);
        var labelIndex = this.labelFilter.findIndex(function (label_i) { return label_i.id == label.id; });
        this.labelFilter = this.labelFilter.slice(0, labelIndex).concat(this.labelFilter.slice(labelIndex + 1));
        delete this.labelFilterHash[label_id];
    };
    return BoardComponent;
}());
BoardComponent = __decorate([
    core_1.Component({
        moduleId: module.id,
        selector: 'board',
        templateUrl: 'board.component.html',
        styleUrls: ['board.component.css'],
        providers: [member_service_1.MemberService, board_service_1.BoardService, card_service_1.CardService, ng2_dragula_1.DragulaService, angular2_notifications_1.NotificationsService]
    })
    /** Board component: manages all user-board interactions */
    ,
    __metadata("design:paramtypes", [router_1.Router,
        router_2.ActivatedRoute,
        member_service_1.MemberService,
        board_service_1.BoardService,
        card_service_1.CardService,
        ng2_dragula_1.DragulaService,
        angular2_notifications_1.NotificationsService])
], BoardComponent);
exports.BoardComponent = BoardComponent;
//# sourceMappingURL=board.component.js.map