import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { BoardService } from './board.service';
import { Board } from '../models/board';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('BoardService', () => {
    let service: BoardService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [BoardService]
        });
        service = TestBed.inject(BoardService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    it('getBoards should return boards', async () => {
        const mockResponse: Board[] = [
            { id: 1, name: 'Board 1' } as Board,
            { id: 2, name: 'Board 2' } as Board
        ];

        const promise = service.getBoards();

        const req = httpMock.expectOne('/api/boards/info');
        expect(req.request.method).toBe('GET');
        req.flush(mockResponse);

        const boards = await promise;
        expect(boards.length).toBe(2);
        expect(boards[0].name).toBe('Board 1');
    });

    it('getBoard should return a board', async () => {
        const mockResponse: Board = { id: 1, name: 'Board 1' } as Board;

        const promise = service.getBoard(1);

        const req = httpMock.expectOne('/api/board/1/info');
        expect(req.request.method).toBe('GET');
        req.flush(mockResponse);

        const board = await promise;
        expect(board.name).toBe('Board 1');
    });
});
