

CREATE TABLE StandardLevelColumnTimeSlice
(
  gmlIdentifier     VARCHAR(70) NOT NULL PRIMARY KEY,
  codeSpace        	VARCHAR(20),
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  series        	VARCHAR(70),
  standardICAO    	VARCHAR(10),
);

