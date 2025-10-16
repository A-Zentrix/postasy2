import os
try:
    import razorpay  # type: ignore
    _razorpay_import_ok = True
except Exception:  # ImportError or runtime import issues
    razorpay = None  # type: ignore
    _razorpay_import_ok = False
import logging
import time
from flask import current_app, flash
from models import db, User, Subscription

# Configure Razorpay with fallback
def get_razorpay_config():
    """Get Razorpay configuration with proper error handling"""
    key_id = os.environ.get('RAZORPAY_KEY_ID') or current_app.config.get('RAZORPAY_KEY_ID', '')
    key_secret = os.environ.get('RAZORPAY_KEY_SECRET') or current_app.config.get('RAZORPAY_KEY_SECRET', '')
    
    if not key_id or key_id == "rzp_test_your-key-id-here":
        logging.warning("RAZORPAY_KEY_ID not set - payment features will be disabled")
        return None, None
    
    if not key_secret or key_secret == "your-key-secret-here":
        logging.warning("RAZORPAY_KEY_SECRET not set - payment features will be disabled")
        return None, None
    
    return key_id, key_secret

# Initialize Razorpay client with configuration (only if import and keys are OK)
key_id, key_secret = get_razorpay_config()
if _razorpay_import_ok and key_id and key_secret:
    try:
        razorpay_client = razorpay.Client(auth=(key_id, key_secret))  # type: ignore[attr-defined]
    except Exception:
        razorpay_client = None
        logging.error("Failed to initialize Razorpay client")
else:
    razorpay_client = None

# Get domain for redirect URLs
def get_domain():
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return os.environ.get('REPLIT_DEV_DOMAIN')
    else:
        domains = os.environ.get('REPLIT_DOMAINS', 'localhost:8000')
        return domains.split(',')[0]

