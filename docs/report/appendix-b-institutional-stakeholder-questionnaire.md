# SaloneFix — Institutional Stakeholder Questionnaire

**Appendix B: Data-collection instrument for public-service institutions**

| | |
|---|---|
| **Project** | SaloneFix: A Human-First Public-Service Reporting and Accountability Platform for Freetown, Sierra Leone |
| **Students** | Ina M. E. Conteh (905004473) · Sahid A. G. Conteh (905004265) · Mark Lamin Ellie (905004456) |
| **Department / Faculty** | FICT / BSEM |
| **Institution** | Limkokwing University of Creative Technology, Sierra Leone |
| **Supervisor** | Ing. Oluwatosin B. Ayorinde |
| **Intended respondents** | Freetown City Council (FCC), Sierra Leone Roads Authority (SLRA), Sierra Leone Road Safety Authority (SLRSA), Guma Valley Water Company, and comparable service institutions |
| **Version / date** | 1.0 — *(insert date of use)* |

---

## Part 1 — Notes for the research team

*This part is for the students. Remove these two pages before giving the instrument to a respondent.*

### 1.1 Purpose

This instrument collects the information needed to answer **Objective 1** of the study — to investigate the information, verification, privacy, and operational workflow requirements for a public-service reporting platform in Freetown — and to answer **supporting research question 1** on what functional, operational, privacy, and verification requirements should guide such a platform.

It is designed to do a second job as well. Several design decisions in the SaloneFix prototype were made from the specification rather than from institutional evidence: the four initial categories, the requirement that a resolution carry photographic proof before a case can be closed, the distinction between a citizen *report* and a verified *incident*, the routing of an incident to a single responsible institution, and the citizen's ability to dispute a resolution and reopen a case. Sections F, I, and J are written specifically to test those decisions against how the institutions actually work. Where the answers contradict the design, that contradiction is a finding and belongs in Chapter Four, not something to be smoothed over.

### 1.2 How to administer it

The instrument works in two modes, and the mode should be chosen to suit the respondent rather than the research team's convenience.

- **Self-completion questionnaire.** Sections A to P, approximately 25–30 minutes. Suitable for an officer or records staff member who prefers to complete a form and return it.
- **Semi-structured interview.** The same sections used as a topic guide, approximately 40–50 minutes, with Part 4 as additional probes. Suitable for a department head, coordinator, or supervisor, and generally the better choice because the open questions produce more usable detail.

Target two to four respondents per institution where access allows, spread across at least two of these positions: a person who **receives** reports, a person who **assigns or coordinates** work, a person who **performs or supervises** field work, and a person responsible for **records or reporting**. A single respondent per institution is a stated limitation of the sample, not a failure of the instrument.

Not every section applies to every institution. Mark a question **N/A** rather than inferring an answer, and record which sections were skipped and why.

### 1.3 Ethical rules for this instrument

These rules follow from the University's request letters, which promised that only non-confidential information would be sought, that all information would be used strictly for academic purposes, and that it would be treated confidentially. They also follow from the project's own governance commitments.

1. **Obtain recorded consent before the first question.** Use the consent statement in Part 2. Written consent is preferred; note verbal consent in writing where a signature is not practical.
2. **Request no confidential material.** Do not ask for case files, citizen personal data, staff records, contract values, internal correspondence, or anything the respondent indicates is restricted. If a respondent volunteers such material, do not record it.
3. **Do not ask about, or record, allegations against any individual.** This instrument examines *processes and evidence sufficiency*, never the conduct or honesty of a named person. No question may be reworded in the field to ask whether a colleague, contractor, or citizen has acted dishonestly. The project's rules prohibit attaching findings of fraud or dishonesty to any person, and that prohibition applies to data collection as much as to the software.
4. **Report at institutional level.** Attribute findings to a role and an institution, never to a named person, unless the respondent explicitly consents to attribution in writing.
5. **Participation is voluntary throughout.** Any question may be declined and consent may be withdrawn at any point, including after the interview, without the respondent giving a reason.
6. **Do not present the prototype as an agreed or forthcoming system.** It is a student prototype. No question should imply that the institution has adopted it or is expected to.

