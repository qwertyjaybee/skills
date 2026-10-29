# Jira Task Description Automation (`/jira-description`)

An automated workflow for generating user-centric Jira Kanban task descriptions structured with **Description**, categorized **Requirements** (with exact quoted UI strings, button labels, and validation errors), and a 4-column **Permissions** table from codebase changes across the `ui/` and `api/` repositories.

---

## Features
- **Strictly User-Centric & Jargon-Free:** Completely strips out technical backend jargon (no database schema names, migrations, GraphQL query/mutation names).
- **Structured 3-Part Output Format:**
  1. **Description:** High-level narrative summarizing the feature or enhancement, how it functions end-to-end, and user value.
  2. **Requirements:** Detailed functional requirements grouped by capability areas, quoting exact UI strings, labels, options, validation constraints, and error/confirmation messages.
  3. **Permissions:** Explicit permission statement accompanied by a structured 4-column Markdown table (`Permission | Allows the user to | Where it applies | Default roles`).
- **SED vs. FRD Modes:**
  - **SED (System Enhancement):** Focuses on optimizations, streamlined workflows, and enhanced usability of existing features (`# Enhancement Documentation`).
  - **FRD (Functional Requirement / New Feature):** Enforces a **strict pure-creation rule** (zero "removed", "deleted", or "deprecated" phrases; frames all changes constructively as new capabilities or version 2 deliverables; `# Feature Documentation`).
- **Multi-Repository Git & Code Inspection:** Inspects commits, templates, and reactive forms across `api/` and `ui/` to extract exact UI labels, error messages, and permission keys.
- **Interactive Approval Gate:** Previews the exact description in an interactive draft artifact (`RequestFeedback: true`) so you can review, comment, and click **Proceed** before anything is uploaded.
- **Automated Python Jira Upload:** Upon approval (clicking **Proceed**), executes `scripts/upload_to_jira.py` to upload the approved description directly to Jira via the Jira REST API.

---

## Usage

Invoke the automation in Antigravity using:

```text
/jira-description <task_name_or_link> <FRD|SED>
```

### Examples:
- **System Enhancement (SED):**
  ```text
  /jira-description AIRI-284 | Membership UI Redesign to Draggable Hierarchy like Design SED
  ```
- **New Feature / Pure Creation (FRD):**
  ```text
  /jira-description https://your-company.atlassian.net/browse/AIRI-284 FRD
  ```

---

## Jira Upload Configuration

Configure your Jira credentials in one of two ways:

### Option 1: Config File (Recommended)
Copy the example configuration:
```bash
cp /opt/core-aairi/.agents/automation/jira-description/jira_config.example.json /opt/core-aairi/.agents/automation/jira-description/jira_config.json
```
Edit `/opt/core-aairi/.agents/automation/jira-description/jira_config.json`:
```json
{
  "jira_url": "https://your-company.atlassian.net",
  "jira_email": "your-email@company.com",
  "jira_api_token": "your_jira_api_token"
}
```
*(Or place it at `~/.gemini/config/jira.json` or `~/.jira_config.json`)*

### Option 2: Environment Variables
```bash
export JIRA_URL="https://your-company.atlassian.net"
export JIRA_EMAIL="your-email@company.com"
export JIRA_API_TOKEN="your_jira_api_token"
```

*(Generate a Jira API token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens))*
*(Generate an API token at [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens))*
