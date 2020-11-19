




CREATE TABLE DesignatedPointTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  codeSpace			VARCHAR(10),
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  type              CodeNavaidServiceType,
  designator        VARCHAR(40),
  name              TextNameType,
);

CREATE TABLE DesignatedPoint_PointUsage
(
  designatedpoint_pk     	uuid REFERENCES DesignatedPointTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  pointusage_pk     INTEGER REFERENCES PointUsage (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT designated_pointusage_pk    PRIMARY KEY (designatedpoint_pk, pointusage_pk)
);
