# SaloneFix — Resident and Citizen Questionnaire

**Appendix A: Data-collection instrument for residents of Freetown**

| | |
|---|---|
| **Project** | SaloneFix: A Human-First Public-Service Reporting and Accountability Platform for Freetown, Sierra Leone |
| **Students** | Ina M. E. Conteh (905004473) · Sahid A. G. Conteh (905004265) · Mark Lamin Ellie (905004456) |
| **Department / Faculty** | FICT / BSEM |
| **Institution** | Limkokwing University of Creative Technology, Sierra Leone |
| **Supervisor** | Ing. Oluwatosin B. Ayorinde |
| **Intended respondents** | Adult residents of Freetown and its surrounding communities |
| **Version / date** | 1.0 — *(insert date of use)* |

---

## Part 1 — Notes for the research team

*This part is for the students. Remove these pages before giving the instrument to a respondent.*

### 1.1 Purpose

This instrument collects the resident-side evidence for **Objective 1** of the study — to investigate the information, verification, privacy, and workflow requirements for a public-service reporting platform in Freetown — from the people who would be submitting the reports. Its institutional counterpart is Appendix B; the two are designed to be read against each other, and the places where residents and institutions disagree are themselves a finding.

It also does a second job. Several citizen-facing design decisions in the SaloneFix prototype were taken from the specification rather than from evidence about how residents actually behave: the four initial categories, the optional photograph, the three-way classification of how precisely a location was captured, the reference number as the means of tracking a case, the review of every report by a person before it becomes a case, and the citizen's ability to dispute a resolution and reopen a case. Sections E to L are written to test those decisions. Where the answers contradict the design, that contradiction belongs in Chapter Four as a result, not smoothed over.

Section C is additionally a baseline measure. It establishes what residents do **today**, without the prototype, so that anything observed during user acceptance testing can be interpreted against existing behaviour rather than in isolation.

### 1.2 How to administer it

This instrument is written to be **read aloud by a researcher and filled in by the researcher**, not handed over for self-completion, because literacy, language, and familiarity with questionnaires vary widely in the intended sample. Self-completion is acceptable where a respondent prefers it and is comfortable doing so.

- **Researcher-administered, face to face.** Sections A to M, approximately 20–25 minutes. This is the default mode.
- **Self-completion.** The same sections, approximately 15–20 minutes. Offer it only where the respondent asks for it.

Sections E to L ask about the prototype. Before starting Section E, show the respondent the submission screen on a phone or laptop and let them look at it for a minute; several questions cannot be answered meaningfully by someone who has never seen the interface. Where the respondent has just taken part in the usability session in Appendix F, note that on the record sheet, because their answers to Sections E to L are then informed by use rather than by inspection, and the two groups should be reported separately.

Aim for variation rather than a large number: different wards, a spread of ages, both men and women, and a deliberate effort to include residents who do not own a smartphone and residents who have never reported a problem to any institution. A sample drawn only from people who already report, and already own smartphones, will overstate how usable and how welcome the platform is. The composition of the achieved sample is a stated limitation and must be reported in Chapter Four.

Mark a question **N/A** rather than inferring an answer, and record which questions were skipped.

### 1.3 Ethical rules for this instrument

These rules follow from the undertakings given in the project's request letters — that only non-confidential information would be sought, that all information would be used strictly for academic purposes, and that it would be treated confidentially — and from the project's own governance commitments. The same posture applies to residents as to institutions.

1. **Obtain recorded consent before the first question.** Use the statement in Part 2. Written consent is preferred; note verbal consent in writing where a signature is not practical, which will often be the case.
2. **Collect no more personal data than the study needs.** Do not record names, addresses, house numbers, telephone numbers, national identification numbers, or photographs of the respondent. The ward or community name in A2 is recorded at community level only. A respondent who volunteers identifying detail should not have it written down.
3. **Do not ask about, or record, the honesty or conduct of any named person.** This instrument examines *experiences and processes*, never whether any official, contractor, neighbour, or community leader has behaved dishonestly. No question may be reworded in the field to invite an allegation against an individual. If a respondent begins to make one, thank them, explain that the study cannot record it, and move to the next question. The project's rules prohibit attaching findings of dishonesty to any person, and that prohibition binds data collection exactly as it binds the software.
4. **Do not present the prototype as a government service, an adopted system, or a forthcoming one.** It is a student prototype built for a dissertation. Say so in those words at the start. No question may imply that reports made through it will reach an institution, that any institution has agreed to use it, or that a problem the respondent mentions will be fixed. Raising an expectation that cannot be met would be a harm to the participant, not merely an inaccuracy.
5. **Do not take a real report.** If a respondent describes a current problem and asks for help, explain that the study cannot pass it on, and direct them to the ordinary channel they would otherwise use.
6. **Participation is voluntary throughout.** Any question may be declined, and consent may be withdrawn at any point afterwards, without a reason being given.
7. **No payment or inducement.** Refreshment during a session is acceptable; payment for participation is not, because it would bias who agrees to take part and what they say.

