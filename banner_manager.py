#!/usr/bin/env python3
"""
Hometown Hero Banner Management System

This script manages the banner verification process for the Millcreek Kiwanis
Hometown Hero program. It processes CSV files from Wix, verifies completeness,
tracks payment, manages notifications, and handles signoff for printing.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from models import BannerRecord
from database import BannerDatabase
from csv_processor import CSVProcessor
from notifications import NotificationService
import config

# Optional M365 email support
try:
    from email_service import M365EmailService, load_m365_config, create_m365_config_template
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


def import_csvs(hero_csv: str, payment_csv: str, db: BannerDatabase):
    """Import and process CSV files from Wix."""
    print(f"\n{'='*60}")
    print("IMPORTING CSV FILES")
    print(f"{'='*60}\n")
    
    # Parse CSV files
    print(f"Reading hero information from: {hero_csv}")
    heroes = CSVProcessor.parse_hero_csv(hero_csv)
    print(f"Found {len(heroes)} hero records\n")
    
    print(f"Reading payment information from: {payment_csv}")
    payments = CSVProcessor.parse_payment_csv(payment_csv)
    print(f"Found {len(payments)} payment records\n")
    
    # Generate import report
    print(f"{'='*60}")
    print("IMPORT ANALYSIS")
    print(f"{'='*60}\n")
    
    import_report = CSVProcessor.generate_import_report(heroes, payments)
    
    print(f"Total heroes in CMS CSV:        {import_report['total_heroes']}")
    print(f"Total payments in payment CSV:  {import_report['total_payments']}")
    print(f"Heroes with verified payment:   {import_report['heroes_with_payment']}")
    print(f"Heroes without payment:         {import_report['heroes_without_payment']}")
    print(f"Payments without hero:          {import_report['payments_without_hero']}")
    
    if import_report['duplicate_payments']:
        print(f"\n⚠️  Warning: {len(import_report['duplicate_payments'])} sponsors have duplicate payments")
    
    if import_report['unmatched_heroes']:
        print(f"\n⚠️  Heroes without matching payment:")
        for item in import_report['unmatched_heroes'][:10]:  # Show first 10
            print(f"   - {item['hero_name']} (Sponsor: {item['sponsor_name']}) - {item['reason']}")
        if len(import_report['unmatched_heroes']) > 10:
            print(f"   ... and {len(import_report['unmatched_heroes']) - 10} more")
    
    if import_report['unmatched_payments']:
        print(f"\n⚠️  Payments without matching hero:")
        for item in import_report['unmatched_payments'][:10]:  # Show first 10
            print(f"   - {item['sponsor_name']} (${item['amount']:.2f}) - Status: {item['status']}")
        if len(import_report['unmatched_payments']) > 10:
            print(f"   ... and {len(import_report['unmatched_payments']) - 10} more")
    
    print(f"\n{'='*60}")
    print("UPDATING DATABASE")
    print(f"{'='*60}\n")
    
    # Process each hero - ALL heroes are imported regardless of payment status
    updated_count = 0
    for hero in heroes:
        print(f"Processing: {hero.name}")
        
        # Get or create banner record
        banner = db.get_or_create_banner(hero.name, hero.sponsor_name or "Unknown")
        
        # Update hero information completeness
        is_complete, missing = hero.is_complete()
        banner.info_complete = is_complete
        banner.sponsor_email = hero.sponsor_email
        
        if not is_complete:
            print(f"  ⚠️  Missing fields: {', '.join(missing)}")
        else:
            print(f"  ✓ Hero information complete")
        
        # Check payment status
        payment_verified, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
        banner.payment_verified = payment_verified
        
        if payment_verified:
            print(f"  ✓ Payment verified: ${payment_info.amount_paid:.2f}")
        else:
            print(f"  ⚠️  Payment not found")
        
        # Update database
        db.update_banner(banner)
        updated_count += 1
        print(f"  Status: {banner.get_status()}\n")
    
    print(f"{'='*60}")
    print(f"Import complete! Updated {updated_count} banner records.")
    print(f"All {len(heroes)} heroes have been imported into the database.")
    print(f"{'='*60}\n")


def list_banners(db: BannerDatabase, status_filter: str = None):
    """List all banners with optional status filter."""
    print(f"\n{'='*60}")
    print("BANNER STATUS REPORT")
    print(f"{'='*60}\n")
    
    if status_filter:
        banners = db.get_banners_by_status(status_filter)
        print(f"Filtering by status: {status_filter}")
    else:
        banners = db.get_all_banners()
        print("Showing all banners")
    
    print(f"Total: {len(banners)} banners\n")
    
    if not banners:
        print("No banners found.")
        return
    
    # Group by status
    status_groups = {}
    for banner in banners:
        status = banner.get_status()
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(banner)
    
    # Display by status
    for status, group in sorted(status_groups.items()):
        print(f"\n{status} ({len(group)}):")
        print("-" * 60)
        for banner in group:
            print(f"  • {banner.hero_name} (Sponsor: {banner.sponsor_name})")
            if banner.pole_location:
                print(f"    Pole: {banner.pole_location}")
            if banner.notes:
                print(f"    Notes: {banner.notes}")
    
    print(f"\n{'='*60}\n")


def send_notifications(db: BannerDatabase, status: str):
    """Send notifications for banners with specific status."""
    print(f"\n{'='*60}")
    print("GENERATING NOTIFICATIONS")
    print(f"{'='*60}\n")
    
    banners = db.get_banners_by_status(status)
    print(f"Found {len(banners)} banners with status matching: {status}\n")
    
    notifier = NotificationService()
    
    for banner in banners:
        if banner.payment_verified and banner.info_complete and not banner.proof_sent:
            message = notifier.generate_proof_ready_notification(banner)
            notifier.save_notification(message)
            print(f"✓ Notification saved for {banner.hero_name}")
            
            # Mark as proof sent
            banner.proof_sent = True
            db.update_banner(banner)
    
    print(f"\nNotifications saved to: notifications.txt")
    print(f"{'='*60}\n")


def update_banner(db: BannerDatabase, hero_name: str, field: str, value: str):
    """Update a specific field for a banner."""
    # Find banner
    banners = db.get_all_banners()
    matching = [b for b in banners if hero_name.lower() in b.hero_name.lower()]
    
    if not matching:
        print(f"Error: No banner found matching '{hero_name}'")
        return
    
    if len(matching) > 1:
        print(f"Error: Multiple banners match '{hero_name}'. Please be more specific.")
        for b in matching:
            print(f"  - {b.hero_name} (Sponsor: {b.sponsor_name})")
        return
    
    banner = matching[0]
    print(f"\nUpdating banner for: {banner.hero_name}")
    
    # Update field
    if field == 'pole_location':
        banner.pole_location = value
        print(f"✓ Pole location set to: {value}")
    elif field == 'notes':
        banner.notes = value
        print(f"✓ Notes updated: {value}")
    elif field == 'documents_verified':
        banner.documents_verified = value.lower() in ['true', 'yes', '1']
        print(f"✓ Documents verified: {banner.documents_verified}")
    elif field == 'photo_verified':
        banner.photo_verified = value.lower() in ['true', 'yes', '1']
        print(f"✓ Photo verified: {banner.photo_verified}")
    elif field == 'proof_approved':
        banner.proof_approved = value.lower() in ['true', 'yes', '1']
        print(f"✓ Proof approved: {banner.proof_approved}")
    elif field == 'print_approved':
        banner.print_approved = value.lower() in ['true', 'yes', '1']
        print(f"✓ Print approved: {banner.print_approved}")
    elif field == 'submitted_to_printer':
        banner.submitted_to_printer = value.lower() in ['true', 'yes', '1']
        print(f"✓ Submitted to printer: {banner.submitted_to_printer}")
    elif field == 'thank_you_sent':
        banner.thank_you_sent = value.lower() in ['true', 'yes', '1']
        print(f"✓ Thank you sent: {banner.thank_you_sent}")
    else:
        print(f"Error: Unknown field '{field}'")
        print("Available fields: pole_location, notes, documents_verified, photo_verified,")
        print("                  proof_approved, print_approved, submitted_to_printer, thank_you_sent")
        return
    
    db.update_banner(banner)
    print(f"Status: {banner.get_status()}\n")


def show_summary(db: BannerDatabase):
    """Show summary statistics."""
    banners = db.get_all_banners()
    
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}\n")
    
    print(f"Total Banners: {len(banners)}\n")
    
    # Count by status
    status_counts = {}
    for banner in banners:
        status = banner.get_status()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("Status Breakdown:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    
    print(f"\n{'='*60}\n")


def email_setup(config_file: str = None):
    """Setup M365 email configuration."""
    if not EMAIL_AVAILABLE:
        print("✗ Email functionality not available.")
        print("  Install with: pip install O365")
        return
    
    if config_file is None:
        config_file = config.get_m365_config_path()
    
    print(f"\n{'='*60}")
    print("M365 EMAIL SETUP")
    print(f"{'='*60}\n")
    
    create_m365_config_template(config_file)


def email_send(db: BannerDatabase, config_file: str = None):
    """Create draft emails for proof ready notifications."""
    if not EMAIL_AVAILABLE:
        print("✗ Email functionality not available.")
        print("  Install with: pip install O365")
        return
    
    if config_file is None:
        config_file = config.get_m365_config_path()
    
    print(f"\n{'='*60}")
    print("CREATING DRAFT EMAILS FOR PROOF READY NOTIFICATIONS")
    print(f"{'='*60}\n")
    
    # Load config
    config = load_m365_config(config_file)
    if not config:
        print(f"✗ Configuration file not found: {config_file}")
        print(f"  Run 'python banner_manager.py email-setup' to create it")
        return
    
    # Validate config
    if config.get('client_id') == 'YOUR_AZURE_AD_CLIENT_ID':
        print("✗ Configuration file not updated with real credentials")
        print(f"  Please edit {config_file} with your Azure AD app credentials")
        return
    
    # Initialize email service
    try:
        email_service = M365EmailService(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            tenant_id=config.get('tenant_id')
        )
    except Exception as e:
        print(f"✗ Error initializing email service: {e}")
        return
    
    # Authenticate
    if not email_service.authenticate():
        print("✗ Failed to authenticate with Microsoft 365")
        print("  Please check your credentials in the config file")
        return
    
    # Get banners ready for notification
    banners = db.get_all_banners()
    ready_banners = [b for b in banners 
                    if b.payment_verified and b.info_complete and not b.proof_sent]
    
    if not ready_banners:
        print("No banners ready for notification")
        return
    
    print(f"Found {len(ready_banners)} banners ready for notification\n")
    
    # Create draft emails
    stats = email_service.send_bulk_notifications(ready_banners, db)
    
    print(f"\n{'='*60}")
    print(f"Draft emails created: {stats['created']}")
    print(f"Failed: {stats['failed']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"\n{'='*60}")
    print(f"✓ Drafts are now in your Drafts folder.")
    print(f"  Review and send them from Outlook when ready.")
    print(f"{'='*60}\n")


def email_check(db: BannerDatabase, config_file: str = None, days: int = 7):
    """Check for approval responses in email."""
    if not EMAIL_AVAILABLE:
        print("✗ Email functionality not available.")
        print("  Install with: pip install O365")
        return
    
    if config_file is None:
        config_file = config.get_m365_config_path()
    
    print(f"\n{'='*60}")
    print("CHECKING EMAIL FOR APPROVALS")
    print(f"{'='*60}\n")
    
    # Load config
    m365_config = load_m365_config(config_file)
    if not m365_config:
        print(f"✗ Configuration file not found: {config_file}")
        print(f"  Run 'python banner_manager.py email-setup' to create it")
        return
    
    # Validate config
    if m365_config.get('client_id') == 'YOUR_AZURE_AD_CLIENT_ID':
        print("✗ Configuration file not updated with real credentials")
        print(f"  Please edit {config_file} with your Azure AD app credentials")
        return
    
    # Initialize email service
    try:
        email_service = M365EmailService(
            client_id=m365_config['client_id'],
            client_secret=m365_config['client_secret'],
            tenant_id=m365_config.get('tenant_id')
        )
    except Exception as e:
        print(f"✗ Error initializing email service: {e}")
        return
    
    # Authenticate
    if not email_service.authenticate():
        print("✗ Failed to authenticate with Microsoft 365")
        return
    
    print(f"Checking inbox for emails from last {days} days...\n")
    
    # Check for approvals
    results = email_service.check_approval_responses(db, days_back=days)
    
    if results:
        print(f"\n{'='*60}")
        print(f"Processed {len(results)} approval responses:")
        for result in results:
            status = "✓ Approved" if result['approved'] else "⚠ Needs attention"
            print(f"  {status}: {result['hero_name']} ({result['sponsor_email']})")
        print(f"{'='*60}\n")
    else:
        print("No approval responses found")
        print(f"{'='*60}\n")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Hometown Hero Banner Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import CSV files from Wix
  python banner_manager.py import --hero heroes.csv --payment payments.csv
  
  # List all banners
  python banner_manager.py list
  
  # List banners by status
  python banner_manager.py list --status "ready for proof"
  
  # Send notifications for ready proofs
  python banner_manager.py notify --status "ready for proof"
  
  # Update pole location
  python banner_manager.py update "John Smith" pole_location "Main St & 1st Ave"
  
  # Add notes
  python banner_manager.py update "John Smith" notes "Family requested specific location"
  
  # Verify documents quality
  python banner_manager.py update "John Smith" documents_verified yes
  
  # Verify photo meets requirements
  python banner_manager.py update "John Smith" photo_verified yes
  
  # Approve proof
  python banner_manager.py update "John Smith" proof_approved yes
  
  # Approve for printing
  python banner_manager.py update "John Smith" print_approved yes
  
  # Mark as submitted to printer
  python banner_manager.py update "John Smith" submitted_to_printer yes
  
  # Mark thank you sent
  python banner_manager.py update "John Smith" thank_you_sent yes
  
  # Show summary
  python banner_manager.py summary
  
  # Email automation (requires M365 setup)
  python banner_manager.py email-setup
  python banner_manager.py email-send
  python banner_manager.py email-check --days 7
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import CSV files from Wix')
    import_parser.add_argument('--hero', required=True, help='Path to hero information CSV')
    import_parser.add_argument('--payment', required=True, help='Path to payment CSV')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List banners')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Notify command
    notify_parser = subparsers.add_parser('notify', help='Send notifications')
    notify_parser.add_argument('--status', required=True, help='Status to notify')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update banner field')
    update_parser.add_argument('hero_name', help='Hero name to update')
    update_parser.add_argument('field', help='Field to update (pole_location, notes, documents_verified, photo_verified, proof_approved, print_approved, submitted_to_printer, thank_you_sent)')
    update_parser.add_argument('value', help='New value')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show summary statistics')
    
    # Email commands
    if EMAIL_AVAILABLE:
        email_setup_parser = subparsers.add_parser('email-setup', help='Setup M365 email configuration')
        email_setup_parser.add_argument('--config', default=None, help='Path to M365 config file (default: from HH_M365_CONFIG or ./m365_config.json)')
        
        email_send_parser = subparsers.add_parser('email-send', help='Create draft emails in M365 Drafts folder for manual sending')
        email_send_parser.add_argument('--config', default=None, help='Path to M365 config file (default: from HH_M365_CONFIG or ./m365_config.json)')
        
        email_check_parser = subparsers.add_parser('email-check', help='Check inbox for approval responses')
        email_check_parser.add_argument('--config', default=None, help='Path to M365 config file (default: from HH_M365_CONFIG or ./m365_config.json)')
        email_check_parser.add_argument('--days', type=int, default=7, help='Days to look back for emails')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize database
    db = BannerDatabase()
    
    # Execute command
    if args.command == 'import':
        import_csvs(args.hero, args.payment, db)
    elif args.command == 'list':
        list_banners(db, args.status)
    elif args.command == 'notify':
        send_notifications(db, args.status)
    elif args.command == 'update':
        update_banner(db, args.hero_name, args.field, args.value)
    elif args.command == 'summary':
        show_summary(db)
    elif args.command == 'email-setup':
        email_setup(args.config if hasattr(args, 'config') else None)
    elif args.command == 'email-send':
        email_send(db, args.config)
    elif args.command == 'email-check':
        email_check(db, args.config, args.days)


if __name__ == '__main__':
    main()
