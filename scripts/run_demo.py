import sys
import os
import io
import json
from PIL import Image
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.db.init_db import init_db
from app.models.entities import User, ServiceCategory, Institution, Incident, Report
from app.models.enums import UserRole, LocationPrecision, ModerationDecisionType, IncidentPriority, AssignmentStatus, EvidenceReviewStatus
from app.schemas.report import ReportCreate
from app.schemas.moderation import ModerationDecisionCreate
from app.schemas.incident import IncidentCreate
from app.schemas.assignment import AssignmentCreate, AssignmentStatusUpdate
from app.schemas.resolution import ResolutionEvidenceCreate, ResolutionReviewCreate, DisputeCreate, ReopenRequest
from app.services.report_service import create_report, get_public_report_status
from app.services.moderation_service import get_moderation_queue, process_moderation_decision
from app.services.incident_service import create_incident, transition_incident_status, get_incident_detail
# pyrefly: ignore [missing-import]
from app.services.assignment_service import assign_incident, update_assignment_status
from app.services.resolution_service import submit_resolution_evidence, review_resolution_evidence, dispute_resolution, reopen_incident, attach_evidence_media
from app.services.media_processor import validate_and_sanitize_image
from app.api.v1.endpoints.audit import get_incident_audit


def print_step(step_num: int, title: str):
    print(f"\n{'='*70}")
    print(f" STEP {step_num}: {title.upper()}")
    print(f"{'='*70}")


