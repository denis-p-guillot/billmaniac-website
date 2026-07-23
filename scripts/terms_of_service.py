"""Standard Terms of Service copy for Bill Maniac (en, fr, es, id)."""

from __future__ import annotations

import json
import re
from typing import Any


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


COMPANY = "PT. DEVINCI GROUP INDONESIA"
CONTACT = "contact@billmaniac.win"
BILLING = "billing@billmaniac.win"
SUPPORT = "support@billmaniac.win"
ADDRESS = (
    "Menara Ravindo, Lantai 12, Jl. Kebon Sirih Kav. 75, "
    "RT 001/RW 001, Kelurahan Kebon Sirih, Kecamatan Menteng, "
    "Jakarta Pusat 10340, DKI Jakarta, Indonesia"
)

TERMS_EN = _block(
    {
        "title": "Terms of Service",
        "lastUpdated": "Last updated",
        "backToHome": "Back to Home",
    },
    [
        _section(
            "1. Agreement to Terms",
            f'By accessing or using Bill Maniac (the "Service"), including the website at billmaniac.win, '
            f'the web app at my.billmaniac.win, and the Android app, you agree to these Terms of Service. '
            f"If you do not agree, do not use the Service.",
        ),
        _section(
            "2. Operator",
            f"The Service is operated by {COMPANY}, registered in Indonesia, with office at {ADDRESS}. "
            f"Bill Maniac is a product for personal and business expense tracking, receipt scanning, "
            f"analytics, and exports.",
        ),
        _section(
            "3. Service Description",
            "Bill Maniac lets you sign in with Google, store bills and receipt images in a private "
            "Bill Maniac Pro cloud (Cloudflare D1 database and R2 object storage), scan receipts with AI "
            "OCR, analyze spending, and export CSV/Excel reports. Features and limits depend on your plan "
            "(Free, Pro, or Maniac).",
        ),
        _section(
            "4. Eligibility & Accounts",
            "You must be at least 16 years old and able to enter a binding contract. You are responsible "
            "for your Google account credentials, device security (including PIN or biometrics where "
            "enabled), and all activity under your Bill Maniac account. Keep your contact email accurate.",
        ),
        _section(
            "5. Acceptable Use",
            "You agree not to misuse the Service. Without limiting other remedies, you must not:",
            [
                "Use the Service for unlawful, fraudulent, or abusive purposes.",
                "Upload malware, attempt unauthorized access, or interfere with the Service or other users.",
                "Reverse engineer, scrape, or resell the Service except as allowed by law.",
                "Upload content you do not have the right to store or process.",
            ],
        ),
        _section(
            "6. Subscriptions, Fees & Payment",
            "Paid plans (Pro and Maniac) are billed yearly unless stated otherwise. Prices are shown on "
            "billmaniac.win and may change for new purchases; we will not reduce your paid term mid-cycle "
            "without notice. Checkout may be completed by email or WhatsApp with manual payment confirmation. "
            "Unless required by law, fees are non-refundable once the paid term has started. If you cancel, "
            "paid features remain until the end of the billing period, then your account reverts to Free. "
            "Your data remains exportable regardless of plan.",
        ),
        _section(
            "7. AI, OCR & Financial Information",
            "Receipt scanning and categorization may use automated and AI-assisted processing. Results "
            "can contain errors. Bill Maniac is a record-keeping and analysis tool, not accounting, tax, "
            "or legal advice. You are responsible for verifying amounts, categories, and compliance with "
            "your tax or corporate rules before relying on exports or reports.",
        ),
        _section(
            "8. Your Data & Privacy",
            "You retain ownership of the expense records and receipt files you upload. We process data "
            "to provide the Service as described in our Privacy Policy at billmaniac.win/privacy. "
            "You can export your data and may request account deletion by contacting us. We do not sell "
            "your personal data.",
        ),
        _section(
            "9. Intellectual Property",
            f"{COMPANY} and its licensors own the Bill Maniac name, branding, software, and documentation. "
            "You receive a limited, non-exclusive, non-transferable license to use the Service for your "
            "internal expense management while your account is in good standing.",
        ),
        _section(
            "10. Third-Party Services",
            "The Service integrates with third parties such as Google (sign-in), Cloudflare (hosting and "
            "storage), and AI/OCR providers. Their terms and privacy policies apply to those services. "
            "We are not responsible for outages or changes made by third parties outside our control.",
        ),
        _section(
            "11. Disclaimers",
            'THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE." TO THE MAXIMUM EXTENT PERMITTED BY LAW, '
            f"{COMPANY} DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING MERCHANTABILITY, FITNESS "
            "FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. We do not guarantee uninterrupted or error-free "
            "operation.",
        ),
        _section(
            "12. Limitation of Liability",
            f"TO THE MAXIMUM EXTENT PERMITTED BY LAW, {COMPANY} AND ITS OFFICERS, EMPLOYEES, AND PARTNERS "
            "WILL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, "
            "OR ANY LOSS OF DATA, PROFITS, OR GOODWILL, ARISING FROM YOUR USE OF THE SERVICE. OUR TOTAL "
            "LIABILITY FOR ANY CLAIM RELATING TO THE SERVICE IN A TWELVE-MONTH PERIOD IS LIMITED TO THE "
            "AMOUNT YOU PAID US FOR THE SERVICE IN THAT PERIOD, OR USD $50 IF YOU USE THE FREE PLAN.",
        ),
        _section(
            "13. Indemnification",
            "You agree to indemnify and hold harmless "
            f"{COMPANY} from claims, damages, and expenses (including reasonable legal fees) arising from "
            "your use of the Service, your content, or your violation of these Terms.",
        ),
        _section(
            "14. Suspension & Termination",
            "We may suspend or terminate access if you breach these Terms, if required by law, or to protect "
            "the Service. You may stop using the Service at any time. Sections that by nature should survive "
            "(including disclaimers, liability limits, and governing law) remain in effect after termination.",
        ),
        _section(
            "15. Changes to These Terms",
            "We may update these Terms from time to time. Material changes will be posted on this page with "
            "an updated date. Continued use after changes take effect constitutes acceptance. If you do not "
            "agree, stop using the Service and contact us to close your account.",
        ),
        _section(
            "16. Governing Law & Disputes",
            "These Terms are governed by the laws of the Republic of Indonesia, without regard to conflict-of-law "
            "rules. Courts in Jakarta, Indonesia have exclusive jurisdiction, unless mandatory consumer protection "
            "law in your country requires otherwise.",
        ),
        _section(
            "17. Contact",
            f"Questions about these Terms: {CONTACT} (general), {BILLING} (billing), {SUPPORT} (support). "
            f"{COMPANY}, {ADDRESS}.",
        ),
    ],
)

