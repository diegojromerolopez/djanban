import { assign } from 'rxjs/util/assign';
import { Card } from './card';

export class List {
  id: number;
  uuid: string;
  name: string;
  type: string;
  position: number;
  cards?: Card[];

  public constructor(list: List){
      assign(this, list)
  }

  public getCardById(card_id: number) : Card{
    return this.cards.find(function(card_i){ return card_i.id == card_id; });
  }

  public addCard(card: Card, position: any){
    List.addCardToList(this, card, position);
  }

  public static addCardToList(list: List, card: Card, position: any){
    if(position == "top"){
      list.cards = [card].concat(list.cards);
    }else if(position == "bottom"){
      list.cards = list.cards.concat([card]);
    }else{
      list.cards.push(card);
      List.sortListCards(list);
    }
  }

  public removeCard(card: Card){
    let removed_card = this.getCardById(card.id);
    let removed_card_index = this.cards.indexOf(removed_card);
    if(removed_card_index < 0){
      return false;
    }
    if(removed_card_index == 0){
      this.cards.pop();
    }else if(removed_card_index == this.cards.length){
      this.cards = this.cards.slice(0, this.cards.length-1);
    }else{
      this.cards.slice(0, removed_card_index).concat(this.cards.slice(removed_card_index+1))
    }
    return true; 
  }

  private sortCards(){
    List.sortListCards(this);
  }

  private static sortListCards(list: List){
    list.cards.sort(function(card_i: Card, card_j: Card){
        if(card_i.position < card_j.position) {
          return -1;
        }else if(card_i.position > card_j.position) {
          return 1;
        }else {
          return 0;
        }
      });
  }
}