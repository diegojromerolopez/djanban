import { Component } from '@angular/core';

@Component({
  selector: 'django-trello-stats',
  template: `
        <h1>DASHBOARD</h1>
        <nav>
            <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
        </nav>
        <router-outlet></router-outlet>
    `,
    //styleUrls: ['./css/app.component.css']
})

export class AppComponent {
    title = 'Django Trello Stats';
}