### 1.4 Language

Administer the instrument in whichever of English or Krio the respondent is more comfortable with, and record which was used, because it bears on how the answers should be read.

The table below gives suggested Krio prompts for the terms that carry the most meaning in this instrument. They are a starting point for the administering researcher, **not** a validated translation: confirm the wording with a Krio speaker before fieldwork begins, keep the wording identical across respondents once settled, and record in Part 4 the wording actually used.

| Term in the questionnaire | Suggested Krio prompt |
|---|---|
| To report a problem | *Fɔ tɛl dɛn bɔt wan problɛm* |
| Damaged road, pothole | *Ol na di rod* |
| Blocked drainage, flooding | *Gɔta we blɔk, wata we flod* |
| Waste, rubbish accumulation | *Dɔti we gada* |
| Public facilities | *Ples dɛn we ɔlman de yuz — makit, toilet, layt na rod* |
| Photograph | *Foto, piksha* |
| Location | *Di ples usai di problɛm de* |
| Landmark | *Sɔntin we pipul dɛn no na di eria* |
| Status of your report | *Wetin apin to yu rɛpɔt* |
| Reference number | *Di nɔmba we dɛn gi yu fɔ yu rɛpɔt* |
| To dispute a resolution | *Fɔ tɔk se di wok nɔ dɔn gud* |
| Private, not shown publicly | *Nɔbɔdi nɔ go si am pas di wan dɛn we gɛt rayt* |
| Student project, not a government service | *Na stɔdɛnt wok, i nɔto gɔvmɛnt sɔvis* |

### 1.5 What each section feeds

| Section | Feeds |
|---|---|
| A | Sample description; representativeness of the achieved sample |
| B | Device and connectivity constraints; non-functional requirements; limitations in Chapter One §1.10 |
| C | Baseline reporting behaviour; Chapter Three existing-system analysis; comparison against institutional intake in Appendix B §B1 |
| D | Trust and expectation baseline; interpretation of willingness to use in Section L |
| E | Clarity of the submission flow; **report completion rate** in the evaluation protocol |
| F | Category design; whether four categories are sufficient; mis-categorisation risk |
| G | Description quality; **clarification rate** in the evaluation protocol |
| H | Location-precision design (exact / approximate / user-entered); confidence in location capture |
| I | Media requirements; ease of attaching evidence; optional-photograph decision |
| J | Status vocabulary and tracking design; understanding of what each status means |
| K | Perceived fairness of human review; **dispute rate** in the evaluation protocol |
| L | Privacy defaults; location and media disclosure rules; willingness to use |
| M | Preferred feedback channels; adoption barriers; Chapter Five recommendations |

Sections E, G, K, and L are the ones that bear directly on the human-only metrics in the evaluation protocol. Where a measured rate from the prototype and a self-reported answer here disagree, report both and say which is which; a self-reported intention is not a measurement.

---

## Part 2 — Participant information and consent

*Read this page aloud to the respondent and keep the signed or recorded copy.*

### 2.1 About the research

Three final-year students at Limkokwing University of Creative Technology, Sierra Leone, are carrying out a university project about how residents report public-service problems in Freetown, and how those reports are handled.

As part of the project the students have built a **prototype** — a test version of a web application — in which a resident can report a problem with a road, a drain, waste, or a public facility; a person then checks the report; it is passed to the institution responsible; and the resident can follow what happens to it.

