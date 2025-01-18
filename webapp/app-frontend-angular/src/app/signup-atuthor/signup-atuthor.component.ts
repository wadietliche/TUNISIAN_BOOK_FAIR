import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl,FormBuilder,Validators } from '@angular/forms';  // Import FormGroup and FormControl
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-signup-author',
  templateUrl: './signup-atuthor.component.html',
  styleUrls: ['./signup-atuthor.component.css']
})
export class SignupAtuthorComponent implements OnInit {
  username='';
  password='';
  authorname='';
  signUpForm!: FormGroup;

  constructor(private fb: FormBuilder, private router: Router, private authService: AuthService) {}

  ngOnInit(): void {
    this.signUpForm = this.fb.group({
      username: ['', Validators.required],
      authorname: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(3)]]
    });
  }


  onSubmit(): void {
    this.username=this.signUpForm?.get('username')?.value;
    this.password=this.signUpForm?.get('password')?.value;
    this.authorname=this.signUpForm?.get('authorname')?.value;
    if (this.signUpForm.valid) {
      const user = this.signUpForm.value;
      this.authService.signupAuthor(this.username, this.password,this.authorname).subscribe(
        data => {
          console.log('Signup successful!', data);
          this.router.navigate(['/login']);
        },
        error => {
          console.error('Signup failed', error);
        }
      );
    } else {
      console.log('Form is invalid!');
    }
  }
}
