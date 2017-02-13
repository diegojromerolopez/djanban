import { Component, NgZone, OnInit, ChangeDetectorRef } from '@angular/core';
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
import { Label } from '../../models/label';


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
  
  // Visibility of the closed cards
  public closedItemsVisibility: string;
  // Status of the new card form. Stores if it is showed and if is waiting the server response
  public newCardFormStatus: {};
  // Status of the remove member action
  public removeMemberStatus: {};
  // Status of the add member form
  public addMemberStatus: {};
  // Status of the form that moves all cards of a list at once
  public moveAllCardsStatus: {};
  /** Label filter */
  public labelFilter: Label[];
  public labelFilterHash: {};

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
    // Visibility of the closed cards
    this.closedItemsVisibility = "hidden";
    // Initialization of statuses
    this.newCardFormStatus = {};
    this.removeMemberStatus = {};
    this.addMemberStatus = {};
    this.moveAllCardsStatus = {};
    // Label filter: show only the cards that has a label here
    this.labelFilter = [];
    this.labelFilterHash = {};

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
    console.log(parameters);
    // Source list
    let source_list_id = parameters[3]["dataset"]["list"];
    let source_list = this.board.getListById(parseInt(source_list_id));
    
    // Destination list
    let destination_list_id = parameters[2]["dataset"]["list"];
    let destination_list = this.board.getListById(parseInt(destination_list_id));

    // Card that has bee moved from source list to destination list
    let moved_card_id = parameters[1]["dataset"]["card"];
    let moved_card = destination_list.getCardById(parseInt(moved_card_id));
    let old_moved_card_position = moved_card.position;

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

    if(source_list_id == destination_list_id){
      destination_list = null;
    }

    // Move card
    // - To another list
    // - In the same list up or down
    this.cardService.moveCard(moved_card, destination_list, destination_position)
      .then(board_response => {
        this.prepareBoard(board_response);
        let sucessMessage = destination_list? `${moved_card.name} was moved to list ${destination_list.name} sucessfully`: `Change position of ${moved_card.name} sucessfully`
        this.notificationsService.success("Card moved successfully", sucessMessage);
      }).catch(error_message => {
        this.loadBoard(this.board.id);
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
      let list_i = 0;
      for(let list of this.board.lists){
        this.board.lists[list_i] = new List(list);
        this.newCardFormStatus[list.id] = {show: false, waiting: false};
        this.moveAllCardsStatus[list.id] = "hidden";
        list_i += 1;
      }
  }

  /** Load board */
  loadBoard(board_id: number): void {
      this.boardService.getBoard(board_id).then(board_response =>{
          this.prepareBoard(board_response);
          this.notificationsService.success("Loaded successfully", "Board loaded successfully", {timeOut: 3000});
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
      this.notificationsService.success("Removed member",  `${member.external_username} was successfully removed from ${this.board.name}.`);
    });
  }

  onAddMemberSubmit(member_id: number, member_type: string):void {
    let member = this.members.find(function(member_i: Member){ return member_i.id == member_id; });
    if(member){
      this.boardService.addMember(this.board, member, member_type).then(added_member => {
        this.board.addMember(added_member);
        this.addMemberStatus = {show: false, waiting: false};
        this.notificationsService.success("Added member",  `${member.external_username} was successfully added to ${this.board.name}.`);
      }).catch(error_message => {
        this.notificationsService.error("Error", `Couldn't add a new member to board ${this.board.name}. ${error_message}`);
      });
    }
  }

  /* Label filter */

  cardInLabelFilter(card: Card): boolean {
    // If there is no filter, card is always in the filter
    if(this.labelFilter.length == 0){
      return true;
    }
    // Otherwise, check if any of the labels of the card is in the filter
    for(let label of card.labels){
      if (label.id in this.labelFilterHash){
        return true;
      }
    }
    // If none of the labels of the car is in the filter, this card is filtered out
    return false;
  }

  /** Return a list with the cards that are in the current label filter */
  cardsInLabelFilter(cards: Card[], onlyActive: boolean): Card[]{
    let filteredCards: Card[] = [];
    for(let card of cards){
      // A card is in the label filter if:
      // We are selected open cards and this card is not closed OR we are not selecting only active cards
      // and there is some label in the filter or the latter is empty.
      if(((onlyActive && !card.is_closed) || !onlyActive) && this.cardInLabelFilter(card)){
        filteredCards.push(card);
      }
    }
    return filteredCards;
  }

  addLabelToLabelFilter(label_id: number): void {
    let label = this.board.getLabelById(label_id)
    if(this.labelFilter.findIndex(label_i => label_i.id == label_id)>=0){
      return;
    }
    this.labelFilter.push(label);
    this.labelFilterHash[label_id] = label;
  }

  removeLabelFromLabelFilter(label_id: number): void {
    let label = this.board.getLabelById(label_id)
    let labelIndex = this.labelFilter.findIndex(function(label_i:Label){ return label_i.id == label.id });
    this.labelFilter = this.labelFilter.slice(0, labelIndex).concat(this.labelFilter.slice(labelIndex+1));
    delete this.labelFilterHash[label_id];
  }

}