**This is a student project for a university dissertation. It is not a government service. It has not been adopted by any institution, and we cannot promise that it ever will be.** Nothing you say here will be passed to any institution as a complaint, and taking part will not get any problem fixed. We are asking for your views so that the project can be assessed, and so that the students can report honestly on what residents would actually need.

### 2.2 What participation involves

Answering questions for about 20 to 25 minutes. A researcher will read the questions to you and write down your answers, unless you prefer to fill the form in yourself. You may also be shown the prototype on a phone or laptop for a minute so that some of the questions make sense.

### 2.3 Your rights

- Taking part is entirely your choice, and there is no payment for taking part.
- You may refuse any individual question.
- You may stop at any time, and you may ask us afterwards to remove your answers, without giving a reason.
- **We will not write down your name, your address, your telephone number, or any identification number.** Your answers are recorded under a reference such as R-014, and only your community and a broad age group are noted.
- We will not ask you anything about the honesty or behaviour of any particular person, and we cannot record such a statement if you make one.
- Your answers are used only for this university dissertation and its assessment.
- Notes are kept securely and are seen only by the three students and their supervisor.

### 2.4 Consent

Please complete:

| | |
|---|---|
| The researcher has explained the project to me and I understood the explanation | ☐ Yes  ☐ No |
| I understand that this is a student project and **not** a government service, and that no problem I mention will be fixed because of it | ☐ Yes  ☐ No |
| I agree to take part | ☐ Yes  ☐ No |
| I understand that my name and contact details will not be recorded | ☐ Yes  ☐ No |
| I understand that I may stop at any time, or withdraw my answers afterwards | ☐ Yes  ☐ No |

| | |
|---|---|
| Participant reference *(assigned by the researcher, e.g. R-014)* | |
| Consent given | ☐ In writing (signature below)  ☐ Verbally, witnessed by the researcher |
| Signature or mark *(optional)* | |
| Date | |
| Researcher present | |
| Language used | ☐ English  ☐ Krio  ☐ Both  ☐ Other: ______________ |

---

## Part 3 — Questionnaire

### Section A. About you

*These questions describe the group of people who took part. They do not identify you.*

**A1.** Which age group are you in?
☐ 18–24  ☐ 25–34  ☐ 35–44  ☐ 45–54  ☐ 55–64  ☐ 65 or over  ☐ Prefer not to say

**A2.** Which community or ward do you live in? *(community name only — no address)* ______________________

**A3.** How long have you lived there? ☐ Under 1 year  ☐ 1–5 years  ☐ 6–15 years  ☐ Over 15 years

**A4.** Gender: ☐ Female  ☐ Male  ☐ Prefer not to say  ☐ Prefer to self-describe: ______________

**A5.** What is the highest level of schooling you completed?
☐ None  ☐ Primary  ☐ Secondary  ☐ Technical or vocational  ☐ University  ☐ Prefer not to say

**A6.** Which language are you most comfortable reading?
☐ Krio  ☐ English  ☐ Both equally  ☐ Another language: ______________  ☐ I do not read easily

**A7.** Which of these problems affect the place you live? *(tick all that apply)*
☐ Damaged roads or potholes  ☐ Blocked drains or flooding  ☐ Waste or rubbish not collected  ☐ Damaged public facilities such as markets, public toilets, or street lighting  ☐ Water supply  ☐ Street lighting  ☐ None of these  ☐ Other: ______________

**A8.** Which **one** of those affects you most? ______________________

### Section B. Your phone and internet

*This tells us what the system has to work on, and what it cannot assume.*

**B1.** What kind of phone do you use most?
☐ Smartphone with internet  ☐ Basic phone, calls and SMS only  ☐ I use someone else's phone  ☐ No phone

**B2.** If you have a smartphone, is it ☐ yours alone  ☐ shared with family  ☐ not applicable

**B3.** How do you usually get internet on it?
☐ Mobile data that I buy  ☐ Wi-Fi at home  ☐ Wi-Fi at work or school  ☐ Someone else's hotspot  ☐ I do not use the internet

**B4.** How often is your internet good enough to load a web page or send a photograph?
☐ Most of the time  ☐ About half the time  ☐ Rarely  ☐ Almost never  ☐ I do not use the internet

**B5.** How much does the cost of data affect what you do on your phone?
☐ Not at all  ☐ A little  ☐ A lot  ☐ It stops me doing things I would otherwise do

