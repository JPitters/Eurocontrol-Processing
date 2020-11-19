

CREATE TABLE OrganisationAuthorityTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  name              TextNameType,
  designator        VARCHAR(40),
  type              VARCHAR(50),
);

