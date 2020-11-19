

CREATE TABLE InstrumentApproachProcedureTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  type              VARCHAR(50),
  designator        VARCHAR(40),
  name              TextNameType,
  timeReference        	VARCHAR(30),
  day        			VARCHAR(30),
  startTime        		TIME,
  endTime        		TIME,
  status        	VARCHAR(40),
  airportHeliport	    	VARCHAR(70)
);

