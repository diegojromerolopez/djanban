import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Board } from '../../models/board';
import { BoardService } from '../../services/board.service';
import { ActivatedRoute } from '@angular/router';
import { Card } from '../../models/card';


@Component({
    moduleId: module.id,
    selector: 'board',
    templateUrl: 'board.component.html',
    styleUrls: ['board.component.css'],
    providers: [BoardService]
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
        private boardService: BoardService
    ) {
      
    }

    loadBoard(board_id: number): void {
        this.boardService.getBoard(board_id).then(board => this.board = board);
    }

    onCardSelect(card: Card): void {
      this.router.navigate(['/board', this.board.id, 'card', card.id]);
    }

}
