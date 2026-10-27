# PROJECT CHECKLIST

> Universal checklist. Answer only what you know; `?` = unknown, `N/A` = not applicable, `LATER` = defer. You do not need to complete it before starting the interview.
>
> Labels: **[CORE]** usually worth defining; **[COND]** only when relevant; **[ADV]** for projects that require it. An answer can be a **DECISION**, **PREFERENCE**, or **CONSTRAINT**.

## 01. Idea and goals
1. [CORE] What is the project's name (working title)?
2. [CORE] What do you want to build, in one sentence?
3. [CORE] What problem does it solve?
4. [CORE] Who is it for?
5. [CORE] What concrete outcome do you expect?
6. [CORE] How will you know it worked?
7. [CORE] Why build it now?
8. [COND] What existing alternatives do you know of?
9. [COND] What makes this solution different?
10. [CORE] What do you explicitly not want to do?

## 02. Type, maturity, and scope
11. [CORE] Is this an experiment, POC, MVP, or production project?
12. [CORE] Is it a new project, extension, migration, or replacement?
13. [CORE] Is it a CLI, web app, API, desktop app, mobile app, library, automation, infrastructure project, or something else?
14. [CORE] What must work in the first version?
15. [CORE] What can wait until later?
16. [CORE] What is out of scope?
17. [COND] Do you need a demo?
18. [COND] What hypothesis do you want to validate?
19. [CORE] How much time do you want to invest initially?
20. [COND] Is there a real deadline?

## 03. Users and experience
21. [CORE] Who will actually use it?
22. [COND] How many users do you expect?
23. [COND] How technically skilled are they?
24. [COND] What tasks will they perform most often?
25. [COND] What steps must a user take to complete the application's main task?
26. [COND] Do you need user accounts?
27. [COND] Will there be different roles or permissions?
28. [COND] Must it be accessible to people with disabilities?
29. [COND] Which languages must it support?
30. [COND] Must it work offline?

## 04. Features and rules
31. [CORE] What are the three must-have features?
32. [COND] What data does the user enter?
33. [COND] What outputs does the system produce?
34. [COND] What actions can it perform?
35. [COND] What business rules must never be broken?
36. [COND] What validations are needed?
37. [COND] What errors are expected, and how should they be shown?
38. [COND] Are there repetitive tasks to automate?
39. [COND] Are there operations that require confirmation?
40. [CORE] What concrete example demonstrates the primary use case?

## 05. Interface and developer experience
41. [COND] Is a graphical interface needed?
42. [COND] What minimum screens or views are required?
43. [COND] Must the interface be responsive?
44. [COND] Do you need a design system, or is a basic UI enough?
45. [COND] Will the CLI use commands, subcommands, or an interactive mode?
46. [COND] What inputs and outputs will the CLI have?
47. [COND] Must it support flags, pipes, or JSON output?
48. [COND] What public endpoints or contracts will the API expose?
49. [COND] Do you need API documentation?
50. [COND] How is the project configured when running it?

## 06. Technology and architecture
51. [CORE] Is there a required or preferred programming language?
52. [COND] Is a particular language version required?
53. [COND] Is there a required or preferred framework?
54. [COND] Are any technologies prohibited?
55. [CORE] Which operating systems must it run on?
56. [COND] Where will it run: locally, on a server, in the cloud, or in a hybrid environment?
57. [COND] Should it be a monolith, multiple services, or is that undecided?
58. [COND] Is there an existing architecture to follow?
59. [COND] Do you need concurrency or background jobs?
60. [COND] Are there memory, CPU, or size constraints?

## 07. Data and storage
61. [COND] Must it persist data between runs?
62. [COND] What entities or data types does it handle?
63. [COND] How much data do you expect?
64. [COND] Do you prefer files, SQLite, a relational database, NoSQL, or something else?
65. [COND] Do you need searching, filtering, or sorting?
66. [COND] Will data be imported or exported?
67. [COND] In which formats?
68. [COND] Do you need schema migrations?
69. [COND] How long must data be retained?
70. [COND] Which data can be lost, and which cannot?

## 08. Integrations and dependencies
71. [COND] Which systems must it integrate with?
72. [COND] Which external APIs will it consume?
73. [COND] Which external services are mandatory?
74. [COND] Can it keep working if an integration fails?
75. [COND] Are there quotas or rate limits?
76. [COND] Do you need webhooks or events?
77. [COND] Are specific formats or protocols required?
78. [COND] Will it use external credentials or tokens?
79. [COND] Are there dependencies with restrictive licenses?
80. [COND] Must an existing integration be replaced or migrated?

