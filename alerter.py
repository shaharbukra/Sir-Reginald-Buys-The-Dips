"""
Critical Alert System for Trading System
Sends immediate notifications for CRITICAL events and uses Ollama AI for autonomous decision making
"""

import logging
import smtplib
import os
import asyncio
import subprocess
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class CriticalAlerter:
    """
    Sends critical alerts via multiple channels when trading system encounters
    dangerous conditions that require immediate attention
    """
    
    def __init__(self):
        self.email_enabled = False
        self.console_alerts = True  # Always enabled as fallback
        self.ai_enabled = True  # Ollama AI decision making
        self.ollama_model = "llama3:latest"  # Default model
        
        # Email configuration from environment variables
        self.smtp_server = os.environ.get('ALERT_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('ALERT_SMTP_PORT', '587'))
        self.sender_email = os.environ.get('ALERT_SENDER_EMAIL')
        self.sender_password = os.environ.get('ALERT_SENDER_PASSWORD')
        self.recipient_email = os.environ.get('ALERT_RECIPIENT_EMAIL')
        
        # Check Ollama availability
        self._check_ollama_availability()
        
        # Enable email if credentials are provided
        if all([self.sender_email, self.sender_password, self.recipient_email]):
            self.email_enabled = True
            logger.info("📧 Critical alerting system initialized with email notifications")
        else:
            logger.info("📢 Critical alerting system initialized (console only)")
            
        if self.ai_enabled:
            logger.info(f"🤖 AI decision making enabled with {self.ollama_model}")
    
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
    
    def _check_ollama_availability(self):
        """Check if Ollama is available and what models are installed"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                models = result.stdout.strip()
                if 'llama3:latest' in models:
                    self.ollama_model = "llama3:latest"
                elif 'qwq:32b' in models:
                    self.ollama_model = "qwq:32b"
                elif 'qwen2.5:32b' in models:
                    self.ollama_model = "qwen2.5:32b"
                else:
                    # Try to find any available model
                    lines = models.split('\n')[1:]  # Skip header
                    if lines and lines[0].strip():
                        self.ollama_model = lines[0].split()[0]
                
                logger.info(f"🤖 Ollama detected with model: {self.ollama_model}")
                return True
            else:
                self.ai_enabled = False
                logger.warning("⚠️ Ollama not available - AI decisions disabled")
                return False
        except Exception as e:
            self.ai_enabled = False
            logger.warning(f"⚠️ Ollama check failed: {e} - AI decisions disabled")
            return False
    
    async def get_ai_decision(self, alert_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI decision from Ollama for critical alert"""
        if not self.ai_enabled:
            return {"decision": "manual_review", "reasoning": "AI unavailable"}
        
        try:
            # Create prompt for AI decision making
            prompt = self._create_decision_prompt(alert_type, context)
            
            # Query Ollama
            process = await asyncio.create_subprocess_exec(
                'ollama', 'run', self.ollama_model,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=prompt.encode())
            
            if process.returncode == 0:
                response = stdout.decode().strip()
                return self._parse_ai_response(response)
            else:
                logger.error(f"Ollama error: {stderr.decode()}")
                return {"decision": "manual_review", "reasoning": "AI query failed"}
                
        except Exception as e:
            logger.error(f"AI decision failed: {e}")
            return {"decision": "manual_review", "reasoning": f"AI error: {e}"}
    
    def _create_decision_prompt(self, alert_type: str, context: Dict[str, Any]) -> str:
        """Create prompt for AI decision making"""
        base_prompt = """You are Sir Reginald, an AI trading assistant managing a live $2000 paper trading account. 
A CRITICAL trading alert has been triggered that requires immediate decision making.

ALERT TYPE: {alert_type}
CONTEXT: {context}

Your trading philosophy:
- Risk management is paramount 
- Cut losses quickly, let winners run
- No position should risk more than 2-3% of account
- Extended hours gaps >5% are dangerous
- Always protect capital first

RESPOND WITH ONLY A JSON object in this exact format:
{{
  "decision": "hold|sell_market_open|set_stop_loss|emergency_sell|manual_review",
  "reasoning": "Brief explanation of decision",
  "confidence": 0.85,
  "risk_level": "low|medium|high",
  "action_details": "Specific action to take if any"
}}

Be decisive and conservative. When in doubt, protect capital."""

        return base_prompt.format(
            alert_type=alert_type,
            context=json.dumps(context, indent=2)
        )
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract decision"""
        try:
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                decision_data = json.loads(json_str)
                
                # Validate required fields
                required_fields = ["decision", "reasoning", "confidence", "risk_level"]
                if all(field in decision_data for field in required_fields):
                    return decision_data
                    
            # Fallback parsing if JSON is malformed
            logger.warning("AI response not in expected JSON format, using fallback parsing")
            
            # Simple keyword-based parsing
            response_lower = response.lower()
            if "sell" in response_lower and "emergency" in response_lower:
                decision = "emergency_sell"
            elif "sell" in response_lower and ("market" in response_lower or "open" in response_lower):
                decision = "sell_market_open"  
            elif "stop" in response_lower and "loss" in response_lower:
                decision = "set_stop_loss"
            elif "hold" in response_lower:
                decision = "hold"
            else:
                decision = "manual_review"
                
            return {
                "decision": decision,
                "reasoning": response[:200] + "..." if len(response) > 200 else response,
                "confidence": 0.7,
                "risk_level": "medium"
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return {
                "decision": "manual_review", 
                "reasoning": f"Parse error: {e}",
                "confidence": 0.0,
                "risk_level": "unknown"
            }
    
    async def send_gap_risk_alert_with_ai(self, symbol: str, gap_percent: float, 
                                         current_price: float, context: Dict = None):
        """Send gap risk alert and get AI decision"""
        # Prepare context for AI
        ai_context = {
            "symbol": symbol,
            "gap_percent": gap_percent,
            "current_price": current_price,
            "alert_type": "extended_hours_gap_risk",
            "market_session": context.get("market_session", "after_hours") if context else "after_hours",
            "position_value": context.get("position_value", "unknown") if context else "unknown",
            "account_equity": context.get("account_equity", 2000) if context else 2000
        }
        
        # Get AI decision
        if self.ai_enabled:
            logger.info(f"🤖 Consulting AI for gap risk decision on {symbol}...")
            ai_decision = await self.get_ai_decision("gap_risk", ai_context)
            
            # Log AI decision
            logger.info(f"🤖 AI Decision for {symbol}: {ai_decision['decision']}")
            logger.info(f"🤖 AI Reasoning: {ai_decision['reasoning']}")
            logger.info(f"🤖 AI Confidence: {ai_decision['confidence']:.1%}, Risk Level: {ai_decision['risk_level']}")
            
            # Send enhanced alert with AI decision
            message = f"Extended hours gap risk detected in {ai_context['market_session']}"
            details = (f"Significant moves detected: {symbol}\n"
                      f"Gap: {gap_percent:+.1f}% to ${current_price:.2f}\n\n"
                      f"🤖 AI DECISION: {ai_decision['decision'].upper()}\n"
                      f"🤖 Reasoning: {ai_decision['reasoning']}\n"
                      f"🤖 Confidence: {ai_decision['confidence']:.1%} | Risk: {ai_decision['risk_level']}")
            
            await self.send_critical_alert(message, details)
            return ai_decision
        else:
            # Fallback to regular alert
            message = f"Extended hours gap risk detected"
            details = f"Significant moves detected: {symbol}"
            await self.send_critical_alert(message, details)
            return {"decision": "manual_review", "reasoning": "AI unavailable"}