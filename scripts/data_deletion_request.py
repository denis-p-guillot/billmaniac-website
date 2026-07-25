"""Data deletion request page copy for Bill Maniac (en, fr, es, id)."""

from __future__ import annotations

import json
import re
from typing import Any

from terms_of_service import ADDRESS, COMPANY, CONTACT, SUPPORT  # noqa: F401


def _section(title: str, content: str, items: list[str] | None = None) -> dict[str, Any]:
    s: dict[str, Any] = {"title": title, "content": content}
    if items:
        s["list"] = items
    return s


def _block(meta: dict[str, str], sections: list[dict[str, Any]]) -> str:
    lines = [
        f'            "title": {json.dumps(meta["title"], ensure_ascii=False)},',
        f'            "lastUpdated": {json.dumps(meta["lastUpdated"], ensure_ascii=False)},',
        '            "sections": [',
    ]
    for sec in sections:
        lines.append("                {")
        lines.append(
            f'                    "title": {json.dumps(sec["title"], ensure_ascii=False)},'
        )
        lines.append(
            f'                    "content": {json.dumps(sec["content"], ensure_ascii=False)}'
        )
        if sec.get("list"):
            lines.append(",")
            lines.append('                    "list": [')
            for item in sec["list"]:
                lines.append(
                    f'                        {json.dumps(item, ensure_ascii=False)},'
                )
            lines[-1] = lines[-1].rstrip(",")
            lines.append("                    ]")
        lines.append("                },")
    if lines[-1].endswith(","):
        lines[-1] = lines[-1][:-1]
    lines.append("            ],")
    lines.append(
        f'            "backToHome": {json.dumps(meta["backToHome"], ensure_ascii=False)}'
    )
    return "\n".join(lines)


DATA_DELETION_EN = _block(
    {
        "title": "Data deletion request",
        "lastUpdated": "Last updated",
        "backToHome": "Back to Home",
    },
    [
        _section(
            "1. Your right to delete your data",
            f"You can request deletion of your Bill Maniac account and associated personal data "
            f"at any time. {COMPANY} operates Bill Maniac (billmaniac.win, my.billmaniac.win, "
            f"and the Android app).",
        ),
        _section(
            "2. Delete from the app (recommended)",
            "If you can still sign in, use the in-app account deletion flow:",
            [
                "Open Bill Maniac and sign in.",
                "Go to My Account (account settings).",
                'Scroll to the danger zone and tap "Delete my account and data".',
                "Confirm the prompt.",
            ],
        ),
        _section(
            "3. What is deleted",
            "When deletion completes, we permanently remove:",
            [
                "Your user profile (name, email, PIN settings, preferences, and address if saved).",
                "All bill records linked to your account.",
                "Receipt images stored in your private cloud storage.",
                "Custom categories and vendors you created.",
            ],
        ),
        _section(
            "4. Request deletion by email",
            f"If you cannot access the app, email us from the address linked to your account:",
            [
                f"General & privacy requests: {CONTACT}",
                f"Support: {SUPPORT}",
            ],
        ),
        _section(
            "5. Email subject and information to include",
            "Use the subject line: Bill Maniac — data deletion request. In the message, include:",
            [
                "The email address registered on your Bill Maniac account.",
                "Your full name (as shown in the app), if known.",
                "A clear statement that you want your account and all associated data deleted.",
                "Optional: whether you use the web app, Android app, or both.",
            ],
        ),
        _section(
            "6. Processing time",
            "In-app deletion is processed immediately when you confirm in My Account. "
            "Email requests are handled within 30 days (usually much sooner). "
            "We may reply to verify your identity before deleting data.",
        ),
        _section(
            "7. Contact",
            f"{COMPANY}, {ADDRESS}. Questions about this page: {CONTACT} or {SUPPORT}.",
        ),
    ],
)

