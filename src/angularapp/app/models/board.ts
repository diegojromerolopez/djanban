import { List } from './list';
import { Label } from './label';


export class Board {
  id: number;
  uuid: string;
  name: string;
  description: string;
  lists?: List[];
  labels?: Label[];
}