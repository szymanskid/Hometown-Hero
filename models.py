"""Data models for the Hometown Hero banner verification system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List


@dataclass
class HeroInfo:
    """Hero information from CMS CSV."""
    name: str
    service_branch: Optional[str] = None
    rank: Optional[str] = None
    years_served: Optional[str] = None
    hometown: Optional[str] = None
    photo_path: Optional[str] = None
    sponsor_name: Optional[str] = None
    sponsor_email: Optional[str] = None
    sponsor_phone: Optional[str] = None
    
    def is_complete(self) -> Tuple[bool, List[str]]:
        """Check if all required fields are present."""
        missing = []
        required_fields = {
            'name': self.name,
            'service_branch': self.service_branch,
            'photo_path': self.photo_path,
            'sponsor_name': self.sponsor_name,
            'sponsor_email': self.sponsor_email
        }
        
        for field_name, value in required_fields.items():
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(field_name)
        
        return len(missing) == 0, missing


@dataclass
class PaymentInfo:
    """Payment information from payment CSV."""
    sponsor_name: str
    amount_paid: float
    payment_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    
    def is_paid(self) -> bool:
        """Check if payment is complete."""
        return self.amount_paid > 0


@dataclass
class BannerRecord:
    """Complete banner record with persistent data."""
    id: Optional[int] = None
    hero_name: str = ""
    sponsor_name: str = ""
    sponsor_email: str = ""
    info_complete: bool = False
    payment_verified: bool = False
    documents_verified: bool = False
    photo_verified: bool = False
    proof_sent: bool = False
    proof_approved: bool = False
    print_approved: bool = False
    submitted_to_printer: bool = False
    pole_location: Optional[str] = None
    thank_you_sent: bool = False
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def get_status(self) -> str:
        """Get current status of the banner."""
        if self.thank_you_sent:
            return "Complete - Thank You Sent"
        elif self.submitted_to_printer:
            return "Submitted to Printer"
        elif self.print_approved:
            return "Approved for Printing"
        elif self.proof_approved:
            return "Proof Approved by Customer"
        elif self.proof_sent:
            return "Awaiting Customer Approval"
        elif self.photo_verified and self.documents_verified:
            return "Ready to Send Proof"
        elif self.documents_verified:
            return "Documents Verified - Photo Pending"
        elif self.payment_verified and self.info_complete:
            return "Paid - Awaiting Verification"
        elif self.payment_verified:
            return "Paid - Info Incomplete"
        elif self.info_complete:
            return "Info Complete - Payment Pending"
        else:
            return "Incomplete"
