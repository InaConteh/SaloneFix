# SaloneFix — Usability Evaluation and User Acceptance Testing Instrument

**Appendix F: Post-task instrument for citizen user acceptance testing**

| | |
|---|---|
| **Project** | SaloneFix: A Human-First Public-Service Reporting and Accountability Platform for Freetown, Sierra Leone |
| **Students** | Ina M. E. Conteh (905004473) · Sahid A. G. Conteh (905004265) · Mark Lamin Ellie (905004456) |
| **Department / Faculty** | FICT / BSEM |
| **Institution** | Limkokwing University of Creative Technology, Sierra Leone |
| **Supervisor** | Ing. Oluwatosin B. Ayorinde |
| **Intended participants** | Adult residents of Freetown taking part in a supervised session with the prototype |
| **Instrument** | Scripted tasks, per-task observation record, System Usability Scale (Brooke, 1996), post-test debrief |
| **Version / date** | 1.0 — *(insert date of use)* |

---

## Part 1 — Notes for the research team

*This part is for the students. Remove these pages before running a session.*

### 1.1 Purpose

This instrument produces the measured, observed evidence for **Objective 4** of the study — to evaluate the prototype against the human-only baseline — and supplies four of the human-only metrics named in the evaluation protocol that cannot be derived from system records alone:

| Metric in the evaluation protocol | Produced by |
|---|---|
| **Usability score** | Section 3 of Part 3 — the System Usability Scale. Chapter One §1.10 states that usability requires a survey instrument and is never estimated from the system's own data; this is that instrument. |
| **Report completion rate** | Task 2 in Part 3 — whether a participant completes a submission unaided, and what is missing when they do not. |
| **Clarification rate** | Task 2, read together with the moderator pass in §1.6 — how many submitted reports a moderator judges too incomplete to verify. |
| **Dispute rate** | Task 5 — whether a participant who is shown an inadequate resolution actually disputes it, as against the willingness they reported in Appendix A §K5. |

Appendix A asks residents what they think they would do. This instrument records what they actually do. Where the two disagree, report both, label which is self-report and which is observation, and treat the gap itself as a finding rather than resolving it in favour of either.

### 1.2 What is being tested

**The system is on trial, not the participant.** Say this at the start of every session, in those words, and again whenever a participant apologises or says they are not good with phones. A participant who struggles has produced a result, not a failure. Nothing in this instrument records a participant's competence, and no session note may characterise a participant as slow, careless, or unable.

### 1.3 How to administer it

Two researchers are needed.

- **The facilitator** sits with the participant, reads the task scripts, times the tasks, and completes the observation record. The facilitator does not help, explain, or point at the screen during a timed task.
- **The operator** works from a second device, out of the participant's sight, and plays the moderator and the institutional officer so that the lifecycle advances between tasks. §1.6 sets out what the operator does.

Session length is about 40 to 50 minutes: 5 minutes for consent and orientation, 20 to 25 minutes of tasks, 5 minutes for the usability scale, and 10 minutes of debrief.

Run the session on a device the participant is used to where that is possible — their own phone on the test site, if they consent and have data — and otherwise on a project phone. Record which was used; a result obtained on an unfamiliar device is not comparable to one obtained on the participant's own.

**During a timed task the facilitator stays silent.** If the participant is stuck, wait. Intervene only in the three situations in §1.5, and record the intervention. Prompting a participant and then recording the task as successful destroys the measurement.

Target 8 to 12 participants, chosen for variation rather than number: different wards, a spread of ages, both men and women, participants who own a smartphone and participants who do not use one daily. A sample of confident smartphone users will produce a usability score that means nothing. The composition of the achieved sample is a stated limitation and must be reported with the result.

### 1.4 Test environment

Run against a **separate test deployment** with seeded data, never against anything holding real reports.

- Sign the participant in with a prepared test citizen account. Do not ask a participant to create an account, choose a password, or use any credential of their own.
- Seed each session so that the participant starts with no reports of their own, and so that the tasks in Part 3 can run in order.
- Reset the data between participants, so that each session starts from the same state and times are comparable.
- Record the test build identifier and the date, because a usability score belongs to a specific build.
- The reports created during a session are test data. Delete them when the study's analysis is complete, and say so in the consent statement.

### 1.5 When the facilitator may intervene

Only these three, and each is written on the record:

