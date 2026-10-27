# SaloneFix: An AI-Powered Integrity and Accountability Platform for Public-Service Reporting in Sierra Leone

**Chapter Two: Literature Review and Existing Systems**

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

## 2.1 Introduction

Chapter One argued that the problem SaloneFix addresses is not the absence of a channel through which citizens can report public-service failures, but the absence of a mechanism that establishes whether the information flowing through such a channel is good enough to act on, and whether the institutional response to it can be inspected afterwards. This chapter examines the literature and the existing systems that bear on that argument.

The review is organised in three movements. The first is conceptual (sections 2.2 to 2.9). It establishes what accountability requires beyond disclosure, situates civic technology within Sierra Leone's digital-government context, and then examines each of the technical mechanisms on which the SaloneFix design depends: the data-quality properties of crowdsourced reporting, spatial clustering and corroboration, digital-evidence integrity and image metadata, multimodal classification, human-in-the-loop decision support, and the privacy, fairness, and governance frameworks that constrain all of them. The second movement is comparative (sections 2.10 and 2.11). It reviews four existing reporting and information platforms and the empirical studies most closely related to this project. The third movement is synthetic (sections 2.12 to 2.14). It states the gap that the conceptual and comparative reviews jointly identify, describes the proposed solution, and presents the conceptual framework that carries forward into the methodology in Chapter Three.

Two commitments govern the review throughout. The first is that each mechanism is examined for its weaknesses as well as its usefulness, because the central design claim of this project — that verification should precede institutional action — is only defensible if the limits of each verification signal are understood. The second is that no claim of novelty is made beyond what the review supports. Citizen reporting, geospatial clustering, image forensics, and human-in-the-loop moderation are all established fields. The contribution this project claims is the specific combination of them in one auditable workflow, and the comparative evaluation of that combination in a low-resource urban setting.

## 2.2 Public Accountability, Transparency and Citizen Participation

Accountability is conventionally understood as a relationship in which an actor is obliged to explain and justify conduct to a forum that can pose questions, pass judgement, and attach consequences (Bovens, 2007). Each of the three elements matters for system design. Information alone satisfies only the first. A platform that publishes reports but cannot show who examined them, what was decided, and on what evidence, supports explanation without judgement, and judgement without consequence.

This distinction is borne out empirically. Research on transparency initiatives has repeatedly found that disclosure does not produce accountability on its own: information must be credible, it must reach an actor with the capacity and incentive to respond, and the response must be observable to those who raised the issue (Fung, Graham and Weil, 2007). Reviews of transparency and accountability initiatives in service delivery reach the same conclusion from the development-practice side, finding mixed and context-dependent effects, and attributing the variation largely to whether an institutional response pathway exists rather than to the quality of the information channel (Gaventa and McGee, 2013; Joshi, 2013). Peixoto and Fox (2016), examining twenty-three cases of technology-enabled citizen voice, found that responsiveness depended on institutional conditions — whether an agency had the mandate, resources, and incentive to act — rather than on the sophistication of the reporting technology.

Participation itself has a reciprocal dynamic. Sjoberg, Mellon and Peixoto (2017) found that citizens who receive a response to a report are substantially more likely to report again, while those whose reports are ignored withdraw. This finding is directly relevant to the trust gap described in Chapter One: a reporting platform that cannot demonstrate institutional response does not merely fail to improve accountability, it actively depletes the willingness to participate that it depends on. Theories of coproduction frame the same relationship as a joint production problem, in which citizens and institutions each supply inputs that the other cannot substitute for, and in which the institution's reliability determines whether citizen inputs continue to arrive (Ostrom, 1996; Linders, 2012).

Trust, finally, is not a simple function of openness. Grimmelikhuijsen and Meijer (2014) found that the effect of transparency on perceived trustworthiness is conditioned by what the disclosed information shows and by the prior disposition of the person receiving it; transparency about poor performance can reduce trust. For SaloneFix this is a caution against treating publication as an unqualified good. The design implication adopted in this project is that the platform should make the *process* inspectable — who decided, when, on what basis, with what evidence — rather than exposing raw submissions and personal data by default.

Sierra Leone's own policy commitments identify this territory explicitly. The Open Government Partnership action-plan commitments name citizen participation, transparency, public access to information, feedback mechanisms, and data management among the country's open-government priorities (Open Government Partnership, 2021–2023), and the World Bank's institutional roadmap for citizen participation emphasises strengthening community-level participation so that citizens can influence and monitor decisions affecting services (World Bank, 2026).

Taken together, this literature sets the accountability requirements that the SaloneFix design must satisfy. A submission form is insufficient. The system must additionally provide a recorded status history, an identified responsible institution, required resolution evidence, an escalation path, a citizen route to dispute a resolution, and audit access for an independent reviewer. These requirements are not derived from the technology; they are derived from what accountability means.

## 2.3 Digital Government and Civic Technology in Sierra Leone

The Sierra Leonean context creates both the opportunity for this project and the constraints on it. The World Bank's digital-economy diagnostic describes digital technologies as a route to improved public services, access to information, and government transformation, while identifying infrastructure limitations, affordability, digital literacy, and institutional capacity as binding constraints on who can actually use such systems and how reliably they operate (World Bank, 2021). The African Development Bank's DIGEST project links digital solutions to governance efficiency, public-sector coordination, and digital-skills development, confirming the policy relevance of the domain while making the same capacity qualifications (African Development Bank, 2025).

Three design consequences follow, and all three are reflected in the implemented system.

**The interface must assume constrained devices and connectivity.** A platform that requires a recent smartphone, a continuous data connection, or a precise satellite fix excludes a substantial share of the population it is intended to serve. The implemented prototype is a mobile-first web application rather than a native application, uses a relative API path so that devices on a local network can reach it without additional configuration, and treats imagery as optional rather than mandatory on a report.

**Location capture must degrade gracefully.** Satellite positioning in dense urban environments is unreliable, and some devices will not supply it at all. The implemented system therefore records a location-precision classification alongside the coordinates, distinguishing a reading accurate to within approximately one hundred metres from a coarser reading and from a landmark description typed by the person reporting. A report with a user-entered landmark is a valid report, not a degraded one; what changes is the confidence attached to its position, and that difference is recorded rather than hidden.