DATA_DELETION_FR = _block(
    {
        "title": "Demande de suppression des données",
        "lastUpdated": "Dernière mise à jour",
        "backToHome": "Retour à l'accueil",
    },
    [
        _section(
            "1. Votre droit de supprimer vos données",
            f"Vous pouvez demander la suppression de votre compte Bill Maniac et des données "
            f"associées à tout moment. {COMPANY} exploite Bill Maniac (billmaniac.win, "
            f"my.billmaniac.win et l'application Android).",
        ),
        _section(
            "2. Supprimer depuis l'application (recommandé)",
            "Si vous pouvez encore vous connecter, utilisez la suppression intégrée :",
            [
                "Ouvrez Bill Maniac et connectez-vous.",
                "Allez dans Mon compte (paramètres du compte).",
                'Descendez jusqu\'à la zone sensible et appuyez sur « Supprimer mon compte et mes données ».',
                "Confirmez la demande.",
            ],
        ),
        _section(
            "3. Ce qui est supprimé",
            "Une fois la suppression terminée, nous effaçons définitivement :",
            [
                "Votre profil (nom, e-mail, PIN, préférences et adresse enregistrée).",
                "Toutes les factures liées à votre compte.",
                "Les images de reçus stockées dans votre cloud privé.",
                "Les catégories et fournisseurs personnalisés que vous avez créés.",
            ],
        ),
        _section(
            "4. Demande par e-mail",
            f"Si vous ne pouvez pas accéder à l'application, écrivez-nous depuis l'adresse "
            f"associée à votre compte :",
            [
                f"Demandes générales & confidentialité : {CONTACT}",
                f"Support : {SUPPORT}",
            ],
        ),
        _section(
            "5. Objet et informations à inclure",
            "Objet : Bill Maniac — demande de suppression des données. Indiquez :",
            [
                "L'adresse e-mail enregistrée sur votre compte Bill Maniac.",
                "Votre nom complet (tel qu'affiché dans l'app), si connu.",
                "Une demande claire de suppression du compte et de toutes les données associées.",
                "Optionnel : application web, Android, ou les deux.",
            ],
        ),
        _section(
            "6. Délai de traitement",
            "La suppression dans l'application est traitée immédiatement après confirmation "
            "dans Mon compte. Les demandes par e-mail sont traitées sous 30 jours (souvent bien "
            "plus tôt). Nous pouvons vous contacter pour vérifier votre identité.",
        ),
        _section(
            "7. Contact",
            f"{COMPANY}, {ADDRESS}. Questions : {CONTACT} ou {SUPPORT}.",
        ),
    ],
)

DATA_DELETION_ES = _block(
    {
        "title": "Solicitud de eliminación de datos",
        "lastUpdated": "Última actualización",
        "backToHome": "Volver al inicio",
    },
    [
        _section(
            "1. Su derecho a eliminar sus datos",
            f"Puede solicitar la eliminación de su cuenta Bill Maniac y los datos asociados "
            f"en cualquier momento. {COMPANY} opera Bill Maniac (billmaniac.win, "
            f"my.billmaniac.win y la aplicación Android).",
        ),
        _section(
            "2. Eliminar desde la aplicación (recomendado)",
            "Si aún puede iniciar sesión, use el flujo integrado de eliminación:",
            [
                "Abra Bill Maniac e inicie sesión.",
                "Vaya a Mi cuenta (ajustes de la cuenta).",
                'Desplácese a la zona de riesgo y pulse «Eliminar mi cuenta y mis datos».',
                "Confirme la solicitud.",
            ],
        ),
        _section(
            "3. Qué se elimina",
            "Cuando finaliza la eliminación, borramos permanentemente:",
            [
                "Su perfil (nombre, correo, PIN, preferencias y dirección guardada).",
                "Todos los registros de facturas vinculados a su cuenta.",
                "Imágenes de recibos almacenadas en su nube privada.",
                "Categorías y proveedores personalizados que haya creado.",
            ],
        ),
        _section(
            "4. Solicitud por correo",
            f"Si no puede acceder a la app, escríbanos desde el correo vinculado a su cuenta:",
            [
                f"Solicitudes generales y privacidad: {CONTACT}",
                f"Soporte: {SUPPORT}",
            ],
        ),
        _section(
            "5. Asunto e información a incluir",
            "Asunto: Bill Maniac — solicitud de eliminación de datos. Incluya:",
            [
                "El correo registrado en su cuenta Bill Maniac.",
                "Su nombre completo (como aparece en la app), si lo conoce.",
                "Una solicitud clara de eliminar la cuenta y todos los datos asociados.",
                "Opcional: app web, Android, o ambas.",
            ],
        ),
        _section(
            "6. Plazo de procesamiento",
            "La eliminación en la app se procesa de inmediato al confirmar en Mi cuenta. "
            "Las solicitudes por correo se atienden en un plazo de 30 días (normalmente antes). "
            "Podemos responder para verificar su identidad.",
        ),
        _section(
            "7. Contacto",
            f"{COMPANY}, {ADDRESS}. Preguntas: {CONTACT} o {SUPPORT}.",
        ),
    ],
)

