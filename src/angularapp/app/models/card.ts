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
  
  public getLocalDueDatetime(): string{
    let dueDatetimeObject = this.getDueDatetimeObject();
    
    let dateTimeFormatOptions = {
        year: "2-digit", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit",
        timeZoneName: "short",
        timeZone: "Europe/Madrid"
    };

    let local_due_datetime =  Intl.DateTimeFormat("es-ES", dateTimeFormatOptions).format(dueDatetimeObject);
    console.log(local_due_datetime);
    return local_due_datetime;
  }

}