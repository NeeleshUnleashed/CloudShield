from typing import Optional, List
from fastapi import Header, Query, HTTPException, status
from app.models.approval import DemoRole

def get_current_role(
    x_user_role: Optional[str] = Header(None, alias="X-User-Role", description="Demo active user role"),
    role: Optional[str] = Query(None, description="Demo role query parameter override")
) -> DemoRole:
    """
    Extracts and validates the demo user role from HTTP headers or query parameter.
    
    ACADEMIC GOVERNANCE NOTE:
    Demo role selection is designed for college evaluation and interactive simulation.
    It demonstrates backend role enforcement, separation of concerns, and permission gates.
    It is NOT production-grade cryptographic authentication (OAuth2 / JWT).
    """
    selected_role_str = x_user_role or role or DemoRole.EMERGENCY_OFFICER.value
    
    try:
        return DemoRole(selected_role_str.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid demo role '{selected_role_str}'. Valid roles: {[r.value for r in DemoRole]}"
        )

def require_roles(allowed_roles: List[DemoRole], current_role: DemoRole):
    """
    Enforces role-based permission boundaries on backend endpoints.
    Throws 403 Forbidden if current_role is not in allowed_roles.
    """
    if current_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Access Denied: Role '{current_role.value}' is not authorized for this operation. "
                f"Required role(s): {[r.value for r in allowed_roles]}."
            )
        )
