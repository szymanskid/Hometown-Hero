# Email Automation Setup Guide

This guide explains how to set up automated email notifications using your Microsoft 365 Business Premium account.

## Overview

The email automation features allow you to:
- **Send proof-ready notifications** automatically via email to sponsors
- **Include approval links** in emails for easy client response
- **Check inbox for approval responses** and automatically update the database
- **Track email status** to avoid duplicate notifications

## Prerequisites

- Microsoft 365 Business Premium account
- Admin access to Azure Active Directory (or ability to create app registrations)
- Python with O365 library installed: `pip install O365`

## Step 1: Azure AD App Registration

### 1. Go to Azure Portal
Visit: https://portal.azure.com

### 2. Navigate to App Registrations
- Click on "Azure Active Directory" in the left sidebar
- Click on "App registrations"
- Click "+ New registration"

### 3. Register the Application
- **Name**: `Hometown Hero Banner System`
- **Supported account types**: Select "Accounts in this organizational directory only"
- **Redirect URI**: Leave blank (we're using device code flow)
- Click "Register"

### 4. Note the Application Details
After registration, you'll see:
- **Application (client) ID** - Copy this, you'll need it
- **Directory (tenant) ID** - Copy this too

### 5. Create a Client Secret
- In the app registration, click "Certificates & secrets" in the left menu
- Click "+ New client secret"
- Description: `Banner System Secret`
- Expires: Choose your preference (recommend 24 months)
- Click "Add"
- **IMPORTANT**: Copy the secret VALUE immediately (you can't see it again)

### 6. Add API Permissions
- Click "API permissions" in the left menu
- Click "+ Add a permission"
- Choose "Microsoft Graph"
- Choose "Application permissions" (not Delegated)
- Add these permissions:
  - `Mail.Send`
  - `Mail.Read`
  - `Mail.ReadWrite`
- Click "Add permissions"
- **IMPORTANT**: Click "Grant admin consent for [your organization]"

## Step 2: Configure the Banner System

### 1. Create Configuration File
Run this command to create a template configuration file:

```bash
python banner_manager.py email-setup
```

This creates `m365_config.json` with this structure:

```json
{
  "client_id": "YOUR_AZURE_AD_CLIENT_ID",
  "client_secret": "YOUR_AZURE_AD_CLIENT_SECRET",
  "tenant_id": "YOUR_TENANT_ID_OR_common"
}
```

### 2. Edit Configuration File
Open `m365_config.json` and replace:
- `YOUR_AZURE_AD_CLIENT_ID` with the Application (client) ID from step 1.4
- `YOUR_AZURE_AD_CLIENT_SECRET` with the secret value from step 1.5
- `YOUR_TENANT_ID_OR_common` with the Directory (tenant) ID from step 1.4

### 3. Secure the Configuration File
**IMPORTANT**: This file contains sensitive credentials!
- Never commit it to version control (already in .gitignore)
- Store it securely with restricted permissions
- Consider using environment variables in production

## Step 3: Usage

### Send Proof Ready Emails

Once banners have complete information and verified payment:

```bash
python banner_manager.py email-send
```

This will:
1. Connect to your M365 account
2. Find all banners that are "Ready for Proof" and haven't been notified
3. Send professional HTML emails to each sponsor
4. Mark banners as "proof_sent" in the database
5. Show statistics (sent, failed, skipped)

### Check for Approval Responses

Periodically check your inbox for client approval responses:

```bash
python banner_manager.py email-check
```

Optional: Specify how many days back to check (default is 7):

```bash
python banner_manager.py email-check --days 14
```

This will:
1. Connect to your M365 account
2. Scan inbox for emails with "APPROVE" in subject or replies to banner emails
3. Match emails to banners by sponsor email address
4. Update `proof_approved` status in database
5. Mark processed emails as read

### Use Custom Config File

If you want to use a different config file location:

```bash
python banner_manager.py email-send --config /path/to/config.json
python banner_manager.py email-check --config /path/to/config.json
```

## Email Workflow

### Complete Automated Workflow

1. **Import CSVs** (as usual):
   ```bash
   python banner_manager.py import --hero heroes.csv --payment payments.csv
   ```

2. **Send automated emails** to ready sponsors:
   ```bash
   python banner_manager.py email-send
   ```
   - Sponsors receive professional email with proof link
   - Email asks them to reply with "APPROVE" in subject

3. **Check for approvals** (run daily or as needed):
   ```bash
   python banner_manager.py email-check
   ```
   - System reads inbox
   - Updates database automatically
   - Marks approved banners

4. **Assign pole locations** and **approve for printing**:
   ```bash
   python banner_manager.py update "John Smith" pole_location "Main St & 5th Ave"
   python banner_manager.py update "John Smith" print_approved yes
   ```

5. **Check what's ready to print**:
   ```bash
   python banner_manager.py list --status "printing"
   ```

## Email Template

Sponsors receive an HTML email like this:

```
Subject: Hometown Hero Banner Proof Ready - [Hero Name]

Your Banner Proof is Ready!

Dear [Sponsor Name],

Great news! The banner proof for [Hero Name] is ready for your review.

Please review the proof at: https://www.millcreekkiwanis.org/about-9

To approve this proof, please reply to this email with "APPROVE" in the subject line.

If you need any changes, please describe them in your reply.

---
Banner Details:
Hero: [Hero Name]
Sponsor: [Sponsor Name]
Reference ID: [Tracking ID]

Thank you for supporting our hometown heroes!

Millcreek Kiwanis Club
Hometown Hero Banner Program
```

## Troubleshooting

### Authentication Fails

**Error**: "Failed to authenticate with Microsoft 365"

**Solutions**:
1. Verify your client_id and client_secret are correct
2. Check that admin consent was granted for API permissions
3. Ensure your Azure AD app has the correct permissions
4. Try deleting `o365_token.txt` and re-authenticating

### No Emails Sent

**Check**:
1. Banners must have `info_complete = True` and `payment_verified = True`
2. Banners must not already have `proof_sent = True`
3. Sponsors must have valid email addresses
4. Run `python banner_manager.py list --status "ready for proof"` to see eligible banners

### Approvals Not Detected

**Requirements**:
- Sponsor must reply from the SAME email address in the database
- Subject line should contain "APPROVE" (case-insensitive)
- Email must be within the checked time window (default 7 days)

**Tips**:
- Run with more days: `--days 30` if needed
- Check that sponsor email addresses match exactly

### Permission Errors

**Error**: "Insufficient privileges to complete the operation"

**Solution**:
- Make sure you granted admin consent in Azure AD
- Verify you selected "Application permissions" not "Delegated permissions"
- Wait a few minutes for permissions to propagate

## Security Best Practices

1. **Never share your config file** - it contains credentials
2. **Rotate secrets regularly** - Update client secret every 12-24 months
3. **Use least privilege** - Only grant permissions actually needed
4. **Monitor access** - Check Azure AD sign-in logs periodically
5. **Backup your config** - Store securely in case of accidental deletion

## Advanced Configuration

### Using Environment Variables

Instead of storing credentials in a file, you can use environment variables:

```bash
export M365_CLIENT_ID="your-client-id"
export M365_CLIENT_SECRET="your-secret"
export M365_TENANT_ID="your-tenant-id"
```

Then modify the config file to use these.

### Scheduling Automated Checks

Set up a cron job (Linux/Mac) or Task Scheduler (Windows) to run checks automatically:

**Linux/Mac cron example** (check daily at 9 AM):
```cron
0 9 * * * cd /path/to/Hometown-Hero && python banner_manager.py email-check
```

**Windows Task Scheduler**:
1. Create new task
2. Trigger: Daily at 9:00 AM
3. Action: Start program
   - Program: `python`
   - Arguments: `banner_manager.py email-check`
   - Start in: `C:\path\to\Hometown-Hero`

## Support

For issues with:
- **Azure AD setup**: Consult Microsoft documentation or IT admin
- **O365 library**: https://github.com/O365/python-o365
- **Banner system**: Contact the development team

## Summary

Once configured, the email automation:
- ✅ Sends professional notifications automatically
- ✅ Tracks which sponsors have been notified
- ✅ Reads inbox for approvals
- ✅ Updates database automatically
- ✅ Saves hours of manual email work
- ✅ Provides audit trail of communications

This gives you a fully automated notification and approval workflow while maintaining the flexibility to handle special cases manually when needed.
