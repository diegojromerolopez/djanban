"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
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
var http_1 = require("@angular/http");
var djanban_service_1 = require("./djanban.service");
require("rxjs/add/operator/map");
require("rxjs/add/operator/catch");
require("rxjs/add/operator/toPromise");
var BoardService = (function (_super) {
    __extends(BoardService, _super);
    function BoardService(http) {
        var _this = _super.call(this, http) || this;
        _this.GET_BOARDS_URL = '/api/boards/info';
        _this.GET_BOARD_URL = '/api/board/{id}/info';
        _this.MOVE_LIST_URL = '/api/board/{id}/list/{list_id}';
        _this.DELETE_MEMBER_URL = '/api/board/{id}/member/{member_id}';
        _this.ADD_MEMBER_URL = '/api/board/{id}/member';
        return _this;
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
    BoardService.prototype.moveList = function (board, list, position) {
        if (position === void 0) { position = "bottom"; }
        var move_list_url = this.MOVE_LIST_URL.replace("{id}", board.id.toString()).replace("{list_id}", list.id.toString());
        var post_body = { position: position };
        return this.http.post(move_list_url, post_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    BoardService.prototype.removeMember = function (board, member) {
        var delete_member_url = this.DELETE_MEMBER_URL.replace("{id}", board.id.toString()).replace("{member_id}", member.id.toString());
        return this.http.delete(delete_member_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    BoardService.prototype.addMember = function (board, member, member_type) {
        var add_member_url = this.ADD_MEMBER_URL.replace("{id}", board.id.toString());
        var put_body = { member: member.id, member_type: member_type };
        console.log(put_body);
        return this.http.put(add_member_url, put_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    return BoardService;
}(djanban_service_1.DjanbanService));
BoardService = __decorate([
    core_1.Injectable(),
    __metadata("design:paramtypes", [http_1.Http])
], BoardService);
exports.BoardService = BoardService;
//# sourceMappingURL=board.service.js.map