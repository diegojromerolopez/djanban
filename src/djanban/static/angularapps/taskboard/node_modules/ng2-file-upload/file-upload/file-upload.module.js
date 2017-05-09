"use strict";
var common_1 = require('@angular/common');
var core_1 = require('@angular/core');
var file_drop_directive_1 = require('./file-drop.directive');
var file_select_directive_1 = require('./file-select.directive');
var FileUploadModule = (function () {
    function FileUploadModule() {
    }
    FileUploadModule.decorators = [
        { type: core_1.NgModule, args: [{
                    imports: [common_1.CommonModule],
                    declarations: [file_drop_directive_1.FileDropDirective, file_select_directive_1.FileSelectDirective],
                    exports: [file_drop_directive_1.FileDropDirective, file_select_directive_1.FileSelectDirective]
                },] },
    ];
    /** @nocollapse */
    FileUploadModule.ctorParameters = function () { return []; };
    return FileUploadModule;
}());
exports.FileUploadModule = FileUploadModule;
