import { KeyboardEvent } from '@angular/platform-browser/src/facade/browser';

import { Inject, Injectable } from '@angular/core';
import { Http, RequestMethod, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { CardAttachment } from '../models/attachment';
import { Requirement } from '../models/requirement';
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


  private ADD_CARD_URL = "/api/board/{board_id}/card";
  private ADD_SE_URL = "/api/board/{board_id}/card/{card_id}/time";
  private ADD_COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment";
  private COMMENT_URL = "/api/board/{board_id}/card/{card_id}/comment/{comment_id}";
  private MOVE_CARD_URL = "/api/board/{board_id}/card/{card_id}/list";
  private MOVE_ALL_LIST_CARDS_URL = "/api/board/{board_id}/card";
  private CHANGE_LABELS_URL = "/api/board/{board_id}/card/{card_id}/labels";
  private CHANGE_MEMBERS_URL = "/api/board/{board_id}/card/{card_id}/members";
  private CHANGE_CARD_URL = "/api/board/{board_id}/card/{card_id}";
  private GET_CARD_URL = '/api/board/{board_id}/card/{card_id}/info';
  private BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card';
  private REMOVE_BLOCKING_CARD_URL = '/api/board/{board_id}/card/{card_id}/blocking_card/{blocking_card_id}';
  private ADD_REVIEW_URL = '/api/board/{board_id}/card/{card_id}/review';
  private DELETE_REVIEW_URL = '/api/board/{board_id}/card/{card_id}/review/{review_id}';
  private ADD_REQUIREMENT_URL = '/api/board/{board_id}/card/{card_id}/requirement';
  private REMOVE_REQUIREMENT_URL = '/api/board/{board_id}/card/{card_id}/requirement/{requirement_id}';
  private DELETE_ATTACHMENT_URL = '/api/board/{board_id}/card/{card_id}/attachment/{attachment_id}'

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

  changeCardValue(card: Card, value?: number){
    let change_value_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    let put_body = {value: value};
    return this.http.put(change_value_url, put_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  changeCardName(card: Card, new_name: string): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(change_card_url, {name: new_name})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  /** Change the description of the card */
  changeCardDescription(card: Card, new_description: string): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(change_card_url, {description: new_description})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  /** Change the due datetime (deadline) */
  changeCardDueDatetime(card: Card, due_datetime: Date): Promise<Card> {
    console.log("CardService.changeCardDueDatetime");
    console.log(due_datetime);
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(change_card_url, {due_datetime: due_datetime})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  removeCardDueDatetime(card: Card): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(change_card_url, {due_datetime: null})
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  /** Change the status of the card to "active" (open or visible) */
  activeCard(card: Card): Promise<Card> {
    let is_closed = false;
    return this.changeCardClausure(card, is_closed);
  }

  /** Change the status of the card to "closed" (archived) */
  closeCard(card: Card): Promise<Card> {
    let is_closed = true;
    return this.changeCardClausure(card, is_closed);
  }

  /** Change the status of the card */
  changeCardClausure(card: Card, is_closed: boolean): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    return this.http.put(change_card_url,  {is_closed: is_closed})
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

  /** Add a new requirement to a card */
  addRequirement(card: Card, requirement: Requirement): Promise<Card> {
    let add_requirement_url = this.prepareUrl(this.ADD_REQUIREMENT_URL, card);
    let put_body = {requirement: requirement.id}
    return this.http.put(add_requirement_url, put_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);    
  }

  /** Remove a requirement from a card */
  removeRequirement(card: Card, requirement: Requirement): Promise<Card> {
    let remove_requirement_url = this.prepareUrl(this.REMOVE_REQUIREMENT_URL, card).replace("{requirement_id}", requirement.id.toString());
    return this.http.delete(remove_requirement_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);    
  }

  deleteAttachment(card: Card, attachment: CardAttachment){
    let delete_attachment_url = this.prepareUrl(this.DELETE_ATTACHMENT_URL, card).replace("{attachment_id}", attachment.id.toString());
    return this.http.delete(delete_attachment_url)
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

  /** Move a card to another list */
  moveCard(card: Card, new_list: List, position="top"): Promise<Board> {
    let move_list_url = this.prepareUrl(this.MOVE_CARD_URL, card);
    let post_body = {position: position};
    if(new_list) {
      post_body["new_list"] = new_list.id
    }
    
    return this.http.post(move_list_url, post_body)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

  /** Move all list from a card to another card */
  moveAllListCards(board: Board, source_list: List, destination_list: List): Promise<Board> {
    let move_all_list_cards_url = this.MOVE_ALL_LIST_CARDS_URL.replace("{board_id}", board.id.toString());
    return this.http.post(move_all_list_cards_url, {source_list: source_list.id, destination_list: destination_list.id})
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