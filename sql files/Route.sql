

CREATE TABLE RouteTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  designatorPrefix        	VARCHAR(10),
  designatorSecondLetter    VARCHAR(10),
  designatorNumber			NUMERIC,
  multipleIdentifier        VARCHAR(30),
  type        				VARCHAR(30)
);