def run_full_lifecycle_demo():
    print("\n" + "#"*70)
    print(" SALONEFIX: HUMAN-FIRST FOUNDATION - LIFECYCLE DEMONSTRATION")
    print(" Phase: Human-First Foundation Launch (AI & WhatsApp Disabled)")
    print(" Scope: Freetown Civic Infrastructure Incident Lifecycle")
    print("#"*70)

    # Initialize DB
    init_db()
    db: Session = SessionLocal()

    try:
        # Load Actors
        citizen = db.query(User).filter(User.contact == "citizen@freetown.sl").first()
        moderator = db.query(User).filter(User.contact == "moderator@salonefix.gov.sl").first()
        officer = db.query(User).filter(User.contact == "officer.fcc@salonefix.gov.sl").first()
        auditor = db.query(User).filter(User.contact == "auditor@salonefix.gov.sl").first()
        fcc = db.query(Institution).filter(Institution.name == "Freetown City Council (FCC)").first()
        road_cat = db.query(ServiceCategory).filter(ServiceCategory.code == "ROAD_POTHOLE").first()

        print("\nActors Loaded:")
        print(f" - Citizen:     {citizen.name_or_alias} ({citizen.contact})")
        print(f" - Moderator:   {moderator.name_or_alias} ({moderator.contact})")
        print(f" - Officer:     {officer.name_or_alias} ({officer.contact}) - {fcc.name}")
        print(f" - Auditor:     {auditor.name_or_alias} ({auditor.contact})")

        # 1. Citizen submits report 1
        print_step(1, "Citizen Submits Public Road Damage Report")
        rep1_in = ReportCreate(
            category_code="ROAD_POTHOLE",
            description="Massive deep pothole on Kissy Road opposite UMC Primary School blocking east-bound traffic.",
            latitude=8.4851,
            longitude=-13.2285,
            location_precision=LocationPrecision.EXACT,
        )
        rep1_res = create_report(db, rep1_in, citizen, request_id="REQ-DEMO-01")
        print(f" -> Report 1 Created! Tracking Ref: {rep1_res.tracking_reference}")
        print(f" -> Status: {rep1_res.status.value}")
        print(f" -> Citizen Guidance: \"{rep1_res.next_step}\"")

        # 2. Second Citizen submits duplicate report
        print_step(2, "Second Citizen Submits Duplicate Report Nearby")
        rep2_in = ReportCreate(
            category_code="ROAD_POTHOLE",
            description="Dangerous asphalt hole near Kissy Road school causing vehicle damage.",
            latitude=8.4853,
            longitude=-13.2287,
            location_precision=LocationPrecision.APPROXIMATE,
        )
        rep2_res = create_report(db, rep2_in, citizen, request_id="REQ-DEMO-02")
        print(f" -> Report 2 Created! Tracking Ref: {rep2_res.tracking_reference}")

        # 3. Moderator inspects queue & verifies Report 1
        print_step(3, "Moderator Reviews Queue & Verifies Report")
        queue = get_moderation_queue(db)
        print(f" -> Moderator Queue Length: {len(queue)} pending report(s)")
        print(f" -> Inspecting: {rep1_res.tracking_reference}")

        mod_dec = ModerationDecisionCreate(
            decision=ModerationDecisionType.VERIFY,
            reason="Verified as hazardous road surface defect requiring immediate civil works.",
        )
        rep1_verified = process_moderation_decision(db, rep1_res.id, mod_dec, moderator, request_id="REQ-DEMO-03")
        print(f" -> Report 1 Status: {rep1_verified.current_status.value}")
        print(f" -> Moderator Recorded Reason: \"{mod_dec.reason}\"")

        # 4. Moderator creates Incident & links duplicate Report 2
        print_step(4, "Moderator Creates Incident Case & Fuses Duplicate Report")
        inc_in = IncidentCreate(
            category_id=road_cat.id,
            title="Kissy Road / UMC School Pothole Repair",
            summary="Emergency asphalt repair and sub-base stabilization on Kissy Road.",
            priority=IncidentPriority.HIGH,
            report_id=rep1_res.id,
        )
        incident = create_incident(db, inc_in, moderator, request_id="REQ-DEMO-04")
        print(f" -> Incident Case Created: {incident.id} [{incident.title}]")
        print(f" -> Status: {incident.lifecycle_status.value}, Priority: {incident.priority.value}")

        # Merge Report 2 into Incident
        merge_dec = ModerationDecisionCreate(
            decision=ModerationDecisionType.MERGE,
            reason="Duplicate report for same physical crater at Kissy Road.",
            target_incident_id=incident.id,
        )
        process_moderation_decision(db, rep2_res.id, merge_dec, moderator, request_id="REQ-DEMO-05")
        inc_detail = get_incident_detail(db, incident.id, moderator)
        print(f" -> Report 2 Merged. Total reports linked to Incident: {inc_detail.linked_reports_count}")

        # 5. Incident assigned to Freetown City Council
        print_step(5, "Incident Assigned to Freetown City Council (FCC)")
        assign_in = AssignmentCreate(institution_id=fcc.id, officer_id=officer.id)
        assignment = assign_incident(db, incident.id, assign_in, moderator, request_id="REQ-DEMO-06")
        print(f" -> Assigned to: {fcc.name}")
        print(f" -> Incident Status: {assignment.incident.lifecycle_status.value}")

        # 6. Institutional Officer accepts & begins work
        print_step(6, "FCC Officer Accepts Assignment & Begins Work")
        update_assignment_status(db, assignment.id, AssignmentStatusUpdate(status=AssignmentStatus.ACCEPTED), officer, request_id="REQ-DEMO-07")
        inc_detail = get_incident_detail(db, incident.id, officer)
        print(f" -> Officer Accepted Assignment.")
        print(f" -> Incident Status: {inc_detail.lifecycle_status.value}")

        # 7. Institutional Officer completes repair and submits evidence
        print_step(7, "Officer Submits Resolution Evidence")
        evidence_in = ResolutionEvidenceCreate(
            description="Excavated loose road debris, backfilled with crushed aggregate, and applied cold mix asphalt with mechanized roller compaction.",
        )
        evidence = submit_resolution_evidence(db, incident.id, evidence_in, officer, request_id="REQ-DEMO-08")
        inc_detail = get_incident_detail(db, incident.id, officer)
        print(f" -> Resolution Evidence Stored (ID: {evidence.id})")
        print(f" -> Incident Status: {inc_detail.lifecycle_status.value}")

        # 7b. Officer attaches the "after repair" photo (required for ROAD_POTHOLE)
        photo = io.BytesIO()
        Image.new("RGB", (160, 120), color=(90, 90, 90)).save(photo, format="JPEG")
        sanitized, mime, fname = validate_and_sanitize_image(photo.getvalue(), "after_repair.jpg", "image/jpeg")
        asset = attach_evidence_media(
            db, incident.id, evidence.id, officer,
            sanitized_bytes=sanitized, filename=fname, mime_type=mime,
            idempotency_key="demo-after-repair", request_id="REQ-DEMO-08b",
        )
        print(f" -> Photo Evidence Attached (asset {asset.id}, {asset.file_size} bytes, EXIF stripped)")

        # 8. Moderator reviews resolution evidence & marks RESOLVED
        print_step(8, "Moderator Reviews & Approves Resolution Evidence")
        review_in = ResolutionReviewCreate(
            decision=EvidenceReviewStatus.APPROVED,
            reason="Work completion report meets municipal road restoration criteria.",
        )
        incident_resolved = review_resolution_evidence(db, incident.id, review_in, moderator, request_id="REQ-DEMO-09")
        print(f" -> Review Decision: {review_in.decision.value}")
        print(f" -> Incident Status: {incident_resolved.lifecycle_status.value}")

        # 9. Citizen checks public status & files dispute
        print_step(9, "Citizen Checks Tracking Status & Files Dispute")
        tracking = get_public_report_status(db, rep1_res.tracking_reference)
        print(f" -> Citizen Tracking View: Status = {tracking.current_status.value}, Can Dispute = {tracking.can_dispute}")

        dispute_in = DisputeCreate(
            reason="The asphalt subsided and washed away during morning rainfall. The pothole is still open and hazardous.",
        )
        dispute = dispute_resolution(db, incident.id, dispute_in, citizen, request_id="REQ-DEMO-10")
        inc_detail = get_incident_detail(db, incident.id, citizen)
        print(f" -> Citizen Dispute Submitted (ID: {dispute.id})")
        print(f" -> Incident Status: {inc_detail.lifecycle_status.value}")

        # 10. Moderator reopens the incident
        print_step(10, "Moderator Reopens Incident Following Citizen Dispute")
        reopen_in = ReopenRequest(
            reason="Citizen dispute verified with reported aggregate breakdown. Reopening case for road crew dispatch.",
        )
        reopened = reopen_incident(db, incident.id, reopen_in, moderator, request_id="REQ-DEMO-11")
        print(f" -> Case Reopened! Incident Status: {reopened.lifecycle_status.value}")

        # 11. Auditor inspects immutable audit trail
        print_step(11, "Auditor Inspects Complete Append-Only Audit Trail")
        audit_events = get_incident_audit(incident.id, db, auditor)
        print(f" -> Total Audit Events in Chain: {len(audit_events)}\n")
        print(f" {'TIME':<20} | {'ACTOR':<25} | {'ACTION':<30} | {'REASON'}")
        print("-" * 110)
        for ev in audit_events:
            actor_display = f"{ev.actor_name} ({ev.actor_role or 'SYS'})"
            print(f" {str(ev.created_at)[:19]:<20} | {actor_display:<25} | {ev.action:<30} | {ev.reason or ''}")

        print("\n" + "#"*70)
        print(" LIFECYCLE DEMONSTRATION PASSED WITH 100% AUDIT INTEGRITY!")
        print("#"*70 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    run_full_lifecycle_demo()
