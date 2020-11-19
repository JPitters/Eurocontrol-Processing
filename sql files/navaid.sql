CREATE SEQUENCE auto_id_point;

CREATE DOMAIN latitude AS DECIMAL(17, 15);

CREATE DOMAIN longitude AS DECIMAL(18, 15);

CREATE DOMAIN UomDistanceType AS VARCHAR(60)
CHECK (VALUE ~ '(NM|KM|M|FT|MI|CM|OTHER: [A-Z]{0,30})');

CREATE DOMAIN UomDistanceVerticalType AS VARCHAR(60)
CHECK (VALUE ~ '(FT|M|FL|SM|OTHER: [A-Z]{0,30})');

CREATE TYPE ValDistanceSignedType AS (
  value DECIMAL(30, 20),
  unit  UomDistanceType
);

CREATE DOMAIN CodeVerticalDatumType AS VARCHAR(60)
CHECK (VALUE ~ '(EMG_96|AHD|NAVD88|OTHER: [A-Z]{0,30})');

CREATE DOMAIN ValDistanceVerticalBaseType AS DECIMAL(12, 4);
CREATE DOMAIN ValDistanceVerticalBaseTypeNonNumeric AS VARCHAR(40) CHECK (VALUE ~
                                                                          '((UNL|GND|FLOOR|CEILING)|OTHER: [A-Z]{0,30})');
CREATE TYPE ValDistanceVerticalType AS (
  value      ValDistanceVerticalBaseType,
  nonNumeric ValDistanceVerticalBaseTypeNonNumeric,
  unit       UomDistanceVerticalType
);
CREATE DOMAIN ValMagneticVariationType AS DECIMAL(13, 10)
CHECK (VALUE >= -180 AND VALUE <= 180);

CREATE DOMAIN ValDistanceBaseType AS DECIMAL(30, 20)
CHECK (VALUE >= 0);

CREATE TYPE ValDistanceType AS (
  value ValDistanceBaseType,
  unit  UomDistanceType
);


CREATE SEQUENCE auto_id_timeslice;

CREATE DOMAIN DateType AS DATE;

CREATE DOMAIN TimesliceInterpretationType AS VARCHAR(40)
    CHECK (VALUE ~ 'BASELINE|PERMDELTA|SNAPSHOT|TEMPDELTA|OTHER: [A-Z]{0,30}');

CREATE DOMAIN NoNumberType AS INTEGER;

CREATE TABLE TimeSlice
(
  id INTEGER PRIMARY KEY DEFAULT nextval('auto_id_timeslice'),
  validTimeBegin DateType,
  validTimeEnd DateType,
  interpretation TimesliceInterpretationType,
  sequenceNumber NoNumberType,
  correctionNumber NoNumberType
);

CREATE DOMAIN TextNameType AS VARCHAR(60);

CREATE DOMAIN CodeNavaidServiceType AS VARCHAR(40)
CHECK (VALUE ~
       '(VOR|DME|NDB|TACAN|MKR|ILS|ILS_DME|MLS|MLS_DME|VORTAC|VOR_DME|NDB_DME|TLS|LOC|LOC_DME|NDB_MKR|DF|OTHER: [A-Z]{0,30})');

CREATE DOMAIN CodeNavaidDesignatorType AS VARCHAR(4)
CHECK (VALUE ~ '([A-Z]|\d)*');

CREATE DOMAIN CodeNavaidPurposeType AS VARCHAR(40)
CHECK (VALUE ~ '(TERMINAL|ENROUTE|ALL|OTHER: [A-Z]{0,30})');

CREATE DOMAIN CodeSignalPerformanceILSType AS VARCHAR(40)
CHECK (VALUE ~ '(I|II|III|OTHER: [A-Z]{0,30})');

CREATE DOMAIN CodeCourseQualityILSType AS VARCHAR(40)
CHECK (VALUE ~ '(A|B|C|D|E|T|OTHER: [A-Z]{0,30})');

CREATE DOMAIN CodeIntegrityLevelILSType AS VARCHAR(40)
CHECK (VALUE ~ '(1|2|3|4|OTHER: [A-Z]{0,30})');