1. **The participant asks to stop, or shows distress.** Stop the task immediately and move on, or end the session.
2. **A technical fault blocks the task** — the server is unreachable, the build is broken. Stop the clock, record the fault, and either restart the task or abandon it. A task lost to a fault is not a task failure and must not be counted as one.
3. **The participant has been stuck past the cut-off time** in the task table and asks for help, or is clearly unable to continue. Record the task as *not completed*, note what they were trying to do, then give the minimum prompt needed to continue so that the later tasks can still be attempted. The prompt is recorded; the task stays failed.

Answer a question with *"whatever you would do if I were not here"* during a timed task. Answer it properly in the debrief.

### 1.6 Operator actions between tasks

The participant must meet a real lifecycle, not a simulation of one. Between tasks the operator acts on the participant's own report from the moderator and officer screens. The operator makes genuine decisions on what the participant actually submitted — this is what makes the clarification measurement real — and records them.

| After | The operator does | So that |
|---|---|---|
| Task 2 | Opens the participant's report, judges it as a moderator would, and either verifies it or sends a clarification request with a reason | Task 3 has something to show, and the clarification measurement reflects a real moderator judgement on a real report |
| Task 3 | Assigns the verified case to an institution and moves it to work in progress | Task 4 shows a case that has moved |
| Task 4 | Submits resolution evidence as the assigned officer, using the **deliberately inadequate** seeded photograph described below, and moves the case to resolved | Task 5 presents a resolution a reasonable person would question |

For Task 5 the resolution photograph must be plainly inadequate — a picture of a different place, or of work obviously unfinished — and the same photograph is used for every participant. The participant is **not** told that it is inadequate. Whether they notice, and whether they then dispute, is the measurement. Debrief this at the end of the session: tell every participant that the resolution they were shown was a prepared test case, not the work of any real institution or person.

### 1.7 Ethical rules for this instrument

These follow from the undertakings in the project's request letters and from the project's own governance rules.

1. **Obtain recorded consent before the orientation.** Use the statement in Part 2.
2. **The prototype is a student project, not a government service.** Say so at the start. No task, script, or question may imply that an institution has adopted it, intends to, or will receive anything the participant submits.
3. **Nothing submitted in a session is a real report.** If a participant describes a real problem they want fixed, explain that the study cannot pass it on, and direct them to the ordinary channel.
4. **Do not ask about, or record, the honesty or conduct of any named person.** Task 5 asks a participant to assess whether a *piece of evidence* shows completed work. It must never be presented, or written up, as a judgement about whether an officer, contractor, or institution lied. The seeded resolution was prepared by the research team, and the debrief says so explicitly.
5. **No personal data.** Do not record names, contact details, or identification numbers, and do not photograph or video the participant. Screen recording is permitted only with consent, and only of the screen.
6. **Record no judgement of the participant.** Observation notes describe what happened on the screen and what the participant said, not what the participant is like.
7. **Participation is voluntary throughout.** Any task may be refused, the session may be stopped at any time, and responses may be withdrawn afterwards without a reason.
8. **No payment.** Transport reimbursement at cost is acceptable and must be recorded; payment for participation is not.

### 1.8 What each part feeds

| Part | Feeds |
|---|---|
| Part 3 §1, task record | Report completion rate; task success and time; Chapter Four usability results |
| Part 3 §1, Task 2 with the operator's moderator pass | Clarification rate |
| Part 3 §1, Task 5 | Dispute rate; the gap against self-reported willingness in Appendix A §K5 |
| Part 3 §2, System Usability Scale | Usability score; the single comparable figure carried into Chapter Four and re-measured in the hybrid phase |
| Part 3 §3, debrief | Qualitative explanation of the scores; defect list; Chapter Five recommendations |
| Part 4, severity list | Prioritised defects for Chapter Five future work |

The System Usability Scale is administered **unchanged** so that the figure stays comparable with the published literature and with the later hybrid-phase measurement. Do not add items to it, do not drop items, and do not reorder it. Additional questions belong in the debrief.

---

## Part 2 — Participant information and consent

*Read this page aloud to the participant and keep the signed or recorded copy.*

### 2.1 About the research

Three final-year students at Limkokwing University of Creative Technology, Sierra Leone, are carrying out a university project about how residents report public-service problems in Freetown — damaged roads, blocked drains, waste, and damaged public facilities — and how those reports are handled.

They have built a **prototype**: a test version of a web application. Today we would like you to try it and tell us what you think of it.

