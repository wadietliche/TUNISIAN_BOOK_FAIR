import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AttendeepageComponent } from './attendeepage.component';

describe('AttendeepageComponent', () => {
  let component: AttendeepageComponent;
  let fixture: ComponentFixture<AttendeepageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AttendeepageComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AttendeepageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
