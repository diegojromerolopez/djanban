import { Component } from '@angular/core';

@Component({
  selector: 'djanban-taskboard',
  template: `
        <!--<a routerLink="" routerLinkActive="active">Board list</a>-->
        <router-outlet></router-outlet>
        <simple-notifications></simple-notifications>
    `,
})

export class AppComponent {
 
}