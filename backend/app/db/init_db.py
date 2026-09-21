import logging
from pathlib import Path
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.models.entities import ServiceCategory, Institution, User
from app.models.enums import UserRole
from app.core.security import hash_password
from app.core.config import settings

logger = logging.getLogger("salonefix.db")

# Revision that matches a database created by Base.metadata.create_all() before
# Alembic was introduced. Such databases are stamped here, then upgraded.
LEGACY_BASELINE_REVISION = "0001"


def run_migrations() -> None:
    """Bring the configured database to the latest Alembic revision.

    - Fresh database  -> all migrations applied.
    - Legacy database (tables exist, no alembic_version) -> stamped at the
      baseline, then upgraded, so pre-Alembic dev databases keep working.
    """
    from alembic import command
    from alembic.config import Config

    backend_root = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    inspector = inspect(engine)
    if inspector.has_table("users") and not inspector.has_table("alembic_version"):
        logger.warning("legacy_database_detected", extra={"data": {"stamp": LEGACY_BASELINE_REVISION}})
        with engine.begin() as conn:
            # Pre-Alembic guard from the original prototype: very old files lack this column.
            cols = {c["name"] for c in inspector.get_columns("reports")}
            if "idempotency_key" not in cols:
                conn.execute(text("ALTER TABLE reports ADD COLUMN idempotency_key VARCHAR(128)"))
        command.stamp(cfg, LEGACY_BASELINE_REVISION)

    command.upgrade(cfg, "head")
    logger.info("migrations_applied")


def init_db(db: Session = None) -> None:
    """Apply schema and seed reference data.

    Called with no session at application startup: runs Alembic migrations.
    Called with a session by the test-suite: the caller has already created the
    schema (create_all on an in-memory database) and only seeding is needed.
    """
    close_db = False
    if db is None:
        run_migrations()
        db = SessionLocal()
        close_db = True

    try:
        # 1. Seed Service Categories
        categories_data = [
            {
                "code": "ROAD_POTHOLE",
                "name": "Roads & Potholes",
                "description": "Damaged asphalt, deep potholes, and road surface hazards.",
                "requires_resolution_evidence": True,
            },
            {
                "code": "DRAINAGE_FLOODING",
                "name": "Drainage & Flooding",
                "description": "Blocked gutters, culverts, stagnant water, and storm overflow.",
                "requires_resolution_evidence": True,
            },
            {
                "code": "WASTE_MANAGEMENT",
                "name": "Waste Management",
                "description": "Illegal dump sites, overflowing public bins, and uncollected refuse.",
                "requires_resolution_evidence": True,
            },
            {
                "code": "PUBLIC_FACILITIES",
                "name": "Public Facilities",
                "description": "Damaged street lights, public toilets, markets, and municipal structures.",
                "requires_resolution_evidence": True,
            },
        ]

        for cat_info in categories_data:
            existing = db.query(ServiceCategory).filter(ServiceCategory.code == cat_info["code"]).first()
            if not existing:
                cat = ServiceCategory(
                    code=cat_info["code"],
                    name=cat_info["name"],
                    description=cat_info["description"],
                    requires_resolution_evidence=cat_info["requires_resolution_evidence"],
                    is_active=True,
                )
                db.add(cat)

        db.commit()

        # 2. Seed Institutions
        institutions_data = [
            {
                "name": "Freetown City Council (FCC)",
                "description": "Municipal authority responsible for waste management, public facilities, and local infrastructure.",
                "service_area": "Freetown Municipality",
                "contact_channel": "fcc.civic@freetown.gov.sl",
            },
            {
                "name": "Sierra Leone Roads Authority (SLRA)",
                "description": "National authority managing primary roads, asphalt maintenance, and major bridges.",
                "service_area": "Greater Freetown & National",
                "contact_channel": "operations@slra.gov.sl",
            },
            {
                "name": "Guma Valley Water Company (GVWC)",
                "description": "Public water and major municipal drainage utility provider.",
                "service_area": "Freetown Peninsula",
                "contact_channel": "support@gumavalley.sl",
            },
        ]

        inst_map = {}
        for inst_info in institutions_data:
            existing = db.query(Institution).filter(Institution.name == inst_info["name"]).first()
            if not existing:
                inst = Institution(
                    name=inst_info["name"],
                    description=inst_info["description"],
                    service_area=inst_info["service_area"],
                    contact_channel=inst_info["contact_channel"],
                    is_active=True,
                )
                db.add(inst)
                db.flush()
                inst_map[inst.name] = inst.id
            else:
                inst_map[existing.name] = existing.id

        db.commit()

        # 3. Seed Standard Role Accounts
        users_data = [
            {
                "contact": "admin@salonefix.gov.sl",
                "name_or_alias": "System Administrator",
                "password": "AdminPass123!",
                "role": UserRole.ADMIN,
                "institution_id": None,
            },
            {
                "contact": "moderator@salonefix.gov.sl",
                "name_or_alias": "Civic Moderator Alpha",
                "password": "ModPass123!",
                "role": UserRole.MODERATOR,
                "institution_id": None,
            },
            {
                "contact": "officer.fcc@salonefix.gov.sl",
                "name_or_alias": "FCC Works Officer",
                "password": "OfficerPass123!",
                "role": UserRole.OFFICER,
                "institution_id": inst_map.get("Freetown City Council (FCC)"),
            },
            {
                "contact": "officer.slra@salonefix.gov.sl",
                "name_or_alias": "SLRA Roads Engineer",
                "password": "OfficerPass123!",
                "role": UserRole.OFFICER,
                "institution_id": inst_map.get("Sierra Leone Roads Authority (SLRA)"),
            },
            {
                "contact": "citizen@freetown.sl",
                "name_or_alias": "Fatu Kamara",
                "password": "CitizenPass123!",
                "role": UserRole.CITIZEN,
                "institution_id": None,
            },
            {
                "contact": "auditor@salonefix.gov.sl",
                "name_or_alias": "Independent Auditor",
                "password": "AuditorPass123!",
                "role": UserRole.AUDITOR,
                "institution_id": None,
            },
        ]

        for user_info in users_data:
            existing = db.query(User).filter(User.contact == user_info["contact"]).first()
            if not existing:
                u = User(
                    contact=user_info["contact"],
                    name_or_alias=user_info["name_or_alias"],
                    # Cheap hashing keeps the test suite fast; real cost in any other environment.
                    password_hash=hash_password(user_info["password"], rounds=4 if settings.APP_ENV in ("development", "test") else 12),
                    role=user_info["role"],
                    institution_id=user_info["institution_id"],
                    consent_status=True,
                    is_active=True,
                )
                db.add(u)

        db.commit()
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    init_db()
    print("Database schema created and seed data initialized successfully.")
