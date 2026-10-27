# SaloneFix: An AI-Powered Integrity and Accountability Platform for Public-Service Reporting in Sierra Leone

**Chapter One: Introduction**

| | |
|---|---|
| **Students** | Ina M. E. Conteh (905004473) · Sahid A. G. Conteh (905004265) · Mark Lamin Ellie (905004456) |
| **Department** | FICT |
| **Faculty** | BSEM |
| **Institution** | Limkokwing University of Creative Technology |
| **Degree Programme** | Bachelor (Hons) in Software Engineering and Multimedia |
| **Supervisor** | Ing. Oluwatosin B. Ayorinde |
| **Date** | *(insert submission date)* |

---

## 1.1 Background of the Study

Public-service institutions depend on reliable information to identify infrastructure problems, prioritise interventions, deploy field teams, and communicate progress to the people they serve. A digital reporting platform can improve that flow of information by allowing residents to submit complaints about roads, drainage, waste, water access, public facilities, and related services. The existence of a reporting channel, however, does not by itself produce reliable accountability data.

Citizen reporting treats residents as distributed sensors who observe and describe local conditions (Goodchild, 2007). Research on transparency initiatives has consistently found that disclosure alone does not produce accountability: information must be credible, it must reach an actor with the capacity to respond, and that response must be observable (Fung, Graham and Weil, 2007). Reviews of information-and-communication-technology-enabled citizen voice reach a similar conclusion, finding that responsiveness depends on institutional conditions rather than on the technology itself (Peixoto and Fox, 2016).

The value of a civic-reporting system therefore depends on whether submitted reports are accurate, sufficiently specific, non-duplicative, geographically useful, and connected to verifiable action. Low-quality or malicious submissions create operational noise. Duplicate reports can make a single incident appear more widespread or more severe than it is. A report may be incorrectly categorised and routed to an institution that cannot act on it. More seriously, a case may be marked as resolved without adequate evidence that the underlying problem was addressed. Together these weaknesses create a trust gap in both directions: citizens stop reporting because they do not believe reports lead to action, and institutions stop relying on the platform because they consider its data unreliable.

This project is situated within Sierra Leone's wider movement toward digital government and more transparent public institutions. The Open Government Partnership identifies citizen participation, transparency, public access to information, and feedback mechanisms among Sierra Leone's open-government commitments (Open Government Partnership, 2021–2023). The World Bank has emphasised strengthening community-level participation so that citizens can influence and monitor decisions affecting services such as water, schools, health, and agriculture (World Bank, 2026), and its digital-economy diagnostic describes digital technologies as an opportunity for public-service innovation while identifying infrastructure and digital-capacity constraints that condition what is realistic (World Bank, 2021). The African Development Bank's DIGEST project similarly links digital solutions with governance efficiency and public-sector transformation (African Development Bank, 2025).

SaloneFix responds to this context. It is designed not merely to collect complaints but to evaluate the quality and consistency of the evidence attached to a report before that report reaches an institution, and to make the subsequent institutional response auditable. The design combines four mechanisms: human-in-the-loop moderation, spatial corroboration between nearby reports, evidence checks on resolution submissions, and — in a later phase — AI-assisted multimodal classification that compares image, text, and spatial context together (Baltrušaitis, Ahuja and Morency, 2019). Human-in-the-loop design is retained throughout, so that uncertain or contested decisions remain the responsibility of an accountable person rather than a model (Amershi *et al.*, 2019; Wu *et al.*, 2022).

One framing point requires explicit correction at the outset. Early project material described the platform as a means of producing a "100% trustworthy dataset". That claim is not defensible. No automated platform can guarantee absolute truth when users can manipulate inputs, when image metadata can be stripped or altered, and when field conditions change between observation and inspection. This study therefore adopts the weaker and more defensible objective of producing higher-confidence, more auditable, and more operationally useful civic-reporting data, and of measuring whether it does so.

