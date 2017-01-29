import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Board } from '../../models/board';
import { BoardService } from '../../services/board.service';
import { ActivatedRoute } from '@angular/router';
import { Card } from '../../models/card';
import {DragulaDirective, DragulaService} from 'ng2-dragula/ng2-dragula';
import { List } from '../../models/list';
import { CardService } from '../../services/card.service';


@Component({
    moduleId: module.id,
    selector: 'board',
    templateUrl: 'board.component.html',
    styleUrls: ['board.component.css'],
    providers: [BoardService, CardService, DragulaService]
})

export class BoardComponent implements OnInit {
    board: Board;

    ngOnInit(): void {
      let that = this;
      this.route.params.subscribe(params => {
        let board_id = params["board_id"];
        that.loadBoard(board_id);
      });
    }

      constructor(
        private router: Router,
        private route: ActivatedRoute,
        private boardService: BoardService,
        private cardService: CardService,
        private dragulaService: DragulaService
    ) {
      dragulaService.drag.subscribe((value: any) => {
        console.log(`drag: ${value[0]}`);
        this.onDrag(value.slice(1));
      });
      
      dragulaService.drop.subscribe((parameters: any) => {
        console.log(`drop: ${parameters[0]}`);
        console.log(parameters);

        // Card drop
        if(parameters[0] == "first-bag"){
          this.onCardDrop(parameters);
        }
        
      });
      
      dragulaService.over.subscribe((value: any) => {
        console.log(`over: ${value[0]}`);
        this.onOver(value.slice(1));
      });
      dragulaService.out.subscribe((value: any) => {
        console.log(`out: ${value[0]}`);
        this.onOut(value.slice(1));
      });
    }

    private onDrag(args: any) {
      let [e, el] = args;
      // do something
    }

    private onCardDrop(parameters: any) {
      console.log(this.board);
      console.log(this.board.getListById);
      // Source list
      let source_list_id = parameters[3]["dataset"]["list"];
      let source_list = new List(this.board.getListById(parseInt(source_list_id)));
      
      // Destination list
      let destination_list_id = parameters[2]["dataset"]["list"];
      let destination_list = new List(this.board.getListById(parseInt(destination_list_id)));

      // Card that has bee moved from source list to destination list
      let moved_card_id = parameters[1]["dataset"]["card"];
      let moved_card = destination_list.getCardById(parseInt(moved_card_id));

      // Next card in order in destination
      let next_card_in_destination_id = null;
      // If next card is null, the moved card is the last one of the list
      let next_card = null;
      if(parameters[4] != null){
        next_card_in_destination_id = parameters[4]["dataset"]["card"];
        next_card = destination_list.getCardById(parseInt(next_card_in_destination_id));
      }

      let destination_position = "bottom";
      if (next_card != null){
        destination_position = (next_card.position - 10).toString();
      }

      // Move card to list
      this.cardService.moveCard(moved_card, destination_list, destination_position).then(card => {
        source_list.removeCard(moved_card);
        destination_list.addCard(moved_card, destination_position);
      });
    }

    private onOver(args: any) {
      let [e, el, container] = args;
      // do something
    }

    private onOut(args: any) {
      let [e, el, container] = args;
      // do something
    }

    loadBoard(board_id: number): void {
        this.boardService.getBoard(board_id).then(board_response =>{this.board =new Board(board_response)});
    }

    onCardSelect(card: Card): void {
      this.router.navigate(['/board', this.board.id, 'card', card.id]);
    }

    

}
