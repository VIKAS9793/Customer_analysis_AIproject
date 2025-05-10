"""
Role-Based Access Control (RBAC) System

This module implements enterprise-grade RBAC following NIST SP 800-53 and ISO 27001 standards.
"""

import logging
from typing import Dict, Set, List, Optional, Type
from enum import Enum
from dataclasses import dataclass
from security.audit_trail import AuditTrail
from security.risk_assessment import RiskAssessment

class Permission(Enum):
    """Security permissions following ISO 27001 controls"""
    VIEW_TRANSACTIONS = "view_transactions"
    FLAG_TRANSACTIONS = "flag_transactions"
    REVIEW_TRANSACTIONS = "review_transactions"
    MANAGE_USERS = "manage_users"
    CONFIGURE_SYSTEM = "configure_system"
    MONITOR_SYSTEM = "monitor_system"
    ACCESS_LOGS = "access_logs"
    MANAGE_POLICIES = "manage_policies"
    OVERRIDE_RULES = "override_rules"
    ACCESS_SENSITIVE_DATA = "access_sensitive_data"
    
    @classmethod
    def get_risk_level(cls, permission: 'Permission') -> str:
        """Get risk level for permission"""
        high_risk = {
            Permission.ACCESS_SENSITIVE_DATA,
            Permission.OVERRIDE_RULES,
            Permission.MANAGE_POLICIES,
            Permission.CONFIGURE_SYSTEM
        }
        
        medium_risk = {
            Permission.MANAGE_USERS,
            Permission.ACCESS_LOGS,
            Permission.MONITOR_SYSTEM
        }
        
        if permission in high_risk:
            return "high"
        elif permission in medium_risk:
            return "medium"
        return "low"

class Role(Enum):
    """Security roles following ISO 27001 role-based access control"""
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    AUDITOR = "auditor"
    SECURITY_ADMIN = "security_admin"
    
    @property
    def risk_level(self) -> str:
        """Get risk level for role"""
        high_risk = {Role.SUPER_ADMIN, Role.SECURITY_ADMIN}
        medium_risk = {Role.ADMIN, Role.AUDITOR}
        
        if self in high_risk:
            return "high"
        elif self in medium_risk:
            return "medium"
        return "low"

class AccessControlError(Exception):
    """Raised when access control operations fail"""
    pass

