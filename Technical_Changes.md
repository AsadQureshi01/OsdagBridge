# OsdagBridge Report Generator Refactoring

## Overview

The report generator has been reorganized to produce clearer, more consistent PDF reports from OsdagBridge design outputs. The changes add shared report styling, improve long-table behavior, separate load schedules, connect summary charts to report data, and improve drawing and quantity presentation.

## Refactoring and modifications

### Shared report presentation

- Added `styles.py` as the shared configuration for page geometry, colors, typography, table spacing and widths, headers and footers, and chart appearance.
- Added `tables.py` for long-table column sizing, repeated table headers, continued-table labels, row spacing, and keeping related rows together across page breaks.
- Updated the report generator to use the shared style and table helpers when assembling the final LaTeX document.

### Tables and load schedules

- Updated the legacy long tables to retain their column specifications and repeat their headings on later pages.
- Refined the Chapter 2 component-detail tables and Chapter 3 load tables using shared column layouts.
- Split vehicle live loads and footway loads into separate tables, with explicit units and the selected vehicle cases from the Loading inputs.
- Made vehicle selection parsing handle Boolean and Yes/No values explicitly.
- Updated the Chapter 7 bill of materials to use a more readable five-column layout.

### Design and quantity charts

- Added `charts.py` for report-ready Matplotlib charts generated with the non-interactive Agg backend.
- Connected the Chapter 5 design summary to utilization-ratio data for girders, deck slab, cross bracing, and end diaphragms. The charts show a UR = 1.0 reference line.
- Connected Chapter 7 quantity data to charts for structural steel quantities and concrete versus reinforcement quantities.
- Added report-payload collection for the design checks and quantities used to create the charts.

### Drawings and quantity calculations

- Updated Chapter 6 to include captured CAD images with captions and labels, and to arrange available component views together.
- Improved CAD image capture by allowing the viewport to repaint before export, validating the exported PNG, and using a Qt viewport capture as a fallback.
- Extended bill-of-quantities calculations to include cross-bracing steel and geometry-based end-diaphragm quantities when the required inputs are available.
- Updated the IRC 6 braking-force helper to accumulate contributions according to the configured traffic-lane count.

## Centralized formatting structure

`src/osdagbridge/core/reports/styles.py` is the central presentation configuration. It defines document geometry, the color palette, table dimensions and spacing, page headers and footers, heading styles, and figure and chart formatting. `tables.py` and `charts.py` consume this shared configuration, while the report generator and chapter modules use the shared layouts and helpers where applicable. This keeps report-wide styling decisions together and reduces duplicated formatting rules.

## Files modified

- `src/osdagbridge/core/reports/styles.py` — shared presentation settings and LaTeX style builders.
- `src/osdagbridge/core/reports/tables.py` — long-table formatting and repeated-header helpers.
- `src/osdagbridge/core/reports/charts.py` — utilization and material quantity charts.
- `src/osdagbridge/core/reports/report_generator.py` — report-data collection, chart generation, and final LaTeX assembly.
- `src/osdagbridge/core/reports/chap2.py` — component detail tables and shared table layouts.
- `src/osdagbridge/core/reports/chap3.py` — vehicle and footway load tables.
- `src/osdagbridge/core/reports/chap5.py` — design summary charts and report layout.
- `src/osdagbridge/core/reports/chap6.py` — CAD drawing figures and component-view layout.
- `src/osdagbridge/core/reports/chap7.py` — bill of materials and quantity charts.
- `src/osdagbridge/core/reports/executive_summary.py` — design outcome and project summary presentation.
- `src/osdagbridge/core/boq/boq_generator.py` — material quantity aggregation.
- `src/osdagbridge/core/utils/codes/irc6_2017.py` — lane-based braking-force calculation helper.
- `src/osdagbridge/desktop/ui/cad_3d.py` — CAD viewport image capture for report figures.

## Report-generation rationale

Long-table helpers keep headings identifiable on every page and give tables a consistent layout. Central style settings make report-wide appearance easier to maintain. Charts are built from the structured report data so the visual summaries correspond to the values presented in the report tables. CAD images are captured at report-generation time and included as captioned figures.
