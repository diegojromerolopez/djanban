"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var testing_1 = require("@angular/core/testing");
var http_1 = require("@angular/http");
var testing_2 = require("@angular/http/testing");
var card_service_1 = require("./card.service");
describe('CardService', function () {
    beforeEach(function () {
        testing_1.TestBed.configureTestingModule({
            imports: [http_1.HttpModule],
            providers: [
                card_service_1.CardService,
                { provide: http_1.XHRBackend, useClass: testing_2.MockBackend }
            ]
        });
    });
    it('should be created', testing_1.inject([card_service_1.CardService], function (service) {
        expect(service).toBeTruthy();
    }));
    it('addCard should create a new card', testing_1.async(testing_1.inject([card_service_1.CardService, http_1.XHRBackend], function (service, mockBackend) {
        var mockBoard = { id: 1 };
        var mockList = { id: 10 };
        var mockResponse = { id: 100, name: 'New Card' };
        mockBackend.connections.subscribe(function (connection) {
            expect(connection.request.url).toMatch(/\/api\/board\/1\/card/);
            expect(JSON.parse(connection.request.getBody())).toEqual({
                name: 'New Card',
                list: 10,
                position: 'top'
            });
            connection.mockRespond(new http_1.Response(new http_1.ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });
        service.addCard(mockBoard, mockList, 'New Card').then(function (card) {
            expect(card.id).toBe(100);
            expect(card.name).toEqual('New Card');
        });
    })));
    it('getCard should return a card', testing_1.async(testing_1.inject([card_service_1.CardService, http_1.XHRBackend], function (service, mockBackend) {
        var mockResponse = { id: 100, name: 'Sample Card' };
        mockBackend.connections.subscribe(function (connection) {
            expect(connection.request.url).toMatch(/\/api\/board\/1\/card\/100\/info/);
            connection.mockRespond(new http_1.Response(new http_1.ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });
        service.getCard(1, 100).then(function (card) {
            expect(card.name).toEqual('Sample Card');
        });
    })));
});
//# sourceMappingURL=card.service.spec.js.map