import { Component } from '@angular/core';

@Component({
  selector: 'django-trello-stats',
  template: `
        <!--<a routerLink="" routerLinkActive="active">Board list</a>-->
        <router-outlet></router-outlet>
        <!--<simple-notifications [options]="options" (onCreate)="created($event)" (onDestroy)="destroyed($event)"></simple-notifications>-->
    `,
})

export class AppComponent {
  public options = {
      position: ["bottom", "left"],
      timeOut: 5000,
      lastOnBottom: true
  }
}