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

CREATE TABLE Navaid
(
  gmlIdentifier     uuid PRIMARY KEY DEFAULT uuid_generate_v4 (),
  _transasID                  VARCHAR(20)
);

CREATE TABLE NavaidTimeSlice
(
  idTimeSlice       INTEGER NOT NULL PRIMARY KEY REFERENCES TimeSlice (id),
  gmlIdentifier     uuid REFERENCES Navaid (gmlIdentifier),
  type              CodeNavaidServiceType,
  designator        CodeNavaidDesignatorType,
  name              TextNameType,
  flightChecked     CodeYesNoType,
  purpose           CodeNavaidPurposeType,
  signalPerformance CodeSignalPerformanceILSType,
  courseQuality     CodeCourseQualityILSType,
  integrityLevel    CodeIntegrityLevelILSType,
  idElevatedPoint   INTEGER REFERENCES ElevatedPoint (id) ON DELETE CASCADE ON UPDATE CASCADE
);

