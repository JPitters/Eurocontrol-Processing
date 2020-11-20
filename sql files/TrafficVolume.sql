CREATE TABLE TrafficVolumeActivation
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  timeReference        	VARCHAR(30),
  day        			VARCHAR(30),
  startTime        		TIME,
  endTime        		TIME,
  validTimeBegin 		DateType,
  validTimeEnd 			DateType
);

CREATE TABLE TrafficVolumeTimeSlice
(
  gmlIdentifier     	uuid NOT NULL PRIMARY KEY,
  validTimeBegin 		DateType,
  validTimeEnd 			DateType,
  interpretation 		TimesliceInterpretationType,
  tvId              	VARCHAR(30),
  referenceLocation        VARCHAR(70),
  TrafficVolumeActivation_pk     INTEGER REFERENCES TrafficVolumeActivation (id) ON UPDATE CASCADE,
);

CREATE TABLE TrafficVolume_LinkedFlow
(
  id                			INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  trafficVolumeTimeSlice_pk     uuid REFERENCES TrafficVolumeTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  role        					VARCHAR(20),
  theFlow        				VARCHAR(70)
);
