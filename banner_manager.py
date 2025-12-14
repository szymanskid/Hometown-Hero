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
    
    # Process each hero
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
    elif field == 'proof_approved':
        banner.proof_approved = value.lower() in ['true', 'yes', '1']
        print(f"✓ Proof approved: {banner.proof_approved}")
    elif field == 'print_approved':
        banner.print_approved = value.lower() in ['true', 'yes', '1']
        print(f"✓ Print approved: {banner.print_approved}")
    else:
        print(f"Error: Unknown field '{field}'")
        print("Available fields: pole_location, notes, proof_approved, print_approved")
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
  
  # Approve proof
  python banner_manager.py update "John Smith" proof_approved yes
  
  # Approve for printing
  python banner_manager.py update "John Smith" print_approved yes
  
  # Show summary
  python banner_manager.py summary
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
    update_parser.add_argument('field', help='Field to update (pole_location, notes, proof_approved, print_approved)')
    update_parser.add_argument('value', help='New value')
    
    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show summary statistics')
    
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


if __name__ == '__main__':
    main()
