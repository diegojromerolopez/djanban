"use strict";
var core_1 = require('@angular/core');
var dragula_directive_1 = require('./dragula.directive');
var dragula_provider_1 = require('./dragula.provider');
var DragulaModule = (function () {
    function DragulaModule() {
    }
    DragulaModule.decorators = [
        { type: core_1.NgModule, args: [{
                    exports: [dragula_directive_1.DragulaDirective],
                    declarations: [dragula_directive_1.DragulaDirective],
                    providers: [dragula_provider_1.DragulaService]
                },] },
    ];
    /** @nocollapse */
    DragulaModule.ctorParameters = function () { return []; };
    return DragulaModule;
}());
exports.DragulaModule = DragulaModule;
