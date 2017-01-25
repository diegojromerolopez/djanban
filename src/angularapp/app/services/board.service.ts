
import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { Card } from '../models/card';
import { Board } from '../models/board';

import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';

//import { Observable }     from 'rxjs/Observable';

@Injectable()
export class BoardService {

  private GET_BOARD_URL = 'http://localhost:8000/api/boards/{id}/info';
  private GET_BOARDS_URL = 'http://localhost:8000/api/boards/info';

  private GET_CARD_URL = 'http://localhost:8000/api/cards/{board_id}/{card_id}/info';

  constructor (private http: Http) { }

  private extractData(res: Response) {
    let body = res.json();
    return body || { };
  }

  private handleError (error: Response | any) {
    let errMsg: string;
    if (error instanceof Response) {
      const body = error.json() || '';
      const err = body.error || JSON.stringify(body);
      errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
    } else {
      errMsg = error.message ? error.message : error.toString();
    }
    console.error(errMsg);
    return Promise.reject(errMsg);
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

  /*addSETimeToCard(card_id: number, date: string, spent_time:number, estimated_time: number) StringMap<>{
    let add_se_to_card_url = this.ADD_SE_TO_CARD_URL.replace(/\{board_id\}/, board_id.toString()).replace(/\{card_id\}/, card_id.toString());
    return this.http.get(get_card_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
}*/

}