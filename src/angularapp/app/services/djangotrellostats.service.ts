
import { Inject, Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import { Headers, RequestOptions } from '@angular/http';


import { Observable }     from 'rxjs/Observable';
import { Card } from '../models/card';
import { Board } from '../models/board';


import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/toPromise';

@Injectable()
export class DjangoTrelloStatsService {

    http: Http;

    constructor (http: Http) {
        this.http = http;
    }

    extractData(res: Response) {
        let body = res.json();
        return body || { };
    }

    handleError (error: Response | any) {
        let errMsg = "Not controlled error";
        try{
            if (error instanceof Response) {
                const body = error.json() || '';
                const err = body.error || JSON.stringify(body);
                errMsg = `${error.status} - ${error.statusText || ''} ${err}`;
            } else {
                errMsg = error.message ? error.message : error.toString();
            }
        }catch(e){

        }
        
        console.error(errMsg);
        return Promise.reject(errMsg);
    }
}