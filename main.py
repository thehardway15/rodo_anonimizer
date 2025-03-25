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
        (r"\+\d{2}\s\d{3}\s\d{3}\s\d{3}\b", "<PHONE NUMBER>"),
        (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "<EMAIL_ADDRESS>"),
        (r"\b\d{1,2}\s(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia)\s\d{4}\b", "<DATE OF BIRTH>"),
        (r"\b\d{1,2}\.\d{1,2}\.\d{4}\b", "<DATE OF BIRTH>"),
        (r"\b\d{11}\b", "<PESEL>"),
        (r"\b\d{2}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}[ ]?\d{4}\b", "<BANK ACCOUNT>"),
        (r"\b\d{2}[- ]?\d{3}\b", "<POSTAL CODE>"),
        (r"\bPL\d{9}\b", "<INSURANCE POLICY>"),
        (r"\b[A-Z]{3}\d{6}\b", "<ID CARD>")
    ]
    for pat, label in patterns:
        for m in re.finditer(pat, text):
            entities.append((m.start(), m.end(), label))

    # 3️⃣ Regex: anonimizacja nazwy ulicy po słowie "ulicy"
    for m in re.finditer(r"ulicy\s([A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż]+)", text):
        entities.append((m.start(1), m.end(1), "<LOCATION>"))
        
    # Dodatkowe wzorce dla adresów ulicy z prefiksem "ul."
    for m in re.finditer(r"ul\.\s([A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż]+)", text):
        entities.append((m.start(1), m.end(1), "<LOCATION>"))
        
    # Anonimizacja numerów budynków
    for m in re.finditer(r"ul\.\s[A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż]+\s(\d+[A-Za-z]?)(?=[\s,.]|$)", text):
        entities.append((m.start(1), m.end(1), "<BUILDING NUMBER>"))
    
    for m in re.finditer(r"ulicy\s[A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźż]+\s(\d+[A-Za-z]?)(?=[\s,.]|$)", text):
        entities.append((m.start(1), m.end(1), "<BUILDING NUMBER>"))

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
    
    # Update the output text with visual highlighting
    text_output.delete("1.0", tk.END)
    text_output.tag_configure("entity", background="#ffefaf", foreground="#c7254e")
    
    # Insert text with tags for visual highlighting
    entities_pattern = r'<[A-Z_ ]+>'
    fragments = re.split(f'({entities_pattern})', result)
    
    for i, fragment in enumerate(fragments):
        if i % 2 == 1:  # This is an entity tag
            text_output.insert(tk.END, fragment, "entity")
        else:
            text_output.insert(tk.END, fragment)
    
    # Count entities
    global entity_counts
    counts = {}
    for entity_type in entity_types.keys():
        count = len(re.findall(entity_type, result))
        if count > 0:
            counts[entity_type] = count
    
    # Save counts for details view
    entity_counts = counts
    
    # Enable the show stats button if we have data
    show_stats_button.config(state=tk.NORMAL if counts else tk.DISABLED)
    
def show_detailed_summary():
    """Show a detailed summary in a separate window"""
    if not hasattr(entity_counts, 'items') or not entity_counts:
        messagebox.showinfo("Informacja", "Brak danych do wyświetlenia. Wykonaj najpierw anonimizację.")
        return
        
    summary_window = tk.Toplevel(root)
    summary_window.title("Podsumowanie anonimizacji")
    summary_window.geometry("500x500")
    summary_window.minsize(500, 500)
    
    # Create frame for content
    content_frame = tk.Frame(summary_window, padx=20, pady=20)
    content_frame.pack(fill="both", expand=True)
    
    # Title
    tk.Label(content_frame, text="Zanonimizowane dane osobowe", 
           font=("Arial", 16, "bold"), fg="#3a7ebf").pack(pady=(0, 20))
    
    # Create summary text with scrollbar
    text_frame = tk.Frame(content_frame)
    text_frame.pack(fill="both", expand=True)
    
    summary_scroll_y = tk.Scrollbar(text_frame)
    summary_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget = tk.Text(text_frame, height=20, width=60, 
                        font=("Arial", 11), yscrollcommand=summary_scroll_y.set)
    text_widget.pack(fill="both", expand=True)
    summary_scroll_y.config(command=text_widget.yview)
    
    # Insert summary content
    text_widget.insert(tk.END, "Podsumowanie anonimizacji\n\n", "title")
    text_widget.insert(tk.END, "Typ danych\tLiczba\n", "header")
    text_widget.insert(tk.END, "-" * 40 + "\n")
    
    # Sort by count
    sorted_items = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
    for entity, count in sorted_items:
        entity_name = entity_types.get(entity, entity.strip("<>"))
        text_widget.insert(tk.END, f"{entity_name}\t{count}\n")
    
    # Add total
    total = sum(entity_counts.values())
    text_widget.insert(tk.END, "-" * 40 + "\n")
    text_widget.insert(tk.END, f"RAZEM\t{total}\n", "bold")
    
    # Configure tags
    text_widget.tag_configure("title", font=("Arial", 14, "bold"), justify="center")
    text_widget.tag_configure("header", font=("Arial", 12, "bold"))
    text_widget.tag_configure("bold", font=("Arial", 11, "bold"))
    
    # Make read-only
    text_widget.configure(state="disabled")
    
    # Close button with better styling
    button_frame = tk.Frame(content_frame, pady=15)
    button_frame.pack(fill="x")
    
    tk.Button(button_frame, text="Zamknij", 
             command=summary_window.destroy,
             bg="#f44336", fg="black", 
             font=("Arial", 12, "bold"), padx=20, pady=8).pack()

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

