"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
var core_1 = require("@angular/core");
/**
 * This pipe returns the active cards of a card array
 * Remember that the cards have the is_closed attribute that implies the card is archived if true.
*/
var ActiveCardsPipe = (function () {
    function ActiveCardsPipe() {
    }
    ActiveCardsPipe.prototype.transform = function (cards) {
        var activeCards = [];
        for (var _i = 0, cards_1 = cards; _i < cards_1.length; _i++) {
            var card = cards_1[_i];
            if (!card.is_closed) {
                activeCards.push(card);
            }
        }
        return activeCards;
    };
    return ActiveCardsPipe;
}());
ActiveCardsPipe = __decorate([
    core_1.Pipe({ name: 'active_cards' })
], ActiveCardsPipe);
exports.ActiveCardsPipe = ActiveCardsPipe;
//# sourceMappingURL=active_cards.pipe.js.map