import { assign } from 'rxjs/util/assign';
import { List } from './list';
import { Label } from './label';


export class Board {
  id: number;
  uuid: string;
  name: string;
  description: string;
  lists?: List[];
  labels?: Label[];

  public constructor(board: Board){
    assign(this, board);
  }

  public getListById(list_id: number) : List{
    return this.lists.find(function(list_i){ return list_i.id == list_id; });
  }

}