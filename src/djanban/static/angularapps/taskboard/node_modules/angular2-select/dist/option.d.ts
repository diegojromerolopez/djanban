export declare class Option {
    value: string;
    label: string;
    disabled: boolean;
    highlighted: boolean;
    selected: boolean;
    shown: boolean;
    constructor(value: string, label: string);
    show(): void;
    hide(): void;
    disable(): void;
    enable(): void;
    undecoratedCopy(): {
        label: string;
        value: string;
    };
}
