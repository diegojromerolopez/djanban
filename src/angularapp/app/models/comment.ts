import { Member } from './member';


export class CardComment {
  id: number;
  uuid: string;
  content: string;
  creation_datetime: Date;
  last_edition_datetime?: Date;
  author: Member;
}