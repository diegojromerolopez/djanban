"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var testing_1 = require("@angular/core/testing");
var http_1 = require("@angular/http");
var testing_2 = require("@angular/http/testing");
var board_service_1 = require("./board.service");
describe('BoardService', function () {
    beforeEach(function () {
        testing_1.TestBed.configureTestingModule({
            imports: [http_1.HttpModule],
            providers: [
                board_service_1.BoardService,
                { provide: http_1.XHRBackend, useClass: testing_2.MockBackend }
            ]
        });
    });
    it('should be created', testing_1.inject([board_service_1.BoardService], function (service) {
        expect(service).toBeTruthy();
    }));
    it('getBoards should return boards', testing_1.async(testing_1.inject([board_service_1.BoardService, http_1.XHRBackend], function (service, mockBackend) {
        var mockResponse = [
            { id: 1, name: 'Board 1' },
            { id: 2, name: 'Board 2' }
        ];
        mockBackend.connections.subscribe(function (connection) {
            connection.mockRespond(new http_1.Response(new http_1.ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });
        service.getBoards().then(function (boards) {
            expect(boards.length).toBe(2);
            expect(boards[0].name).toEqual('Board 1');
            expect(boards[1].name).toEqual('Board 2');
        });
    })));
    it('getBoard should return a board', testing_1.async(testing_1.inject([board_service_1.BoardService, http_1.XHRBackend], function (service, mockBackend) {
        var mockResponse = { id: 1, name: 'Board 1' };
        mockBackend.connections.subscribe(function (connection) {
            expect(connection.request.url).toMatch(/\/api\/board\/1\/info/);
            connection.mockRespond(new http_1.Response(new http_1.ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });
        service.getBoard(1).then(function (board) {
            expect(board.name).toEqual('Board 1');
        });
    })));
});
//# sourceMappingURL=board.service.spec.js.map