**B6.** Would sending a photograph with a report be a problem for you because of data cost or slow internet?
☐ Not a problem  ☐ Sometimes a problem  ☐ Often a problem  ☐ I could not send a photograph at all

**B7.** Which of these do you use at least weekly? *(tick all that apply)*
☐ WhatsApp  ☐ Facebook  ☐ SMS  ☐ Email  ☐ A web browser  ☐ A banking or money app  ☐ None of these

**B8.** How comfortable are you filling in a form on a phone or computer?
☐ Very comfortable  ☐ Fairly comfortable  ☐ Not very comfortable  ☐ I would need someone to help me  ☐ I could not do it

### Section C. What you do today when there is a problem

*These questions are about your experience now, before and apart from this project.*

**C1.** Have you ever reported a public-service problem — a road, a drain, waste, water, or a public facility — to anyone in authority?
☐ Yes, more than once  ☐ Yes, once  ☐ No, never  → *if No, go to C7*

**C2.** The last time you reported something, how did you report it? *(tick all that apply)*
☐ Went to an office in person  ☐ Telephoned  ☐ WhatsApp or SMS  ☐ Social media  ☐ Radio programme  ☐ Told a ward councillor or community leader  ☐ Told a community or youth group  ☐ Wrote a letter  ☐ Through an existing app or website  ☐ Other: ______________

**C3.** Roughly how long did it take you to make that report, including travel and waiting?
☐ Under 15 minutes  ☐ 15–60 minutes  ☐ Several hours  ☐ More than one day  ☐ I do not remember

**C4.** Did it cost you anything — transport, airtime, time away from work?
☐ Nothing  ☐ A small amount  ☐ A significant amount  ☐ I do not remember

**C5.** What happened after you reported it?
☐ The problem was fixed  ☐ Someone came to look but nothing was fixed  ☐ I was told something would be done, and nothing was  ☐ I heard nothing at all  ☐ I was told it was not their responsibility  ☐ I do not know what happened  ☐ Other: ______________

**C6.** Were you ever told what was happening with your report?
☐ Yes, and it was clear  ☐ Yes, but it was not clear  ☐ Only when I went back and asked  ☐ No, never

**C7.** *(For everyone, including those who have never reported.)* What stops people in your community from reporting problems? *(tick all that apply, then circle the single biggest)*
☐ Not knowing who to report to  ☐ Not knowing how to report  ☐ Believing nothing will be done  ☐ The office is too far  ☐ Cost of transport or airtime  ☐ No time  ☐ Fear of trouble or of being blamed  ☐ Language or reading difficulty  ☐ Someone else will report it  ☐ Other: ______________

**C8.** In the last year, roughly how many problems did you notice that you did **not** report?
☐ None  ☐ 1–2  ☐ 3–5  ☐ More than 5  ☐ Too many to count

**C9.** Is there anyone in your community who reports problems on behalf of others?
☐ Yes — who, by role, not by name: ______________________  ☐ No  ☐ I do not know

### Section D. What you expect from institutions

*Please answer about institutions generally. Do not name any person.*

**D1.** If you reported a damaged road, a blocked drain, or uncollected waste today, how likely do you think it is that it would be fixed within three months?
☐ Very likely  ☐ Fairly likely  ☐ Unlikely  ☐ Very unlikely  ☐ I do not know

**D2.** How confident are you that a report you made would reach the right institution at all?
☐ Very confident  ☐ Fairly confident  ☐ Not very confident  ☐ Not at all confident

**D3.** In your experience, which matters more in getting something fixed?
☐ Making a formal report  ☐ Knowing someone  ☐ Many people complaining together  ☐ Where the problem is located  ☐ All of these equally  ☐ I do not know

**D4.** How much do you agree with each statement? *(1 = strongly disagree, 5 = strongly agree)*

| | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Problems in my community are fixed more slowly than in other parts of Freetown | ☐ | ☐ | ☐ | ☐ | ☐ |
| If I report a problem, somebody will at least read it | ☐ | ☐ | ☐ | ☐ | ☐ |
| Being told honestly that a problem cannot be fixed is better than hearing nothing | ☐ | ☐ | ☐ | ☐ | ☐ |
| I would report more often if I could see what happened to my report | ☐ | ☐ | ☐ | ☐ | ☐ |
| Seeing a photograph of the completed work would convince me a problem was really fixed | ☐ | ☐ | ☐ | ☐ | ☐ |

