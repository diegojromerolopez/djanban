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
var core_1 = require('@angular/core');
var http_1 = require('@angular/http');
require('rxjs/add/operator/map');
require('rxjs/add/operator/catch');
require('rxjs/add/operator/toPromise');
//import { Observable }     from 'rxjs/Observable';
var BoardService = (function () {
    function BoardService(http) {
        this.http = http;
        this.GET_BOARD_URL = 'http://localhost:8000/boards/api/{id}/info';
        this.GET_BOARDS_URL = 'http://localhost:8000/boards/api/info';
    }
    BoardService.prototype.extractData = function (res) {
        var body = res.json();
        return body || {};
    };
    BoardService.prototype.handleError = function (error) {
        var errMsg;
        if (error instanceof http_1.Response) {
            var body = error.json() || '';
            var err = body.error || JSON.stringify(body);
            errMsg = error.status + " - " + (error.statusText || '') + " " + err;
        }
        else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.error(errMsg);
        return Promise.reject(errMsg);
    };
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
    BoardService = __decorate([
        core_1.Injectable(), 
        __metadata('design:paramtypes', [http_1.Http])
    ], BoardService);
    return BoardService;
}());
exports.BoardService = BoardService;
//# sourceMappingURL=board.service.js.map