@dataclass
class UserContext:
    """User context for access control decisions"""
    user_id: str
    role: Role
    permissions: Set[Permission]
    risk_level: str
    last_access: datetime
    ip_address: str
    user_agent: str
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has permission"""
        return permission in self.permissions

class RBAC:
    """
    Enterprise-grade Role-Based Access Control system.
    
    Implements NIST SP 800-53 AC-2, AC-3, AC-6 controls.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RBAC system.
        
        Args:
            config: Configuration containing:
                - role_hierarchy: Role hierarchy definitions
                - permission_mapping: Permission to role mapping
                - audit_config: Audit trail configuration
                - risk_config: Risk assessment configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.audit = AuditTrail(config["audit_config"])
        self.risk_assessment = RiskAssessment(config["risk_config"])
        
        # Initialize role hierarchy
        self.roles = self._initialize_roles()
        self.permission_hierarchy = self._initialize_permission_hierarchy()
        self.role_hierarchy = self._initialize_role_hierarchy()
        
        # Initialize user sessions
        self.user_sessions: Dict[str, UserContext] = {}
        
    def authenticate(self, user_id: str, role: Role, context: Dict[str, Any]) -> UserContext:
        """
        Authenticate user and create session context.
        
        Args:
            user_id: Unique user identifier
            role: User's role
            context: Authentication context (IP, user agent, etc.)
            
        Returns:
            UserContext with session information
            
        Raises:
            AccessControlError: If authentication fails
        """
        try:
            # Risk assessment
            risk_level = self.risk_assessment.evaluate_session(user_id, context)
            
            # Get role permissions
            permissions = self.roles[role]
            
            # Create user context
            user_context = UserContext(
                user_id=user_id,
                role=role,
                permissions=permissions,
                risk_level=risk_level,
                last_access=datetime.utcnow(),
                ip_address=context.get("ip_address", "unknown"),
                user_agent=context.get("user_agent", "unknown")
            )
            
            # Store session
            self.user_sessions[user_id] = user_context
            
            # Log authentication
            self.audit.log_event("authentication", {
                "user_id": user_id,
                "role": role.value,
                "risk_level": risk_level,
                "ip_address": context.get("ip_address")
            })
            
            return user_context
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise AccessControlError(f"Failed to authenticate user: {str(e)}")
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if user has permission.
        
        Args:
            user_id: User identifier
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        if user_id not in self.user_sessions:
            return False
            
        user_context = self.user_sessions[user_id]
        return user_context.has_permission(permission)
    
    def _initialize_roles(self) -> Dict[Role, Set[Permission]]:
        """Initialize role-to-permission mapping."""
        return {
            Role.ANALYST: {
                Permission.VIEW_TRANSACTIONS,
                Permission.FLAG_TRANSACTIONS
            },
            Role.REVIEWER: {
                Permission.VIEW_TRANSACTIONS,
                Permission.REVIEW_TRANSACTIONS,
                Permission.FLAG_TRANSACTIONS
            },
            Role.ADMIN: {
                Permission.VIEW_TRANSACTIONS,
                Permission.FLAG_TRANSACTIONS,
                Permission.REVIEW_TRANSACTIONS,
                Permission.MANAGE_USERS,
                Permission.MONITOR_SYSTEM
            },
            Role.SUPER_ADMIN: set(Permission),
            Role.AUDITOR: {
                Permission.ACCESS_LOGS,
                Permission.VIEW_TRANSACTIONS,
                Permission.MONITOR_SYSTEM
            },
            Role.SECURITY_ADMIN: {
                Permission.CONFIGURE_SYSTEM,
                Permission.MANAGE_POLICIES,
                Permission.ACCESS_LOGS,
                Permission.MONITOR_SYSTEM
            }
        }
    
    def _initialize_permission_hierarchy(self) -> Dict[Permission, Set[Permission]]:
        """Initialize permission hierarchy."""
        return {
            Permission.VIEW_TRANSACTIONS: set(),
            Permission.FLAG_TRANSACTIONS: {Permission.VIEW_TRANSACTIONS},
            Permission.REVIEW_TRANSACTIONS: {Permission.VIEW_TRANSACTIONS, Permission.FLAG_TRANSACTIONS},
            Permission.MANAGE_USERS: set(),
            Permission.CONFIGURE_SYSTEM: {Permission.MANAGE_USERS},
            Permission.MONITOR_SYSTEM: {Permission.VIEW_TRANSACTIONS},
            Permission.ACCESS_LOGS: set(),
            Permission.MANAGE_POLICIES: {Permission.CONFIGURE_SYSTEM},
            Permission.OVERRIDE_RULES: {Permission.CONFIGURE_SYSTEM},
            Permission.ACCESS_SENSITIVE_DATA: {Permission.VIEW_TRANSACTIONS}
        }
    
    def _initialize_role_hierarchy(self) -> Dict[Role, Set[Role]]:
        """Initialize role hierarchy."""
        return {
            Role.ANALYST: set(),
            Role.REVIEWER: {Role.ANALYST},
            Role.ADMIN: {Role.ANALYST, Role.REVIEWER},
            Role.SUPER_ADMIN: {Role.ANALYST, Role.REVIEWER, Role.ADMIN},
            Role.AUDITOR: {Role.ANALYST},
            Role.SECURITY_ADMIN: {Role.ADMIN}
        }
    
    def get_role_permissions(self, role: Role) -> Set[Permission]:
        """Get all permissions for a role."""
        return self.roles[role]
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for a user."""
        if user_id not in self.user_sessions:
            return set()
        return self.user_sessions[user_id].permissions
    
    def get_user_risk_level(self, user_id: str) -> str:
        """Get user's current risk level."""
        if user_id not in self.user_sessions:
            return "unknown"
        return self.user_sessions[user_id].risk_level
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get RBAC system metrics."""
        metrics = {
            "active_users": len(self.user_sessions),
            "roles": len(self.roles),
            "permissions": len(Permission),
            "high_risk_users": len([u for u in self.user_sessions.values() 
                                  if u.risk_level == "high"]),
            "medium_risk_users": len([u for u in self.user_sessions.values() 
                                    if u.risk_level == "medium"])
        }
        return metrics

    def __init__(self, config: Dict[str, Any]):
        """Initialize RBAC system"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Security parameters
        self.users: Dict[str, Role] = {}
        self.permissions: Dict[str, Set[Permission]] = {}
        self.roles: Dict[str, Set[Permission]] = {
            "admin": {"read", "write", "delete", "admin"},
            "user": {"read", "write"},
            "guest": {"read"}
        }
        self.role_hierarchy: Dict[str, List[str]] = {
            "admin": ["user", "guest"],
            "user": ["guest"]
        }
    
    def add_user(self, user_id: str, role: Role) -> None:
        """Add user with specified role"""
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")
        self.users[user_id] = role
        self.permissions[user_id] = self.roles[role]
    
    def remove_user(self, user_id: str) -> None:
        """Remove user from system"""
        if user_id in self.users:
            del self.users[user_id]
            del self.permissions[user_id]
    
    def verify_permission(self, user_id: str, permission: Permission) -> bool:
        """Verify if user has permission"""
        if user_id not in self.permissions:
            raise AccessControlError(f"User {user_id} not found")
            
        return permission in self.permissions[user_id]
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get all permissions for user"""
        return self.permissions.get(user_id, set())
    
    def get_user_role(self, user_id: str) -> Optional[Role]:
        """Get user's role"""
        return self.users.get(user_id)
    
    def verify_transaction_access(self, user_id: str, transaction_id: str) -> bool:
        """Verify if user can access transaction"""
        if not self.verify_permission(user_id, Permission.VIEW_TRANSACTIONS):
            return False
            
        # Add additional transaction-specific access checks here
        return True
    
    def verify_flagging_access(self, user_id: str, transaction_id: str) -> bool:
        """Verify if user can flag transaction"""
        if not self.verify_permission(user_id, Permission.FLAG_TRANSACTIONS):
            return False
            
        # Add additional flagging-specific access checks here
        return True
    
    def verify_review_access(self, user_id: str, transaction_id: str) -> bool:
        """Verify if user can review transaction"""
        if not self.verify_permission(user_id, Permission.REVIEW_TRANSACTIONS):
            return False
            
        # Add additional review-specific access checks here
        return True
