import { KeyboardEvent } from '@angular/platform-browser/src/facade/browser';

import { Inject, Injectable } from '@angular/core';
import { Http, RequestMethod, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { CardReview } from '../models/review';
import { Label } from '../models/label';
import { CardComment } from '../models/comment';
import { DjangoTrelloStatsService } from './djangotrellostats.service';
import { Card } from '../models/card';
import { Board } from '../models/board';
import { List } from '../models/list';


import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';

//import { Observable }     from 'rxjs/Observable';

@Injectable()
export class CardService extends DjangoTrelloStatsService {


  private ADD_CARD_URL = '/api/board/{board_id}/card';
  private ADD_SE_URL = "/api/board/{board_id}/card/{card_id}/time";
  private ADD_COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment";
  private COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment/{comment_id}";
  private MOVE_CARD_URL = "/api/board/{board_id}/card/{card_id}/list";
  private CHANGE_LABELS_URL = "/api/board/{board_id}/card/{card_id}/labels";
  private CHANGE_MEMBERS_URL = "/api/board/{board_id}/card/{card_id}/members";
  private CHANGE_CARD_URL = "/api/board/{board_id}/card/{card_id}";
  private GET_CARD_URL = '/api/board/{board_id}/card/{card_id}/info';
  private BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card';
  private REMOVE_BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card/{blocking_card_id}';
  private ADD_REVIEW_URL = '/api/board/{board_id}/card/{card_id}/review';
  private DELETE_REVIEW_URL = '/api/board/{board_id}/card/{card_id}/review/{review_id}';
  

  constructor (http: Http) {
    super(http);
  }

  /**
  * Adds a new card to a list of the board.
  */
  addCard(board: Board, list: List, name: string, position="top"): Promise<Card> {
    let add_card_url = this.ADD_CARD_URL.replace(/\{board_id\}/, board.id.toString());
    let put_body = {
      name: name,
      list: list.id,
      position: position
    };
    return this.http.put(add_card_url, put_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  addSETime(card: Card, date: string, spent_time:number, estimated_time: number, description: string){
    let add_se_url = this.prepareUrl(this.ADD_SE_URL, card);
    let post_body = {date: date, spent_time: spent_time, estimated_time: estimated_time, description: description};
    return this.http.post(add_se_url, post_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  changeCardName(card: Card, new_name: string): Promise<Card> {
    let chage_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(chage_card_url, {name: new_name})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  changeCardDescription(card: Card, new_description: string): Promise<Card> {
    let chage_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(chage_card_url, {description: new_description})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  changeCardLabels(card: Card, new_label_ids: number[]): Promise<Card> {
    let chage_labels_url = this.prepareUrl(this.CHANGE_LABELS_URL, card);
    return this.http.post(chage_labels_url, {labels: new_label_ids})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  changeCardMembers(card: Card, new_member_ids: number[]): Promise<Card> {
    let chage_members_url = this.prepareUrl(this.CHANGE_MEMBERS_URL, card);
    return this.http.post(chage_members_url, {members: new_member_ids})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  addBlockingCard(card: Card, blocking_card: Card): Promise<Card> {
    let add_blocking_card_url = this.prepareUrl(this.BLOCKING_CARD_URL, card);
    let put_body = {blocking_card: blocking_card.id};
    console.log(card, blocking_card);
    console.log(put_body);
    return this.http.put(add_blocking_card_url, put_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  removeBlockingCard(card: Card, blocking_card: Card): Promise<Card> {
    let remove_blocking_card_url = this.prepareUrl(this.REMOVE_BLOCKING_CARD_URL, card).replace("{blocking_card_id}", blocking_card.id.toString());
    return this.http.delete(remove_blocking_card_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);    
  }

  /** Create a new card review */
  addNewReview(card: Card, new_member_ids: number[], description: string): Promise<Card> {
    let add_new_review_url = this.prepareUrl(this.ADD_REVIEW_URL, card);
    let put_body = {members: new_member_ids, description: description};
    return this.http.put(add_new_review_url, put_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  /** Delete a card review */
  deleteReview(card: Card, review: CardReview): Promise<Card> {
    let delete_review_url = this.prepareUrl(this.DELETE_REVIEW_URL, card).replace("{review_id}", review.id.toString());
    return this.http.delete(delete_review_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  addNewComment(card: Card, comment_content: string) : Promise<CardComment> {
    let add_new_comment_url = this.prepareUrl(this.ADD_COMMENT_URL, card);
    return this.http.put(add_new_comment_url, {content: comment_content})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  deleteComment(card: Card, comment: CardComment) : Promise<CardComment> {
    let comment_id = comment.id.toString();
    let comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment_id);
    return this.http.delete(comment_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  editComment(card: Card, comment: CardComment, new_content: string) : Promise<CardComment> {
    let comment_id = comment.id.toString();
    let comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment_id);
    return this.http.post(comment_url, {content: new_content})
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

  moveCard(card: Card, new_list: List, position="top"): Promise<Card> {
    let move_list_url = this.prepareUrl(this.MOVE_CARD_URL, card);
    return this.http.post(move_list_url, {new_list: new_list.id, position: position})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }  

  private prepareUrl(url: string, card: Card): string{
    let board_id = card.board.id.toString();
    let card_id = card.id.toString();
    return url.replace(/\{board_id\}/, board_id).replace(/\{card_id\}/, card_id);
  }

}