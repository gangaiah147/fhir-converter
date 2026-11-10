# Feature Specification: Baseline FHIR Converter

**Feature Branch**: `001-baseline-fhir-converter`

**Created**: 2026-11-06

**Status**: Draft

**Input**: User description: "Create a baseline specification of the existing FHIR converter so future features are specified against current behavior."

> This is a **baseline** spec. It records what the converter already does today, so later feature specs can reference it and so regressions can be measured against it. It does not propose new behavior.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Convert a C-CDA document to FHIR R4 (Priority: P1)

A data engineer has a C-CDA clinical document (for example a Continuity of Care Document or a Discharge Summary) and needs the same clinical content as a FHIR R4 Bundle so it can be loaded into a FHIR-based system. They pick the document type and receive a FHIR R4 JSON Bundle.

**Why this priority**: C-CDA to FHIR R4 is the primary reason the product exists. Without it there is no product.

**Independent Test**: Convert a sample C-CDA document with the matching document-type template and confirm the output is a well-formed FHIR R4 Bundle containing resources for the document's sections.

**Acceptance Scenarios**:

1. **Given** a valid C-CDA CCD document, **When** the user converts it with the CCD template, **Then** a FHIR R4 Bundle is produced as JSON.
2. **Given** a valid C-CDA document of a supported type (CCD, Consultation Note, Discharge Summary, History and Physical, Operative Note, Procedure Note, Progress Note, Referral Note, Transfer Summary), **When** the user converts it with the matching template, **Then** a FHIR R4 Bundle is produced.
3. **Given** a C-CDA document, **When** the user requests a template name that does not exist, **Then** the conversion fails with an error that identifies the failure, and no partial output is left behind.

---

### User Story 2 - Convert a FHIR STU3 resource to FHIR R4 (Priority: P2)

A data engineer holds FHIR STU3 JSON resources from an older system and needs them upgraded to FHIR R4 without hand-mapping each resource type.

**Why this priority**: It is the second supported conversion path and serves teams migrating off STU3, but fewer users depend on it than on C-CDA.

**Independent Test**: Convert a sample STU3 resource (for example a Patient or an AllergyIntolerance) and confirm the output is the R4 form of that resource.

**Acceptance Scenarios**:

1. **Given** a valid STU3 resource of a supported type, **When** the user converts it with the matching resource template, **Then** the R4 representation of that resource is produced as JSON.
2. **Given** an STU3 Bundle, **When** the user converts it with the Bundle template, **Then** each contained resource is converted to R4.

---

### User Story 3 - Batch-convert a directory from the command line (Priority: P2)

An operator needs to convert many files at once without writing code. They point the command-line tool at an input file or folder, an output folder, a source format, and a template, and get one output file per input file.

**Why this priority**: Batch conversion is how most real workloads run, and the command line makes the product usable without programming.

**Independent Test**: Run the command line against a folder of sample documents and confirm one output file is written per input file, with a success or failure summary at the end.

**Acceptance Scenarios**:

1. **Given** a single input file, **When** the operator converts it to an output folder, **Then** one output file with the same base name and a `.json` extension is written to that folder.
2. **Given** an input folder with nested subfolders, **When** the operator converts it, **Then** outputs mirror the input subfolder structure by default.
3. **Given** an input folder with nested subfolders, **When** the operator asks to flatten output, **Then** all outputs are written to the root of the output folder.
4. **Given** a folder where one file is malformed, **When** the operator converts it with default settings, **Then** the run stops and reports failure.
5. **Given** a folder where one file is malformed, **When** the operator converts it with "continue on error", **Then** the remaining files are still converted and the bad file is reported.
6. **Given** any run, **When** it finishes, **Then** a summary shows success or failure, total time, finish time, and memory used.

---

### User Story 4 - Use custom templates alongside the bundled ones (Priority: P3)

An integration developer needs to change how certain sections are mapped (or add a new document type) without forking the product. They supply their own template folder, and their templates can reuse the bundled templates by name.

**Why this priority**: Most organizations need mapping tweaks, but they can start with the bundled templates.

**Independent Test**: Provide a template folder containing one new document-type template that includes a bundled section template, convert a sample document with it, and confirm both the custom and bundled parts appear in the output.

**Acceptance Scenarios**:

1. **Given** a user template folder, **When** the user converts with a template name that exists only in that folder, **Then** the user template is used.
2. **Given** a user template that references a bundled template by its conventional name, **When** it is rendered, **Then** the bundled template is found and applied without changes to the user template.

---

### User Story 5 - Embed conversion in a data pipeline (Priority: P3)

A developer builds conversion into an existing data pipeline. They call the converter as a library, passing text or a readable stream, and receive either the FHIR result as a string, as structured data, or written to a stream they provide.

**Why this priority**: It is the main way the product is used in production pipelines, but it relies on the same conversion engine as Stories 1 and 2.

**Independent Test**: From a short program, convert a sample document and receive the result in each of the three output forms.

**Acceptance Scenarios**:

1. **Given** document text, **When** the developer asks for a string result, **Then** FHIR JSON text is returned.
2. **Given** a readable stream, **When** the developer asks for structured data, **Then** a key/value structure of the FHIR result is returned.
3. **Given** an output stream, **When** the developer converts to it, **Then** FHIR JSON is written to that stream.
4. **Given** a conversion failure, **When** the developer supplies their own error handler for batch operations, **Then** that handler decides whether to stop or continue.

