"use strict";
var core_1 = require('@angular/core');
var common_1 = require('@angular/common');
var notifications_service_1 = require('./notifications.service');
var simple_notifications_component_1 = require('./simple-notifications.component');
var notification_component_1 = require('./notification.component');
var max_pipe_1 = require('./max.pipe');
var SimpleNotificationsModule = (function () {
    function SimpleNotificationsModule() {
    }
    SimpleNotificationsModule.forRoot = function () {
        return {
            ngModule: SimpleNotificationsModule,
            providers: [
                notifications_service_1.NotificationsService
            ]
        };
    };
    SimpleNotificationsModule.decorators = [
        { type: core_1.NgModule, args: [{
                    imports: [common_1.CommonModule],
                    declarations: [simple_notifications_component_1.SimpleNotificationsComponent, notification_component_1.NotificationComponent, max_pipe_1.MaxPipe],
                    providers: [],
                    exports: [simple_notifications_component_1.SimpleNotificationsComponent]
                },] },
    ];
    SimpleNotificationsModule.ctorParameters = function () { return []; };
    return SimpleNotificationsModule;
}());
exports.SimpleNotificationsModule = SimpleNotificationsModule;
//# sourceMappingURL=simple-notifications.module.js.map