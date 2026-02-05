import logging
import upstox_client
from upstox_client.rest import ApiException

logger = logging.getLogger("UpstoxClient")

class UpstoxHandler:
    def __init__(self, config):
        self.config = config
        self.api_version = '2.0'
        self.access_token = self.config.get("ACCESS_TOKEN")
        
        if not self.access_token:
            logger.warning("No access token found in config. Authentication required.")
            
        self.configuration = upstox_client.Configuration()
        self.configuration.access_token = self.access_token

    def validate_session(self):
        """
        Verify if the current token is valid by fetching user profile.
        """
        if not self.access_token:
            return False
            
        try:
            api_instance = upstox_client.UserApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.get_profile(self.api_version)
            logger.info(f"Session Valid. User: {api_response.data.user_name}")
            return True
        except ApiException as e:
            logger.error(f"Session Invalid: {e}")
            return False

    def get_login_url(self):
        """
        Generate the login URL for the user to authenticate.
        """
        base_url = "https://api.upstox.com/v2/login/authorization/dialog"
        client_id = self.config["UPSTOX_API_KEY"]
        redirect_uri = self.config["UPSTOX_REDIRECT_URI"]
        return f"{base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"

    def generate_access_token(self, code):
        """
        Exchange auth code for access token.
        """
        api_instance = upstox_client.LoginApi()
        try:
            api_response = api_instance.token(
                self.api_version,
                code=code,
                client_id=self.config["UPSTOX_API_KEY"],
                client_secret=self.config["UPSTOX_API_SECRET"],
                redirect_uri=self.config["UPSTOX_REDIRECT_URI"],
                grant_type="authorization_code"
            )
            self.access_token = api_response.access_token
            self.configuration.access_token = self.access_token
            logger.info("Access Token Generated successfully")
            return self.access_token
        except ApiException as e:
            logger.error(f"Failed to generate token: {e}")
            raise

    def get_market_data_feed_details(self):
        # We will implement WebSocket logic in a separate module
        pass

    def place_order(self, symbol, side, quantity, product='I', order_type='MARKET', price=0.0):
        """
        Place an order via Upstox API.
        """
        if not self.access_token:
            logger.error("Cannot place order: No Access Token.")
            return None
            
        try:
            api_instance = upstox_client.OrderApi(upstox_client.ApiClient(self.configuration))
            
            # Construct order body
            body = upstox_client.PlaceOrderRequest(
                quantity=quantity,
                product=product, # I = Intraday, D = Delivery
                validity='DAY',
                price=price if order_type == 'LIMIT' else 0.0,
                tag='NKBot_Algo',
                instrument_token=symbol, # This needs to be the instrument KEY (e.g., NSE_EQ|INE...)
                order_type=order_type,
                transaction_type=side,
                disclosed_quantity=0,
                trigger_price=0.0,
                is_amo=False
            )
            
            api_response = api_instance.place_order(body, self.api_version)
            logger.info(f"Order Placed: {api_response.data.order_id}")
            return api_response.data.order_id
            
        except ApiException as e:
            logger.error(f"Order Placement Failed: {e}")
            return None

    def cancel_order(self, order_id):
        """
        Cancel an open order.
        """
        try:
            api_instance = upstox_client.OrderApi(upstox_client.ApiClient(self.configuration))
            api_response = api_instance.cancel_order(order_id, self.api_version)
            logger.info(f"Order Cancelled: {order_id}")
            return True
        except ApiException as e:
            logger.error(f"Cancel Order Failed: {e}")
            return False
