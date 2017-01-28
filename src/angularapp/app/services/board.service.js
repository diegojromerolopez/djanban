"use strict";
var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var core_1 = require('@angular/core');
var http_1 = require('@angular/http');
var djangotrellostats_service_1 = require('./djangotrellostats.service');
require('rxjs/add/operator/map');
require('rxjs/add/operator/catch');
require('rxjs/add/operator/toPromise');
var BoardService = (function (_super) {
    __extends(BoardService, _super);
    function BoardService(http) {
        _super.call(this, http);
        this.GET_BOARDS_URL = 'http://localhost:8000/api/boards/info';
        this.GET_BOARD_URL = 'http://localhost:8000/api/board/{id}/info';
        this.GET_CARD_URL = 'http://localhost:8000/api/board/{board_id}/card/{card_id}/info';
    }
    BoardService.prototype.getBoards = function () {
        var get_boards_url = this.GET_BOARDS_URL;
        return this.http.get(get_boards_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    BoardService.prototype.getBoard = function (board_id) {
        var get_board_url = this.GET_BOARD_URL.replace(/\{id\}/, board_id.toString());
        return this.http.get(get_board_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    BoardService.prototype.getCard = function (board_id, card_id) {
        var get_card_url = this.GET_CARD_URL.replace(/\{board_id\}/, board_id.toString()).replace(/\{card_id\}/, card_id.toString());
        return this.http.get(get_card_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    BoardService = __decorate([
        core_1.Injectable(), 
        __metadata('design:paramtypes', [http_1.Http])
    ], BoardService);
    return BoardService;
}(djangotrellostats_service_1.DjangoTrelloStatsService));
exports.BoardService = BoardService;
//# sourceMappingURL=board.service.js.map