**Human fallback is a requirement, not a contingency.** Where connectivity, device capability, and digital literacy vary widely, a workflow that can only complete when every automated component is available will fail unevenly across the population. This consideration reinforces, on practical grounds, the architectural rule adopted for independent reasons in section 2.13: the core lifecycle must complete under human authority alone.

A fourth consideration concerns inclusion in the interface itself. Where digital literacy is uneven and assistive-technology use is undocumented, conformance to an external accessibility standard is the only defensible basis for interface decisions. The project targets Web Content Accessibility Guidelines 2.2 Level AA (World Wide Web Consortium, 2024), which requires among other things that status information be conveyed by text and not by colour alone — a requirement that directly shapes how case states are presented in the implemented interface.

## 2.4 Crowdsourced Reporting and Data Quality

The conceptual foundation of citizen reporting is the treatment of residents as distributed observers of local conditions. Goodchild (2007) described this as volunteered geographic information, noting both its coverage advantages over authoritative surveying and its uncontrolled provenance. Comparative studies of volunteered data have found quality that is often surprisingly good in aggregate but highly uneven in distribution: Haklay (2010), comparing OpenStreetMap with national mapping-agency data, found positional accuracy adequate for many purposes but coverage strongly concentrated in affluent and densely populated areas.

Three quality problems recur across this literature and map directly onto the problems stated in Chapter One.

**Credibility cannot be inferred from the artefact.** Flanagin and Metzger (2008) argued that volunteered geographic information presents a distinctive credibility problem because the usual cues by which people assess a source — institutional authorship, editorial process, professional accountability — are absent. A report is a claim, and its persuasiveness as a rendered record is independent of its accuracy. Goodchild and Li (2012) proposed three approaches to quality assurance for such data: a crowdsourcing approach, in which convergent independent contributions raise confidence; a social approach, in which trusted reviewers moderate; and a geographic approach, in which submissions are checked against known properties of the location. The SaloneFix verification pipeline uses all three, and section 2.5 examines the first of them in detail because it is the one most often over-claimed.

**Volume is not evidence.** A high report count is not a measure of data quality, and it is not even a reliable measure of incident severity. Reports may duplicate one another, reuse the same image, originate from a single account, or be coordinated. Basiri *et al.* (2019), surveying crowdsourced geospatial data quality, identify duplication, incompleteness, positional error, and participation bias as persistent challenges that require explicit handling rather than assuming that scale resolves them. The design consequence adopted here is a structural distinction between a *report*, which is one person's submission, and an *incident*, which is a case created by a human moderator and to which one or more reports are linked. Corroboration is computed over incidents and their linked reports, with provenance tracked, so that reports sharing an image, an account, or a submission pattern are not counted as independent evidence.

**Participation is socially structured.** This is the most consequential finding for a system intended to inform resource allocation. Clark, Brudney and Jang (2013), studying technology-mediated coproduction of municipal services, found distributional biases in who reports, with reporting propensity varying by socio-economic status independently of underlying service need. O'Brien *et al.* (2017) found that reporting behaviour reflects individual motivation and territorial attachment rather than objective conditions alone. Kontokosta and Hong (2021) demonstrated directly that socio-spatial disparities in complaint behaviour bias data-driven municipal decisions, with under-reporting neighbourhoods systematically disadvantaged when complaint volume is used as a proxy for need.

This last finding is why Chapter One states spatial corroboration bias as a limitation of the study rather than a minor technical caveat. A verification mechanism that raises confidence when reports converge geographically will, if applied without qualification, systematically discount genuine problems in neighbourhoods that report less. The design rule adopted in response is that corroboration may raise confidence in an incident but must never be a precondition for acting on one, and that a single report from an under-reporting area must remain fully actionable on a moderator's judgement.

## 2.5 Spatial Clustering and Spatial Corroboration

Spatial clustering groups observations by proximity. Density-based methods are the established approach for this class of problem because they discover clusters of arbitrary shape without requiring the number of clusters to be specified in advance, and because they explicitly classify sparse observations as noise rather than forcing them into a cluster (Ester *et al.*, 1996). Both properties matter for incident reporting, where a pothole is a point problem, a flooded drain may extend along a street, and an isolated report is common and meaningful.

Applying such a method to civic reports, however, requires care on three counts.

First, the distance threshold is not a natural constant. The appropriate radius depends on positioning accuracy, road geometry, urban density, the category of incident, and whether the problem is a point or an extended feature. The proposal identified a range of roughly ten to twenty-five metres as a starting point for evaluation; this project treats the radius as a configurable parameter to be tuned and reported, not as a fixed property of the design. Where positional uncertainty is itself variable — as it is when reports carry differing location-precision classifications — a single fixed threshold applied uniformly will over-cluster imprecise reports and under-cluster precise ones.

Second, proximity alone is a weak signal of identity. Two reports twelve metres apart may describe the same pothole, two adjacent potholes, or a pothole and a blocked drain. Distance must therefore be combined with temporal proximity, category agreement, textual similarity, image similarity, and independence of the submitting accounts before the reports are treated as describing one incident.

Third, and most importantly, corroboration is not proof. Goodchild and Li's (2012) crowdsourcing approach to quality assurance assumes that contributions are independent, and that assumption fails in exactly the cases where it matters most. Coordinated or copied submissions can manufacture apparent consensus, while a genuine and serious problem in a sparsely reporting area may attract a single report — which, as section 2.4 established, is a socially patterned outcome rather than a random one.

The design position adopted in this project follows from these three points. Clustering is used to *suggest* that reports may describe one incident; a human moderator decides whether they do. The linking of a report to an incident is a recorded human decision with an actor, a timestamp, and a reason, not an automatic consequence of a distance calculation. This is a deliberate reduction in automation relative to what the technique permits, and it is adopted because an incorrect automatic merge destroys information — it makes one person's distinct report disappear into another case — whereas an incorrect suggestion merely wastes a moderator's attention. For the same reason, linking a report to an incident in the implemented system marks the report as merged but preserves it in full; nothing is discarded.

