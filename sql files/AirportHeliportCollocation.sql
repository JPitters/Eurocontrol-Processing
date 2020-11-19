
CREATE TABLE AirportHeliportCollocation
(
  gmlIdentifier     VARCHAR(70) NOT NULL PRIMARY KEY,
  codeSpace			VARCHAR(10),
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  hostAirport       VARCHAR(70),
  dependentAirport  VARCHAR(70)
);