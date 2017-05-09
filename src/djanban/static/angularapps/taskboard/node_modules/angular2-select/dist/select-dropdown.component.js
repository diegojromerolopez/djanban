"use strict";
var core_1 = require('@angular/core');
var select_dropdown_component_css_1 = require('./select-dropdown.component.css');
var select_dropdown_component_html_1 = require('./select-dropdown.component.html');
var SelectDropdownComponent = (function () {
    function SelectDropdownComponent() {
        this.close = new core_1.EventEmitter();
        this.optionClicked = new core_1.EventEmitter();
        this.singleFilterClick = new core_1.EventEmitter();
        this.singleFilterInput = new core_1.EventEmitter();
        this.singleFilterKeydown = new core_1.EventEmitter();
        this.disabledColor = '#fff';
        this.disabledTextColor = '9e9e9e';
    }
    /** Event handlers. **/
    // Angular life cycle hooks.
    SelectDropdownComponent.prototype.ngOnInit = function () {
        this.optionsReset();
    };
    SelectDropdownComponent.prototype.ngOnChanges = function (changes) {
        if (changes.hasOwnProperty('optionList')) {
            this.optionsReset();
        }
    };
    SelectDropdownComponent.prototype.ngAfterViewInit = function () {
        this.moveHighlightedIntoView();
        if (!this.multiple && this.filterEnabled) {
            this.filterInput.nativeElement.focus();
        }
    };
    // Filter input (single select).
    SelectDropdownComponent.prototype.onSingleFilterClick = function (event) {
        this.singleFilterClick.emit(null);
    };
    SelectDropdownComponent.prototype.onSingleFilterInput = function (event) {
        this.singleFilterInput.emit(event.target.value);
    };
    SelectDropdownComponent.prototype.onSingleFilterKeydown = function (event) {
        this.singleFilterKeydown.emit(event);
    };
    // Options list.
    SelectDropdownComponent.prototype.onOptionsWheel = function (event) {
        this.handleOptionsWheel(event);
    };
    SelectDropdownComponent.prototype.onOptionMouseover = function (option) {
        this.optionList.highlightOption(option);
    };
    SelectDropdownComponent.prototype.onOptionClick = function (option) {
        this.optionClicked.emit(option);
    };
    /** Initialization. **/
    SelectDropdownComponent.prototype.optionsReset = function () {
        this.optionList.filter('');
        this.optionList.highlight();
    };
    /** View. **/
    SelectDropdownComponent.prototype.getOptionStyle = function (option) {
        if (option.highlighted) {
            var style = {};
            if (typeof this.highlightColor !== 'undefined') {
                style['background-color'] = this.highlightColor;
            }
            if (typeof this.highlightTextColor !== 'undefined') {
                style['color'] = this.highlightTextColor;
            }
            return style;
        }
        else {
            return {};
        }
    };
    SelectDropdownComponent.prototype.clearFilterInput = function () {
        if (this.filterEnabled) {
            this.filterInput.nativeElement.value = '';
        }
    };
    SelectDropdownComponent.prototype.moveHighlightedIntoView = function () {
        var list = this.optionsList.nativeElement;
        var listHeight = list.offsetHeight;
        var itemIndex = this.optionList.getHighlightedIndex();
        if (itemIndex > -1) {
            var item = list.children[0].children[itemIndex];
            var itemHeight = item.offsetHeight;
            var itemTop = itemIndex * itemHeight;
            var itemBottom = itemTop + itemHeight;
            var viewTop = list.scrollTop;
            var viewBottom = viewTop + listHeight;
            if (itemBottom > viewBottom) {
                list.scrollTop = itemBottom - listHeight;
            }
            else if (itemTop < viewTop) {
                list.scrollTop = itemTop;
            }
        }
    };
    SelectDropdownComponent.prototype.handleOptionsWheel = function (e) {
        var div = this.optionsList.nativeElement;
        var atTop = div.scrollTop === 0;
        var atBottom = div.offsetHeight + div.scrollTop === div.scrollHeight;
        if (atTop && e.deltaY < 0) {
            e.preventDefault();
        }
        else if (atBottom && e.deltaY > 0) {
            e.preventDefault();
        }
    };
    SelectDropdownComponent.decorators = [
        { type: core_1.Component, args: [{
                    selector: 'select-dropdown',
                    template: select_dropdown_component_html_1.TEMPLATE,
                    styles: [select_dropdown_component_css_1.STYLE],
                    encapsulation: core_1.ViewEncapsulation.None
                },] },
    ];
    /** @nocollapse */
    SelectDropdownComponent.ctorParameters = function () { return []; };
    SelectDropdownComponent.propDecorators = {
        'filterEnabled': [{ type: core_1.Input },],
        'highlightColor': [{ type: core_1.Input },],
        'highlightTextColor': [{ type: core_1.Input },],
        'left': [{ type: core_1.Input },],
        'multiple': [{ type: core_1.Input },],
        'notFoundMsg': [{ type: core_1.Input },],
        'optionList': [{ type: core_1.Input },],
        'top': [{ type: core_1.Input },],
        'width': [{ type: core_1.Input },],
        'close': [{ type: core_1.Output },],
        'optionClicked': [{ type: core_1.Output },],
        'singleFilterClick': [{ type: core_1.Output },],
        'singleFilterInput': [{ type: core_1.Output },],
        'singleFilterKeydown': [{ type: core_1.Output },],
        'filterInput': [{ type: core_1.ViewChild, args: ['filterInput',] },],
        'optionsList': [{ type: core_1.ViewChild, args: ['optionsList',] },],
    };
    return SelectDropdownComponent;
}());
exports.SelectDropdownComponent = SelectDropdownComponent;
