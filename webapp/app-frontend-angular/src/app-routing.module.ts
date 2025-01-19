import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LandingComponent } from './app/landing/landing.component';
import { SignupAttendeeComponent } from './app/signup-attendee/signup-attendee.component';
import { SignupAtuthorComponent } from './app/signup-atuthor/signup-atuthor.component';
import { LoginComponent } from './app/login/login.component';
import { AttendeepageComponent } from './app/attendeepage/attendeepage.component';
import { AuthorpageComponent } from './app/authorpage/authorpage.component';


const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'attendee-page', component: AttendeepageComponent },
  { path: 'author-page', component: AuthorpageComponent },
  { path: 'sign-up-attendee', component: SignupAttendeeComponent },
  { path: 'sign-up-author', component: SignupAtuthorComponent },
  {path:'login', component: LoginComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }