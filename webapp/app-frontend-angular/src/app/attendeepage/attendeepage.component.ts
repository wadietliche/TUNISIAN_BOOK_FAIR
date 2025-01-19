import { Component, OnInit } from '@angular/core';
import { AttendeeServiceService } from '../services/attendee-service.service';
import { EventModel } from '../models/event.model';
import { AuthService } from '../services/auth.service';
import { AuthorBook } from '../models/author-book.model';
import { Book } from '../models/book.model';
@Component({
  selector: 'app-attendeepage',
  templateUrl: './attendeepage.component.html',
  styleUrls: ['./attendeepage.component.css']
})
export class AttendeepageComponent implements OnInit {
  eventInfo: EventModel={duration:0,location:'',eventname:'',start_hour:'',
    final_hour:''};
    book: Book ={description: '',
      isbn: '',
      publishedDate:'',
      publisher: '',
      title: ''};
  feedback='';
  authorName='';
  bookeTitle='';
  favouriteBookTitle='';
  favouriteAuthorName='';
  authorBooks :AuthorBook[]=[];
  constructor(private attendeeService: AttendeeServiceService, private authService: AuthService) { }

  ngOnInit(): void {
    this.getEventInfo();
    this.getAuthorBooks();
  }
  onButtonClick(buttonName: string) {
    console.log(`${buttonName} button clicked`);
  }
  getEventInfo(){
    this.attendeeService.getEventInfos().subscribe(result=>{
      this.eventInfo.duration=result.duration;
      this.eventInfo.location=result.location;
      this.eventInfo.eventname=result.event_name;
      this.eventInfo.start_hour=result.start_hour;
      this.eventInfo.final_hour=result.final_hour;
    })
  }

  getBookInfo(){
    this.attendeeService.getBookData(this.bookeTitle,this.authorName).subscribe(result=>{
      this.book.description=result[0].description;
      this.book.isbn=result[0].isbn;
      this.book.publishedDate=result[0].publishedDate;
      this.book.publisher=result[0].publisher;
      this.book.title=result[0].title;
    })
  }
  getAuthorBooks(){
    this.attendeeService.getAuthorsBooks().subscribe(result =>{
      this.authorBooks=result.approved_authors_booths;
    })
  }
  onConfirmAttendee(){
    const attendee_id=this.authService.getAttendeeId();
    if(attendee_id){
      this.attendeeService.confirmAttendee(+attendee_id).subscribe()
    }
  }
  onSendFeedBack(){
    const attendee_id=this.authService.getAttendeeId();
    if(this.feedback&& attendee_id)
      this.attendeeService.addFeedBack(+attendee_id,this.feedback).subscribe()
  }
  OnSearchBook(){
    if(this.bookeTitle && this.authorName){
      this.getBookInfo()
    }
  }
  onAddFavouriteBook(){
    const attendee_id=this.authService.getAttendeeId();
    if(this.favouriteBookTitle && attendee_id )
      this.attendeeService.addFavouriteBook(+attendee_id,this.favouriteBookTitle).subscribe()
  }
  onAddFavouriteAuthor(){
    const attendee_id=this.authService.getAttendeeId();
    if(this.favouriteAuthorName && attendee_id )
      this.attendeeService.addFavouriteAuthor(+attendee_id,this.favouriteAuthorName).subscribe()
  }
  showRecommandations(){
    const attendee_id=this.authService.getAttendeeId();
    if(attendee_id)
    this.attendeeService.getRecommandations(+attendee_id).subscribe
  }
}
