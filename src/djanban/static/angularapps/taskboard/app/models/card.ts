import { List } from './list';
import { CardComment } from './comment';
import { Board } from './board';
import { Member } from './member';
import { Label } from './label';
import { assign } from 'rxjs/util/assign';
import { CardReview } from './review';
import { Requirement } from './requirement';
import { CardAttachment } from './attachment';
import { Forecast } from './forecast';


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
  value?: number;
  short_url: string;
  is_closed: boolean;
  number_of_attachments?: number;
  number_of_comments?: number;
  number_of_forward_movements?: number;
  number_of_backward_movements?: number;
  spent_time?: number;
  cycle_time?: number;
  lead_time?: number;
  board?: Board;
  list?: List;
  labels?: Label[];
  forecasts?: Forecast[];
  attachments?: CardAttachment[];
  comments?: CardComment[];
  members?: Member[];
  number_of_reviews?: number;
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