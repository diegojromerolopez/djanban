import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { DjanbanService } from './djanban.service';
import { Board } from '../models/board';
import { List } from '../models/list';
import { Member } from '../models/member';

@Injectable({
  providedIn: 'root'
})
export class BoardService extends DjanbanService {

  private GET_BOARDS_URL = '/api/boards/info';
  private GET_BOARD_URL = '/api/board/{id}/info';

  private MOVE_LIST_URL = '/api/board/{id}/list/{list_id}';
  private DELETE_MEMBER_URL = '/api/board/{id}/member/{member_id}';
  private ADD_MEMBER_URL = '/api/board/{id}/member';

  constructor(http: HttpClient) {
    super(http);
  }

  async getBoards(): Promise<Board[]> {
    let get_boards_url = this.GET_BOARDS_URL;
    try {
      const response = await firstValueFrom(this.http.get<Board[]>(get_boards_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async getBoard(board_id: number): Promise<Board> {
    let get_board_url = this.GET_BOARD_URL.replace(/\{id\}/, board_id.toString());
    try {
      const response = await firstValueFrom(this.http.get<Board>(get_board_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async moveList(board: Board, list: List, position = "bottom"): Promise<List> {
    let move_list_url = this.MOVE_LIST_URL.replace("{id}", board.id.toString()).replace("{list_id}", list.id.toString());
    let post_body = { position: position };
    try {
      const response = await firstValueFrom(this.http.post<List>(move_list_url, post_body));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async removeMember(board: Board, member: Member): Promise<Member> {
    let delete_member_url = this.DELETE_MEMBER_URL.replace("{id}", board.id.toString()).replace("{member_id}", member.id.toString());
    try {
      const response = await firstValueFrom(this.http.delete<Member>(delete_member_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  async addMember(board: Board, member: Member, member_type: string): Promise<Member> {
    let add_member_url = this.ADD_MEMBER_URL.replace("{id}", board.id.toString());
    let put_body = { member: member.id, member_type: member_type };
    try {
      const response = await firstValueFrom(this.http.put<Member>(add_member_url, put_body));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }
}