**D5.** What would most increase your confidence that a report leads to action?
_______________________________________________________________________________

### Section E. Making a report in the prototype — is it clear?

*Before this section, show the respondent the submission screen. The prototype asks for four things in order: the type of problem, a description, the location, and a photograph if the person has one. The photograph is optional.*

**E1.** Looking at the submission screen, how clear is it what you are being asked to do?
☐ Very clear  ☐ Fairly clear  ☐ Confusing in places  ☐ Very confusing

**E2.** Does the order of the steps — type of problem, description, location, photograph — make sense to you?
☐ Yes  ☐ Mostly  ☐ No — what would you change: ______________________

**E3.** Which step, if any, looks like it would be hardest? *(tick one)*
☐ Choosing the type of problem  ☐ Writing the description  ☐ Giving the location  ☐ Taking or attaching the photograph  ☐ None looks hard

Why? ___________________________________________________________________________

**E4.** Is there anything on the screen you do not understand the meaning of?
_______________________________________________________________________________

**E5.** How long would you be willing to spend making one report?
☐ Under 1 minute  ☐ 1–3 minutes  ☐ 3–5 minutes  ☐ As long as it takes  ☐ I would not make a report

**E6.** Would you be able to complete a report like this without anyone helping you?
☐ Yes, on my own  ☐ Yes, with a little help the first time  ☐ Only with someone helping  ☐ No

**E7.** Should it be possible to make a report **without** creating an account or signing in?
☐ Yes, it should be possible  ☐ No, signing in is reasonable  ☐ It does not matter to me

Please say why: _________________________________________________________________

**E8.** Would you prefer to report in Krio rather than English, if the choice existed?
☐ Krio  ☐ English  ☐ Either is fine  ☐ Another language: ______________

### Section F. Choosing the type of problem

*The prototype offers four types: damaged roads and potholes; blocked drainage and flooding; waste and rubbish; damaged public facilities.*

**F1.** Are those four types clear to you?
☐ All four are clear  ☐ Some are clear  ☐ They are not clear

Which, if any, are unclear? ______________________________________________________

**F2.** For each problem below, which type would you choose?

| The problem you saw | Which type would you pick? |
|---|---|
| A large hole in the road that damages vehicles | |
| Water standing in the street after rain because the gutter is blocked | |
| Rubbish piled at a junction for several weeks | |
| A public toilet at the market that is broken | |
| A street light that does not work | |
| A burst water pipe in the street | |

**F3.** Were any of those difficult to place in one of the four types?
☐ Yes — which: ______________________  ☐ No

**F4.** What other kinds of problem should this system accept, in your view?
_______________________________________________________________________________

**F5.** If you were not sure which type to choose, what would you do?
☐ Pick the closest one  ☐ Pick any one  ☐ Give up and not report  ☐ Ask someone  ☐ Other: ______________

### Section G. Describing the problem

*In the prototype a person — not a machine — reads each description. If it is not clear enough, that person can send back a question before the report becomes a case.*

**G1.** How easy would it be for you to write a description of a problem?
☐ Very easy  ☐ Fairly easy  ☐ Difficult  ☐ I would need help  ☐ I would prefer to speak rather than write

**G2.** How long a description would you be willing to write?
☐ A few words  ☐ One or two sentences  ☐ A short paragraph  ☐ As much as needed

**G3.** Which of these would you naturally include without being asked? *(tick all that apply)*
☐ What the problem is  ☐ Where exactly it is  ☐ How long it has been there  ☐ How dangerous it is  ☐ How many people it affects  ☐ Whether anyone has been hurt  ☐ What you think should be done

**G4.** Would it help if the form gave you prompts — for example, *"How long has this been here?"* — rather than one empty box?
☐ Yes, much better  ☐ A little better  ☐ No, an empty box is fine

**G5.** If the person reviewing your report sent back a question, such as *"Which end of the street is the hole?"*, would you answer it?
☐ Yes, straight away  ☐ Yes, if it was easy  ☐ Probably not  ☐ No

**G6.** How would you want to receive that question? *(tick up to two)*
☐ Inside the app  ☐ SMS  ☐ WhatsApp  ☐ Telephone call  ☐ Email  ☐ I would not want to be contacted

