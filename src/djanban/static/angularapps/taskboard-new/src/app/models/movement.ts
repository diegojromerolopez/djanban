import { Member } from './member';
import { List } from './list';


export class Movement {
  id: number;
  source_list: List;
  destination_list: List;
  datetime: Date;
  member: Member;
}