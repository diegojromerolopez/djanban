import { composeValidators } from '@angular/forms/src/directives/shared';
import { Validator } from '@angular/forms';
import { Component, OnInit, DebugElement } from '@angular/core';
import { FormGroup, FormBuilder ,Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { BoardService } from '../../services/board.service';
import { Card } from '../../models/card';
import { Board } from '../../models/board';
import { List } from '../../models/list';
import { CardService } from '../../services/card.service';
import { CardComment } from '../../models/comment';
import { Label } from '../../models/label';
import { Member } from '../../models/member';
import { CardReview } from '../../models/review';
import { Requirement } from '../../models/requirement';
import { NotificationsService } from 'angular2-notifications';


@Component({
    moduleId: module.id,
    selector: 'card',
    templateUrl: 'card.component.html',
    styleUrls: ['card.component.css'],
    providers: [BoardService, CardService, NotificationsService]
})


/** Card component: contains all the actions doable on a card */
export class CardComponent implements OnInit  {

    private board: Board;
    private card: Card;
    private cards: Card[];
    private card_hash: {};
    
    private locale_due_datetime_string: string;

    private now: any;

    private changeNameStatus: string;
    private changeListStatus: string;

    // NotificationsService options
    public notificationsOptions = {
      position: ["top", "right"],
      timeOut: 10000,
      pauseOnHover: true,
    };

    // Status of the lateral menu
    /** Change of status of the card (active/closed) */
    private statusCardStatus: string;
    private changeLabelsStatus: string;
    private changeMembersStatus: string;
    
    // Status of the due datetime
    private removeDueDatetimeStatus: string;
    private changeDueDatetimeStatus: string;
    
    private changeSETimeStatus: string;
    private changeDescriptionStatus: string;
    private newCommentStatus: string;
    
    // Blocking card statuses
    private addBlockingCardStatus: string;
    private removeBlockingCardStatus: {};

    // Review statuses
    private newReviewStatus: string;
    private deleteReviewStatus: {};

    // Requirement statuses
    private addRequirementStatus: string;
    private removeRequirementStatus: {};

    /**
     * Stores the status of the edition of each comment: standby (standby),
     * asking confirmation (asking) and waiting server response (waiting)
     * */
    private editCommentStatus: {};

    private commentPreviousContent = {};
    
    /**
     * Stores the status of the deletion of each comment: standby (standby),
     * asking confirmation (asking) and waiting server response (waiting)
     * */
    private deleteCommentStatus: {};


    ngOnInit(): void {
        this.now = Date();
        let that = this;
        this.route.params.subscribe(params => {
            let board_id = params["board_id"];
            let card_id = params["card_id"];
            that.loadBoard(board_id);
            that.loadCard(board_id, card_id);
        });
    }

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private boardService: BoardService,
        private cardService: CardService,
        private notificationsService: NotificationsService
    ) {
        this.card_hash = {};
        this.changeNameStatus = "hidden";
        this.changeListStatus = "hidden";
        this.statusCardStatus = "standby";
        this.changeLabelsStatus = "hidden";
        this.changeMembersStatus = "hidden";
        this.changeDueDatetimeStatus = "hidden";
        this.removeDueDatetimeStatus = "standby"
        this.changeSETimeStatus = "standby";
        this.changeDescriptionStatus = "hidden";
        this.newCommentStatus = "standby";
        this.addBlockingCardStatus = "hidden";
        this.newReviewStatus = "hidden";
        this.editCommentStatus = { };
        this.commentPreviousContent = { }
        this.deleteCommentStatus = { };
        this.removeBlockingCardStatus = { };
        this.deleteReviewStatus = { };
        this.addRequirementStatus = "hidden";
        this.removeRequirementStatus = { };
    }

    cardHasLabel(label: Label): boolean {
        return this.card.labels.find(function(label_i){ return label_i.id == label.id }) != undefined;
    }

    cardHasMember(member: Member): boolean {
        return this.card.members.find(function(member_id){ return member_id.id == member.id }) != undefined;
    }

    /** Mark card as active */
    activeCard(): void{
        this.cardService.activeCard(this.card).then(updated_card => {
                this.card.is_closed = false;
                this.statusCardStatus = "standby";
                this.notificationsService.success("Card activated", `${this.card.name} is now active.`);
            }).catch(error_message => {
                this.notificationsService.error("Error", `Couldn't activate ${this.card.name}. ${error_message}`);
                this.statusCardStatus = "standby";
            });
    }

    /** Mark card as closed (disabled) */
    closeCard(): void{
        this.cardService.closeCard(this.card).then(updated_card => {
            this.card.is_closed = true;
            this.statusCardStatus = "standby";
            this.notificationsService.success("Card archived", `${this.card.name} is now archived. Remember if will not show up on the board.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't archive ${this.card.name}. ${error_message}`);
            this.statusCardStatus = "standby";
        });
    }

    /** Called when the change labels form is submitted */
    onChangeLabels(label_ids: number[]): void{
        this.cardService.changeCardLabels(this.card, label_ids).then(updated_card => {
            this.card = updated_card;
            this.changeLabelsStatus = "hidden";
            this.notificationsService.success("Labels changed", `${this.card.name} has now ${this.card.labels.length} labels.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't change labels on ${this.card.name}. ${error_message}`);
            this.changeLabelsStatus = "standby";
        });
    }

    /** Called when the change members form is submitted */
    onChangeMembers(member_ids: number[]): void{
        this.cardService.changeCardMembers(this.card, member_ids).then(updated_card => {
            this.card = updated_card;
            this.changeMembersStatus = "hidden";
            this.notificationsService.success("Members changed", `${this.card.name} has now ${this.card.members.length} members.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't change members of ${this.card.name}. ${error_message}`);
            this.changeMembersStatus = "showed";
        });
    }

    removeDueDatetime(){
        this.cardService.removeCardDueDatetime(this.card).then(card_response => {
            this.card.due_datetime = null;
            this.removeDueDatetimeStatus = "standby"; 
            this.notificationsService.success("Deadline removed", `${this.card.name} has no deadline.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't remove the deadline of ${this.card.name}. ${error_message}`);
            this.removeDueDatetimeStatus = "standby";
        });
    }

    /** Set due datetime */
    onChangeDueDatetime(due_date: string, due_time: string){
        let yymmdd = due_date.split("-");
        let hhmm = due_time.split(":");
        let local_due_datetime = new Date(parseInt(yymmdd[0]), parseInt(yymmdd[1])-1, parseInt(yymmdd[2]), parseInt(hhmm[0]), parseInt(hhmm[1]));
        this.cardService.changeCardDueDatetime(this.card, local_due_datetime).then(card_response => {
            this.card.due_datetime = new Date(card_response.due_datetime);
            this.changeDueDatetimeStatus = "hidden";
            this.notificationsService.success("Deadline added", `${this.card.name} has a new deadline.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't set the deadline for ${this.card.name}. ${error_message}`);
            this.changeDueDatetimeStatus = "showed";
        });
    }

    addBlockingCardRightCandidate(blockingCardId: number) {
        let blocking_card_ids = {};
        for(let blocking_card of this.card.blocking_cards){
            blocking_card_ids[blocking_card.id] = true;
        }
        return this.card.id != blockingCardId && !(blockingCardId in blocking_card_ids);
    }

    /** Called when we add a blocking card */
    onAddBlockingCard(blockingCardId: number){
        let blockingCard = this.card_hash[blockingCardId];
        this.cardService.addBlockingCard(this.card, blockingCard).then(card_response => {
            this.card.blocking_cards = card_response.blocking_cards;
            // We have to update the comments
            this.card.comments = card_response.comments;
            this.addBlockingCardStatus = "hidden";
            this.notificationsService.success("Blocking card removed", `${this.card.name} is now blocked by ${blockingCard.name} (leaving ${this.card.blocking_cards.length} blocking cards in total).`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't add blocking card to ${this.card.name}. ${error_message}`);
            this.addBlockingCardStatus = "showed";
        });
    }

        /** Called when we remove a blocking card */
    onRemoveBlockingCard(blockingCard: Card){
        this.cardService.removeBlockingCard(this.card, blockingCard).then(card_response => {
            this.card.blocking_cards = card_response.blocking_cards;
            delete this.removeBlockingCardStatus[blockingCard.id];
            // We have to remove the associated comment
            // Remember that comments with the format "blocked by <card_url_in_trello>" means card-blocking
            this.card.comments = card_response.comments;
            this.notificationsService.success("Blocking card removed", `${this.card.name} is not blocked by ${blockingCard.name} (leaving ${this.card.blocking_cards.length} blocking cards in total).`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't remove ${blockingCard.name} blocking card of ${this.card.name}. ${error_message}`);
            this.removeBlockingCardStatus[blockingCard.id] = "showed";
        });
    }

    /** Called when adding a review. */
    onAddReview(member_ids: number[], description: string): void{
        this.cardService.addNewReview(this.card, member_ids, description).then(card_response => {
            this.card.reviews = card_response.reviews;
            this.card.comments = card_response.comments;
            this.newReviewStatus = "hidden";
            let review_comment = this.card.comments[0];
            this.editCommentStatus[review_comment.id] == 'standby';
            this.deleteCommentStatus[review_comment.id] = "standby";
            this.notificationsService.success("Blocking card added", `${this.card.name} has a new review (${this.card.blocking_cards.length} in total).`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't add review to ${this.card.name}. ${error_message}`);
            this.newReviewStatus = "showed";
        });
    }

    /** Called when deleting a review */
    deleteReview(review: CardReview): void {
        this.cardService.deleteReview(this.card, review).then(card_response => {
            this.card.reviews = card_response.reviews;
            this.card.comments = card_response.comments;
            delete this.deleteReviewStatus[review.id];
            this.notificationsService.success("Review deleted", `A review of ${this.card.name} was deleted. This card has now ${this.card.reviews.length} reviews.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't delete review of ${this.card.name}. ${error_message}`);
            this.deleteReviewStatus[review.id] = "showed";
        });
    }

    /** Called when adding a requirement. */
    onAddRequirement(requirement_id: number):void {
        let requirement = this.board.requirements.find(function(requirement_i){ return requirement_i.id == requirement_id; });
        this.cardService.addRequirement(this.card, requirement).then(card_response => {
            this.card.requirements = card_response.requirements;
            this.card.comments = card_response.comments;
            this.addRequirementStatus = "hidden";
            for(let requirement of this.card.requirements){
                this.removeRequirementStatus[requirement.id] = "standby";
                this.notificationsService.success("Requirement added", `This card depends on the requirement ${requirement.name}.`);
            }
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't add requirement to ${this.card.name}. ${error_message}`);
            this.addRequirementStatus = "showed";
        });
    }

    /** Remove a requirement of this card */
    removeRequirement(requirement: Requirement): void {
        this.cardService.removeRequirement(this.card, requirement).then(card_response => {
            // Note we have to update the requirements and the comments because a comment has also been deleted.
            // Remember that the information about a requirement is stored in card comments.
            this.card.requirements = card_response.requirements;
            this.card.comments = card_response.comments;
            delete this.removeRequirementStatus[requirement.id];
            this.notificationsService.success("Requirement removed", `This card already does not depend on the requirement ${requirement.name}.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't remove requirement from ${this.card.name}. ${error_message}`);
            this.removeRequirementStatus[requirement.id] = "standby";
        });
    }

    /** Called when the card name change form is submitted */
    onChangeName(name: string){
        this.cardService.changeCardName(this.card, name).then(card_response => {
            this.card.name = name;
            this.changeNameStatus = "hidden";
            this.notificationsService.success("Name changed", `This card now is know as ${name}.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't change the name of ${this.card.name}. ${error_message}`);
            this.changeNameStatus = "showed";
        });
    }

    /** Called when the card description change form is submitted */
    onChangeDescription(description: string){
        this.cardService.changeCardDescription(this.card, description).then(card_response => {
            this.card.description = description;
            this.changeDescriptionStatus = "hidden";
            this.notificationsService.success("Description changed", `This card now has a new description.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't change the description of ${this.card.name}. ${error_message}`);
            this.changeDescriptionStatus = "showed";
        });
    }

    /** Called when the card S/E form is submitted */
    onSubmitSETimeForm(time_values: any) {
        let date = time_values["date"];
        let spent_time = time_values["spent_time"];
        let estimated_time = time_values["estimated_time"];
        let description = time_values["description"];
        this.cardService.addSETime(this.card, date, spent_time, estimated_time, description).then(updated_card => {
            this.card = updated_card;
            this.changeSETimeStatus = "standby";
            this.notificationsService.success("New S/E time added", `S: ${spent_time} / E: ${estimated_time}.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't submit a spent/estimated time to ${this.card.name}. ${error_message}`);
            this.changeSETimeStatus = "standby";
        });
    }
    
    /** Called when the change list  form is submitted */
    onSubmitChangeList(destination_list_id: number): void {
        // If the destination list is the same as the current list of the card, do nothing
        if(this.card.list.id == destination_list_id){
            this.notificationsService.error("Error", `${this.card.name} is already in ${this.card.list.name}`);
        }
        // Otherwise, get the list with that index and change the list
        for(let list_index in this.card.board.lists){
            let list_i = this.card.board.lists[list_index];
            if (list_i.id == destination_list_id) {
                this.cardService.moveCard(this.card, list_i).then(updated_card => {
                    this.card = updated_card;
                    this.changeListStatus = "hidden";
                    this.notificationsService.success("This card has been moved", `${this.card.name} is in ${this.card.list.name}.`);
                });
            }
        }
    }

    /** Called when creating new comment */
    onSubmitNewComment(comment_content: string): void {
        this.cardService.addNewComment(this.card, comment_content).then(comment => {
            this.card.comments = [comment].concat(this.card.comments);
            this.newCommentStatus = "standby"; 
            this.editCommentStatus[comment.id] = "standby";
            this.deleteCommentStatus[comment.id] = "standby";
            this.notificationsService.success("New comment added", `${this.card.name} has a new comment (${this.card.comments.length} in total).`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't add a new comment to ${this.card.name}. ${error_message}`);
            this.newCommentStatus = "standby";
        });
    }

    /** Called when editing a comment */
    onSubmitEditComment(comment: CardComment, new_content: string): void {
        this.cardService.editComment(this.card, comment, new_content).then(edited_comment => {
            comment.content = new_content;
            this.editCommentStatus[comment.id] = "standby";
            this.notificationsService.success("Comment edited", `A comment of ${this.card.name} was edited.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't edit a comment from ${this.card.name}. ${error_message}`);
            this.editCommentStatus[comment.id] = "showed";
        });
    }

    /** Called when deleting a comment */
    onSubmitDeleteComment(comment: CardComment): void {
        this.cardService.deleteComment(this.card, comment).then(deleted_comment => {
            this.card.comments.splice(this.card.comments.indexOf(comment), 1);
            delete this.deleteCommentStatus[comment.id];
            delete this.editCommentStatus[comment.id];
            delete this.commentPreviousContent[comment.id];
            this.notificationsService.success("Comment deleted", `A comment of ${this.card.name} was deleted.`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't delete a comment from ${this.card.name}. ${error_message}`);
            this.deleteCommentStatus[comment.id] = "showed";
        });;
    }

    /** Navigation on the top of the page */
    onReturnToBoardSelect(): void {
      this.router.navigate([this.board.id]);
    }

    // Basic loading methods

    /** Load card data and prepare its statuses */
    loadCard(board_id: number, card_id: number): void {
        this.cardService.getCard(board_id, card_id).then(card => {
            this.card = new Card(card);
            // Inicialization of the status of the edition or deletion or the comments of this card
            for(let comment of this.card.comments){
                this.editCommentStatus[comment.id] = "standby";
                this.deleteCommentStatus[comment.id] = "standby";
            }
            // Initialization of the status of the removal of each one of the blocking cards of this card
            for(let blocking_card of this.card.blocking_cards){
                this.removeBlockingCardStatus[blocking_card.id] = "showed";
            }
            // Initialization of the status of the removal of each one of the reviews of this card
            for(let review of this.card.reviews){
                this.deleteReviewStatus[review.id] = "showed";
            }
            // Initalization of requirements' status
            for(let requirement of this.card.requirements){
                this.removeRequirementStatus[requirement.id] = "hidden";
            }
            this.notificationsService.success("Successful load", `${card.name} loaded successfully`);
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't load this card. ${error_message}`);
        });;
    }

    loadBoard(board_id: number): void {
        this.boardService.getBoard(board_id).then(board => {
            this.board = board;
            this.card_hash = {};
            this.cards = [];
            for(let list of this.board.lists){
                for(let card of list.cards){
                    this.cards.push(card);
                    this.card_hash[card.id] = card;
                }
            }
        }).catch(error_message => {
            this.notificationsService.error("Error", `Couldn't load this card's board data. ${error_message}`);
        });
    }

}
