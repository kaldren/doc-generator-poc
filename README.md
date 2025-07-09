User Perspective Flow for CDD Generation:
1. User Login and Authentication

Users log in using their own credentials; no external identity provider (e.g., KPMG’s provider) is requiredMeeting Notes_10 June.

2. Input and Selection

User specifies the following information through a web-based, chat-style interface:

Source system (e.g., Oracle EBS, JD Edwards, Lawson)Requirements Traceabili….

Target system (e.g., Oracle Cloud/HCM, SAP, Workday).

Industry (e.g., Healthcare, Financial Services, State and Local Government).

Object for conversion (e.g., suppliers, customers, invoices, balances).

3. Initial Document Analysis

The system analyzes source and target configurations:

Identifies relevant data fields, schema, and configurationsRequirements Traceabili….

Analyzes custom settings, relationships, and constraints.

4. Field Mapping Generation

The system automatically generates initial mappings between source and target systemsRequirements Traceabili….

Validates mappings (field types, lengths, compatibility).

Allows manual adjustments and refinements based on user feedback.

5. Data Transformation

System identifies and documents data transformation rules required for converting values between source and target systems:

Applies transformation rules to the data.

Validates transformed data for accuracy and completenessRequirements Traceabili….

6. Automated CDD Generation

The system leverages Retrieval-Augmented Generation (RAG):

Uses indexed historical documents (e.g., past CDDs, compliance guidelines) to generate client-ready CDDs with proper formatting (including tables and diagrams)Meeting Notes_5 June.

Continuously updates corpus data with new projects.

7. Feedback and Refinement

Users can review the generated CDDs:

Provide feedback directly within the system.

Adjust mappings and transformation rules as necessary.

The system learns from feedback, enhancing the accuracy and quality of future document generationsMeeting Notes 5 June.

8. Approval Workflow

Generated CDD goes through a structured approval process:

Routed for internal review and client approval.

Incorporates feedback before finalizingRequirements Traceabili….

9. Document Storage and Versioning

Final approved CDDs are stored in a secure, centralized SharePoint repository:

Version control implemented to track and revert document changes.

Robust document retrieval system allowing search and filteringRequirements Traceabili….

10. Deployment and Hosting

The entire system is containerized and deployed within the client’s environment (Azure-based Docker solution) ensuring data never leaves the client’s infrastructure, addressing security and compliance concernsMeeting Notes_10 June.