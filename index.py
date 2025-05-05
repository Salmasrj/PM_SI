import streamlit as st


# PAGE CONFIGURATION MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Prestige Motors - Gestion de Stock",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import all other libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
from datetime import datetime, timedelta
from streamlit_extras.metric_cards import style_metric_cards

    # On importe les fonctions de notre page web
from fonctions import load_csv_data, calculate_summary_metrics

    # On importe le modèle de prédiction de prix de voiture
from fonctions import CarPricePredictor
# Initialiser et entraîner le modèle
price_predictor = CarPricePredictor()
results = price_predictor.train("data.csv")
st.session_state.price_predictor = price_predictor
from fonctions import estimate_price

    # On importe les données de stock et leurs fonctions issues du diagramme d'activite algo
from fonctions import Capacite
from fonctions import NombreVehicules
from fonctions import diagA_Algo_Actions
# Créer une instance de la classe
algo_actions = diagA_Algo_Actions(Capacite, NombreVehicules)

# Define color palette for Prestige Motors
COLOR_PALETTE = {
    # Main colors
    "dark_blue": "#1A2A57",
    "blue": "#2E4172",
    "light_blue": "#6384B3",
    "gold": "#D4AF37",
    "silver": "#C0C0C0",
    "black": "#222222",
    "white": "#FFFFFF",
    
    # Status colors
    "in_stock": "#2E7D32",  # green
    "reserved": "#FF9800",  # orange
    "sold": "#D32F2F",      # red
    
    # Chart colors
    "luxury": "#D4AF37",    # gold
    "sport": "#FF5252",     # red
    "suv": "#43A047",       # green
    "sedan": "#1E88E5",     # blue
    "other": "#757575",     # gray
    
    # Indicators
    "success": "#2E7D32",   # green
    "warning": "#FF9800",   # orange
    "danger": "#D32F2F",    # red
    "info": "#1976D2",      # blue
    "neutral": "#757575"    # gray
}

# Initialize session state
if "selected_car" not in st.session_state:
    st.session_state.selected_car = None
if "filter_brand" not in st.session_state:
    st.session_state.filter_brand = "Tous"
if "filter_status" not in st.session_state:
    st.session_state.filter_status = "Tous"
if "price_range" not in st.session_state:
    st.session_state.price_range = [0, 1000000]
if "year_range" not in st.session_state:
    st.session_state.year_range = [1990, 2025]

# Load data
stock_data = load_csv_data("data.csv")
summary_metrics = calculate_summary_metrics(stock_data)


# Page header
st.title("🚗 Gestion de Stock - Prestige Motors 🚗")

# Top level navigation with tabs
tab_titles = ["📊 Tableau de bord", "📋 Liste des véhicules"]
tabs = st.tabs(tab_titles)

# Sidebar
with st.sidebar:
    st.title("Prestige Motors")
    
    # Filters for the data
    st.header("⚙️ Filtres")
    
    # Brand filter
    all_brands = ["Tous"] + sorted(stock_data["Marque"].unique().tolist())
    selected_brand = st.selectbox("Marque", all_brands, index=0)
    
    # Status filter
    all_statuses = ["Tous"] + sorted(stock_data["Statut"].unique().tolist())
    selected_status = st.selectbox("Statut", all_statuses, index=0)
    
    # Price range filter
    min_price = int(stock_data["Prix de vente"].min())
    max_price = int(stock_data["Prix de vente"].max())
    price_range = st.slider(
        "Plage de prix (€)",
        min_price, max_price, (min_price, max_price)
    )
    
    # Year range filter
    min_year = int(stock_data["Année"].min())
    max_year = int(stock_data["Année"].max())
    year_range = st.slider(
        "Année du véhicule",
        min_year, max_year, (min_year, max_year)
    )
    
    # Apply filters button
    if st.button("Appliquer les filtres"):
        st.session_state.filter_brand = selected_brand
        st.session_state.filter_status = selected_status
        st.session_state.price_range = price_range
        st.session_state.year_range = year_range
        st.rerun()
    
    # Reset filters button
    if st.button("Réinitialiser les filtres"):
        st.session_state.filter_brand = "Tous"
        st.session_state.filter_status = "Tous"
        st.session_state.price_range = [min_price, max_price]
        st.session_state.year_range = [min_year, max_year]
        st.rerun()
    
   
    # Contact info
    st.markdown("---")
    st.caption("© 2025 Prestige Motors")
    st.caption("📞 Contact: +33 1 23 45 67 89")

