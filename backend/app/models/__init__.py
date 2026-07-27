"""SQLAlchemy models for the Mithrava platform.

All models are imported here so that Base.metadata.create_all() and
Alembic autogenerate can discover every table.
"""

from app.models.farmer import Farmer
from app.models.crop import Crop
from app.models.disease import DiseaseScan
from app.models.finance import Expense, Income
from app.models.vendor import Vendor, VendorReview
from app.models.forum import ForumPost, ForumComment, ForumLike
from app.models.mitra import MitraConversation, MitraMessage
from app.models.notification import Notification
from app.models.knowledge import (
    KnowledgeCategory,
    KnowledgeArticle,
    KnowledgeChunk,
    KnowledgeDocument,
    DocumentEmbedding,
)
from app.models.push_subscription import PushSubscription
from app.models.device_token import DeviceToken
from app.models.support import SupportCall
from app.models.otp import OTPCode
from app.models.audit_log import AuditLog
from app.models.land import Land
from app.models.market_price import MarketPrice
from app.models.expert_call import ExpertCall
from app.models.refresh_token import RefreshToken
from app.models.settings import FarmerSetting

__all__ = [
    # Core entities
    "Farmer",
    "Crop",
    "DiseaseScan",
    "Expense",
    "Income",
    # Marketplace
    "Vendor",
    "VendorReview",
    # Community
    "ForumPost",
    "ForumComment",
    "ForumLike",
    # AI Assistant
    "MitraConversation",
    "MitraMessage",
    # Notifications
    "Notification",
    "PushSubscription",
    "DeviceToken",
    # Knowledge / RAG
    "KnowledgeCategory",
    "KnowledgeArticle",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "DocumentEmbedding",
    # Support
    "SupportCall",
    # Auth / Security
    "OTPCode",
    "RefreshToken",
    # Audit / Compliance
    "AuditLog",
    # Land / Market
    "Land",
    "MarketPrice",
    "ExpertCall",
    # Settings
    "FarmerSetting",
]
