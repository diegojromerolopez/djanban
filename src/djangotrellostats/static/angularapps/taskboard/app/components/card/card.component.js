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
var angular2_notifications_1 = require("angular2-notifications");
var ng2_file_upload_1 = require("ng2-file-upload");
var CardComponent = (function () {
    function CardComponent(router, route, boardService, cardService, notificationsService) {
        this.router = router;
        this.route = route;
        this.boardService = boardService;
        this.cardService = cardService;
        this.notificationsService = notificationsService;
        // NotificationsService options
        this.notificationsOptions = {
            position: ["top", "right"],
            timeOut: 10000,
            pauseOnHover: true,
        };
        // File uploader
        this.ATTACHMENT_UPLOAD_URL = '/api/board/{board_id}/card/{card_id}/attachment/add';
        this.hasBaseDropZoneOver = false;
        this.hasAnotherDropZoneOver = false;
        this.lockFileUploader = false;
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
        this.deleteAttachmentStatus = {};
        this.lockFileUploader = false;
        this.hasBaseDropZoneOver = false;
        this.hasAnotherDropZoneOver = false;
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
            _this.notificationsService.success("Card activated", _this.card.name + " is now active.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't activate " + _this.card.name + ". " + error_message);
            _this.statusCardStatus = "standby";
        });
    };
    /** Mark card as closed (disabled) */
    CardComponent.prototype.closeCard = function () {
        var _this = this;
        this.cardService.closeCard(this.card).then(function (updated_card) {
            _this.card.is_closed = true;
            _this.statusCardStatus = "standby";
            _this.notificationsService.success("Card archived", _this.card.name + " is now archived. Remember if will not show up on the board.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't archive " + _this.card.name + ". " + error_message);
            _this.statusCardStatus = "standby";
        });
    };
    /** Called when the change labels form is submitted */
    CardComponent.prototype.onChangeLabels = function (label_ids) {
        var _this = this;
        this.cardService.changeCardLabels(this.card, label_ids).then(function (updated_card) {
            _this.card = updated_card;
            _this.changeLabelsStatus = "hidden";
            _this.notificationsService.success("Labels changed", _this.card.name + " has now " + _this.card.labels.length + " labels.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't change labels on " + _this.card.name + ". " + error_message);
            _this.changeLabelsStatus = "standby";
        });
    };
    /** Called when the change members form is submitted */
    CardComponent.prototype.onChangeMembers = function (member_ids) {
        var _this = this;
        this.cardService.changeCardMembers(this.card, member_ids).then(function (updated_card) {
            _this.card = updated_card;
            _this.changeMembersStatus = "hidden";
            _this.notificationsService.success("Members changed", _this.card.name + " has now " + _this.card.members.length + " members.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't change members of " + _this.card.name + ". " + error_message);
            _this.changeMembersStatus = "showed";
        });
    };
    CardComponent.prototype.removeDueDatetime = function () {
        var _this = this;
        this.cardService.removeCardDueDatetime(this.card).then(function (card_response) {
            _this.card.due_datetime = null;
            _this.removeDueDatetimeStatus = "standby";
            _this.notificationsService.success("Deadline removed", _this.card.name + " has no deadline.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't remove the deadline of " + _this.card.name + ". " + error_message);
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
            _this.notificationsService.success("Deadline added", _this.card.name + " has a new deadline.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't set the deadline for " + _this.card.name + ". " + error_message);
            _this.changeDueDatetimeStatus = "showed";
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
            _this.notificationsService.success("Blocking card removed", _this.card.name + " is now blocked by " + blockingCard.name + " (leaving " + _this.card.blocking_cards.length + " blocking cards in total).");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't add blocking card to " + _this.card.name + ". " + error_message);
            _this.addBlockingCardStatus = "showed";
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
            _this.notificationsService.success("Blocking card removed", _this.card.name + " is not blocked by " + blockingCard.name + " (leaving " + _this.card.blocking_cards.length + " blocking cards in total).");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't remove " + blockingCard.name + " blocking card of " + _this.card.name + ". " + error_message);
            _this.removeBlockingCardStatus[blockingCard.id] = "showed";
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
            _this.notificationsService.success("Blocking card added", _this.card.name + " has a new review (" + _this.card.blocking_cards.length + " in total).");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't add review to " + _this.card.name + ". " + error_message);
            _this.newReviewStatus = "showed";
        });
    };
    /** Called when deleting a review */
    CardComponent.prototype.deleteReview = function (review) {
        var _this = this;
        this.cardService.deleteReview(this.card, review).then(function (card_response) {
            _this.card.reviews = card_response.reviews;
            _this.card.comments = card_response.comments;
            delete _this.deleteReviewStatus[review.id];
            _this.notificationsService.success("Review deleted", "A review of " + _this.card.name + " was deleted. This card has now " + _this.card.reviews.length + " reviews.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't delete review of " + _this.card.name + ". " + error_message);
            _this.deleteReviewStatus[review.id] = "showed";
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
                _this.notificationsService.success("Requirement added", "This card depends on the requirement " + requirement_1.name + ".");
            }
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't add requirement to " + _this.card.name + ". " + error_message);
            _this.addRequirementStatus = "showed";
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
            _this.notificationsService.success("Requirement removed", "This card already does not depend on the requirement " + requirement.name + ".");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't remove requirement from " + _this.card.name + ". " + error_message);
            _this.removeRequirementStatus[requirement.id] = "standby";
        });
    };
    /** Called when the card name change form is submitted */
    CardComponent.prototype.onChangeName = function (name) {
        var _this = this;
        this.cardService.changeCardName(this.card, name).then(function (card_response) {
            _this.card.name = name;
            _this.changeNameStatus = "hidden";
            _this.notificationsService.success("Name changed", "This card now is know as " + name + ".");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't change the name of " + _this.card.name + ". " + error_message);
            _this.changeNameStatus = "showed";
        });
    };
    /** Called when the card description change form is submitted */
    CardComponent.prototype.onChangeDescription = function (description) {
        var _this = this;
        this.cardService.changeCardDescription(this.card, description).then(function (card_response) {
            _this.card.description = description;
            _this.changeDescriptionStatus = "hidden";
            _this.notificationsService.success("Description changed", "This card now has a new description.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't change the description of " + _this.card.name + ". " + error_message);
            _this.changeDescriptionStatus = "showed";
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
            _this.notificationsService.success("New S/E time added", "S: " + spent_time + " / E: " + estimated_time + ".");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't submit a spent/estimated time to " + _this.card.name + ". " + error_message);
            _this.changeSETimeStatus = "standby";
        });
    };
    /** Called when the card change value form is submitted */
    CardComponent.prototype.onSubmitValueForm = function (value) {
        var _this = this;
        this.cardService.changeCardValue(this.card, value).then(function (updated_card) {
            _this.card = updated_card;
            _this.changeValueStatus = "standby";
            if (updated_card.value == null) {
                _this.notificationsService.success("Value deleted", "Value of " + _this.card.name + " has been deleted");
            }
            else {
                _this.notificationsService.success("Value changed to", "" + value);
            }
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't change the value of " + _this.card.name + ". " + error_message);
            _this.changeValueStatus = "standby";
        });
    };
    /** Called when the change list  form is submitted */
    CardComponent.prototype.onSubmitChangeList = function (destination_list_id) {
        var _this = this;
        // If the destination list is the same as the current list of the card, do nothing
        if (this.card.list.id == destination_list_id) {
            this.notificationsService.error("Error", this.card.name + " is already in " + this.card.list.name);
        }
        var _loop_1 = function (list_index) {
            var list_i = this_1.card.board.lists[list_index];
            if (list_i.id == destination_list_id) {
                this_1.cardService.moveCard(this_1.card, list_i).then(function (board_response) {
                    _this.board = board_response;
                    _this.card.list = list_i;
                    _this.changeListStatus = "hidden";
                    _this.notificationsService.success("This card has been moved", _this.card.name + " is in " + _this.card.list.name + ".");
                });
            }
        };
        var this_1 = this;
        // Otherwise, get the list with that index and change the list
        for (var list_index in this.card.board.lists) {
            _loop_1(list_index);
        }
    };
    CardComponent.prototype.fileOverFileUploaderDropZone = function (e) {
        var _this = this;
        this.hasBaseDropZoneOver = e;
        var _loop_2 = function (queuedFile) {
            if (!queuedFile.isReady && !queuedFile.isUploading && !queuedFile.isSuccess) {
                queuedFile.onComplete = function (response, status, headers) {
                    var attachment = JSON.parse(response);
                    _this.card.attachments = [attachment].concat(_this.card.attachments);
                    _this.deleteAttachmentStatus[attachment.id] = "standby";
                    queuedFile.remove();
                    _this.lockFileUploader = false;
                    _this.notificationsService.success("Attachment added", _this.card.name + " has a new attachment (" + _this.card.number_of_attachments + " in total).");
                };
                queuedFile.onError = function (response, status, headers) {
                    _this.lockFileUploader = false;
                    _this.notificationsService.error("Error", "Couldn't add attachment to " + _this.card.name);
                };
                this_2.fileUploader.options.url = this_2.ATTACHMENT_UPLOAD_URL + "?uploaded_file_name=" + queuedFile.file.name;
                queuedFile.url = this_2.ATTACHMENT_UPLOAD_URL + "?uploaded_file_name=" + queuedFile.file.name;
                this_2.lockFileUploader = true;
                queuedFile.upload();
            }
        };
        var this_2 = this;
        for (var _i = 0, _a = this.fileUploader.queue; _i < _a.length; _i++) {
            var queuedFile = _a[_i];
            _loop_2(queuedFile);
        }
    };
    CardComponent.prototype.deleteAttachment = function (attachment) {
        var _this = this;
        this.deleteAttachmentStatus[attachment.id] = "waiting";
        this.cardService.deleteAttachment(this.card, attachment).then(function (deleted_attachment) {
            _this.card.attachments.splice(_this.card.attachments.indexOf(attachment), 1);
            delete _this.deleteAttachmentStatus[attachment.id];
            _this.notificationsService.success("Attachment deleted", _this.card.name + " has had one of its attachments deleted (" + _this.card.number_of_attachments + " in total).");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't delete attachment of " + _this.card.name + ". " + error_message);
            _this.deleteAttachmentStatus[attachment.id] = "standby";
        });
    };
    /** Called when creating new comment */
    CardComponent.prototype.onSubmitNewComment = function (comment_content) {
        var _this = this;
        this.cardService.addNewComment(this.card, comment_content).then(function (comment) {
            _this.card.comments = [comment].concat(_this.card.comments);
            _this.newCommentStatus = "standby";
            _this.editCommentStatus[comment.id] = "standby";
            _this.deleteCommentStatus[comment.id] = "standby";
            _this.notificationsService.success("New comment added", _this.card.name + " has a new comment (" + _this.card.comments.length + " in total).");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't add a new comment to " + _this.card.name + ". " + error_message);
            _this.newCommentStatus = "standby";
        });
    };
    /** Called when editing a comment */
    CardComponent.prototype.onSubmitEditComment = function (comment, new_content) {
        var _this = this;
        this.cardService.editComment(this.card, comment, new_content).then(function (edited_comment) {
            comment.content = new_content;
            _this.editCommentStatus[comment.id] = "standby";
            _this.notificationsService.success("Comment edited", "A comment of " + _this.card.name + " was edited.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't edit a comment from " + _this.card.name + ". " + error_message);
            _this.editCommentStatus[comment.id] = "showed";
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
            _this.notificationsService.success("Comment deleted", "A comment of " + _this.card.name + " was deleted.");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't delete a comment from " + _this.card.name + ". " + error_message);
            _this.deleteCommentStatus[comment.id] = "showed";
        });
        ;
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
            // Initialization of file uploader
            _this.ATTACHMENT_UPLOAD_URL = _this.ATTACHMENT_UPLOAD_URL.replace("{board_id}", board_id.toString()).replace("{card_id}", card_id.toString());
            _this.fileUploader = new ng2_file_upload_1.FileUploader({ url: _this.ATTACHMENT_UPLOAD_URL, disableMultipart: true });
            // Show that card is loaded all right
            _this.notificationsService.success("Successful load", card.name + " loaded successfully");
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't load this card. " + error_message);
        });
        ;
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
        }).catch(function (error_message) {
            _this.notificationsService.error("Error", "Couldn't load this card's board data. " + error_message);
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
        providers: [board_service_1.BoardService, card_service_1.CardService, angular2_notifications_1.NotificationsService]
    }),
    __metadata("design:paramtypes", [router_1.Router,
        router_1.ActivatedRoute,
        board_service_1.BoardService,
        card_service_1.CardService,
        angular2_notifications_1.NotificationsService])
], CardComponent);
exports.CardComponent = CardComponent;
//# sourceMappingURL=card.component.js.map