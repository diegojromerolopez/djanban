import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { DjanbanService } from './djanban.service';
import { Member } from '../models/member';

@Injectable({
  providedIn: 'root'
})
export class MemberService extends DjanbanService {

  private GET_MEMBERS_URL = '/api/members/info';

  constructor(http: HttpClient) {
    super(http);
  }

  async getMembers(): Promise<Member[]> {
    let get_members_url = this.GET_MEMBERS_URL;
    try {
      const response = await firstValueFrom(this.http.get<Member[]>(get_members_url));
      return this.extractData(response);
    } catch (error) {
      return this.handleError(error);
    }
  }
}
