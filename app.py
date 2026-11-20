import math
import flet as ft

PROFILS_CONSTRUCTEURS = {
    "ABB / Standard": {
        "B_tesla": 1.65,
        "J_alu_ht": 1.30,
        "J_cu_ht": 3.15,
        "J_alu_bt": 2.50,
        "J_cu_bt": 3.20,
        "marge_spires": 0.0,
    },
    "Cahors / Transfix": {
        "B_tesla": 1.65,
        "J_alu_ht": 1.35,
        "J_cu_ht": 3.20,
        "J_alu_bt": 2.55,
        "J_cu_bt": 3.25,
        "marge_spires": 0.0,
    },
    "Schneider / France Transfo": {
        "B_tesla": 1.64,
        "J_alu_ht": 1.35,
        "J_cu_ht": 3.20,
        "J_alu_bt": 2.55,
        "J_cu_bt": 3.30,
        "marge_spires": 0.0,
    },
    "Siemens": {
        "B_tesla": 1.65,
        "J_alu_ht": 1.30,
        "J_cu_ht": 3.15,
        "J_alu_bt": 2.50,
        "J_cu_bt": 3.20,
        "marge_spires": 0.0,
    },
    "SACEM": {
        "B_tesla": 1.62,
        "J_alu_ht": 1.25,
        "J_cu_ht": 3.00,
        "J_alu_bt": 2.45,
        "J_cu_bt": 3.00,
        "marge_spires": 0.0,
    },
    "Nexans": {
        "B_tesla": 1.64,
        "J_alu_ht": 1.30,
        "J_cu_ht": 3.15,
        "J_alu_bt": 2.50,
        "J_cu_bt": 3.20,
        "marge_spires": 0.0,
    },
    "Energie Transfo": {
        "B_tesla": 1.62,
        "J_alu_ht": 1.25,
        "J_cu_ht": 3.00,
        "J_alu_bt": 2.40,
        "J_cu_bt": 2.95,
        "marge_spires": 0.0,
    },
    "Générique / Inconnu": {
        "B_tesla": 1.62,
        "J_alu_ht": 1.30,
        "J_cu_ht": 3.10,
        "J_alu_bt": 2.45,
        "J_cu_bt": 3.10,
        "marge_spires": 0.0,
    },
}


def calculer_section_fer(largeur_cm, nb_toles, epaisseur_tole_mm, nb_etages):
    epaisseur_totale_cm = (nb_toles * epaisseur_tole_mm) / 10.0

    # Facteur de remplissage géométrique réel des noyaux étagés
    if nb_etages <= 3:
        k_gradins = 0.74
    elif nb_etages <= 5:
        k_gradins = 0.78
    elif nb_etages <= 7:
        k_gradins = 0.81
    elif nb_etages <= 9:
        k_gradins = 0.825
    elif nb_etages <= 11:
        k_gradins = 0.835
    elif nb_etages <= 13:
        k_gradins = 0.845
    else:
        k_gradins = 0.855

    section_brute_etagee = largeur_cm * epaisseur_totale_cm * k_gradins
    return section_brute_etagee * 0.95


def estimer_meplat(section_mm2):
    ep = (
        2.0
        if section_mm2 <= 15
        else (3.0 if section_mm2 <= 40 else (4.0 if section_mm2 <= 80 else 5.0))
    )
    return ep, section_mm2 / ep


