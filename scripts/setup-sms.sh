#!/bin/bash

# ReSan Bank - SMS Setup Script
# This script helps you configure Twilio SMS

cd "$(dirname "$0")/.." || exit

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           ReSan Bank - SMS OTP Setup                         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env already exists
if [ -f "config/.env" ]; then
    echo "⚠️  config/.env already exists!"
    echo ""
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Cancelled. Your existing .env file is unchanged."
        exit 0
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Step 1: Get Twilio Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Sign up at: https://www.twilio.com/try-twilio"
echo "2. Go to: https://console.twilio.com/"
echo "3. Copy your Account SID (starts with AC...)"
echo "4. Copy your Auth Token (click to reveal)"
echo "5. Buy a phone number with SMS capability"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Enter your Twilio Account SID: " account_sid
read -p "Enter your Twilio Auth Token: " auth_token
read -p "Enter your Twilio Phone Number (e.g., +1234567890): " phone_number

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Creating config/.env file..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create .env file
cat > config/.env << EOF
# Twilio SMS Configuration
# Created: $(date)

TWILIO_ACCOUNT_SID=$account_sid
TWILIO_AUTH_TOKEN=$auth_token
TWILIO_PHONE_NUMBER=$phone_number

# Instructions:
# 1. Restart the server after updating this file
# 2. To send SMS to ANY number (not just verified):
#    - Upgrade your Twilio account by adding a payment method
#    - Visit: https://console.twilio.com/us1/billing/manage-billing/billing-overview
#    - Cost: ~\$0.0075 per SMS (less than 1 cent per OTP)
EOF

echo "✅ config/.env file created successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Restart your server:"
echo "   ./scripts/start.sh"
echo ""
echo "2. You should see: ✓ Twilio SMS enabled"
echo ""
echo "3. ⚠️  IMPORTANT: Free trial limitation"
echo "   - Can only send to verified numbers"
echo "   - To send to ANY number, upgrade your account:"
echo "     https://console.twilio.com/us1/billing/manage-billing/billing-overview"
echo ""
echo "4. Test SMS:"
echo "   - Create a new account in the app"
echo "   - OTP should arrive on your phone!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Setup complete!"
echo ""
