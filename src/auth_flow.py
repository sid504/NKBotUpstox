from config import load_config
from upstox_client import UpstoxHandler

def run_auth_flow():
    config = load_config()
    handler = UpstoxHandler(config)
    
    if handler.validate_session():
        print("Existing session is valid. No action needed.")
        return

    print("Authentication Required.")
    print("Please login using this URL in your browser:")
    print("-" * 50)
    print(handler.get_login_url())
    print("-" * 50)
    
    code = input("After login, paste the 'code' parameter from the redirect URL here: ").strip()
    
    try:
        token = handler.generate_access_token(code)
        print("\nSUCCESS! Access Token Generated.")
        print(f"Update your .env file with this token:\nACCESS_TOKEN={token}")
    except Exception as e:
        print(f"Error generating token: {e}")

if __name__ == "__main__":
    run_auth_flow()
