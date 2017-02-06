import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { Board } from '../../models/board';
import { BoardService } from '../../services/board.service';
import { ActivatedRoute } from '@angular/router';
import { Card } from '../../models/card';
import { DragulaDirective, DragulaService } from 'ng2-dragula/ng2-dragula';
import { List } from '../../models/list';
import { CardService } from '../../services/card.service';
import { Member } from '../../models/member';
import { MemberService } from '../../services/member.service';
import { NotificationsService } from 'angular2-notifications';


@Component({
    moduleId: module.id,
    selector: 'board',
    templateUrl: 'board.component.html',
    styleUrls: ['board.component.css'],
    providers: [MemberService, BoardService, CardService, DragulaService, NotificationsService]
})


/** Board component: manages all user-board interactions */
export class BoardComponent implements OnInit {
  board: Board;
  members: Member[];
  
  // NotificationsService options
  public notificationsOptions = {
    position: ["top", "right"],
    timeOut: 10000,
    pauseOnHover: true,
  };
  
  // Status of the new card form. Stores if it is showed and if is waiting the server response
  public newCardFormStatus: {};
  // Status of the remove member action
  public removeMemberStatus: {};
  // Status of the add member form
  public addMemberStatus: {};
  // Status of the form that moves all cards of a list at once
  public moveAllCardsStatus: {};

  /** First thing we have to do is loading both the board and all available members */
  ngOnInit(): void {
    let that = this;
    this.route.params.subscribe(params => {
      let board_id = params["board_id"];
      that.loadBoard(board_id);
    });
    this.loadMembers();
  }

