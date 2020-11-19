


CREATE TABLE AirportHeliportExtension
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  defaultTaxiTime        NUMERIC,
  defaultTaxiTimeUOM        VARCHAR(10)
);

CREATE TABLE AirTrafficManagementService
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  codeSpace			VARCHAR(10),
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  serviceProvider	uuid
);

CREATE TABLE AirTrafficManagementService_ClientAirspace
(
  id             	INTEGER DEFAULT nextval('auto_id_point'),
  service_pk     	uuid REFERENCES AirTrafficManagementService (gmlIdentifier) ON UPDATE CASCADE,
  clientAirspace    uuid,
  CONSTRAINT service_client_pk    PRIMARY KEY (id, service_pk)
);

CREATE TABLE ClientRoute
(
  id             				INTEGER DEFAULT nextval('auto_id_point'),
  service_pk     				uuid REFERENCES AirTrafficManagementService (gmlIdentifier) ON UPDATE CASCADE,
  start_fixDesignatedPoint    	uuid,
  referencedRoute    			uuid,
  start_fixDesignatedPoint    	uuid,
  CONSTRAINT service_client_pk    PRIMARY KEY (id, service_pk)
);

