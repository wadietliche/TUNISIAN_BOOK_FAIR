import { TestBed } from '@angular/core/testing';

import { AttendeeServiceService } from './attendee-service.service';

describe('AttendeeServiceService', () => {
  let service: AttendeeServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AttendeeServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
