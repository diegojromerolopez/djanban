
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

  private MOVE_LIST_URL = '/api/board/{id}/list/{list_id}';

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

  moveList(board: Board, list: List, position="bottom") : Promise<List> {
    console.log(board);
    console.log(list);
    console.log(position);
    let move_list_url = this.MOVE_LIST_URL.replace("{id}", board.id.toString()).replace("{list_id}", list.id.toString());
    let post_body = {position: position}
    return this.http.post(move_list_url, post_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

}