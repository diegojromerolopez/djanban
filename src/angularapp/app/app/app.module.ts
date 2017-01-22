import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';

import { HttpModule }    from '@angular/http';

import { AppComponent }  from './app.component';


import { AppRoutingModule } from './app-routing.module';
import { BoardService } from '../services/board.service';
import { BoardComponent } from '../components/board/board.component';
import { DashboardComponent } from '../components/dashboard/dashboard.component';


@NgModule({
  imports: [ 
    BrowserModule,
    HttpModule,
    FormsModule, 
    AppRoutingModule
  ],
  declarations: [ AppComponent, DashboardComponent, BoardComponent ],
  providers: [ BoardService ],
  bootstrap:    [ AppComponent ]
})

export class AppModule {
  
}
