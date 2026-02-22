import random
import string
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY)

def generate_random_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def encrypt_password(password):
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return fernet.decrypt(encrypted_password.encode()).decode()

def get_decoys(category='other', count=19):
    decoy_base = os.path.join('static', 'decoys')
    category_dir = os.path.join(decoy_base, category)
    
    all_decoys = []
    
    # 1. Try category folder
    if os.path.exists(category_dir):
        cat_files = [f"{category}/{f}" for f in os.listdir(category_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        all_decoys.extend(cat_files)
    
    # 2. Try base folder (the original 10 decoys)
    base_files = [f for f in os.listdir(decoy_base) if os.path.isfile(os.path.join(decoy_base, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    all_decoys.extend(base_files)
    
    # 3. Try other category folders if still low
    if len(all_decoys) < count:
        for folder in ['people', 'pets', 'nature', 'other']:
            if folder != category:
                fdir = os.path.join(decoy_base, folder)
                if os.path.exists(fdir):
                    f_files = [f"{folder}/{f}" for f in os.listdir(fdir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    all_decoys.extend(f_files)
    
    # Remove duplicates and ensure we have enough
    all_decoys = list(set(all_decoys))
    
    if not all_decoys:
        return []

    # If still not enough, repeat images to fill the count (the "same kind of logos" request)
    while len(all_decoys) < count:
        all_decoys.append(random.choice(all_decoys))
        
    return random.sample(all_decoys, count)
