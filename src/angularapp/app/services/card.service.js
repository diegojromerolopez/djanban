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
        _this.ADD_SE_URL = "/api/board/{board_id}/card/{card_id}/time";
        _this.ADD_COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment";
        _this.COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment/{comment_id}";
        _this.MOVE_CARD_URL = "/api/board/{board_id}/card/{card_id}/list";
        _this.CHANGE_LABELS_URL = "/api/board/{board_id}/card/{card_id}/labels";
        _this.CHANGE_MEMBERS_URL = "/api/board/{board_id}/card/{card_id}/members";
        _this.CHANGE_CARD_URL = "/api/board/{board_id}/card/{card_id}";
        return _this;
    }
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
    CardService.prototype.addNewComment = function (card, comment_content) {
        var add_new_comment_url = this.prepareUrl(this.ADD_COMMENT_URL, card);
        return this.http.put(add_new_comment_url, { content: comment_content })
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
    CardService.prototype.deleteComment = function (card, comment) {
        var comment_id = comment.id.toString();
        var comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment_id);
        return this.http.delete(comment_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.moveCard = function (card, new_list, position) {
        if (position === void 0) { position = "top"; }
        console.log(card, new_list, position);
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