"""CSV processing module for importing Wix data."""

import re
import pandas as pd
from datetime import datetime
from typing import List, Tuple
from models import HeroInfo, PaymentInfo


class CSVProcessor:
    """Processes CSV files from Wix."""
    
    @staticmethod
    def parse_hero_csv(csv_path: str) -> List[HeroInfo]:
        """
        Parse the CMS CSV file with hero information.
        This handles the specific Wix CMS format with columns like:
        Status, Name of Buyer, Service Name, Branch, Rank, etc.
        """
        try:
            df = pd.read_csv(csv_path)
            heroes = []
            
            # Map exact Wix column names
            for _, row in df.iterrows():
                # Only process PUBLISHED entries (skip DRAFT)
                status = str(row.get('Status', '')).strip().upper()
                if status != 'PUBLISHED':
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
            
            return heroes
        
        except Exception as e:
            print(f"Error parsing hero CSV: {e}")
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
            payments = []
            
            for _, row in df.iterrows():
                # Extract payer name from "Your Name" column
                payer_name = str(row.get('Your Name', '')).strip()
                
                # Clean up payer name - remove anything in parentheses (like "For wife...")
                if '(' in payer_name:
                    payer_name = payer_name[:payer_name.index('(')].strip()
                
                if not payer_name or payer_name == 'nan':
                    continue
                
                # Check payment status
                status = str(row.get('Status', '')).strip().upper()
                is_confirmed = status == 'CONFIRMED'
                
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
            
            return payments
        
        except Exception as e:
            print(f"Error parsing payment CSV: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def match_hero_to_payment(hero: HeroInfo, payments: List[PaymentInfo]) -> Tuple[bool, PaymentInfo]:
        """Match a hero record to a payment record by sponsor name."""
        if not hero.sponsor_name:
            return False, None
        
        for payment in payments:
            # Normalize names for comparison
            hero_sponsor = hero.sponsor_name.lower().strip()
            payment_sponsor = payment.sponsor_name.lower().strip()
            
            if hero_sponsor == payment_sponsor:
                return payment.is_paid(), payment
        
        return False, None
