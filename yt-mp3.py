import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk, scrolledtext
import yt_dlp
from pydub import AudioSegment
import os
import threading
def browse_folder():
    # Ouvre l'explorateur de fichiers pour sélectionner un dossier
    initial_dir = os.path.expanduser("~")  # Chemin par défaut au dossier utilisateur
    selected_folder = filedialog.askdirectory(initialdir=initial_dir)

    # Si un dossier est sélectionné
    if selected_folder:
        folder_entry.delete(0, tk.END)  # Efface l'ancienne entrée
        folder_entry.insert(0, selected_folder)  # Insère le nouveau chemin

def create_new_folder_dialog():
    # Crée une nouvelle fenêtre contextuelle pour entrer le nom du nouveau dossier
    new_folder_window = tk.Toplevel(root)
    new_folder_window.title("Créer un nouveau dossier")

    tk.Label(new_folder_window, text="Nom du nouveau dossier :").pack(padx=10, pady=10)
    new_folder_name_entry = tk.Entry(new_folder_window)
    new_folder_name_entry.pack(padx=10, pady=10)

    def create_folder():
        # Récupère le chemin du dossier sélectionné
        base_folder = folder_entry.get()
        new_folder_name = new_folder_name_entry.get().strip()  # Nom du nouveau dossier

        if base_folder and new_folder_name:  # Vérifie si les deux champs sont remplis
            new_folder_path = os.path.join(base_folder, new_folder_name)
            try:
                os.makedirs(new_folder_path, exist_ok=True)  # Crée le nouveau dossier
                log_console.insert(tk.END, f"Dossier créé : {new_folder_path}\n")
                folder_entry.delete(0, tk.END)  # Efface l'ancienne entrée
                folder_entry.insert(0, new_folder_path)  # Insère le chemin du nouveau dossier
                new_folder_window.destroy()  # Ferme la fenêtre contextuelle
            except Exception as e:
                log_console.insert(tk.END, f"Erreur lors de la création du dossier : {str(e)}\n")
        else:
            log_console.insert(tk.END, "Erreur : Veuillez sélectionner un dossier et entrer un nom de dossier.\n")

    create_button = tk.Button(new_folder_window, text="Créer", command=create_folder)
    create_button.pack(padx=10, pady=10)
def download_and_convert_to_mp3():
    url = url_entry.get()
    if not url:
        log_console.insert(tk.END, "Erreur: Veuillez entrer une URL valide.\n")
        return

    # Configuration de la barre de progression
    progress_bar["value"] = 0
    progress_bar["maximum"] = 100

    def run_download():
        download_folder = folder_entry.get()

        if not download_folder:
            log_console.insert(tk.END, "Erreur: Veuillez sélectionner un dossier de destination.\n")
            return

        # Options pour télécharger au format webm
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'progress_hooks': [hook]
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                log_console.insert(tk.END, "Téléchargement en cours...\n")
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', None)
                ydl.download([url])
        except Exception as e:
            log_console.insert(tk.END, f"Erreur lors du téléchargement: {str(e)}\n")
            return

        # Conversion du fichier webm en MP3
        webm_filepath = os.path.join(download_folder, f'{title}.webm')
        mp3_filepath = os.path.join(download_folder, f'{title}.mp3')

        try:
            audio = AudioSegment.from_file(webm_filepath, format="webm")
            log_console.insert(tk.END, f"Conversion en MP3 ....: {mp3_filepath}\n")
            audio.export(mp3_filepath, format="mp3")
            os.remove(webm_filepath)  # Supprimer le fichier WebM après la conversion
            log_console.insert(tk.END, f"Conversion en MP3 terminée: {mp3_filepath}\n")
            messagebox.showinfo("Succès", f"Téléchargement et conversion en MP3 terminés.\nFichier MP3 enregistré à : {mp3_filepath}")
        except Exception as e:
            log_console.insert(tk.END, f"Erreur lors de la conversion en MP3: {str(e)}\n")

    # Fonction de mise à jour de la barre de progression
    def hook(d):
        if d['status'] == 'downloading':
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            progress_bar["value"] = percent
            root.update_idletasks()  # Met à jour l'interface

        if d['status'] == 'finished':
            progress_bar["value"] = 100
            log_console.insert(tk.END, "Téléchargement terminé.\n")

    # Exécute le téléchargement dans un thread séparé pour ne pas bloquer l'interface
    threading.Thread(target=run_download).start()

# Création de l'interface utilisateur
# Création de l'interface utilisateur
root = tk.Tk()
root.title("Téléchargeur et Convertisseur MP3 YouTube")

url_label = tk.Label(root, text="URL de la vidéo :")
url_label.pack()

url_entry = tk.Entry(root, width=50)
url_entry.pack()

# Créer un frame pour contenir l'entrée de texte et le bouton
folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)  # Ajoute un peu d'espace vertical autour du cadre

folder_label = tk.Label(folder_frame, text="Destination :")
folder_label.grid(row=0, column=0)

# Nouveau bouton pour créer un dossier
create_button = tk.Button(folder_frame, text="Créer Dossier", command=create_new_folder_dialog)
create_button.grid(row=0, column=3)

folder_entry = tk.Entry(folder_frame, width=30)  # On diminue la largeur de l'entrée pour laisser de la place au bouton
folder_entry.grid(row=0, column=1, padx=5)

folder_button = tk.Button(folder_frame, text="Parcourir", command=browse_folder)
folder_button.grid(row=0, column=2)

download_button = tk.Button(root, text="Télécharger et Convertir en MP3", command=download_and_convert_to_mp3)
download_button.pack()

# Barre de progression
progress_bar = ttk.Progressbar(root, length=300, mode='determinate')
progress_bar.pack(pady=10)

# Console pour afficher les logs
log_console = scrolledtext.ScrolledText(root, height=10, width=60, bg="black", fg="white")
log_console.pack(pady=10)

root.mainloop()

