import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BoardComponent }      from '../components/board/board.component';
import { AppComponent } from './app.component';
import { DashboardComponent } from '../components/dashboard/dashboard.component';
import { CardComponent } from '../components/card/card.component';


const routes: Routes = [
  { path: '',  component: DashboardComponent },
  { path: ':board_id',  component: BoardComponent },
  { path: ':board_id/card/:card_id',  component: CardComponent }
];


@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})


export class AppRoutingModule {}
