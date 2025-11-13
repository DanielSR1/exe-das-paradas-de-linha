import subprocess
import tkinter as tk
from tkinter import messagebox
import psutil
import os
import time
import webbrowser

# === LOCALIZA AUTOMATICAMENTE O manage.py ===
def localizar_manage_py():
    usuario = os.path.expanduser("~")

    # 1️⃣ Caminho padrão em português
    caminho1 = os.path.join(usuario, "Documentos", "web automacao", "monitor_linha", "manage.py")

    # 2️⃣ Caminho padrão em inglês
    caminho2 = os.path.join(usuario, "Documents", "web automacao", "monitor_linha", "manage.py")

    # 3️⃣ Caminho dentro do OneDrive (qualquer nome de pasta com "OneDrive")
    onedrive_base = None
    for pasta in os.listdir(usuario):
        if "OneDrive" in pasta:
            onedrive_base = os.path.join(usuario, pasta, "Documentos")
            break

    caminho3 = os.path.join(onedrive_base, "web automacao", "monitor_linha", "manage.py") if onedrive_base else None

    # Verifica qual caminho realmente existe
    for caminho in [caminho1, caminho2, caminho3]:
        if caminho and os.path.exists(caminho):
            return caminho

    return None


DJANGO_PATH = localizar_manage_py()

if not DJANGO_PATH:
    messagebox.showerror(
        "Erro",
        "⚠️ manage.py não encontrado.\n\nVerifique se o caminho existe:\n"
        "Documentos\\web automacao\\monitor_linha\\manage.py\n\n"
        "Dica: se seus arquivos estiverem no OneDrive, verifique se ele está sincronizado."
    )
    exit()

# Variável global para armazenar o processo
server_process = None

def iniciar_servidor():
    global server_process
    if servidor_ativo():
        messagebox.showinfo("Servidor", "O servidor já está em execução.")
        return

    try:
        server_process = subprocess.Popen(
            ["python", DJANGO_PATH, "runserver", "127.0.0.1:8000"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(3)
        webbrowser.open("http://127.0.0.1:8000/")
        status_label.config(text="🟢 Servidor ativo", fg="green")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao iniciar o servidor:\n{e}")

def parar_servidor():
    global server_process
    if not servidor_ativo():
        messagebox.showinfo("Servidor", "O servidor não está em execução.")
        return

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['cmdline'] and "manage.py" in ' '.join(proc.info['cmdline']):
                proc.kill()
        server_process = None
        status_label.config(text="🔴 Servidor parado", fg="red")
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao parar o servidor:\n{e}")

def reiniciar_servidor():
    parar_servidor()
    time.sleep(3)
    iniciar_servidor()

def servidor_ativo():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and "manage.py" in ' '.join(proc.info['cmdline']):
                return True
        except (psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def atualizar_status():
    if servidor_ativo():
        status_label.config(text="🟢 Aplicação Online", fg="green")
    else:
        status_label.config(text="🔴 Aplicação Offline", fg="red")
    root.after(2000, atualizar_status)

def abrir_plataforma(event=None):
    webbrowser.open("http://127.0.0.1:8000/")

# --- INTERFACE TKINTER ---
root = tk.Tk()
root.title("Gerenciador Django Offline")
root.geometry("360x240")
root.resizable(False, False)

tk.Label(root, text="Controle do Software de Paradas", font=("Arial", 12, "bold")).pack(pady=10)

status_label = tk.Label(root, text="Verificando...", font=("Arial", 10))
status_label.pack(pady=5)

# Exibe o caminho detectado
tk.Label(root, text=f"Caminho detectado:\n{DJANGO_PATH}", font=("Arial", 8), wraplength=320, fg="gray").pack(pady=5)

link_label = tk.Label(
    root,
    text="Clique aqui para acessar a plataforma",
    font=("Arial", 10, "underline"),
    fg="blue",
    cursor="hand2"
)
link_label.pack(pady=5)
link_label.bind("<Button-1>", abrir_plataforma)

frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="Iniciar", width=10, command=iniciar_servidor).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes, text="Parar", width=10, command=parar_servidor).grid(row=0, column=1, padx=5)
tk.Button(frame_botoes, text="Reiniciar", width=10, command=reiniciar_servidor).grid(row=0, column=2, padx=5)

atualizar_status()
root.mainloop()
