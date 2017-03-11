import { assign } from 'rxjs/util/assign';
import { List } from './list';
import { Label } from './label';
import { Member } from './member';
import { Requirement } from './requirement';


export class Board {
  id: number;
  uuid: string;
  name: string;
  description: string;
  identicon_url: string;
  local_url?: string;
  lists?: List[];
  labels?: Label[];
  members?: Member[];
  requirements?: Requirement[];

  public constructor(board: Board){
    assign(this, board);
  }

  public getLabelById(label_id: number): Label {
    return this.labels.find(function(label_i){ return label_i.id == label_id; });
  }

  public removeLabel(label: Label): void {
    let labelIndex = this.labels.findIndex(function(label_i:Label){ return label_i.id == label.id });
    this.labels.slice(0, labelIndex).concat(this.labels.slice(labelIndex+1));
  }

  public getListById(list_id: number) : List{
    return this.lists.find(function(list_i){ return list_i.id == list_id; });
  }
  public getMemberById(member_id: number) : Member{
    return this.members.find(function(member_i){ return member_i.id == member_id; });
  }

  public addMember(member: Member){
    this.members.push(member);
  }

  public removeMember(member: Member){
    for(let member_index in this.members){
      let member_i = this.members[member_index];
      if(member_i.id == member.id){
        this.members = this.members.slice(0, parseInt(member_index)).concat(this.members.slice(parseInt(member_index)+1));
        break;
      }
    }
    
  }

}