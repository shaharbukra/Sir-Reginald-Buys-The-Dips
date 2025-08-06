"""
Critical Alert System for Trading System
Sends immediate notifications for CRITICAL events
"""

import logging
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

class CriticalAlerter:
    """
    Sends critical alerts via multiple channels when trading system encounters
    dangerous conditions that require immediate attention
    """
    
    def __init__(self):
        self.email_enabled = False
        self.console_alerts = True  # Always enabled as fallback
        
        # Email configuration from environment variables
        self.smtp_server = os.environ.get('ALERT_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('ALERT_SMTP_PORT', '587'))
        self.sender_email = os.environ.get('ALERT_SENDER_EMAIL')
        self.sender_password = os.environ.get('ALERT_SENDER_PASSWORD')
        self.recipient_email = os.environ.get('ALERT_RECIPIENT_EMAIL')
        
        # Enable email if credentials are provided
        if all([self.sender_email, self.sender_password, self.recipient_email]):
            self.email_enabled = True
            logger.info("📧 Critical alerting system initialized with email notifications")
        else:
            logger.info("📢 Critical alerting system initialized (console only)")
    
    async def send_critical_alert(self, message: str, details: str = None):
        """Send critical alert via all available channels"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format alert message
            alert_title = "🚨 CRITICAL TRADING SYSTEM ALERT"
            full_message = f"{alert_title}\n"
            full_message += f"Time: {timestamp}\n"
            full_message += f"Alert: {message}\n"
            if details:
                full_message += f"Details: {details}\n"
            full_message += "\nImmediate attention required!"
            
            # Console alert (always enabled)
            self._send_console_alert(full_message)
            
            # Email alert (if configured)
            if self.email_enabled:
                await self._send_email_alert(alert_title, full_message)
            
        except Exception as e:
            logger.error(f"Critical alert system failure: {e}")
            # Fallback to basic console alert
            print(f"\n{'='*50}")
            print(f"CRITICAL ALERT SYSTEM FAILURE: {e}")
            print(f"ORIGINAL ALERT: {message}")
            print(f"{'='*50}\n")
    
    def _send_console_alert(self, message: str):
        """Send alert to console with visual emphasis"""
        border = "=" * 60
        print(f"\n{border}")
        print(message)
        print(f"{border}\n")
        
        # Also log at CRITICAL level
        logger.critical(f"ALERT SENT: {message}")
    
    async def _send_email_alert(self, subject: str, message: str):
        """Send email alert"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.recipient_email, text)
            server.quit()
            
            logger.info(f"📧 Critical alert email sent to {self.recipient_email}")
            
        except Exception as e:
            logger.error(f"Email alert failed: {e}")
    
    async def send_position_safety_alert(self, symbol: str, issue: str, action_taken: str):
        """Specific alert for position safety issues"""
        message = f"Position safety violation: {symbol}"
        details = f"Issue: {issue}\nAction taken: {action_taken}"
        await self.send_critical_alert(message, details)
    
    async def send_broker_interface_alert(self, symbol: str, broker_issue: str, system_response: str):
        """Specific alert for broker interface problems"""
        message = f"Broker interface failure: {symbol}"
        details = f"Broker issue: {broker_issue}\nSystem response: {system_response}"
        await self.send_critical_alert(message, details)
    
    async def send_pdt_violation_alert(self, violation_details: str):
        """Specific alert for PDT violations"""
        message = "Pattern Day Trading rule violation detected"
        details = f"PDT Issue: {violation_details}\nTrading halted to prevent account restrictions"
        await self.send_critical_alert(message, details)
    
    async def send_system_startup_alert(self, naked_positions: list):
        """Alert for naked positions found at startup"""
        if naked_positions:
            message = f"System startup: {len(naked_positions)} naked positions detected"
            details = f"Positions without stop protection: {', '.join(naked_positions)}"
            await self.send_critical_alert(message, details)