import re
import tkinter as tk
from tkinter import filedialog, messagebox
from transformers import pipeline
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Pipeline NER (HerBERT – najlepszy polski model NER)
ner = pipeline("ner", model="pczarnik/herbert-base-ner", grouped_entities=True)
#ner = pipeline("ner", model="wietsedzielenski/herbert-small-ner-pl", grouped_entities=True)


def anonymize_text(text: str) -> str:
    entities = []

    # 1️⃣ AI‑NER (HerBERT small)
    for ent in ner(text):
        label = ent["entity_group"]
        start, end = ent["start"], ent["end"]
        # ⚠️ Pomijamy "Polski" w kontekście "o historii"
        if label == "LOC" and text[max(0, start-10):start].lower().endswith("histori"):
            continue
        placeholder = {
            "PER": "<PERSON>",
            "LOC": "<LOCATION>",
            "ORG": "<ORGANIZATION>"
        }.get(label, f"<{label}>")
        entities.append((start, end, placeholder))

    # 2️⃣ Regex: numer telefonu, email, data
    patterns = [
        (r"\b\d{3}[- ]\d{3}[- ]\d{3}\b", "<PHONE NUMBER>"),
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<EMAIL_ADDRESS>"),
        (r"\b\d{1,2}\s(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s\d{4}\b", "<DATE OF BIRTH>")
    ]
    for pat, label in patterns:
        for m in re.finditer(pat, text):
            entities.append((m.start(), m.end(), label))

    # 3️⃣ Regex: anonimizacja nazwy ulicy po słowie "ulicy"
    for m in re.finditer(r"(?<=\bulicy\s)[A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż]+", text):
        entities.append((m.start(), m.end(), "<LOCATION>"))

    # Sortuj i zastępuj
    entities.sort(key=lambda x: x[0])
    result, last = [], 0
    for start, end, label in entities:
        if start < last:
            continue
        result.append(text[last:start])
        result.append(label)
        last = end
    result.append(text[last:])
    return "".join(result)


def analyze_and_anonymize():
    txt = text_input.get("1.0", tk.END).strip()
    if not txt:
        messagebox.showerror("Błąd", "Wprowadź tekst")
        return
    result = anonymize_text(txt)
    text_output.delete("1.0", tk.END); text_output.insert(tk.END, result)
    report_text.set(f"Znaleziono {len(re.findall(r'<[A-Z_ ]+>', result))} encji")

def load_file():
    path = filedialog.askopenfilename(filetypes=[("TXT","*.txt")])
    if path:
        with open(path, encoding="utf-8") as f:
            text_input.delete("1.0", tk.END); text_input.insert(tk.END, f.read())

def save_result():
    path = filedialog.asksaveasfilename(defaultextension=".txt")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text_output.get("1.0", tk.END))

def quit_app(): root.destroy()

root = tk.Tk(); root.title("Asystent RODO"); root.geometry("600x500")
frame = tk.Frame(root); frame.pack(pady=10)
text_input = tk.Text(frame, height=10, width=70); text_input.pack()
tk.Button(frame, text="Anonimizuj", command=analyze_and_anonymize).pack(pady=5)
text_output = tk.Text(frame, height=10, width=70); text_output.pack()
report_text = tk.StringVar(); tk.Label(frame, textvariable=report_text).pack()
btns = tk.Frame(frame); btns.pack(fill="x", pady=5)
tk.Button(btns, text="Wczytaj", command=load_file).pack(side=tk.LEFT)
tk.Button(btns, text="Zapisz", command=save_result).pack(side=tk.RIGHT)
tk.Button(root, text="Zamknij", command=quit_app).pack(pady=10)
root.mainloop()
