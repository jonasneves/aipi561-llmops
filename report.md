# Week 5 — Evaluation Report

TechCorp Knowledge Assistant · 10 test queries against `gemini-2.5-flash`.

## Cost summary

| Metric | Value |
|---|---|
| Total queries | 10 |
| Total tokens | 13,777 |
| **Total cost** | **$0.001189** |
| Avg cost / query | $0.000119 |
| Avg tokens / query | 1,378 |

Rates (rubric): input $0.075 / 1M, output $0.30 / 1M tokens.

## Per-query results

| # | Role | Query | Tools called | Tokens | Cost |
|---|---|---|---|---|---|
| 1 | engineer | What is the PTO policy, and how many days do managers get? | policy_search | 1574 | $0.000141 |
| 2 | engineer | What's the expense approval limit for a manager? | expense_query | 633 | $0.000052 |
| 3 | manager | Look up the employee with ID 1 — name, title, and department. | employee_lookup | 872 | $0.000070 |
| 4 | engineer | What does the travel policy say about international flight limits? | policy_search | 1449 | $0.000118 |
| 5 | manager | Find an employee whose name contains 'Smith'. | employee_lookup | 1874 | $0.000169 |
| 6 | manager | What's the approval limit for a director, and does policy require a receipt for a $30 expense? | expense_query, policy_search, policy_search | 2458 | $0.000196 |
| 7 | engineer | What is the company's security or data-handling policy? | policy_search | 1486 | $0.000158 |
| 8 | manager | What is employee 100's title and department? | employee_lookup | 850 | $0.000070 |
| 9 | engineer | What is the expense submission deadline, per policy? | policy_search, policy_search | 1893 | $0.000153 |
| 10 | manager | Compare the expense approval limits for ic3 versus vp. | expense_query, expense_query | 688 | $0.000061 |

## Answers

### 1. What is the PTO policy, and how many days do managers get?
*Role: engineer · tools: policy_search*

TechCorp's Paid Time Off (PTO) Policy states that all full-time employees receive paid time off. PTO resets on January 1st each year, and unused PTO does not roll over.

Managers receive 20 days of PTO per year.

The company also observes the following holidays: New Year's Day, MLK Day, Presidents Day, Memorial Day, Independence Day, Labor Day, Thanksgiving, and Christmas.

(Source: Paid Time Off Policy)

### 2. What's the expense approval limit for a manager?
*Role: engineer · tools: expense_query*

The expense approval limit for a manager is $5,000.

### 3. Look up the employee with ID 1 — name, title, and department.
*Role: manager · tools: employee_lookup*

Brian Yang is a VP Engineering (Executive) in the Engineering department.

### 4. What does the travel policy say about international flight limits?
*Role: engineer · tools: policy_search*

According to the "Travel and Expense Policy", all international travel requires VP approval. The budget limits for international travel are 50% higher than domestic travel limits.

### 5. Find an employee whose name contains 'Smith'.
*Role: manager · tools: employee_lookup*

Here are the employees whose names contain 'Smith':

*   **Desiree Smith** (ID: 20) - Mid-level Specialist in Operations
*   **Jessica Smith** (ID: 121) - Principal Specialist in Marketing
*   **Tina Smith** (ID: 122) - C-Suite Specialist in Product
*   **Patrick Smith DDS** (ID: 152) - Senior Specialist in Sales
*   **Toni Smith** (ID: 157) - Sr. Manager Specialist in Marketing

### 6. What's the approval limit for a director, and does policy require a receipt for a $30 expense?
*Role: manager · tools: expense_query, policy_search, policy_search*

A director's expense approval limit is $25,000.

I could not find a policy document that specifies receipt requirements for a $30 expense.

### 7. What is the company's security or data-handling policy?
*Role: engineer · tools: policy_search*

TechCorp has a GDPR Compliance Policy that outlines requirements for data handling and security. Key aspects include:

**Data Subject Rights:**
*   Right to access (within 30 days)
*   Right to rectification
*   Right to erasure ("right to be forgotten")
*   Right to restrict processing
*   Right to data portability

**TechCorp Obligations:**
*   Maintain a data inventory
*   Conduct Data Protection Impact Assessments (DPIAs) for new processing activities
*   Report breaches within 72 hours
*   Appoint a Data Protection Officer (DPO)
*   Document all processing activities

**Employee Data Handling:**
*   Employee data should only be processed for HR, payroll, and benefits purposes.
*   Cross-border transfers of employee data require consent.
*   Data retention policies are in place (maximum retention period is specified as "ma").

This information is from the "GDPR Compliance Policy".

### 8. What is employee 100's title and department?
*Role: manager · tools: employee_lookup*

Employee 100, Andrea Hughes, is a Director Specialist in the Human Resources department.

### 9. What is the expense submission deadline, per policy?
*Role: engineer · tools: policy_search, policy_search*

I couldn't find any information about an expense submission deadline in the available policy documents. The "Travel and Expense Policy" does not specify a deadline for submitting expenses.

### 10. Compare the expense approval limits for ic3 versus vp.
*Role: manager · tools: expense_query, expense_query*

The expense approval limit for an IC3 is $2,000, while the limit for a VP is $100,000.

