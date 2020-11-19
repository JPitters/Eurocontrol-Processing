

CREATE TABLE SpecialDateTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  type        		VARCHAR(30),
  dateDay        	VARCHAR(10),
  dateYear    		VARCHAR(10),
  name        		TextNameType,
  authority        	VARCHAR(70)
);

