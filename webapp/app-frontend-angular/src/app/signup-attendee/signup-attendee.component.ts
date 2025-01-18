import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormGroup, FormControl,FormBuilder,Validators } from '@angular/forms';  // Import FormGroup and FormControl
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-signup-attendee',
  templateUrl: './signup-attendee.component.html',
  styleUrls: ['./signup-attendee.component.css']
})
export class SignupAttendeeComponent implements OnInit {
  signUpForm!: FormGroup;
  username='';
  password='';
  constructor(private fb: FormBuilder, private router: Router, private authService: AuthService) {}

  ngOnInit(): void {
    this.signUpForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(3)]]
    });
  }

  onSubmit() {
    this.username=this.signUpForm?.get('username')?.value;
    this.password=this.signUpForm?.get('password')?.value;
    this.authService.signupAttendee(this.username, this.password).subscribe(
      data => {
        console.log('Signup successful!', data);
        this.router.navigate(['/login']);
      },
      error => {
        console.error('Signup failed', error);
      }
    );
  }
 
}
