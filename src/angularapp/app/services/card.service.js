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
        _this.MOVE_ALL_LIST_CARDS_URL = "/api/board/{board_id}/card";
        _this.CHANGE_LABELS_URL = "/api/board/{board_id}/card/{card_id}/labels";
        _this.CHANGE_MEMBERS_URL = "/api/board/{board_id}/card/{card_id}/members";
        _this.CHANGE_CARD_URL = "/api/board/{board_id}/card/{card_id}";
        _this.GET_CARD_URL = '/api/board/{board_id}/card/{card_id}/info';
        _this.BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card';
        _this.REMOVE_BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card/{blocking_card_id}';
        _this.ADD_REVIEW_URL = '/api/board/{board_id}/card/{card_id}/review';
        _this.DELETE_REVIEW_URL = '/api/board/{board_id}/card/{card_id}/review/{review_id}';
        _this.ADD_REQUIREMENT_URL = '/api/board/{board_id}/card/{card_id}/requirement';
        _this.REMOVE_REQUIREMENT_URL = '/api/board/{board_id}/card/{card_id}/requirement/{requirement_id}';
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
        var change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(change_card_url, { name: new_name })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Change the description of the card */
    CardService.prototype.changeCardDescription = function (card, new_description) {
        var change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(change_card_url, { description: new_description })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Change the due datetime (deadline) */
    CardService.prototype.changeCardDueDatetime = function (card, due_datetime) {
        console.log("CardService.changeCardDueDatetime");
        console.log(due_datetime);
        var change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(change_card_url, { due_datetime: due_datetime })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.removeCardDueDatetime = function (card) {
        var change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(change_card_url, { due_datetime: null })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Change the status of the card to "active" (open or visible) */
    CardService.prototype.activeCard = function (card) {
        var is_closed = false;
        return this.changeCardClausure(card, is_closed);
    };
    /** Change the status of the card to "closed" (archived) */
    CardService.prototype.closeCard = function (card) {
        var is_closed = true;
        return this.changeCardClausure(card, is_closed);
    };
    /** Change the status of the card */
    CardService.prototype.changeCardClausure = function (card, is_closed) {
        var change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
        return this.http.put(change_card_url, { is_closed: is_closed })
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
    CardService.prototype.changeCardMembers = function (card, new_member_ids) {
        var chage_members_url = this.prepareUrl(this.CHANGE_MEMBERS_URL, card);
        return this.http.post(chage_members_url, { members: new_member_ids })
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
    /** Create a new card review */
    CardService.prototype.addNewReview = function (card, new_member_ids, description) {
        var add_new_review_url = this.prepareUrl(this.ADD_REVIEW_URL, card);
        var put_body = { members: new_member_ids, description: description };
        return this.http.put(add_new_review_url, put_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Delete a card review */
    CardService.prototype.deleteReview = function (card, review) {
        var delete_review_url = this.prepareUrl(this.DELETE_REVIEW_URL, card).replace("{review_id}", review.id.toString());
        return this.http.delete(delete_review_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Add a new requirement to a card */
    CardService.prototype.addRequirement = function (card, requirement) {
        var add_requirement_url = this.prepareUrl(this.ADD_REQUIREMENT_URL, card);
        var put_body = { requirement: requirement.id };
        return this.http.put(add_requirement_url, put_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Remove a requirement from a card */
    CardService.prototype.removeRequirement = function (card, requirement) {
        var remove_requirement_url = this.prepareUrl(this.REMOVE_REQUIREMENT_URL, card).replace("{requirement_id}", requirement.id.toString());
        return this.http.delete(remove_requirement_url)
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
    /** Move a card to another list */
    CardService.prototype.moveCard = function (card, new_list, position) {
        if (position === void 0) { position = "top"; }
        var move_list_url = this.prepareUrl(this.MOVE_CARD_URL, card);
        var post_body = { position: position };
        if (new_list) {
            post_body["new_list"] = new_list.id;
        }
        return this.http.post(move_list_url, post_body)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    /** Move all list from a card to another card */
    CardService.prototype.moveAllListCards = function (board, source_list, destination_list) {
        var move_all_list_cards_url = this.MOVE_ALL_LIST_CARDS_URL.replace("{board_id}", board.id.toString());
        return this.http.post(move_all_list_cards_url, { source_list: source_list.id, destination_list: destination_list.id })
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