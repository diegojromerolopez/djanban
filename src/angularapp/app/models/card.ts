import { List } from './list';
import { CardComment } from './comment';
import { Board } from './board';
import { Member } from './member';
import { Label } from './label';


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
  list?: List;
  labels?: Label[];
  comments?: CardComment[];
  members?: Member[];
}