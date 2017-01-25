import { composeValidators } from '@angular/forms/src/directives/shared';
import { Validator } from '@angular/forms';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BoardService } from '../../services/board.service';
import { Card } from '../../models/card';
import { Board } from '../../models/board';
import { FormBuilder, Validators } from '@angular/forms';


@Component({
    moduleId: module.id,
    selector: 'card',
    templateUrl: 'card.component.html',
    styleUrls: ['card.component.css'],
    providers: [BoardService]
})


export class CardComponent implements OnInit  {

    private board_id: number;
    private card: Card;
    
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
        private boardService: BoardService
    ) {
        
    }

    onSubmitSETimeForm(form: any) {
        console.log(form);
        //console.log(this.spentEstimatedForm.value.date);
        //console.log(this.spentEstimatedForm.value.spent_time);
        //console.log(this.spentEstimatedForm.value.estimated_time);
        //this.spentEstimatedForm.reset();
    }

    loadCard(board_id: number, card_id: number): void {
        this.boardService.getCard(board_id, card_id).then(card => this.card = card);
    }

}
