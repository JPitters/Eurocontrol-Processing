

CREATE TABLE TrafficVolumeSetTimeSlice
(
  gmlIdentifier     	uuid NOT NULL PRIMARY KEY,
  validTimeBegin 		DateType,
  validTimeEnd 			DateType,
  interpretation 		TimesliceInterpretationType,
  tvSetId              	VARCHAR(40),
  tvSetName              	VARCHAR(60),
  TrafficVolumeActivation_pk     INTEGER REFERENCES TrafficVolumeActivation (id) ON UPDATE CASCADE,
);

CREATE TABLE TrafficVolumeSet_TrafficVolume
(
  id                			INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  trafficVolumeSetTimeSlice_pk     uuid REFERENCES TrafficVolumeSetTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  trafficVolumeID        				VARCHAR(70)
);
