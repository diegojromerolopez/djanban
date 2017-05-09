import { Board } from './board';
import { assign } from 'rxjs/util/assign';

export class Label {
  id: number;
  uuid: string;
  name: string;
  color: string;
  board?: Board;
  
  public constructor(label: Label){
      assign(this, label);
  }

}