**G7.** Would being asked a follow-up question make you feel your report was being taken seriously, or make it feel like too much trouble?
☐ Taken seriously  ☐ Too much trouble  ☐ Depends on the question  ☐ Unsure

### Section H. Giving the location

*The prototype tries to take the location from the phone. If the phone's position is good it records the exact place; if it is less accurate it records an approximate place; and if there is no position at all the person types a landmark instead. The system keeps a note of which of the three happened.*

**H1.** Would you allow the app to use your phone's location for a report?
☐ Yes, always  ☐ Yes, but only while reporting  ☐ No  ☐ I do not know how

**H2.** If not, or not always, what is your concern?
☐ Battery or data  ☐ Being tracked  ☐ Someone knowing where I live  ☐ I do not understand what it does  ☐ Other: ______________

**H3.** How confident would you be that the location recorded is the right one?
☐ Very confident  ☐ Fairly confident  ☐ Not very confident  ☐ Not at all confident

**H4.** If the phone could not find your position, would you be able to describe the place in words so that a work team could find it?
☐ Yes, easily  ☐ Yes, with effort  ☐ Difficult  ☐ No

**H5.** How do people in your area normally describe where something is? *(tick all that apply)*
☐ By a landmark — a building, a junction, a tree, a market  ☐ By street name  ☐ By the name of a person's house or shop  ☐ By a bus or poda-poda stop  ☐ By the community name only  ☐ Other: ______________

**H6.** Would you report a problem that is **not** where you are standing — for example, one you saw earlier?
☐ Yes, often  ☐ Sometimes  ☐ No

If yes, how would you give its location? ________________________________________

**H7.** Should the system tell you how precisely it recorded your location — for example, *"exact"*, *"approximate"*, or *"you typed this"*?
☐ Yes, it should say  ☐ It does not matter  ☐ No, that would confuse me

**H8.** Would you be willing to report a problem at a place where you do not want anyone to know you were present?
☐ Yes  ☐ No  ☐ It depends — explain: ______________________

### Section I. Attaching a photograph

*In the prototype the photograph is optional. Photographs sent in are kept private: only authorised staff can open them, and the hidden location information inside the picture file is removed before it is stored.*

**I1.** Would you normally take a photograph of a problem like this?
☐ Yes, usually  ☐ Sometimes  ☐ Rarely  ☐ No

**I2.** How easy would it be for you to attach a photograph to a report?
☐ Very easy  ☐ Fairly easy  ☐ Difficult  ☐ I would not know how  ☐ My phone cannot do it

**I3.** What would stop you attaching one? *(tick all that apply)*
☐ Data cost  ☐ Slow internet  ☐ Phone storage  ☐ Camera quality  ☐ Not safe to stop and take a photograph there  ☐ Not wanting to be seen taking a photograph  ☐ Nothing would stop me  ☐ Other: ______________

**I4.** Should the photograph be required, or should it stay optional?
☐ Required — a report without one is too weak  ☐ Optional — people without a camera must still be able to report  ☐ Unsure

**I5.** Would you be more or less willing to attach a photograph knowing it is **not** shown to the public?
☐ Much more willing  ☐ A little more willing  ☐ No difference  ☐ I would want it shown publicly

**I6.** Would you be worried about a photograph you sent accidentally showing a person, a vehicle number plate, or the front of someone's house?
☐ Very worried  ☐ A little worried  ☐ Not worried  ☐ I had not thought of it

**I7.** Would it reassure you to know that the hidden location recorded inside a photograph file is removed before the picture is stored?
☐ Yes  ☐ It makes no difference  ☐ I do not understand what that means

### Section J. Following what happens to your report

*After a report is submitted the prototype gives it a reference number, such as SF-2026-000123. The person who reported can look it up and see what stage it has reached — being checked, accepted as a case, given to an institution, work started, work finished and being checked, finished, or closed.*

**J1.** How important is it to you to be able to see what happened to your report?
☐ Essential  ☐ Important  ☐ Slightly important  ☐ Not important

**J2.** Would you be able to keep a reference number such as SF-2026-000123 and use it later?
☐ Yes, easily  ☐ Yes, if I wrote it down  ☐ Probably lose it  ☐ No