**This is a student project for a university dissertation. It is not a government service.** No institution has adopted it. Anything you submit today goes into a test system only; it will not reach Freetown City Council, the Sierra Leone Roads Authority, Guma Valley, or anyone else, and no problem will be fixed because of it. The test information is deleted once the project's analysis is finished.

### 2.2 What participation involves

About 45 minutes. We will ask you to carry out five short tasks in the application, such as reporting a problem and then checking what happened to it. Afterwards we will ask you ten short questions about how easy or difficult it was, and then talk with you for a few minutes about what you thought.

**We are testing the application, not you.** There is no right or wrong way to do the tasks. If something is confusing, that is information we need — it is a problem with what we built. Please work as you normally would, and say out loud whatever you are thinking if you are comfortable doing so.

One of the tasks will show you a case that an institution has marked as finished. That case and its photograph were prepared by us for the test. It is not real work by any real institution or any real person.

### 2.3 Your rights

- Taking part is entirely your choice, and you are not paid for taking part. Transport costs can be reimbursed.
- You may skip any task or any question.
- You may stop at any time, and you may ask us afterwards to remove your answers, without giving a reason.
- **We will not write down your name, your telephone number, your address, or any identification number.** Your answers are recorded under a reference such as U-07.
- We will not photograph or film you. If you agree, we may record the screen only — not you — so that we can check our notes afterwards.
- We will not write down any judgement about you or your ability. Our notes describe the application.
- We will not ask you anything about the honesty or behaviour of any particular person, and we cannot record such a statement if you make one.
- Your answers are used only for this dissertation and its assessment, and are seen only by the three students and their supervisor.

### 2.4 Consent

Please complete:

| | |
|---|---|
| The researcher has explained the session to me and I understood the explanation | ☐ Yes  ☐ No |
| I understand that this is a student project and **not** a government service, and that nothing I submit today reaches any institution | ☐ Yes  ☐ No |
| I understand that the application is being tested, not me | ☐ Yes  ☐ No |
| I agree to take part | ☐ Yes  ☐ No |
| I agree to the **screen** being recorded *(optional — declining does not prevent participation)* | ☐ Yes  ☐ No |
| I agree to being audio-recorded during the discussion at the end *(optional)* | ☐ Yes  ☐ No |
| I understand that my name and contact details will not be recorded | ☐ Yes  ☐ No |
| I agree to use my own phone for the session *(optional — a project phone is available instead)* | ☐ Yes  ☐ No |

| | |
|---|---|
| Participant reference *(assigned by the researcher, e.g. U-07)* | |
| Consent given | ☐ In writing (signature below)  ☐ Verbally, witnessed by the researcher |
| Signature or mark *(optional)* | |
| Date | |
| Facilitator | |
| Operator | |
| Language used | ☐ English  ☐ Krio  ☐ Both |

---

## Part 3 — The session

### Section 1. Scripted tasks

*Read each script to the participant exactly as written, then stop talking and start the clock. Do not explain the application. Do not say which button to press.*

**Before Task 1.** Say: *"You will see five short tasks. We are testing the application, not you. If something does not work or does not make sense, that is exactly what we need to find out. Please say out loud what you are thinking, if you are comfortable doing that. If you get stuck, that is fine — just tell me."*

Sign the participant in with the prepared test account before Task 1 and let them look at the opening screen for up to one minute, untimed. Record first impressions in the observation column.

---

**Task 1 — Find where to make a report.** *(Warm-up. Cut-off: 2 minutes.)*

Script: *"You have noticed a problem in your area and you want to tell someone about it using this application. Find the place where you would start."*

Success: the participant opens the report submission form.

---

**Task 2 — Submit a report with a photograph and a location.** *(The central task. Cut-off: 8 minutes.)*

Script: *"There is a large hole in the road outside the market near you. Vehicles have been damaged by it and it has been there for about two weeks. Report it. There is a photograph of it already saved on this phone. Give the location as best you can. Tell me when you think you have finished."*

Success: a report is submitted containing a category, a description, a location of any precision, and the attached photograph.

Record separately, because partial completion is the interesting result:

