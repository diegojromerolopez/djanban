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
//import { Observable }     from 'rxjs/Observable';
var CardService = (function (_super) {
    __extends(CardService, _super);
    function CardService(http) {
        _super.call(this, http);
        this.ADD_COMMENT_URL = "http://localhost:8000/api/board/{board_id}/card/{card_id}/comment";
        this.COMMENT_URL = "http://localhost:8000/api/board/{board_id}/card/{card_id}/comment/{comment_id}";
    }
    CardService.prototype.addNewComment = function (card, comment_content) {
        var board_id = card.board.id.toString();
        var card_id = card.id.toString();
        var add_new_comment_url = this.ADD_COMMENT_URL.replace("{board_id}", board_id).replace("{card_id}", card_id);
        return this.http.put(add_new_comment_url, { content: comment_content })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.editComment = function (card, comment, new_content) {
        var board_id = card.board.id.toString();
        var card_id = card.id.toString();
        var comment_id = comment.id.toString();
        var comment_url = this.COMMENT_URL.replace("{board_id}", board_id).replace("{card_id}", card_id).replace("{comment_id}", comment_id);
        return this.http.post(comment_url, { content: new_content })
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService.prototype.deleteComment = function (card, comment) {
        var board_id = card.board.id.toString();
        var card_id = card.id.toString();
        var comment_id = comment.id.toString();
        var comment_url = this.COMMENT_URL.replace("{board_id}", board_id).replace("{card_id}", card_id).replace("{comment_id}", comment_id);
        return this.http.delete(comment_url)
            .toPromise()
            .then(this.extractData)
            .catch(this.handleError);
    };
    CardService = __decorate([
        core_1.Injectable(), 
        __metadata('design:paramtypes', [http_1.Http])
    ], CardService);
    return CardService;
}(djangotrellostats_service_1.DjangoTrelloStatsService));
exports.CardService = CardService;
//# sourceMappingURL=card.service.js.map