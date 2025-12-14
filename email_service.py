"""Microsoft 365 email integration for automated notifications and approval tracking."""

import os
import json
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import BannerRecord
from database import BannerDatabase

try:
    from O365 import Account, FileSystemTokenBackend
    O365_AVAILABLE = True
except ImportError:
    O365_AVAILABLE = False


class M365EmailService:
    """Handles automated email notifications and approval tracking via Microsoft 365."""
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str = None):
        """
        Initialize M365 email service.
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret  
            tenant_id: Azure AD tenant ID (optional, defaults to 'common')
        """
        if not O365_AVAILABLE:
            raise ImportError(
                "O365 library not installed. Install with: pip install O365"
            )
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id or 'common'
        
        # Setup credentials
        credentials = (client_id, client_secret)
        
        # Use file system token backend for persistent authentication
        token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token.txt')
        
        # Create account with proper scopes for sending and reading email
        self.account = Account(
            credentials,
            auth_flow_type='credentials',
            tenant_id=self.tenant_id,
            token_backend=token_backend
        )
        
        self.mailbox = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Microsoft 365.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Request necessary scopes
            scopes = ['https://graph.microsoft.com/Mail.Send',
                     'https://graph.microsoft.com/Mail.Read',
                     'https://graph.microsoft.com/Mail.ReadWrite']
            
            if self.account.authenticate(scopes=scopes):
                self.mailbox = self.account.mailbox()
                print("✓ Successfully authenticated with Microsoft 365")
                return True
            else:
                print("✗ Failed to authenticate with Microsoft 365")
                return False
        except Exception as e:
            print(f"✗ Authentication error: {e}")
            return False
    
    def send_proof_ready_email(self, banner: BannerRecord, proof_url: str = None) -> bool:
        """
        Send proof ready notification email to sponsor.
        
        Args:
            banner: Banner record with sponsor information
            proof_url: Optional URL to the proof (defaults to website)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.mailbox:
            print("✗ Not authenticated. Call authenticate() first.")
            return False
        
        if not banner.sponsor_email:
            print(f"✗ No email address for {banner.hero_name}")
            return False
        
        # Default proof URL
        if not proof_url:
            proof_url = "https://www.millcreekkiwanis.org/about-9"
        
        # Generate unique approval token (using banner ID and timestamp)
        approval_token = f"{banner.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create email message
        try:
            message = self.mailbox.new_message()
            message.to.add(banner.sponsor_email)
            message.subject = f"Hometown Hero Banner Proof Ready - {banner.hero_name}"
            
            # HTML email body with approval button
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #0066cc;">Your Banner Proof is Ready!</h2>
                
                <p>Dear {banner.sponsor_name},</p>
                
                <p>Great news! The banner proof for <strong>{banner.hero_name}</strong> is ready for your review.</p>
                
                <p>Please review the proof at: <a href="{proof_url}">{proof_url}</a></p>
                
                <div style="margin: 30px 0;">
                    <p><strong>To approve this proof, please reply to this email with "APPROVE" in the subject line.</strong></p>
                    <p>If you need any changes, please describe them in your reply.</p>
                </div>
                
                <hr style="border: 1px solid #ddd; margin: 20px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    Banner Details:<br>
                    Hero: {banner.hero_name}<br>
                    Sponsor: {banner.sponsor_name}<br>
                    Reference ID: {approval_token}
                </p>
                
                <p>Thank you for supporting our hometown heroes!</p>
                
                <p style="font-size: 12px; color: #666;">
                    Millcreek Kiwanis Club<br>
                    Hometown Hero Banner Program
                </p>
            </body>
            </html>
            """
            
            message.body = html_body
            message.body_type = 'HTML'
            
            # Send the email
            if message.send():
                print(f"✓ Email sent to {banner.sponsor_email} ({banner.hero_name})")
                return True
            else:
                print(f"✗ Failed to send email to {banner.sponsor_email}")
                return False
                
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def check_approval_responses(self, db: BannerDatabase, days_back: int = 7) -> List[Dict]:
        """
        Check inbox for approval responses and update database.
        
        Args:
            db: BannerDatabase instance to update
            days_back: Number of days to look back for emails
            
        Returns:
            List of dictionaries with processing results
        """
        if not self.mailbox:
            print("✗ Not authenticated. Call authenticate() first.")
            return []
        
        results = []
        
        try:
            # Get inbox folder
            inbox = self.mailbox.inbox_folder()
            
            # Query for emails received in the last N days
            query = inbox.new_query().on_attribute('receivedDateTime')
            query = query.greater_equal(datetime.now() - timedelta(days=days_back))
            
            # Get messages
            messages = inbox.get_messages(limit=100, query=query)
            
            for message in messages:
                # Check if this is a reply to our proof notification
                subject = message.subject or ""
                
                if "Hometown Hero Banner Proof" in subject or "APPROVE" in subject.upper():
                    # Try to extract banner reference
                    body = message.body or ""
                    
                    # Look for approval keyword in subject
                    is_approved = "APPROVE" in subject.upper()
                    
                    # Try to match to a banner by hero name or sponsor email
                    sender_email = message.sender.address if message.sender else None
                    
                    if sender_email:
                        # Find banner by sponsor email
                        banners = db.get_all_banners()
                        matching_banners = [b for b in banners 
                                          if b.sponsor_email and 
                                          b.sponsor_email.lower() == sender_email.lower()]
                        
                        for banner in matching_banners:
                            if not banner.proof_approved:
                                # Update banner approval status
                                banner.proof_approved = is_approved
                                db.update_banner(banner)
                                
                                result = {
                                    'hero_name': banner.hero_name,
                                    'sponsor_email': sender_email,
                                    'approved': is_approved,
                                    'received': message.received,
                                    'message_id': message.object_id
                                }
                                results.append(result)
                                
                                print(f"✓ Updated {banner.hero_name}: Approved={is_approved}")
                                
                                # Mark message as read
                                message.mark_as_read()
            
            return results
            
        except Exception as e:
            print(f"✗ Error checking approval responses: {e}")
            return results
    
    def send_bulk_notifications(self, banners: List[BannerRecord], db: BannerDatabase) -> Dict[str, int]:
        """
        Send proof ready notifications to multiple sponsors.
        
        Args:
            banners: List of banner records ready for notification
            db: Database instance to update proof_sent status
            
        Returns:
            Dictionary with counts of sent, failed, and skipped emails
        """
        stats = {'sent': 0, 'failed': 0, 'skipped': 0}
        
        for banner in banners:
            # Only send if ready and not already sent
            if banner.payment_verified and banner.info_complete and not banner.proof_sent:
                if self.send_proof_ready_email(banner):
                    # Mark as sent in database
                    banner.proof_sent = True
                    db.update_banner(banner)
                    stats['sent'] += 1
                else:
                    stats['failed'] += 1
            else:
                stats['skipped'] += 1
        
        return stats


def load_m365_config(config_file: str = 'm365_config.json') -> Optional[Dict]:
    """
    Load M365 configuration from JSON file.
    
    Expected format:
    {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "tenant_id": "your-tenant-id"  (optional)
    }
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary or None if file doesn't exist
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
    return None


def create_m365_config_template(config_file: str = 'm365_config.json'):
    """
    Create a template M365 configuration file.
    
    Args:
        config_file: Path to create configuration file
    """
    template = {
        "client_id": "YOUR_AZURE_AD_CLIENT_ID",
        "client_secret": "YOUR_AZURE_AD_CLIENT_SECRET",
        "tenant_id": "YOUR_TENANT_ID_OR_common"
    }
    
    with open(config_file, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"✓ Created template configuration file: {config_file}")
    print("\nPlease edit the file and add your Microsoft 365 credentials.")
    print("\nTo set up Azure AD app registration:")
    print("1. Go to https://portal.azure.com")
    print("2. Navigate to Azure Active Directory > App registrations")
    print("3. Create a new registration")
    print("4. Add permissions: Mail.Send, Mail.Read, Mail.ReadWrite")
    print("5. Create a client secret")
    print("6. Copy the client ID, secret, and tenant ID to the config file")