## 1.2 Problem Statement

Existing public-service reporting processes tend to focus on receiving and forwarding complaints rather than on verifying the quality of the information before institutional action is taken. Five related problems follow.

**First, the noise problem.** Residents or automated systems may submit low-quality, duplicated, mislocated, or deliberately false reports. Such noise reduces the signal-to-noise ratio of the reporting dataset and causes institutions to spend limited field resources on cases that do not warrant them.

**Second, the single-source verification gap.** One image and one text description are often insufficient to establish that a problem exists, that it is located where it was reported, and that it remains unresolved. A report may consequently be routed to an inappropriate institution or assigned an inappropriate priority.

**Third, the automation-error problem.** Automated classification can fail. An image may be unclear, the text may contradict the image, or a model may assign a category confidently and wrongly. Routing every prediction automatically allows such errors to enter the institutional workflow without human review.

**Fourth, weak resolution evidence.** A case may be closed using an image that is old, that was captured elsewhere, or that does not clearly demonstrate completion of the work. Without evidence requirements and a durable record of who decided what, the public-facing status of a case can diverge from the actual state of the problem on the ground.

**Fifth, the absence of a transparent history.** A conventional database permits records and status changes to be edited or deleted without trace. This prevents supervisors, auditors, researchers, and citizens from reconstructing how a report moved through the system and who was responsible at each step.

The central problem is therefore not the absence of a reporting platform. It is the absence of an affordable, context-appropriate mechanism for improving data precision, evidence integrity, and institutional accountability across the reporting lifecycle.

## 1.3 Research Gap

Conventional digital complaint systems commonly provide a submission form, a category, a location, and a status workflow. What they do not generally combine within a single verification pipeline are the following elements:

- **Spatial corroboration**, in which independent reports falling within a defined geographic radius raise confidence that an incident is real and correctly located.
- **Metadata-assisted evidence checking**, in which available image metadata is compared against the reported location and time before a resolution is accepted — treated as an indicator for human review, never as proof.
- **Multimodal consistency analysis**, in which image content, text description, and spatial context are assessed together rather than independently.
- **Human-in-the-loop triage**, in which uncertain or conflicting cases are routed to a moderator instead of being automatically accepted or rejected.
- **Comparative evaluation**, in which a human-only baseline, an AI-only model, and the hybrid model are measured against identical criteria.

The gap is also methodological. A system can claim to improve accountability without demonstrating which of its components produces the improvement. This study addresses that through a staged comparison — described in Chapter Three as the *Ablation of Trust* study — that isolates the contribution of individual verification mechanisms rather than evaluating the pipeline only as a whole.

## 1.4 Aim of the Study

The aim of this project is to design, develop, and evaluate SaloneFix, a public-service reporting platform that improves the precision, verifiability, and accountability of civic reports in Sierra Leone through human oversight, spatial corroboration, evidence checks on resolutions, and AI-assisted multimodal verification.

## 1.5 Objectives

1. To investigate the information, verification, privacy, and operational workflow requirements for an AI-assisted public-service reporting platform in Freetown, Sierra Leone.
2. To review and analyse existing digital reporting and civic-accountability approaches, and to identify the technical and operational gaps that SaloneFix is designed to address.
3. To design and develop a verify-first SaloneFix prototype integrating text, image, and location capture, spatial clustering, metadata-assisted evidence review, AI-assisted classification, human moderation, institutional assignment, and audit logging.
4. To implement and compare three verification approaches — a human-only baseline, an AI-only model, and the SaloneFix hybrid model — and to evaluate them using classification accuracy, precision, recall, false-positive rate, duplicate reduction, resolution-evidence rejection rate, verification confidence, and moderator workload.
5. To assess the usability, privacy, fairness, technical limitations, and overall suitability of the prototype for potential future pilot deployment.

## 1.6 Research Questions

**Main question.** To what extent does a hybrid human-and-AI verification model improve data precision and institutional accountability compared with standard digital reporting in a low-resource urban context?

