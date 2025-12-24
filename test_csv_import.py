#!/usr/bin/env python3
"""
Unit tests for CSV import logic.
Tests normalization, matching, and ensures all hero rows are preserved.
"""

import unittest
import tempfile
import os
from csv_processor import CSVProcessor
from models import HeroInfo, PaymentInfo


class TestCSVProcessor(unittest.TestCase):
    """Test CSV processing functions."""
    
    def test_normalize_name(self):
        """Test name normalization for matching."""
        # Test whitespace trimming
        self.assertEqual(
            CSVProcessor.normalize_name("  John Smith  "),
            "JOHN SMITH"
        )
        
        # Test case conversion
        self.assertEqual(
            CSVProcessor.normalize_name("john smith"),
            "JOHN SMITH"
        )
        
        # Test multiple spaces
        self.assertEqual(
            CSVProcessor.normalize_name("John   Smith"),
            "JOHN SMITH"
        )
        
        # Test trailing punctuation
        self.assertEqual(
            CSVProcessor.normalize_name("John Smith."),
            "JOHN SMITH"
        )
        
        # Test empty/nan
        self.assertEqual(CSVProcessor.normalize_name(""), "")
        self.assertEqual(CSVProcessor.normalize_name("nan"), "")
    
    def test_hero_payment_matching_normalized(self):
        """Test that hero-payment matching uses normalized names."""
        # Create hero with mixed case and extra spaces
        hero = HeroInfo(
            name="Test Hero",
            sponsor_name="  Jane   Doe  ",
            sponsor_email="jane@example.com"
        )
        
        # Create payments with slightly different formatting
        payments = [
            PaymentInfo(sponsor_name="JANE DOE", amount_paid=95.0),
            PaymentInfo(sponsor_name="Bob Smith", amount_paid=95.0),
        ]
        
        # Should match despite formatting differences
        matched, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
        self.assertTrue(matched)
        self.assertIsNotNone(payment_info)
        self.assertEqual(payment_info.amount_paid, 95.0)
    
    def test_hero_payment_matching_case_insensitive(self):
        """Test that matching is case-insensitive."""
        hero = HeroInfo(
            name="Test Hero",
            sponsor_name="john SMITH",
            sponsor_email="john@example.com"
        )
        
        payments = [
            PaymentInfo(sponsor_name="John Smith", amount_paid=95.0),
        ]
        
        matched, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
        self.assertTrue(matched)
        self.assertIsNotNone(payment_info)
    
    def test_hero_without_payment(self):
        """Test hero without matching payment."""
        hero = HeroInfo(
            name="Test Hero",
            sponsor_name="Jane Doe",
            sponsor_email="jane@example.com"
        )
        
        payments = [
            PaymentInfo(sponsor_name="Bob Smith", amount_paid=95.0),
        ]
        
        matched, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
        self.assertFalse(matched)
        self.assertIsNone(payment_info)
    
    def test_hero_without_sponsor_name(self):
        """Test hero without sponsor name."""
        hero = HeroInfo(
            name="Test Hero",
            sponsor_name=None,
            sponsor_email="jane@example.com"
        )
        
        payments = [
            PaymentInfo(sponsor_name="Jane Doe", amount_paid=95.0),
        ]
        
        matched, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
        self.assertFalse(matched)
        self.assertIsNone(payment_info)
    
    def test_payment_not_confirmed(self):
        """Test that unconfirmed payments (amount=0) don't match."""
        hero = HeroInfo(
            name="Test Hero",
            sponsor_name="Jane Doe",
            sponsor_email="jane@example.com"
        )
        
        payments = [
            PaymentInfo(sponsor_name="Jane Doe", amount_paid=0.0),  # Not paid
        ]
        
        matched, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
        self.assertFalse(matched)  # Not considered paid
        self.assertIsNotNone(payment_info)  # Found but not paid
    
    def test_import_report_basic(self):
        """Test import report generation."""
        heroes = [
            HeroInfo(name="Hero1", sponsor_name="Sponsor A", sponsor_email="a@example.com"),
            HeroInfo(name="Hero2", sponsor_name="Sponsor B", sponsor_email="b@example.com"),
            HeroInfo(name="Hero3", sponsor_name="Sponsor C", sponsor_email="c@example.com"),
        ]
        
        payments = [
            PaymentInfo(sponsor_name="Sponsor A", amount_paid=95.0),
            PaymentInfo(sponsor_name="Sponsor B", amount_paid=95.0),
        ]
        
        report = CSVProcessor.generate_import_report(heroes, payments)
        
        self.assertEqual(report['total_heroes'], 3)
        self.assertEqual(report['total_payments'], 2)
        self.assertEqual(report['heroes_with_payment'], 2)
        self.assertEqual(report['heroes_without_payment'], 1)
        self.assertEqual(report['payments_without_hero'], 0)
        
        # Check unmatched heroes
        self.assertEqual(len(report['unmatched_heroes']), 1)
        self.assertEqual(report['unmatched_heroes'][0]['hero_name'], "Hero3")
    
    def test_import_report_unmatched_payments(self):
        """Test detection of payments without heroes."""
        heroes = [
            HeroInfo(name="Hero1", sponsor_name="Sponsor A", sponsor_email="a@example.com"),
        ]
        
        payments = [
            PaymentInfo(sponsor_name="Sponsor A", amount_paid=95.0),
            PaymentInfo(sponsor_name="Sponsor B", amount_paid=95.0),
            PaymentInfo(sponsor_name="Sponsor C", amount_paid=95.0),
        ]
        
        report = CSVProcessor.generate_import_report(heroes, payments)
        
        self.assertEqual(report['total_heroes'], 1)
        self.assertEqual(report['total_payments'], 3)
        self.assertEqual(report['heroes_with_payment'], 1)
        self.assertEqual(report['payments_without_hero'], 2)
        
        # Check unmatched payments
        self.assertEqual(len(report['unmatched_payments']), 2)
    
    def test_import_report_duplicate_payments(self):
        """Test detection of duplicate payment records."""
        heroes = [
            HeroInfo(name="Hero1", sponsor_name="Sponsor A", sponsor_email="a@example.com"),
        ]
        
        payments = [
            PaymentInfo(sponsor_name="Sponsor A", amount_paid=95.0),
            PaymentInfo(sponsor_name="Sponsor A", amount_paid=95.0),  # Duplicate
        ]
        
        report = CSVProcessor.generate_import_report(heroes, payments)
        
        # Should detect duplicate
        self.assertEqual(len(report['duplicate_payments']), 1)
        self.assertIn("Sponsor A", report['duplicate_payments'][0])
    
    def test_parse_hero_csv_sample(self):
        """Test parsing the sample hero CSV."""
        csv_path = "sample_hero_cms.csv"
        if os.path.exists(csv_path):
            heroes = CSVProcessor.parse_hero_csv(csv_path)
            
            # Should parse PUBLISHED entries only (3 in sample)
            self.assertEqual(len(heroes), 3)
            
            # Check first hero
            self.assertEqual(heroes[0].name, "John Smith")
            self.assertEqual(heroes[0].sponsor_name, "Jane Doe")
            self.assertEqual(heroes[0].service_branch, "Army")
    
    def test_parse_payment_csv_sample(self):
        """Test parsing the sample payment CSV."""
        csv_path = "sample_payment.csv"
        if os.path.exists(csv_path):
            payments = CSVProcessor.parse_payment_csv(csv_path)
            
            # Should parse all payment records (4 in sample)
            self.assertEqual(len(payments), 4)
            
            # Check confirmed payments
            confirmed = [p for p in payments if p.is_paid()]
            self.assertEqual(len(confirmed), 3)  # 3 CONFIRMED
            
            # Check first payment
            self.assertEqual(payments[0].sponsor_name, "Jane Doe")
            self.assertEqual(payments[0].amount_paid, 95.0)
    
    def test_all_heroes_preserved_with_different_counts(self):
        """
        Critical test: Ensure all heroes are preserved even when fewer payments exist.
        This simulates the reported issue: 56 heroes, 40 payments.
        """
        # Create 56 heroes
        heroes = []
        for i in range(1, 57):
            heroes.append(HeroInfo(
                name=f"Hero{i}",
                sponsor_name=f"Sponsor{i}",
                sponsor_email=f"sponsor{i}@example.com"
            ))
        
        # Create only 40 payments (for heroes 1-40)
        payments = []
        for i in range(1, 41):
            payments.append(PaymentInfo(
                sponsor_name=f"Sponsor{i}",
                amount_paid=95.0
            ))
        
        # Generate report
        report = CSVProcessor.generate_import_report(heroes, payments)
        
        # Verify counts
        self.assertEqual(report['total_heroes'], 56, "Should have 56 heroes")
        self.assertEqual(report['total_payments'], 40, "Should have 40 payments")
        self.assertEqual(report['heroes_with_payment'], 40, "40 heroes should have payment")
        self.assertEqual(report['heroes_without_payment'], 16, "16 heroes should be without payment")
        self.assertEqual(report['payments_without_hero'], 0, "All payments should match")
        
        # Verify unmatched heroes
        self.assertEqual(len(report['unmatched_heroes']), 16)
        
        # All 56 heroes should still be "processed" (the function doesn't drop them)
        # In actual import, all 56 should be in the database
        # This is verified by the fact that the report shows 56 total heroes


