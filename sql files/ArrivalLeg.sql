

CREATE TABLE ArrivalLeg
(
  gmlIdentifier     	uuid NOT NULL PRIMARY KEY,
  codeSpace				VARCHAR(10),
  validTimeBegin 		DateType,
  validTimeEnd 			DateType,
  interpretation 		TimesliceInterpretationType,
  upperLimitAltitude 	ValDistanceVerticalType,
  upperLimitReference 	ValDistanceVerticalType,
  lowerLimitAltitude 	ValDistanceVerticalType,
  lowerLimitReference 	ValDistanceVerticalType,
  startPoint	    	VARCHAR(70),
  startPointType    	VARCHAR(40),
  endPoint		    	VARCHAR(70),
  endPointType    		VARCHAR(40),
  arrival				VARCHAR(70)
);

