import { Pipe, PipeTransform } from '@angular/core';
import { Card } from '../models/card';

/**
 * This pipe returns the active cards of a card array
 * Remember that the cards have the is_closed attribute that implies the card is archived if true.
*/
@Pipe({
  name: 'active_cards',
  standalone: true
})
export class ActiveCardsPipe implements PipeTransform {
  transform(cards: Card[] | null | undefined): Card[] {
    if (!cards) {
      return [];
    }
    return cards.filter(card => !card.is_closed);
  }
}