import { List } from './list';

export class Board {
  id: number;
  uuid: string;
  name: string;
  description: string;
  lists?: List[];
}