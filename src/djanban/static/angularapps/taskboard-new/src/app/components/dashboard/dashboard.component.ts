import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Board } from '../../models/board';
import { BoardService } from '../../services/board.service';

@Component({
    selector: 'dashboard',
    templateUrl: 'dashboard.component.html',
    styleUrls: ['dashboard.component.css'],
    standalone: true
})
export class DashboardComponent implements OnInit {

    boards: Board[] = [];

    constructor(
        private router: Router,
        private boardService: BoardService
    ) { }

    ngOnInit(): void {
        this.loadBoards()
    }

    async loadBoards(): Promise<void> {
        this.boards = await this.boardService.getBoards();
    }

    onBoardSelect(board: Board) {
        this.router.navigate([board.id]);
    }

}