### 1.4 What each section feeds

| Section | Feeds |
|---|---|
| A, B | Chapter Three existing-system analysis; current intake channels |
| C, D | Report schema and location-precision design; functional requirements |
| E | Report/incident distinction; spatial corroboration parameters |
| F | Institutional routing and jurisdiction rules; assignment design |
| G | Prioritisation and due-date design; overdue signalling |
| H | State-machine vocabulary; status mapping in Chapter Three |
| I | Resolution-evidence requirement per category; review step |
| J | Dispute and reopen design; citizen feedback loop |
| K | Audit-trail requirements; auditor role |
| L | Privacy rules; location and media disclosure defaults |
| M | Role-based access control; provisioning model |
| N | Non-functional requirements; deployment constraints |
| O | Phase-three AI scope and acceptable uses |
| P | Adoption barriers; Chapter Five recommendations |

---

## Part 2 — Participant information and consent

*Give this page to the respondent and keep the signed copy.*

### 2.1 About the research

Three final-year students at Limkokwing University of Creative Technology, Sierra Leone, are undertaking a dissertation project titled *SaloneFix: A Human-First Public-Service Reporting and Accountability Platform for Freetown, Sierra Leone*. The project has built a prototype web system through which residents can report public-service problems — damaged roads and potholes, blocked drainage and flooding, waste accumulation, and damaged public facilities — and through which those reports can be reviewed by a person, assigned to a responsible institution, worked on, and closed with evidence.

The purpose of this questionnaire is to understand **how such reports are received, checked, assigned, acted upon, recorded, and communicated to citizens in your institution today**, and what a system of this kind would need to provide in order to be useful rather than burdensome. Your institution's practices are the reference point for the study; the prototype is not being proposed for adoption.

### 2.2 What participation involves

Completing this questionnaire, or taking part in an interview covering the same topics, lasting approximately 30 to 50 minutes.

### 2.3 Your rights

- Participation is entirely voluntary.
- You may decline any individual question.
- You may stop at any time, and you may withdraw your responses afterwards, without giving a reason.
- You will not be asked for any confidential records, any personal data about citizens or staff, or any information about the conduct of any individual.
- Findings will be reported by role and institution — for example, "an officer at a roads institution reported that…" — and not by name, unless you give separate written permission.
- Responses are used for academic purposes only, in this dissertation and in its assessment.
- Notes and recordings are stored securely, accessible only to the three students and their supervisor.

### 2.4 Consent

Please complete:

| | |
|---|---|
| I confirm I have read and understood the information above | ☐ Yes  ☐ No |
| I agree to take part in this questionnaire or interview | ☐ Yes  ☐ No |
| I agree to the interview being audio-recorded for accuracy *(optional — declining does not prevent participation)* | ☐ Yes  ☐ No |
| I agree to my **role and institution** being named in the dissertation | ☐ Yes  ☐ No |
| I agree to my **name** being named in the dissertation *(optional)* | ☐ Yes  ☐ No |

| | |
|---|---|
| Name *(or "withheld")* | |
| Role / position | |
| Institution / department | |
| Signature | |
| Date | |
| Researcher present | |

---

## Part 3 — Questionnaire

### Section A. Respondent and institutional context

**A1.** Institution: ☐ FCC  ☐ SLRA  ☐ SLRSA  ☐ Guma Valley Water Company  ☐ Other: ______________________

**A2.** Department or unit: ______________________________________________

**A3.** Your role or position: ____________________________________________

**A4.** How long have you worked in this role? ☐ Under 1 year  ☐ 1–3 years  ☐ 4–10 years  ☐ Over 10 years

**A5.** Which of the following describes your involvement with public-service reports? *(tick all that apply)*
☐ I receive reports from the public  ☐ I check or verify reports  ☐ I assign work  ☐ I carry out or supervise field work  ☐ I keep records or prepare reports  ☐ I communicate with citizens  ☐ I supervise others who do the above  ☐ Other: ______________

