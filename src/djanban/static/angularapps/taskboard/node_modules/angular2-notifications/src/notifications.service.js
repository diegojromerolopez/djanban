"use strict";
var core_1 = require('@angular/core');
var Subject_1 = require('rxjs/Subject');
var icons_1 = require('./icons');
var NotificationsService = (function () {
    function NotificationsService() {
        this.emitter = new Subject_1.Subject();
        this.icons = icons_1.defaultIcons;
    }
    NotificationsService.prototype.set = function (notification, to) {
        notification.id = notification.override && notification.override.id ? notification.override.id : Math.random().toString(36).substring(3);
        notification.click = new core_1.EventEmitter();
        this.emitter.next({ command: 'set', notification: notification, add: to });
        return notification;
    };
    ;
    NotificationsService.prototype.getChangeEmitter = function () {
        return this.emitter;
    };
    NotificationsService.prototype.success = function (title, content, override) {
        return this.set({
            title: title,
            content: content,
            type: 'success',
            icon: this.icons.success,
            override: override
        }, true);
    };
    NotificationsService.prototype.error = function (title, content, override) {
        return this.set({ title: title, content: content, type: 'error', icon: this.icons.error, override: override }, true);
    };
    NotificationsService.prototype.alert = function (title, content, override) {
        return this.set({ title: title, content: content, type: 'alert', icon: this.icons.alert, override: override }, true);
    };
    NotificationsService.prototype.info = function (title, content, override) {
        return this.set({ title: title, content: content, type: 'info', icon: this.icons.info, override: override }, true);
    };
    NotificationsService.prototype.bare = function (title, content, override) {
        return this.set({ title: title, content: content, type: 'bare', icon: 'bare', override: override }, true);
    };
    NotificationsService.prototype.create = function (title, content, type, override) {
        return this.set({ title: title, content: content, type: type, icon: 'bare', override: override }, true);
    };
    NotificationsService.prototype.html = function (html, type, override) {
        return this.set({ html: html, type: type, icon: 'bare', override: override }, true);
    };
    NotificationsService.prototype.remove = function (id) {
        if (id)
            this.emitter.next({ command: 'clean', id: id });
        else
            this.emitter.next({ command: 'cleanAll' });
    };
    NotificationsService.decorators = [
        { type: core_1.Injectable },
    ];
    NotificationsService.ctorParameters = function () { return []; };
    return NotificationsService;
}());
exports.NotificationsService = NotificationsService;
//# sourceMappingURL=notifications.service.js.map