| | |
|---|---|
| Category chosen | ______________________ |
| Was the category the one a moderator would choose? | ☐ Yes  ☐ No |
| Description submitted *(copy the text, or "none")* | ______________________________________________ |
| Location precision recorded by the system | ☐ Exact  ☐ Approximate  ☐ Typed landmark  ☐ None |
| Did the participant allow the phone's location to be used? | ☐ Yes  ☐ No  ☐ Did not reach the prompt |
| Photograph attached | ☐ Yes  ☐ No  ☐ Attempted and failed |
| Did the participant read the privacy note on the form? | ☐ Yes  ☐ No  ☐ Unclear |
| Did the participant notice the reference number? | ☐ Yes, unprompted  ☐ Only when asked later  ☐ No |

**Operator:** before Task 3, judge this report as a moderator and either verify it or return a clarification request with a reason. Record the decision and the reason in the table below.

| | |
|---|---|
| Moderator decision on this participant's report | ☐ Verified  ☐ Clarification requested  ☐ Would have rejected |
| Reason recorded | ______________________________________________ |
| What was missing or unclear, if anything | ______________________________________________ |

---

**Task 3 — Find your report and see what has happened to it.** *(Cut-off: 4 minutes.)*

Script: *"Some time has passed. Find the report you just made, and tell me what has happened to it."*

Success: the participant locates their report and states its current stage.

| | |
|---|---|
| How did the participant find it? | ☐ My reports list  ☐ Reference number  ☐ Did not find it |
| Stage the system showed | ______________________ |
| What the participant said it meant, in their own words | ______________________________________________ |
| Was their understanding correct? | ☐ Yes  ☐ Partly  ☐ No |
| If a clarification was requested, did the participant notice the question? | ☐ Yes  ☐ No  ☐ Not applicable |
| If they noticed it, what did they say they would do about it? | ______________________________________________ |

*Note for the research team: the current build shows a moderator's clarification question to the citizen but provides no way for the citizen to answer it in the application. Do not prompt the participant about this. Record what they try to do, and whether they expected to be able to reply — it is a known gap and this is the evidence for it.*

**Operator:** before Task 4, assign the case to an institution and move it to work in progress.

---

**Task 4 — Find out who is dealing with it and what stage it has reached.** *(Cut-off: 4 minutes.)*

Script: *"Find out who is now dealing with your report, and what stage it has reached."*

Success: the participant states the responsible institution and the current stage.

| | |
|---|---|
| Institution named correctly | ☐ Yes  ☐ No  ☐ Did not find it |
| Stage named correctly | ☐ Yes  ☐ No  ☐ Did not find it |
| Did the participant understand that their report had become a case? | ☐ Yes  ☐ Partly  ☐ No |

**Operator:** before Task 5, submit the prepared inadequate resolution evidence as the assigned officer and move the case to resolved.

---

**Task 5 — Respond to a resolution you are not satisfied with.** *(Cut-off: 6 minutes.)*

Script: *"The institution has now said the work is finished. Look at what they have recorded, and do whatever you would do about it."*

Do not say that the evidence is inadequate, and do not use the word *dispute*. Whether the participant examines the evidence, forms a judgement, and finds the action is the whole measurement.

| | |
|---|---|
| Did the participant open or look at the resolution photograph? | ☐ Yes  ☐ No |
| Did they say, unprompted, that the work did not look finished? | ☐ Yes  ☐ No |
| Did they find the option to disagree with the resolution? | ☐ Yes  ☐ No  ☐ Found it only after the cut-off prompt |
| Did they use it? | ☐ Yes  ☐ No — they chose not to  ☐ No — they did not find it |
| If they chose not to, what reason did they give? | ______________________________________________ |
| Reason they entered, if they disputed | ______________________________________________ |
| Did they understand what would happen next? | ☐ Yes  ☐ Partly  ☐ No |

*The distinction between "did not find it" and "found it and chose not to use it" is the point of this task. The first is a usability defect; the second is a finding about whether residents will contradict an official result at all. Do not collapse the two.*

---

#### Task record

*One row per task. Time from the end of the script to the participant saying they have finished, or to the cut-off.*

| Task | Start | End | Duration | Outcome | Prompts given | Errors, wrong turns, hesitations observed |
|---|---|---|---|---|---|---|
| 1. Find where to report | | | | ☐ Unaided ☐ With prompt ☐ Not completed ☐ Abandoned (fault) | | |
| 2. Submit report with photo and location | | | | ☐ Unaided ☐ With prompt ☐ Not completed ☐ Abandoned (fault) | | |
| 3. Find the report and its stage | | | | ☐ Unaided ☐ With prompt ☐ Not completed ☐ Abandoned (fault) | | |
| 4. Find the institution and stage | | | | ☐ Unaided ☐ With prompt ☐ Not completed ☐ Abandoned (fault) | | |
| 5. Respond to the resolution | | | | ☐ Unaided ☐ With prompt ☐ Not completed ☐ Abandoned (fault) | | |

