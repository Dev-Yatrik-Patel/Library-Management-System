from app.models.audit_log import AuditLog

def log_audit(
    db,
    action: str,
    entity: str,
    entity_id: int | None = None,
    performed_by: int | None = None,
    message: str | None = None
):
    
    audit = AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        performed_by=performed_by,
        message=message
    )
    db.add(audit)