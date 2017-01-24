import { CardComment } from './comment';
import { Board } from './board';


export class Card {
  id: number;
  uuid: string;
  name: string;
  description: string;
  creation_datetime: Date;
  due_datetime?: Date;
  local_url: string;
  url: string;
  short_url: string;
  spent_time?: number;
  cycle_time?: number;
  lead_time?: number;
  is_closed?: boolean;
  board?: Board;
  comments?: CardComment[];
}