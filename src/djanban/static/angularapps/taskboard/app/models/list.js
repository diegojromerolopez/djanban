"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var assign_1 = require("rxjs/util/assign");
var List = (function () {
    function List(list) {
        assign_1.assign(this, list);
    }
    List.prototype.getCardById = function (card_id) {
        return this.cards.find(function (card_i) { return card_i.id == card_id; });
    };
    List.prototype.addCard = function (card, position) {
        List.addCardToList(this, card, position);
    };
    List.addCardToList = function (list, card, position) {
        if (position == "top") {
            list.cards = [card].concat(list.cards);
        }
        else if (position == "bottom") {
            list.cards = list.cards.concat([card]);
        }
        else {
            list.cards.push(card);
            List.sortListCards(list);
        }
    };
    List.prototype.removeCard = function (card) {
        var removed_card = this.getCardById(card.id);
        var removed_card_index = this.cards.indexOf(removed_card);
        if (removed_card_index < 0) {
            return false;
        }
        if (removed_card_index == 0) {
            this.cards.pop();
        }
        else if (removed_card_index == this.cards.length) {
            this.cards = this.cards.slice(0, this.cards.length - 1);
        }
        else {
            this.cards.slice(0, removed_card_index).concat(this.cards.slice(removed_card_index + 1));
        }
        return true;
    };
    List.prototype.sortCards = function () {
        List.sortListCards(this);
    };
    List.sortListCards = function (list) {
        list.cards.sort(function (card_i, card_j) {
            if (card_i.position < card_j.position) {
                return -1;
            }
            else if (card_i.position > card_j.position) {
                return 1;
            }
            else {
                return 0;
            }
        });
    };
    return List;
}());
exports.List = List;
//# sourceMappingURL=list.js.map