## 2.6 Digital-Evidence Integrity and Image Metadata

Photographic evidence is central to this project in two places: on a citizen report, where it substantiates a claim that a problem exists, and on a resolution, where it substantiates a claim that the problem was fixed. The second is the more consequential, because a resolution closes a case and removes it from institutional attention.

Image files may carry Exchangeable Image File Format metadata recording capture time, satellite coordinates, device make and model, orientation, and processing software. Alvarez (2004) set out the use of such headers in digital evidence analysis, and the broader image-forensics literature has developed techniques for detecting manipulation from compression characteristics, sensor noise, and file-structure artefacts (Farid, 2009; Piva, 2013). Kee, Johnson and Farid (2011) showed that the structure of a JPEG header alone can indicate whether a file came directly from a camera or passed through editing software.

The limitations of this evidence class are severe and well documented, and they are decisive for the present design.

**Metadata is routinely absent.** Messaging applications strip it on transmission, social platforms remove it on upload, editing software discards it on save, and device privacy settings suppress it at capture. Its absence is the normal case for an image that has travelled through consumer software, and carries no information about the honesty of the person who supplied it.

**Metadata is trivially alterable.** It is not cryptographically bound to the image content. A capture time and a coordinate pair can be edited with freely available tools, which means that present and apparently consistent metadata establishes considerably less than it appears to.

**Metadata is not a chain of custody.** It records assertions made by a device under conditions that cannot be reconstructed after the fact.

Three design rules follow, and they are stated here because they are also ethical commitments. First, metadata findings are indicators that lower an evidence-confidence signal and prompt human review; they are never determinations. Second, the system must not label a person. Chapter One's exclusions and the project's engineering rules both prohibit attaching a finding of fraud or dishonesty to a citizen or an officer; the permissible language is that evidence is inconsistent or requires review, which locates the deficiency in the evidence rather than in the person. Third, any check must be reconciled with privacy.

That third rule creates a genuine design tension, which Chapter One records as a limitation and which this review can now state precisely. Metadata is itself sensitive: coordinates in an image disclose where the person reporting was standing, and device identifiers help to re-identify them. The implemented system therefore sanitises every uploaded image on ingestion, validating its type by file signature, enforcing a size limit, and stripping metadata before the file is stored. This protects the location privacy of the reporter — but it also means that any metadata-assisted checking must operate at the moment of ingestion, before sanitisation, and must persist only a derived finding, never the raw metadata. The alternative, retaining original metadata so that it remains available for later inspection, would convert a verification feature into a standing privacy liability. The project resolves the tension in favour of privacy, and accepts the consequent reduction in forensic capability as a documented limitation.

Access control is the complement to sanitisation. Media in the implemented system is held in private storage, is never served as static content, and is reachable only through an authenticated request or a signed, expiring link issued to an authorised viewer. This follows the general principle that evidence must be preserved and inspectable by accountable parties without being publicly exposed, and reflects the application-security verification requirements adopted by the project (OWASP Foundation, no date).

## 2.7 Artificial Intelligence for Multimodal Classification

A report carries at least three kinds of information: an image, a textual description, and a location. Treating these jointly rather than independently is the core argument for a multimodal approach. Baltrušaitis, Ahuja and Morency (2019) distinguish the representation, alignment, and fusion problems in multimodal machine learning and note that the characteristic advantage of multimodal models is complementarity — text may supply context invisible in an image, while an image may contradict an inaccurate description. Joint image–text models trained on large paired corpora have demonstrated transferable classification from natural-language category descriptions without task-specific training data (Radford *et al.*, 2021), which is directly relevant to a setting where locally representative labelled imagery is scarce.

The *inconsistency* case is the more interesting one for this project. A report whose photograph shows a blocked drain while its text describes a pothole is not merely harder to classify; the discrepancy is itself a signal worth surfacing to a human reviewer. Multimodal comparison is therefore proposed here less as a labelling mechanism than as a conflict detector.

Three constraints shape how such a model may be used, and they correspond to the automation-error problem stated in Chapter One.

**Classification fails, and fails unevenly.** Performance varies with image quality, illumination, weather, urban environment, language, and category. Buolamwini and Gebru (2018) demonstrated that aggregate accuracy figures can conceal large disparities in error rates across subgroups, establishing the general principle that a single headline accuracy number is an inadequate basis for deployment decisions. For this project, the corresponding requirement is that evaluation must report performance disaggregated by category and by data-quality condition, not as a single figure.

**Automatic routing propagates error into institutional work.** A confidently wrong category sends a case to an institution that cannot act on it, and the error surfaces only when a field team arrives. Confidence estimates do not solve this, since a miscalibrated model is confidently wrong precisely in the cases that matter.

**Citizen text and imagery are untrusted input.** Where a language model processes user-supplied text, that text must be treated as data and must not be able to alter the system's instructions. The project's engineering rules state this explicitly, together with the requirement to minimise the identity and precise-location data sent to any external provider and to record the provider, model version, configuration, timestamp, and any failure alongside each recommendation.

These constraints lead to a specific contract for the AI component, which is the one adopted in the project's architecture. The adapter accepts a report identifier and returns a versioned recommendation record containing a suggested category, a confidence value, supporting signals where available, and a flag indicating whether human review is required. It does not change a case's status, link reports to incidents, assign an institution, or close a case. The original submission and the model output are both preserved so that errors can be examined after the fact. If the provider is unavailable, the adapter raises a dependency failure that leaves the human workflow intact rather than blocking it. This is the architectural expression of the human-first boundary described in section 2.13.

## 2.8 Human-in-the-Loop Verification and Decision Support

Human-in-the-loop designs route uncertain, conflicting, or high-impact cases to a person rather than resolving them automatically. Wu *et al.* (2022) survey the field and distinguish configurations by where the human intervenes — data labelling, model training, or inference-time decision-making. The configuration relevant here is the last: a moderator examines a case, sees whatever automated signals exist, and decides.

