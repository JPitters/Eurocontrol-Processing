

CREATE TABLE DistanceIndication
(
  gmlIdentifier     	VARCHAR(70) NOT NULL PRIMARY KEY,
  codeSpace				VARCHAR(10),
  validTimeBegin 		DateType,
  validTimeEnd 			DateType,
  interpretation 		TimesliceInterpretationType,
  distance 				ValDistanceType,
  fix	    			VARCHAR(70),
  pointChoice_navaidSystem				VARCHAR(70)
);

