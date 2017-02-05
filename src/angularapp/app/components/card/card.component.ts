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


@Component({
    moduleId: module.id,
    selector: 'card',
    templateUrl: 'card.component.html',
    styleUrls: ['card.component.css'],
    providers: [BoardService, CardService]
})


export class CardComponent implements OnInit  {

    private board: Board;
    private card: Card;
    private cards: Card[];
    private card_hash: {};
    
    private locale_due_datetime_string: string;

    private now: any;

    private changeNameStatus: string;
    private changeListStatus: string;

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
        private cardService: CardService
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
        });
    }

    /** Mark card as closed (disabled) */
    closeCard(): void{
        this.cardService.closeCard(this.card).then(updated_card => {
            this.card.is_closed = true;
            this.statusCardStatus = "standby";
        });
    }

    /** Called when the change labels form is submitted */
    onChangeLabels(label_ids: number[]): void{
        this.cardService.changeCardLabels(this.card, label_ids).then(updated_card => {
            this.card = updated_card;
            this.changeLabelsStatus = "hidden";
        });
    }

    /** Called when the change members form is submitted */
    onChangeMembers(member_ids: number[]): void{
        this.cardService.changeCardMembers(this.card, member_ids).then(updated_card => {
            this.card = updated_card;
            this.changeMembersStatus = "hidden";
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
        });
    }

    removeDueDatetime(){
        this.cardService.removeCardDueDatetime(this.card).then(card_response => {
            this.card.due_datetime = null;
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
        });
    }

    /** Called when deleting a review */
    deleteReview(review: CardReview): void {
        this.cardService.deleteReview(this.card, review).then(card_response => {
            this.card.reviews = card_response.reviews;
            this.card.comments = card_response.comments;
            this.newReviewStatus = "hidden";
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
            }
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
        });
    }

    /** Called when the card name change form is submitted */
    onChangeName(name: string){
        this.cardService.changeCardName(this.card, name).then(card_response => {
            this.card.name = name;
            this.changeNameStatus = "hidden";
        });
    }

    /** Called when the card description change form is submitted */
    onChangeDescription(description: string){
        this.cardService.changeCardDescription(this.card, description).then(card_response => {
            this.card.description = description;
            this.changeDescriptionStatus = "hidden";
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
        });
    }
    
    /** Called when the change list  form is submitted */
    onSubmitChangeList(destination_list_id: number): void {
        // If the destination list is the same as the current list of the card, do nothing
        if(this.card.list.id == destination_list_id){
            return;
        }
        // Otherwise, get the list with that index and change the list
        for(let list_index in this.card.board.lists){
            let list_i = this.card.board.lists[list_index];
            if (list_i.id == destination_list_id) {
                this.cardService.moveCard(this.card, list_i).then(updated_card => {
                    this.card = updated_card;
                    this.changeListStatus = "hidden"; 
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
        });
    }

    /** Called when editing a comment */
    onSubmitEditComment(comment: CardComment, new_content: string): void {
        this.cardService.editComment(this.card, comment, new_content).then(edited_comment => {
            comment.content = new_content;
            this.editCommentStatus[comment.id] = "standby";
        });
    }

    /** Called when deleting a comment */
    onSubmitDeleteComment(comment: CardComment): void {
        this.cardService.deleteComment(this.card, comment).then(deleted_comment => {
            this.card.comments.splice(this.card.comments.indexOf(comment), 1);
            delete this.deleteCommentStatus[comment.id];
            delete this.editCommentStatus[comment.id];
            delete this.commentPreviousContent[comment.id];
        });
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
        });
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
        });
    }

}
