import { Pipe, PipeTransform } from '@angular/core';
import { Card } from '../../models/card';

/**
 * This pipe returns the active cards of a card array
 * Remember that the cards have the is_closed attribute that implies the card is archived if true.
*/
@Pipe({name: 'active_cards'})
export class ActiveCardsPipe implements PipeTransform {
  transform(cards: Card[]): Card[] {
    let activeCards: Card[] = [];
    for(let card of cards){
      if(!card.is_closed){
        activeCards.push(card);
      }
    }
    return activeCards;
  }
}