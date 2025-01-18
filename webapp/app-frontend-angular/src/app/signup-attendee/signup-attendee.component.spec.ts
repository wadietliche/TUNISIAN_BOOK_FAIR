import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SignupAttendeeComponent } from './signup-attendee.component';

describe('SignupAttendeeComponent', () => {
  let component: SignupAttendeeComponent;
  let fixture: ComponentFixture<SignupAttendeeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SignupAttendeeComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SignupAttendeeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