DATA_DELETION_ID = _block(
    {
        "title": "Permintaan penghapusan data",
        "lastUpdated": "Terakhir diperbarui",
        "backToHome": "Kembali ke beranda",
    },
    [
        _section(
            "1. Hak Anda untuk menghapus data",
            f"Anda dapat meminta penghapusan akun Bill Maniac dan data pribadi terkait "
            f"kapan saja. {COMPANY} mengoperasikan Bill Maniac (billmaniac.win, "
            f"my.billmaniac.win, dan aplikasi Android).",
        ),
        _section(
            "2. Hapus dari aplikasi (disarankan)",
            "Jika masih bisa masuk, gunakan alur penghapusan di aplikasi:",
            [
                "Buka Bill Maniac dan masuk.",
                "Buka Akun Saya (pengaturan akun).",
                'Gulir ke zona bahaya dan ketuk "Hapus akun dan data saya".',
                "Konfirmasi permintaan.",
            ],
        ),
        _section(
            "3. Data yang dihapus",
            "Setelah penghapusan selesai, kami hapus permanen:",
            [
                "Profil Anda (nama, email, PIN, preferensi, dan alamat jika disimpan).",
                "Semua catatan tagihan yang terhubung ke akun Anda.",
                "Gambar struk di cloud pribadi Anda.",
                "Kategori dan vendor kustom yang Anda buat.",
            ],
        ),
        _section(
            "4. Permintaan melalui email",
            f"Jika tidak bisa mengakses aplikasi, email kami dari alamat yang terdaftar di akun:",
            [
                f"Permintaan umum & privasi: {CONTACT}",
                f"Dukungan: {SUPPORT}",
            ],
        ),
        _section(
            "5. Subjek email dan informasi yang perlu disertakan",
            "Subjek: Bill Maniac — permintaan penghapusan data. Sertakan:",
            [
                "Alamat email terdaftar di akun Bill Maniac Anda.",
                "Nama lengkap (seperti di aplikasi), jika ada.",
                "Permintaan jelas untuk menghapus akun dan semua data terkait.",
                "Opsional: aplikasi web, Android, atau keduanya.",
            ],
        ),
        _section(
            "6. Waktu pemrosesan",
            "Penghapusan di aplikasi diproses segera setelah konfirmasi di Akun Saya. "
            "Permintaan email ditangani dalam 30 hari (biasanya lebih cepat). "
            "Kami dapat membalas untuk memverifikasi identitas Anda.",
        ),
        _section(
            "7. Kontak",
            f"{COMPANY}, {ADDRESS}. Pertanyaan: {CONTACT} atau {SUPPORT}.",
        ),
    ],
)

DATA_DELETION_BY_LANG = {
    "en": DATA_DELETION_EN,
    "fr": DATA_DELETION_FR,
    "es": DATA_DELETION_ES,
    "id": DATA_DELETION_ID,
}

FOOTER_NAV_DATA_DELETION = {
    "en": "Data deletion request",
    "fr": "Demande de suppression des données",
    "es": "Solicitud de eliminación de datos",
    "id": "Permintaan penghapusan data",
}


def patch_data_deletion_in_translations(raw: str) -> str:
    """Insert dataDeletion page copy and footer nav label for each language."""
    raw = raw.replace('\\"dataDeletion\\":', '"dataDeletion":')

    for lang, label in FOOTER_NAV_DATA_DELETION.items():
        pattern = (
            rf'("{lang}":\s*\{{[\s\S]*?"footer":\s*\{{[\s\S]*?"nav":\s*\{{[\s\S]*?)'
            rf'(                "terms": "[^"]+",\n)'
            rf'(                "technical":)'
        )
        replacement = rf'\1\2                "dataDeletion": {json.dumps(label, ensure_ascii=False)},\n\3'
        new_raw, count = re.subn(pattern, replacement, raw, count=1)
        if count != 1:
            raise SystemExit(
                f"Failed to patch footer nav dataDeletion for {lang!r} (matches={count})"
            )
        raw = new_raw

    for lang, block in DATA_DELETION_BY_LANG.items():
        pattern = (
            rf'("{lang}":\s*\{{[\s\S]*?)'
            rf'(        "terms":\s*\{{[\s\S]*?\n        \}},)'
            rf'(\n        "technical")'
        )
        replacement = (
            rf'\1\2\n        "dataDeletion": {{\n        {block}\n        }},\3'
        )
        new_raw, count = re.subn(pattern, replacement, raw, count=1)
        if count != 1:
            raise SystemExit(
                f"Failed to patch dataDeletion page for {lang!r} (matches={count})"
            )
        raw = new_raw

    return raw
