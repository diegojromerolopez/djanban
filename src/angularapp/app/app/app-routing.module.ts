import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { BoardComponent }      from '../components/board/board.component';
import { AppComponent } from './app.component';
import { DashboardComponent } from '../components/dashboard/dashboard.component';

const routes: Routes = [
 //{ path: '', redirectTo: 'dashboard', pathMatch: "prefix" },
  { path: '',  component: DashboardComponent },
  { path: 'board/:id',  component: BoardComponent },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
