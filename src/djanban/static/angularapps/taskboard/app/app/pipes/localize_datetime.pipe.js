"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
var core_1 = require("@angular/core");
/** This pipe returns the localized datetime of a datetime string as represented by angular2 */
var LocalizeDatetimePipe = (function () {
    function LocalizeDatetimePipe() {
    }
    LocalizeDatetimePipe.prototype.transform = function (datetimeString, args) {
        if (!datetimeString) {
            return datetimeString;
        }
        // Convert the datetime string to a Date object
        var datetime = new Date(datetimeString);
        // Get the current browser internacionalization options.
        // We are interested in current timezone and locale (language)
        var currentClientInternacionalizationOptions = Intl.DateTimeFormat().resolvedOptions();
        var currentClientTimeZone = currentClientInternacionalizationOptions.timeZone;
        var currentClientLocale = currentClientInternacionalizationOptions.locale;
        // Format options
        var dateTimeFormatOptions = {
            year: "numeric", month: "2-digit", day: "2-digit",
            hour: "2-digit", minute: "2-digit",
            timeZoneName: "short",
            timeZone: currentClientTimeZone
        };
        // Localized datetime
        var localDatetime = Intl.DateTimeFormat(currentClientLocale, dateTimeFormatOptions).format(datetime);
        return localDatetime;
    };
    return LocalizeDatetimePipe;
}());
LocalizeDatetimePipe = __decorate([
    core_1.Pipe({ name: 'localize_datetime' })
], LocalizeDatetimePipe);
exports.LocalizeDatetimePipe = LocalizeDatetimePipe;
//# sourceMappingURL=localize_datetime.pipe.js.map