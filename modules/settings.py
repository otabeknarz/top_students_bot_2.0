import pathlib
import os
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

USERS_SHOULD_INVITE_COUNT = 3

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
USERS_API = f"{BASE_URL}/api/users/users/"
INVITATIONS_API = f"{BASE_URL}/api/users/invitations/"

CHANNELS_IDs = {
    -1001825051597: ("Azizbek Zaylobiddinov", "https://t.me/abdulazizziy"),
    -1002277135189: ("Saidafzal Shukurov", "https://t.me/shoks927"),
    -1002078049933: ("Akramjon Abdurakhimov", "https://t.me/akramjon_io"),
    -1001803075478: ("Ozodbek Eshboboev", "https://t.me/ozodiiy"),
}