# Initialize global variables
entity_counts = {}
entity_types = {
    "<PERSON>": "Osób",
    "<LOCATION>": "Lokalizacji",
    "<ORGANIZATION>": "Organizacji",
    "<PHONE NUMBER>": "Numerów telefonu",
    "<EMAIL_ADDRESS>": "Adresów email",
    "<DATE OF BIRTH>": "Dat urodzenia",
    "<PESEL>": "Numerów PESEL",
    "<BANK ACCOUNT>": "Kont bankowych",
    "<POSTAL CODE>": "Kodów pocztowych",
    "<INSURANCE POLICY>": "Polis ubezpieczeniowych",
    "<ID CARD>": "Dowodów osobistych",
    "<BUILDING NUMBER>": "Numerów budynków",
    "<REGULATION>": "Regulacji"
}

# Simple GUI
root = tk.Tk()
root.title("Asystent RODO - Anonimizacja Danych Osobowych")
root.geometry("900x800")  # Significantly increased window size
root.minsize(900, 800)    # Set larger minimum window size

# Title
title_frame = tk.Frame(root)
title_frame.pack(fill="x", pady=10)
tk.Label(title_frame, text="Asystent Anonimizacji Danych Osobowych", 
       font=("Arial", 18, "bold"), fg="#3a7ebf").pack()
tk.Label(title_frame, text="Zgodny z wymogami RODO", 
       font=("Arial", 12), fg="#3a7ebf").pack()

# Create a main container that can handle scrolling if needed
main_container = tk.Frame(root)
main_container.pack(fill="both", expand=True)

# Split the main area into content and buttons areas
content_frame = tk.Frame(main_container)
content_frame.pack(fill="both", expand=True, side=tk.TOP, padx=20)

buttons_area = tk.Frame(main_container, height=120)  # Fixed height for buttons
buttons_area.pack(fill="x", side=tk.BOTTOM, pady=10, padx=20)
buttons_area.pack_propagate(False)  # Prevent resizing

# Input section
input_frame = tk.LabelFrame(content_frame, text="Tekst do anonimizacji", 
                        font=("Arial", 12, "bold"), padx=10, pady=10)
input_frame.pack(fill="both", expand=True)

# Add scrollbars to input text
input_scroll_y = tk.Scrollbar(input_frame)
input_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

text_input = tk.Text(input_frame, height=10, width=80, font=("Arial", 11),
                   borderwidth=2, relief="groove", yscrollcommand=input_scroll_y.set)
text_input.pack(fill="both", expand=True, padx=5, pady=5, side=tk.LEFT)
input_scroll_y.config(command=text_input.yview)

# Action button
button_frame = tk.Frame(content_frame)
button_frame.pack(fill="x", pady=10)
anonymize_button = tk.Button(button_frame, text="Anonimizuj", command=analyze_and_anonymize,
                         bg="#4CAF50", fg="black", font=("Arial", 12, "bold"),
                         padx=20, pady=5)
anonymize_button.pack()

# Output section
output_frame = tk.LabelFrame(content_frame, text="Zanonimizowany tekst", 
                         font=("Arial", 12, "bold"), padx=10, pady=10)
output_frame.pack(fill="both", expand=True)

# Add scrollbars to output text
output_scroll_y = tk.Scrollbar(output_frame)
output_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

text_output = tk.Text(output_frame, height=10, width=80, font=("Arial", 11),
                    borderwidth=2, relief="groove", bg="#f8f8f8", 
                    yscrollcommand=output_scroll_y.set)
text_output.pack(fill="both", expand=True, padx=5, pady=5, side=tk.LEFT)
output_scroll_y.config(command=text_output.yview)

# Bottom buttons - with clear frame and borders
btns_frame = tk.Frame(buttons_area, pady=10, bd=1, relief=tk.RAISED, bg="#f0f0f0")
btns_frame.pack(fill="both", expand=True)

# Add a label above the buttons
tk.Label(btns_frame, text="Opcje:", font=("Arial", 10, "bold"), 
        bg="#f0f0f0").pack(anchor="w", padx=10, pady=(5,10))

# Button container - center align for better appearance
button_container = tk.Frame(btns_frame, bg="#f0f0f0")
button_container.pack(fill="x", padx=10, pady=5)
button_container.columnconfigure(0, weight=1)  # For center alignment
button_container.columnconfigure(4, weight=1)  # For center alignment

# Make buttons more visible with clearer colors and better spacing
load_button = tk.Button(button_container, text="📂 Wczytaj z pliku", command=load_file,
                      bg="#2196F3", fg="black", font=("Arial", 11, "bold"),
                      padx=15, pady=8)
load_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(button_container, text="💾 Zapisz do pliku", command=save_result,
                      bg="#2196F3", fg="black", font=("Arial", 11, "bold"),
                      padx=15, pady=8)
save_button.pack(side=tk.LEFT, padx=10)

show_stats_button = tk.Button(button_container, text="📊 Pokaż szczegóły", command=show_detailed_summary,
                           bg="#ff9800", fg="black", font=("Arial", 11, "bold"),
                           padx=15, pady=8, state=tk.DISABLED)  # Initially disabled
show_stats_button.pack(side=tk.LEFT, padx=10)

quit_button = tk.Button(button_container, text="❌ Zakończ", command=quit_app,
                      bg="#f44336", fg="black", font=("Arial", 11, "bold"),
                      padx=15, pady=8)
quit_button.pack(side=tk.RIGHT, padx=10)

root.mainloop()
