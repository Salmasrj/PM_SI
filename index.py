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
from datetime import datetime, timedelta
from streamlit_extras.metric_cards import style_metric_cards

    # On importe les fonctions de notre page web
from fonctions import load_stock_data, calculate_summary_metrics

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
    st.session_state.year_range = [2000, 2025]

# Load data
stock_data = load_stock_data()
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

# Tab 1: Dashboard Overview
with tabs[0]:
    st.header("📊 Tableau de bord du stock")
    
    # Action buttons in the main area
    col1, col2, col3 = st.columns(3)
    
    # Remplacer le bouton d'achat actuel par:

    with col1:
        if st.button("🛒 Achat de véhicule", use_container_width=True):
            with st.form("achat_vehicule_form"):
                st.subheader("Formulaire d'achat de véhicule")
                
                # Type de véhicule (neuf ou occasion)
                vehicle_type = st.radio("Type de véhicule", ["Neuf", "Occasion"])
                
                # Informations de base du véhicule
                col1, col2 = st.columns(2)
                with col1:
                    vehicle_id = st.text_input("ID du véhicule", value=f"PM{np.random.randint(1000, 9999)}")
                    brand = st.selectbox("Marque", ["Mercedes", "BMW", "Audi", "Porsche", "Ferrari", "Lamborghini", "Bentley", "Maserati"])
                    model = st.text_input("Modèle")
                    year = st.number_input("Année", min_value=2000, max_value=2025, value=2023)
                
                with col2:
                    mileage = st.number_input("Kilométrage", min_value=0, value=5000)
                    purchase_price = st.number_input("Prix d'achat (€)", min_value=0, value=50000)
                    selling_price = st.number_input("Prix de vente estimé (€)", min_value=0, value=int(purchase_price * 1.2))
                    condition = st.selectbox("État", ["Excellent", "Bon", "Correct"])
                
                # Créer un dictionnaire pour le véhicule
                vehicle_data = {
                    "ID": vehicle_id,
                    "Marque": brand,
                    "Modèle": model,
                    "Année": year,
                    "Kilométrage": mileage,
                    "Prix d'achat": purchase_price,
                    "Prix de vente": selling_price,
                    "Marge": selling_price - purchase_price,
                    "Date d'achat": datetime.now().strftime('%Y-%m-%d'),
                    "Statut": "En stock",
                    "Catégorie": "Luxury",  # À déterminer automatiquement selon la marque/modèle
                    "État": condition,
                    "Disponibilité": "Disponible"
                }
                
                submit = st.form_submit_button("Confirmer l'achat", use_container_width=True)
                
                if submit:
                    # Appeler la méthode ActionVenteAchat avec type d'opération "achat"
                    operation = ["achat", vehicle_type.lower()]
                    message = algo_actions.ActionVenteAchat(operation, vehicle_data)
                    
                    # Afficher le message retourné par la méthode
                    if "ajouté" in message:
                        st.success(message)
                    else:
                        st.error(message)
                    
                    # Mettre à jour les données
                    if "ajouté" in message:
                        st.rerun()
        
        # Remplacer le bouton de vente actuel par:

    with col2:
        if st.button("💰 Vente de véhicule", use_container_width=True):
            with st.form("vente_vehicule_form"):
                st.subheader("Formulaire de vente de véhicule")
                
                # Récupérer uniquement les véhicules en stock
                vehicles_in_stock = filtered_data[filtered_data["Statut"] == "En stock"]
                
                if len(vehicles_in_stock) == 0:
                    st.warning("Aucun véhicule en stock disponible pour la vente")
                    submit_disabled = True
                else:
                    # Sélection du véhicule à vendre
                    selected_vehicle_id = st.selectbox(
                        "Sélectionner un véhicule à vendre",
                        options=vehicles_in_stock["ID"].tolist(),
                        format_func=lambda x: f"{x} - {vehicles_in_stock[vehicles_in_stock['ID'] == x]['Marque'].iloc[0]} {vehicles_in_stock[vehicles_in_stock['ID'] == x]['Modèle'].iloc[0]}"
                    )
                    
                    # Récupérer toutes les informations du véhicule sélectionné
                    selected_vehicle = vehicles_in_stock[vehicles_in_stock["ID"] == selected_vehicle_id].iloc[0].to_dict()
                    
                    # Afficher les détails du véhicule
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Marque", selected_vehicle["Marque"])
                        st.metric("Modèle", selected_vehicle["Modèle"])
                    
                    with col2:
                        st.metric("Année", selected_vehicle["Année"])
                        st.metric("Kilométrage", f"{selected_vehicle['Kilométrage']} km")
                    
                    with col3:
                        st.metric("Prix d'achat", f"{selected_vehicle['Prix d\'achat']} €")
                        st.metric("Prix de vente", f"{selected_vehicle['Prix de vente']} €")
                    
                    # Option pour ajuster le prix de vente final
                    final_sale_price = st.number_input(
                        "Prix de vente final (€)",
                        min_value=0,
                        value=int(selected_vehicle["Prix de vente"]),
                        step=1000
                    )
                    
                    # Mettre à jour le prix de vente
                    selected_vehicle["Prix de vente"] = final_sale_price
                    selected_vehicle["Marge"] = final_sale_price - selected_vehicle["Prix d'achat"]
                    
                    submit_disabled = False
                
                submit = st.form_submit_button("Confirmer la vente", disabled=submit_disabled, use_container_width=True)
                
                if submit and not submit_disabled:
                    # Appeler la méthode ActionVenteAchat avec type d'opération "vente"
                    operation = ["vente", ""]
                    message = algo_actions.ActionVenteAchat(operation, selected_vehicle)
                    
                    # Afficher le message retourné par la méthode
                    if "retiré" in message:
                        st.success(message)
                    else:
                        st.error(message)
                    
                    # Mettre à jour les données
                    if "retiré" in message:
                        st.rerun()
    
    with col3:
        if st.button("💹 Estimation de prix", use_container_width=True):
            estimate_price(st.session_state.price_predictor)
    
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
        st.progress(Capacite[2]/100)
    
    with col2:
        st.metric("Capacité du showroom", f"{Capacite[1]}/60", f"{Capacite[3]:.1f}%")
        st.progress(Capacite[3]/100)
    
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
        st.button("✏️ Modifier", use_container_width=True)
    
    with col2:
        st.button("❌ Supprimer", use_container_width=True)
    
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
    
    # Display the data table
    # Add a selection column
    filtered_data["Date d'achat"] = pd.to_datetime(filtered_data["Date d'achat"])
    st.data_editor(
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
            "Catégorie": st.column_config.TextColumn("Catégorie", width="medium"),
            "État": st.column_config.TextColumn("État", width="medium"),
            "Disponibilité": st.column_config.TextColumn("Disponibilité", width="medium")
        }
    )
    
