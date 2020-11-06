# Eurocontrol-Processing
An application to process Eurocontrol AIXM 5.1.1 data and push it into a database.

## Datasets Used

Datasets will be downloaded to the Dataset directory specified.
On first run, the most recent Complete AIXM dataset will be downloaded
for the current AIRAC cycle (28 days). Incremental AIXM datasets will then be downloaded
at every full hour.

> **WARNING**: Complete AIXM Dataset download will require at least 800 MB of Disk space due to file unzip

- File Path will be `<PERSISTENT_DATASET_DIRECTORY>/<DATE>/Complete_<UpdateID>_<AiracID>/*.BASELINE`
  for Complete AIXM files. Files are unzipped upon download completion.
- File Path will be `<PERSISTENT_DATASET_DIRECTORY>/<DATE>/Incremental_<UpdateID>_<AiracID>/*.BASELINE`
  for Incremental AIXM files. Files are unzipped upon download completion. It should be noted that it is
  also possible to retrieve `PERMDELTA` files instead of `BASELINE` files during Incremental dataset download.
- Files can be one of the following AIXM datasets (`BASELINE` or `PERMDELTA`)
  - AirportHeliport.BASELINE
  - AirportHeliportCollocation.BASELINE
  - AirportHeliportSet.BASELINE
  - Airspace.BASELINE
  - AirTrafficManagementService.BASELINE
  - AngleIndication.BASELINE
  - ApproachLeg.BASELINE
  - ArrivalLeg.BASELINE
  - DepartureLeg.BASELINE
  - DesignatedPoint.BASELINE
  - DistanceIndication.BASELINE
  - FlightRestriction.BASELINE
  - Flow.BASELINE
  - InstrumentApproachProcedure.BASELINE
  - Navaid.BASELINE
  - OrganisationAuthority.BASELINE
  - ReferenceLocation.BASELINE
  - Route.BASELINE
  - RouteSegment.BASELINE
  - SpecialDate.BASELINE
  - StandardInstrumentArrival.BASELINE
  - StandardInstrumentDeparture.BASELINE
  - StandardLevelColumn.BASELINE
  - StandardLevelTable.BASELINE
  - TrafficVolume.BASELINE
  - TrafficVolumeSet.BASELINE
  - Unit.BASELINE
