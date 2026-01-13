import { TestBed, async, inject } from '@angular/core/testing';
import { HttpModule, Http, Response, ResponseOptions, XHRBackend } from '@angular/http';
import { MockBackend } from '@angular/http/testing';
import { CardService } from './card.service';
import { Card } from '../models/card';
import { Board } from '../models/board';
import { List } from '../models/list';

describe('CardService', () => {
    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpModule],
            providers: [
                CardService,
                { provide: XHRBackend, useClass: MockBackend }
            ]
        });
    });

    it('should be created', inject([CardService], (service: CardService) => {
        expect(service).toBeTruthy();
    }));

    it('addCard should create a new card', async(inject([CardService, XHRBackend], (service: CardService, mockBackend: MockBackend) => {
        const mockBoard = { id: 1 } as Board;
        const mockList = { id: 10 } as List;
        const mockResponse = { id: 100, name: 'New Card' };

        mockBackend.connections.subscribe((connection: any) => {
            expect(connection.request.url).toMatch(/\/api\/board\/1\/card/);
            expect(JSON.parse(connection.request.getBody())).toEqual({
                name: 'New Card',
                list: 10,
                position: 'top'
            });
            connection.mockRespond(new Response(new ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });

        service.addCard(mockBoard, mockList, 'New Card').then((card) => {
            expect(card.id).toBe(100);
            expect(card.name).toEqual('New Card');
        });
    })));

    it('getCard should return a card', async(inject([CardService, XHRBackend], (service: CardService, mockBackend: MockBackend) => {
        const mockResponse = { id: 100, name: 'Sample Card' };

        mockBackend.connections.subscribe((connection: any) => {
            expect(connection.request.url).toMatch(/\/api\/board\/1\/card\/100\/info/);
            connection.mockRespond(new Response(new ResponseOptions({
                body: JSON.stringify(mockResponse)
            })));
        });

        service.getCard(1, 100).then((card) => {
            expect(card.name).toEqual('Sample Card');
        });
    })));
});