**A6.** Which service areas does your institution handle? *(tick all that apply)*
☐ Roads and potholes  ☐ Drainage and flooding  ☐ Waste collection and dumping  ☐ Public facilities (markets, toilets, street lighting)  ☐ Water supply  ☐ Road safety and traffic  ☐ Other: ______________

**A7.** Roughly how many public-service reports or complaints does your unit receive in a typical month?
☐ Under 10  ☐ 10–50  ☐ 51–200  ☐ 201–500  ☐ Over 500  ☐ Not recorded / unknown

### Section B. How reports currently reach the institution

**B1.** How do reports from the public most commonly reach your institution? *(tick all that apply, then circle the single most common)*
☐ In person at an office  ☐ Telephone call  ☐ Written letter  ☐ WhatsApp or SMS  ☐ Email  ☐ Social media  ☐ Radio programme  ☐ Ward councillor or community leader  ☐ Another government institution  ☐ Field staff observation  ☐ Existing digital system  ☐ Other: ______________

**B2.** Is there a single point in your institution where incoming reports are recorded?
☐ Yes, one place  ☐ Several places  ☐ No defined place  ☐ Unsure

**B3.** How are incoming reports currently recorded? *(tick all that apply)*
☐ Paper register or logbook  ☐ Spreadsheet  ☐ Dedicated software  ☐ Email folder  ☐ WhatsApp messages  ☐ Not systematically recorded  ☐ Other: ______________

**B4.** If your institution uses software for this, what is it, and what works well or poorly about it?
_______________________________________________________________________________
_______________________________________________________________________________

**B5.** Approximately what proportion of reports arrive with a photograph?
☐ None  ☐ Under 10%  ☐ 10–40%  ☐ 41–70%  ☐ Over 70%  ☐ Unknown

**B6.** In your experience, what is the single biggest problem with how reports arrive today?
_______________________________________________________________________________
_______________________________________________________________________________

### Section C. What makes a report actionable

**C1.** For your institution to act on a report, how important is each of the following? *(1 = not important, 5 = essential)*

| Information supplied with a report | 1 | 2 | 3 | 4 | 5 | N/A |
|---|---|---|---|---|---|---|
| A clear description of the problem | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| A category or type of problem | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| A photograph of the problem | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Satellite coordinates of the location | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| A landmark or place description | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| The ward or community name | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| How long the problem has existed | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| An indication of severity or danger | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| Whether anyone has been injured or harmed | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| The reporter's name | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| The reporter's contact number | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| How many people are affected | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**C2.** Is there anything in the list above that your institution would consider **mandatory** — a report without it cannot be acted on at all?
_______________________________________________________________________________

**C3.** Is there anything **not** in the list above that your institution needs in order to act?
_______________________________________________________________________________

**C4.** What most commonly makes a report unusable, in order of how often it happens? *(rank 1 = most common; leave blank if not applicable)*

| | Rank |
|---|---|
| The location cannot be identified | |
| The description is too vague | |
| The problem is not this institution's responsibility | |
| It duplicates a report already received | |
| No photograph or other evidence | |
| The reporter cannot be contacted for clarification | |
| The problem had already been fixed | |
| The report appears not to describe a real problem | |
| Other: ______________________ | |

**C5.** When a report is incomplete, what happens to it?
☐ We contact the reporter for more detail  ☐ We send someone to look  ☐ It is held until more reports arrive  ☐ It is set aside  ☐ It depends — explain: ______________________

**C6.** Can your institution currently ask a reporter a follow-up question?
☐ Yes, routinely  ☐ Yes, sometimes  ☐ Rarely  ☐ No

### Section D. Locating a reported problem

**D1.** How is the location of a reported problem usually established?
☐ Landmark or place name given by the reporter  ☐ Street name and area  ☐ Ward or community  ☐ Satellite coordinates  ☐ A staff member goes to look  ☐ Other: ______________

