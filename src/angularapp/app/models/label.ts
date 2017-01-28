import { Board } from './board';

export class Label {
  id: number;
  uuid: string;
  name: string;
  color: string;
  board?: Board;
}