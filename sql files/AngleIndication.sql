


CREATE TABLE AngleIndicationTimeSlice
(
  gmlIdentifier     VARCHAR(70) NOT NULL PRIMARY KEY,
  codeSpace			VARCHAR(10),
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  angle				NUMERIC,
  angleType         VARCHAR(20),
  designator        VARCHAR(40),
  fix				VARCHAR(60),
  pointChoice_NavaidSystem		VARCHAR(60)
);


