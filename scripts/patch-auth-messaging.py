#!/usr/bin/env python3
"""Update marketing copy: signup is not Google-only (email + optional Google)."""
from __future__ import annotations

import base64
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "dist" / "index.html"

# Old → new (exact substring matches in @/translations module)
REPLACEMENTS: list[tuple[str, str]] = [
    # Header buttons
    ('"signUp": "Sign Up with Google"', '"signUp": "Get Started"'),
    ('"signUp": "S\'inscrire avec Google"', '"signUp": "Commencer"'),
    ('"signUp": "Registrarse con Google"', '"signUp": "Empezar"'),
    ('"signUp": "Daftar dengan Google"', '"signUp": "Mulai"'),
    # Hero CTAs
    (
        '"cta": "Get Started for Free with Google"',
        '"cta": "Get Started for Free"',
    ),
    (
        '"cta": "Commencez gratuitement avec Google"',
        '"cta": "Commencez gratuitement"',
    ),
    (
        '"cta": "Empieza Gratis con Google"',
        '"cta": "Empieza gratis"',
    ),
    (
        '"cta": "Mulai Gratis dengan Google"',
        '"cta": "Mulai gratis"',
    ),
    # Bottom call-to-action
    (
        '"cta": "Sign Up with Google and Tame Your Spending"',
        '"cta": "Get Started and Tame Your Spending"',
    ),
    (
        '"cta": "Inscrivez-vous avec Google et maîtrisez vos dépenses"',
        '"cta": "Commencez et maîtrisez vos dépenses"',
    ),
    (
        '"cta": "Regístrate con Google y Domina Tus Gastos"',
        '"cta": "Empieza y domina tus gastos"',
    ),
    (
        '"cta": "Daftar dengan Google dan Jinakkan Pengeluaran Anda"',
        '"cta": "Mulai dan jinakkan pengeluaran Anda"',
    ),
    # How it works — step 1
    (
        '"description": "Sign in securely with Google. We never see your password — authentication is handled by Google OAuth."',
        '"description": "Create a free account with email, or continue with Google. We never see your Google password — email uses a verification code."',
    ),
    (
        '"description": "Connectez-vous en toute sécurité avec Google. Nous ne voyons jamais votre mot de passe — l\'authentification est gérée par Google OAuth."',
        '"description": "Créez un compte gratuit par e-mail, ou continuez avec Google. Nous ne voyons jamais votre mot de passe Google — l\'e-mail utilise un code de vérification."',
    ),
    (
        '"description": "Masuk dengan aman menggunakan Google. Kami tidak pernah melihat kata sandi Anda — autentikasi ditangani oleh Google OAuth."',
        '"description": "Buat akun gratis dengan email, atau lanjutkan dengan Google. Kami tidak pernah melihat kata sandi Google Anda — email menggunakan kode verifikasi."',
    ),
    # Android page note
    (
        '"note": "Android APK / Play listing coming soon. Sign in on web today with the same Google account you\'ll use on Android."',
        '"note": "Android APK / Play listing coming soon. Sign in on web today with email or Google — the same account works on Android."',
    ),
    (
        '"note": "APK / fiche Play bientôt disponibles. Connectez-vous dès maintenant sur le web avec le compte Google que vous utiliserez sur Android."',
        '"note": "APK / fiche Play bientôt disponibles. Connectez-vous sur le web par e-mail ou Google — le même compte fonctionne sur Android."',
    ),
    (
        '"note": "APK / ficha de Play próximamente. Inicia sesión hoy en la web con la cuenta de Google que usarás en Android."',
        '"note": "APK / ficha de Play próximamente. Inicia sesión en la web con correo o Google — la misma cuenta funciona en Android."',
    ),
    (
        '"note": "APK Android / listing Play segera hadir. Masuk di web hari ini dengan akun Google yang sama yang akan Anda gunakan di Android."',
        '"note": "APK Android / listing Play segera hadir. Masuk di web dengan email atau Google — akun yang sama berfungsi di Android."',
    ),
    # Blog — step 1 headings
    (
        '"text": "Step 1: Sign Up with Your Google Account (1 Minute)"',
        '"text": "Step 1: Create Your Account (1 Minute)"',
    ),
    (
        '"text": "Étape 1 : Inscrivez-vous avec votre compte Google (1 minute)"',
        '"text": "Étape 1 : Créez votre compte (1 minute)"',
    ),
    (
        '"text": "Paso 1: Regístrate con tu cuenta de Google (1 minuto)"',
        '"text": "Paso 1: Crea tu cuenta (1 minuto)"',
    ),
    (
        '"text": "Langkah 1: Daftar dengan Akun Google Anda (1 Menit)"',
        '"text": "Langkah 1: Buat Akun Anda (1 Menit)"',
    ),
    # Blog — step 1 body
    (
        '"text": "The first step is the easiest. On our homepage, click the \'Sign Up with Google\' or \'Get Started for Free\' button. This will open a standard Google authentication window."',
        '"text": "The first step is the easiest. On our homepage, click \'Get Started\' to open the app. Sign up with your email (we send a verification code) or choose Continue with Google if you prefer."',
    ),
    (
        '"text": "La première étape est la plus simple. Sur notre page d\'accueil, cliquez sur le bouton \'S\'inscrire avec Google\' ou \'Commencer gratuitement\'. Cela ouvrira une fenêtre d\'authentification Google standard."',
        '"text": "La première étape est la plus simple. Sur notre page d\'accueil, cliquez sur « Commencer » pour ouvrir l\'application. Inscrivez-vous par e-mail (code de vérification) ou choisissez Continuer avec Google."',
    ),
    (
        '"text": "El primer paso es el más fácil. En nuestra página de inicio, haz clic en el botón \'Registrarse con Google\' o \'Empezar Gratis\'. Esto abrirá una ventana de autenticación estándar de Google."',
        '"text": "El primer paso es el más fácil. En la página de inicio, haz clic en « Empezar » para abrir la app. Regístrate con correo (código de verificación) o elige Continuar con Google."',
    ),
    (
        '"text": "Langkah pertama adalah yang termudah. Di beranda kami, klik tombol \'Daftar dengan Google\' atau \'Mulai Gratis\'. Ini akan membuka jendela autentikasi Google standar."',
        '"text": "Langkah pertama adalah yang termudah. Di beranda, klik « Mulai » untuk membuka aplikasi. Daftar dengan email (kode verifikasi) atau pilih Lanjutkan dengan Google."',
    ),
    # Blog — account association paragraph
    (
        '"text": "Choose the Google account you want to associate with BillManiac. You\'ll sign in with Google to create your account. Your bills and receipts are stored in your private Bill Maniac cloud — export anytime. That\'s our \'You Own Your Data\' philosophy."',
        '"text": "Enter your email or pick a Google account. Your bills and receipts are stored in your private Bill Maniac cloud — export anytime. That\'s our \'You Own Your Data\' philosophy."',
    ),
    (
        '"text": "Choisissez le compte Google que vous souhaitez associer à BillManiac. Vous vous connectez avec Google pour créer votre compte. Vos données vivent dans votre cloud Bill Maniac privé — exportables à tout moment. C\'est notre philosophie \'Vous êtes propriétaire de vos données\'."',
        '"text": "Saisissez votre e-mail ou choisissez un compte Google. Vos données vivent dans votre cloud Bill Maniac privé — exportables à tout moment. C\'est notre philosophie « Vous êtes propriétaire de vos données »."',
    ),
    (
        '"text": "Elige la cuenta de Google que deseas asociar con BillManiac. Se te iniciarás sesión con Google para crear tu cuenta. Tus datos viven en tu nube privada Bill Maniac — exportables cuando quieras. Ese es el núcleo de nuestra filosofía \'Tú eres el dueño de tus datos\'."',
        '"text": "Introduce tu correo o elige una cuenta de Google. Tus datos viven en tu nube privada Bill Maniac — exportables cuando quieras. Ese es el núcleo de nuestra filosofía « Tú eres el dueño de tus datos »."',
    ),
    (
        '"text": "Pilih akun Google yang ingin Anda kaitkan dengan BillManiac. Anda masuk dengan Google untuk membuat akun. Tagihan dan struk disimpan di cloud pribadi Bill Maniac Anda — ekspor kapan saja. Itulah filosofi kami: \'Anda Memiliki Data Anda\'."',
        '"text": "Masukkan email Anda atau pilih akun Google. Tagihan dan struk disimpan di cloud pribadi Bill Maniac — ekspor kapan saja. Itulah filosofi kami: « Anda Memiliki Data Anda »."',
    ),
    # Blog — security paragraph (email + Google)
    (
        '"text": "Absolutely. We use Google\'s secure OAuth 2.0 protocol, which means we never see or store your password. We only request permission to create your private Bill Maniac cloud account only. We cannot access your Gmail, other Drive files, or unrelated Google data."',
        '"text": "Absolutely. Email sign-up uses a one-time verification code — we never store a password. Google sign-in uses OAuth 2.0, so we never see your Google password either. Your data stays in your private Bill Maniac cloud only."',
    ),
    (
        '"text": "Absolument. Nous utilisons le protocole OAuth 2.0 sécurisé de Google, ce qui signifie que nous ne voyons ni ne stockons jamais votre mot de passe. Nous ne demandons que votre compte cloud privé Bill Maniac uniquement. Nous ne pouvons accéder à aucun de vos autres fichiers, documents ou e-mails."',
        '"text": "Absolument. L\'inscription par e-mail utilise un code de vérification — nous ne stockons pas de mot de passe. Google utilise OAuth 2.0 : nous ne voyons jamais votre mot de passe Google. Vos données restent dans votre cloud Bill Maniac privé."',
    ),
    (
        '"text": "Absolutamente. Usamos el protocolo seguro OAuth 2.0 de Google, lo que significa que nunca vemos ni almacenamos tu contraseña. Solo solictu cuenta cloud privada Bill Maniac únicamente. No podemos acceder a ninguno de tus otros archivos, documentos o correos electrónicos."',
        '"text": "Absolutamente. El registro por correo usa un código de verificación — no guardamos contraseña. Google usa OAuth 2.0: nunca vemos tu contraseña de Google. Tus datos permanecen solo en tu nube privada Bill Maniac."',
    ),
    (
        '"text": "Tentu saja. Kami menggunakan protokol OAuth 2.0 yang aman dari Google, yang berarti kami tidak pernah melihat atau menyimpan kata sandi Anda. Kami hanya meminta izin untuk membuat akun cloud pribadi Bill Maniac Anda. Kami tidak dapat mengakses Gmail, file Drive lain, atau data Google yang tidak terkait."',
        '"text": "Tentu saja. Pendaftaran email memakai kode verifikasi — kami tidak menyimpan kata sandi. Google memakai OAuth 2.0 sehingga kami tidak pernah melihat kata sandi Google Anda. Data Anda hanya di cloud pribadi Bill Maniac."',
    ),
    # Blog — wizard redirect
    (
        '"text": "Once you\'ve granted permission, you\'ll be redirected to the BillManiac app and greeted by our onboarding wizard. This is where the magic happens automatically."',
        '"text": "Once you\'re signed in, you\'ll enter the BillManiac app and our onboarding wizard. This is where the magic happens automatically."',
    ),
    (
        '"text": "Une fois que vous avez accordé l\'autorisation, vous serez redirigé vers l\'application BillManiac et accueilli par notre assistant d\'intégration. C\'est là que la magie opère automatiquement."',
        '"text": "Une fois connecté, vous entrez dans l\'application BillManiac et notre assistant d\'intégration. C\'est là que la magie opère automatiquement."',
    ),
    (
        '"text": "Una vez que hayas otorgado el permiso, serás redirigido a la aplicación BillManiac y recibido por nuestro asistente de incorporación. Aquí es donde la magia ocurre automáticamente."',
        '"text": "Una vez iniciada la sesión, entrarás en la aplicación BillManiac y nuestro asistente de incorporación. Aquí es donde ocurre la magia automáticamente."',
    ),
    (
        '"text": "Setelah Anda memberikan izin, Anda akan dialihkan ke aplikasi BillManiac dan disambut oleh wizard onboarding kami. Di sinilah keajaiban terjadi secara otomatis."',
        '"text": "Setelah masuk, Anda akan masuk ke aplikasi BillManiac dan wizard onboarding kami. Di sinilah keajaiban terjadi secara otomatis."',
    ),
    # Blog — wizard bullet
    (
        '"Create your Bill Maniac account with Google sign-in. Your secure cloud database is provisioned automatically."',
        '"Create your Bill Maniac account with email or Google. Your secure cloud database is provisioned automatically."',
    ),
    (
        '"Créez votre compte Bill Maniac avec Google. Votre base cloud sécurisée est provisionnée automatiquement."',
        '"Créez votre compte Bill Maniac par e-mail ou Google. Votre base cloud sécurisée est provisionnée automatiquement."',
    ),
    (
        '"Creará utu cuenta Bill Maniac con Google. Tu base cloud segura se provisiona automáticamente."',
        '"Creará tu cuenta Bill Maniac con correo o Google. Tu base cloud segura se provisiona automáticamente."',
    ),
    (
        '"Membuat akun Bill Maniac Anda dengan Google sign-in. Database cloud aman Anda disiapkan secara otomatis."',
        '"Membuat akun Bill Maniac Anda dengan email atau Google. Database cloud aman Anda disiapkan secara otomatis."',
    ),
]


def patch_translations_src(raw: str) -> str:
    for old, new in REPLACEMENTS:
        if old not in raw:
            raise SystemExit(f"Missing expected string:\n{old[:120]}...")
        raw = raw.replace(old, new, 1)
    return raw


def main() -> None:
    html = INDEX.read_text()
    m = re.search(r'(<script type="importmap">)(.*?)(</script>)', html, re.S)
    if not m:
        raise SystemExit("importmap not found")
    imap = json.loads(m.group(2))
    key = "@/translations"
    src = base64.b64decode(imap["imports"][key].split(",", 1)[1]).decode("utf-8")
    patched = patch_translations_src(src)
    imap["imports"][key] = (
        "data:application/javascript;base64,"
        + base64.b64encode(patched.encode("utf-8")).decode("ascii")
    )
    out = json.dumps(imap, separators=(",", ":"))
    INDEX.write_text(html[: m.start()] + m.group(1) + out + m.group(3) + html[m.end() :])
    print("Patched auth messaging in", INDEX)


if __name__ == "__main__":
    main()