**D2.** How often is a reported location too imprecise to find the problem?
☐ Almost never  ☐ Occasionally  ☐ Often  ☐ Very often

**D3.** For your work, which is more useful — satellite coordinates, or a landmark description in local terms? Why?
_______________________________________________________________________________
_______________________________________________________________________________

**D4.** How close do coordinates need to be to the actual problem to be useful to a field team?
☐ Within 10 metres  ☐ Within 50 metres  ☐ Within 100 metres  ☐ Within the correct street  ☐ Within the correct ward  ☐ Coordinates are not how we work

**D5.** Would it be useful to know how accurate a reported location is — for example, that one report's position is precise while another's is only a typed landmark?
☐ Very useful  ☐ Somewhat useful  ☐ Not useful  ☐ Unsure

Comment: ______________________________________________________________________

### Section E. Duplicate and repeated reports

**E1.** How often do several reports describe the same problem?
☐ Almost never  ☐ Occasionally  ☐ Often  ☐ Very often  ☐ Unknown

**E2.** How are duplicates identified at present?
☐ A staff member recognises them  ☐ By checking the register  ☐ By location  ☐ They are not systematically identified  ☐ Other: ______________

**E3.** What problems do duplicates cause? *(tick all that apply)*
☐ Teams sent twice to the same place  ☐ Inflated report counts  ☐ Wasted review time  ☐ Confusion over which case is current  ☐ Difficulty reporting accurate figures  ☐ No real problem  ☐ Other: ______________

**E4.** The prototype treats several reports about one problem as a single **case**, while keeping each individual report attached to it. Would that be useful to your institution?
☐ Very useful  ☐ Somewhat useful  ☐ Not useful  ☐ Unsure

Comment: ______________________________________________________________________

**E5.** If several residents report the same problem, does that make your institution more likely to act on it?
☐ Much more likely  ☐ Somewhat more likely  ☐ No difference  ☐ It depends — explain: ______________

**E6.** Conversely, is a problem reported by only one person treated as less credible?
☐ Yes  ☐ No  ☐ It depends — explain: ______________________________________________

**E7.** Are there areas of Freetown from which your institution receives very few reports, despite problems being present?
☐ Yes — which, broadly: ______________________  ☐ No  ☐ Unsure

### Section F. Responsibility, jurisdiction and assignment

*This section tests whether routing a case to one responsible institution matches how responsibility actually works.*

**F1.** Who decides which institution or department is responsible for a reported problem?
_______________________________________________________________________________

**F2.** How often does a report arrive that is another institution's responsibility?
☐ Almost never  ☐ Occasionally  ☐ Often  ☐ Very often

**F3.** When that happens, what do you do?
☐ Forward it formally  ☐ Pass it informally  ☐ Advise the reporter to go elsewhere  ☐ Nothing  ☐ Other: ______________

**F4.** Are there categories of problem where responsibility between institutions is genuinely unclear or shared? Please describe one or two.
_______________________________________________________________________________
_______________________________________________________________________________

**F5.** Within your institution, how is a report assigned to a person or team for action?
_______________________________________________________________________________

**F6.** Is that assignment recorded anywhere?
☐ Yes, always  ☐ Sometimes  ☐ No  ☐ Unsure

**F7.** The prototype assigns each case to **one** responsible institution, with one officer accountable for it. Does that match how work is actually allocated?
☐ Yes, closely  ☐ Partly  ☐ No — explain: __________________________________________

**F8.** Would it be workable for an officer of your institution to see only the cases assigned to your institution, and not those of other institutions?
☐ Yes, that is appropriate  ☐ We would need visibility of related cases elsewhere  ☐ Unsure

### Section G. Prioritisation and timelines

**G1.** How is it decided which reports are dealt with first? *(tick all that apply)*
☐ Order received  ☐ Danger to life or safety  ☐ Number of people affected  ☐ Number of reports received  ☐ Instruction from management  ☐ Availability of resources  ☐ Location or route importance  ☐ Other: ______________

