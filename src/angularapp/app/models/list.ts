import { Card } from './card';

export class List {
  id: number;
  uuid: string;
  name: string;
  type: string;
  position: number;
  cards?: Card[];
}