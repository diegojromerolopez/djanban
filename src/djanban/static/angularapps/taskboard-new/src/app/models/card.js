"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var assign_1 = require("rxjs/util/assign");
var Card = (function () {
    function Card(card) {
        assign_1.assign(this, card);
    }
    Card.prototype.getDueDatetimeObject = function () {
        return new Date(this.due_datetime);
    };
    return Card;
}());
exports.Card = Card;
//# sourceMappingURL=card.js.map