import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
@Injectable({
  providedIn: 'root'
})
export class AuthorServiceService {

  constructor(private http: HttpClient) { }
  private apiUrl = 'http://127.0.0.1:5000'; 

  getEventInfos(): Observable<any> {
      
      return this.http.get<any>(`${this.apiUrl}/author/event`).pipe(
        catchError(error => {
          throw error;
        })
      );
    }

  reservePlace(): Observable<any> {
      const data={};
      return this.http.post<any>(`${this.apiUrl}/author/event`,data).pipe(
        catchError(error => {
          throw error;
        })
      );
    }
  addBook(): Observable<any> {
      const data={};
      return this.http.post<any>(`${this.apiUrl}/author/book`,data).pipe(
        catchError(error => {
          throw error;
        })
      );
    }
}
