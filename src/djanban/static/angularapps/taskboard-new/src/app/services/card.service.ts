import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { DjanbanService } from './djanban.service';
import { Card } from '../models/card';
import { Board } from '../models/board';
import { List } from '../models/list';
import { CardAttachment } from '../models/attachment';
import { Requirement } from '../models/requirement';
import { CardReview } from '../models/review';
import { CardComment } from '../models/comment';

@Injectable({
  providedIn: 'root'
})
export class CardService extends DjanbanService {

  private ADD_CARD_URL = "/api/board/{board_id}/card";
  private ADD_SE_URL = "/api/board/{board_id}/card/{card_id}/time";
  private UPDATE_FORECASTS = "/api/board/{board_id}/card/{card_id}/forecasts";
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
  private DELETE_ATTACHMENT_URL = '/api/board/{board_id}/card/{card_id}/attachment/{attachment_id}';

  constructor(http: HttpClient) {
    super(http);
  }

  async addCard(board: Board, list: List, name: string, position = "top"): Promise<Card> {
    let add_card_url = this.ADD_CARD_URL.replace(/\{board_id\}/, board.id.toString());
    let put_body = { name: name, list: list.id, position: position };
    try {
      const response = await firstValueFrom(this.http.put<Card>(add_card_url, put_body));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async addSETime(card: Card, date: string, spent_time: number, estimated_time: number, description: string) {
    let add_se_url = this.prepareUrl(this.ADD_SE_URL, card);
    let post_body = { date: date, spent_time: spent_time, estimated_time: estimated_time, description: description };
    try {
      const response = await firstValueFrom(this.http.post(add_se_url, post_body));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async updateForecasts(card: Card) {
    let update_forecasts_url = this.prepareUrl(this.UPDATE_FORECASTS, card);
    try {
      const response = await firstValueFrom(this.http.post(update_forecasts_url, {}));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async changeCardValue(card: Card, value?: number) {
    let change_value_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put(change_value_url, { value: value }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async changeCardName(card: Card, new_name: string): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(change_card_url, { name: new_name }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async changeCardDescription(card: Card, new_description: string): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(change_card_url, { description: new_description }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async changeCardDueDatetime(card: Card, due_datetime: Date): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(change_card_url, { due_datetime: due_datetime }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async removeCardDueDatetime(card: Card): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(change_card_url, { due_datetime: null }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async activeCard(card: Card): Promise<Card> {
    return this.changeCardClausure(card, false);
  }

  async closeCard(card: Card): Promise<Card> {
    return this.changeCardClausure(card, true);
  }

  async changeCardClausure(card: Card, is_closed: boolean): Promise<Card> {
    let change_card_url = this.prepareUrl(this.CHANGE_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(change_card_url, { is_closed: is_closed }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async changeCardLabels(card: Card, new_label_ids: number[]): Promise<Card> {
    let chage_labels_url = this.prepareUrl(this.CHANGE_LABELS_URL, card);
    try {
      const response = await firstValueFrom(this.http.post<Card>(chage_labels_url, { labels: new_label_ids }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async changeCardMembers(card: Card, new_member_ids: number[]): Promise<Card> {
    let chage_members_url = this.prepareUrl(this.CHANGE_MEMBERS_URL, card);
    try {
      const response = await firstValueFrom(this.http.post<Card>(chage_members_url, { members: new_member_ids }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async addBlockingCard(card: Card, blocking_card: Card): Promise<Card> {
    let add_blocking_card_url = this.prepareUrl(this.BLOCKING_CARD_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(add_blocking_card_url, { blocking_card: blocking_card.id }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async removeBlockingCard(card: Card, blocking_card: Card): Promise<Card> {
    let remove_blocking_card_url = this.prepareUrl(this.REMOVE_BLOCKING_CARD_URL, card).replace("{blocking_card_id}", blocking_card.id.toString());
    try {
      const response = await firstValueFrom(this.http.delete<Card>(remove_blocking_card_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async addNewReview(card: Card, new_member_ids: number[], description: string): Promise<Card> {
    let add_new_review_url = this.prepareUrl(this.ADD_REVIEW_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(add_new_review_url, { members: new_member_ids, description: description }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteReview(card: Card, review: CardReview): Promise<Card> {
    let delete_review_url = this.prepareUrl(this.DELETE_REVIEW_URL, card).replace("{review_id}", review.id.toString());
    try {
      const response = await firstValueFrom(this.http.delete<Card>(delete_review_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async addRequirement(card: Card, requirement: Requirement): Promise<Card> {
    let add_requirement_url = this.prepareUrl(this.ADD_REQUIREMENT_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<Card>(add_requirement_url, { requirement: requirement.id }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async removeRequirement(card: Card, requirement: Requirement): Promise<Card> {
    let remove_requirement_url = this.prepareUrl(this.REMOVE_REQUIREMENT_URL, card).replace("{requirement_id}", requirement.id.toString());
    try {
      const response = await firstValueFrom(this.http.delete<Card>(remove_requirement_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteAttachment(card: Card, attachment: CardAttachment) {
    let delete_attachment_url = this.prepareUrl(this.DELETE_ATTACHMENT_URL, card).replace("{attachment_id}", attachment.id.toString());
    try {
      const response = await firstValueFrom(this.http.delete(delete_attachment_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async addNewComment(card: Card, comment_content: string): Promise<CardComment> {
    let add_new_comment_url = this.prepareUrl(this.ADD_COMMENT_URL, card);
    try {
      const response = await firstValueFrom(this.http.put<CardComment>(add_new_comment_url, { content: comment_content }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async deleteComment(card: Card, comment: CardComment): Promise<CardComment> {
    let comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment.id.toString());
    try {
      const response = await firstValueFrom(this.http.delete<CardComment>(comment_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async editComment(card: Card, comment: CardComment, new_content: string): Promise<CardComment> {
    let comment_url = this.prepareUrl(this.COMMENT_URL, card).replace("{comment_id}", comment.id.toString());
    try {
      const response = await firstValueFrom(this.http.post<CardComment>(comment_url, { content: new_content }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getCard(board_id: number, card_id: number): Promise<Card> {
    let get_card_url = this.GET_CARD_URL.replace(/\{board_id\}/, board_id.toString()).replace(/\{card_id\}/, card_id.toString());
    try {
      const response = await firstValueFrom(this.http.get<Card>(get_card_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async moveCard(card: Card, new_list: List, position = "top"): Promise<Board> {
    let move_list_url = this.prepareUrl(this.MOVE_CARD_URL, card);
    let post_body: any = { position: position };
    if (new_list) {
      post_body["new_list"] = new_list.id;
    }
    try {
      const response = await firstValueFrom(this.http.post<Board>(move_list_url, post_body));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async moveAllListCards(board: Board, source_list: List, destination_list: List): Promise<Board> {
    let move_all_list_cards_url = this.MOVE_ALL_LIST_CARDS_URL.replace("{board_id}", board.id.toString());
    try {
      const response = await firstValueFrom(this.http.post<Board>(move_all_list_cards_url, { source_list: source_list.id, destination_list: destination_list.id }));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  private prepareUrl(url: string, card: Card): string {
    let board_id = card.board?.id.toString();
    let card_id = card.id?.toString();
    return url.replace(/\{board_id\}/, board_id || '').replace(/\{card_id\}/, card_id || '');
  }

}