**G2.** Does your institution have target times within which a report should be acted on?
☐ Yes, formal targets  ☐ Informal expectations  ☐ No  ☐ Unsure

If yes, what are they, by type of problem?
_______________________________________________________________________________

**G3.** Typically, how long from a report arriving to a field team attending?
☐ Same day  ☐ 2–7 days  ☐ 1–4 weeks  ☐ 1–3 months  ☐ Longer  ☐ Highly variable

**G4.** And from attendance to the problem being fixed?
☐ Same day  ☐ 2–7 days  ☐ 1–4 weeks  ☐ 1–3 months  ☐ Longer  ☐ Highly variable

**G5.** What most often delays action? *(rank 1 = most frequent cause)*

| | Rank |
|---|---|
| Funding or budget approval | |
| Equipment or materials unavailable | |
| Staff or contractor availability | |
| Weather or seasonal conditions | |
| Waiting on another institution | |
| Access to the site | |
| Report arrived too late or incomplete | |
| Approval or authorisation steps | |
| Other: ______________________ | |

**G6.** Would it be useful for the system to show that a case has passed its target date?
☐ Very useful  ☐ Somewhat useful  ☐ Not useful — explain: ______________________

### Section H. Recording progress and status

**H1.** Is the progress of a report recorded as it moves through your institution?
☐ Yes, at each stage  ☐ At some stages  ☐ Only at the start and end  ☐ No

**H2.** What terms does your institution use for the stages of a case? Please give your own wording against each stage below, or write **N/A** where the stage does not exist.

| Stage in the prototype | Your institution's term |
|---|---|
| Report received, not yet checked | |
| Report being checked | |
| Report accepted as a genuine case | |
| Report not accepted | |
| More information needed from the reporter | |
| Case assigned to an institution | |
| Work in progress | |
| Work completed, awaiting verification | |
| Case confirmed resolved | |
| Case closed | |
| Case raised to a higher authority | |
| Resolution contested by the reporter | |

**H3.** Are any stages in your process missing from the list above?
_______________________________________________________________________________

**H4.** Who is permitted to change the status of a case?
_______________________________________________________________________________

**H5.** When a status changes, is a reason recorded?
☐ Always  ☐ Sometimes  ☐ No  ☐ Unsure

**H6.** How do field teams report progress from site? *(tick all that apply)*
☐ Verbally  ☐ Written form returned to office  ☐ Telephone  ☐ WhatsApp  ☐ Photographs  ☐ Mobile application  ☐ Other: ______________

### Section I. Resolution and evidence of completion

*This section tests the prototype's rule that a case in certain categories cannot be closed without a photograph of the completed work.*

**I1.** What is currently required before a case is treated as resolved? *(tick all that apply)*
☐ Field team states it is done  ☐ Supervisor inspects  ☐ Photograph of completed work  ☐ Written completion report  ☐ Contractor sign-off  ☐ Reporter confirms  ☐ Nothing formal is required  ☐ Other: ______________

**I2.** Is photographic evidence of completed work required at present?
☐ Always  ☐ For some types of work  ☐ Rarely  ☐ Never  ☐ Unsure

**I3.** Who checks that completion evidence is adequate before a case is closed?
_______________________________________________________________________________

**I4.** How confident are you that a case recorded as resolved has in fact been resolved?
☐ Very confident  ☐ Fairly confident  ☐ Not very confident  ☐ Unsure

**I5.** The prototype refuses to close a case in certain categories unless a photograph of the completed work is attached. For which of these would that requirement be reasonable?
☐ Roads and potholes  ☐ Drainage and flooding  ☐ Waste collection  ☐ Public facilities  ☐ Water supply  ☐ None of them  ☐ All of them

**I6.** Would that requirement create difficulty for your field teams? *(For example, device availability, connectivity at site, or the time it takes.)*
☐ No difficulty  ☐ Some difficulty  ☐ Significant difficulty

Please explain: ________________________________________________________________
_______________________________________________________________________________

