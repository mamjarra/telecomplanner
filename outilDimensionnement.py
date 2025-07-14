import streamlit as st
import math
from fpdf import FPDF
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="TelecomPlanner+", layout="wide")
st.title("📡 TelecomPlanner+ - Outil de Dimensionnement Télécom")
st.sidebar.title("Paramètres d'entrée")

# Initialisation de la session state
if "rapport_data" not in st.session_state:
    st.session_state.rapport_data = []

# Choix du module
network_type = st.sidebar.selectbox("Choisir le type de réseau", [
    "Dimensionnement GSM", "Liaison Hertienne", "Liaison Optique", "Dimensionnement LTE"])


# === MODULE GSM ===
if network_type == "Dimensionnement GSM":
    st.header("📶 Dimensionnement GSM")
    superficie = st.number_input("Superficie à couvrir (km²)", min_value=1.0, step=1.0)
    surface_cellule = st.number_input("Surface d'une cellule (km²)", value=5.0)
    nb_canaux = st.number_input("Nombre de canaux fréquentiels", value=200)
    bande_MHz = st.number_input("Bande passante disponible (MHz)", value=50.0)
    taille_cluster = st.number_input("Taille du cluster (N)", value=7)

    if st.button("Calculer la capacité GSM"):
        nb_cellules = math.ceil(superficie / surface_cellule)
        nb_clusters = math.ceil(nb_cellules / taille_cluster)
        capacite = nb_cellules * (nb_canaux / taille_cluster)
        largeur_canal = bande_MHz / nb_canaux

        st.success(f"Nombre total de cellules : {nb_cellules}")
        st.success(f"Nombre de clusters nécessaires : {nb_clusters}")
        st.success(f"Capacité maximale du réseau : {capacite:.0f} communications simultanées")
        st.info(f"Largeur d'un canal : {largeur_canal:.3f} MHz")

        # Données pour le rapport
        st.session_state.rapport_data.append([
            "GSM", f"Surface: {superficie} km², Cellule: {surface_cellule} km²",
            f"Capacité: {capacite:.0f}, Canaux: {nb_canaux}, Cluster N: {taille_cluster}"
        ])

        # Graphique avec matplotlib
        fig, ax = plt.subplots()
        ax.bar(["Cellules", "Clusters", "Capacité"], [nb_cellules, nb_clusters, capacite], color=["#6fa8dc", "#93c47d", "#f6b26b"])
        ax.set_ylabel("Valeurs")
        ax.set_title("📊 Résumé du dimensionnement GSM")
        st.pyplot(fig)

        # Enregistrement temporaire du graphe
        graph_path = "graph_gsm.png"
        fig.savefig(graph_path)
        st.session_state.gsm_graph_path = graph_path


# === MODULE HERTIENNE ===
elif network_type == "Liaison Hertienne":
    st.header("📡 Bilan de Liaison Hertzienne")
    freq = st.number_input("Fréquence (GHz)", value=6.0)
    distance = st.number_input("Distance (km)", value=50.0)
    pe_dBm = st.number_input("Puissance d'émission (dBm)", value=40.0)
    g1 = st.number_input("Gain antenne 1 (dB)", value=45.5)
    g2 = st.number_input("Gain antenne 2 (dB)", value=45.5)
    pertes = st.number_input("Pertes totales (guide + branchements) (dB)", value=10.9)

    if st.button("Calculer puissance reçue"):
        fspl = 20 * math.log10(distance) + 20 * math.log10(freq) + 92.45
        pr = pe_dBm + g1 + g2 - fspl - pertes
        st.success(f"FSPL = {fspl:.2f} dB")
        st.success(f"Puissance reçue = {pr:.2f} dBm")

        st.session_state.rapport_data.append([
            "Hertzienne", f"Fréquence: {freq} GHz, Distance: {distance} km",
            f"Pr: {pr:.2f} dBm, FSPL: {fspl:.2f} dB"
        ])

        # Graphe puissance
        fig, ax = plt.subplots()
        labels = ["Puissance émission", "FSPL + pertes", "Puissance reçue"]
        values = [pe_dBm, fspl + pertes, pr]
        colors = ["#6fa8dc", "#f4cccc", "#93c47d"]

        ax.bar(labels, values, color=colors)
        ax.set_ylabel("dBm / dB")
        ax.set_title("📊 Bilan de Puissance Liaison Hertienne")
        st.pyplot(fig)

        # Sauvegarde graphe
        graph_path = "graph_hertienne.png"
        fig.savefig(graph_path)
        st.session_state.hertienne_graph_path = graph_path


