import { Pipe, PipeTransform } from '@angular/core';

/** This pipe returns the localized datetime of a datetime string as represented by angular2 */
@Pipe({name: 'localize_datetime'})
export class LocalizeDatetimePipe implements PipeTransform {
  transform(datetimeString: string, args: string[]): any {
    if (!datetimeString){
        return datetimeString;
    }

    // Convert the datetime string to a Date object
    let datetime = new Date(datetimeString);

    // Get the current browser internacionalization options.
    // We are interested in current timezone and locale (language)
    let currentClientInternacionalizationOptions = Intl.DateTimeFormat().resolvedOptions();
    let currentClientTimeZone = currentClientInternacionalizationOptions.timeZone;
    let currentClientLocale = currentClientInternacionalizationOptions.locale;
    
    // Format options
    let dateTimeFormatOptions = {
        year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit",
        timeZoneName: "short",
        timeZone: currentClientTimeZone
    };

    // Localized datetime
    let localDatetime =  Intl.DateTimeFormat(currentClientLocale, dateTimeFormatOptions).format(datetime);

    return localDatetime;
  }
}