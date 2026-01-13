import { Member } from './member';


export class CardReview {
  id: number;
  creation_datetime: Date;
  reviewers: Member[];
}