### Edge Cases

- **Empty input**: an empty C-CDA or JSON file must not crash the batch. The run either produces an empty result or a reported error, depending on the error setting.
- **Malformed input**: XML or JSON that cannot be parsed raises a conversion error that names the file.
- **Failed output write**: if conversion fails mid-write, the partial output file is deleted.
- **Empty output subfolders**: when output mirrors input structure, subfolders left empty after a run are removed.
- **Both file and folder given**: when both an input file and an input folder are supplied, the folder takes precedence.
- **Templates ported from the original C# converter**: they may fail until tag parameters are comma-separated and snippet variables are named explicitly. This is a known limitation, not a defect.
- **C# date format strings in templates**: supported to a documented extent. Formats outside that set are not guaranteed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST convert C-CDA documents to FHIR R4 JSON for these document types: CCD, Consultation Note, Discharge Summary, History and Physical, Operative Note, Procedure Note, Progress Note, Referral Note, Transfer Summary.
- **FR-002**: System MUST convert FHIR STU3 JSON resources, including Bundles, to FHIR R4 JSON using per-resource-type templates.
- **FR-003**: System MUST let callers choose the template by name for every conversion.
- **FR-004**: System MUST accept input as text or as a readable stream, with a configurable character encoding (default UTF-8).
- **FR-005**: System MUST return results as a JSON string, as structured data, or written to a caller-supplied output stream.
- **FR-006**: System MUST provide a command-line tool that converts a single file or an entire folder into an output folder.
- **FR-007**: The command-line tool MUST accept the source format (C-CDA or STU3), the template name, an optional user template folder, an option to continue on errors, and an option to flatten nested output.
- **FR-008**: Batch conversion MUST write one output file per input file, using the input base name with a `.json` extension.
- **FR-009**: Batch conversion MUST stop on the first error by default, and MUST support a caller-chosen error policy (for example continue and report).
- **FR-010**: System MUST delete any partially written output file when a conversion fails.
- **FR-011**: System MUST report every conversion failure as a conversion error that identifies the failing input.
- **FR-012**: The command-line tool MUST print a run summary (success or failure, total time, finish time, memory used) and exit with a non-zero status on failure.
- **FR-013**: System MUST load bundled templates by default and MUST allow a user template folder whose templates can reference bundled templates by their conventional names.
- **FR-014**: System MUST support templates written for the original C# FHIR-Converter, subject to the documented syntax differences (comma-separated parameters, named snippet variables, a subset of C# date formats).
- **FR-015**: Supported runtime versions MUST match what the product declares and tests against. Decision (2026-11-10): keep declared support for Python 3.8 and later; the command-line tool was fixed to run on 3.8 to 3.10 in [002-cli-python-compat](../002-cli-python-compat/spec.md) (Jira SCRUM-5).

### Key Entities

- **Source document**: the input to convert. Either a C-CDA XML clinical document or a FHIR STU3 JSON resource. May contain protected health information.
- **Source format**: which kind of source document is being converted (C-CDA or STU3). Determines the default template set and how the input is parsed.
- **Template**: a named mapping that turns a parsed source document into FHIR R4. Templates are organized by document or resource type and can include shared sub-templates (sections, data types, references, value sets).
- **Template set**: a collection of templates. The bundled set ships with the product. A user set can add or override templates and can reuse bundled ones by name.
- **FHIR R4 output**: the converted JSON result, usually a Bundle for C-CDA input or a single resource for STU3 input.
- **Conversion error**: the failure record for one input, identifying the input and the cause.
- **Run summary**: the command-line outcome report (success or failure, timing, memory).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the bundled sample documents for each supported C-CDA document type convert without error using the matching template.
- **SC-002**: A typical C-CDA clinical document converts in under 0.1 seconds on developer-class hardware. (Source: the README benchmark reports averages of about 0.008 to 0.020 seconds per document on a 2021 laptop. Re-measure on your own hardware before treating this as a target.)
- **SC-003**: In a batch run with "continue on error", one malformed file out of N still yields N-1 converted outputs and exactly one reported failure.
- **SC-004**: After any failed conversion, zero partial output files remain in the output folder.
- **SC-005**: An operator with no programming background can convert a folder of documents with a single command after reading the usage section of the README.
- **SC-006**: A user-defined template that reuses bundled section templates works with no edits to the bundled templates.

## Assumptions

- Primary users are data engineers and integration developers working in data pipelines, plus operators running batch conversions.
- Conversion runs locally. The product does not send data to any network service.
- Input files contain clinical data that may include PHI. Handling, storage, and access control of that data are the caller's responsibility. The product itself does not log or persist document contents beyond the requested output.
- Output is FHIR R4 only. JSON-to-FHIR, HL7v2-to-FHIR, and FHIR-to-HL7v2 are out of scope for this baseline.
- The bundled C-CDA templates are a derivative of the Microsoft FHIR-Converter templates, with the enhancements and fixes this project has already made.
- Clinical correctness of the mapping is judged against the upstream FHIR-Converter templates. This spec does not claim clinical validation of the output, and the output is not a substitute for professional clinical or compliance review.
