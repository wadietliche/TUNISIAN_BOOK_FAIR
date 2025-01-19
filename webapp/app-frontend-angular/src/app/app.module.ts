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
import { HttpClient, HttpClientModule, HttpHandler, HTTP_INTERCEPTORS } from '@angular/common/http';
import { AttendeepageComponent } from './attendeepage/attendeepage.component';
import { AuthorpageComponent } from './authorpage/authorpage.component';
import { InterceptorInterceptor } from './services/interceptor.interceptor';
import { FormsModule } from '@angular/forms';
@NgModule({
  declarations: [
    AppComponent,
    LandingComponent,
    SignupAttendeeComponent,
    SignupAtuthorComponent,
    LoginComponent,
    AttendeepageComponent,
    AuthorpageComponent
  ],
  imports: [
    BrowserModule,FormsModule,ReactiveFormsModule,RouterModule.forRoot([]),AppRoutingModule,HttpClientModule
  ],
  providers: [{
    provide: HTTP_INTERCEPTORS,
    useClass: InterceptorInterceptor,
    multi: true, // Allows multiple interceptors
  },AuthService,HttpClient],
  bootstrap: [AppComponent]
})
export class AppModule { }