TERMS_FR = _block(
    {
        "title": "Conditions d'utilisation",
        "lastUpdated": "Dernière mise à jour",
        "backToHome": "Retour à l'accueil",
    },
    [
        _section(
            "1. Acceptation des conditions",
            'En accédant ou en utilisant Bill Maniac (le « Service »), y compris le site billmaniac.win, '
            "l'application web my.billmaniac.win et l'application Android, vous acceptez ces Conditions "
            "d'utilisation. Si vous n'êtes pas d'accord, n'utilisez pas le Service.",
        ),
        _section(
            "2. Exploitant",
            f"Le Service est exploité par {COMPANY}, enregistrée en Indonésie, avec un bureau au {ADDRESS}. "
            "Bill Maniac est un produit de suivi des dépenses, scan de reçus, analytique et exports.",
        ),
        _section(
            "3. Description du service",
            "Bill Maniac vous permet de vous connecter avec Google, de stocker factures et images de reçus "
            "dans un cloud privé Bill Maniac Pro (base Cloudflare D1 et stockage R2), de scanner des reçus "
            "par OCR/IA, d'analyser vos dépenses et d'exporter des rapports CSV/Excel. Les fonctionnalités "
            "dépendent de votre offre (Free, Pro ou Maniac).",
        ),
        _section(
            "4. Éligibilité et comptes",
            "Vous devez avoir au moins 16 ans et la capacité juridique de contracter. Vous êtes responsable "
            "de vos identifiants Google, de la sécurité de vos appareils (PIN/biométrie le cas échéant) et "
            "de toute activité sur votre compte Bill Maniac.",
        ),
        _section(
            "5. Utilisation acceptable",
            "Vous vous engagez à ne pas faire un usage abusif du Service. Notamment, vous ne devez pas :",
            [
                "Utiliser le Service à des fins illégales, frauduleuses ou abusives.",
                "Téléverser des malwares, tenter un accès non autorisé ou perturber le Service.",
                "Désosser, scraper ou revendre le Service sauf si la loi l'autorise.",
                "Téléverser du contenu que vous n'avez pas le droit de stocker ou traiter.",
            ],
        ),
        _section(
            "6. Abonnements, tarifs et paiement",
            "Les offres payantes (Pro et Maniac) sont facturées annuellement sauf indication contraire. "
            "Les prix sont affichés sur billmaniac.win. Le paiement peut se faire par e-mail ou WhatsApp "
            "avec confirmation manuelle. Sauf obligation légale, les frais ne sont pas remboursables une "
            "fois la période payée commencée. En cas d'annulation, les fonctions payantes restent jusqu'à "
            "la fin de la période, puis le compte repasse en Free. Vos données restent exportables.",
        ),
        _section(
            "7. IA, OCR et informations financières",
            "Le scan et la catégorisation peuvent utiliser des traitements automatisés et assistés par IA. "
            "Des erreurs sont possibles. Bill Maniac est un outil de tenue de registres, pas un conseil "
            "comptable, fiscal ou juridique. Vous devez vérifier montants et catégories avant de vous fier "
            "aux exports.",
        ),
        _section(
            "8. Vos données et confidentialité",
            "Vous conservez la propriété de vos enregistrements et fichiers. Nous traitons les données "
            "comme décrit dans notre Politique de confidentialité (billmaniac.win/privacy). Vous pouvez "
            "exporter vos données et demander la suppression du compte. Nous ne vendons pas vos données.",
        ),
        _section(
            "9. Propriété intellectuelle",
            f"{COMPANY} et ses concédants détiennent la marque Bill Maniac, le logiciel et la documentation. "
            "Vous recevez une licence limitée, non exclusive et non transférable pour un usage interne de "
            "gestion des dépenses.",
        ),
        _section(
            "10. Services tiers",
            "Le Service s'appuie sur des tiers (Google, Cloudflare, fournisseurs IA/OCR). Leurs conditions "
            "s'appliquent. Nous ne sommes pas responsables des interruptions ou changements hors de notre "
            "contrôle.",
        ),
        _section(
            "11. Exclusions de garantie",
            'LE SERVICE EST FOURNI « EN L\'ÉTAT » ET « SELON DISPONIBILITÉ ». DANS LA LIMITE PERMISE PAR LA LOI, '
            f"{COMPANY} EXCLUT TOUTE GARANTIE, EXPRESSE OU IMPLICITE.",
        ),
        _section(
            "12. Limitation de responsabilité",
            f"DANS LA LIMITE PERMISE PAR LA LOI, {COMPANY} NE SERA PAS RESPONSABLE DES DOMMAGES INDIRECTS, "
            "ACCESSOIRES, SPÉCIAUX OU CONSÉCUTIFS, NI DES PERTES DE DONNÉES OU DE PROFITS. NOTRE RESPONSABILITÉ "
            "TOTALE SUR DOUZE MOIS EST LIMITÉE AU MONTANT PAYÉ POUR LE SERVICE, OU 50 USD EN OFFRE GRATUITE.",
        ),
        _section(
            "13. Indemnisation",
            f"Vous indemnisez {COMPANY} contre les réclamations liées à votre utilisation, votre contenu ou "
            "une violation de ces Conditions.",
        ),
        _section(
            "14. Suspension et résiliation",
            "Nous pouvons suspendre ou résilier l'accès en cas de violation, obligation légale ou protection "
            "du Service. Les clauses devant survivre (garanties, responsabilité, droit applicable) restent "
            "en vigueur.",
        ),
        _section(
            "15. Modifications",
            "Nous pouvons mettre à jour ces Conditions sur cette page. L'utilisation continue vaut acceptation.",
        ),
        _section(
            "16. Droit applicable et litiges",
            "Ces Conditions sont régies par le droit indonésien. Les tribunaux de Jakarta ont compétence "
            "exclusive, sauf droit impératif contraire du consommateur.",
        ),
        _section(
            "17. Contact",
            f"Questions : {CONTACT}, facturation {BILLING}, support {SUPPORT}. {COMPANY}, {ADDRESS}.",
        ),
    ],
)