The design guidance for such interfaces is well established. Amershi *et al.* (2019) set out eighteen guidelines for human–AI interaction, including making clear what the system can do, conveying confidence, supporting efficient correction and dismissal, and scoping services to context. Shneiderman (2020) frames the objective as combining high automation with high human control rather than trading one against the other.

The empirical literature on whether human oversight actually improves outcomes is, however, more equivocal than the design guidance implies, and this project treats that equivocation as a finding to be designed around rather than an inconvenience.

**Complementarity is not automatic.** Bansal *et al.* (2021) found that human–AI teams frequently fail to outperform the better of the two alone, because people accept incorrect recommendations and because explanations can increase acceptance of wrong answers as readily as right ones. Oversight that consists of confirming a displayed suggestion adds procedural legitimacy without adding verification.

**Oversight can be nominal.** Green and Chen (2019), studying algorithm-in-the-loop decisions in a risk-assessment setting, found that people adjusted their judgements towards an algorithmic score without a corresponding gain in accuracy, and did not reliably detect when the score was wrong. The presence of a human in the workflow is therefore not by itself evidence that human judgement is being exercised.

Four design responses follow, and all four are implemented in the current system.

First, the moderator is shown the original evidence beside any recommendation, not a recommendation alone, so that the decision can be made on the evidence rather than on the suggestion. Second, the moderator's authority is explicit: a case may be verified, rejected, returned for clarification, linked to an existing incident, or escalated, and the destructive or consequential decisions among these require a recorded reason. Third, both the recommendation and the human decision are recorded, which makes the rate at which humans correct the model a measurable quantity rather than an assumption — this is the basis of the human-correction metric in the evaluation protocol. Fourth, and decisively for this project's methodology, the human-only configuration is measured first and frozen before any automated assistance is introduced, so that the question of whether assistance helps can be answered empirically rather than asserted.

Recording decisions also serves accountability in the sense established in section 2.2. Every material action in the implemented system — a moderation decision, an assignment, a status transition, an evidence submission or review, a dispute, a reopening, a provisioning action, and an auditor's own read — writes an append-only audit event capturing the actor, the timestamp, the reason, the previous state, and the new state. This is what allows an independent reviewer to reconstruct a case lifecycle, and it is the mechanism by which the system attempts to satisfy Bovens's (2007) third element, consequence, rather than only the first.

## 2.9 Privacy, Fairness and Governance Frameworks

Three external frameworks bound the design, and they are cited here because they supply requirements that the project did not invent and cannot negotiate.

The NIST Artificial Intelligence Risk Management Framework organises AI risk management around governing, mapping, measuring, and managing risk across a system's lifecycle, and emphasises documenting intended use, known limitations, and the conditions under which a system should not be relied upon (National Institute of Standards and Technology, 2023). Its influence on this project is visible in the staged introduction of automation, the requirement that AI components be independently evaluable, and the explicit documentation of limitations in Chapter One.

ISO/IEC 27701 extends information-security management to privacy information management, requiring purpose limitation, data minimisation, defined retention, and controlled access to personal information (International Organization for Standardization, 2019). The corresponding rules in this project are that only data required to submit, manage, communicate, evaluate, and audit an incident is collected; that exact identity, exact coordinates, device metadata, and original media are not public by default; and that citizen-facing responses return approximate location and a precision classification rather than precise coordinates.

The OWASP Application Security Verification Standard supplies the security baseline: server-side authorisation at both the role and the object level, secure credential storage, short-lived sessions, rate limiting on authentication and submission endpoints, validation of uploaded files by signature as well as declared type, private media storage with short-lived signed access, and logs that exclude secrets and unnecessary personal data (OWASP Foundation, no date). Two of these deserve emphasis because they are frequently implemented incorrectly in systems of this kind. Authorisation must be enforced on the server and re-checked against the specific object being acted upon, since role checks alone permit a user with a legitimate role to read records belonging to others; and interface-level role gating is a usability affordance, never a control.

The fairness literature reviewed in sections 2.4 and 2.7 completes the picture. Participation bias means that report volume is not a measure of need (Kontokosta and Hong, 2021); disaggregated error analysis means that aggregate accuracy is not a measure of fitness (Buolamwini and Gebru, 2018). Both findings constrain what this project may claim from its results, and both are carried into the evaluation design as reporting requirements rather than as discretionary additions.

## 2.10 Review of Existing Systems

Four existing platforms illustrate how far the field has already come and what it leaves unaddressed. Each is examined for the component SaloneFix adopts from it and the respect in which it differs.

**FixMyStreet**, developed by mySociety, allows residents to report street-level problems such as potholes and broken street lighting, uses the location and category of a report to identify the responsible authority, and routes the report to it, typically by email, while publishing reports so that others can see what has been raised (mySociety, no date). Its central contribution is the demonstration that location plus category is sufficient to determine institutional responsibility — a model this project adopts directly in its assignment of verified incidents to institutions. Offenhuber (2015), comparing citizen-feedback systems built on the Open311 specification, found that such platforms differ markedly in how legible they make the subsequent institutional process, and that the feedback loop back to the reporting citizen is frequently the weakest element. FixMyStreet's limitation for the present purpose is that routing is the terminal step of the pipeline: verification before dispatch is minimal, and the strength of the evidence on which a case is later closed is not systematically assessed.

**Ushahidi** is a crowdsourcing and mapping platform for collecting, managing, and visualising community-sourced information, accepting submissions from web forms, SMS, and email, and offering map, list, and timeline views together with role-based workflow management (Ushahidi, no date). It originated in post-election crisis mapping in Kenya (Okolloh, 2009) and became a standard tool in digital humanitarian response (Meier, 2015). Its contributions to this project's thinking are multi-channel intake, role-based processing, and the demonstration that crowdsourced information can be organised at scale under time pressure. The same literature, however, documents the verification difficulty that accompanies that scale: Meier (2015) describes the substantial volunteer effort required to triage and corroborate crisis reports, which is precisely the workload problem that this project's evaluation protocol treats as a measured quantity.

