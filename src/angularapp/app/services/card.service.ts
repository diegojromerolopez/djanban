import { KeyboardEvent } from '@angular/platform-browser/src/facade/browser';

import { Inject, Injectable } from '@angular/core';
import { Http, RequestMethod, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { CardComment } from '../models/comment';
import { DjangoTrelloStatsService } from './djangotrellostats.service';
import { Card } from '../models/card';
import { Board } from '../models/board';


import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';

//import { Observable }     from 'rxjs/Observable';

@Injectable()
export class CardService extends DjangoTrelloStatsService {

  private ADD_COMMENT_URL = "http://localhost:8000/api/board/{board_id}/card/{card_id}/comment";
  private COMMENT_URL = "http://localhost:8000/api/board/{board_id}/card/{card_id}/comment/{comment_id}";

  constructor (http: Http) {
    super(http);
  }

  addNewComment(card: Card, comment_content: string) : Promise<CardComment> {
    let board_id = card.board.id.toString();
    let card_id = card.id.toString();
    let add_new_comment_url = this.ADD_COMMENT_URL.replace("{board_id}", board_id).replace("{card_id}", card_id);
    return this.http.put(add_new_comment_url, {content: comment_content})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  editComment(card: Card, comment: CardComment, new_content: string) : Promise<CardComment> {
    let board_id = card.board.id.toString();
    let card_id = card.id.toString();
    let comment_id = comment.id.toString();
    let comment_url = this.COMMENT_URL.replace("{board_id}", board_id).replace("{card_id}", card_id).replace("{comment_id}", comment_id);
    return this.http.post(comment_url, {content: new_content})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  deleteComment(card: Card, comment: CardComment) : Promise<CardComment> {
    let board_id = card.board.id.toString();
    let card_id = card.id.toString();
    let comment_id = comment.id.toString();
    let comment_url = this.COMMENT_URL.replace("{board_id}", board_id).replace("{card_id}", card_id).replace("{comment_id}", comment_id);
    return this.http.delete(comment_url)
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