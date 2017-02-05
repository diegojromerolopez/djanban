"use strict";
var assign_1 = require("rxjs/util/assign");
var Card = (function () {
    function Card(card) {
        assign_1.assign(this, card);
    }
    Card.prototype.getDueDatetimeObject = function () {
        return new Date(this.due_datetime);
    };
    Card.prototype.getLocalDueDatetime = function () {
        var dueDatetimeObject = this.getDueDatetimeObject();
        var dateTimeFormatOptions = {
            year: "2-digit", month: "2-digit", day: "2-digit",
            hour: "2-digit", minute: "2-digit",
            timeZoneName: "short",
            timeZone: "Europe/Madrid"
        };
        var local_due_datetime = Intl.DateTimeFormat("es-ES", dateTimeFormatOptions).format(dueDatetimeObject);
        console.log(local_due_datetime);
        return local_due_datetime;
    };
    return Card;
}());
exports.Card = Card;
//# sourceMappingURL=card.js.map