**Supporting questions.**

1. What functional, operational, privacy, and verification requirements should guide an AI-assisted public-service reporting platform in Sierra Leone?
2. To what extent does spatial corroboration improve the identification and prioritisation of genuine public-service incidents compared with treating reports individually?
3. To what extent can available image metadata assist a human reviewer in detecting inconsistent or unverifiable resolution evidence?
4. How does a multimodal model perform when image, text, and spatial context are considered together rather than independently?
5. To what extent does the hybrid model improve data precision and institutional accountability compared with human-only and AI-only models?
6. What usability, infrastructure, privacy, and fairness risks must be addressed before the platform could be deployed in a real public-service environment?

## 1.7 Research Hypotheses

The following hypotheses will be tested where sufficient evaluation data is available. They are stated for testing, not assumed to hold.

- **H1.** The hybrid model will achieve higher report-classification precision than the AI-only model.
- **H2.** The hybrid model will reduce false-positive and duplicate-report rates relative to an unverified digital-reporting baseline.
- **H3.** Metadata-assisted resolution checks will surface a measurable proportion of inconsistent resolution submissions that a status-only workflow would not detect.
- **H4.** Human review of low-confidence or conflicting cases will reduce serious routing errors relative to fully automatic routing.

## 1.8 Significance of the Study

For citizens, the project offers a clearer channel for reporting public-service problems and for tracking what institutions did in response, including the evidence on which a case was closed. For public institutions, it offers improved report quality, fewer duplicate field visits, better prioritisation of recurring incidents, and a transparent case history that supervisors can inspect. For civil-society organisations and researchers, it offers structured, auditable information about service problems and institutional responses.

The academic contribution is an evaluated design for combining automated signals with spatial and evidence-based verification under human authority. Rather than treating AI as a replacement for human judgement, the study examines how the two can be combined in a low-resource setting, and measures which components actually contribute.

The governance contribution is to translate broad commitments to participation, transparency, and accountability into a concrete, inspectable workflow. The study does not claim that a software system reforms public institutions. Its contribution is a prototype and evidence about one mechanism that may support more accountable institutional workflows.

## 1.9 Scope of the Study

The study covers a prototype focused on public-service incident reporting in Freetown, Sierra Leone. Initial categories are damaged roads and potholes, blocked drainage and flooding, waste accumulation, and damaged public facilities, with further categories subject to requirements analysis.

The system covers citizen report submission with image and location capture, moderation and triage, clustering of related reports into incidents, institutional assignment, status transitions, resolution-evidence submission and review, citizen dispute and reopening, an append-only audit history, and administrative provisioning of staff accounts.

**Phased delivery.** The platform is delivered in three phases, and this is a deliberate methodological choice rather than a scheduling convenience. The evaluation design requires a human-only baseline against which later AI-assisted configurations can be compared; that baseline cannot be obtained if automated assistance is present from the start.

| Phase | Content | Status |
|---|---|---|
| 1. Human-First Foundation | Complete lifecycle under human authority, with AI and messaging integrations disabled by configuration | Implemented |
| 2. Human-Only MVP and Baseline | Controlled scenarios, user acceptance testing, and measurement of the human-only baseline, which is then frozen | In progress |
| 3. Hybrid Human + AI | AI adapters introduced behind feature flags, producing recommendations that a human may accept or override, evaluated against the frozen baseline | Planned |

**Exclusions.** The project does not attempt to provide a nationwide production service, to replace emergency services, to make legal findings of dishonesty against any person or institution, to guarantee that an incident is genuine, or to make final institutional decisions without an accountable human authority. Metadata checks are treated as indicators for review, never as conclusive proof. Messaging-channel integration will be implemented only if a suitable approved interface and testing access are available; otherwise the web interface remains the primary channel.

## 1.10 Limitations