**J3.** Would you rather find your reports by signing in than by using a reference number?
☐ Signing in  ☐ Reference number  ☐ Both should work  ☐ No preference

**J4.** For each stage below, say whether the wording is clear to you, and what you think it means.

| The system says | Clear? | What do you understand by it? |
|---|---|---|
| Submitted | ☐ Clear ☐ Unclear | |
| Under review | ☐ Clear ☐ Unclear | |
| More information needed | ☐ Clear ☐ Unclear | |
| Verified | ☐ Clear ☐ Unclear | |
| Joined to an existing case | ☐ Clear ☐ Unclear | |
| Not accepted | ☐ Clear ☐ Unclear | |
| Assigned to an institution | ☐ Clear ☐ Unclear | |
| Work in progress | ☐ Clear ☐ Unclear | |
| Work finished, being checked | ☐ Clear ☐ Unclear | |
| Resolved | ☐ Clear ☐ Unclear | |
| Closed | ☐ Clear ☐ Unclear | |

**J5.** Is there any difference, to you, between a case being *resolved* and a case being *closed*?
_______________________________________________________________________________

**J6.** If your report was **not accepted**, what would you want to be told?
☐ Just that it was not accepted  ☐ The reason  ☐ The reason and who decided  ☐ What I could do next  ☐ Nothing

**J7.** If your report was joined to an existing case because other people had reported the same problem, how would that feel?
☐ Fine — it is the same problem  ☐ I would want to know my report was still counted  ☐ I would feel my report was ignored  ☐ Unsure

**J8.** How often would you want to hear about progress on a case?
☐ At every change  ☐ Only at important changes  ☐ Only when it is finished  ☐ Only if I ask  ☐ Not at all

### Section K. Review, fairness and disputing a result

*Every report in the prototype is read by a person before it becomes a case; no machine decides. When an institution says the work is done, the person who reported it can say they disagree, and the case is reopened and looked at again.*

**K1.** Knowing that a person, not a machine, reads each report — does that make you more or less willing to report?
☐ Much more willing  ☐ A little more willing  ☐ No difference  ☐ Less willing

Why? ___________________________________________________________________________

**K2.** Do you think reports from all parts of Freetown would be treated equally in a system like this?
☐ Yes  ☐ Probably  ☐ Probably not  ☐ No  ☐ I do not know

What would make it fairer? _____________________________________________________

**K3.** If only one person reports a problem and nobody else does, should it be treated as seriously as a problem many people reported?
☐ Just as seriously  ☐ Somewhat less seriously  ☐ It is reasonable to treat it as less urgent  ☐ Unsure

**K4.** If your report was not accepted, how fair would you consider that?
☐ Fair if a reason is given  ☐ Fair only if I can ask again  ☐ Unfair whatever the reason  ☐ Unsure

**K5.** If an institution said a problem was fixed and it was **not** fixed, would you use a button in the app to say so?
☐ Yes, certainly  ☐ Probably  ☐ Probably not  ☐ No

If probably not or no, why? ____________________________________________________

**K6.** What would stop you from disagreeing with an official result? *(tick all that apply)*
☐ Nothing would stop me  ☐ Fear of trouble  ☐ Belief that it would change nothing  ☐ Not wanting to cause offence  ☐ Too much effort  ☐ Not being sure enough  ☐ Other: ______________

**K7.** Who should decide whether a disputed case is really unfinished?
☐ The institution that did the work  ☐ Someone independent of that institution  ☐ The person who reported it  ☐ A community representative  ☐ Unsure

**K8.** Should the photograph of the completed work be shown to the person who reported the problem?
☐ Yes  ☐ No  ☐ Unsure

### Section L. Privacy, and whether you would use it

**L1.** How concerned would you be about each of the following?

| | Not concerned | A little concerned | Very concerned | Unsure |
|---|---|---|---|---|
| The system knowing who made a report | ☐ | ☐ | ☐ | ☐ |
| The system recording where I was when I reported | ☐ | ☐ | ☐ | ☐ |
| Other members of the public seeing that a report exists | ☐ | ☐ | ☐ | ☐ |
| Other members of the public seeing the exact place reported | ☐ | ☐ | ☐ | ☐ |
| Other members of the public seeing my photograph | ☐ | ☐ | ☐ | ☐ |
| Officials knowing my name | ☐ | ☐ | ☐ | ☐ |
| Someone in my community finding out that I reported | ☐ | ☐ | ☐ | ☐ |
| My phone number being stored | ☐ | ☐ | ☐ | ☐ |

