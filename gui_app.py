#!/usr/bin/env python3
"""
Hometown Hero Banner Management System - GUI Application
A web-based graphical interface built with Streamlit for managing the banner verification process.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import os
import tempfile

from models import BannerRecord
from database import BannerDatabase
from csv_processor import CSVProcessor
from notifications import NotificationService

# Optional M365 email support
try:
    from email_service import M365EmailService, load_m365_config, create_m365_config_template
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False


# Page configuration
st.set_page_config(
    page_title="Hometown Hero Banner Management",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .metric-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


def init_database():
    """Initialize database connection."""
    if 'db' not in st.session_state:
        st.session_state.db = BannerDatabase()
    return st.session_state.db


def show_dashboard():
    """Display the main dashboard with statistics."""
    st.markdown('<div class="main-header">🎖️ Hometown Hero Banner Management</div>', unsafe_allow_html=True)
    
    db = init_database()
    banners = db.get_all_banners()
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Banners", len(banners))
    
    with col2:
        paid_count = sum(1 for b in banners if b.payment_verified)
        st.metric("Paid", paid_count)
    
    with col3:
        ready_count = sum(1 for b in banners if b.photo_verified and b.documents_verified and not b.proof_sent)
        st.metric("Ready to Send", ready_count)
    
    with col4:
        approved_count = sum(1 for b in banners if b.print_approved)
        st.metric("Approved for Print", approved_count)
    
    st.divider()
    
    # Status breakdown
    st.subheader("📊 Status Breakdown")
    
    status_counts = {}
    for banner in banners:
        status = banner.get_status()
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        # Create DataFrame for better display
        df_status = pd.DataFrame([
            {"Status": status, "Count": count}
            for status, count in sorted(status_counts.items(), key=lambda x: -x[1])
        ])
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(df_status, width='stretch', hide_index=True)
        with col2:
            st.bar_chart(df_status.set_index("Status"))
    else:
        st.info("No banners in the system yet. Import CSV files to get started.")


def show_import_csv():
    """Display CSV import interface."""
    st.header("📥 Import CSV Files")
    st.write("Upload hero information and payment CSV files from Wix to update the database.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hero_file = st.file_uploader("Hero Information CSV", type=['csv'], key='hero_csv')
    
    with col2:
        payment_file = st.file_uploader("Payment CSV", type=['csv'], key='payment_csv')
    
    if st.button("Import CSV Files", type="primary", disabled=(hero_file is None or payment_file is None)):
        if hero_file and payment_file:
            with st.spinner("Importing CSV files..."):
                # Create temporary files with context managers
                hero_temp = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
                payment_temp = tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False)
                
                try:
                    # Write uploaded files to temporary files
                    hero_temp.write(hero_file.getvalue())
                    hero_temp.close()
                    
                    payment_temp.write(payment_file.getvalue())
                    payment_temp.close()
                    
                    # Process CSV files
                    db = init_database()
                    
                    heroes = CSVProcessor.parse_hero_csv(hero_temp.name)
                    payments = CSVProcessor.parse_payment_csv(payment_temp.name)
                    
                    updated_count = 0
                    for hero in heroes:
                        banner = db.get_or_create_banner(hero.name, hero.sponsor_name or "Unknown")
                        
                        is_complete, missing = hero.is_complete()
                        banner.info_complete = is_complete
                        banner.sponsor_email = hero.sponsor_email
                        
                        payment_verified, payment_info = CSVProcessor.match_hero_to_payment(hero, payments)
                        banner.payment_verified = payment_verified
                        
                        db.update_banner(banner)
                        updated_count += 1
                    
                    st.success(f"✅ Successfully imported {len(heroes)} hero records and {len(payments)} payment records!")
                    st.info(f"Updated {updated_count} banner records in the database.")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error importing CSV files: {str(e)}")
                finally:
                    # Clean up temporary files
                    try:
                        os.unlink(hero_temp.name)
                    except:
                        pass
                    try:
                        os.unlink(payment_temp.name)
                    except:
                        pass


def show_banner_list():
    """Display list of all banners with filtering options."""
    st.header("📋 Banner List")
    
    db = init_database()
    banners = db.get_all_banners()
    
    if not banners:
        st.info("No banners found. Import CSV files to get started.")
        return
    
    # Filter options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get all unique statuses
        all_statuses = sorted(set(b.get_status() for b in banners))
        status_filter = st.selectbox("Filter by Status", ["All"] + all_statuses)
    
    with col2:
        search_term = st.text_input("Search by name", "")
    
    # Apply filters
    filtered_banners = banners
    if status_filter != "All":
        filtered_banners = [b for b in filtered_banners if b.get_status() == status_filter]
    
    if search_term:
        filtered_banners = [b for b in filtered_banners 
                           if search_term.lower() in b.hero_name.lower() 
                           or search_term.lower() in b.sponsor_name.lower()]
    
    st.write(f"Showing {len(filtered_banners)} of {len(banners)} banners")
    
    # Display banners
    for banner in filtered_banners:
        with st.expander(f"🎖️ {banner.hero_name} (Sponsor: {banner.sponsor_name})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Status:**", banner.get_status())
                st.write("**Info Complete:**", "✅" if banner.info_complete else "❌")
                st.write("**Payment Verified:**", "✅" if banner.payment_verified else "❌")
                st.write("**Documents Verified:**", "✅" if banner.documents_verified else "❌")
                st.write("**Photo Verified:**", "✅" if banner.photo_verified else "❌")
                st.write("**Sponsor Email:**", banner.sponsor_email or "N/A")
            
            with col2:
                st.write("**Proof Sent:**", "✅" if banner.proof_sent else "❌")
                st.write("**Proof Approved:**", "✅" if banner.proof_approved else "❌")
                st.write("**Print Approved:**", "✅" if banner.print_approved else "❌")
                st.write("**Submitted to Printer:**", "✅" if banner.submitted_to_printer else "❌")
                st.write("**Thank You Sent:**", "✅" if banner.thank_you_sent else "❌")
            
            if banner.pole_location:
                st.write("**📍 Pole Location:**", banner.pole_location)
            
            if banner.notes:
                st.write("**📝 Notes:**", banner.notes)
            
            if banner.updated_at:
                st.write("**Last Updated:**", banner.updated_at.strftime("%Y-%m-%d %H:%M"))


def show_update_banner():
    """Display interface for updating banner information."""
    st.header("✏️ Update Banner")
    
    db = init_database()
    banners = db.get_all_banners()
    
    if not banners:
        st.info("No banners found. Import CSV files to get started.")
        return
    
    # Select banner to update
    banner_names = [f"{b.hero_name} (Sponsor: {b.sponsor_name})" for b in banners]
    selected_name = st.selectbox("Select Banner", banner_names)
    
    if selected_name:
        # Find selected banner
        selected_banner = banners[banner_names.index(selected_name)]
        
        st.divider()
        st.subheader(f"Update: {selected_banner.hero_name}")
        
        # Create update form
        with st.form("update_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Verification Flags**")
                documents_verified = st.checkbox("Documents Verified", value=selected_banner.documents_verified)
                photo_verified = st.checkbox("Photo Verified", value=selected_banner.photo_verified)
                proof_approved = st.checkbox("Proof Approved by Customer", value=selected_banner.proof_approved)
                print_approved = st.checkbox("Approved for Printing", value=selected_banner.print_approved)
            
            with col2:
                st.write("**Process Flags**")
                submitted_to_printer = st.checkbox("Submitted to Printer", value=selected_banner.submitted_to_printer)
                thank_you_sent = st.checkbox("Thank You Sent", value=selected_banner.thank_you_sent)
            
            st.divider()
            
            pole_location = st.text_input("Pole Location", value=selected_banner.pole_location or "")
            notes = st.text_area("Notes", value=selected_banner.notes or "", height=100)
            
            submitted = st.form_submit_button("Update Banner", type="primary")
            
            if submitted:
                # Update banner
                selected_banner.documents_verified = documents_verified
                selected_banner.photo_verified = photo_verified
                selected_banner.proof_approved = proof_approved
                selected_banner.print_approved = print_approved
                selected_banner.submitted_to_printer = submitted_to_printer
                selected_banner.thank_you_sent = thank_you_sent
                selected_banner.pole_location = pole_location if pole_location else None
                selected_banner.notes = notes if notes else None
                
                db.update_banner(selected_banner)
                st.success(f"✅ Updated banner for {selected_banner.hero_name}")
                st.info(f"New status: {selected_banner.get_status()}")
                st.rerun()


def show_notifications():
    """Display notification management interface."""
    st.header("📧 Notifications")
    
    db = init_database()
    banners = db.get_all_banners()
    
    # Find banners ready for proof
    ready_banners = [b for b in banners 
                    if b.payment_verified and b.info_complete 
                    and b.photo_verified and b.documents_verified
                    and not b.proof_sent]
    
    st.subheader(f"📬 Banners Ready for Notification: {len(ready_banners)}")
    
    if ready_banners:
        for banner in ready_banners:
            st.write(f"- {banner.hero_name} (Sponsor: {banner.sponsor_name}, Email: {banner.sponsor_email})")
        
        st.divider()
        
        if st.button("Generate Text Notifications", type="primary"):
            notifier = NotificationService()
            count = 0
            
            for banner in ready_banners:
                message = notifier.generate_proof_ready_notification(banner)
                notifier.save_notification(message)
                banner.proof_sent = True
                db.update_banner(banner)
                count += 1
            
            st.success(f"✅ Generated {count} notifications and saved to notifications.txt")
            st.info("Banners marked as 'Proof Sent'")
            st.rerun()
    else:
        st.info("No banners are currently ready for notification.")
        st.write("Banners need to have:")
        st.write("- ✅ Complete information")
        st.write("- ✅ Verified payment")
        st.write("- ✅ Verified documents")
        st.write("- ✅ Verified photo")


def show_email_management():
    """Display email management interface."""
    st.header("📧 Email Management")
    
    if not EMAIL_AVAILABLE:
        st.error("❌ Email functionality not available. Install with: `pip install O365`")
        return
    
    config_file = 'm365_config.json'
    
    # Check if config exists
    config_exists = Path(config_file).exists()
    
    tab1, tab2, tab3 = st.tabs(["Setup", "Send Emails", "Check Responses"])
    
    with tab1:
        st.subheader("⚙️ M365 Email Setup")
        
        if config_exists:
            st.success("✅ Configuration file exists")
            config = load_m365_config(config_file)
            if config and config.get('client_id') != 'YOUR_AZURE_AD_CLIENT_ID':
                st.info("Configuration appears to be set up. You can send emails from the 'Send Emails' tab.")
            else:
                st.warning("⚠️ Configuration file exists but needs to be updated with real credentials.")
        else:
            st.info("No configuration file found.")
        
        if st.button("Create/Recreate Config Template"):
            create_m365_config_template(config_file)
            st.success(f"✅ Created config template: {config_file}")
            st.info("Please edit this file with your Azure AD app credentials before sending emails.")
            st.rerun()
        
        st.divider()
        st.write("📖 For detailed setup instructions, see EMAIL_SETUP.md")
    
    with tab2:
        st.subheader("📤 Create Draft Emails")
        
        db = init_database()
        banners = db.get_all_banners()
        ready_banners = [b for b in banners 
                        if b.payment_verified and b.info_complete 
                        and b.photo_verified and b.documents_verified
                        and not b.proof_sent]
        
        st.write(f"Found {len(ready_banners)} banners ready for email notification")
        
        if ready_banners:
            for banner in ready_banners[:5]:  # Show first 5
                st.write(f"- {banner.hero_name} ({banner.sponsor_email})")
            if len(ready_banners) > 5:
                st.write(f"... and {len(ready_banners) - 5} more")
        
        if st.button("Create Draft Emails in Outlook", type="primary", disabled=len(ready_banners) == 0):
            if not config_exists:
                st.error("❌ Configuration file not found. Set up email in the 'Setup' tab first.")
            else:
                config = load_m365_config(config_file)
                
                if not config:
                    st.error("❌ Failed to load configuration file.")
                elif config.get('client_id') == 'YOUR_AZURE_AD_CLIENT_ID':
                    st.error("❌ Please update the config file with real Azure AD credentials.")
                else:
                    with st.spinner("Creating draft emails..."):
                        try:
                            email_service = M365EmailService(
                                client_id=config['client_id'],
                                client_secret=config['client_secret'],
                                tenant_id=config.get('tenant_id')
                            )
                            
                            if email_service.authenticate():
                                stats = email_service.send_bulk_notifications(ready_banners, db)
                                st.success(f"✅ Created {stats['created']} draft emails")
                                if stats['failed'] > 0:
                                    st.warning(f"⚠️ Failed: {stats['failed']}")
                                if stats['skipped'] > 0:
                                    st.info(f"ℹ️ Skipped: {stats['skipped']}")
                                st.info("📬 Drafts are now in your Drafts folder. Review and send from Outlook.")
                            else:
                                st.error("❌ Failed to authenticate with Microsoft 365")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    with tab3:
        st.subheader("📨 Check for Approval Responses")
        
        days_back = st.slider("Check emails from last N days", 1, 30, 7)
        
        if st.button("Check Inbox for Approvals", type="primary"):
            if not config_exists:
                st.error("❌ Configuration file not found. Set up email in the 'Setup' tab first.")
            else:
                config = load_m365_config(config_file)
                
                if not config:
                    st.error("❌ Failed to load configuration file.")
                elif config.get('client_id') == 'YOUR_AZURE_AD_CLIENT_ID':
                    st.error("❌ Please update the config file with real Azure AD credentials.")
                else:
                    with st.spinner("Checking inbox..."):
                        try:
                            email_service = M365EmailService(
                                client_id=config['client_id'],
                                client_secret=config['client_secret'],
                                tenant_id=config.get('tenant_id')
                            )
                            
                            if email_service.authenticate():
                                db = init_database()
                                results = email_service.check_approval_responses(db, days_back=days_back)
                                
                                if results:
                                    st.success(f"✅ Processed {len(results)} approval responses")
                                    for result in results:
                                        status = "✅ Approved" if result['approved'] else "⚠️ Needs attention"
                                        st.write(f"{status}: {result['hero_name']} ({result['sponsor_email']})")
                                else:
                                    st.info("No approval responses found")
                            else:
                                st.error("❌ Failed to authenticate with Microsoft 365")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")


def main():
    """Main application entry point."""
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Import CSV", "Banner List", "Update Banner", "Notifications", "Email Management"]
    )
    
    st.sidebar.divider()
    st.sidebar.info("""
        **Hometown Hero Banner Management**
        
        A system for managing the Millcreek Kiwanis Hometown Hero banner program.
        
        Navigate using the menu above to:
        - View dashboard statistics
        - Import CSV files from Wix
        - Manage banner records
        - Send notifications
        - Manage email automation
    """)
    
    # Display selected page
    if page == "Dashboard":
        show_dashboard()
    elif page == "Import CSV":
        show_import_csv()
    elif page == "Banner List":
        show_banner_list()
    elif page == "Update Banner":
        show_update_banner()
    elif page == "Notifications":
        show_notifications()
    elif page == "Email Management":
        show_email_management()


if __name__ == '__main__':
    main()
