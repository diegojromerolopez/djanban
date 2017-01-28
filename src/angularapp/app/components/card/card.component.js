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
var router_1 = require('@angular/router');
var board_service_1 = require('../../services/board.service');
var card_service_1 = require('../../services/card.service');
var CardComponent = (function () {
    function CardComponent(route, boardService, cardService) {
        this.route = route;
        this.boardService = boardService;
        this.cardService = cardService;
    }
    /*private spentEstimatedForm = this.formBuilder.group({
        "date": ["", Validators.required],
        "spent_time": ["", Validators.required],
        "estimated_time": ["", Validators.required]
    });*/
    CardComponent.prototype.ngOnInit = function () {
        var _this = this;
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            var card_id = params["card_id"];
            _this.board_id = board_id;
            that.loadCard(board_id, card_id);
        });
    };
    CardComponent.prototype.cardHasLabel = function (label) {
        return this.card.labels.find(function (label_i) { return label_i.id == label.id; }) != undefined;
    };
    CardComponent.prototype.showCommentEdition = function (comment) {
        this.editing_comment = comment;
        //this.EditCommentForm.value.content = comment.content;
    };
    CardComponent.prototype.hideCommentEdition = function (comment) {
        this.editing_comment = null;
    };
    CardComponent.prototype.onSubmitSETimeForm = function (time_values) {
        var _this = this;
        var date = time_values["date"];
        var spent_time = time_values["spent_time"];
        var estimated_time = time_values["estimated_time"];
        var description = time_values["description"];
        this.cardService.addSETime(this.card, date, spent_time, estimated_time, description).then(function (updated_card) { return _this.card = updated_card; });
    };
    CardComponent.prototype.onSubmitChangeList = function (destination_list_id) {
        var _this = this;
        // If the destination list is the same as the current list of the card, do nothing
        if (this.card.list.id == destination_list_id) {
            return;
        }
        // Otherwise, get the list with that index and change the list
        for (var list_index in this.card.board.lists) {
            var list_i = this.card.board.lists[list_index];
            if (list_i.id == destination_list_id) {
                this.cardService.changeList(this.card, list_i).then(function (updated_card) { return _this.card = updated_card; });
            }
        }
    };
    CardComponent.prototype.onSubmitNewComment = function (comment_content) {
        var _this = this;
        this.cardService.addNewComment(this.card, comment_content).then(function (comment) { return _this.card.comments.push(comment); });
    };
    CardComponent.prototype.onSubmitEditComment = function (comment, new_content) {
        var _this = this;
        this.cardService.editComment(this.card, comment, new_content).then(function (edited_comment) {
            comment.content = new_content;
            _this.editing_comment = null;
        });
    };
    CardComponent.prototype.onSubmitDeleteComment = function (comment) {
        var _this = this;
        this.cardService.deleteComment(this.card, comment).then(function (deleted_comment) {
            _this.card.comments.splice(_this.card.comments.indexOf(comment), 1);
        });
    };
    CardComponent.prototype.onChangeCardLabels = function (label_ids) {
        var _this = this;
        this.cardService.changeCardLabels(this.card, label_ids).then(function (updated_card) { return _this.card = updated_card; });
    };
    CardComponent.prototype.loadCard = function (board_id, card_id) {
        var _this = this;
        this.boardService.getCard(board_id, card_id).then(function (card) { return _this.card = card; });
    };
    CardComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'card',
            templateUrl: 'card.component.html',
            styleUrls: ['card.component.css'],
            providers: [board_service_1.BoardService, card_service_1.CardService]
        }), 
        __metadata('design:paramtypes', [router_1.ActivatedRoute, board_service_1.BoardService, card_service_1.CardService])
    ], CardComponent);
    return CardComponent;
}());
exports.CardComponent = CardComponent;
//# sourceMappingURL=card.component.js.map