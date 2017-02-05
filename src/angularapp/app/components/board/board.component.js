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
    function BoardComponent(router, route, memberService, boardService, cardService, dragulaService, notificationsService) {
        var _this = this;
        this.router = router;
        this.route = route;
        this.memberService = memberService;
        this.boardService = boardService;
        this.cardService = cardService;
        this.dragulaService = dragulaService;
        this.notificationsService = notificationsService;
        this.newCardFormStatus = {};
        this.removeMemberStatus = {};
        this.addMemberStatus = {};
        this.moveAllCardsStatus = {};
        dragulaService.setOptions('lists', {
            moves: function (el, container, handle) {
                return handle.className === 'move_list_handle' || handle.className == 'move_list_handle_icon';
            }
        });
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
    BoardComponent.prototype.ngOnInit = function () {
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            that.loadBoard(board_id);
        });
        this.loadMembers();
        this.notificationsService.success("WELLCOME", "WOWOW");
    };
    BoardComponent.prototype.onCardDrop = function (parameters) {
        // Source list
        var source_list_id = parameters[3]["dataset"]["list"];
        var source_list = new list_1.List(this.board.getListById(parseInt(source_list_id)));
        // Destination list
        var destination_list_id = parameters[2]["dataset"]["list"];
        var destination_list = new list_1.List(this.board.getListById(parseInt(destination_list_id)));
        // Card that has bee moved from source list to destination list
        var moved_card_id = parameters[1]["dataset"]["card"];
        var moved_card = destination_list.getCardById(parseInt(moved_card_id));
        // Next card in order in destination
        var next_card_in_destination_id = null;
        // If next card is null, the moved card is the last one of the list
        var next_card = null;
        if (parameters[4] != null) {
            next_card_in_destination_id = parameters[4]["dataset"]["card"];
            next_card = destination_list.getCardById(parseInt(next_card_in_destination_id));
        }
        var destination_position = "bottom";
        if (next_card != null) {
            destination_position = (next_card.position - 10).toString();
        }
        // Move card to list
        this.cardService.moveCard(moved_card, destination_list, destination_position).then(function (card) {
            //source_list.removeCard(moved_card);
            //destination_list.addCard(moved_card, destination_position);
        });
    };
    BoardComponent.prototype.onListDrop = function (parameters) {
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
        this.boardService.moveList(this.board, moved_list, destination_position).then(function (list) { moved_list.position = list.position; });
    };
    /** Prepare board attributes, status, etc. when fetching the board from the server */
    BoardComponent.prototype.prepareBoard = function (board_response) {
        this.board = new board_1.Board(board_response);
        for (var _i = 0, _a = this.board.lists; _i < _a.length; _i++) {
            var list = _a[_i];
            this.newCardFormStatus[list.id] = { show: false, waiting: false };
            this.moveAllCardsStatus[list.id] = "hidden";
        }
    };
    /** Load board */
    BoardComponent.prototype.loadBoard = function (board_id) {
        var _this = this;
        this.boardService.getBoard(board_id).then(function (board_response) {
            _this.prepareBoard(board_response);
        });
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
        });
    };
    /** Move to the card view */
    BoardComponent.prototype.onCardSelect = function (card) {
        this.router.navigate([this.board.id, 'card', card.id]);
    };
    /* Controls for card creation form */
    BoardComponent.prototype.onNewCardSubmit = function (list, name, position) {
        var _this = this;
        this.cardService.addCard(this.board, list, name, position).then(function (card_response) {
            list_1.List.addCardToList(list, card_response, position);
            _this.newCardFormStatus[list.id] = { "show": false, "waiting": false };
        });
    };
    BoardComponent.prototype.onMoveAllCardsSubmit = function (source_list_id, destination_list_id) {
        var _this = this;
        console.log(source_list_id, destination_list_id);
        var source_list = this.board.lists.find(function (list_i) { return list_i.id == source_list_id; });
        var destination_list = this.board.lists.find(function (list_i) { return list_i.id == destination_list_id; });
        if (source_list && destination_list) {
            this.cardService.moveAllListCards(this.board, source_list, destination_list).then(function (board_response) { return _this.prepareBoard(board_response); });
        }
        else {
            console.error("There is something wrong with the lists");
        }
    };
    /* Member actions */
    BoardComponent.prototype.removeMember = function (member) {
        var _this = this;
        this.boardService.removeMember(this.board, member).then(function (deleted_member) {
            _this.board.removeMember(member);
            _this.removeMemberStatus[member.id] = { waiting: false };
        });
    };
    BoardComponent.prototype.onAddMemberSubmit = function (member_id) {
        var _this = this;
        var member = this.members.find(function (member_i) { return member_i.id == member_id; });
        if (member) {
            this.boardService.addMember(this.board, member).then(function (added_member) {
                _this.board.addMember(added_member);
                _this.addMemberStatus = { show: false, waiting: false };
            });
        }
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
    }),
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