"use strict";
var core_1 = require('@angular/core');
var platform_browser_1 = require('@angular/platform-browser');
var notifications_service_1 = require('./notifications.service');
var NotificationComponent = (function () {
    function NotificationComponent(notificationService, domSanitizer, zone) {
        var _this = this;
        this.notificationService = notificationService;
        this.domSanitizer = domSanitizer;
        this.zone = zone;
        this.progressWidth = 0;
        this.stopTime = false;
        this.count = 0;
        this.instance = function () {
            _this.zone.runOutsideAngular(function () {
                _this.zone.run(function () { return _this.diff = (new Date().getTime() - _this.start) - (_this.count * _this.speed); });
                if (_this.count++ === _this.steps)
                    _this.zone.run(function () { return _this.remove(); });
                else if (!_this.stopTime) {
                    if (_this.showProgressBar)
                        _this.zone.run(function () { return _this.progressWidth += 100 / _this.steps; });
                    _this.timer = setTimeout(_this.instance, (_this.speed - _this.diff));
                }
            });
        };
    }
    NotificationComponent.prototype.ngOnInit = function () {
        if (this.animate) {
            this.item.state = this.animate;
        }
        if (this.item.override) {
            this.attachOverrides();
        }
        if (this.timeOut !== 0) {
            this.startTimeOut();
        }
        this.safeSvg = this.domSanitizer.bypassSecurityTrustHtml(this.item.icon);
    };
    NotificationComponent.prototype.startTimeOut = function () {
        var _this = this;
        this.steps = this.timeOut / 10;
        this.speed = this.timeOut / this.steps;
        this.start = new Date().getTime();
        this.zone.runOutsideAngular(function () { return _this.timer = setTimeout(_this.instance, _this.speed); });
    };
    NotificationComponent.prototype.onEnter = function () {
        if (this.pauseOnHover) {
            this.stopTime = true;
        }
    };
    NotificationComponent.prototype.onLeave = function () {
        if (this.pauseOnHover) {
            this.stopTime = false;
            setTimeout(this.instance, (this.speed - this.diff));
        }
    };
    NotificationComponent.prototype.setPosition = function () {
        return this.position !== 0 ? this.position * 90 : 0;
    };
    NotificationComponent.prototype.onClick = function ($e) {
        this.item.click.emit($e);
        if (this.clickToClose) {
            this.remove();
        }
    };
    NotificationComponent.prototype.attachOverrides = function () {
        var _this = this;
        Object.keys(this.item.override).forEach(function (a) {
            if (_this.hasOwnProperty(a)) {
                _this[a] = _this.item.override[a];
            }
        });
    };
    NotificationComponent.prototype.ngOnDestroy = function () {
        clearTimeout(this.timer);
    };
    NotificationComponent.prototype.remove = function () {
        var _this = this;
        if (this.animate) {
            this.item.state = this.animate + 'Out';
            this.zone.runOutsideAngular(function () {
                setTimeout(function () {
                    _this.zone.run(function () { return _this.notificationService.set(_this.item, false); });
                }, 310);
            });
        }
        else {
            this.notificationService.set(this.item, false);
        }
    };
    NotificationComponent.decorators = [
        { type: core_1.Component, args: [{
                    selector: 'simple-notification',
                    encapsulation: core_1.ViewEncapsulation.None,
                    animations: [
                        core_1.trigger('enterLeave', [
                            core_1.state('fromRight', core_1.style({ opacity: 1, transform: 'translateX(0)' })),
                            core_1.transition('* => fromRight', [
                                core_1.style({ opacity: 0, transform: 'translateX(5%)' }),
                                core_1.animate('400ms ease-in-out')
                            ]),
                            core_1.state('fromRightOut', core_1.style({ opacity: 0, transform: 'translateX(-5%)' })),
                            core_1.transition('fromRight => fromRightOut', [
                                core_1.style({ opacity: 1, transform: 'translateX(0)' }),
                                core_1.animate('300ms ease-in-out')
                            ]),
                            core_1.state('fromLeft', core_1.style({ opacity: 1, transform: 'translateX(0)' })),
                            core_1.transition('* => fromLeft', [
                                core_1.style({ opacity: 0, transform: 'translateX(-5%)' }),
                                core_1.animate('400ms ease-in-out')
                            ]),
                            core_1.state('fromLeftOut', core_1.style({ opacity: 0, transform: 'translateX(5%)' })),
                            core_1.transition('fromLeft => fromLeftOut', [
                                core_1.style({ opacity: 1, transform: 'translateX(0)' }),
                                core_1.animate('300ms ease-in-out')
                            ]),
                            core_1.state('scale', core_1.style({ opacity: 1, transform: 'scale(1)' })),
                            core_1.transition('* => scale', [
                                core_1.style({ opacity: 0, transform: 'scale(0)' }),
                                core_1.animate('400ms ease-in-out')
                            ]),
                            core_1.state('scaleOut', core_1.style({ opacity: 0, transform: 'scale(0)' })),
                            core_1.transition('scale => scaleOut', [
                                core_1.style({ opacity: 1, transform: 'scale(1)' }),
                                core_1.animate('400ms ease-in-out')
                            ]),
                            core_1.state('rotate', core_1.style({ opacity: 1, transform: 'rotate(0deg)' })),
                            core_1.transition('* => rotate', [
                                core_1.style({ opacity: 0, transform: 'rotate(5deg)' }),
                                core_1.animate('400ms ease-in-out')
                            ]),
                            core_1.state('rotateOut', core_1.style({ opacity: 0, transform: 'rotate(-5deg)' })),
                            core_1.transition('rotate => rotateOut', [
                                core_1.style({ opacity: 1, transform: 'rotate(0deg)' }),
                                core_1.animate('400ms ease-in-out')
                            ])
                        ])
                    ],
                    template: "\n        <div class=\"simple-notification\"\n            [@enterLeave]=\"item.state\"\n            (click)=\"onClick($event)\"\n            [class]=\"theClass\"\n\n            [ngClass]=\"{\n                'alert': item.type === 'alert',\n                'error': item.type === 'error',\n                'success': item.type === 'success',\n                'info': item.type === 'info',\n                'bare': item.type === 'bare',\n                'rtl-mode': rtl\n            }\"\n\n            (mouseenter)=\"onEnter()\"\n            (mouseleave)=\"onLeave()\">\n\n            <div *ngIf=\"!item.html\">\n                <div class=\"sn-title\">{{item.title}}</div>\n                <div class=\"sn-content\">{{item.content | max:maxLength}}</div>\n\n                <div *ngIf=\"item.type !== 'bare'\" [innerHTML]=\"safeSvg\"></div>\n            </div>\n            <div *ngIf=\"item.html\" [innerHTML]=\"item.html\"></div>\n\n            <div class=\"sn-progress-loader\" *ngIf=\"showProgressBar\">\n                <span [ngStyle]=\"{'width': progressWidth + '%'}\"></span>\n            </div>\n\n        </div>\n    ",
                    styles: ["\n        .simple-notification {\n            width: 100%;\n            padding: 10px 20px;\n            box-sizing: border-box;\n            position: relative;\n            float: left;\n            margin-bottom: 10px;\n            color: #fff;\n            cursor: pointer;\n            transition: all 0.5s;\n        }\n\n        .simple-notification .sn-title {\n            margin: 0;\n            padding: 0 50px 0 0;\n            line-height: 30px;\n            font-size: 20px;\n        }\n\n        .simple-notification .sn-content {\n            margin: 0;\n            font-size: 16px;\n            padding: 0 50px 0 0;\n            line-height: 20px;\n        }\n\n        .simple-notification svg {\n            position: absolute;\n            box-sizing: border-box;\n            top: 0;\n            right: 0;\n            width: 70px;\n            height: 70px;\n            padding: 10px;\n            fill: #fff;\n        }\n\n        .simple-notification.rtl-mode {\n            direction: rtl;\n        }\n\n        .simple-notification.rtl-mode .sn-content {\n            padding: 0 0 0 50px;\n        }\n\n        .simple-notification.rtl-mode svg {\n            left: 0;\n            right: auto;\n        }\n\n        .simple-notification.error { background: #F44336; }\n        .simple-notification.success { background: #8BC34A; }\n        .simple-notification.alert { background: #ffdb5b; }\n        .simple-notification.info { background: #03A9F4; }\n\n        .simple-notification .sn-progress-loader {\n            position: absolute;\n            top: 0;\n            left: 0;\n            width: 100%;\n            height: 5px;\n        }\n\n        .simple-notification .sn-progress-loader span {\n            float: left;\n            height: 100%;\n        }\n\n        .simple-notification.success .sn-progress-loader span { background: #689F38; }\n        .simple-notification.error .sn-progress-loader span { background: #D32F2F; }\n        .simple-notification.alert .sn-progress-loader span { background: #edc242; }\n        .simple-notification.info .sn-progress-loader span { background: #0288D1; }\n        .simple-notification.bare .sn-progress-loader span { background: #ccc; }\n    "]
                },] },
    ];
    NotificationComponent.ctorParameters = function () { return [
        { type: notifications_service_1.NotificationsService, },
        { type: platform_browser_1.DomSanitizer, },
        { type: core_1.NgZone, },
    ]; };
    NotificationComponent.propDecorators = {
        'timeOut': [{ type: core_1.Input },],
        'showProgressBar': [{ type: core_1.Input },],
        'pauseOnHover': [{ type: core_1.Input },],
        'clickToClose': [{ type: core_1.Input },],
        'maxLength': [{ type: core_1.Input },],
        'theClass': [{ type: core_1.Input },],
        'rtl': [{ type: core_1.Input },],
        'animate': [{ type: core_1.Input },],
        'position': [{ type: core_1.Input },],
        'item': [{ type: core_1.Input },],
    };
    return NotificationComponent;
}());
exports.NotificationComponent = NotificationComponent;
//# sourceMappingURL=notification.component.js.map