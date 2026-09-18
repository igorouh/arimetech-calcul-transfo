import math
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


PROFILS_CONSTRUCTEURS = {
    "ABB / Standard": {
        "B_tesla": 1.64,
        "J_alu_ht": 1.0,
        "J_cu_ht": 2.5,
        "J_alu_bt": 2.5,
        "J_cu_bt": 3.0,
    },
    "Schneider / France Transfo": {
        "B_tesla": 1.62,
        "J_alu_ht": 1.1,
        "J_cu_ht": 2.7,
        "J_alu_bt": 2.5,
        "J_cu_bt": 3.2,
    },
    "Siemens": {
        "B_tesla": 1.65,
        "J_alu_ht": 1.0,
        "J_cu_ht": 2.6,
        "J_alu_bt": 2.5,
        "J_cu_bt": 3.0,
    },
    "SACEM": {
        "B_tesla": 1.60,
        "J_alu_ht": 1.05,
        "J_cu_ht": 2.55,
        "J_alu_bt": 2.45,
        "J_cu_bt": 2.9,
    },
    "Nexans": {
        "B_tesla": 1.63,
        "J_alu_ht": 1.1,
        "J_cu_ht": 2.65,
        "J_alu_bt": 2.5,
        "J_cu_bt": 3.1,
    },
    "Energie Transfo": {
        "B_tesla": 1.61,
        "J_alu_ht": 1.0,
        "J_cu_ht": 2.5,
        "J_alu_bt": 2.4,
        "J_cu_bt": 2.85,
    },
    "Générique / Inconnu": {
        "B_tesla": 1.60,
        "J_alu_ht": 1.0,
        "J_cu_ht": 2.5,
        "J_alu_bt": 2.4,
        "J_cu_bt": 2.8,
    },
}


def calculer_section_fer(largeur_cm, nb_toles, epaisseur_tole_mm, nb_etages):
    epaisseur_totale_cm = (nb_toles * epaisseur_tole_mm) / 10.0
    section_brute = largeur_cm * epaisseur_totale_cm
    k_forme = 0.83 if nb_etages <= 3 else (0.88 if nb_etages <= 5 else 0.91)
    return section_brute * k_forme * 0.95


def estimer_meplat(section_mm2):
    if section_mm2 <= 15:
        ep = 2.0
    elif section_mm2 <= 40:
        ep = 3.0
    elif section_mm2 <= 80:
        ep = 4.0
    else:
        ep = 5.0
    return ep, section_mm2 / ep


def convertir_alu_cuivre():
    try:
        d_alu = float(entry_conv_alu.get())
        # Conversion empirique d'atelier (~78% du diamètre Alu)
        d_cu = d_alu * 0.78
        sec_alu = math.pi * ((d_alu / 2) ** 2)
        sec_cu = math.pi * ((d_cu / 2) ** 2)
        lbl_res_conv.config(
            text=f"Ø Cuivre : {d_cu:.2f} mm  (S_alu={sec_alu:.2f}mm² → S_cu={sec_cu:.2f}mm²)"
        )
    except ValueError:
        messagebox.showerror(
            "Erreur", "Veuillez entrer un diamètre valide en mm."
        )


