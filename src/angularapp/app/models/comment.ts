import { Member } from './member';
import { Card } from './card';
import { CardReview } from './review';
import { Requirement } from './requirement';


export class CardComment {
  id: number;
  uuid: string;
  content: string;
  creation_datetime: Date;
  last_edition_datetime?: Date;
  author: Member;
  blocking_card?: Card;
  valued_card?: Card;
  review?: CardReview;
  requirement?: Requirement;
}