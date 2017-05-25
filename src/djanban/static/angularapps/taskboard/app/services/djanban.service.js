"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
var core_1 = require("@angular/core");
var http_1 = require("@angular/http");
require("rxjs/add/operator/map");
require("rxjs/add/operator/catch");
require("rxjs/add/operator/toPromise");
var DjanbanService = (function () {
    function DjanbanService(http) {
        this.http = http;
    }
    DjanbanService.prototype.extractData = function (res) {
        var body = res.json();
        return body || {};
    };
    DjanbanService.prototype.handleError = function (error) {
        var errMsg = "Not controlled error";
        try {
            if (error instanceof http_1.Response) {
                var body = error.json() || '';
                errMsg = body.message + " (" + error.status + " - " + (error.statusText || '') + ").";
            }
            else {
                errMsg = error.message ? error.message : error.toString();
            }
        }
        catch (e) {
        }
        console.error(errMsg);
        return Promise.reject(errMsg);
    };
    return DjanbanService;
}());
DjanbanService = __decorate([
    core_1.Injectable(),
    __metadata("design:paramtypes", [http_1.Http])
], DjanbanService);
exports.DjanbanService = DjanbanService;
//# sourceMappingURL=djanban.service.js.map