## 09. Security and privacy
81. [COND] Does it handle personal or sensitive data?
82. [COND] Does it require authentication?
83. [COND] Does it require authorization by role or resource?
84. [COND] Which secrets must it protect?
85. [COND] Which operations would be dangerous if triggered accidentally?
86. [COND] Does it need encryption in transit or at rest?
87. [COND] Must sensitive actions be audited?
88. [COND] Are there legal or compliance requirements?
89. [COND] Who can access it over the network?
90. [COND] How can access be recovered if a credential is lost?

## 10. Repository and collaboration
91. [CORE] Does a repository already exist?
92. [CORE] Where will the code be hosted?
93. [COND] Will it be public or private?
94. [COND] Will it be a monorepo or a standalone repository?
95. [COND] Is there an existing folder structure to preserve?
96. [COND] Who will develop and maintain it?
97. [COND] Do you need branch and commit conventions?
98. [COND] Will changes require review or pull requests?
99. [COND] Which license will it use?
100. [CORE] What minimum documentation do you want to maintain?

## 11. Environment, running, and deployment
101. [CORE] How do you want to run the project locally during development?
102. [COND] Do you need Docker or containers?
103. [COND] Where will it be deployed?
104. [COND] Do you need a domain or HTTPS?
105. [COND] Will there be dev, test, staging, or production environments?
106. [COND] Do you need CI/CD?
107. [COND] How will environment-specific configuration be managed?
108. [COND] How will a release be updated or rolled back?
109. [COND] Must it start automatically?
110. [COND] Are there network, port, or firewall restrictions?

## 12. Quality, testing, and operations
111. [CORE] What behavior is essential to verify?
112. [COND] Do you need unit tests?
113. [COND] Do you need integration or end-to-end tests?
114. [COND] What quality level is sufficient at this stage?
115. [COND] What logs are needed to diagnose errors?
116. [COND] Do you need metrics, alerts, or monitoring?
117. [COND] What minimum performance is required?
118. [COND] How much availability is required?
119. [COND] Do you need backups and restoration?
120. [COND] How will failures be detected and resolved?

## 13. Time, cost, and evolution
121. [CORE] What is the monetary budget?
122. [CORE] What is the time budget?
123. [COND] Which paid services are allowed?
124. [COND] What resources or hardware do you already have?
125. [COND] What dependency or risk could block the project?
126. [COND] What milestones or deliverables do you want?
127. [COND] How will you prioritize features?
128. [COND] What can be dropped if time runs short?
129. [COND] Is future growth expected, or is the project disposable?
130. [CORE] What defines the first version as done?

## 14. AI-assisted development [only if applicable]
131. [COND] Which AI tools will be used for development?
132. [COND] What tasks may AI perform without confirmation?
133. [COND] Which changes require human approval?
134. [COND] Do you want an AGENTS.md or other repository instructions?
135. [COND] Which coding conventions must AI follow?
136. [COND] How should AI investigate the code before editing?
137. [COND] Which files or areas must AI not modify?
138. [COND] Which tests must AI run before marking a task complete?
139. [COND] Which documentation must be updated with each change?
140. [COND] How should AI report decisions, risks, and pending work?

## 15. Special cases [enable as needed]
141. [COND] If this is a homelab project, which existing hosts and services are involved?
142. [COND] If this is a homelab project, which volumes, mounts, and paths must be preserved?
143. [COND] If this is a homelab project, what data-loss risks exist?
144. [COND] If this is an infrastructure project, which changes require rollback?
145. [COND] If this is a migration, which data or behaviors must be preserved?
146. [COND] If this is a migration, will it coexist with the old system?
147. [COND] If this is a library, what is its minimum public API?
148. [COND] If this is an automation, what event or schedule triggers it?
149. [COND] If it uses AI models, what tasks will the model perform, and how will you evaluate the results?
150. [COND] If it uses AI models, what cost, latency, privacy, and context limits apply?

## Quick-answer template

```md
# My project
Idea: ...
High-level specifications: ...

## Checklist answers
2: ...
11: POC
13: CLI
51: Preference: Python
55: Constraint: Linux
91: No
121: Constraint: $0
...

## Confirmed decisions
- ...

## Negotiable preferences
- ...

## Non-negotiable constraints
- ...

## Questions / unknowns
- ...
```

> You can answer by number, in natural language, or both. The interviewer should infer what has already been answered and ask only about what is missing and truly matters.