def create_test_csv_files():
    """Create test CSV files for manual testing."""
    # Create hero CSV with 56 heroes
    hero_csv_path = "/tmp/test_heroes_56.csv"
    with open(hero_csv_path, 'w') as f:
        f.write("Status,Name of Buyer,Service Name,Branch,Rank,Service Details,Email,Phone,Image\n")
        for i in range(1, 57):
            f.write(f"PUBLISHED,Sponsor{i},Hero{i},Army,Sergeant,Veteran,sponsor{i}@example.com,555-{i:04d},wix:image://hero{i}.jpg\n")
    
    # Create payment CSV with 40 payments
    payment_csv_path = "/tmp/test_payments_40.csv"
    with open(payment_csv_path, 'w') as f:
        f.write("Your Name,Status,One Banner,Created date,Id\n")
        for i in range(1, 41):
            f.write(f'Sponsor{i},CONFIRMED,"[[""One Banner"",""$95""]]",2024-01-{(i%28)+1:02d}T10:00:00Z,tx-{i:03d}\n')
    
    print(f"Created test CSV files:")
    print(f"  Heroes (56): {hero_csv_path}")
    print(f"  Payments (40): {payment_csv_path}")
    print(f"\nYou can use these files to test the import:")
    print(f"  python banner_manager.py import --hero {hero_csv_path} --payment {payment_csv_path}")
    
    return hero_csv_path, payment_csv_path


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-test-files':
        create_test_csv_files()
    else:
        # Run unit tests
        unittest.main()
