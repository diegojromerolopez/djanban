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
var BoardComponent = (function () {
    function BoardComponent(router, route, boardService, cardService, dragulaService) {
        var _this = this;
        this.router = router;
        this.route = route;
        this.boardService = boardService;
        this.cardService = cardService;
        this.dragulaService = dragulaService;
        this.showNewCardForm = {};
        dragulaService.setOptions('lists', {
            moves: function (el, container, handle) {
                return handle.className === 'move_list_handle';
            }
        });
        dragulaService.drag.subscribe(function (value) {
            console.log("drag: " + value[0]);
            _this.onDrag(value.slice(1));
        });
        dragulaService.drop.subscribe(function (parameters) {
            console.log("drop: " + parameters[0]);
            console.log(parameters);
            // Card drop
            if (parameters[0] == "cards") {
                _this.onCardDrop(parameters);
            }
            else if (parameters[0] == "lists") {
                _this.onListDrop(parameters);
            }
        });
        dragulaService.over.subscribe(function (value) {
            console.log("over: " + value[0]);
            _this.onOver(value.slice(1));
        });
        dragulaService.out.subscribe(function (value) {
            console.log("out: " + value[0]);
            _this.onOut(value.slice(1));
        });
    }
    BoardComponent.prototype.ngOnInit = function () {
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            that.loadBoard(board_id);
        });
    };
    BoardComponent.prototype.onDrag = function (args) {
        var e = args[0], el = args[1];
        // do something
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
        console.log(parameters);
        // Moved list
        var moved_list_id = parameters[1]["dataset"]["list"];
        var moved_list = new list_1.List(this.board.getListById(parseInt(moved_list_id)));
        // Next list after the list has been moved
        var next_list_id = parameters[4]["dataset"]["list"];
        var next_list = null;
        var destination_position = "bottom";
        if (next_list_id) {
            next_list = new list_1.List(this.board.getListById(parseInt(next_list_id)));
            console.log("THIS IS NEXT LIST");
            console.log(next_list);
            console.log("THIS IS NEXT LIST POSITION");
            console.log(next_list.position);
            destination_position = (next_list.position - 10).toString();
        }
        this.boardService.moveList(this.board, moved_list, destination_position).then(function (list) { moved_list.position = list.position; });
    };
    BoardComponent.prototype.onOver = function (args) {
        var e = args[0], el = args[1], container = args[2];
        // do something
    };
    BoardComponent.prototype.onOut = function (args) {
        var e = args[0], el = args[1], container = args[2];
        // do something
    };
    /** Load board */
    BoardComponent.prototype.loadBoard = function (board_id) {
        var _this = this;
        this.boardService.getBoard(board_id).then(function (board_response) {
            _this.board = new board_1.Board(board_response);
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
            _this.showNewCardForm[list.id] = false;
        });
    };
    return BoardComponent;
}());
BoardComponent = __decorate([
    core_1.Component({
        moduleId: module.id,
        selector: 'board',
        templateUrl: 'board.component.html',
        styleUrls: ['board.component.css'],
        providers: [board_service_1.BoardService, card_service_1.CardService, ng2_dragula_1.DragulaService]
    }),
    __metadata("design:paramtypes", [router_1.Router,
        router_2.ActivatedRoute,
        board_service_1.BoardService,
        card_service_1.CardService,
        ng2_dragula_1.DragulaService])
], BoardComponent);
exports.BoardComponent = BoardComponent;
//# sourceMappingURL=board.component.js.map