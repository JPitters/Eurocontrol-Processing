

CREATE TABLE Unit
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  name        		TextNameType,
  type        		VARCHAR(50),
  desginator        VARCHAR(50)
);

