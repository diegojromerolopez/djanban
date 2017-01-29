
import { Inject, Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { DjangoTrelloStatsService } from './djangotrellostats.service';
import { Card } from '../models/card';
import { Board } from '../models/board';


import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';


@Injectable()
export class BoardService extends DjangoTrelloStatsService{

  private GET_BOARDS_URL = '/api/boards/info';

  private GET_BOARD_URL = '/api/board/{id}/info';
  private GET_CARD_URL = '/api/board/{board_id}/card/{card_id}/info';

  constructor (http: Http) {
      super(http);
  }

  getBoards(): Promise<Board[]> {
    let get_boards_url = this.GET_BOARDS_URL;
    return this.http.get(get_boards_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  getBoard(board_id: number): Promise<Board> {
    let get_board_url = this.GET_BOARD_URL.replace(/\{id\}/, board_id.toString());
    return this.http.get(get_board_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  getCard(board_id: number, card_id: number): Promise<Card> {
    let get_card_url = this.GET_CARD_URL.replace(/\{board_id\}/, board_id.toString()).replace(/\{card_id\}/, card_id.toString());
    return this.http.get(get_card_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

}