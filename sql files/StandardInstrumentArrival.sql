

CREATE TABLE Availability
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  featureType        VARCHAR(80)
);

CREATE TABLE ProcedureAvailability
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  StandardInstrumentArrivalTimeSlice_pk     uuid REFERENCES StandardInstrumentArrivalTimeSlice (gmlIdentifier),
);

CREATE TABLE StandardInstrumentArrivalExtension
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point')
);

CREATE TABLE StandardInstrumentArrivalTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  featureTimeBegin 	DateType,
  featureTimeEnd 	DateType,
  instruction        VARCHAR(100),
  designator              VARCHAR(50),
  timeReference        	VARCHAR(30),
  day        			VARCHAR(30),
  startTime        		TIME,
  endTime        		TIME,
  status        	VARCHAR(40),
  airportHeliport	    	VARCHAR(70)
);

CREATE TABLE StandardInstrumentArrival_TerminalSegmentPoint
(
  id                			INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  StandardInstrumentArrivalTimeSlice_pk     uuid REFERENCES StandardInstrumentArrivalTimeSlice (gmlIdentifier),
  pointChoice_fixDesignatedPoint        	VARCHAR(70)
);


CREATE TABLE Availability_ProcedureAvailability
(
  id                			INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  StandardInstrumentArrivalTimeSlice_pk     uuid REFERENCES StandardInstrumentArrivalTimeSlice (gmlIdentifier),
  pointChoice_fixDesignatedPoint        	VARCHAR(70)
);