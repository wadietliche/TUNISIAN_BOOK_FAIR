import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-authorpage',
  templateUrl: './authorpage.component.html',
  styleUrls: ['./authorpage.component.css']
})
export class AuthorpageComponent implements OnInit {

  constructor() { }

  ngOnInit(): void {
  }
  onButtonClick(buttonName: string) {
    console.log(`${buttonName} button clicked`);
  }
}