CREATE DOMAIN CodeYesNoType AS VARCHAR(60)
CHECK (VALUE ~ '(YES|NO|OTHER: [A-Z]{0,30})');




CREATE TABLE Point
(
  id                 INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  latitude           latitude,
  longitude          longitude,
  srid               INTEGER REFERENCES spatial_ref_sys (srid),
  horizontalAccuracy ValDistanceType,
  magneticVariation  ValMagneticVariationType,
  geom               GEOMETRY(POINT, 4326)
);

CREATE TABLE ElevatedPoint
(
  id               INTEGER PRIMARY KEY REFERENCES Point (id) ON DELETE CASCADE ON UPDATE CASCADE,
  elevation        ValDistanceVerticalType,
  geoidUndulation  ValDistanceSignedType,
  verticalDatum    CodeVerticalDatumType,
  verticalAccuracy ValDistanceType
);


CREATE TABLE NavaidExtension
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  commomSystemUsage 	CodeYesNoType,
  publicUse        		CodeYesNoType,
  navaidClass        	VARCHAR(40),
  artccIdForHighAltitude        VARCHAR(40),
  artccNameForHighAltitude        VARCHAR(40),
  artccIdForLowAltitude        VARCHAR(40),
  surveyAccuracy        NUMERIC,
  monitoringCategory    NUMERIC,
  notamAccountabilityCode        VARCHAR(40),
  navaidStatus        	VARCHAR(40),
  pitchFlag        		CodeYesNoType,
  catchFlag        		CodeYesNoType,
  suaAtcaaFlag        	CodeYesNoType,
  stateName        		VARCHAR(40),
  faaRegionCode        	VARCHAR(40),
  cityName        		VARCHAR(40),
  administrativeArea    VARCHAR(40)
);

CREATE TABLE NavaidTimeSlice
(
  gmlIdentifier     uuid NOT NULL PRIMARY KEY,
  validTimeBegin 	DateType,
  validTimeEnd 		DateType,
  interpretation 	TimesliceInterpretationType,
  type              CodeNavaidServiceType,
  designator        VARCHAR(40),
  name              TextNameType,
  flightChecked     CodeYesNoType,
  purpose           CodeNavaidPurposeType,
  signalPerformance CodeSignalPerformanceILSType,
  courseQuality     CodeCourseQualityILSType,
  integrityLevel    CodeIntegrityLevelILSType,
  idNavaidExtension   INTEGER REFERENCES NavaidExtension (id) ON DELETE CASCADE ON UPDATE CASCADE,
  idElevatedPoint   INTEGER REFERENCES ElevatedPoint (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE AnnotationNote
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  propertyName      VARCHAR(40),
  note        		TEXT
);

CREATE TABLE NavaidTimeSlice_AnnotationNote
(
  navaid_pk     	uuid REFERENCES NavaidTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  annotation_pk     INTEGER REFERENCES AnnotationNote (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT navaid_annotation_pk    PRIMARY KEY (navaid_pk, annotation_pk)
);

CREATE TABLE AirspaceBorderCrossingObject
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  enteredAirspace      VARCHAR(60),
  exitedAirspace      VARCHAR(60)
);

CREATE TABLE PointUsage
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  timeReference        	VARCHAR(30),
  day        			VARCHAR(30),
  startTime        		TIME,
  endTime        		TIME,
  validTimeBegin        DateType,
  validTimeEnd        	DateType,
  role        			VARCHAR(30),
  refernceAirspace  	VARCHAR(60),
  refernceAirportHeliport  VARCHAR(60),
  refernceAirportHeliportSet  VARCHAR(60),
  refernceBorderID  	INTEGER REFERENCES AirspaceBorderCrossingObject (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE NavaidTimeSlice_PointUsage
(
  navaid_pk     	uuid REFERENCES NavaidTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  pointusage_pk     INTEGER REFERENCES PointUsage (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT navaid_pointusage_pk    PRIMARY KEY (navaid_pk, pointusage_pk)
);