*Counting rule, applied identically to every participant: a task counts as successful only if it was completed **unaided**. A task completed after a prompt is recorded as completed with a prompt and is excluded from the success rate, not counted toward it. A task abandoned because of a technical fault is excluded from both the numerator and the denominator, and the exclusion is reported.*

### Section 2. System Usability Scale

*Administer immediately after Task 5, before the debrief, so that the scores are not shaped by the discussion.*

Say: *"Now ten short statements about the application. For each one, tell me how much you agree or disagree. There is no right answer — please give your first reaction rather than thinking about it for long. If a statement does not apply, say so and we will leave it blank."*

Read each statement and mark one box. An italic plain-language gloss is given for each; **read a gloss only if the participant asks what a statement means**, so that the wording stays comparable across participants. Record in Part 4 which glosses were used.

| | Strongly disagree | | | | Strongly agree |
|---|---|---|---|---|---|
| | **1** | **2** | **3** | **4** | **5** |
| **1.** I think that I would like to use this system frequently. — *Would you want to use this often?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **2.** I found the system unnecessarily complex. — *Was it more complicated than it needed to be?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **3.** I thought the system was easy to use. — *Was it easy?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **4.** I think that I would need the support of a technical person to be able to use this system. — *Would you need someone who knows computers to help you?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **5.** I found the various functions in this system were well integrated. — *Did the different parts work together properly?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **6.** I thought there was too much inconsistency in this system. — *Did different parts behave differently when they should have behaved the same?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **7.** I would imagine that most people would learn to use this system very quickly. — *Would most people pick it up quickly?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **8.** I found the system very cumbersome to use. — *Was it heavy going, or awkward?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **9.** I felt very confident using the system. — *Did you feel sure of yourself while using it?* | ☐ | ☐ | ☐ | ☐ | ☐ |
| **10.** I needed to learn a lot of things before I could get going with this system. — *Did you have to learn a lot before you could start?* | ☐ | ☐ | ☐ | ☐ | ☐ |

#### Scoring

The scale is scored as specified by Brooke (1996):

1. For the **odd-numbered** items — 1, 3, 5, 7, 9 — the item score is the position selected **minus 1**. A response of 4 scores 3.
2. For the **even-numbered** items — 2, 4, 6, 8, 10 — the item score is **5 minus** the position selected. A response of 4 scores 1.
3. Each item therefore contributes between 0 and 4.
4. Add the ten item scores, giving a total between 0 and 40.
5. **Multiply the total by 2.5.** The result is the System Usability Scale score for that participant, between 0 and 100.

| Item | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | Sum | × 2.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Position selected | | | | | | | | | | | — | — |
| Item score (0–4) | | | | | | | | | | | | |

**SUS score for this participant: ______ / 100**

*Two points to carry into Chapter Four. First, the score is **not a percentage** and must never be reported as one; it is a figure on a 0–100 scale whose meaning comes from comparison, not from its face value. Second, individual item scores are not reported on their own — the scale is designed to be interpreted only as the combined figure. Report the mean across participants with the number of participants and the range, state the build it was measured on, and keep it as the frozen human-only usability baseline against which the later hybrid configuration is compared. A questionnaire with any item left blank is reported as incomplete and excluded from the mean; say how many were excluded.*

### Section 3. Post-test debrief

*Five to ten minutes, conversational. Write the participant's own words rather than a summary wherever you can.*

**Before starting, close the deception in Task 5.** Say: *"The finished work you were shown in the last task, and its photograph, were prepared by us for this test. It was not real work by any real institution and not by any real person. We set it up that way to see whether the application makes it possible to disagree with a result. Thank you for going along with it."*

**D1.** What was the easiest part of what you did today?
_______________________________________________________________________________

**D2.** What was the most difficult or most annoying part?
_______________________________________________________________________________

**D3.** Was there any moment when you did not know what to do next? What was happening?
_______________________________________________________________________________

**D4.** Was there anything on the screen whose meaning you were not sure of?
_______________________________________________________________________________

**D5.** When you gave the location, how confident were you that it recorded the right place?
☐ Very confident  ☐ Fairly confident  ☐ Not very confident  ☐ Not at all confident

