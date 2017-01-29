import { OnInit } from '@angular/core';
import { Component } from '@angular/core';
import { Board } from '../../models/board';
import { Router } from '@angular/router';
import { BoardService } from '../../services/board.service';

@Component({
    moduleId: module.id,
    selector: 'dashboard',
    templateUrl: 'dashboard.component.html',
    styleUrls: ['dashboard.component.css'],
    providers: [BoardService]
})
export class DashboardComponent implements OnInit  {

    private boards: Board[];

    constructor(
        private router: Router,
        private boardService: BoardService
    ) {}

    ngOnInit(): void {
        this.loadBoards()
    }

    loadBoards(): void {
        this.boardService.getBoards().then(boards => this.boards = boards);
    }

    onBoardSelect(board: Board) {
        this.router.navigate([board.id]);
    }

}