TERMS_ES = _block(
    {
        "title": "Términos de Servicio",
        "lastUpdated": "Última actualización",
        "backToHome": "Volver al Inicio",
    },
    [
        _section(
            "1. Aceptación de los términos",
            'Al acceder o usar Bill Maniac (el "Servicio"), incluido billmaniac.win, la app web my.billmaniac.win '
            "y la app Android, aceptas estos Términos de Servicio. Si no estás de acuerdo, no uses el Servicio.",
        ),
        _section(
            "2. Operador",
            f"El Servicio es operado por {COMPANY}, registrada en Indonesia, con oficina en {ADDRESS}. "
            "Bill Maniac es un producto de seguimiento de gastos, escaneo de recibos, analítica y exportaciones.",
        ),
        _section(
            "3. Descripción del servicio",
            "Bill Maniac permite iniciar sesión con Google, almacenar facturas e imágenes en un cloud privado "
            "Bill Maniac Pro (base Cloudflare D1 y almacenamiento R2), escanear recibos con OCR/IA, analizar "
            "gastos y exportar informes CSV/Excel. Las funciones dependen de tu plan (Free, Pro o Maniac).",
        ),
        _section(
            "4. Elegibilidad y cuentas",
            "Debes tener al menos 16 años y capacidad legal para contratar. Eres responsable de tus credenciales "
            "de Google, la seguridad del dispositivo (PIN/biometría) y toda actividad en tu cuenta.",
        ),
        _section(
            "5. Uso aceptable",
            "Te comprometes a no hacer un uso indebido del Servicio. En particular, no debes:",
            [
                "Usar el Servicio con fines ilegales, fraudulentos o abusivos.",
                "Subir malware, intentar acceso no autorizado o interferir con el Servicio.",
                "Realizar ingeniería inversa, scraping o reventa del Servicio salvo lo permitido por ley.",
                "Subir contenido que no tengas derecho a almacenar o procesar.",
            ],
        ),
        _section(
            "6. Suscripciones, tarifas y pago",
            "Los planes de pago (Pro y Maniac) se facturan anualmente salvo indicación contraria. Los precios "
            "se muestran en billmaniac.win. El checkout puede completarse por correo o WhatsApp con confirmación "
            "manual. Salvo obligación legal, las tarifas no son reembolsables una vez iniciado el periodo pagado. "
            "Si cancelas, conservas funciones de pago hasta el final del periodo y luego vuelves a Free. "
            "Tus datos siguen exportables.",
        ),
        _section(
            "7. IA, OCR e información financiera",
            "El escaneo y categorización pueden usar procesamiento automatizado y asistido por IA. Puede haber "
            "errores. Bill Maniac es una herramienta de registro, no asesoramiento contable, fiscal o legal. "
            "Debes verificar importes y categorías antes de confiar en exportaciones.",
        ),
        _section(
            "8. Tus datos y privacidad",
            "Conservas la propiedad de tus registros y archivos. Procesamos datos según la Política de Privacidad "
            "en billmaniac.win/privacy. Puedes exportar datos y solicitar eliminación de cuenta. No vendemos "
            "tus datos personales.",
        ),
        _section(
            "9. Propiedad intelectual",
            f"{COMPANY} y sus licenciantes poseen la marca Bill Maniac, el software y la documentación. "
            "Recibes una licencia limitada, no exclusiva e intransferible para gestión interna de gastos.",
        ),
        _section(
            "10. Servicios de terceros",
            "El Servicio integra terceros como Google, Cloudflare y proveedores de IA/OCR. Sus términos aplican. "
            "No somos responsables de interrupciones fuera de nuestro control.",
        ),
        _section(
            "11. Exenciones de garantía",
            'EL SERVICIO SE PROPORCIONA "TAL CUAL" Y "SEGÚN DISPONIBILIDAD". EN LA MEDIDA PERMITIDA POR LA LEY, '
            f"{COMPANY} RECHAZA TODAS LAS GARANTÍAS, EXPRESAS O IMPLÍCITAS.",
        ),
        _section(
            "12. Limitación de responsabilidad",
            f"EN LA MEDIDA PERMITIDA POR LA LEY, {COMPANY} NO SERÁ RESPONSABLE DE DAÑOS INDIRECTOS, INCIDENTALES, "
            "ESPECIALES O CONSECUENTES, NI PÉRDIDA DE DATOS O BENEFICIOS. LA RESPONSABILIDAD TOTAL EN DOCE MESES "
            "SE LIMITA AL IMPORTE PAGADO POR EL SERVICIO, O 50 USD EN EL PLAN GRATUITO.",
        ),
        _section(
            "13. Indemnización",
            f"Indemnizas a {COMPANY} frente a reclamaciones derivadas de tu uso, tu contenido o incumplimiento "
            "de estos Términos.",
        ),
        _section(
            "14. Suspensión y terminación",
            "Podemos suspender o terminar el acceso por incumplimiento, obligación legal o protección del Servicio. "
            "Las cláusulas que deban sobrevivir permanecen vigentes.",
        ),
        _section(
            "15. Cambios en estos términos",
            "Podemos actualizar estos Términos en esta página. El uso continuado implica aceptación.",
        ),
        _section(
            "16. Ley aplicable y disputas",
            "Estos Términos se rigen por las leyes de la República de Indonesia. Los tribunales de Yakarta "
            "tienen jurisdicción exclusiva, salvo ley imperativa del consumidor.",
        ),
        _section(
            "17. Contacto",
            f"Preguntas: {CONTACT}, facturación {BILLING}, soporte {SUPPORT}. {COMPANY}, {ADDRESS}.",
        ),
    ],
)