**SeeClickFix**, a municipal issue-reporting service used widely in North America, demonstrates the operational side of the same model — intake, routing, status communication, and public visibility integrated with municipal work-management systems (SeeClickFix, no date). Its relevance here is as evidence that the lifecycle model scales in practice when institutional capacity exists to receive it, which reinforces the finding in section 2.2 that the binding constraint is institutional rather than technical.

**Sabi Salone** provides a Sierra Leone-specific example of an artificial-intelligence-supported information platform. It assembles national policies, laws, evaluations, reports, and research materials and returns referenced results, so that an answer can be traced to a source document (Sabi Salone, no date). It is not an incident-reporting system, and it is reviewed here for a different reason: it demonstrates both the demand for locally relevant, traceable information systems in Sierra Leone and the design principle that a system's output should be auditable back to its evidence. SaloneFix applies that principle to citizen-generated incident reports rather than to policy documents.

The comparison can be summarised as follows.

| Capability | FixMyStreet | Ushahidi | SeeClickFix | Sabi Salone | SaloneFix |
|---|---|---|---|---|---|
| Citizen submission with image and location | Yes | Yes | Yes | Not applicable | Yes |
| Category-and-location based institutional routing | Yes | Partial | Yes | Not applicable | Yes |
| Multi-channel intake | Partial | Yes | Partial | Not applicable | Planned, flag-gated |
| Human moderation before institutional dispatch | Limited | Yes | Limited | Not applicable | Required |
| Duplicate and spatial corroboration handling | Limited | Limited | Partial | Not applicable | Yes, moderator-confirmed |
| Metadata-assisted evidence checking | No | No | No | Not applicable | Planned, privacy-bounded |
| Mandatory resolution evidence before closure | No | No | Partial | Not applicable | Yes, per category |
| Citizen dispute and reopening of a resolution | Limited | No | Partial | Not applicable | Yes |
| Append-only audit trail with independent auditor access | No | Partial | No | Partial | Yes |
| Comparative evaluation isolating verification components | Not published | Not published | Not published | Not published | Study design |

Two qualifications apply to this table. The capabilities listed for the comparator systems are assessed from their public documentation and the published literature, and deployments may be configured differently. The capabilities listed for SaloneFix distinguish what is implemented from what is planned behind a feature flag, consistent with the phased delivery stated in Chapter One; the table should not be read as a claim that the full design is operational.

What the comparison establishes is that the individual components are not novel. Citizen reporting, institutional routing, mapping, workflow management, role-based permissions, and evidence traceability all exist in deployed systems. What is not evident in any single one of them is a pipeline that places verification *before* institutional dispatch, requires evidence *before* closure, and records both in a form an independent auditor can inspect.

## 2.11 Review of Related Studies

Four strands of empirical work bear most directly on this project's research questions, and each supplies both a method and a caution.

Studies of technology-enabled citizen voice establish the dependence of outcomes on institutional conditions. Peixoto and Fox (2016) found across twenty-three cases that responsiveness tracked institutional capacity and incentive rather than channel design, while Sjoberg, Mellon and Peixoto (2017) established the reciprocal effect of responsiveness on continued participation. The methodological lesson for this project is that a prototype evaluation cannot demonstrate improved accountability outcomes, because those depend on institutional behaviour outside the system's control. What it can demonstrate is whether the workflow improves the precision, traceability, and operational usefulness of the information on which such behaviour would depend — which is why the project's evaluation protocol states that interpretation must be confined to those properties and must not claim that the system determines truth.

Studies of complaint-data bias establish a constraint on inference. Clark, Brudney and Jang (2013), O'Brien *et al.* (2017), and Kontokosta and Hong (2021) collectively show that complaint volume reflects reporting propensity as much as underlying need, and that decisions driven by volume therefore inherit a socio-spatial bias. The methodological lesson is that any corroboration or prioritisation mechanism in this project must be evaluated for differential effect across areas, not only for aggregate performance.

Studies of human–AI decision-making establish that the hypothesis under test is genuinely open. Bansal *et al.* (2021) and Green and Chen (2019) both found that adding a human reviewer to an automated decision did not produce the expected accuracy gain. This is the empirical basis for stating the project's hypotheses in Chapter One as propositions to be tested rather than as design assumptions, and for the staged comparison that follows.

Studies of crowdsourced geospatial quality supply the measurement apparatus. Goodchild and Li (2012) provide the three-approach taxonomy of quality assurance that the SaloneFix pipeline operationalises; Haklay (2010) and Basiri *et al.* (2019) supply the quality dimensions — positional accuracy, completeness, duplication, bias — against which the data a system produces can be assessed.

One further methodological point concerns the comparison design itself. A system can claim to improve accountability without identifying which of its components produces the improvement, and an evaluation of a pipeline as a whole cannot distinguish a contribution from moderation, from corroboration, from evidence requirements, or from automation. The staged comparison described in Chapter One as the *Ablation of Trust* study addresses this by measuring configurations in sequence: a human-only baseline, then individual verification mechanisms, then automated assistance against the frozen baseline. Usability is measured separately with an established instrument (Brooke, 1996) rather than inferred from system records, and classification and routing correctness require adjudicated labels from at least two independent reviewers with disagreements recorded, as Chapter One's limitations state and the project's evaluation protocol requires.

## 2.12 Identified Gap

The review identifies two gaps, one technical and one methodological.

**The technical gap** is the limited integration, within a single civic-reporting workflow designed for a low-resource urban context, of five elements that the literature treats separately and that deployed systems implement partially at best:

- report-quality verification occurring *before* institutional dispatch rather than after it;
- spatial corroboration that raises confidence without becoming a precondition for action, and that is confirmed by a human rather than applied automatically;
- evidence requirements on *closure* — a case in a category requiring photographic proof cannot be closed without it — rather than evidence requirements only on submission;
- a citizen route to dispute a resolution and reopen a case, closing the feedback loop that Offenhuber (2015) found to be the weakest element of comparable systems;
- an append-only lifecycle record that an independent auditor can inspect, including the auditor's own access.

