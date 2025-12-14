"""Notification system for client communications."""

from typing import List
from models import BannerRecord
from datetime import datetime


class NotificationService:
    """Handles notifications for various banner statuses."""
    
    def __init__(self, output_file: str = "notifications.txt"):
        """Initialize notification service."""
        self.output_file = output_file
    
    def generate_proof_ready_notification(self, banner: BannerRecord) -> str:
        """Generate notification when proof is ready for client review."""
        message = f"""
========================================
PROOF READY NOTIFICATION
========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hero Name: {banner.hero_name}
Sponsor: {banner.sponsor_name}
Email: {banner.sponsor_email}

Your banner proof is ready for review on the website.
Please visit: https://www.millcreekkiwanis.org/about-9

Once you review the proof, please provide your approval so we can proceed with printing.

If you have any questions or need changes, please contact us.

Thank you for supporting our hometown heroes!
========================================
"""
        return message
    
    def generate_incomplete_info_notification(self, banner: BannerRecord, missing_fields: List[str]) -> str:
        """Generate notification when banner information is incomplete."""
        message = f"""
========================================
INCOMPLETE INFORMATION
========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hero Name: {banner.hero_name}
Sponsor: {banner.sponsor_name}
Email: {banner.sponsor_email}

The following information is missing for this banner:
{chr(10).join(f'  - {field}' for field in missing_fields)}

Please provide the missing information to proceed.
========================================
"""
        return message
    
    def generate_payment_pending_notification(self, banner: BannerRecord) -> str:
        """Generate notification when payment is pending."""
        message = f"""
========================================
PAYMENT PENDING
========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hero Name: {banner.hero_name}
Sponsor: {banner.sponsor_name}
Email: {banner.sponsor_email}

We have received your banner information, but payment has not been verified.

Please complete payment to proceed with banner production.
========================================
"""
        return message
    
    def generate_print_approved_notification(self, banner: BannerRecord) -> str:
        """Generate notification when banner is approved for printing."""
        message = f"""
========================================
APPROVED FOR PRINTING
========================================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hero Name: {banner.hero_name}
Sponsor: {banner.sponsor_name}
Pole Location: {banner.pole_location or 'Not assigned'}

This banner has been approved and is ready for printing.
========================================
"""
        return message
    
    def save_notification(self, message: str):
        """Save notification to file."""
        with open(self.output_file, 'a') as f:
            f.write(message + '\n')
    
    def send_notifications_for_status(self, banners: List[BannerRecord], status: str):
        """Generate and save notifications for banners with specific status."""
        for banner in banners:
            if status.lower() == 'ready for proof' and banner.payment_verified and banner.info_complete and not banner.proof_sent:
                message = self.generate_proof_ready_notification(banner)
                self.save_notification(message)
                print(f"Notification generated for {banner.hero_name}")