def lancer_calcul():
    try:
        s_kva = float(entry_skva.get())
        u1_volts = float(entry_u1.get())
        u2_volts = float(entry_u2.get())
        largeur_cm = float(entry_largeur.get())
        nb_toles = int(entry_toles.get())
        epaisseur_mm = float(entry_epaisseur.get())
        nb_etages = int(combo_etages.get())
        mat_prim = combo_mat_ht.get()
        mat_sec = combo_mat_bt.get()
        constructeur = combo_constructeur.get()
        marge_spires = float(entry_marge.get()) / 100.0

        profil = PROFILS_CONSTRUCTEURS.get(
            constructeur, PROFILS_CONSTRUCTEURS["Générique / Inconnu"]
        )
        b_tesla = profil["B_tesla"]

        j_prim = (
            profil["J_alu_ht"]
            if mat_prim.lower() == "aluminium"
            else profil["J_cu_ht"]
        )
        j_sec = (
            profil["J_alu_bt"]
            if mat_sec.lower() == "aluminium"
            else profil["J_cu_bt"]
        )

        i1_phase = (s_kva * 1000) / (3 * u1_volts)
        i2_phase = (s_kva * 1000) / (math.sqrt(3) * u2_volts)
        v2_phase = u2_volts / math.sqrt(3)

        s_fer_cm2 = calculer_section_fer(
            largeur_cm, nb_toles, epaisseur_mm, nb_etages
        )
        s_fer_m2 = s_fer_cm2 / 10000.0

        e_t = 4.44 * 50 * b_tesla * s_fer_m2

        # Prise en compte de la correction / surcompensation à vide
        n2_theorique = v2_phase / e_t
        n2 = round(n2_theorique * (1 + marge_spires))
        n1 = round(n2 * (u1_volts / v2_phase))

        sec_ht_mm2 = i1_phase / j_prim
        diam_ht_mm = 2 * math.sqrt(sec_ht_mm2 / math.pi)

        sec_bt_mm2 = i2_phase / j_sec
        diam_bt_mm = 2 * math.sqrt(sec_bt_mm2 / math.pi)
        ep_mep, larg_mep = estimer_meplat(sec_bt_mm2)

        lbl_sfer.config(text=f"{s_fer_cm2:.2f} cm²")
        lbl_et.config(text=f"{e_t:.3f} V/spire")
        lbl_n2.config(text=f"{n2} spires (ajusté)")
        lbl_n1.config(text=f"{n1} spires")
        lbl_i1.config(text=f"{i1_phase:.3f} A")
        lbl_i2.config(text=f"{i2_phase:.2f} A")

        lbl_sec_ht.config(text=f"{sec_ht_mm2:.3f} mm² (Ø {diam_ht_mm:.2f} mm)")
        lbl_sec_bt.config(text=f"{sec_bt_mm2:.2f} mm²")
        lbl_diam_bt.config(text=f"Ø {diam_bt_mm:.2f} mm")
        lbl_meplat_bt.config(
            text=f"{ep_mep:.1f} mm x {larg_mep:.2f} mm (Ép. x Larg.)"
        )

    except ValueError:
        messagebox.showerror(
            "Erreur de saisie", "Veuillez vérifier vos données !"
        )


root = tk.Tk()
root.title("Calculateur de Rebobinage Transformateur - Atelier HTA")
root.geometry("560x900")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

# En-tête
frame_header = tk.Frame(root, bg="#1E3A8A", pady=10)
frame_header.pack(fill="x")

image_path = resource_path("transfo.png")
if os.path.exists(image_path):
    img_icon = tk.PhotoImage(file=image_path)
    img_icon_small = img_icon.subsample(4, 4)
    lbl_img = tk.Label(frame_header, image=img_icon_small, bg="#1E3A8A")
    lbl_img.pack(side="left", padx=15)

lbl_title = tk.Label(
    frame_header,
    text="DIMENSIONNEMENT TRANSFO HTA/BT",
    font=("Helvetica", 13, "bold"),
    fg="white",
    bg="#1E3A8A",
)
lbl_title.pack(side="left", padx=5)

# Formulaire
frame_form = ttk.LabelFrame(root, text=" Données d'entrée ", padding=10)
frame_form.pack(fill="x", padx=15, pady=5)

ttk.Label(frame_form, text="Puissance (kVA) :").grid(
    row=0, column=0, sticky="w", pady=2
)
entry_skva = ttk.Entry(frame_form)
entry_skva.insert(0, "50")
entry_skva.grid(row=0, column=1, pady=2)

ttk.Label(frame_form, text="Tension HT (Volts) :").grid(
    row=1, column=0, sticky="w", pady=2
)
entry_u1 = ttk.Entry(frame_form)
entry_u1.insert(0, "33000")
entry_u1.grid(row=1, column=1, pady=2)

ttk.Label(frame_form, text="Tension BT (Volts) :").grid(
    row=2, column=0, sticky="w", pady=2
)
entry_u2 = ttk.Entry(frame_form)
entry_u2.insert(0, "400")
entry_u2.grid(row=2, column=1, pady=2)

ttk.Label(frame_form, text="Largeur tôle (cm) :").grid(
    row=3, column=0, sticky="w", pady=2
)
entry_largeur = ttk.Entry(frame_form)
entry_largeur.insert(0, "10.0")
entry_largeur.grid(row=3, column=1, pady=2)

ttk.Label(frame_form, text="Nombre de tôles :").grid(
    row=4, column=0, sticky="w", pady=2
)
entry_toles = ttk.Entry(frame_form)
entry_toles.insert(0, "318")
entry_toles.grid(row=4, column=1, pady=2)

ttk.Label(frame_form, text="Épaisseur tôle (mm) :").grid(
    row=5, column=0, sticky="w", pady=2
)
entry_epaisseur = ttk.Entry(frame_form)
entry_epaisseur.insert(0, "0.30")
entry_epaisseur.grid(row=5, column=1, pady=2)