**The methodological gap** is the absence of comparative evaluation that isolates the contribution of individual verification mechanisms. The literature on human–AI decision-making gives specific reason to doubt that adding either automation or human oversight produces improvement by itself (Green and Chen, 2019; Bansal *et al.*, 2021). A study that evaluates a hybrid pipeline only as a whole cannot distinguish a real contribution from the appearance of one, and cannot tell an institution which part of the mechanism is worth the cost of operating it.

These two gaps are related. The technical gap describes a design; the methodological gap explains why that design must be evaluated in stages rather than demonstrated as a working whole. Addressing only the first would produce a plausible system with no evidence behind it.

## 2.13 Proposed Solution

SaloneFix implements a verify-first pipeline. Every submission enters the platform as an unverified report and is preserved exactly as submitted. It is reviewed by a human moderator, who may verify it, reject it, return it for clarification, link it to an existing incident, or escalate it, recording a reason for each consequential decision. A verified report becomes or joins an incident, which is assigned to a responsible institution; an officer of that institution progresses it, submits resolution evidence, and the resolution is reviewed before the case is closed. The citizen who reported may dispute a resolution, which reopens the case for review. Every material step writes an append-only audit event.

Three principles distinguish this design from the comparator systems reviewed in section 2.10.

**Verification precedes dispatch.** A report does not reach an institution until a human has examined it. This inverts the ordering in the systems reviewed above, where routing is immediate and quality problems surface in the field.

**Evidence is required at closure and is immutable.** Where an incident category requires photographic proof of completion, a resolution without an attached photograph cannot be approved, and the attempt is refused and recorded. Evidence once submitted is never overwritten or deleted; linking a report to an incident marks it as merged but preserves it in full. This is the design response to the weak-resolution-evidence problem in Chapter One.

**Automation is introduced in stages and only where it is measured to help.** This is the point at which the project's framing must be stated plainly. The title of this project describes an AI-powered platform, and the proposal set out an AI-centred verification pipeline. The system as implemented runs with AI and messaging integrations disabled by configuration, and the complete lifecycle — submission, moderation, incident creation, assignment, progress, resolution evidence, review, dispute, reopening, and closure — is fully operable in that state.

This is a methodological decision, not an unmet objective, and the literature reviewed above supplies its justification. The evaluation requires a human-only baseline against which later configurations can be compared, and that baseline is unobtainable if automated assistance is present from the beginning. Bansal *et al.* (2021) and Green and Chen (2019) give direct empirical reason to expect that assistance may not improve outcomes, which makes the baseline the load-bearing part of the study rather than a preliminary to it. The three phases are therefore as Chapter One states them: a human-first foundation, now implemented; a human-only operational phase in which the baseline is measured and frozen; and a hybrid phase in which AI adapters are introduced one capability at a time behind feature flags, each producing recommendations that a human may accept, correct, or ignore, and each evaluated against the frozen baseline. The project's engineering rules make the dependency explicit: AI work may begin only after the human workflow passes acceptance testing, the baseline is measured, the dataset and ground-truth procedure are documented, privacy approval for AI processing is in place, and a specific value hypothesis has been defined.

The architectural expression of this staging is a boundary rule: the core domain must never call an automated service to complete a required state transition. An AI adapter accepts a report identifier and returns a versioned recommendation; it cannot change a status, link reports, assign an institution, or close a case, and if its provider is unavailable it raises a dependency failure that the human workflow routes around rather than one that halts it. The same rule applies to the planned messaging channel. The result is a system in which automation is additive and removable: if a component is found not to create measurable value, it can be withdrawn without disabling the service.

## 2.14 Conceptual Framework

The framework that follows from this review has four layers. Each layer contributes a distinct signal, and no layer is permitted to be decisive on its own.

| Layer | Mechanism | Signal contributed | Explicit limitation |
|---|---|---|---|
| **Intake** | Structured submission of category, description, location with a recorded precision classification, and optional sanitised imagery | Establishes a preserved, attributable claim | A single submission is a claim, not a verified fact (Flanagin and Metzger, 2008) |
| **Corroboration** | Proximity, time, category, and content comparison across reports, with provenance tracked and account independence assessed | Raises confidence that an incident is real and correctly located | Socially biased by reporting propensity; never a precondition for action (Kontokosta and Hong, 2021) |
| **Evidence assessment** | Validation and sanitisation of media on ingestion; metadata-derived findings where available; required proof at closure for categories that demand it | Raises or lowers confidence in the strength of the evidence | Metadata is absent, alterable, and not a chain of custody; findings never label a person (Alvarez, 2004; Farid, 2009) |
| **Human authority** | Moderator triage, institutional assignment, resolution review, citizen dispute, append-only audit | Converts signals into an accountable, reconstructable decision | Oversight can be nominal; the human-correction rate must be measured, not assumed (Green and Chen, 2019) |

The framework operates as a sequence in which confidence accumulates but authority does not transfer. Intake produces a claim. Corroboration and evidence assessment produce signals that may raise or lower confidence in that claim and may route it towards closer scrutiny. Human authority produces the decision, and the audit layer records it. Automated assistance, when introduced in the third phase, enters at the corroboration and evidence-assessment layers as an additional signal; it does not enter the authority layer at all.

Three propositions carry this framework into Chapter Three. First, confidence is a routing device, not a truth claim: its function is to determine how much scrutiny a case receives, and the project's interpretation rule forbids presenting it as a determination of what is true. Second, every signal in the framework has a documented failure mode, and the design response in each case is to route to a human rather than to decide. Third, the framework's value is an empirical question: whether layering these mechanisms improves precision, traceability, and operational usefulness over a human-only baseline is what the staged evaluation is designed to test, and the hypotheses in Chapter One are stated so that the answer may be negative.

## 2.15 Chapter Summary

