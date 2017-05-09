import { Inject, Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { DjanbanService } from './djanban.service';
import { Card } from '../models/card';
import { Board } from '../models/board';


import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';
import { List } from '../models/list';
import { Member } from '../models/member';


@Injectable()
export class MemberService extends DjanbanService{

  private GET_MEMBERS_URL = '/api/members/info';

  constructor (http: Http) {
      super(http);
  }

  getMembers(): Promise<Member[]> {
    let get_members_url = this.GET_MEMBERS_URL;
    return this.http.get(get_members_url)
                  .toPromise()
                  .then(this.extractData)
                  .catch(this.handleError);
  }

}
