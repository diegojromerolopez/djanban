"use strict";
var core_1 = require('@angular/core');
var push_notifications_service_1 = require('./push-notifications.service');
var PushNotificationsModule = (function () {
    function PushNotificationsModule() {
    }
    PushNotificationsModule.decorators = [
        { type: core_1.NgModule, args: [{
                    providers: [push_notifications_service_1.PushNotificationsService]
                },] },
    ];
    PushNotificationsModule.ctorParameters = function () { return []; };
    return PushNotificationsModule;
}());
exports.PushNotificationsModule = PushNotificationsModule;
//# sourceMappingURL=push-notifications.module.js.map