# Apply filters to the dataframe
filtered_data = stock_data.copy()

if st.session_state.filter_brand != "Tous":
    filtered_data = filtered_data[filtered_data["Marque"] == st.session_state.filter_brand]

if st.session_state.filter_status != "Tous":
    filtered_data = filtered_data[filtered_data["Statut"] == st.session_state.filter_status]

filtered_data = filtered_data[
    (filtered_data["Prix de vente"] >= st.session_state.price_range[0]) & 
    (filtered_data["Prix de vente"] <= st.session_state.price_range[1])
]

filtered_data = filtered_data[
    (filtered_data["Année"] >= st.session_state.year_range[0]) & 
    (filtered_data["Année"] <= st.session_state.year_range[1])
]

# Ajouter après les imports, avant le début des tabs
# Système de notification global
if "notification" not in st.session_state:
    st.session_state.notification = {"type": None, "message": None, "time": None}

# Afficher la notification si elle existe et est récente (moins de 5 secondes)
if st.session_state.notification["message"]:
    current_time = datetime.now()
    notification_time = st.session_state.notification["time"]
    
    # Si la notification date de moins de 5 secondes
    if notification_time and (current_time - notification_time).total_seconds() < 5:
        # Création d'un conteneur flottant pour la notification
        st.markdown(
            f"""
            <div style="position: fixed; top: 70px; right: 20px; z-index: 1000; 
                       padding: 10px 20px; background-color: {'#4CAF50' if st.session_state.notification['type'] == 'success' else '#F44336'}; 
                       color: white; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <p style="margin: 0; font-weight: bold;">{st.session_state.notification["message"]}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # Réinitialiser la notification après 5 secondes
        st.session_state.notification = {"type": None, "message": None, "time": None}

# Tab 1: Dashboard Overview
with tabs[0]:
    st.header("📊 Tableau de bord du stock")
    
    # Action buttons in the main area
    col1, col2, col3 = st.columns(3)

    with col1:
        # Initialiser l'état du formulaire d'achat si nécessaire
        if "show_purchase_form" not in st.session_state:
            st.session_state.show_purchase_form = False
        
        # Bouton pour afficher/masquer le formulaire d'achat
        if st.button("🛒 Achat de véhicule", use_container_width=True):
            st.session_state.show_purchase_form = True
        
        # Afficher le formulaire si l'état est activé
        if st.session_state.show_purchase_form:
            with st.form("achat_vehicule_form"):
                st.subheader("Formulaire d'achat de véhicule")
                
                # Type de véhicule (neuf ou occasion)
                vehicle_type = st.radio("Type de véhicule", ["Neuf", "Occasion"])
                
                # Informations de base du véhicule
                form_col1, form_col2 = st.columns(2)
                with form_col1:
                    vehicle_id = st.text_input("ID du véhicule", value=f"PM{np.random.randint(1000, 9999)}")
                    brand = st.selectbox("Marque", ["Mercedes", "BMW", "Audi", "Porsche", "Ferrari", "Lamborghini", "Bentley", "Maserati", "Rimac"])
                    model = st.text_input("Modèle")
                    year = st.number_input("Année", min_value=2000, max_value=2025, value=2023)
                
                with form_col2:
                    mileage = st.number_input("Kilométrage", min_value=0, value=5000)
                    purchase_price = st.number_input("Prix d'achat (€)", min_value=0, value=50000, step=1000)
                    selling_price = st.number_input("Prix de vente estimé (€)", min_value=0, value=int(purchase_price * 1.2), step=1000)
                    condition = st.selectbox("État", ["neuf", "occasion"])
                
                # Emplacement et statut
                form_col3, form_col4 = st.columns(2)
                with form_col3:
                    location = st.selectbox("Emplacement", ["parc", "showroom"], index=0)
                    status = st.selectbox("Statut", ["en stock", "réservé", "vendu"], index=0)
                
                with form_col4:
                    category = st.selectbox("Catégorie", ["Luxury", "Sport", "SUV", "Sedan", "Other"], index=0)
                    st.info("La catégorie sera automatiquement ajustée selon la marque et le modèle")
                
                # Informations sur les pièces
                st.subheader("État des pièces et composants")
                st.info("Sélectionnez deux pièces principales et leur importance")
                
                # Liste des pièces disponibles
                pieces_list = ["Moteur", "Transmission", "Freins", "Suspension", "Carrosserie", "Intérieur", 
                              "Électronique", "Batterie", "Moteurs électriques", "Aérodynamique"]
                
                # Création de deux colonnes pour les sélections
                pieces_col1, pieces_col2 = st.columns(2)
                
                # Première pièce
                with pieces_col1:
                    piece1 = st.selectbox("Première pièce importante", pieces_list, key="piece1")
                    importance1 = st.select_slider(
                        f"Importance de {piece1}",
                        options=[1, 2, 3, 4, 5],
                        value=4,
                        key="importance1"
                    )
                
                # Deuxième pièce (filtrer pour éviter les doublons)
                with pieces_col2:
                    # Créer une liste sans la première pièce sélectionnée
                    remaining_pieces = [p for p in pieces_list if p != piece1]
                    piece2 = st.selectbox("Deuxième pièce importante", remaining_pieces, key="piece2")
                    importance2 = st.select_slider(
                        f"Importance de {piece2}",
                        options=[1, 2, 3, 4, 5],
                        value=5,
                        key="importance2"
                    )
                
                # Créer les données des pièces
                pieces_data = [
                    {"nom_pièce": piece1, "importance_pièce": importance1},
                    {"nom_pièce": piece2, "importance_pièce": importance2}
                ]
                
                # Créer un dictionnaire pour le véhicule dans le format attendu
                vehicle_data = {
                    "ID": vehicle_id,
                    "Marque": brand,
                    "Model": model,  # Utiliser "Model" au lieu de "Modèle"
                    "Année": year,
                    "État": condition.lower(),
                    "ValeurEntrée": float(purchase_price),
                    "Emplacement": location.lower(),
                    "Statut": status.capitalize(),  # Capitaliser pour cohérence
                    "Jours avant sortie du stock": "",
                    "Kilométrage": mileage,
                    "Pièces": json.dumps(pieces_data, ensure_ascii=False),  # ensure_ascii=False pour conserver les accents
                    "ValeurSortie": float(selling_price),
                    "Modèle": "",  # Laisser vide
                    "Prix d'achat": "",  # Laisser vide
                    "Prix de vente": "",  # Laisser vide
                    "Marge": "",  # Laisser vide
                    "Date d'achat": "",  # Laisser vide
                    "Catégorie": "",
                    "Disponibilité": "Disponible" if status.lower() == "en stock" else "Non disponible"
                }
                # Boutons du formulaire
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    cancel = st.form_submit_button("Annuler", use_container_width=True)
                    if cancel:
                        st.session_state.show_purchase_form = False
                        st.rerun()
                
                with btn_col2:
                    submit = st.form_submit_button("Confirmer l'achat", use_container_width=True)
                
                # Traitement après soumission
                if submit:
                    # Déterminer la catégorie automatiquement
                    if brand in ["Ferrari", "Lamborghini", "Porsche"] and not any(suv in model.lower() for suv in ["cayenne", "urus"]):
                        vehicle_data["Catégorie"] = "Sport"
                    elif brand in ["Bentley", "Mercedes"] and any(lux in model.lower() for lux in ["classe s", "continental", "flying spur"]):
                        vehicle_data["Catégorie"] = "Luxury"
                    elif any(suv in model.lower() for suv in ["gle", "x5", "q7", "cayenne", "urus", "bentayga", "levante"]):
                        vehicle_data["Catégorie"] = "SUV"
                    elif any(sedan in model.lower() for sedan in ["classe e", "série 5", "a6", "panamera", "ghibli", "quattroporte"]):
                        vehicle_data["Catégorie"] = "Sedan"
                    
                    # Appeler la méthode ActionVenteAchat avec type d'opération "achat"
                    operation = ["achat", vehicle_type.lower()]
                    message = algo_actions.ActionVenteAchat(operation, vehicle_data)
                    
                    # Afficher le message retourné par la méthode
                    if "ajouté" in message:
                        # Enregistrer la notification dans le session state
                        st.session_state.notification = {
                            "type": "success",
                            "message": message,
                            "time": datetime.now()
                        }
                        
                        # Fermer le formulaire après un achat réussi
                        st.session_state.show_purchase_form = False
                        st.rerun()
                    else:
                        # Enregistrer la notification d'erreur
                        st.session_state.notification = {
                            "type": "error",
                            "message": message,
                            "time": datetime.now()
                        }

    with col2:
        # Initialiser l'état du formulaire de vente si nécessaire
        if "show_sale_form" not in st.session_state:
            st.session_state.show_sale_form = False
        
        # Bouton pour afficher/masquer le formulaire de vente
        if st.button("💰 Vente de véhicule", use_container_width=True):
            st.session_state.show_sale_form = True
        
        # Afficher le formulaire si l'état est activé
        
        if st.session_state.show_sale_form:
        # Initialize vehicle selection outside the form if not already done
            if "selected_sale_vehicle_id" not in st.session_state:
                st.session_state.selected_sale_vehicle_id = None
            
            # Get vehicles in stock
            vehicles_in_stock = filtered_data[filtered_data["Statut"] == "En stock"]
            
            if len(vehicles_in_stock) == 0:
                st.warning("Aucun véhicule en stock disponible pour la vente")
            else:
                # Vehicle selection outside the form
                selected_vehicle_id = st.selectbox(
                    "Sélectionner un véhicule à vendre",
                    options=vehicles_in_stock["ID"].tolist(),
                    format_func=lambda x: f"{x} - {vehicles_in_stock[vehicles_in_stock['ID'] == x]['Marque'].iloc[0]} {vehicles_in_stock[vehicles_in_stock['ID'] == x]['Modèle'].iloc[0]}",
                    key="vehicle_sale_selector"
                )
                
                # Update session state with selected vehicle ID
                if st.session_state.selected_sale_vehicle_id != selected_vehicle_id:
                    st.session_state.selected_sale_vehicle_id = selected_vehicle_id
                    st.rerun()
                
                # Get the vehicle details based on the selection
                selected_vehicle = vehicles_in_stock[vehicles_in_stock["ID"] == selected_vehicle_id].iloc[0].to_dict()
                
                # Show vehicle details outside the form
                st.markdown("### Détails du véhicule")
                
                # Create columns for vehicle details
                detail_cols = st.columns(3)
                
                # First column - Basic information
                with detail_cols[0]:
                    if "Marque" in selected_vehicle:
                        st.metric("Marque", selected_vehicle["Marque"])
                    if "Modèle" in selected_vehicle:
                        st.metric("Modèle", selected_vehicle["Modèle"])
                    if "Catégorie" in selected_vehicle:
                        st.metric("Catégorie", selected_vehicle["Catégorie"])
                
                # Second column - Technical specifications
                with detail_cols[1]:
                    if "Année" in selected_vehicle:
                        st.metric("Année", selected_vehicle["Année"])
                    if "Kilométrage" in selected_vehicle:
                        st.metric("Kilométrage", f"{selected_vehicle['Kilométrage']} km")
                    if "État" in selected_vehicle:
                        st.metric("État", selected_vehicle["État"])
                
                # Third column - Financial information
                with detail_cols[2]:
                    if "Prix d'achat" in selected_vehicle:
                        st.metric("Prix d'achat", f"{selected_vehicle['Prix d\'achat']} €")
                    if "Prix de vente" in selected_vehicle:
                        st.metric("Prix de vente", f"{selected_vehicle['Prix de vente']} €")
                    marge = selected_vehicle.get("Prix de vente", 0) - selected_vehicle.get("Prix d'achat", 0)
                    st.metric("Marge estimée", f"{marge} €")
                
                # CSS to reduce metric text size
                st.markdown("""
                <style>
                [data-testid="stMetricValue"] {
                    font-size: 1rem !important;
                }
                [data-testid="stMetricLabel"] {
                    font-size: 0.8rem !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Now the form for the sale process
                with st.form("vente_vehicule_form"):
                    st.subheader("Confirmer la vente")
                    
                    # Option to adjust final sale price
                    final_sale_price = st.number_input(
                        "Prix de vente final (€)",
                        min_value=0,
                        value=int(selected_vehicle.get("Prix de vente", 0)),
                        step=1000
                    )
                    
                    # Update the sale price and margin
                    selected_vehicle_for_form = selected_vehicle.copy()
                    selected_vehicle_for_form["Prix de vente"] = final_sale_price
                    selected_vehicle_for_form["Marge"] = final_sale_price - selected_vehicle_for_form.get("Prix d'achat", 0)
                    
                    # Form buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        cancel = st.form_submit_button("Annuler", use_container_width=True)
                        if cancel:
                            st.session_state.show_sale_form = False
                            st.rerun()
                    
                    with col2:
                        submit = st.form_submit_button("Confirmer la vente", use_container_width=True)
                    
                    # Process form submission
                    if submit:
                        # Call the ActionVenteAchat method with operation type "vente"
                        operation = ["vente", ""]
                        message = algo_actions.ActionVenteAchat(operation, selected_vehicle_for_form)
                        
                        # Create a more visible notification that persists across reruns
                        if "retiré" in message:
                            # Enregistrer la notification dans le session state
                            st.session_state.notification = {
                                "type": "success",
                                "message": message,
                                "time": datetime.now()
                            }
                            
                            # Close the form after a successful sale
                            st.session_state.show_sale_form = False
                            st.rerun()
                        else:
                            # Enregistrer la notification d'erreur
                            st.session_state.notification = {
                                "type": "error",
                                "message": message,
                                "time": datetime.now()
                            }
    with col3:
        if "show_price_estimation" not in st.session_state:
            st.session_state.show_price_estimation = False
            
        if st.button("💹 Estimation de prix", use_container_width=True):
            st.session_state.show_price_estimation = True
        
        # Afficher l'interface d'estimation si le bouton a été cliqué
        if st.session_state.show_price_estimation:
            st.subheader("💹 Estimation du prix d'un véhicule")
            
            # Créer une interface sans utiliser de formulaire
            col1, col2 = st.columns(2)
            
            with col1:
                annee = st.number_input("Année du véhicule", min_value=2000, max_value=2030, value=2023)
                valeur_entree = st.number_input("Prix d'achat (€)", min_value=0, value=50000, step=1000)
            
            with col2:
                kilometrage = st.number_input("Kilométrage", min_value=0, value=5000, step=1000)
                marque = st.selectbox("Marque", options=["Mercedes", "BMW", "Audi", "Porsche", "Ferrari", "Lamborghini", "Bentley", "Maserati"])
            
            st.subheader("État des pièces et composants")
            st.info("Indiquez l'importance et l'état des pièces principales du véhicule")
            
            col1, col2 = st.columns(2)
            
            pieces = []
            unique_pieces = ["Moteur", "Transmission", "Freins", "Suspension", "Carrosserie", "Intérieur", "Électronique"]
            
            # Créer des contrôles pour chaque pièce
            for i, piece in enumerate(unique_pieces):
                with col1 if i % 2 == 0 else col2:
                    importance = st.slider(f"Importance de {piece}", 1, 5, 3)
                    pieces.append({"nom_pièce": piece, "importance_pièce": importance})
            
            st.markdown("---")
            
            # Use a more logical button layout
            estimate_btn = st.button("Calculer l'estimation", type="primary", use_container_width=True)
            cancel_btn = st.button("Annuler", use_container_width=True)
            
            if cancel_btn:
                st.session_state.show_price_estimation = False
                st.rerun()
                
            if estimate_btn:
                try:
                    estimated_price = st.session_state.price_predictor.predict(
                        annee, valeur_entree, kilometrage, pieces
                    )
                    
                    # Calculer une fourchette de prix (±5%)
                    price_min = estimated_price * 0.95
                    price_max = estimated_price * 1.05
                    
                    # Show results in a nice container with better formatting
                    with st.container():
                        st.success(f"### Prix estimé: {estimated_price:,.2f} €")
                        st.info(f"Fourchette recommandée: {price_min:,.2f} € - {price_max:,.2f} €")
                    
                    # Organize metrics in a cleaner layout
                    metric_cols = st.columns(3)
                    with metric_cols[0]:
                        marge = estimated_price - valeur_entree
                        marge_percent = (marge / valeur_entree) * 100 if valeur_entree > 0 else 0
                        st.metric("Marge potentielle", f"{marge:,.2f} €", f"{marge_percent:.1f}%")
                    
                    with metric_cols[1]:
                        marche_actuel = estimated_price * 0.98  # Simuler prix du marché
                        diff = estimated_price - marche_actuel
                        diff_percent = (diff / marche_actuel) * 100
                        st.metric("Comparaison marché", f"{marche_actuel:,.2f} €", f"{diff_percent:.1f}%")
                    
                    with metric_cols[2]:
                        st.metric("Prix au km", f"{estimated_price / kilometrage:.2f} €/km" if kilometrage > 0 else "N/A")
                    
                    # Add CSS to make metrics more compact and readable
                    st.markdown("""
                    <style>
                    [data-testid="stMetricValue"] {
                        font-size: 1rem !important;
                    }
                    [data-testid="stMetricDelta"] {
                        font-size: 0.8rem !important;
                    }
                    [data-testid="stMetricLabel"] {
                        font-size: 0.8rem !important;
                        font-weight: bold !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erreur lors de l'estimation du prix: {str(e)}")
                    st.error("Veuillez vérifier que le modèle a été correctement entraîné avec les données")
        
    st.markdown("---")

    st.markdown("""
    <style>
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Capacité du parc", f"{Capacite[0]}/140", f"{Capacite[2]:.1f}%")
    
    with col2:
        st.metric("Capacité du showroom", f"{Capacite[1]}/60", f"{Capacite[3]:.1f}%")
        if Capacite[3] > 100:
            st.warning(f"⚠️ Showroom en surcapacité: {Capacite[3]:.1f}%")
    
    with col3:
        st.metric("Prix moyen", f"{summary_metrics['avg_price']:,.0f} €", delta=None, delta_color="normal", help=None, label_visibility="visible")
    
    with col4:
        st.metric("Marge potentielle", f"{summary_metrics['potential_margin']:,.0f} €", delta=None, delta_color="normal", help=None, label_visibility="visible")
    
    # Style metrics
    style_metric_cards(
        background_color="#FFFFFF",
        border_left_color=COLOR_PALETTE["blue"],
        border_color="#FFFFFF",
        box_shadow=True
    )
    
    # Top row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory by brand
        st.subheader("Stock par marque")
        brand_counts = filtered_data[filtered_data["Statut"] == "En stock"]["Marque"].value_counts().reset_index()
        brand_counts.columns = ["Marque", "Nombre"]
        
        fig = px.bar(
            brand_counts,
            x="Marque",
            y="Nombre",
            color="Marque",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="",
            yaxis_title="Nombre de véhicules"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales performance by month
        st.subheader("Performance des ventes")
        
        # Convert dates and create month column
        df_sales = filtered_data[filtered_data["Statut"] == "Vendu"].copy()
        df_sales["Date"] = pd.to_datetime(df_sales["Date d'achat"])
        df_sales["Mois"] = df_sales["Date"].dt.strftime("%Y-%m")
        
        # Group by month and count
        sales_by_month = df_sales.groupby("Mois").size().reset_index()
        sales_by_month.columns = ["Mois", "Ventes"]
        
        # Sort by month
        sales_by_month = sales_by_month.sort_values("Mois")
        
        fig = px.line(
            sales_by_month,
            x="Mois",
            y="Ventes",
            markers=True,
            line_shape="linear"
        )
        
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=30),
            xaxis_title="",
            yaxis_title="Nombre de ventes"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity table
    st.subheader("Activité récente")
    
    # Sort by purchase date to get the most recent entries
    recent_activity = filtered_data.sort_values("Date d'achat", ascending=False).head(5)
    
    # Show recent activity table
    st.dataframe(
        recent_activity[["ID", "Marque", "Modèle", "Prix de vente", "Statut", "Date d'achat"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Prix de vente": st.column_config.NumberColumn("Prix de vente", format="%.0f €"),
            "Date d'achat": "Date d'achat"
        }
    )

# Tab 2: Vehicle List
with tabs[1]:
    st.header("📋 Liste des véhicules")
    
    # Actions bar
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✏️ Modifier", use_container_width=True):
            st.info("Sélectionnez un véhicule dans le tableau puis modifiez ses informations")
    
    with col2:
        if st.button("❌ Supprimer", use_container_width=True):
            st.warning("Sélectionnez un véhicule dans le tableau pour le supprimer")
            with st.expander("Confirmation de suppression"):
                vehicle_to_delete = st.selectbox(
                    "Choisir le véhicule à supprimer",
                    options=filtered_data["ID"].tolist(),
                    format_func=lambda x: f"{x} - {filtered_data[filtered_data['ID'] == x]['Marque'].iloc[0]} {filtered_data[filtered_data['ID'] == x]['Modèle'].iloc[0]}"
                )
                if st.button("Confirmer la suppression", type="primary"):
                    # Appeler la méthode de suppression avec l'ID sélectionné
                    vehicle_to_remove = filtered_data[filtered_data["ID"] == vehicle_to_delete].iloc[0].to_dict()
                    message = algo_actions.ActionVenteAchat(["vente", ""], vehicle_to_remove)
                    st.success(message)
                    st.rerun()
    
    with col3:
        search_query = st.text_input("Rechercher un véhicule", placeholder="Entrez l'ID, la marque ou le modèle")
    
    # Apply search filter if provided
    if search_query:
        search_filter = (
            filtered_data["ID"].str.contains(search_query, case=False) |
            filtered_data["Marque"].str.contains(search_query, case=False) |
            filtered_data["Modèle"].str.contains(search_query, case=False)
        )
        filtered_data = filtered_data[search_filter]
    
    # Filtres supplémentaires avec des expanders
    with st.expander("Filtres avancés"):
        filter_cols = st.columns(4)
        
        with filter_cols[0]:
            status_filter = st.multiselect(
                "Statut", 
                options=["En stock", "Réservé", "Vendu"],
                default=[]
            )
        
        with filter_cols[1]:
            location_filter = st.multiselect(
                "Emplacement", 
                options=["parc", "showroom"],
                default=[]
            )
            
        with filter_cols[2]:
            min_year = int(filtered_data["Année"].min())
            max_year = int(filtered_data["Année"].max())
            year_range = st.slider(
                "Année", 
                min_value=min_year, 
                max_value=max_year,
                value=(min_year, max_year)
            )
            
        with filter_cols[3]:
            state_filter = st.multiselect(
                "État", 
                options=["neuf", "occasion"],
                default=[]
            )
    
        # Appliquer les filtres avancés
        if status_filter:
            filtered_data = filtered_data[filtered_data["Statut"].isin(status_filter)]
        
        if location_filter:
            filtered_data = filtered_data[filtered_data["Emplacement"].isin(location_filter)]
            
        if year_range:
            filtered_data = filtered_data[(filtered_data["Année"] >= year_range[0]) & 
                                         (filtered_data["Année"] <= year_range[1])]
            
        if state_filter:
            filtered_data = filtered_data[filtered_data["État"].isin(state_filter)]
    
    # Configuration pour l'affichage des données
    try:
        # Convertir la date en format datetime (si présente)
        if "Date d'achat" in filtered_data.columns:
            filtered_data["Date d'achat"] = pd.to_datetime(filtered_data["Date d'achat"])
        
        # Afficher le tableau de véhicules
        edited_data = st.data_editor(
            filtered_data,
            hide_index=True,
            use_container_width=True,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Marque": st.column_config.TextColumn("Marque", width="medium"),
                "Modèle": st.column_config.TextColumn("Modèle", width="medium"),
                "Année": st.column_config.NumberColumn("Année", width="small"),
                "Kilométrage": st.column_config.NumberColumn("Kilométrage", format="%d km", width="medium"),
                "Prix d'achat": st.column_config.NumberColumn("Prix d'achat", format="%d €", width="medium"),
                "Prix de vente": st.column_config.NumberColumn("Prix de vente", format="%d €", width="medium"),
                "Marge": st.column_config.NumberColumn("Marge", format="%d €", width="medium"),
                "Date d'achat": st.column_config.DateColumn("Date d'achat", width="medium"),
                "Statut": st.column_config.SelectboxColumn(
                    "Statut",
                    options=["En stock", "Réservé", "Vendu"],
                    width="medium"
                ),
                "Emplacement": st.column_config.SelectboxColumn(
                    "Emplacement",
                    options=["parc", "showroom"],
                    width="medium"
                ),
                "État": st.column_config.SelectboxColumn(
                    "État", 
                    options=["neuf", "occasion"],
                    width="medium"
                ),
                "Catégorie": st.column_config.TextColumn("Catégorie", width="medium"),
                "Disponibilité": st.column_config.TextColumn("Disponibilité", width="medium")
            },
            num_rows="dynamic"
        )
        
        # Vérifier si des modifications ont été apportées et mettre à jour les données
        if not edited_data.equals(filtered_data):
            st.success("Modifications enregistrées!")
            # Vous pouvez ajouter ici le code pour sauvegarder les modifications dans data.csv
            
    except Exception as e:
        st.error(f"Erreur lors de l'affichage des données: {e}")
        st.write(filtered_data.head())
    
    # Afficher des statistiques sur les résultats
    st.caption(f"{len(filtered_data)} véhicules affichés sur un total de {len(stock_data)}")