The study may be constrained by the availability of representative local imagery, access to public institutions and field officers, internet connectivity, device capability, inconsistent GPS accuracy, image compression, absent image metadata, limited computing resources, and the difficulty of obtaining a fully verified ground-truth dataset.

Three limitations deserve particular emphasis because they bear directly on the claims the study can make.

**Spatial corroboration is socially biased.** It favours areas where more residents have smartphones, connectivity, or the motivation to report, and it is inappropriate for genuinely isolated incidents. A single report of a real problem in an under-connected neighbourhood must not be treated as less credible simply because it stands alone.

**Image metadata is weak evidence.** Metadata can be removed by messaging applications, stripped by editing software, altered by device settings, or absent entirely. Missing or conflicting metadata must therefore never be treated as proof that a citizen or officer has acted dishonestly; it can only lower an evidence-confidence signal and prompt human review. A further design tension arises in the current implementation: uploaded images are sanitised on ingestion, with metadata removed to protect the location privacy of the person reporting. Any metadata-assisted checking must consequently operate at the moment of ingestion, before sanitisation, and must record only a derived finding rather than retaining the raw metadata itself.

**Three metrics cannot be derived from system data.** Classification accuracy and routing correctness require adjudicated ground-truth labels produced by independent human reviewers, and usability requires a survey instrument (Brooke, 1996). These are collected separately and are reported as such; they are never estimated from the system's own records.

Model performance may additionally vary with image quality, lighting, weather, language, urban environment, and incident category. Participant feedback may be affected by social desirability and by limited familiarity with a prototype. These limitations are documented and carried into the interpretation of results.

## 1.11 Definition of Key Terms

| Term | Definition as used in this study |
|---|---|
| **Civic technology** | Digital technology supporting communication, participation, public services, or accountability between citizens and institutions. |
| **Report** | A single citizen submission describing an observed problem. Reports are preserved as submitted and are never silently discarded. |
| **Incident** | A verified case, created by a moderator, to which one or more reports are linked and against which institutional work is assigned. |
| **Spatial corroboration (spatial consensus)** | Increased confidence in an incident when independent reports occur within a defined geographic radius and appear to describe the same problem. The radius is a configurable parameter, not a fixed constant. |
| **Metadata-assisted evidence checking** | Extraction and comparison of available image metadata — capture time, coordinates, device information — for evidence-quality assessment. An indicator for human review, not proof. |
| **Multimodal AI** | A model analysing more than one information type, such as text, image, and location, in combination. |
| **Human-in-the-loop** | A workflow in which human reviewers examine uncertain, conflicting, or high-impact cases before final action, and retain authority to override automated signals. |
| **Verification confidence** | A system-generated signal representing the strength of available evidence. It is not a statement of truth. |
| **Append-only audit log** | A protected chronological record of material events and status transitions that cannot be silently altered or deleted, recording actor, timestamp, reason, previous state, and new state. |
| **Ablation of Trust study** | The comparative evaluation of different verification configurations to isolate the contribution of each integrity mechanism. |

## 1.12 Structure of the Report

**Chapter One** introduces the problem, states the aim, objectives, research questions, and hypotheses, and sets the scope and limitations of the study.

**Chapter Two** reviews the literature on public accountability and citizen participation, civic technology in Sierra Leone, crowdsourced data quality, spatial clustering and corroboration, digital-evidence integrity, multimodal classification, human-in-the-loop verification, and the privacy, fairness, and governance frameworks that bound the design. It compares existing reporting platforms and related studies to identify the gap this study addresses, and sets out the conceptual framework carried into the methodology.

**Chapter Three** presents the methodology and the proposed system, including research design, requirements, system architecture, the verification pipeline, the data model, the technology stack, the ethical and privacy framework, and the testing and evaluation strategy.

**Chapter Four** presents the implementation and the results of the evaluation, including the human-only baseline and the comparison between verification configurations.

**Chapter Five** discusses the findings against the research questions, states the contributions and limitations, and makes recommendations for future work and for any future pilot deployment.