  /** Constructor of BoardComponent: initialization of status and setting up the Dragula service */
  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private memberService: MemberService,
    private boardService: BoardService,
    private cardService: CardService,
    private dragulaService: DragulaService,
    private notificationsService: NotificationsService
) {
    // Initialization of statuses
    this.newCardFormStatus = {};
    this.removeMemberStatus = {};
    this.addMemberStatus = {};
    this.moveAllCardsStatus = {};

    // Options of the drag and drop service
    dragulaService.setOptions('lists', {
      moves: function (el: any, container: any, handle: any) {
        return handle.className === 'move_list_handle' || handle.className == 'move_list_handle_icon';
      }
    });
    
    // Subscription to drop event 
    dragulaService.drop.subscribe((parameters: any) => {
      // Card drop
      if(parameters[0] == "cards"){
        this.onCardDrop(parameters);
      }else if(parameters[0] == "lists"){
        this.onListDrop(parameters);
      }
    });
  }

  /** Action of the drop card event */
  private onCardDrop(parameters: any) {
    
    // Source list
    let source_list_id = parameters[3]["dataset"]["list"];
    let source_list = new List(this.board.getListById(parseInt(source_list_id)));
    
    // Destination list
    let destination_list_id = parameters[2]["dataset"]["list"];
    let destination_list = new List(this.board.getListById(parseInt(destination_list_id)));

    // Card that has bee moved from source list to destination list
    let moved_card_id = parameters[1]["dataset"]["card"];
    let moved_card = destination_list.getCardById(parseInt(moved_card_id));

    // Next card in order in destination
    let next_card_in_destination_id = null;
    // If next card is null, the moved card is the last one of the list
    let next_card = null;
    if(parameters[4] != null){
      next_card_in_destination_id = parameters[4]["dataset"]["card"];
      next_card = destination_list.getCardById(parseInt(next_card_in_destination_id));
    }

    // Position of the moved card. It will be based on the next card on the destination list (if exists).
    // Otherwise, the position will be at the bottom of the list.
    let destination_position = "bottom";
    if (next_card != null){
      destination_position = (next_card.position - 10).toString();
    }

    // Move card to list
    this.cardService.moveCard(moved_card, destination_list, destination_position)
      .then(card => {
        //source_list.removeCard(moved_card);
        //destination_list.addCard(moved_card, destination_position);
        this.notificationsService.success("Card moved successfully", `${card.name} was moved to list ${destination_list.name} sucessfully`);
      }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't move card ${moved_card.name}. ${error_message}`);
      });
  }

  /** Action of the drop list event */
  private onListDrop(parameters: any) {
    // Moved list
    let moved_list_id = parameters[1]["dataset"]["list"];
    let moved_list = new List(this.board.getListById(parseInt(moved_list_id)));

    // Next list after the list has been moved
    let next_list_id = parameters[4]["dataset"]["list"];
    let next_list: List = null;
    let destination_position = "bottom";
    if(next_list_id){
      next_list = new List(this.board.getListById(parseInt(next_list_id)));
      destination_position = (next_list.position - 10).toString();
    }
    // Call to list mover service
    this.boardService.moveList(this.board, moved_list, destination_position).then(list => {
      moved_list.position = list.position;
      // Sucess message
      // Show one message or another depending on if this is the last list or not
      let successNotificationMessage = null;
      if(next_list != null){
        let successNotificationMessage = `${moved_list.name} was sucessfully moved at in front of ${next_list.name}`;
      }else{
        let successNotificationMessage = `${moved_list.name} was sucessfully moved at the end of the board`;
      }
      this.notificationsService.success("List moved successfully", successNotificationMessage);
      
    }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't move list ${moved_list.name}. ${error_message}`);
    });
  }

  /** Prepare board attributes, status, etc. when fetching the board from the server */
  private prepareBoard(board_response: Board){
      this.board = new Board(board_response);
      for(let list of this.board.lists){
        this.newCardFormStatus[list.id] = {show: false, waiting: false};
        this.moveAllCardsStatus[list.id] = "hidden";
      }
  }

  /** Load board */
  loadBoard(board_id: number): void {
      this.boardService.getBoard(board_id).then(board_response =>{
          this.prepareBoard(board_response);
          this.notificationsService.success(`Welcome to board ${this.board.name}`, "Here you could manage all tasks. You can click no the notifications like this to close them.");
      }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't load board. ${error_message}`);
    });;
  }

  /** Load all available members */
  loadMembers(): void {
    this.memberService.getMembers().then(members => {
      this.members = members;
      for(let member of this.members){
        this.removeMemberStatus[member.id] = {waiting: false};
      }
    }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't load members. ${error_message}`);
    });
  }

  /** Move to the card view */
  onCardSelect(card: Card): void {
    this.router.navigate([this.board.id, 'card', card.id]);
  }

  /* Controls for card creation form */
  onNewCardSubmit(list: List, name: string, position: string): void {
    this.cardService.addCard(this.board, list, name, position).then(card_response => {
      List.addCardToList(list, card_response, position);
      this.newCardFormStatus[list.id] = {"show": false, "waiting": false};
      this.notificationsService.success("New card created",  `${card_response.name} was successfully created.`);
    }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't add card to board ${list.name} on board ${this.board.name}. ${error_message}`);
        this.newCardFormStatus[list.id] = {"show": true, "waiting": false};
    });
  }

  /** Action of the move all cards submit form */
  onMoveAllCardsSubmit(source_list_id: number, destination_list_id: number): void{
    console.log(source_list_id, destination_list_id);
    let sourceList = this.board.lists.find(function(list_i){ return list_i.id == source_list_id;  });
    let numberOfCardsToMove = sourceList.cards.length;
    let destinationList = this.board.lists.find(function(list_i){ return list_i.id == destination_list_id;  });
    if(sourceList && destinationList){
      this.cardService.moveAllListCards(this.board, sourceList, destinationList).then(board_response => {
        this.prepareBoard(board_response);
        this.notificationsService.success("Cards moved",  `${numberOfCardsToMove} cards from ${sourceList.name} were moved to ${destinationList.name}.`);
      }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't move all cards from ${sourceList.name} to ${destinationList.name} on board ${this.board.name}. ${error_message}`);
      });
    } else {
      this.notificationsService.error("Unable to move cards",  `There is something wrong with ${sourceList.name} or ${destinationList.name}.`);
    }
  }

  /* Member actions */
  removeMember(member: Member): void {
    this.boardService.removeMember(this.board, member).then(deleted_member => {
      this.board.removeMember(member);
      this.removeMemberStatus[member.id] = {waiting: false};
      this.notificationsService.success("Removed member",  `${member.extern_username} was successfully removed from ${this.board.name}.`);
    });
  }

  onAddMemberSubmit(member_id: number):void {
    let member = this.members.find(function(member_i: Member){ return member_i.id == member_id; });
    if(member){
      this.boardService.addMember(this.board, member).then(added_member => {
        this.board.addMember(added_member);
        this.addMemberStatus = {show: false, waiting: false};
        this.notificationsService.success("Added member",  `${member.extern_username} was successfully added to ${this.board.name}.`);
      }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't add a new member to board ${this.board.name}. ${error_message}`);
      });
    }
  }

}
