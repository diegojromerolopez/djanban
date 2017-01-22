import { Component } from '@angular/core';

@Component({
  selector: 'django-trello-stats',
  template: `
        <nav>
            <a routerLink="/dashboard" routerLinkActive="active">Board list</a>
        </nav>
        <router-outlet></router-outlet>
    `,
})

export class AppComponent {
   
}