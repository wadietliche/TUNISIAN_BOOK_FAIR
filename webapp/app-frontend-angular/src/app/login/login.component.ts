import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';  
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  authService: AuthService;
  username='';
  password='';
  role='';
  roles: string[] = ['Author', 'Attendee', 'Admin'];
  constructor(private fb: FormBuilder, authService: AuthService, private router: Router) {
    this.authService=authService;
    // Initialize the login form with form controls and validators
    this.loginForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      password: ['', [Validators.required, Validators.minLength(3)]],
      role: ['', [Validators.required]] 
    });
  }
ngOnInit(): void {
  
}
  onSubmit() {
    if (this.loginForm.valid) {
      this.username=this.loginForm?.get('username')?.value;
      this.password=this.loginForm?.get('password')?.value;
      this.role=this.loginForm?.get('role')?.value;
      if(this.role == 'Admin')
      {
        this.authService.adminLogin(this.username,this.password).subscribe((result)=>{
          if(result.admin_id){
            this.router.navigate(['/']);
          }
        })
      }
      else if(this.role == 'Author')
      {
        this.authService.authorLogin(this.username,this.password).subscribe((result)=>{
          if(result.author_id){
            this.router.navigate(['/']);
          }
        })
      }else{
        this.authService.attendeeLogin(this.username,this.password).subscribe((result)=>{
          if(result.attendee_id){
            this.router.navigate(['/attendee-page']);
            console.log(result.tokens)
            this.authService.saveToken(result.tokens.access);
            this.authService.saveAttendeeId(result.attendee_id);
          }
        })
      }
    } else {
      console.log('Form is invalid');
    }
  }
}
