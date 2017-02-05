"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var core_1 = require("@angular/core");
var platform_browser_1 = require("@angular/platform-browser");
var forms_1 = require("@angular/forms");
var http_1 = require("@angular/http");
var app_component_1 = require("./app.component");
var app_routing_module_1 = require("./app-routing.module");
var board_service_1 = require("../services/board.service");
var board_component_1 = require("../components/board/board.component");
var dashboard_component_1 = require("../components/dashboard/dashboard.component");
var card_component_1 = require("../components/card/card.component");
var card_service_1 = require("../services/card.service");
var member_service_1 = require("../services/member.service");
var ng2_dragula_1 = require("ng2-dragula/ng2-dragula");
var angular2_notifications_1 = require("angular2-notifications");
var AppModule = (function () {
    function AppModule() {
    }
    return AppModule;
}());
AppModule = __decorate([
    core_1.NgModule({
        imports: [
            platform_browser_1.BrowserModule,
            http_1.HttpModule,
            forms_1.FormsModule,
            app_routing_module_1.AppRoutingModule,
            ng2_dragula_1.DragulaModule,
            angular2_notifications_1.SimpleNotificationsModule.forRoot()
        ],
        declarations: [app_component_1.AppComponent, dashboard_component_1.DashboardComponent, board_component_1.BoardComponent, card_component_1.CardComponent],
        providers: [member_service_1.MemberService, board_service_1.BoardService, card_service_1.CardService, angular2_notifications_1.NotificationsService],
        bootstrap: [app_component_1.AppComponent]
    })
], AppModule);
exports.AppModule = AppModule;
//# sourceMappingURL=app.module.js.map