**I7.** What makes a completion photograph genuinely useful as evidence, as opposed to merely present?
_______________________________________________________________________________
_______________________________________________________________________________

**I8.** Should completion evidence, once submitted, be impossible to delete or replace?
☐ Yes  ☐ No  ☐ It depends — explain: ______________________________________________

### Section J. Communicating with citizens, and contested resolutions

**J1.** Is the person who made a report told what happened to it?
☐ Always  ☐ Usually  ☐ Sometimes  ☐ Rarely  ☐ Never

**J2.** If so, how? *(tick all that apply)*
☐ Telephone call  ☐ SMS or WhatsApp  ☐ In person  ☐ Through a community leader  ☐ Public notice or radio  ☐ Not communicated  ☐ Other: ______________

**J3.** What prevents your institution from giving feedback to reporters more consistently?
_______________________________________________________________________________

**J4.** Can a resident currently complain that a problem recorded as fixed is not in fact fixed?
☐ Yes, there is a route for that  ☐ Informally only  ☐ No  ☐ Unsure

**J5.** The prototype allows the resident who reported a problem to **dispute** a resolution, which reopens the case for review. How would your institution regard that?
☐ Appropriate and useful  ☐ Acceptable with conditions  ☐ Problematic  ☐ Unsure

Please explain, including any conditions: _______________________________________
_______________________________________________________________________________

**J6.** Who should decide whether a disputed case is genuinely unresolved?
☐ The assigned officer  ☐ A supervisor in the institution  ☐ An independent reviewer outside the institution  ☐ Other: ______________

**J7.** Roughly how often do residents currently return to say a problem was not properly fixed?
☐ Never  ☐ Rarely  ☐ Sometimes  ☐ Often  ☐ Unknown

### Section K. Records, oversight and inspection

**K1.** Can the full history of a case be reconstructed from your institution's records — who did what, when, and why?
☐ Yes, fully  ☐ Partly  ☐ No  ☐ Unsure

**K2.** Who inspects or audits this information? *(tick all that apply)*
☐ Internal supervisors  ☐ Internal audit  ☐ A ministry or parent body  ☐ Audit Service Sierra Leone  ☐ Civil-society organisations  ☐ Nobody routinely  ☐ Other: ______________

**K3.** What reports or figures does your unit have to produce, and to whom?
_______________________________________________________________________________

**K4.** How difficult is it to produce those figures from current records?
☐ Straightforward  ☐ Time-consuming  ☐ Very difficult  ☐ Not possible

**K5.** Would a permanent record of every decision on a case — showing who decided, when, and the reason, and which cannot be edited or deleted afterwards — be useful or problematic for your institution?
☐ Useful  ☐ Useful with conditions  ☐ Problematic  ☐ Unsure

Please explain: ________________________________________________________________
_______________________________________________________________________________

**K6.** Should someone outside your institution be able to inspect that record?
☐ Yes, any authorised reviewer  ☐ Yes, but only a designated oversight body  ☐ No  ☐ Unsure

### Section L. Data sharing, privacy and publication

**L1.** How would your institution regard each of the following being visible to the general public?

| Information | Acceptable | Acceptable in part | Not acceptable | Unsure |
|---|---|---|---|---|
| That a report exists, and its category | ☐ | ☐ | ☐ | ☐ |
| The approximate location of a reported problem | ☐ | ☐ | ☐ | ☐ |
| The exact coordinates of a reported problem | ☐ | ☐ | ☐ | ☐ |
| The photograph submitted by the reporter | ☐ | ☐ | ☐ | ☐ |
| The identity of the reporter | ☐ | ☐ | ☐ | ☐ |
| Which institution a case is assigned to | ☐ | ☐ | ☐ | ☐ |
| The current status of a case | ☐ | ☐ | ☐ | ☐ |
| How long a case has been open | ☐ | ☐ | ☐ | ☐ |
| The photograph of completed work | ☐ | ☐ | ☐ | ☐ |
| The name of the officer handling a case | ☐ | ☐ | ☐ | ☐ |
| Aggregate figures, such as cases closed per month | ☐ | ☐ | ☐ | ☐ |