---

## References

*Sources cited in Chapter Two are repeated there where they are also cited in this chapter, so that each chapter is self-contained. The final report consolidates both lists into a single reference section.*

African Development Bank (2025) *Sierra Leone – Digital Innovation for Government Efficiency and Sector Transformation (DIGEST)*. Available at: https://mapafrica.afdb.org/en/projects/46002-P-SL-GB0-003

Alvarez, P. (2004) 'Using Extended File Information (EXIF) file headers in digital evidence analysis', *International Journal of Digital Evidence*, 2(3). Available at: https://www.utica.edu/academic/institutes/ecii/publications/articles/A0B1F944-FF4E-4788-E75541A7418DAE24.pdf

Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P.N., Inkpen, K., Teevan, J., Kikin-Gil, R. and Horvitz, E. (2019) 'Guidelines for human-AI interaction', in *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*. Available at: https://doi.org/10.1145/3290605.3300233

Baltrušaitis, T., Ahuja, C. and Morency, L.-P. (2019) 'Multimodal machine learning: a survey and taxonomy', *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 41(2), pp. 423–443. Available at: https://doi.org/10.1109/TPAMI.2018.2798607

Basiri, A., Haklay, M., Foody, G. and Mooney, P. (2019) 'Crowdsourced geospatial data quality: challenges and future directions', *International Journal of Geographical Information Science*, 33(8), pp. 1588–1593. Available at: https://doi.org/10.1080/13658816.2019.1593422

Brooke, J. (1996) 'SUS: a "quick and dirty" usability scale', in Jordan, P.W., Thomas, B., Weerdmeester, B.A. and McClelland, I.L. (eds.) *Usability Evaluation in Industry*. London: Taylor & Francis, pp. 189–194.

Creswell, J.W. and Creswell, J.D. (2018) *Research Design: Qualitative, Quantitative, and Mixed Methods Approaches*. 5th edn. Thousand Oaks, CA: SAGE Publications.

Fung, A., Graham, M. and Weil, D. (2007) *Full Disclosure: The Perils and Promise of Transparency*. Cambridge: Cambridge University Press.

Goodchild, M.F. (2007) 'Citizens as sensors: the world of volunteered geography', *GeoJournal*, 69(4), pp. 211–221. Available at: https://doi.org/10.1007/s10708-007-9111-y

National Institute of Standards and Technology (2023) *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1. Available at: https://doi.org/10.6028/NIST.AI.100-1

Open Government Partnership (2021–2023) *Citizen Participation in Parliament (SL0030): Sierra Leone Action Plan 2021–2023*. Available at: https://www.opengovpartnership.org/members/sierra-leone/commitments/sl0030/

OWASP Foundation (no date) *Application Security Verification Standard (ASVS)*. Available at: https://owasp.org/www-project-application-security-verification-standard/

Peixoto, T. and Fox, J. (2016) 'When does ICT-enabled citizen voice lead to government responsiveness?', *IDS Bulletin*, 47(1), pp. 23–40. Available at: https://doi.org/10.19088/1968-2016.104

World Bank (2021) *Sierra Leone Digital Economy Diagnostic*. Available at: https://openknowledge.worldbank.org/entities/publication/1ef37484-3de5-553a-b58e-9867d6f146ed

World Bank (2026) *Strengthening Citizen Participation in Sierra Leone: A Policy and Institutional Roadmap*. Available at: https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099022726040510797

World Wide Web Consortium (2024) *Web Content Accessibility Guidelines (WCAG) 2.2*. Available at: https://www.w3.org/TR/WCAG22/

Wu, X., Xiao, L., Sun, Y., Zhang, J., Ma, T. and He, L. (2022) 'A survey of human-in-the-loop for machine learning', *Future Generation Computer Systems*, 135, pp. 364–381. Available at: https://doi.org/10.1016/j.future.2022.05.014
