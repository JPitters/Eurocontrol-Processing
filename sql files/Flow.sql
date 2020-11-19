

CREATE TABLE FlowTimeSlice
(
  gmlIdentifier     	uuid NOT NULL PRIMARY KEY,
  codeSpace				VARCHAR(10),
  validTimeBegin 		DateType,
  validTimeEnd 			DateType,
  interpretation 		TimesliceInterpretationType,
  flowName	    		VARCHAR(70),
  flowId    			VARCHAR(20)
);


CREATE TABLE FlowLocationElement
(
  id                INTEGER PRIMARY KEY DEFAULT nextval('auto_id_point'),
  index				INTEGER,
  flowElementType		    VARCHAR(30),
  referencedElementType		VARCHAR(30),
  referencedElement		    VARCHAR(70)
);

CREATE TABLE Flow_FlowLocationElement
(
  flow_pk     	uuid REFERENCES FlowTimeSlice (gmlIdentifier) ON UPDATE CASCADE,
  flowLocationElement_pk     INTEGER REFERENCES FlowLocationElement (id) ON UPDATE CASCADE,
  pattern        VARCHAR(5)
  CONSTRAINT flow_flowLocationElement_pk    PRIMARY KEY (flow_pk, flowLocationElement_pk)
);