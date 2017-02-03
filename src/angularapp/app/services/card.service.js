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
var core_1 = require("@angular/core");
var http_1 = require("@angular/http");
var djangotrellostats_service_1 = require("./djangotrellostats.service");
require("rxjs/add/operator/map");
require("rxjs/add/operator/catch");
require("rxjs/add/operator/toPromise");
//import { Observable }     from 'rxjs/Observable';
var CardService = (function (_super) {
    __extends(CardService, _super);
    function CardService(http) {
        var _this = _super.call(this, http) || this;
        _this.ADD_CARD_URL = '/api/board/{board_id}/card';
        _this.ADD_SE_URL = "/api/board/{board_id}/card/{card_id}/time";
        _this.ADD_COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment";
        _this.COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment/{comment_id}";
        _this.MOVE_CARD_URL = "/api/board/{board_id}/card/{card_id}/list";
        _this.CHANGE_LABELS_URL = "/api/board/{board_id}/card/{card_id}/labels";
        _this.CHANGE_MEMBERS_URL = "/api/board/{board_id}/card/{card_id}/members";
        _this.CHANGE_CARD_URL = "/api/board/{board_id}/card/{card_id}";
        _this.GET_CARD_URL = '/api/board/{board_id}/card/{card_id}/info';
        _this.BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card';
        _this.REMOVE_BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card/{blocking_card_id}';
        return _this;
    }
    /**
    * Adds a new card to a list of the board.
    */
    CardService.prototype.addCard = function (board, list, name, position) {
        if (position === void 0) { position = "top"; }
        var add_card_url = this.ADD_CARD_URL.replace(/\{board_id\}/, board.id.toString());
        var put_body = {
            name: name,
            list: list.id,
            position: position
        };
        return this.http.put(add_card_url, put_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.addSETime = function (card, date, spent_time, estimated_time, description) {
        var add_se_url = this.prepareUrl(this.ADD_SE_URL, card);
        var post_body = { date: date, spent_time: spent_time, estimated_time: estimated_time, description: description };
        return this.http.post(add_se_url, post_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.changeCardName = function (card, new_name) {
        var chage_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(chage_card_url, { name: new_name })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.changeCardDescription = function (card, new_description) {
        var chage_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(chage_card_url, { description: new_description })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.changeCardLabels = function (card, new_label_ids) {
        var chage_labels_url = this.prepareUrl(this.CHANGE_LABELS_URL, card);
        return this.http.post(chage_labels_url, { labels: new_label_ids })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.changeCardMembers = function (card, new_members_ids) {
        var chage_members_url = this.prepareUrl(this.CHANGE_MEMBERS_URL, card);
        return this.http.post(chage_members_url, { members: new_members_ids })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.addBlockingCard = function (card, blocking_card) {
        var add_blocking_card_url = this.prepareUrl(this.BLOCKING_CARD_URL, card);
        var put_body = { blocking_card: blocking_card.id };
        console.log(card, blocking_card);
        console.log(put_body);
        return this.http.put(add_blocking_card_url, put_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.removeBlockingCard = function (card, blocking_card) {
        var remove_blocking_card_url = this.prepareUrl(this.REMOVE_BLOCKING_CARD_URL, card).replace("{blocking_card_id}", blocking_card.id.toString());
        return this.http.delete(remove_blocking_card_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.addNewComment = function (card, comment_content) {
        var add_new_comment_url = this.prepareUrl(this.ADD_COMMENT_URL, card);
        return this.http.put(add_new_comment_url, { content: comment_content })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.deleteComment = function (card, comment) {
        var comment_id = comment.id.toString();
        var comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment_id);
        return this.http.delete(comment_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.editComment = function (card, comment, new_content) {
        var comment_id = comment.id.toString();
        var comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment_id);
        return this.http.post(comment_url, { content: new_content })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.getCard = function (board_id, card_id) {
        var get_card_url = this.GET_CARD_URL.replace(/\{board_id\}/, board_id.toString()).replace(/\{card_id\}/, card_id.toString());
        return this.http.get(get_card_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.moveCard = function (card, new_list, position) {
        if (position === void 0) { position = "top"; }
        var move_list_url = this.prepareUrl(this.MOVE_CARD_URL, card);
        return this.http.post(move_list_url, { new_list: new_list.id, position: position })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.prepareUrl = function (url, card) {
        var board_id = card.board.id.toString();
        var card_id = card.id.toString();
        return url.replace(/\{board_id\}/, board_id).replace(/\{card_id\}/, card_id);
    };
    return CardService;
}(djangotrellostats_service_1.DjangoTrelloStatsService));
CardService = __decorate([
    core_1.Injectable(),
    __metadata("design:paramtypes", [http_1.Http])
], CardService);
exports.CardService = CardService;
//# sourceMappingURL=card.service.js.map