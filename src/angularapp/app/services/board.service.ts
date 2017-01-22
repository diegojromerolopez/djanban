
import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { Board } from '../models/board';

import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';

//import { Observable }     from 'rxjs/Observable';

@Injectable()
export class BoardService {

  private GET_BOARD_URL = 'http://localhost:8000/boards/api/{id}/info';
  private GET_BOARDS_URL = 'http://localhost:8000/boards/api/info';

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

}