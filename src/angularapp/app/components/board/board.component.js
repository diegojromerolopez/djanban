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
var board_service_1 = require("../../services/board.service");
var router_2 = require("@angular/router");
var BoardComponent = (function () {
    function BoardComponent(router, route, boardService) {
        this.router = router;
        this.route = route;
        this.boardService = boardService;
        this.receivedData = [];
    }
    BoardComponent.prototype.ngOnInit = function () {
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            that.loadBoard(board_id);
        });
    };
    BoardComponent.prototype.loadBoard = function (board_id) {
        var _this = this;
        this.boardService.getBoard(board_id).then(function (board) { return _this.board = board; });
    };
    BoardComponent.prototype.onCardSelect = function (card) {
        this.router.navigate(['/board', this.board.id, 'card', card.id]);
    };
    BoardComponent.prototype.transferDataSuccess = function ($event) {
        console.log($event.dragData);
        this.receivedData.push($event.dragData);
    };
    return BoardComponent;
}());
BoardComponent = __decorate([
    core_1.Component({
        moduleId: module.id,
        selector: 'board',
        templateUrl: 'board.component.html',
        styleUrls: ['board.component.css'],
        providers: [board_service_1.BoardService]
    }),
    __metadata("design:paramtypes", [router_1.Router,
        router_2.ActivatedRoute,
        board_service_1.BoardService])
], BoardComponent);
exports.BoardComponent = BoardComponent;
//# sourceMappingURL=board.component.js.map