ttk.Label(frame_form, text="Nombre d'étages :").grid(
    row=6, column=0, sticky="w", pady=2
)
combo_etages = ttk.Combobox(
    frame_form, values=["3", "5", "7"], state="readonly", width=17
)
combo_etages.current(0)
combo_etages.grid(row=6, column=1, pady=2)

ttk.Label(frame_form, text="Matériau HT (Primaire) :").grid(
    row=7, column=0, sticky="w", pady=2
)
combo_mat_ht = ttk.Combobox(
    frame_form, values=["Aluminium", "Cuivre"], state="readonly", width=17
)
combo_mat_ht.current(0)
combo_mat_ht.grid(row=7, column=1, pady=2)

ttk.Label(frame_form, text="Matériau BT (Secondaire) :").grid(
    row=8, column=0, sticky="w", pady=2
)
combo_mat_bt = ttk.Combobox(
    frame_form, values=["Aluminium", "Cuivre"], state="readonly", width=17
)
combo_mat_bt.current(0)
combo_mat_bt.grid(row=8, column=1, pady=2)

ttk.Label(frame_form, text="Constructeur :").grid(
    row=9, column=0, sticky="w", pady=2
)
combo_constructeur = ttk.Combobox(
    frame_form,
    values=list(PROFILS_CONSTRUCTEURS.keys()),
    state="readonly",
    width=17,
)
combo_constructeur.current(0)
combo_constructeur.grid(row=9, column=1, pady=2)

ttk.Label(frame_form, text="Ajustement Spires BT (%) :").grid(
    row=10, column=0, sticky="w", pady=2
)
entry_marge = ttk.Entry(frame_form)
entry_marge.insert(0, "3.0")
entry_marge.grid(row=10, column=1, pady=2)

btn_calculer = tk.Button(
    root,
    text="CALCULER LE DIMENSIONNEMENT",
    font=("Helvetica", 10, "bold"),
    bg="#10B981",
    fg="white",
    command=lancer_calcul,
    pady=4,
)
btn_calculer.pack(fill="x", padx=15, pady=4)

# Module de conversion d'atelier
frame_conv = ttk.LabelFrame(
    root, text=" Module de Conversion Directe Atelier ", padding=8
)
frame_conv.pack(fill="x", padx=15, pady=4)

ttk.Label(frame_conv, text="Ø Fil Alu (mm) :").grid(
    row=0, column=0, sticky="w"
)
entry_conv_alu = ttk.Entry(frame_conv, width=12)
entry_conv_alu.insert(0, "0.80")
entry_conv_alu.grid(row=0, column=1, padx=5)

btn_conv = tk.Button(
    frame_conv,
    text="Convertir en Cuivre",
    bg="#3B82F6",
    fg="white",
    command=convertir_alu_cuivre,
)
btn_conv.grid(row=0, column=2, padx=5)

lbl_res_conv = ttk.Label(
    frame_conv, text="Ø Cuivre : -", font=("Helvetica", 9, "bold"), foreground="green"
)
lbl_res_conv.grid(row=1, column=0, columnspan=3, sticky="w", pady=4)

# Résultats
frame_res = ttk.LabelFrame(root, text=" Résultats du calcul ", padding=8)
frame_res.pack(fill="x", padx=15, pady=4)

labels = [
    ("Section Nette Fer (Sfer) :", "lbl_sfer"),
    ("Tension par spire :", "lbl_et"),
    ("Spires BT (N2) :", "lbl_n2"),
    ("Spires HT (N1) :", "lbl_n1"),
    ("Courant Phase HT (I1ph) :", "lbl_i1"),
    ("Courant Phase BT (I2ph) :", "lbl_i2"),
    ("Conducteur HT (Primaire) :", "lbl_sec_ht"),
    ("Section Conducteur BT :", "lbl_sec_bt"),
    (" - Si Fil Rond BT :", "lbl_diam_bt"),
    (" - Si Méplat BT (suggéré) :", "lbl_meplat_bt"),
]

for i, (text, var_name) in enumerate(labels):
    ttk.Label(frame_res, text=text, font=("Helvetica", 9, "bold")).grid(
        row=i, column=0, sticky="w", pady=1
    )
    lbl = ttk.Label(
        frame_res, text="-", font=("Helvetica", 9), foreground="blue"
    )
    lbl.grid(row=i, column=1, sticky="w", padx=10, pady=1)
    globals()[var_name] = lbl

root.mainloop()