import { Member } from './member';


export class CardAttachment {
  id: number;
  uuid: string;
  filename: string;
  url: string;
  creation_datetime: Date;
  uploader: Member;
}