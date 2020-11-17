CREATE TABLE AirportHeliportAvailability
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  timeReference        	VARCHAR(10),
  startDate        		VARCHAR(10),
  endDate        		VARCHAR(10),
  day        			VARCHAR(10),
  startTime        		TIME,
  endTime        		TIME,
  logicalOperator       VARCHAR(20),
  flightRule        	VARCHAR(20)
);

CREATE TABLE AirportHeliportExtension
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  defaultTaxiTime        NUMERIC,
  defaultTaxiTimeUOM        VARCHAR(10)
);

CREATE TABLE AirportHeliportSet
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  airportHeliportSetID        VARCHAR(10)
);

CREATE TABLE AirportHeliportSetPattern
(
  id             INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  pattern        VARCHAR(5)
);