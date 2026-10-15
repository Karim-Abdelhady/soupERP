from enum import Enum

class PermissionCatalog(str, Enum):

    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    SUPPLIER_READ = "supplier:read"
    SUPPLIER_CREATE = "supplier:create"
    SUPPLIER_UPDATE = "supplier:update"
    CUSTOMER_READ = "customer:read"
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_UPDATE = "customer:update"
    EMPLOYEE_READ = "employee:read"
    EMPLOYEE_CREATE = "employee:create"
    EMPLOYEE_UPDATE = "employee:update"
    ROLE_READ = "role:read"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_ASSIGN = "role:assign"
    PERMISSION_READ = "permission:read"
    PERMISSION_CREATE = "permission:create"
    PERMISSION_REMOVE = "permission:remove"
    ROLE_ADD_TO_USER = "role_add_to_user:create"