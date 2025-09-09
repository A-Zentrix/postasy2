import os
import stripe
import logging
from flask import current_app

# Configure Stripe with fallback
def get_stripe_config():
    """Get Stripe configuration with proper error handling"""
    secret_key = os.environ.get('STRIPE_SECRET_KEY') or current_app.config.get('STRIPE_SECRET_KEY', '')
    publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY') or current_app.config.get('STRIPE_PUBLISHABLE_KEY', '')
    
    if not secret_key or secret_key == "sk_test_your-stripe-secret-key-here":
        logging.warning("STRIPE_SECRET_KEY not set - payment features will be disabled")
        return None, None
    
    if not publishable_key or publishable_key == "pk_test_your-stripe-publishable-key-here":
        logging.warning("STRIPE_PUBLISHABLE_KEY not set - payment features will be disabled")
        return None, None
    
    return secret_key, publishable_key

# Initialize Stripe with configuration
secret_key, publishable_key = get_stripe_config()
if secret_key:
    stripe.api_key = secret_key

# Get domain for redirect URLs
def get_domain():
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return os.environ.get('REPLIT_DEV_DOMAIN')
    else:
        domains = os.environ.get('REPLIT_DOMAINS', 'localhost:5000')
        return domains.split(',')[0]

class StripeService:
    """Service class for handling Stripe operations"""
    
    # Subscription plans - will be loaded from config
    @staticmethod
    def get_plans():
        """Get subscription plans from configuration"""
        return current_app.config.get('SUBSCRIPTION_PLANS', {
        'free': {
            'name': 'Free Plan',
            'price': 0,
            'features': ['5 posters per month', 'Watermarked downloads', 'Basic templates'],
            'stripe_price_id': None
        },
        'pro': {
            'name': 'Pro Plan',
            'price': 9.99,
            'features': ['Unlimited posters', 'Watermark-free downloads', 'Premium templates', 'High-res exports'],
                'stripe_price_id': 'price_test_pro_plan'
        },
        'premium': {
            'name': 'Premium Plan', 
            'price': 19.99,
            'features': ['Everything in Pro', 'Priority support', 'Advanced AI features', 'Custom branding'],
                'stripe_price_id': 'price_test_premium_plan'
        }
        })
    
    @staticmethod
    def create_checkout_session(plan_id, user_id, success_url=None, cancel_url=None):
        """Create a Stripe checkout session for subscription"""
        try:
            # Check if Stripe is configured
            if not stripe.api_key or stripe.api_key == "sk_test_your-stripe-secret-key-here":
                logging.error("Stripe not configured - cannot create checkout session")
                flash('Payment processing is not configured. Please contact support.', 'warning')
                raise ValueError("Payment processing not available")
            
            plans = StripeService.get_plans()
            if plan_id not in plans:
                raise ValueError(f"Invalid plan: {plan_id}")
            
            plan = plans[plan_id]
            if not plan['stripe_price_id']:
                raise ValueError(f"No Stripe price ID for plan: {plan_id}")
            
            domain = get_domain()
            if not success_url:
                success_url = f"http://{domain}/payment/success"
            if not cancel_url:
                cancel_url = f"http://{domain}/payment/cancel"
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': plan['stripe_price_id'],
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user_id),
                    'plan_id': plan_id
                },
                automatic_tax={'enabled': True},
                billing_address_collection='required',
            )
            
            return session
            
        except Exception as e:
            logging.error(f"Error creating checkout session: {str(e)}")
            flash(f'Error creating checkout session: {str(e)}', 'danger')
            raise e
    
    @staticmethod
    def create_customer_portal_session(customer_id, return_url=None):
        """Create a Stripe customer portal session"""
        try:
            # Check if Stripe is configured
            if not stripe.api_key or stripe.api_key == "sk_test_your-stripe-secret-key-here":
                logging.error("Stripe not configured - cannot create portal session")
                raise ValueError("Payment processing not available")
            
            domain = get_domain()
            if not return_url:
                return_url = f"http://{domain}/profile"
            
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            
            return session
            
        except Exception as e:
            logging.error(f"Error creating portal session: {str(e)}")
            raise e
    
    @staticmethod
    def get_subscription_status(customer_id):
        """Get subscription status for a customer"""
        try:
            # Check if Stripe is configured
            if not stripe.api_key or stripe.api_key == "sk_test_your-stripe-secret-key-here":
                logging.warning("Stripe not configured - returning default subscription status")
                return {'active': False}
            
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                subscription = subscriptions.data[0]
                return {
                    'active': True,
                    'plan_id': subscription.metadata.get('plan_id', 'unknown'),
                    'status': subscription.status
                }
            else:
                return {'active': False}
                
        except Exception as e:
            logging.error(f"Error getting subscription status: {str(e)}")
            return {'active': False}
    
    @staticmethod
    def handle_webhook(payload, sig_header):
        """Handle Stripe webhook events"""
        try:
            # Check if Stripe is configured
            if not stripe.api_key or stripe.api_key == "sk_test_your-stripe-secret-key-here":
                logging.error("Stripe not configured - cannot handle webhook")
                return {'status': 'error', 'message': 'Payment processing not available'}
            
            # Verify webhook signature
            endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET') or current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
            if endpoint_secret and endpoint_secret != "whsec_your-webhook-secret-here":
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            else:
                # For development, skip signature verification
                import json
                event = json.loads(payload)
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                return StripeService._handle_successful_payment(session)
            
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                return StripeService._handle_subscription_update(subscription)
            
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                return StripeService._handle_subscription_cancellation(subscription)
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Webhook error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_successful_payment(session):
        """Handle successful payment completion"""
        try:
            from models import User, Subscription
            from app import db
            
            user_id = session['metadata']['user_id']
            plan_id = session['metadata']['plan_id']
            customer_id = session['customer']
            subscription_id = session['subscription']
            
            # Update user subscription in database
            user = User.query.get(user_id)
            if user:
                # Create or update subscription record
                subscription = Subscription.query.filter_by(user_id=user_id).first()
                if not subscription:
                    subscription = Subscription()
                    subscription.user_id = user_id
                    db.session.add(subscription)
                
                subscription.stripe_customer_id = customer_id
                subscription.stripe_subscription_id = subscription_id
                subscription.plan_id = plan_id
                subscription.status = 'active'
                
                db.session.commit()
                logging.info(f"Updated subscription for user {user_id} to {plan_id}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling successful payment: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_subscription_update(subscription_data):
        """Handle subscription updates"""
        try:
            from models import Subscription
            from app import db
            
            customer_id = subscription_data['customer']
            status = subscription_data['status']
            
            # Find subscription by customer ID
            subscription = Subscription.query.filter_by(
                stripe_customer_id=customer_id
            ).first()
            
            if subscription:
                subscription.status = status
                db.session.commit()
                logging.info(f"Updated subscription status to {status}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling subscription update: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def _handle_subscription_cancellation(subscription_data):
        """Handle subscription cancellation"""
        try:
            from models import Subscription
            from app import db
            
            customer_id = subscription_data['customer']
            
            # Find subscription by customer ID
            subscription = Subscription.query.filter_by(
                stripe_customer_id=customer_id
            ).first()
            
            if subscription:
                subscription.status = 'cancelled'
                subscription.plan_id = 'free'  # Downgrade to free
                db.session.commit()
                logging.info(f"Cancelled subscription for customer {customer_id}")
            
            return {'status': 'success'}
            
        except Exception as e:
            logging.error(f"Error handling subscription cancellation: {str(e)}")
            return {'status': 'error', 'message': str(e)}