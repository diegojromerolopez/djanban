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
var DashboardComponent = (function () {
    function DashboardComponent(router, boardService) {
        this.router = router;
        this.boardService = boardService;
    }
    DashboardComponent.prototype.ngOnInit = function () {
        this.loadBoards();
    };
    DashboardComponent.prototype.loadBoards = function () {
        var _this = this;
        this.boardService.getBoards().then(function (boards) { return _this.boards = boards; });
    };
    DashboardComponent.prototype.onBoardSelect = function (board) {
        this.router.navigate([board.id]);
    };
    return DashboardComponent;
}());
DashboardComponent = __decorate([
    core_1.Component({
        moduleId: module.id,
        selector: 'dashboard',
        templateUrl: 'dashboard.component.html',
        styleUrls: ['dashboard.component.css'],
        providers: [board_service_1.BoardService]
    }),
    __metadata("design:paramtypes", [router_1.Router,
        board_service_1.BoardService])
], DashboardComponent);
exports.DashboardComponent = DashboardComponent;
//# sourceMappingURL=dashboard.component.js.map