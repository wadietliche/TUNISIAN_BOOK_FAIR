import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://127.0.0.1:5000';  // Replace with your actual backend API URL
  private currentUserSubject: BehaviorSubject<any>;
  public currentUser: Observable<any>;

  constructor(private http: HttpClient, private router: Router) {
    // Initializing the currentUser subject with any user data in localStorage
    this.currentUserSubject = new BehaviorSubject<any>(JSON.parse(localStorage.getItem('currentUser') || '{}'));
    this.currentUser = this.currentUserSubject.asObservable();
  }

  // Getter for current user
  public get currentUserValue(): any {
    return this.currentUserSubject.value;
  }

  // Signup method
  adminLogin(admin_name: string, password: string): Observable<any> {
    const loginData = { admin_name, password };
    console.log(loginData)
    return this.http.post<any>(`${this.apiUrl}/admin/login`, loginData).pipe(
      catchError(error => {
        throw error;
      })
    );
  }
  authorLogin(username: string, password: string): Observable<any> {
    const loginData = { username, password };
    console.log(loginData)
    return this.http.post<any>(`${this.apiUrl}/author/login`, loginData).pipe(
      catchError(error => {
        throw error;
      })
    );
  }
  attendeeLogin(attendee_name: string, password: string): Observable<any> {
    const loginData = { attendee_name, password };
    console.log(loginData)
    return this.http.post<any>(`${this.apiUrl}/attendee/login`, loginData).pipe(
      catchError(error => {
        throw error;
      })
    );
  }

  signupAuthor(username: string, password: string, author_name: string): Observable<any> {
    const signupData = { username, password,author_name };
    return this.http.post<any>(`${this.apiUrl}/author/signup`, signupData).pipe(
      catchError(error => {
        throw error;
      })
    );
  }

  signupAttendee(attendee_name: string, password: string): Observable<any> {
    const signupData = { attendee_name, password };
    return this.http.post<any>(`${this.apiUrl}/attendee/signup`, signupData).pipe(
      catchError(error => {
        throw error;
      })
    );
  }

}
