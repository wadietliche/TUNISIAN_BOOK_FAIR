import { Component } from '@angular/core';
import { Router } from '@angular/router'; // Import Router service

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'app-frontend-angular';
  constructor(private router: Router) {}
}
