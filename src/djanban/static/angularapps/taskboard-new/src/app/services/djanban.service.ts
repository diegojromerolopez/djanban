import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DjanbanService {

    constructor(protected http: HttpClient) { }

    protected extractData(res: any) {
        return res || {};
    }

    protected handleError(error: HttpErrorResponse | any) {
        let errMsg = "Not controlled error";
        if (error instanceof HttpErrorResponse) {
            const body = error.error || '';
            const err = body.message || JSON.stringify(body);
            errMsg = `${err} (${error.status} - ${error.statusText || ''}).`;
        } else {
            errMsg = error.message ? error.message : error.toString();
        }

        console.error(errMsg);
        return Promise.reject(errMsg);
    }
}