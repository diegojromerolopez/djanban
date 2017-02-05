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
var card_1 = require("../../models/card");
var card_service_1 = require("../../services/card.service");
var CardComponent = (function () {
    function CardComponent(router, route, boardService, cardService) {
        this.router = router;
        this.route = route;
        this.boardService = boardService;
        this.cardService = cardService;
        this.commentPreviousContent = {};
        this.card_hash = {};
        this.changeNameStatus = "hidden";
        this.changeListStatus = "hidden";
        this.statusCardStatus = "standby";
        this.changeLabelsStatus = "hidden";
        this.changeMembersStatus = "hidden";
        this.changeDueDatetimeStatus = "hidden";
        this.removeDueDatetimeStatus = "standby";
        this.changeSETimeStatus = "standby";
        this.changeDescriptionStatus = "hidden";
        this.newCommentStatus = "standby";
        this.addBlockingCardStatus = "hidden";
        this.newReviewStatus = "hidden";
        this.editCommentStatus = {};
        this.commentPreviousContent = {};
        this.deleteCommentStatus = {};
        this.removeBlockingCardStatus = {};
        this.deleteReviewStatus = {};
        this.addRequirementStatus = "hidden";
        this.removeRequirementStatus = {};
    }
    CardComponent.prototype.ngOnInit = function () {
        this.now = Date();
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            var card_id = params["card_id"];
            that.loadBoard(board_id);
            that.loadCard(board_id, card_id);
        });
    };
    CardComponent.prototype.cardHasLabel = function (label) {
        return this.card.labels.find(function (label_i) { return label_i.id == label.id; }) != undefined;
    };
    CardComponent.prototype.cardHasMember = function (member) {
        return this.card.members.find(function (member_id) { return member_id.id == member.id; }) != undefined;
    };
    /** Mark card as active */
    CardComponent.prototype.activeCard = function () {
        var _this = this;
        this.cardService.activeCard(this.card).then(function (updated_card) {
            _this.card.is_closed = false;
            _this.statusCardStatus = "standby";
        });
    };
    /** Mark card as closed (disabled) */
    CardComponent.prototype.closeCard = function () {
        var _this = this;
        this.cardService.closeCard(this.card).then(function (updated_card) {
            _this.card.is_closed = true;
            _this.statusCardStatus = "standby";
        });
    };
    /** Called when the change labels form is submitted */
    CardComponent.prototype.onChangeLabels = function (label_ids) {
        var _this = this;
        this.cardService.changeCardLabels(this.card, label_ids).then(function (updated_card) {
            _this.card = updated_card;
            _this.changeLabelsStatus = "hidden";
        });
    };
    /** Called when the change members form is submitted */
    CardComponent.prototype.onChangeMembers = function (member_ids) {
        var _this = this;
        this.cardService.changeCardMembers(this.card, member_ids).then(function (updated_card) {
            _this.card = updated_card;
            _this.changeMembersStatus = "hidden";
        });
    };
    /** Called when we remove a blocking card */
    CardComponent.prototype.onRemoveBlockingCard = function (blockingCard) {
        var _this = this;
        this.cardService.removeBlockingCard(this.card, blockingCard).then(function (card_response) {
            _this.card.blocking_cards = card_response.blocking_cards;
            delete _this.removeBlockingCardStatus[blockingCard.id];
            // We have to remove the associated comment
            // Remember that comments with the format "blocked by <card_url_in_trello>" means card-blocking
            _this.card.comments = card_response.comments;
        });
    };
    CardComponent.prototype.removeDueDatetime = function () {
        var _this = this;
        this.cardService.removeCardDueDatetime(this.card).then(function (card_response) {
            _this.card.due_datetime = null;
            _this.removeDueDatetimeStatus = "standby";
        });
    };
    /** Set due datetime */
    CardComponent.prototype.onChangeDueDatetime = function (due_date, due_time) {
        var _this = this;
        var yymmdd = due_date.split("-");
        var hhmm = due_time.split(":");
        var local_due_datetime = new Date(parseInt(yymmdd[0]), parseInt(yymmdd[1]) - 1, parseInt(yymmdd[2]), parseInt(hhmm[0]), parseInt(hhmm[1]));
        this.cardService.changeCardDueDatetime(this.card, local_due_datetime).then(function (card_response) {
            _this.card.due_datetime = new Date(card_response.due_datetime);
            _this.changeDueDatetimeStatus = "hidden";
        });
    };
    CardComponent.prototype.addBlockingCardRightCandidate = function (blockingCardId) {
        var blocking_card_ids = {};
        for (var _i = 0, _a = this.card.blocking_cards; _i < _a.length; _i++) {
            var blocking_card = _a[_i];
            blocking_card_ids[blocking_card.id] = true;
        }
        return this.card.id != blockingCardId && !(blockingCardId in blocking_card_ids);
    };
    /** Called when we add a blocking card */
    CardComponent.prototype.onAddBlockingCard = function (blockingCardId) {
        var _this = this;
        var blockingCard = this.card_hash[blockingCardId];
        this.cardService.addBlockingCard(this.card, blockingCard).then(function (card_response) {
            _this.card.blocking_cards = card_response.blocking_cards;
            // We have to update the comments
            _this.card.comments = card_response.comments;
            _this.addBlockingCardStatus = "hidden";
        });
    };
    /** Called when adding a review. */
    CardComponent.prototype.onAddReview = function (member_ids, description) {
        var _this = this;
        this.cardService.addNewReview(this.card, member_ids, description).then(function (card_response) {
            _this.card.reviews = card_response.reviews;
            _this.card.comments = card_response.comments;
            _this.newReviewStatus = "hidden";
            var review_comment = _this.card.comments[0];
            _this.editCommentStatus[review_comment.id] == 'standby';
            _this.deleteCommentStatus[review_comment.id] = "standby";
        });
    };
    /** Called when deleting a review */
    CardComponent.prototype.deleteReview = function (review) {
        var _this = this;
        this.cardService.deleteReview(this.card, review).then(function (card_response) {
            _this.card.reviews = card_response.reviews;
            _this.card.comments = card_response.comments;
            _this.newReviewStatus = "hidden";
        });
    };
    /** Called when adding a requirement. */
    CardComponent.prototype.onAddRequirement = function (requirement_id) {
        var _this = this;
        var requirement = this.board.requirements.find(function (requirement_i) { return requirement_i.id == requirement_id; });
        this.cardService.addRequirement(this.card, requirement).then(function (card_response) {
            _this.card.requirements = card_response.requirements;
            _this.card.comments = card_response.comments;
            _this.addRequirementStatus = "hidden";
            for (var _i = 0, _a = _this.card.requirements; _i < _a.length; _i++) {
                var requirement_1 = _a[_i];
                _this.removeRequirementStatus[requirement_1.id] = "standby";
            }
        });
    };
    /** Remove a requirement of this card */
    CardComponent.prototype.removeRequirement = function (requirement) {
        var _this = this;
        this.cardService.removeRequirement(this.card, requirement).then(function (card_response) {
            // Note we have to update the requirements and the comments because a comment has also been deleted.
            // Remember that the information about a requirement is stored in card comments.
            _this.card.requirements = card_response.requirements;
            _this.card.comments = card_response.comments;
            delete _this.removeRequirementStatus[requirement.id];
        });
    };
    /** Called when the card name change form is submitted */
    CardComponent.prototype.onChangeName = function (name) {
        var _this = this;
        this.cardService.changeCardName(this.card, name).then(function (card_response) {
            _this.card.name = name;
            _this.changeNameStatus = "hidden";
        });
    };
    /** Called when the card description change form is submitted */
    CardComponent.prototype.onChangeDescription = function (description) {
        var _this = this;
        this.cardService.changeCardDescription(this.card, description).then(function (card_response) {
            _this.card.description = description;
            _this.changeDescriptionStatus = "hidden";
        });
    };
    /** Called when the card S/E form is submitted */
    CardComponent.prototype.onSubmitSETimeForm = function (time_values) {
        var _this = this;
        var date = time_values["date"];
        var spent_time = time_values["spent_time"];
        var estimated_time = time_values["estimated_time"];
        var description = time_values["description"];
        this.cardService.addSETime(this.card, date, spent_time, estimated_time, description).then(function (updated_card) {
            _this.card = updated_card;
            _this.changeSETimeStatus = "standby";
        });
    };
    /** Called when the change list  form is submitted */
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
                this.cardService.moveCard(this.card, list_i).then(function (updated_card) {
                    _this.card = updated_card;
                    _this.changeListStatus = "hidden";
                });
            }
        }
    };
    /** Called when creating new comment */
    CardComponent.prototype.onSubmitNewComment = function (comment_content) {
        var _this = this;
        this.cardService.addNewComment(this.card, comment_content).then(function (comment) {
            _this.card.comments = [comment].concat(_this.card.comments);
            _this.newCommentStatus = "standby";
            _this.editCommentStatus[comment.id] = "standby";
            _this.deleteCommentStatus[comment.id] = "standby";
        });
    };
    /** Called when editing a comment */
    CardComponent.prototype.onSubmitEditComment = function (comment, new_content) {
        var _this = this;
        this.cardService.editComment(this.card, comment, new_content).then(function (edited_comment) {
            comment.content = new_content;
            _this.editCommentStatus[comment.id] = "standby";
        });
    };
    /** Called when deleting a comment */
    CardComponent.prototype.onSubmitDeleteComment = function (comment) {
        var _this = this;
        this.cardService.deleteComment(this.card, comment).then(function (deleted_comment) {
            _this.card.comments.splice(_this.card.comments.indexOf(comment), 1);
            delete _this.deleteCommentStatus[comment.id];
            delete _this.editCommentStatus[comment.id];
            delete _this.commentPreviousContent[comment.id];
        });
    };
    /** Navigation on the top of the page */
    CardComponent.prototype.onReturnToBoardSelect = function () {
        this.router.navigate([this.board.id]);
    };
    // Basic loading methods
    /** Load card data and prepare its statuses */
    CardComponent.prototype.loadCard = function (board_id, card_id) {
        var _this = this;
        this.cardService.getCard(board_id, card_id).then(function (card) {
            _this.card = new card_1.Card(card);
            // Inicialization of the status of the edition or deletion or the comments of this card
            for (var _i = 0, _a = _this.card.comments; _i < _a.length; _i++) {
                var comment = _a[_i];
                _this.editCommentStatus[comment.id] = "standby";
                _this.deleteCommentStatus[comment.id] = "standby";
            }
            // Initialization of the status of the removal of each one of the blocking cards of this card
            for (var _b = 0, _c = _this.card.blocking_cards; _b < _c.length; _b++) {
                var blocking_card = _c[_b];
                _this.removeBlockingCardStatus[blocking_card.id] = "showed";
            }
            // Initialization of the status of the removal of each one of the reviews of this card
            for (var _d = 0, _e = _this.card.reviews; _d < _e.length; _d++) {
                var review = _e[_d];
                _this.deleteReviewStatus[review.id] = "showed";
            }
            // Initalization of requirements' status
            for (var _f = 0, _g = _this.card.requirements; _f < _g.length; _f++) {
                var requirement = _g[_f];
                _this.removeRequirementStatus[requirement.id] = "hidden";
            }
        });
    };
    CardComponent.prototype.loadBoard = function (board_id) {
        var _this = this;
        this.boardService.getBoard(board_id).then(function (board) {
            _this.board = board;
            _this.card_hash = {};
            _this.cards = [];
            for (var _i = 0, _a = _this.board.lists; _i < _a.length; _i++) {
                var list = _a[_i];
                for (var _b = 0, _c = list.cards; _b < _c.length; _b++) {
                    var card = _c[_b];
                    _this.cards.push(card);
                    _this.card_hash[card.id] = card;
                }
            }
        });
    };
    return CardComponent;
}());
CardComponent = __decorate([
    core_1.Component({
        moduleId: module.id,
        selector: 'card',
        templateUrl: 'card.component.html',
        styleUrls: ['card.component.css'],
        providers: [board_service_1.BoardService, card_service_1.CardService]
    }),
    __metadata("design:paramtypes", [router_1.Router,
        router_1.ActivatedRoute,
        board_service_1.BoardService,
        card_service_1.CardService])
], CardComponent);
exports.CardComponent = CardComponent;
//# sourceMappingURL=card.component.js.map