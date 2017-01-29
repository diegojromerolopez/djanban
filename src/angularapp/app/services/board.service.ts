
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
import { List } from '../models/list';


@Injectable()
export class BoardService extends DjangoTrelloStatsService{

  private GET_BOARDS_URL = '/api/boards/info';
  private GET_BOARD_URL = '/api/board/{id}/info';

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

}