import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { LandingComponent } from './landing/landing.component';
import { SignupAttendeeComponent } from './signup-attendee/signup-attendee.component';
import { SignupAtuthorComponent } from './signup-atuthor/signup-atuthor.component';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AppRoutingModule } from 'src/app-routing.module';
import { LoginComponent } from './login/login.component';
import { AuthService } from './services/auth.service';
import { HttpClient, HttpClientModule, HttpHandler } from '@angular/common/http';
@NgModule({
  declarations: [
    AppComponent,
    LandingComponent,
    SignupAttendeeComponent,
    SignupAtuthorComponent,
    LoginComponent
  ],
  imports: [
    BrowserModule,ReactiveFormsModule,RouterModule.forRoot([]),AppRoutingModule,HttpClientModule
  ],
  providers: [AuthService,HttpClient],
  bootstrap: [AppComponent]
})
export class AppModule { }
