import { Pipe, PipeTransform } from '@angular/core';

/** This pipe returns the number of elements in an array of any type */
@Pipe({
  name: 'count',
  standalone: true
})
export class CountPipe implements PipeTransform {
  transform(array: any[] | null | undefined): number {
    return array ? array.length : 0;
  }
}