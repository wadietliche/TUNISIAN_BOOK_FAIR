import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SignupAtuthorComponent } from './signup-atuthor.component';

describe('SignupAtuthorComponent', () => {
  let component: SignupAtuthorComponent;
  let fixture: ComponentFixture<SignupAtuthorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SignupAtuthorComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SignupAtuthorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
