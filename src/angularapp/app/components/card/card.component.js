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
var core_1 = require('@angular/core');
var router_1 = require('@angular/router');
var board_service_1 = require('../../services/board.service');
var CardComponent = (function () {
    function CardComponent(route, boardService) {
        this.route = route;
        this.boardService = boardService;
    }
    /*private spentEstimatedForm = this.formBuilder.group({
        "date": ["", Validators.required],
        "spent_time": ["", Validators.required],
        "estimated_time": ["", Validators.required]
    });*/
    CardComponent.prototype.ngOnInit = function () {
        var _this = this;
        var that = this;
        this.route.params.subscribe(function (params) {
            var board_id = params["board_id"];
            var card_id = params["card_id"];
            _this.board_id = board_id;
            that.loadCard(board_id, card_id);
        });
    };
    CardComponent.prototype.onSubmitSETimeForm = function (form) {
        console.log(form);
        //console.log(this.spentEstimatedForm.value.date);
        //console.log(this.spentEstimatedForm.value.spent_time);
        //console.log(this.spentEstimatedForm.value.estimated_time);
        //this.spentEstimatedForm.reset();
    };
    CardComponent.prototype.loadCard = function (board_id, card_id) {
        var _this = this;
        this.boardService.getCard(board_id, card_id).then(function (card) { return _this.card = card; });
    };
    CardComponent = __decorate([
        core_1.Component({
            moduleId: module.id,
            selector: 'card',
            templateUrl: 'card.component.html',
            styleUrls: ['card.component.css'],
            providers: [board_service_1.BoardService]
        }), 
        __metadata('design:paramtypes', [router_1.ActivatedRoute, board_service_1.BoardService])
    ], CardComponent);
    return CardComponent;
}());
exports.CardComponent = CardComponent;
//# sourceMappingURL=card.component.js.map