What would have made you more confident? ______________________________________

**D6.** When you saw the stage your report had reached, did the words tell you what you wanted to know?
☐ Yes  ☐ Partly  ☐ No — what was missing: ______________________

**D7.** In the last task, what did you think about what the institution had recorded as finished?
_______________________________________________________________________________

**D8.** Would you use the option to disagree with a result in real life, outside a test?
☐ Yes  ☐ Probably  ☐ Probably not  ☐ No

What would make it harder in real life than it was today? ______________________

**D9.** Did anything about the application worry you where your own information is concerned?
_______________________________________________________________________________

**D10.** If a system like this existed and worked on your phone, how likely would you be to use it?
☐ Very likely  ☐ Likely  ☐ Unlikely  ☐ Very unlikely  ☐ I could not — no suitable phone

**D11.** If you could change **one** thing about it, what would you change?
_______________________________________________________________________________

**D12.** Is there anything you expected it to do that it did not do?
_______________________________________________________________________________

**D13.** Is there anything else you want to tell us?
_______________________________________________________________________________

**Close the session.** Repeat that this is a student project and not a government service, that nothing submitted today reaches any institution, that the test data will be deleted after the analysis, and that the participant may still withdraw their responses. Reimburse transport at cost if applicable, and record it.

---

**Thank you for your time and for trying the prototype.**

For queries about this research, contact the project supervisor, Ing. Oluwatosin B. Ayorinde, Limkokwing University of Creative Technology, Sierra Leone.

---

## Part 4 — Response record

*For the research team. One row per participant. Kept separately from the completed instruments.*

| Field | Entry |
|---|---|
| Participant reference *(e.g. U-07)* | |
| Date, start time, total duration | |
| Facilitator / operator | |
| Consent obtained *(written / verbal)* | |
| Screen recording permitted *(yes / no)* | |
| Audio recording of debrief permitted *(yes / no)* | |
| Language used, and SUS glosses read *(list item numbers)* | |
| Device used *(own phone / project phone — model and browser)* | |
| Test build identifier | |
| Community or ward | |
| Age group | |
| Daily smartphone user *(yes / no)* | |
| Has reported a public-service problem before *(yes / no)* | |
| Also completed the Appendix A questionnaire *(yes / no — reference)* | |
| Tasks completed unaided *(n / 5)* | |
| Tasks completed with a prompt | |
| Tasks not completed | |
| Tasks abandoned through technical fault *(excluded from the rate)* | |
| Report submitted with a category, description, location and photograph *(yes / partial — state what was missing / no)* | |
| Location precision achieved *(exact / approximate / typed / none)* | |
| Moderator decision on the report *(verified / clarification requested)* | |
| Noticed the resolution was inadequate *(yes / no)* | |
| Disputed the resolution *(yes / no — not found / no — chose not to)* | |
| **SUS score** *(0–100, or "incomplete")* | |
| Technical faults during the session | |
| Prompts given, and at which task | |
| Defects observed, with severity *(critical / major / minor)* | |
| Design decisions supported by this session | |
| Design decisions contradicted by this session | |
| Anything the researcher declined to record, and why | |

### Severity definitions for the defect list

| Severity | Meaning |
|---|---|
| **Critical** | The participant could not complete a core task, or completed it in a way that produced the wrong result without realising |
| **Major** | The participant completed the task but was substantially delayed, confused, or needed a prompt |
| **Minor** | The participant noticed a problem or an inconsistency but it did not affect the outcome |

### Session summary across participants

*Completed once all sessions are finished, and carried into Chapter Four.*

| Measure | Value | Notes |
|---|---|---|
| Participants, n | | |
| Report completion rate *(unaided completions of Task 2 ÷ attempts)* | | |
| Clarification rate *(reports a moderator returned for clarification ÷ reports submitted)* | | |
| Dispute rate *(participants who disputed ÷ participants who reached Task 5)* | | |
| Participants who noticed the resolution was inadequate but did not dispute | | |
| Mean SUS score, with range | | |
| SUS questionnaires excluded as incomplete | | |
| Median time, Task 2 | | |
| Critical defects | | |

---

## Reference

Brooke, J. (1996) 'SUS: a "quick and dirty" usability scale', in Jordan, P.W., Thomas, B., Weerdmeester, B.A. and McClelland, I.L. (eds.) *Usability Evaluation in Industry*. London: Taylor & Francis, pp. 189–194.