# === MODULE FIBRE OPTIQUE ===
elif network_type == "Liaison Optique":
    st.header("🔦 Liaison Fibre Optique")
    pin = st.number_input("Puissance d'entrée (dBm)", value=-10.0)
    longueur = st.number_input("Longueur de fibre (km)", value=2.0)
    atten_fibre = st.number_input("Atténuation fibre (dB/km)", value=1.0)
    pertes_connecteurs = st.number_input("Pertes connecteurs (dB)", value=0.7)
    pertes_epissures = st.number_input("Pertes épissures (dB)", value=0.7)
    sensibilite_rx = st.number_input("Sensibilité du récepteur (dBm)", value=-20.0)

    if st.button("Calculer puissance reçue optique"):
        total_pertes = longueur * atten_fibre + pertes_connecteurs + pertes_epissures
        pout = pin - total_pertes
        marge = pout - sensibilite_rx
        st.success(f"Pertes totales = {total_pertes:.2f} dB")
        st.success(f"Puissance reçue = {pout:.2f} dBm")
        st.info(f"Marge de puissance = {marge:.2f} dB")

        st.session_state.rapport_data.append([
            "Optique", f"Longueur: {longueur} km, Atténuation: {atten_fibre} dB/km",
            f"Pout: {pout:.2f} dBm, Marge: {marge:.2f} dB"
        ])

        # Graphe optique
        fig, ax = plt.subplots()
        labels = ["Puissance entrée", "Pertes totales", "Puissance reçue"]
        values = [pin, total_pertes, pout]
        colors = ["#6fa8dc", "#f4cccc", "#93c47d"]

        ax.bar(labels, values, color=colors)
        ax.set_ylabel("dBm / dB")
        ax.set_title("📊 Bilan Puissance Liaison Fibre Optique")
        st.pyplot(fig)

        # Sauvegarde graphe
        graph_path = "graph_optique.png"
        fig.savefig(graph_path)
        st.session_state.optique_graph_path = graph_path


# === MODULE LTE ===
elif network_type == "Dimensionnement LTE":
    st.header("📱 Dimensionnement LTE")
    debit_utilisateur = st.number_input("Débit moyen par utilisateur (Mbps)", value=5.0)
    nb_utilisateurs = st.number_input("Nombre d'utilisateurs", value=1000)
    capacite_cellule = st.number_input("Capacité d'une cellule LTE (Mbps)", value=100.0)

    if st.button("Calculer le nombre de cellules LTE nécessaires"):
        debit_total = debit_utilisateur * nb_utilisateurs
        nb_cellules_lte = math.ceil(debit_total / capacite_cellule)
        st.success(f"Débit total requis : {debit_total:.2f} Mbps")
        st.success(f"Nombre minimal de cellules LTE : {nb_cellules_lte}")

        st.session_state.rapport_data.append([
            "LTE", f"Utilisateurs: {nb_utilisateurs}, Débit/utilisateur: {debit_utilisateur} Mbps",
            f"Capacité/cellule: {capacite_cellule} Mbps, Cellules nécessaires: {nb_cellules_lte}"
        ])

        # Graphe LTE
        fig, ax = plt.subplots()
        labels = ["Débit total requis (Mbps)", "Capacité cellule (Mbps)", "Cellules nécessaires"]
        values = [debit_total, capacite_cellule, nb_cellules_lte]
        colors = ["#6fa8dc", "#f4cccc", "#93c47d"]

        ax.bar(labels, values, color=colors)
        ax.set_title("📊 Dimensionnement LTE")
        st.pyplot(fig)

        # Sauvegarde graphe
        graph_path = "graph_lte.png"
        fig.savefig(graph_path)
        st.session_state.lte_graph_path = graph_path


# === AFFICHAGE DES DONNÉES SAISIES ===
if st.session_state.rapport_data:
    st.sidebar.markdown("### 📋 Aperçu du rapport")
    for entry in st.session_state.rapport_data:
        st.sidebar.write(f"- **{entry[0]}** : {entry[1]} / {entry[2]}")

# === GÉNÉRATION DU PDF ===
if st.sidebar.button("📄 Générer Rapport PDF") and st.session_state.rapport_data:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Rapport de Dimensionnement - TelecomPlanner+", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    pdf.multi_cell(0, 10, "Hypothèses utilisées :\n- FSPL = 20log10(d) + 20log10(f) + 92.45 (f en GHz, d en km)\n- Capacité GSM = Cellules × (Canaux/N)\n- Atténuation optique = distance × a + connecteurs + épissures\n")
    pdf.ln(5)

    for section in st.session_state.rapport_data:
        pdf.cell(0, 10, f"[ {section[0]} ]", ln=True)
        pdf.multi_cell(0, 10, f"{section[1]}\n{section[2]}")
        pdf.ln(5)

    rapport_path = "rapport_dimensionnement.pdf"
    pdf.output(rapport_path)

    with open(rapport_path, "rb") as f:
        st.sidebar.download_button(
            label="📥 Télécharger le rapport PDF",
            data=f,
            file_name=rapport_path,
            mime="application/pdf"
        )

    os.remove(rapport_path)