This chapter established the conceptual and empirical basis for the SaloneFix design. The accountability literature showed that disclosure alone is insufficient and that explanation, judgement, and consequence must each be supported, which generates requirements for status history, institutional responsibility, required evidence, dispute, and audit access that no submission form satisfies. The Sierra Leonean digital-government context supplied constraints on devices, connectivity, and institutional capacity that make graceful degradation and human fallback requirements rather than refinements.

The review of each technical mechanism found a usable signal paired with a specific and well-documented limitation. Crowdsourced reporting offers coverage but is socially biased in who reports. Spatial clustering offers corroboration but can manufacture false consensus and penalise isolated reports. Image metadata offers evidence checks but is routinely absent, trivially alterable, and in tension with the location privacy of the person reporting. Multimodal classification offers complementarity and conflict detection but fails unevenly across conditions. Human oversight offers accountability but can be nominal rather than substantive. These paired findings are the reason the design concentrates authority in recorded human decisions while using automated signals only to direct attention.

The comparative review found that the individual components of the design exist in deployed systems, and that what is absent is their combination into a pipeline where verification precedes institutional dispatch, evidence is required at closure, a citizen can dispute a resolution, and an independent auditor can reconstruct the lifecycle. The related-studies review found that the improvement this project hypothesises is genuinely uncertain, which is why the evaluation is staged to isolate each mechanism's contribution rather than demonstrating the pipeline as a whole.

Chapter Three sets out the methodology and the design of the system that implements this framework: the research design and development approach, the requirements derived from this review, the system architecture and data model, the verification pipeline, the technology stack, the ethical and privacy framework, and the testing and evaluation strategy through which the hypotheses stated in Chapter One are tested.

---

## References

*Sources cited in Chapter One are repeated here where they are also cited in this chapter, so that each chapter is self-contained. The final report consolidates both lists into a single reference section.*

African Development Bank (2025) *Sierra Leone – Digital Innovation for Government Efficiency and Sector Transformation (DIGEST)*. Available at: https://mapafrica.afdb.org/en/projects/46002-P-SL-GB0-003

Alvarez, P. (2004) 'Using Extended File Information (EXIF) file headers in digital evidence analysis', *International Journal of Digital Evidence*, 2(3). Available at: https://www.utica.edu/academic/institutes/ecii/publications/articles/A0B1F944-FF4E-4788-E75541A7418DAE24.pdf

Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., Suh, J., Iqbal, S., Bennett, P.N., Inkpen, K., Teevan, J., Kikin-Gil, R. and Horvitz, E. (2019) 'Guidelines for human-AI interaction', in *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*. Available at: https://doi.org/10.1145/3290605.3300233

Baltrušaitis, T., Ahuja, C. and Morency, L.-P. (2019) 'Multimodal machine learning: a survey and taxonomy', *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 41(2), pp. 423–443. Available at: https://doi.org/10.1109/TPAMI.2018.2798607

Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M.T. and Weld, D.S. (2021) 'Does the whole exceed its parts? The effect of AI explanations on complementary team performance', in *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems*. Available at: https://doi.org/10.1145/3411764.3445717

Basiri, A., Haklay, M., Foody, G. and Mooney, P. (2019) 'Crowdsourced geospatial data quality: challenges and future directions', *International Journal of Geographical Information Science*, 33(8), pp. 1588–1593. Available at: https://doi.org/10.1080/13658816.2019.1593422

Bovens, M. (2007) 'Analysing and assessing accountability: a conceptual framework', *European Law Journal*, 13(4), pp. 447–468. Available at: https://doi.org/10.1111/j.1468-0386.2007.00378.x

Brooke, J. (1996) 'SUS: a "quick and dirty" usability scale', in Jordan, P.W., Thomas, B., Weerdmeester, B.A. and McClelland, I.L. (eds.) *Usability Evaluation in Industry*. London: Taylor & Francis, pp. 189–194.

Buolamwini, J. and Gebru, T. (2018) 'Gender shades: intersectional accuracy disparities in commercial gender classification', in *Proceedings of the 1st Conference on Fairness, Accountability and Transparency*, *Proceedings of Machine Learning Research*, 81, pp. 77–91. Available at: https://proceedings.mlr.press/v81/buolamwini18a.html

Clark, B.Y., Brudney, J.L. and Jang, S.-G. (2013) 'Coproduction of government services and the new information technology: investigating the distributional biases', *Public Administration Review*, 73(5), pp. 687–701. Available at: https://doi.org/10.1111/puar.12092

Ester, M., Kriegel, H.-P., Sander, J. and Xu, X. (1996) 'A density-based algorithm for discovering clusters in large spatial databases with noise', in *Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD-96)*. Menlo Park, CA: AAAI Press, pp. 226–231.

Farid, H. (2009) 'Image forgery detection', *IEEE Signal Processing Magazine*, 26(2), pp. 16–25. Available at: https://doi.org/10.1109/MSP.2008.931079

Flanagin, A.J. and Metzger, M.J. (2008) 'The credibility of volunteered geographic information', *GeoJournal*, 72(3–4), pp. 137–148. Available at: https://doi.org/10.1007/s10708-008-9188-y

Fung, A., Graham, M. and Weil, D. (2007) *Full Disclosure: The Perils and Promise of Transparency*. Cambridge: Cambridge University Press.

Gaventa, J. and McGee, R. (2013) 'The impact of transparency and accountability initiatives', *Development Policy Review*, 31(s1), pp. s3–s28. Available at: https://doi.org/10.1111/dpr.12017

Goodchild, M.F. (2007) 'Citizens as sensors: the world of volunteered geography', *GeoJournal*, 69(4), pp. 211–221. Available at: https://doi.org/10.1007/s10708-007-9111-y

Goodchild, M.F. and Li, L. (2012) 'Assuring the quality of volunteered geographic information', *Spatial Statistics*, 1, pp. 110–120. Available at: https://doi.org/10.1016/j.spasta.2012.03.002

Green, B. and Chen, Y. (2019) 'The principles and limits of algorithm-in-the-loop decision making', *Proceedings of the ACM on Human-Computer Interaction*, 3(CSCW), article 50. Available at: https://doi.org/10.1145/3359152

