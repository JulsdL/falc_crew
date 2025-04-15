# Changelog

## [0.0.5] - 2025-04-15

## Added
- Implemented session-based isolation for file uploads and outputs using unique session IDs.
- Enhanced the document processing pipeline to support session-specific output directories.

## Changed
- Updated the document processing workflow to handle output files dynamically based on session context.

## [0.0.4] - 2025-04-14

## Added
- Introduced FalcDocxStructureTaggerTool and FalcDocxRewriterTool for tagging and rewriting .docx files.
- Enhanced functionality to update original Word documents with translated content while preserving layout.

## Changed
- Updated task configuration to support rewriting original documents instead of generating new ones.

## [0.0.3] - 2025-04-14

### Added
- Introduced functionality to scan text for icon placeholders and insert corresponding EVAM PNG images in Word documents.
- Updated icons.json with new company-defined icons and paths.
- Enhanced translation task to utilize icon placeholders instead of emojis.

### Changed

- Modified translation task instructions to prohibit the use of emojis and enforce the use of icon placeholders.
