import { composeValidators } from '@angular/forms/src/directives/shared';
import { Validator } from '@angular/forms';
import { Component, OnInit, DebugElement } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BoardService } from '../../services/board.service';
import { Card } from '../../models/card';
import { Board } from '../../models/board';
import { FormBuilder, Validators } from '@angular/forms';
import { CardService } from '../../services/card.service';
import { CardComment } from '../../models/comment';


@Component({
    moduleId: module.id,
    selector: 'card',
    templateUrl: 'card.component.html',
    styleUrls: ['card.component.css'],
    providers: [BoardService, CardService]
})


export class CardComponent implements OnInit  {

    private board_id: number;
    private card: Card;
    private editing_comment?: CardComment;
    
    /*private spentEstimatedForm = this.formBuilder.group({
        "date": ["", Validators.required],
        "spent_time": ["", Validators.required],
        "estimated_time": ["", Validators.required]
    });*/

    ngOnInit(): void {
        let that = this;
        this.route.params.subscribe(params => {
        let board_id = params["board_id"];
        let card_id = params["card_id"];
        this.board_id = board_id;
        that.loadCard(board_id, card_id);
        });
    }

    constructor(
        private route: ActivatedRoute,
        private boardService: BoardService,
        private cardService: CardService
    ) {
        
    }

    showCommentEdition(comment: CardComment) {
        this.editing_comment = comment;
        //this.EditCommentForm.value.content = comment.content;
    }

    hideCommentEdition(comment: CardComment) {
        this.editing_comment = null;
    }

    onSubmitSETimeForm(form: any) {
        console.log(form);
        //console.log(this.spentEstimatedForm.value.date);
        //console.log(this.spentEstimatedForm.value.spent_time);
        //console.log(this.spentEstimatedForm.value.estimated_time);
        //this.spentEstimatedForm.reset();
    }
    
    onSubmitNewComment(card:Card, comment_content: string): void {
        this.cardService.addNewComment(card, comment_content).then(comment => this.card.comments.push(comment));
    }

    onSubmitEditComment(card:Card, comment: CardComment, new_content: string): void {
        this.cardService.editComment(card, comment, new_content).then(edited_comment => {
            comment.content = new_content;
            this.editing_comment = null;
        });
    }

    onSubmitDeleteComment(card:Card, comment: CardComment): void {
        this.cardService.deleteComment(card, comment).then(deleted_comment => {
            this.card.comments.splice(this.card.comments.indexOf(comment), 1);
        });
    }

    loadCard(board_id: number, card_id: number): void {
        this.boardService.getCard(board_id, card_id).then(card => this.card = card);
    }

}