class RazorpayService:
    """Service class for handling Razorpay operations"""
    
    @staticmethod
    def get_plans():
        """Get subscription plans from configuration"""
        return current_app.config.get('SUBSCRIPTION_PLANS', {
            'free': {
                'name': 'Free Plan',
                'price': 0,
                'currency': 'INR',
                'features': ['10 Templates/month', 'Watermarked downloads', 'No AI features', 'No Scheduling'],
                'razorpay_plan_id': None
            },
            'starter': {
                'name': 'Starter',
                'price': 99,
                'currency': 'INR',
                'features': ['50 Templates/month', 'Remove watermark', 'Scheduler (5 posts/week)', 'Pre-made trending templates'],
                'razorpay_plan_id': 'plan_starter_99'
            },
            'pro': {
                'name': 'Pro Plan',
                'price': 399,
                'currency': 'INR',
                'features': ['Unlimited Templates', 'AI Brand Assistant', 'AI Captions + Hashtags', 'Scheduler (Unlimited)', 'Instagram Performance Dashboard'],
                'razorpay_plan_id': 'plan_pro_399'
            },
            'agency': {
                'name': 'Agency',
                'price': 999,
                'currency': 'INR',
                'features': ['Everything in Pro', '5 Client Accounts', 'Approval Workflow', 'White-label reports', 'API Access'],
                'razorpay_plan_id': 'plan_agency_999'
            }
        })
    
    @staticmethod
    def create_subscription(plan_id, user_id, customer_details=None):
        """Create a Razorpay subscription for a user"""
        try:
            # Check if Razorpay is configured
            if not razorpay_client:
                logging.error("Razorpay not configured - cannot create subscription")
                flash('Payment processing is not configured. Please contact support.', 'warning')
                raise ValueError("Payment processing not available")
            
            plans = RazorpayService.get_plans()
            if plan_id not in plans:
                raise ValueError(f"Invalid plan: {plan_id}")
            
            plan = plans[plan_id]
            if not plan['razorpay_plan_id']:
                raise ValueError(f"No Razorpay plan ID for plan: {plan_id}")
            
            # Get user details
            user = User.query.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Ensure we have a Razorpay customer_id for this user
            # Reuse existing subscription record or create one
            existing_subscription = Subscription.query.filter_by(user_id=user_id).first()
            customer_id = None
            if existing_subscription and existing_subscription.razorpay_customer_id:
                customer_id = existing_subscription.razorpay_customer_id
            else:
                # Create Razorpay customer and persist locally
                customer_payload = customer_details or {
                    'name': user.business_name or user.username,
                    'email': user.email,
                    'contact': getattr(user, 'phone', '9999999999')
                }
                customer = RazorpayService.create_customer(customer_payload)
                customer_id = customer.get('id')
                if not existing_subscription:
                    existing_subscription = Subscription(user_id=user_id)
                    db.session.add(existing_subscription)
                existing_subscription.razorpay_customer_id = customer_id
                db.session.commit()

            # Create subscription (Razorpay expects customer_id, not a full customer object)
            subscription_data = {
                'plan_id': plan['razorpay_plan_id'],
                'customer_notify': 1,
                'quantity': 1,
                'total_count': 12,  # 12 months subscription
                'start_at': int(time.time()) + 60,  # Start 1 minute from now
                'notes': {
                    'user_id': str(user_id),
                    'plan_id': plan_id,
                    'user_email': user.email
                },
                'customer_id': customer_id
            }
            
            subscription = razorpay_client.subscription.create(subscription_data)
            
            logging.info(f"Created Razorpay subscription {subscription['id']} for user {user_id}")
            return subscription
            
        except Exception as e:
            logging.error(f"Error creating subscription: {str(e)}")
            flash(f'Error creating subscription: {str(e)}', 'danger')
            raise e
    
    @staticmethod
    def verify_payment_signature(payment_id, order_id, signature):
        """Verify Razorpay payment signature"""
        try:
            if not razorpay_client:
                logging.error("Razorpay not configured - cannot verify signature")
                return False
            
            # Verify signature
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
            
            return True
            
        except Exception as e:
            logging.error(f"Signature verification failed: {str(e)}")
            return False
    
    @staticmethod
    def verify_webhook_signature(payload, signature):
        """Verify Razorpay webhook signature"""
        try:
            if not razorpay_client:
                logging.error("Razorpay not configured - cannot verify webhook signature")
                return False
            
            webhook_secret = os.environ.get('RAZORPAY_WEBHOOK_SECRET') or current_app.config.get('RAZORPAY_WEBHOOK_SECRET', '')
            if not webhook_secret or webhook_secret == "your-webhook-secret-here":
                logging.warning("RAZORPAY_WEBHOOK_SECRET not set - skipping signature verification")
                return True
            
            razorpay_client.utility.verify_webhook_signature(payload, signature, webhook_secret)
            return True
            
        except Exception as e:
            logging.error(f"Webhook signature verification failed: {str(e)}")
            return False
    
    @staticmethod
    def handle_webhook(payload, signature):
        """Handle Razorpay webhook events"""
        try:
            # Verify webhook signature
            if not RazorpayService.verify_webhook_signature(payload, signature):
                logging.error("Invalid webhook signature")
                return {'status': 'error', 'message': 'Invalid signature'}
            
            import json
            event = json.loads(payload)
            
            # Handle different event types
            if event['type'] == 'subscription.activated':
                subscription = event['data']['object']
                return RazorpayService._handle_subscription_activated(subscription)
            
            elif event['type'] == 'subscription.charged':
                payment = event['data']['object']
                return RazorpayService._handle_subscription_charged(payment)
            
            elif event['type'] == 'subscription.cancelled':
                subscription = event['data']['object']
                return RazorpayService._handle_subscription_cancelled(subscription)
            
            elif event['type'] == 'subscription.completed':
                subscription = event['data']['object']
                return RazorpayService._handle_subscription_completed(subscription)
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Webhook error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_subscription_activated(subscription_data):
        """Handle subscription activation"""
        try:
            user_id = subscription_data['notes'].get('user_id')
            plan_id = subscription_data['notes'].get('plan_id')
            
            if not user_id:
                logging.error("No user_id in subscription notes")
                return {'status': 'error', 'message': 'No user_id found'}
            
            # Update user subscription in database
            user = User.query.get(user_id)
            if user:
                # Create or update subscription record
                subscription = Subscription.query.filter_by(user_id=user_id).first()
                if not subscription:
                    subscription = Subscription()
                    subscription.user_id = user_id
                    db.session.add(subscription)
                
                subscription.razorpay_subscription_id = subscription_data['id']
                subscription.razorpay_customer_id = subscription_data.get('customer_id')
                subscription.plan_id = plan_id
                subscription.status = 'active'
                
                db.session.commit()
                logging.info(f"Activated subscription for user {user_id} to {plan_id}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling subscription activation: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_subscription_charged(payment_data):
        """Handle subscription payment"""
        try:
            subscription_id = payment_data['subscription_id']
            
            # Find subscription by subscription ID
            subscription = Subscription.query.filter_by(
                razorpay_subscription_id=subscription_id
            ).first()
            
            if subscription:
                subscription.razorpay_payment_id = payment_data['id']
                subscription.status = 'active'
                db.session.commit()
                logging.info(f"Updated payment for subscription {subscription_id}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling subscription payment: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_subscription_cancelled(subscription_data):
        """Handle subscription cancellation"""
        try:
            subscription_id = subscription_data['id']
            
            # Find subscription by subscription ID
            subscription = Subscription.query.filter_by(
                razorpay_subscription_id=subscription_id
            ).first()
            
            if subscription:
                subscription.status = 'cancelled'
                subscription.plan_id = 'free'  # Downgrade to free
                db.session.commit()
                logging.info(f"Cancelled subscription {subscription_id}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling subscription cancellation: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_subscription_completed(subscription_data):
        """Handle subscription completion"""
        try:
            subscription_id = subscription_data['id']
            
            # Find subscription by subscription ID
            subscription = Subscription.query.filter_by(
                razorpay_subscription_id=subscription_id
            ).first()
            
            if subscription:
                subscription.status = 'completed'
                db.session.commit()
                logging.info(f"Completed subscription {subscription_id}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling subscription completion: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def get_subscription_status(subscription_id):
        """Get subscription status from Razorpay"""
        try:
            if not razorpay_client:
                logging.warning("Razorpay not configured - returning default subscription status")
                return {'active': False}
            
            subscription = razorpay_client.subscription.fetch(subscription_id)
            
            return {
                'active': subscription['status'] in ['active', 'authenticated'],
                'status': subscription['status'],
                'plan_id': subscription['plan_id'],
                'current_start': subscription.get('current_start'),
                'current_end': subscription.get('current_end')
            }
                
        except Exception as e:
            logging.error(f"Error getting subscription status: {str(e)}")
            return {'active': False}
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancel a Razorpay subscription"""
        try:
            if not razorpay_client:
                logging.error("Razorpay not configured - cannot cancel subscription")
                raise ValueError("Payment processing not available")
            
            subscription = razorpay_client.subscription.cancel(subscription_id)
            
            # Update local database
            local_subscription = Subscription.query.filter_by(
                razorpay_subscription_id=subscription_id
            ).first()
            
            if local_subscription:
                local_subscription.status = 'cancelled'
                local_subscription.plan_id = 'free'
                db.session.commit()
            
            logging.info(f"Cancelled subscription {subscription_id}")
            return subscription
            
        except Exception as e:
            logging.error(f"Error cancelling subscription: {str(e)}")
            raise e
    
    @staticmethod
    def create_customer(customer_details):
        """Create a Razorpay customer"""
        try:
            if not razorpay_client:
                logging.error("Razorpay not configured - cannot create customer")
                raise ValueError("Payment processing not available")
            
            customer = razorpay_client.customer.create(customer_details)
            logging.info(f"Created Razorpay customer {customer['id']}")
            return customer
            
        except Exception as e:
            logging.error(f"Error creating customer: {str(e)}")
            raise e
