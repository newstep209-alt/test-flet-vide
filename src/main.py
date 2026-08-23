import flet as ft
import sqlite3, os, io, threading
from pypdf import PdfReader
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "ifpb_c2.db")
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
os.makedirs(AUDIO_DIR, exist_ok=True)

COULEUR_FOND = "#0F1A13"
COULEUR_PRIMAIRE = "#00FF87" # Vert néon
COULEUR_ACCENT = "#D4AF37" # Or

def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS cours(id INTEGER PRIMARY KEY, titre TEXT, resume TEXT)')
    conn.commit()
    return conn

def parler(page, texte):
    if not texte.strip(): return
    def run_tts():
        try:
            page.snack_bar = ft.SnackBar(ft.Text("Génération audio..."), bgcolor=COULEUR_PRIMAIRE)
            page.snack_bar.open = True; page.update()
            tts = gTTS(text=texte[:500], lang='fr', slow=False) # Limite à 500 char
            file_path = os.path.join(AUDIO_DIR, "temp.mp3")
            tts.save(file_path)
            page.media.play(file_path)
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erreur: {e}"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True; page.update()
    threading.Thread(target=run_tts).start()

def main(page: ft.Page):
    page.title = "IFPB C2 COMPTABILITE AL11"
    page.bgcolor = COULEUR_FOND
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    conn = get_db()

    page.splash = ft.Container(
        bgcolor=COULEUR_PRIMAIRE,
        content=ft.Column([
            ft.Image(src="src/assets/logo_ifpb.png", width=100),
            ft.Text("IFPB C2", color="black", size=20, weight="bold")
        ], alignment=ft.MainAxisAlignment.CENTER),
        alignment=ft.alignment.center
    )

    def on_pdf_upload(e: ft.FilePickerResultEvent):
        if not e.files: return
        page.splash = ft.ProgressRing(color=COULEUR_ACCENT)
        page.update()
        def process_pdf():
            try:
                file = e.files[0]
                reader = PdfReader(io.BytesIO(file.read()))
                texte_complet = "".join([p.extract_text() or "" for p in reader.pages])
                c = conn.cursor()
                c.execute("INSERT INTO cours(titre, resume) VALUES(?,?)", (file.name, texte_complet))
                conn.commit()
                charger_accueil()
                page.snack_bar = ft.SnackBar(ft.Text(f"Module '{file.name}' ajouté!"), bgcolor=COULEUR_PRIMAIRE)
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erreur PDF: {ex}"), bgcolor=ft.Colors.RED_700)
            page.snack_bar.open = True
            page.splash = None
            page.update()
        threading.Thread(target=process_pdf).start()

    file_picker = ft.FilePicker(on_result=on_pdf_upload)
    page.overlay.append(file_picker)

    contenu = ft.Column(spacing=25)

    def carte_action(icone, titre, sous_titre, on_click):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icone, size=35, color=COULEUR_PRIMAIRE),
                ft.Column([ft.Text(titre, size=18, weight="bold", color="white"), ft.Text(sous_titre, size=12, color=ft.Colors.GREY_400)])
            ], spacing=15),
            padding=20, bgcolor="#1E2D25", border_radius=15,
            border=ft.border.all(1, COULEUR_PRIMAIRE),
            on_click=on_click
        )

    def charger_accueil():
        contenu.controls.clear()
        c = conn.cursor()
        nb_cours = c.execute("SELECT COUNT(*) FROM cours").fetchone()[0]

        header = ft.Container(
            padding=25, bgcolor=COULEUR_PRIMAIRE,
            content=ft.Column([
                ft.Row([ft.Image(src="src/assets/logo_ifpb.png", width=45), ft.Text("IFPB C2 COMPTABILITE AL11", color="black", size=16, weight="bold")]),
                ft.Text("Bonjour Devops", color="black", size=26, weight="bold"),
                ft.Text(f"{nb_cours} Modules | Prêt à réviser?", color="black")
            ])
        )

        actions = ft.Column([
            carte_action(ft.icons.AUTO_STORIES, "Mes Modules", "Reprendre un cours", lambda e: print("modules")),
            carte_action(ft.icons.QUIZ, "Mode QCM", "S'entraîner", lambda e: print("qcm")),
            carte_action(ft.icons.MIC, "Audio RnB", "Réviser en écoutant", lambda e: print("audio")),
            ft.ElevatedButton("📄 Ajouter un PDF", icon=ft.icons.UPLOAD_FILE, bgcolor=COULEUR_ACCENT, color="black", on_click=lambda _: file_picker.pick_files(allowed_extensions=["pdf"]))
        ], spacing=15, padding=20)

        contenu.controls = [header, actions]
        page.update()

    page.add(contenu)
    charger_accueil()

ft.app(target=main)
