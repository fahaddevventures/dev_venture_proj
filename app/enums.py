import enum

class ProjectStatusEnum(enum.Enum):
    active = 'active'
    completed = 'completed'

class ProposalStatusEnum(enum.Enum):
    draft = 'draft'
    sent = 'sent'
    rejected = 'rejected'
    accepted = 'accepted'

class ContractTypeEnum(enum.Enum):
    hourly = 'Hourly'
    fixed_price = 'Fixed Price'
    unknown = 'Unknown'

class TaskStatusEnum(enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    completed = 'completed'

class TaskPriorityEnum(enum.Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

class BudgetTypeEnum(enum.Enum):
    fixed = 'fixed'
    hourly = 'hourly'

class FeasibilityEnum(enum.Enum):
    pending = 'pending'
    valid = 'valid'
    scam = 'scam'
    unsure = 'unsure'

class ProfileStatusEnum(enum.Enum):
    active = 'active'
    inactive = 'inactive'

class UserRoleEnum(enum.Enum):
    admin = 'admin'
    team_lead = 'team_lead'
    employee = 'employee'
    salesman = 'salesman'