TERMS_ID = _block(
    {
        "title": "Ketentuan Layanan",
        "lastUpdated": "Terakhir diperbarui",
        "backToHome": "Kembali ke Beranda",
    },
    [
        _section(
            "1. Persetujuan terhadap Ketentuan",
            'Dengan mengakses atau menggunakan Bill Maniac ("Layanan"), termasuk billmaniac.win, aplikasi web '
            "my.billmaniac.win, dan aplikasi Android, Anda setuju dengan Ketentuan Layanan ini. Jika tidak "
            "setuju, jangan gunakan Layanan.",
        ),
        _section(
            "2. Penyedia Layanan",
            f"Layanan dioperasikan oleh {COMPANY}, terdaftar di Indonesia, dengan kantor di {ADDRESS}. "
            "Bill Maniac adalah produk pelacakan pengeluaran, pemindaian struk, analitik, dan ekspor.",
        ),
        _section(
            "3. Deskripsi Layanan",
            "Bill Maniac memungkinkan masuk dengan Google, menyimpan tagihan dan gambar struk di cloud pribadi "
            "Bill Maniac Pro (database Cloudflare D1 dan penyimpanan R2), memindai struk dengan OCR/AI, "
            "menganalisis pengeluaran, dan mengekspor laporan CSV/Excel. Fitur bergantung pada paket "
            "(Free, Pro, atau Maniac).",
        ),
        _section(
            "4. Kelayakan & Akun",
            "Anda harus berusia minimal 16 tahun dan mampu membuat kontrak yang mengikat. Anda bertanggung jawab "
            "atas kredensial Google, keamanan perangkat (PIN/biometrik), dan semua aktivitas di akun Bill Maniac.",
        ),
        _section(
            "5. Penggunaan yang Diperbolehkan",
            "Anda setuju untuk tidak menyalahgunakan Layanan. Secara khusus, Anda dilarang:",
            [
                "Menggunakan Layanan untuk tujuan ilegal, penipuan, atau penyalahgunaan.",
                "Mengunggah malware, mencoba akses tanpa izin, atau mengganggu Layanan.",
                "Melakukan reverse engineering, scraping, atau menjual kembali Layanan kecuali diizinkan hukum.",
                "Mengunggah konten yang tidak berhak Anda simpan atau proses.",
            ],
        ),
        _section(
            "6. Langganan, Biaya & Pembayaran",
            "Paket berbayar (Pro dan Maniac) ditagih tahunan kecuali dinyatakan lain. Harga ditampilkan di "
            "billmaniac.win. Checkout dapat diselesaikan melalui email atau WhatsApp dengan konfirmasi manual. "
            "Kecuali diwajibkan hukum, biaya tidak dapat dikembalikan setelah periode berbayar dimulai. "
            "Jika dibatalkan, fitur berbayar tetap hingga akhir periode lalu akun kembali ke Free. "
            "Data Anda tetap dapat diekspor.",
        ),
        _section(
            "7. AI, OCR & Informasi Keuangan",
            "Pemindaian dan kategorisasi struk dapat menggunakan pemrosesan otomatis dan AI. Hasil dapat "
            "salah. Bill Maniac adalah alat pencatatan, bukan nasihat akuntansi, pajak, atau hukum. "
            "Anda wajib memverifikasi jumlah dan kategori sebelum mengandalkan ekspor.",
        ),
        _section(
            "8. Data Anda & Privasi",
            "Anda memiliki catatan pengeluaran dan file yang diunggah. Kami memproses data sesuai Kebijakan "
            "Privasi di billmaniac.win/privacy. Anda dapat mengekspor data dan meminta penghapusan akun. "
            "Kami tidak menjual data pribadi Anda.",
        ),
        _section(
            "9. Kekayaan Intelektual",
            f"{COMPANY} dan pemberi lisensinya memiliki merek Bill Maniac, perangkat lunak, dan dokumentasi. "
            "Anda mendapat lisensi terbatas, non-eksklusif, dan tidak dapat dialihkan untuk pengelolaan "
            "pengeluaran internal.",
        ),
        _section(
            "10. Layanan Pihak Ketiga",
            "Layanan terintegrasi dengan pihak ketiga seperti Google, Cloudflare, dan penyedia AI/OCR. "
            "Ketentuan mereka berlaku. Kami tidak bertanggung jawab atas gangguan di luar kendali kami.",
        ),
        _section(
            "11. Penafian",
            'LAYANAN DISEDIAKAN "SEBAGAIMANA ADANYA" DAN "SEBAGAIMANA TERSEDIA." SEJAUH DIIZINKAN HUKUM, '
            f"{COMPANY} MENOLAK SEMUA JAMINAN, TERSURAT MAUPUN TERSIRAT.",
        ),
        _section(
            "12. Batasan Tanggung Jawab",
            f"SEJAUH DIIZINKAN HUKUM, {COMPANY} TIDAK BERTANGGUNG JAWAB ATAS KERUSAKAN TIDAK LANGSUNG, "
            "INSIDENTAL, KHUSUS, ATAU KONSEKUENSIAL, ATAU KEHILANGAN DATA ATAU KEUNTUNGAN. TOTAL "
            "TANGGUNG JAWAB KAMI DALAM DUABELAS BULAN TERBATAS PADA JUMLAH YANG ANDA BAYARKAN, "
            "ATAU USD $50 UNTUK PAKET GRATIS.",
        ),
        _section(
            "13. Ganti Rugi",
            f"Anda setuju mengganti rugi {COMPANY} atas klaim yang timbul dari penggunaan Anda, konten Anda, "
            "atau pelanggaran Ketentuan ini.",
        ),
        _section(
            "14. Penangguhan & Penghentian",
            "Kami dapat menangguhkan atau menghentikan akses jika Anda melanggar Ketentuan, jika diwajibkan "
            "hukum, atau untuk melindungi Layanan. Ketentuan yang secara wajar harus tetap berlaku "
            "tetap berlaku setelah penghentian.",
        ),
        _section(
            "15. Perubahan Ketentuan",
            "Kami dapat memperbarui Ketentuan ini di halaman ini. Penggunaan berkelanjutan berarti penerimaan.",
        ),
        _section(
            "16. Hukum yang Berlaku & Sengketa",
            "Ketentuan ini diatur oleh hukum Republik Indonesia. Pengadilan di Jakarta berwenang, kecuali "
            "hukum perlindungan konsumen wajib di negara Anda menentukan lain.",
        ),
        _section(
            "17. Kontak",
            f"Pertanyaan: {CONTACT}, penagihan {BILLING}, dukungan {SUPPORT}. {COMPANY}, {ADDRESS}.",
        ),
    ],
)

TERMS_BY_LANG = {
    "en": TERMS_EN,
    "fr": TERMS_FR,
    "es": TERMS_ES,
    "id": TERMS_ID,
}


def patch_terms_in_translations(raw: str) -> str:
    """Replace each language's terms block in the translations module source."""
    raw = raw.replace('\\"terms\\":', '"terms":')
    for lang, block in TERMS_BY_LANG.items():
        pattern = (
            rf'("{lang}":\s*\{{[\s\S]*?)'
            rf'(        (?:"terms"|\\"terms\\"):\s*\{{[\s\S]*?\n        \}},)'
            rf'(\n        "technical")'
        )
        replacement = rf'\1        "terms": {{\n        {block}\n        }},\3'
        new_raw, count = re.subn(pattern, replacement, raw, count=1)
        if count != 1:
            raise SystemExit(f"Failed to patch terms for language {lang!r} (matches={count})")
        raw = new_raw
    return raw