def main(page: ft.Page):
    page.title = "Calculateur Transfo HTA/BT"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO

    skva = ft.TextField(label="Puissance (kVA)", value="160")
    u1 = ft.TextField(label="Tension HT (V)", value="33000")
    u2 = ft.TextField(label="Tension BT à vide (V)", value="400")
    largeur = ft.TextField(
        label="Diamètre noyau / Largeur tôle principale (cm)", value="13.5"
    )
    toles = ft.TextField(label="Nombre de lames total", value="426")
    epaisseur = ft.TextField(label="Épaisseur lame (mm)", value="0.30")

    etages = ft.TextField(
        label="Nombre d'étages (saisie libre)",
        value="13",
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    mat_ht = ft.Dropdown(
        label="Matériau HT",
        value="Cuivre",
        options=[
            ft.dropdown.Option("Aluminium"),
            ft.dropdown.Option("Cuivre"),
        ],
    )
    mat_bt = ft.Dropdown(
        label="Matériau BT",
        value="Cuivre",
        options=[
            ft.dropdown.Option("Aluminium"),
            ft.dropdown.Option("Cuivre"),
        ],
    )

    marge = ft.TextField(label="Ajustement Spires BT (%)", value="0.0")
    spires_bt_rec = ft.TextField(label="Spires BT relevées (Optionnel)")

    def changer_constructeur(e):
        p = PROFILS_CONSTRUCTEURS.get(
            constructeur.value, PROFILS_CONSTRUCTEURS["Générique / Inconnu"]
        )
        marge.value = str(p.get("marge_spires", 0.0))
        page.update()

    constructeur = ft.Dropdown(
        label="Constructeur",
        value="Cahors / Transfix",
        options=[ft.dropdown.Option(k) for k in PROFILS_CONSTRUCTEURS.keys()],
        on_select=changer_constructeur,
    )

    conv_alu = ft.TextField(label="Ø Fil Alu (mm)", value="0.80", width=150)
    res_conv = ft.Text("Ø Cuivre : -", color="blue", weight=ft.FontWeight.BOLD)

    def executer_conversion(e):
        try:
            d_alu = float(conv_alu.value)
            d_cu = d_alu * 0.78
            sec_alu = math.pi * ((d_alu / 2) ** 2)
            sec_cu = math.pi * ((d_cu / 2) ** 2)
            res_conv.value = (
                f"Ø Cuivre : {d_cu:.2f} mm (S_alu={sec_alu:.2f}mm² →"
                f" S_cu={sec_cu:.2f}mm²)"
            )
        except ValueError:
            res_conv.value = "Erreur de saisie"
        page.update()

    res_text = ft.Text("Entrez les données et cliquez sur Calculer.", size=14)

    def executer_calcul(e):
        try:
            p_skva = float(skva.value)
            p_u1 = float(u1.value)
            p_u2 = float(u2.value)
            p_larg = float(largeur.value)
            if p_larg > 50:
                p_larg = p_larg / 10.0

            p_toles = int(toles.value)
            p_ep = float(epaisseur.value)
            if p_ep > 2:
                p_ep = p_ep / 100.0

            p_etages = int(etages.value)

            profil = PROFILS_CONSTRUCTEURS.get(
                constructeur.value,
                PROFILS_CONSTRUCTEURS["Générique / Inconnu"],
            )
            b_tesla = profil["B_tesla"]

            j_prim = (
                profil["J_alu_ht"]
                if mat_ht.value.lower() == "aluminium"
                else profil["J_cu_ht"]
            )
            j_sec = (
                profil["J_alu_bt"]
                if mat_bt.value.lower() == "aluminium"
                else profil["J_cu_bt"]
            )

            i1_ph = (p_skva * 1000) / (3 * p_u1)
            i2_ph = (p_skva * 1000) / (math.sqrt(3) * p_u2)
            v2_ph = p_u2 / math.sqrt(3)

            s_fer_cm2 = calculer_section_fer(p_larg, p_toles, p_ep, p_etages)
            s_fer_m2 = s_fer_cm2 / 10000.0
            e_t = 4.44 * 50 * b_tesla * s_fer_m2
            n2_theo = v2_ph / e_t

            if spires_bt_rec.value.strip():
                n2 = int(spires_bt_rec.value.strip())
                marge.value = f"{((n2 / n2_theo) - 1) * 100:.1f}"
                info_bt = f"{n2} spires (Relevé)"
            else:
                marge_val = float(marge.value) / 100.0
                n2 = round(n2_theo * (1 + marge_val))
                info_bt = f"{n2} spires (Calculé)"

            n1 = round(p_u1 / (v2_ph / n2))

            sec_ht = i1_ph / j_prim
            diam_ht = 2 * math.sqrt(sec_ht / math.pi)

            sec_bt = i2_ph / j_sec
            diam_bt = 2 * math.sqrt(sec_bt / math.pi)
            ep_mep, larg_mep = estimer_meplat(sec_bt)

            res_text.value = (
                f"Section Fer nette (Sfer) : {s_fer_cm2:.2f} cm² ({p_etages} étages)\n"
                f"Tension par spire (Et) : {e_t:.3f} V/spire\n"
                f"Spires BT (N2) : {info_bt}\n"
                f"Spires HT (N1) : {n1} spires\n"
                f"Courant HT (I1ph) : {i1_ph:.3f} A\n"
                f"Courant BT (I2ph) : {i2_ph:.2f} A\n"
                f"Conducteur HT : {sec_ht:.3f} mm² (Ø {diam_ht:.2f} mm)\n"
                f"Section BT : {sec_bt:.2f} mm² (Ø {diam_bt:.2f} mm)\n"
                f"Méplat BT : {ep_mep:.1f} x {larg_mep:.2f} mm"
            )
        except Exception as ex:
            res_text.value = f"Erreur de saisie : Vérifiez les chiffres ({ex})"
        page.update()

    page.add(
        ft.AppBar(
            title=ft.Text("DIMENSIONNEMENT TRANSFO HTA/BT"),
            bgcolor="#1E3A8A",
            color="white",
        ),
        ft.Container(
            padding=15,
            content=ft.Column(
                [
                    skva,
                    u1,
                    u2,
                    largeur,
                    toles,
                    epaisseur,
                    etages,
                    mat_ht,
                    mat_bt,
                    constructeur,
                    marge,
                    spires_bt_rec,
                    ft.Button(
                        "CALCULER LE DIMENSIONNEMENT",
                        on_click=executer_calcul,
                        style=ft.ButtonStyle(
                            bgcolor="#10B981", color="white"
                        ),
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Conversion Directe Atelier", weight=ft.FontWeight.BOLD
                    ),
                    ft.Row(
                        [
                            conv_alu,
                            ft.Button(
                                "Convertir", on_click=executer_conversion
                            ),
                        ]
                    ),
                    res_conv,
                    ft.Divider(),
                    ft.Card(content=ft.Container(content=res_text, padding=15)),
                ]
            ),
        ),
    )


if __name__ == "__main__":
    ft.run(main)