**L2.** Which single item above would your institution be most reluctant to see published, and why?
_______________________________________________________________________________
_______________________________________________________________________________

**L3.** Does your institution have a policy or legal requirement governing what report data may be shared or published?
☐ Yes — please indicate which: ______________________  ☐ No  ☐ Unsure

**L4.** The prototype keeps reporters' photographs private, viewable only by authorised staff through a time-limited link, and removes location data embedded in the image file before storing it. Is that appropriate?
☐ Yes  ☐ Too restrictive  ☐ Not restrictive enough  ☐ Unsure

Comment: ______________________________________________________________________

**L5.** What concerns would your institution have about report data being held by a system it does not itself operate?
_______________________________________________________________________________
_______________________________________________________________________________

### Section M. Roles and access

**M1.** In a system of this kind, who in your institution should be able to do each of the following?

| Action | Who should be permitted |
|---|---|
| See cases assigned to the institution | |
| Accept a case and begin work | |
| Record progress on a case | |
| Submit evidence of completed work | |
| Confirm that a case is resolved | |
| Close a case | |
| Reassign a case to another institution | |
| Create accounts for institutional staff | |
| Inspect the full history of any case | |

**M2.** Should the same person be able to both submit completion evidence and approve it?
☐ Yes  ☐ No, these should be separate people  ☐ It depends — explain: ______________

**M3.** How many staff in your unit would realistically use such a system?
☐ 1–2  ☐ 3–5  ☐ 6–15  ☐ More than 15

**M4.** Who should be able to create and remove those staff accounts?
☐ Our institution itself  ☐ The platform operator  ☐ Both, with our approval  ☐ Unsure

### Section N. Technology and practical constraints

**N1.** What devices do relevant staff have access to at work? *(tick all that apply)*
☐ Desktop computer  ☐ Laptop  ☐ Institutional smartphone  ☐ Personal smartphone used for work  ☐ Basic mobile phone  ☐ Tablet  ☐ None reliably

**N2.** How reliable is internet access in your offices?
☐ Reliable  ☐ Mostly reliable  ☐ Frequently interrupted  ☐ Rarely available

**N3.** And for field teams at a work site?
☐ Reliable  ☐ Mostly reliable  ☐ Frequently interrupted  ☐ Rarely available  ☐ Unknown

**N4.** Who pays for data used for work purposes?
☐ The institution  ☐ The individual staff member  ☐ Mixed  ☐ Unsure

**N5.** Would staff need training to use a web-based system of this kind?
☐ Little or none  ☐ Some  ☐ Substantial

**N6.** Does your institution already use a system that this would need to work alongside, or that it would duplicate?
☐ Yes — please name it: ______________________  ☐ No  ☐ Unsure

**N7.** What would make a system like this **fail** in your institution, in your judgement?
_______________________________________________________________________________
_______________________________________________________________________________

### Section O. Views on automated assistance

*The prototype currently operates entirely through human decisions. Automated assistance is planned for a later phase, and would only ever produce suggestions for a person to accept, correct, or ignore. These questions ask what your institution would consider acceptable.*

**O1.** How acceptable would each of the following be?

| Automated assistance | Acceptable | Acceptable with human review | Not acceptable | Unsure |
|---|---|---|---|---|
| Suggesting the category of a reported problem | ☐ | ☐ | ☐ | ☐ |
| Flagging that a photograph and description may not match | ☐ | ☐ | ☐ | ☐ |
| Suggesting that two reports may describe the same problem | ☐ | ☐ | ☐ | ☐ |
| Suggesting which cases need attention most urgently | ☐ | ☐ | ☐ | ☐ |
| Flagging completion evidence as needing closer review | ☐ | ☐ | ☐ | ☐ |
| Assigning a case to an institution without human review | ☐ | ☐ | ☐ | ☐ |
| Closing a case without human review | ☐ | ☐ | ☐ | ☐ |

