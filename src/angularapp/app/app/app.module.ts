import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';

import { HttpModule }    from '@angular/http';

import { AppComponent }  from './app.component';


import { AppRoutingModule } from './app-routing.module';
import { BoardService } from '../services/board.service';
import { BoardComponent } from '../components/board/board.component';
import { DashboardComponent } from '../components/dashboard/dashboard.component';
import { CardComponent } from '../components/card/card.component';
import { CardService } from '../services/card.service';
import { DragulaModule } from 'ng2-dragula/ng2-dragula';


@NgModule({
  imports: [ 
    BrowserModule,
    HttpModule,
    FormsModule, 
    AppRoutingModule,
    DragulaModule
  ],
  declarations: [ AppComponent, DashboardComponent, BoardComponent, CardComponent ],
  providers: [ BoardService, CardService ],
  bootstrap:    [ AppComponent ]
})

export class AppModule {

}
