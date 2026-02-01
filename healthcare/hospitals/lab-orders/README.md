# Lab Orders

Laboratory test ordering and results.

## Overview

This model manages laboratory orders including order entry, specimen
collection, processing, and result reporting.

## Key Entities

- **Order** - Test request
- **Specimen** - Sample collected
- **Result** - Test outcome

## Commands

- `PlaceOrder` - Request test
- `CollectSpecimen` - Obtain sample
- `ProcessSpecimen` - Run test
- `ReportResult` - Return findings
- `AcknowledgeResult` - Confirm receipt

## Events

- `OrderPlaced` - Test requested
- `SpecimenCollected` - Sample obtained
- `SpecimenProcessed` - Test run
- `ResultReported` - Findings returned
- `ResultAcknowledged` - Receipt confirmed

## Integration Points

- Order entry systems
- Lab instruments
- EHR systems
- Critical value alerts