Grimmelikhuijsen, S.G. and Meijer, A.J. (2014) 'Effects of transparency on the perceived trustworthiness of a government organization: evidence from an online experiment', *Journal of Public Administration Research and Theory*, 24(1), pp. 137–157. Available at: https://doi.org/10.1093/jopart/mus048

Haklay, M. (2010) 'How good is volunteered geographical information? A comparative study of OpenStreetMap and Ordnance Survey datasets', *Environment and Planning B: Planning and Design*, 37(4), pp. 682–703. Available at: https://doi.org/10.1068/b35097

International Organization for Standardization (2019) *ISO/IEC 27701:2019: Security techniques — Extension to ISO/IEC 27001 and ISO/IEC 27002 for privacy information management*. Available at: https://www.iso.org/standard/71670.html

Joshi, A. (2013) 'Do they work? Assessing the impact of transparency and accountability initiatives in service delivery', *Development Policy Review*, 31(s1), pp. s29–s48. Available at: https://doi.org/10.1111/dpr.12018

Kee, E., Johnson, M.K. and Farid, H. (2011) 'Digital image authentication from JPEG headers', *IEEE Transactions on Information Forensics and Security*, 6(3), pp. 1066–1075. Available at: https://doi.org/10.1109/TIFS.2011.2128309

Kontokosta, C.E. and Hong, B. (2021) 'Bias in smart city governance: how socio-spatial disparities in 311 complaint behavior impact the fairness of data-driven decisions', *Sustainable Cities and Society*, 64, 102503. Available at: https://doi.org/10.1016/j.scs.2020.102503

Linders, D. (2012) 'From e-government to we-government: defining a typology for citizen coproduction in the age of social media', *Government Information Quarterly*, 29(4), pp. 446–454. Available at: https://doi.org/10.1016/j.giq.2012.06.003

Meier, P. (2015) *Digital Humanitarians: How Big Data Is Changing the Face of Humanitarian Response*. Boca Raton, FL: CRC Press.

mySociety (no date) *FixMyStreet*. Available at: https://www.fixmystreet.com/

National Institute of Standards and Technology (2023) *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST AI 100-1. Available at: https://doi.org/10.6028/NIST.AI.100-1

O'Brien, D.T., Offenhuber, D., Baldwin-Philippi, J., Sands, M. and Gordon, E. (2017) 'Uncharted territoriality in coproduction: the motivations for 311 reporting', *Journal of Public Administration Research and Theory*, 27(2), pp. 320–335. Available at: https://doi.org/10.1093/jopart/muw046

Offenhuber, D. (2015) 'Infrastructure legibility — a comparative analysis of Open311-based citizen feedback systems', *Cambridge Journal of Regions, Economy and Society*, 8(1), pp. 93–112. Available at: https://doi.org/10.1093/cjres/rsu001

Okolloh, O. (2009) 'Ushahidi, or "testimony": Web 2.0 tools for crowdsourcing crisis information', *Participatory Learning and Action*, 59(1), pp. 65–70.

Open Government Partnership (2021–2023) *Citizen Participation in Parliament (SL0030): Sierra Leone Action Plan 2021–2023*. Available at: https://www.opengovpartnership.org/members/sierra-leone/commitments/sl0030/

Ostrom, E. (1996) 'Crossing the great divide: coproduction, synergy, and development', *World Development*, 24(6), pp. 1073–1087. Available at: https://doi.org/10.1016/0305-750X(96)00023-X

OWASP Foundation (no date) *Application Security Verification Standard (ASVS)*. Available at: https://owasp.org/www-project-application-security-verification-standard/

Peixoto, T. and Fox, J. (2016) 'When does ICT-enabled citizen voice lead to government responsiveness?', *IDS Bulletin*, 47(1), pp. 23–40. Available at: https://doi.org/10.19088/1968-2016.104

Piva, A. (2013) 'An overview on image forensics', *ISRN Signal Processing*, 2013, article 496701. Available at: https://doi.org/10.1155/2013/496701

Radford, A., Kim, J.W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Askell, A., Mishkin, P., Clark, J., Krueger, G. and Sutskever, I. (2021) 'Learning transferable visual models from natural language supervision', in *Proceedings of the 38th International Conference on Machine Learning*, *Proceedings of Machine Learning Research*, 139, pp. 8748–8763. Available at: https://proceedings.mlr.press/v139/radford21a.html

Sabi Salone (no date) *Sabi Salone: AI-supported access to Sierra Leonean policy, legal and research information*. *(URL to be confirmed before submission.)*

SeeClickFix (no date) *SeeClickFix citizen reporting and request management*. Available at: https://seeclickfix.com/

Shneiderman, B. (2020) 'Human-centered artificial intelligence: reliable, safe and trustworthy', *International Journal of Human–Computer Interaction*, 36(6), pp. 495–504. Available at: https://doi.org/10.1080/10447318.2020.1741118

Sjoberg, F.M., Mellon, J. and Peixoto, T. (2017) 'The effect of bureaucratic responsiveness on citizen participation', *Public Administration Review*, 77(3), pp. 340–351. Available at: https://doi.org/10.1111/puar.12697

Ushahidi (no date) *Ushahidi Platform*. Available at: https://www.ushahidi.com/

World Bank (2021) *Sierra Leone Digital Economy Diagnostic*. Available at: https://openknowledge.worldbank.org/entities/publication/1ef37484-3de5-553a-b58e-9867d6f146ed

World Bank (2026) *Strengthening Citizen Participation in Sierra Leone: A Policy and Institutional Roadmap*. Available at: https://documents.worldbank.org/en/publication/documents-reports/documentdetail/099022726040510797

World Wide Web Consortium (2024) *Web Content Accessibility Guidelines (WCAG) 2.2*. Available at: https://www.w3.org/TR/WCAG22/

Wu, X., Xiao, L., Sun, Y., Zhang, J., Ma, T. and He, L. (2022) 'A survey of human-in-the-loop for machine learning', *Future Generation Computer Systems*, 135, pp. 364–381. Available at: https://doi.org/10.1016/j.future.2022.05.014
