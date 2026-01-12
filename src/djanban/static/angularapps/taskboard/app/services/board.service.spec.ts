import { TestBed, async, inject } from '@angular/core/testing';
import { HttpModule, Http, Response, ResponseOptions, XHRBackend } from '@angular/http';
import { MockBackend } from '@angular/http/testing';
import { BoardService } from './board.service';
import { Board } from '../models/board';

describe('BoardService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpModule],
            providers: [
                BoardService,
                { provide: XHRBackend, useClass: MockBackend }
            ]
        });
    });

    it('should be created', inject([BoardService], (service: BoardService) => {
        expect(service).toBeTruthy();
    }));

    it('getBoards should return boards', async(inject([BoardService, XHRBackend], (service: BoardService, mockBackend: MockBackend) => {
        const mockResponse = [
            { id: 1, name: 'Board 1' },
            { id: 2, name: 'Board 2' }
        ];

        mockBackend.connections.subscribe((connection: any) => {
            connection.mockRespond(new Response(new ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });

        service.getBoards().then((boards) => {
            expect(boards.length).toBe(2);
            expect(boards[0].name).toEqual('Board 1');
            expect(boards[1].name).toEqual('Board 2');
        });
    })));

    it('getBoard should return a board', async(inject([BoardService, XHRBackend], (service: BoardService, mockBackend: MockBackend) => {
        const mockResponse = { id: 1, name: 'Board 1' };

        mockBackend.connections.subscribe((connection: any) => {
            expect(connection.request.url).toMatch(/\/api\/board\/1\/info/);
            connection.mockRespond(new Response(new ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });

        service.getBoard(1).then((board) => {
            expect(board.name).toEqual('Board 1');
        });
    })));
});
