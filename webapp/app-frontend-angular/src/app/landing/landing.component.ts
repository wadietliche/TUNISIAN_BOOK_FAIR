import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router'; 

@Component({
  selector: 'app-landing',
  templateUrl: './landing.component.html',
  styleUrls: ['./landing.component.css']
})
export class LandingComponent implements OnInit {
  constructor(private router: Router) {}
ngOnInit(): void {
  
}
  onSignUpAttendee() {
    this.router.navigate(['/sign-up-attendee']);
  }

  onSignUpAuthor() {
    this.router.navigate(['sign-up-author']);
  }

  onLogin() {
    this.router.navigate(['login']);
  }


}
