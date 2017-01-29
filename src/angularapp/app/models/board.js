"use strict";
var assign_1 = require("rxjs/util/assign");
var Board = (function () {
    function Board(board) {
        assign_1.assign(this, board);
    }
    Board.prototype.getListById = function (list_id) {
        return this.lists.find(function (list_i) { return list_i.id == list_id; });
    };
    return Board;
}());
exports.Board = Board;
//# sourceMappingURL=board.js.map