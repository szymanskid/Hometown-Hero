"""CSV processing module for importing Wix data."""

import re
import pandas as pd
from datetime import datetime
from typing import List, Tuple, Dict, Any
from models import HeroInfo, PaymentInfo
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVProcessor:
    """Processes CSV files from Wix."""
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a name for matching purposes.
        - Trim whitespace
        - Convert to uppercase
        - Collapse multiple spaces to single space
        - Remove common punctuation that might differ
        """
        if not name or name == 'nan':
            return ""
        
        # Convert to string and strip
        name = str(name).strip()
        
        # Convert to uppercase for case-insensitive matching
        name = name.upper()
        
        # Collapse multiple spaces
        name = re.sub(r'\s+', ' ', name)
        
        # Remove trailing/leading punctuation that might differ
        name = name.strip('.,;')
        
        return name
    
    @staticmethod
    def parse_hero_csv(csv_path: str) -> List[HeroInfo]:
        """
        Parse the CMS CSV file with hero information.
        This handles the specific Wix CMS format with columns like:
        Status, Name of Buyer, Service Name, Branch, Rank, etc.
        """
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Hero CSV: Read {len(df)} total rows")
            
            heroes = []
            skipped_draft = 0
            skipped_no_name = 0
            
            # Map exact Wix column names
            for idx, row in df.iterrows():
                # Only process PUBLISHED entries (skip DRAFT)
                status = str(row.get('Status', '')).strip().upper()
                if status != 'PUBLISHED':
                    skipped_draft += 1
                    continue
                
                # Extract hero information from Wix columns
                hero_name = str(row.get('Service Name', '')).strip()
                sponsor_name = str(row.get('Name of Buyer', '')).strip()
                sponsor_email = str(row.get('Email', '')).strip()
                sponsor_phone = str(row.get('Phone', '')).strip()
                service_branch = str(row.get('Branch', '')).strip()
                rank = str(row.get('Rank', '')).strip()
                service_details = str(row.get('Service Details', '')).strip()
                image = str(row.get('Image', '')).strip()
                
                # Check if we have minimum required data
                if not hero_name or hero_name == 'nan':
                    skipped_no_name += 1
                    logger.warning(f"Hero CSV row {idx}: Skipping - no service name")
                    continue
                
                hero = HeroInfo(
                    name=hero_name,
                    service_branch=service_branch if service_branch and service_branch != 'nan' else None,
                    rank=rank if rank and rank != 'nan' else None,
                    years_served=service_details if service_details and service_details != 'nan' else None,
                    hometown=None,  # Not in Wix format
                    photo_path=image if image and image != 'nan' and image.startswith('wix:') else None,
                    sponsor_name=sponsor_name if sponsor_name and sponsor_name != 'nan' else None,
                    sponsor_email=sponsor_email if sponsor_email and sponsor_email != 'nan' else None,
                    sponsor_phone=sponsor_phone if sponsor_phone and sponsor_phone != 'nan' else None
                )
                heroes.append(hero)
            
            logger.info(f"Hero CSV: Parsed {len(heroes)} PUBLISHED heroes")
            logger.info(f"Hero CSV: Skipped {skipped_draft} DRAFT entries")
            logger.info(f"Hero CSV: Skipped {skipped_no_name} entries with no hero name")
            
            return heroes
        
        except Exception as e:
            logger.error(f"Error parsing hero CSV: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def parse_payment_csv(csv_path: str) -> List[PaymentInfo]:
        """
        Parse the payment CSV file.
        This handles the specific Wix payment format with columns like:
        Your Name, Status, One Banner, Created date, etc.
        """
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Payment CSV: Read {len(df)} total rows")
            
            payments = []
            skipped_no_name = 0
            confirmed_count = 0
            pending_count = 0
            
            for idx, row in df.iterrows():
                # Extract payer name from "Your Name" column
                payer_name = str(row.get('Your Name', '')).strip()
                
                # Clean up payer name - remove anything in parentheses (like "For wife...")
                if '(' in payer_name:
                    payer_name = payer_name[:payer_name.index('(')].strip()
                
                if not payer_name or payer_name == 'nan':
                    skipped_no_name += 1
                    logger.warning(f"Payment CSV row {idx}: Skipping - no payer name")
                    continue
                
                # Check payment status
                status = str(row.get('Status', '')).strip().upper()
                is_confirmed = status == 'CONFIRMED'
                
                if is_confirmed:
                    confirmed_count += 1
                else:
                    pending_count += 1
                
                # Parse amount from "One Banner" column
                # Format is like: [["One Banner","$95"]]
                amount_paid = 0.0
                one_banner = str(row.get('One Banner', '')).strip()
                if one_banner and one_banner != 'nan':
                    # Extract dollar amount using simple string parsing
                    match = re.search(r'\$(\d+(?:\.\d{2})?)', one_banner)
                    if match:
                        try:
                            amount_paid = float(match.group(1))
                        except (ValueError, TypeError):
                            pass
                
                # Only consider it paid if status is CONFIRMED and amount > 0
                if not is_confirmed:
                    amount_paid = 0.0
                
                # Parse date
                payment_date = None
                date_str = str(row.get('Created date', '')).strip()
                if date_str and date_str != 'nan':
                    try:
                        payment_date = pd.to_datetime(date_str).to_pydatetime()
                    except (ValueError, TypeError, pd.errors.ParserError):
                        pass
                
                payment = PaymentInfo(
                    sponsor_name=payer_name,
                    amount_paid=amount_paid,
                    payment_date=payment_date,
                    payment_method=status if is_confirmed else None,
                    transaction_id=str(row.get('Id', '')).strip() if 'Id' in row else None
                )
                payments.append(payment)
            
            logger.info(f"Payment CSV: Parsed {len(payments)} payment records")
            logger.info(f"Payment CSV: {confirmed_count} CONFIRMED, {pending_count} pending")
            logger.info(f"Payment CSV: Skipped {skipped_no_name} entries with no payer name")
            
            return payments
        
        except Exception as e:
            logger.error(f"Error parsing payment CSV: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def match_hero_to_payment(hero: HeroInfo, payments: List[PaymentInfo]) -> Tuple[bool, PaymentInfo]:
        """Match a hero record to a payment record by sponsor name."""
        if not hero.sponsor_name:
            return False, None
        
        # Normalize the hero sponsor name
        hero_sponsor_normalized = CSVProcessor.normalize_name(hero.sponsor_name)
        
        # Try to find a matching payment
        for payment in payments:
            # Normalize the payment sponsor name
            payment_sponsor_normalized = CSVProcessor.normalize_name(payment.sponsor_name)
            
            if hero_sponsor_normalized == payment_sponsor_normalized:
                return payment.is_paid(), payment
        
        return False, None
    
    @staticmethod
    def generate_import_report(heroes: List[HeroInfo], payments: List[PaymentInfo]) -> Dict[str, Any]:
        """
        Generate a comprehensive import report showing match statistics.
        
        Returns a dictionary with:
        - total_heroes: count of heroes
        - total_payments: count of payments
        - heroes_with_payment: count of heroes with matching payment
        - heroes_without_payment: count of heroes without matching payment
        - payments_without_hero: count of payments without matching hero
        - unmatched_heroes: list of hero names without payment
        - unmatched_payments: list of payment sponsor names without hero
        - duplicate_payments: list of sponsors with multiple payments
        """
        report = {
            'total_heroes': len(heroes),
            'total_payments': len(payments),
            'heroes_with_payment': 0,
            'heroes_without_payment': 0,
            'payments_without_hero': 0,
            'unmatched_heroes': [],
            'unmatched_payments': [],
            'duplicate_payments': []
        }
        
        # Create normalized lookup for payments
        payment_lookup = {}
        for payment in payments:
            normalized_name = CSVProcessor.normalize_name(payment.sponsor_name)
            if normalized_name:
                if normalized_name in payment_lookup:
                    # Track duplicates
                    if normalized_name not in report['duplicate_payments']:
                        report['duplicate_payments'].append(payment.sponsor_name)
                else:
                    payment_lookup[normalized_name] = payment
        
        # Check each hero for payment match
        matched_payment_names = set()
        for hero in heroes:
            if not hero.sponsor_name:
                report['heroes_without_payment'] += 1
                report['unmatched_heroes'].append({
                    'hero_name': hero.name,
                    'sponsor_name': 'N/A',
                    'reason': 'No sponsor name in hero record'
                })
                continue
            
            hero_sponsor_normalized = CSVProcessor.normalize_name(hero.sponsor_name)
            
            if hero_sponsor_normalized in payment_lookup:
                payment = payment_lookup[hero_sponsor_normalized]
                if payment.is_paid():
                    report['heroes_with_payment'] += 1
                    matched_payment_names.add(hero_sponsor_normalized)
                else:
                    report['heroes_without_payment'] += 1
                    report['unmatched_heroes'].append({
                        'hero_name': hero.name,
                        'sponsor_name': hero.sponsor_name,
                        'reason': 'Payment not confirmed (status not CONFIRMED or amount is $0)'
                    })
            else:
                report['heroes_without_payment'] += 1
                report['unmatched_heroes'].append({
                    'hero_name': hero.name,
                    'sponsor_name': hero.sponsor_name,
                    'reason': 'No matching payment record found'
                })
        
        # Find payments without matching heroes
        for payment in payments:
            normalized_name = CSVProcessor.normalize_name(payment.sponsor_name)
            if normalized_name and normalized_name not in matched_payment_names:
                report['payments_without_hero'] += 1
                report['unmatched_payments'].append({
                    'sponsor_name': payment.sponsor_name,
                    'amount': payment.amount_paid,
                    'status': payment.payment_method or 'PENDING'
                })
        
        return report
