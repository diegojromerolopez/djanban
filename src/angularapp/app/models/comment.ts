import { Member } from './member';
import { Card } from './card';
import { CardReview } from './review';


export class CardComment {
  id: number;
  uuid: string;
  content: string;
  creation_datetime: Date;
  last_edition_datetime?: Date;
  author: Member;
  blocking_card?: Card;
  review?: CardReview;
}