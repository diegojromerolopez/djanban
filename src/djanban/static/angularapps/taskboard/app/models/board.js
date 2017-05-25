"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var assign_1 = require("rxjs/util/assign");
var Board = (function () {
    function Board(board) {
        assign_1.assign(this, board);
    }
    Board.prototype.getLabelById = function (label_id) {
        return this.labels.find(function (label_i) { return label_i.id == label_id; });
    };
    Board.prototype.removeLabel = function (label) {
        var labelIndex = this.labels.findIndex(function (label_i) { return label_i.id == label.id; });
        this.labels.slice(0, labelIndex).concat(this.labels.slice(labelIndex + 1));
    };
    Board.prototype.getListById = function (list_id) {
        return this.lists.find(function (list_i) { return list_i.id == list_id; });
    };
    Board.prototype.getMemberById = function (member_id) {
        return this.members.find(function (member_i) { return member_i.id == member_id; });
    };
    Board.prototype.addMember = function (member) {
        this.members.push(member);
    };
    Board.prototype.removeMember = function (member) {
        for (var member_index in this.members) {
            var member_i = this.members[member_index];
            if (member_i.id == member.id) {
                this.members = this.members.slice(0, parseInt(member_index)).concat(this.members.slice(parseInt(member_index) + 1));
                break;
            }
        }
    };
    return Board;
}());
exports.Board = Board;
//# sourceMappingURL=board.js.map