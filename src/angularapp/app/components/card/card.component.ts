import { composeValidators } from '@angular/forms/src/directives/shared';
import { Validator } from '@angular/forms';
import { Component, OnInit, DebugElement } from '@angular/core';
import { FormGroup, FormBuilder ,Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
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
    
    private editing_comment?: CardComment;
    private change_card_list?: boolean;
    private change_card_labels?: boolean;
    
    private show_card_name_edition_form?: boolean;
    private editing_card_name?: boolean;

    private show_card_description_edition_form?: boolean;
    private editing_card_description?: boolean;

    private show_card_members_edition_form?: boolean;
    private editing_card_members?: boolean;

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
        private route: ActivatedRoute,
        private boardService: BoardService,
        private cardService: CardService
    ) {
        
    }

    cardHasLabel(label: Label): boolean {
        return this.card.labels.find(function(label_i){ return label_i.id == label.id }) != undefined;
    }

    cardHasMember(member: Member): boolean {
        return this.card.members.find(function(member_id){ return member_id.id == member.id }) != undefined;
    }

    showCommentEdition(comment: CardComment) {
        this.editing_comment = comment;
        //this.EditCommentForm.value.content = comment.content;
    }

    hideCommentEdition(comment: CardComment) {
        this.editing_comment = null;
    }

    onChangeCardLabels(label_ids: number[]): void{
        this.cardService.changeCardLabels(this.card, label_ids).then(updated_card => this.card = updated_card);
    }

    onChangeCardMembers(member_ids: number[]): void{
        this.cardService.changeCardMembers(this.card, member_ids).then(updated_card => this.card = updated_card);
    }

    onChangeCardName(name: string){
        this.cardService.changeCardName(this.card, name).then(card_response => {
            this.card.name = name;
            this.show_card_name_edition_form = false;
        });
    }

    onChangeCardDescription(description: string){
        this.cardService.changeCardDescription(this.card, description).then(card_response => {
            this.card.description = description;
            this.show_card_description_edition_form = false;
        });
    }

    onSubmitSETimeForm(time_values: any) {
        let date = time_values["date"];
        let spent_time = time_values["spent_time"];
        let estimated_time = time_values["estimated_time"];
        let description = time_values["description"];
        this.cardService.addSETime(this.card, date, spent_time, estimated_time, description).then(updated_card => this.card = updated_card);
    }
    
    onSubmitChangeList(destination_list_id: number): void {
        // If the destination list is the same as the current list of the card, do nothing
        if(this.card.list.id == destination_list_id){
            return;
        }
        // Otherwise, get the list with that index and change the list
        for(let list_index in this.card.board.lists){
            let list_i = this.card.board.lists[list_index];
            if (list_i.id == destination_list_id) {
                this.cardService.moveCard(this.card, list_i).then(updated_card => this.card = updated_card);
            }
        }
    }

    onSubmitNewComment(comment_content: string): void {
        this.cardService.addNewComment(this.card, comment_content).then(comment => this.card.comments.push(comment));
    }

    onSubmitEditComment(comment: CardComment, new_content: string): void {
        this.cardService.editComment(this.card, comment, new_content).then(edited_comment => {
            comment.content = new_content;
            this.editing_comment = null;
        });
    }

    onSubmitDeleteComment(comment: CardComment): void {
        this.cardService.deleteComment(this.card, comment).then(deleted_comment => {
            this.card.comments.splice(this.card.comments.indexOf(comment), 1);
        });
    }

    loadCard(board_id: number, card_id: number): void {
        this.boardService.getCard(board_id, card_id).then(card => this.card = card);
    }

    loadBoard(board_id: number): void {
        this.boardService.getBoard(board_id).then(board => this.board = board);
    }

}