**L2.** Which single one of those worries you most, and why?
_______________________________________________________________________________

**L3.** The prototype shows only an approximate place to anyone outside the institutions, and keeps the exact position for the staff handling the case. Is that the right balance?
☐ Right  ☐ Still too open  ☐ Too secretive — more should be public  ☐ Unsure

**L4.** Should it be possible to report **without giving your name to the institution**?
☐ Yes, anonymous reporting should be possible  ☐ No, reports should be named  ☐ There should be a choice each time  ☐ Unsure

**L5.** If reporting were anonymous, would you report more?
☐ Much more  ☐ A little more  ☐ No difference  ☐ I would report less

**L6.** Suppose a system like this existed and worked on your phone. How likely would you be to use it?
☐ Very likely  ☐ Likely  ☐ Unlikely  ☐ Very unlikely  ☐ I could not use it — no suitable phone

**L7.** What would make you stop using it after the first time? *(tick all that apply)*
☐ Nothing happened to my report  ☐ It was too slow or difficult  ☐ It used too much data  ☐ I did not trust it with my information  ☐ Nobody else was using it  ☐ Other: ______________

**L8.** Would you recommend it to a neighbour?
☐ Yes  ☐ Perhaps  ☐ No  ☐ Unsure

### Section M. Feedback channels and closing questions

**M1.** The prototype currently gives all its messages **inside the application itself** — there is no SMS and no WhatsApp. How well would that work for you?
☐ Fine, I would check the app  ☐ I would probably miss messages  ☐ It would not work for me at all

**M2.** How would you most want to be told what is happening with your report? *(rank 1 = most preferred, leave blank if unwanted)*

| | Rank |
|---|---|
| A message inside the app | |
| SMS | |
| WhatsApp | |
| Telephone call | |
| Email | |
| Through a community leader or ward councillor | |
| Notice at a community meeting | |
| Radio announcement | |
| Nothing — I would check myself | |
| Other: ______________________ | |

**M3.** Would you want a message for every change, or only for a few?
☐ Every change  ☐ Only important ones  ☐ Only the final result  ☐ None

**M4.** If a message cost you data to receive or to read, would you still want it?
☐ Yes  ☐ Only for important changes  ☐ No

**M5.** Would you use a system like this on someone else's phone — at a community centre, a school, or a neighbour's — if you did not have your own?
☐ Yes  ☐ Perhaps  ☐ No  ☐ Not applicable

**M6.** Is there anything about reporting problems in your community that these questions have missed?
_______________________________________________________________________________
_______________________________________________________________________________

**M7.** Would you be willing to try the prototype and tell us what you think, at a later session?
☐ Yes  ☐ No  ☐ Perhaps

*If yes, do not record contact details here. Arrange the follow-up through the community contact already agreed for this study, and note the arrangement on the record sheet.*

---

**Thank you for your time.**

*Reminder for the researcher: before ending, repeat that this is a student project, that no report made today will be passed to any institution, and that the respondent may still withdraw their answers.*

For queries about this research, contact the project supervisor, Ing. Oluwatosin B. Ayorinde, Limkokwing University of Creative Technology, Sierra Leone.

---

## Part 4 — Response record

*For the research team. One row per respondent. This sheet is kept separately from the completed questionnaires.*

| Field | Entry |
|---|---|
| Participant reference *(e.g. R-014)* | |
| Community or ward | |
| Age group | |
| Mode *(researcher-administered / self-completed)* | |
| Language used, and Krio wording applied | |
| Date and duration | |
| Consent obtained *(written / verbal)* | |
| Was the prototype shown before Section E? *(yes / no)* | |
| Has this respondent also taken part in the Appendix F usability session? *(yes / no)* | |
| Phone type *(smartphone / basic / none)* | |
| Has reported a problem before *(yes / no)* | |
| Questions declined or N/A | |
| Design decisions supported by this response | |
| Design decisions contradicted by this response | |
| Anything the researcher declined to record, and why | |
| Follow-up agreed, and through which community contact | |
