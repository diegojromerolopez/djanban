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
    if(position == "top"){
      this.cards = [card].concat(this.cards);
    }else if(position == "bottom"){
      this.cards = this.cards.concat([card]);
    }else{
      this.cards.push(card);
      this.sortCards();
    }

  }

  public removeCard(card: Card){
    let removed_card = this.getCardById(card.id);
    let removed_card_index = this.cards.indexOf(removed_card);
    if(removed_card_index == 0){
      this.cards.pop();
    }else{
      this.cards.slice(0, removed_card_index).concat(this.cards.slice(removed_card_index+1))
    } 
  }

  private sortCards(){
    this.cards.sort(function(card_i: Card, card_j: Card){
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