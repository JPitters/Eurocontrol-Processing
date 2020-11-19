

CREATE TABLE ReferenceLocationTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  category              			VARCHAR(30),
  referenceLocationId        		VARCHAR(30),
  locationChoice_airportHeliport    VARCHAR(70),
);

CREATE TABLE ReferenceLocation_associatedFlow
(
  referenceLocation_pk     	uuid REFERENCES ReferenceLocationTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  bridge_pk     			INTEGER DEFAULT nextval('auto_id_point'),
  associatedFlow        	VARCHAR(70)
  CONSTRAINT referenceLocation_bridge_pk    PRIMARY KEY (referenceLocation_pk, bridge_pk)
);