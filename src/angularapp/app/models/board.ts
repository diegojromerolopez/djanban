import { assign } from 'rxjs/util/assign';
import { List } from './list';
import { Label } from './label';
import { Member } from './member';


export class Board {
  id: number;
  uuid: string;
  name: string;
  description: string;
  lists?: List[];
  labels?: Label[];
  members?: Member[];

  public constructor(board: Board){
    assign(this, board);
  }

  public getListById(list_id: number) : List{
    return this.lists.find(function(list_i){ return list_i.id == list_id; });
  }

}