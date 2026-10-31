from enum import Enum

class EmployeeStatus(str, Enum):
    ACTIVE = "Active"
    ONLEAVE = "On leave"
    TERMINATED = "Terminated"
    SUSPENDED = "Suspended"

class EmployeeClassification(str, Enum):
    FULLTIME = "Full-Time"
    PARTTIME = "Part-Time"
    CONTRACTOR = "Contractor"
    INTERN = "Intern"
    TEMPORARY = "Temporary"

class EmployeeSite(str, Enum):
    ONSITE = "On-Site"
    REMOTE = "Remotely"
    HYBRID = "Hybrid"

class PayFrequently(str, Enum):
    WEEKLY = "Weekly"
    BIWEEKLY = "Bi-Weekly"
    SEMIMONTHLY = "Semi-Monthly"
    MONTHLY = "Monthly"

class PayRateType(str, Enum):
    SALARIED = "Salaried"
    HOURLY = "Hourly"
    PIECEWORK = "Piecework"
    COMMISSION = "Commission"
