"use strict";
var assign_1 = require("rxjs/util/assign");
var List = (function () {
    function List(list) {
        assign_1.assign(this, list);
    }
    List.prototype.getCardById = function (card_id) {
        return this.cards.find(function (card_i) { return card_i.id == card_id; });
    };
    List.prototype.addCard = function (card, position) {
        if (position == "top") {
            this.cards = [card].concat(this.cards);
        }
        else if (position == "bottom") {
            this.cards = this.cards.concat([card]);
        }
        else {
            this.cards.push(card);
            this.sortCards();
        }
    };
    List.prototype.removeCard = function (card) {
        var removed_card = this.getCardById(card.id);
        var removed_card_index = this.cards.indexOf(removed_card);
        if (removed_card_index == 0) {
            this.cards.pop();
        }
        else {
            this.cards.slice(0, removed_card_index).concat(this.cards.slice(removed_card_index + 1));
        }
    };
    List.prototype.sortCards = function () {
        this.cards.sort(function (card_i, card_j) {
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