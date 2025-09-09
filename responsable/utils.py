from .models import Notification
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from django.conf import settings
import base64
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Responsable


def ajouter_notification(titre, message, destinataire, icone="bx bx-info-circle", url=None):
    from .models import Notification
    Notification.objects.create(
        titre=titre,
        message=message,
        icone=icone,
        url=url or "",
        destinataire=destinataire
    )

def encrypt_password(password: str) -> str:
    key = settings.AES_SECRET_KEY
    iv = settings.AES_IV

    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(password.encode('utf-8')) + padder.finalize()

    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(encrypted).decode('utf-8')  # stocké en base64


def decrypt_password(encrypted_password: str) -> str:
    try:
        # 1. Base64 decode
        encrypted_bytes = base64.b64decode(encrypted_password)

        # 2. Déchiffrement AES-CTR
        key = settings.AES_SECRET_KEY  # Doit être 16, 24 ou 32 octets
        iv = settings.AES_IV           # Doit être 16 octets

        cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted_bytes) + decryptor.finalize()

        # 3. Retirer padding PKCS7
        unpadder = padding.PKCS7(128).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

        return decrypted.decode("utf-8")

    except Exception:
        return encrypted_password