**O2.** Should a person always be able to overrule an automated suggestion?
☐ Yes, always  ☐ In most cases  ☐ Not necessary  ☐ Unsure

**O3.** What would concern your institution most about automated assistance in this process?
_______________________________________________________________________________
_______________________________________________________________________________

**O4.** The system is designed so that it continues to work normally if automated components are switched off or unavailable. How important is that to your institution?
☐ Essential  ☐ Important  ☐ Not important  ☐ Unsure

### Section P. Overall assessment

**P1.** How useful would a system of this kind be to your institution, as described?
☐ Very useful  ☐ Useful  ☐ Of limited use  ☐ Not useful  ☐ Unsure

**P2.** Which single feature would be most valuable?
_______________________________________________________________________________

**P3.** Which single feature would be most problematic?
_______________________________________________________________________________

**P4.** What are the main barriers to a system like this being adopted here? *(rank 1 = largest barrier)*

| | Rank |
|---|---|
| Funding and running costs | |
| Staff capacity and workload | |
| Devices and connectivity | |
| Training and digital skills | |
| Approval and policy processes | |
| Coordination between institutions | |
| Concerns about public visibility of performance | |
| Duplication of an existing system | |
| Data protection and privacy | |
| Other: ______________________ | |

**P5.** What would need to be true for your institution to pilot such a system?
_______________________________________________________________________________
_______________________________________________________________________________

**P6.** Is there anything important about how public-service reports work here that these questions have missed?
_______________________________________________________________________________
_______________________________________________________________________________

**P7.** Would you be willing to look at the prototype and give feedback at a later stage?
☐ Yes  ☐ No  ☐ Perhaps — contact via: ______________________

---

**Thank you for your time and assistance.**

For queries about this research, contact the project supervisor, Ing. Oluwatosin B. Ayorinde, Limkokwing University of Creative Technology, Sierra Leone.

---

## Part 4 — Additional interview probes

*For interview mode only. Use these to open up the answers given in Part 3; they are not for self-completion.*

### 4.1 Narrative walkthrough

Ask the respondent to walk through one recent case from beginning to end, without naming any individual or disclosing any confidential detail. Follow the case, not the process diagram: *What arrived first? Who saw it? What did they do with it? Who decided it was yours? How did the team find the place? What came back from site? How did it get closed? Did anyone tell the person who reported it?* A narrative account usually reveals steps that a process question does not.

### 4.2 Probes by theme

**On evidence.** *What makes you believe a report before you have sent anyone to look? When has a photograph changed a decision? What does a convincing photograph of completed work look like, compared with one that tells you nothing?*

**On responsibility.** *Describe a case where it was unclear whose responsibility it was. How was that settled? How long did it take?*

**On the single-report problem.** *If one person reports something serious and nobody else does, what happens? Does that differ between parts of the city?*

**On closure.** *What does "closed" mean in practice here? Is there a difference between a case being closed and a problem being gone?*

**On being seen.** *If the time your institution takes were visible to the public, what would be the effect — on your work, and on how the institution is understood? What context would need to be shown alongside it to be fair?*

**On burden.** *What would you have to stop doing in order to use a system like this? Where would it save you time, and where would it cost you time?*

### 4.3 Recording and closing

Note the time, the duration, whether the account was recorded or written, and any sections declined. Confirm at the end that the respondent is still content for their answers to be used, and ask whether anything said should be excluded. Offer to share the relevant findings once the dissertation is complete.

---

## Part 5 — Response record

*For the research team. One row per respondent.*

| Field | Entry |
|---|---|
| Respondent reference *(e.g. FCC-01)* | |
| Institution | |
| Role category *(receives / assigns / performs / records / supervises)* | |
| Mode *(questionnaire / interview)* | |
| Date and duration | |
| Consent obtained *(written / verbal)* | |
| Attribution permitted *(none / role and institution / name)* | |
| Recording permitted | |
| Sections declined or N/A | |
| Design decisions supported by this response | |
| Design decisions contradicted by this response | |
| Follow-up agreed | |
