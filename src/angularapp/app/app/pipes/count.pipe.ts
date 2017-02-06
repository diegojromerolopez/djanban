import { Pipe, PipeTransform } from '@angular/core';

/** This pipe the number or elements of an array of any type */
@Pipe({name: 'count'})
export class CountPipe implements PipeTransform {
  transform(array: any[]): number {
    return array.length;
  }
}