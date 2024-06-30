# Import required libraries
import os
import io
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment


# Set up IBM Watson TTS credentials
TTS_API_KEY = os.environ["tts_api_key"]
TTS_URL = os.environ["tts_url"]


# Set up the authenticator and TTS service
authenticator = IAMAuthenticator(TTS_API_KEY)
tts_service = TextToSpeechV1(authenticator = authenticator)
tts_service.set_service_url(TTS_URL)
print("Successfully authenticated for TTS service!!")


# Define the transcription
transcription = [
    ("Agent", "Bonjour, merci d'avoir appelé le support technique de la banque XYZ. Comment puis-je vous aider aujourd'hui?"),
    ("Employé", "Bonjour, je rencontre des difficultés pour configurer mon email Outlook sur mon ordinateur."),
    ("Agent", "Je comprends. Pouvez-vous me fournir votre ID employé et l'ID matériel de votre ordinateur, s'il vous plaît?"),
    ("Employé", "Oui, bien sûr. Mon ID employé est 123456 et l'ID matériel de mon ordinateur est XYZ789."),
    ("Agent", "Merci. Avant de commencer, puis-je vous poser quelques questions de conformité pour confirmer votre identité?"),
    ("Employé", "Oui, pas de problème."),
    ("Agent", "Quelle est votre date de naissance?"),
    ("Employé", "Le 15 mars 1985."),
    ("Agent", "Merci. Et quelle est votre adresse électronique professionnelle?"),
    ("Employé", "c'est jean.dupont@xyzbank.com"),
    ("Agent", "Parfait, tout est en ordre. Maintenant, pouvez-vous me dire exactement où vous rencontrez des problèmes lors de la configuration d'Outlook?"),
    ("Employé", "Oui, chaque fois que j'essaie de configurer le compte, je reçois un message d'erreur disant que le serveur ne peut pas être trouvé."),
    ("Agent", "D'accord, nous allons vérifier ça ensemble. Tout d'abord, ouvrez Outlook et allez dans les paramètres de compte. Avez-vous déjà entré les informations de votre compte?"),
    ("Employé", "Oui, j'ai entré mon adresse e-mail et mon mot de passe."),
    ("Agent", "Très bien. Dans les paramètres du serveur, assurez-vous que le serveur de courrier entrant (IMAP) est 'imap.xyzbank.com' et le serveur de courrier sortant (SMTP) est 'smtp.xyzbank.com'. Pouvez-vous vérifier cela, s'il vous plaît?"),
    ("Employé", "Un instant... Oui, j'ai bien 'imap.xyzbank.com' pour le serveur entrant et 'smtp.xyzbank.com' pour le serveur sortant."),
    ("Agent", "Parfait. Maintenant, vérifiez que les ports sont corrects. Pour le serveur IMAP, utilisez le port 993 et assurez-vous que SSL est activé. Pour le serveur SMTP, utilisez le port 587 avec TLS activé. Pouvez-vous vérifier ces paramètres?"),
    ("Employé", "D'accord, laissez-moi voir... Oui, le port pour IMAP est bien 993 avec SSL et pour SMTP, c'est 587 avec TLS."),
    ("Agent", "Excellent. Maintenant, vérifiez votre connexion Internet pour vous assurer que vous êtes bien connecté. Pouvez-vous ouvrir un navigateur et accéder à un site Web?"),
    ("Employé", "Oui, ma connexion Internet fonctionne bien."),
    ("Agent", "Parfait. Maintenant, essayez de relancer Outlook et de vérifier si le problème persiste."),
    ("Employé", "Un instant... Je viens de relancer Outlook et ça semble fonctionner! Je n'ai plus de message d'erreur."),
    ("Agent", "Très bien, c'est une excellente nouvelle! Si vous rencontrez à nouveau des problèmes, n'hésitez pas à nous rappeler. Y a-t-il autre chose avec laquelle je peux vous aider aujourd'hui?"),
    ("Employé", "Non, c'est tout. Merci beaucoup pour votre aide!"),
    ("Agent", "Avec plaisir! Passez une bonne journée."),
    ("Employé", "Merci, vous aussi. Au revoir!"),
    ("Agent", "Au revoir!")
]


# Define the voices for each speaker
voices = {
    "Agent": "fr-FR_ReneeV3Voice",
    "Employé": "fr-FR_NicolasV3Voice"
}


print(f"Processing started....")
combined = AudioSegment.empty()

# Generate and combine audio for each speaker
for speaker, text in transcription:
    response = tts_service.synthesize(
        text=text,
        voice=voices[speaker],
        accept='audio/wav'
    ).get_result()
    audio_segment = AudioSegment.from_file(io.BytesIO(response.content), format="wav")
    combined += audio_segment

# Save the combined audio file
combined_file = "combined_conversation.wav"
combined.export(combined_file, format="wav")

print(f"Processing ended!!")
print(f"Conversion completed. Check the '{combined_file}' file.")