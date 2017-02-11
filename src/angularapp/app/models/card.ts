import { List } from './list';
import { CardComment } from './comment';
import { Board } from './board';
import { Member } from './member';
import { Label } from './label';
import { assign } from 'rxjs/util/assign';
import { CardReview } from './review';
import { Requirement } from './requirement';


export class Card {
  id: number;
  uuid: string;
  name: string;
  description: string;
  creation_datetime: Date;
  due_datetime?: Date;
  local_url: string;
  url: string;
  position: number;
  short_url: string;
  is_closed: boolean;
  number_of_forward_movements?: number;
  number_of_backward_movements?: number;
  spent_time?: number;
  cycle_time?: number;
  lead_time?: number;
  board?: Board;
  list?: List;
  labels?: Label[];
  comments?: CardComment[];
  members?: Member[];
  reviews?: CardReview[];
  charts?: {};
  blocking_cards?: Card[];
  requirements?: Requirement[];

  public constructor(card: Card){
    assign(this, card)
  }

  
  getDueDatetimeObject(): Date{
    return new Date(this.due_datetime);
  }

}