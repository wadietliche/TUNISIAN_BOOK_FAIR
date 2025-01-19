import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthorBook } from '../models/author-book.model';
import { Book } from '../models/book.model';
@Injectable({
  providedIn: 'root'
})
export class AttendeeServiceService {

  constructor(private http: HttpClient) { }
    private apiUrl = 'http://127.0.0.1:5000'; 
  
    getEventInfos(): Observable<any> {
        
        return this.http.get<any>(`${this.apiUrl}/attendee/event/1`).pipe(
          catchError(error => {
            throw error;
          })
        );
      }
      getAuthorsBooks(): Observable<any> {
        
        return this.http.get<AuthorBook[]>(`${this.apiUrl}/attendee/approved-authors-booths`).pipe(
          catchError(error => {
            throw error;
          })
        );
      }

      getBookData(author: string, title:string): Observable<any> {
        
        return this.http.get<Book[]>(`${this.apiUrl}/attendee/search`,{
          params:{
            author: author,
            title: title
          }
        }).pipe(
          catchError(error => {
            throw error;
          })
        );
      }
    confirmAttendee(attendee_id: number): Observable<any> {
        const data={attendee_id:attendee_id, feedback :''};
        return this.http.post<any>(`${this.apiUrl}/attendee/event/1`,data).pipe(
          catchError(error => {
            throw error;
          })
        );
      }

      addFeedBack(attendee_id: number,feedback: string): Observable<any> {
        const data={attendee_id:attendee_id, feedback :feedback};
        return this.http.put<any>(`${this.apiUrl}/attendee/event/1`,data).pipe(
          catchError(error => {
            throw error;
          })
        );
      }

      addFavouriteBook(attendee_id: number,book_title: string): Observable<any> {
        const data={attendee_id:attendee_id, book_title :book_title}
        return this.http.post<any>(`${this.apiUrl}/attendee/favorite/book`,data).pipe(
          catchError(error => {
            throw error;
          })
        );
      }

      addFavouriteAuthor(attendee_id: number,authorName: string): Observable<any> {
        const data={attendee_id:attendee_id, author_name :authorName}
        return this.http.post<any>(`${this.apiUrl}/attendee/favorite/author`,data).pipe(
          catchError(error => {
            throw error;
          })
        );
      }
      getRecommandations(attendee_id: number): Observable<any> {
        const data={attendee_id:attendee_id}
        return this.http.post<any>(`${this.apiUrl}/attendee/recommand`,data).pipe(
          catchError(error => {
            throw error;
          })
        );
      }

}
