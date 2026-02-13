Use Case 2 – AI Powered Knowledge Chatbot

Overview

This document summarizes Use Case 2 from the provided PDF and structures it into a clean, reusable Markdown format suitable as a foundation for project development.

The objective of this use case is to build a secure, low‑cost, AI-powered knowledge chatbot that assists internal banking operations teams by providing fast, accurate, context-aware access to policies, SOPs, product rules, and exception-handling guidelines.

1. Objective

Develop an AI-powered knowledge assistant that:

Provides context-aware responses to internal operations teams.

Retrieves information from existing enterprise knowledge sources (SharePoint, Confluence, network drives, emails, ticketing systems, policy libraries, etc.).

Reduces dependency on SMEs and accelerates onboarding.

Improves auditability and consistency of responses.

2. Current Challenges in Banking Operations

2.1 Information Fragmentation

SOPs, product guides, exception rules, and policies are scattered across multiple platforms: SharePoint, Confluence, emails, PDFs, legacy portals.

2.2 Policy Churn

Frequent updates to regulatory and internal policies.

Difficulty tracking the latest versions.

2.3 SME Bottlenecks

Heavy reliance on a few subject matter experts.

Delays in resolving operational queries.

2.4 Manual Search Fatigue

Keyword search fails due to:

Format inconsistencies

Terminology mismatch

PDF scans, tables, appendices

2.5 Audit & Compliance Gaps

Limited traceability of what guidance was used, when, and by whom.

2.6 Onboarding Inefficiency

New joiners take weeks to learn where and how to find information.

3. The Solution – AI-Powered Knowledge Chatbot

3.1 Core Capabilities

Context-aware responses with source citations.

RAG (Retrieval-Augmented Generation) architecture using:

On-prem orchestration

Vector search

Custom embeddings

Role-based access

3.2 Query Categorization

Users can select:

Specific domain/area

Generic knowledge base

Enables faster and more accurate retrieval.

3.3 Chat History Management

Maintains conversation history for contextual continuity.

3.4 Custom Embeddings & Retrieval

Vector database for document retrieval.

Embeddings for matching queries with relevant documents.

3.5 LLM Integration

Integrates with a custom LLM (via Citi-managed Stellar API).

Generates responses based on retrieved data.

Ensures informational-only responses (no automated actions).

4. Benefits

4.1 Operational Efficiency

30–50% reduction in time to find answers.

20–35% deflection of routine queries from SMEs.

4.2 Faster Onboarding

Reduces ramp-up time for new staff by 25–40%.

4.3 Improved Auditability

Standardized responses.

Traceable guidance usage.

4.4 Long-Term ROI

Reduced human intervention for L1 support.

Scalable across teams and domains.

5. Architecture Components

5.1 Data Sources

SharePoint

Confluence

Network drives

Emails

Ticketing systems (ServiceNow, Jira)

Policy libraries

5.2 AI/ML Components

Embedding models

Vector database

RAG pipeline

LLM (Stellar API)

5.3 Security & Access

On-prem orchestration

Role-based access control

6. Expected MVP Outcomes (12–16 Weeks)

Working chatbot with:

RAG-based retrieval

Domain selection

Source citations

Chat history

Integration with enterprise knowledge sources

Initial SME deflection and measurable time savings

7. Future Enhancements

Multi-language support

Advanced analytics on query patterns

Integration with workflow automation tools

Continuous learning from user interactions

8. Summary

Use Case 2 outlines a robust, scalable AI-powered knowledge assistant designed to transform internal banking operations. By centralizing knowledge retrieval, reducing SME dependency, and improving compliance traceability, this solution delivers significant operational and strategic value.

End of Document