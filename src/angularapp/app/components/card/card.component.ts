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
    
    private changeNameStatus: string;
    private changeListStatus: string;
    private changeLabelsStatus: string;
    private changeMembersStatus: string;
    private changeSETimeStatus: string;
    private changeDescriptionStatus: string;
    private newCommentStatus: string;
    private editCommentStatus: {};
    private deleteCommentStatus: {};


    ngOnInit(): void {
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
        this.changeNameStatus = "hidden";
        this.changeListStatus = "hidden";
        this.changeLabelsStatus = "hidden";
        this.changeMembersStatus = "hidden";
        this.changeSETimeStatus = "standby";
        this.changeDescriptionStatus = "hidden";
        this.newCommentStatus = "standby";
        this.editCommentStatus = { };
        this.deleteCommentStatus = { };
    }

    cardHasLabel(label: Label): boolean {
        return this.card.labels.find(function(label_i){ return label_i.id == label.id }) != undefined;
    }

    cardHasMember(member: Member): boolean {
        return this.card.members.find(function(member_id){ return member_id.id == member.id }) != undefined;
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

    /** Called when edition a comment */
    onSubmitEditComment(comment: CardComment, new_content: string): void {
        this.cardService.editComment(this.card, comment, new_content).then(edited_comment => {
            comment.content = new_content;
            this.editCommentStatus[comment.id] = "standby";
        });
    }

    onSubmitDeleteComment(comment: CardComment): void {
        this.cardService.deleteComment(this.card, comment).then(deleted_comment => {
            this.card.comments.splice(this.card.comments.indexOf(comment), 1);
            delete this.deleteCommentStatus[comment.id];
            delete this.editCommentStatus[comment.id];
        });
    }

    onReturnToBoardSelect(): void {
      this.router.navigate([this.board.id]);
    }

    loadCard(board_id: number, card_id: number): void {
        this.cardService.getCard(board_id, card_id).then(card => {
            this.card = card;
            for(let comment of this.card.comments){
                this.editCommentStatus[comment.id] = "standby";
                this.deleteCommentStatus[comment.id] = "standby";
            }
        });
    }

    loadBoard(board_id: number): void {
        this.boardService.getBoard(board_id).then(board => this.board = board);
    }

}
