import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import json
import streamlit as st

# Fonctions importées depuis index.py
def load_csv_data(file_path="data.csv"):
    """
    Charge les données depuis data.csv et les transforme au format attendu par l'application
    """
    try:
        # Charger les données
        df = pd.read_csv(file_path)
        
        # Transformation des colonnes pour correspondre au format attendu
        transformed_data = []
        
        for _, row in df.iterrows():
            # Calculer la marge (différence entre ValeurSortie et ValeurEntrée)
            marge = row['ValeurSortie'] - row['ValeurEntrée'] if pd.notna(row['ValeurSortie']) else 0
            
            # Générer une date d'achat (puisqu'elle n'existe pas dans data.csv)
            # Pour les besoins de démo, on utilise une date aléatoire dans les 365 derniers jours
            days_ago = np.random.randint(1, 365)
            purchase_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # Déterminer la catégorie basée sur la marque et le modèle
            marque = row['Marque']
            modele = row['Model']
            
            if marque in ["Ferrari", "Lamborghini", "Porsche"] and modele not in ["Cayenne", "Urus"]:
                category = "Sport"
            elif marque in ["Bentley", "Mercedes"] and modele in ["Classe S", "Continental GT", "Flying Spur"]:
                category = "Luxury"
            elif any(suv in modele for suv in ["GLE", "X5", "Q7", "Cayenne", "Urus", "Bentayga", "Levante"]):
                category = "SUV"
            elif any(sedan in modele for sedan in ["Classe E", "Série 5", "A6", "Panamera", "Ghibli", "Quattroporte"]):
                category = "Sedan"
            else:
                category = "Other"
            
            # Transformer Statut format: première lettre en majuscule et reste en minuscule
            status = row['Statut'].capitalize() if pd.notna(row['Statut']) else ""
            
            # Disponibilité basée sur le statut
            if status == "En stock":
                availability = "Disponible"
            elif status == "Réservé":
                availability = "Réservé"
            else:
                availability = "Vendu"
            
            transformed_data.append({
                "ID": row['ID'],
                "Marque": row['Marque'],
                "Modèle": row['Model'],
                "Année": int(row['Année']) if pd.notna(row['Année']) else 0,
                "Kilométrage": int(row['Kilométrage']) if pd.notna(row['Kilométrage']) else 0,
                "Prix d'achat": float(row['ValeurEntrée']) if pd.notna(row['ValeurEntrée']) else 0,
                "Prix de vente": float(row['ValeurSortie']) if pd.notna(row['ValeurSortie']) else 0,
                "Marge": marge,
                "Date d'achat": purchase_date,
                "Statut": status,
                "Catégorie": category,
                "État": row['État'] if pd.notna(row['État']) else "",
                "Disponibilité": availability,
                "Emplacement": row['Emplacement'] if pd.notna(row['Emplacement']) else ""
            })
        
        return pd.DataFrame(transformed_data)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        # Retourner un DataFrame vide en cas d'erreur
        return pd.DataFrame()

def calculate_summary_metrics(df):
    """Calculate summary metrics for dashboard"""
    total_stock = len(df[df["Statut"] == "En stock"])
    total_value = df[df["Statut"] == "En stock"]["Prix de vente"].sum()
    avg_price = df[df["Statut"] == "En stock"]["Prix de vente"].mean()
    potential_margin = df[df["Statut"] == "En stock"]["Marge"].sum()
    
    # Most popular brands in stock
    popular_brands = df[df["Statut"] == "En stock"]["Marque"].value_counts().head(5)
    
    # Inventory by category
    inventory_by_category = df[df["Statut"] == "En stock"]["Catégorie"].value_counts()
    
    # Performance metrics
    sold_last_month = len(df[(df["Statut"] == "Vendu") & 
                            (pd.to_datetime(df["Date d'achat"]) > datetime.now() - timedelta(days=30))])
    
    # Stock aging analysis - days since purchase for in-stock vehicles
    df_in_stock = df[df["Statut"] == "En stock"].copy()
    df_in_stock["Jours en stock"] = (datetime.now() - pd.to_datetime(df_in_stock["Date d'achat"])).dt.days
    avg_days_in_stock = df_in_stock["Jours en stock"].mean()
    
    return {
        "total_stock": total_stock,
        "total_value": total_value,
        "avg_price": avg_price,
        "potential_margin": potential_margin,
        "popular_brands": popular_brands,
        "inventory_by_category": inventory_by_category,
        "sold_last_month": sold_last_month,
        "avg_days_in_stock": avg_days_in_stock
    }



            # Variables definies dans l'algo du diagramme d'activité
def calculate_capacity():
    """
    Calcule la capacité du parc et du showroom en parcourant la base de données.
    La variable Capacite contient:
    [0]: Nombre de véhicules dans le parc
    [1]: Nombre de véhicules dans le showroom
    [2]: Pourcentage de remplissage du parc (sur 140 places)
    [3]: Pourcentage de remplissage du showroom (sur 60 places)
    """
    # Capacités maximales
    capacite_max_parc = 140
    capacite_max_showroom = 60
    try:
        # Charger les données du CSV
        df = pd.read_csv("data.csv")
        
        # Filtrer les véhicules qui ont un emplacement (ignorer les valeurs nulles/NaN)
        df_avec_emplacement = df[df["Emplacement"].notna()]
        
        # Compter les véhicules par emplacement (peu importe leur statut)
        nb_parc = len(df_avec_emplacement[df_avec_emplacement["Emplacement"].str.lower() == "parc"])
        nb_showroom = len(df_avec_emplacement[df_avec_emplacement["Emplacement"].str.lower() == "showroom"])
        
        # Calculer les pourcentages de remplissage
        pct_parc = (nb_parc / capacite_max_parc) * 100
        pct_showroom = (nb_showroom / capacite_max_showroom) * 100
        
        # Renvoyer la variable Capacite
        return [nb_parc, nb_showroom, pct_parc, pct_showroom]
    
    except Exception as e:
        print(f"Erreur lors du calcul de la capacité: {e}")
        # En cas d'erreur, renvoyer des valeurs par défaut
        return [0, 0, 0.0, 0.0]

# Charger la capacité depuis les données
Capacite = calculate_capacity()

# Variables définies dans l'algo du diagramme d'activité
def get_vehicles_count():
    """
    Calcule le nombre total de véhicules dans la base de données.
    
    Sortie:
        int: Nombre total de véhicules
    """
    try:
        # Charger les données du CSV
        df = pd.read_csv("data.csv")
        return len(df)
    except Exception as e:
        print(f"Erreur lors du comptage des véhicules: {e}")
        # En cas d'erreur, retourner 0
        return 0

# Calculer le nombre de véhicules et le stocker dans une variable
NombreVehicules = get_vehicles_count()


class diagA_Algo_Actions:
    def __init__(self, capacite, nombre_vehicules):
        """
        Objectif : Initialise la classe avec les variables globales requises.
        Entrée:
            capacite: Liste [nb parc, nb showroom, % parc, % showroom]
            nombre_vehicules: Nombre total de véhicules dans la BDD
        """
        self.Capacite = capacite
        self.NombreVehicules = nombre_vehicules
        self.csv_path = "data.csv"
    
    def ActionVenteAchat(self, operation, vehicule):
        """
        Objectif : Gère les opérations d'achat et de vente de véhicules.
        Entrée:
            operation: Liste [type_operation (achat/vente), type_vehicule (occasion/neuf)]
            vehicule: Dictionnaire représentant une ligne de la BDD
        Sortie:
            str: Message de confirmation ou d'erreur
        """
        Message = ""
        # Vérifier si les entrées sont valides
        if operation and vehicule and len(operation) == 2 and isinstance(vehicule, dict):
            # Vérifier le type d'opération (achat/vente)
            if operation[0].lower() == "achat":
                # Vérifier le type de véhicule (occasion/neuf)
                if operation[1].lower() == "occasion":
                    # Vérifier s'il y a de la place dans le parc
                    if self.Capacite[0] < 140:
                        #pos1 correspond à l'emplacement du véhicule dans le parc
                        pos1 = 0
                        Message = self.CreaMessageModifCapAjout(pos1, vehicule)
                    else:
                        #pos2 correspond à l'emplacement du vehicule qu'on cherche à ajouter
                        pos2 = "parc"
                        Message = self.PasDespace(pos2)
                else:  # véhicule neuf
                    # Vérifier s'il y a de la place dans le showroom
                    if self.Capacite[1] < 60:
                        #pos1 correspond à l'emplacement du véhicule dans le showroom
                        pos1 = 1
                        Message = self.CreaMessageModifCapAjout(pos1, vehicule)
                    else:
                        #pos2 correspond à l'emplacement du vehicule qu'on cherche à ajouter
                        pos2 = "showroom"
                        Message = self.PasDespace(pos2)
            else:  # vente
                # Vérifier l'emplacement du véhicule
                if vehicule.get("Emplacement", "").lower() == "parc":
                    # pos3 correspond à l'emplacement du véhicule qui va etre retiré
                    pos3 = 0
                    Message = self.SuppressionDuVehicule(pos3, vehicule)
                else:
                    # pos3 correspond à l'emplacement du véhicule qui va etre retiré
                    pos3 = 1
                    Message = self.SuppressionDuVehicule(pos3, vehicule)
                
                # Si aucun message n'a été généré, le véhicule n'a pas été trouvé
                if not Message:
                    Message = "Vehicule introuvable dans la base de donnees. Contactez un superieur"
        else:
            Message = "Les valeurs entrées sont incorrectes ou incompletes"
        
        return Message
    
    def CreaMessageModifCapAjout(self, pos1, vehicule):
        """
        Objectif : Crée un message, modifie la capacité et ajoute le véhicule à la BDD.
        Entrée:
            pos1: Index de l'emplacement (0 pour parc, 1 pour showroom)
            vehicule: Dictionnaire représentant une ligne de la BDD
        Sortie:
            str: Message de confirmation
        """
        Message = ""
        capacite_max = 140 if pos1 == 0 else 60
        
        # Vérifier si l'espace est presque rempli
        if self.Capacite[pos1] > 0.8 * capacite_max:
            Message = "Espace presque rempli, vehicule ajouté"
        else:
            Message = "Vehicule ajouté"
        
        # Mettre à jour la capacité
        self.Capacite[pos1] += 1
        self.Capacite[pos1+2] = self.Capacite[pos1+2] * (self.Capacite[pos1]-1) / self.Capacite[pos1]
        
        # Ajuster le véhicule avec le bon emplacement
        vehicule_a_ajouter = vehicule.copy()
        vehicule_a_ajouter["Emplacement"] = "parc" if pos1 == 0 else "showroom"
        vehicule_a_ajouter["Statut"] = "en stock"

        # Ajouter le véhicule à la BDD
        try:
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([vehicule_a_ajouter])], ignore_index=True)
            df.to_csv(self.csv_path, index=False)
            self.NombreVehicules += 1
        except Exception as e:
            Message += f" (Erreur BDD: {str(e)})"
        
        return Message
    
    def PasDespace(self, pos2):
        """
        Objectif : Vérifie s'il y a des véhicules qui vont sortir prochainement.
        Entrée:
            pos2: Emplacement ("parc" ou "showroom")
        Sortie:
            str: Message d'erreur ou d'information
        """
        Message = f"Erreur pas d'espace dans {pos2}"
        compt = 0
        # Verifie si un emplacement sera libéré dans la semaine
        try:
            df = pd.read_csv(self.csv_path)
            
            # Filtrer les véhicules d'occasion avec une sortie prévue dans moins de 7 jours
            vehicules_sortants = df[(df["Emplacement"] == pos2) & 
                                   (df["État"] == "occasion") & 
                                   (df["Jours avant sortie du stock"] < 7) & 
                                   (df["Jours avant sortie du stock"] > 0)]
            
            if not vehicules_sortants.empty:
                Message += " - Place liberable dans la semaine"
        except Exception as e:
            Message += f" (Erreur BDD: {str(e)})"
        
        return Message
    
    def SuppressionDuVehicule(self, pos3, vehicule):
        """
        Objectif : Supprime un véhicule de la BDD et met à jour la capacité.
        Entrée:
            pos3: Index de l'emplacement (0 pour parc, 1 pour showroom)
            vehicule: Dictionnaire représentant une ligne de la BDD
        Sortie:
            str: Message de confirmation ou d'erreur
        """
        Message = ""
        vehicule_id = vehicule.get("ID", "")
        
        try:
            df = pd.read_csv(self.csv_path)
            
            # Rechercher le véhicule par ID
            vehicule_index = df[df["ID"] == vehicule_id].index
            # Vérifier si le véhicule existe
            if not vehicule_index.empty:
                # Supprimer le véhicule
                df = df.drop(vehicule_index)
                df.to_csv(self.csv_path, index=False)
                
                # Mettre à jour la capacité
                self.Capacite[pos3] -= 1
                if self.Capacite[pos3] > 0:
                    self.Capacite[pos3+2] = self.Capacite[pos3+2] * (self.Capacite[pos3]+1) / self.Capacite[pos3]
                else:
                    self.Capacite[pos3+2] = 0
                # Mettre à jour le nombre de véhicules
                self.NombreVehicules -= 1
                Message = "Le vehicule a été retiré de la base de données"
        except Exception as e:
            Message = f"Erreur lors de la suppression: {str(e)}"

        return Message



# Estimation de prix avec le modèle de régression linéaire
class CarPricePredictor:
    def __init__(self):
        self.model = None
        self.feature_names = ['Année', 'ValeurEntrée', 'Kilométrage', 'ImportancePieces']
        self.pieces_uniques = set()

    def get_unique_pieces(self, data_path):
        df = pd.read_csv(data_path)
        for pieces_str in df['Pièces']:
            try:
                # Vérifier si la valeur n'est pas None, NaN ou un type non-chaîne
                if pieces_str is not None and isinstance(pieces_str, str):
                    pieces = json.loads(pieces_str)
                    for piece in pieces:
                        self.pieces_uniques.add(piece['nom_pièce'])
            except (TypeError, json.JSONDecodeError):
                # Ignorer les entrées qui ne peuvent pas être décodées
                continue
        return sorted(list(self.pieces_uniques))

    def process_pieces(self, pieces_str):
        try:
            # Si c'est une chaîne, essayer de la parser comme JSON
            if isinstance(pieces_str, str):
                pieces = json.loads(pieces_str)
            else:
                # Si c'est déjà parsé ou un autre type, l'utiliser directement
                pieces = pieces_str
            
            # Vérifier si pieces est un itérable (liste ou similaire)
            if isinstance(pieces, (list, tuple, set)):
                # Calculer la somme des valeurs d'importance
                importance_totale = sum(piece['importance_pièce'] for piece in pieces)
                return importance_totale
            else:
                # Si ce n'est pas un itérable, retourner une valeur par défaut
                return 0
        except (TypeError, json.JSONDecodeError, KeyError):
            # Gérer toutes les erreurs pendant l'analyse ou le traitement
            return 0
        
    def train(self, data_path):
        # Charger les données
        df = pd.read_csv(data_path)
        self.get_unique_pieces(data_path)

        # Préparation des features
        X = pd.DataFrame()
        X['Année'] = df['Année']
        X['ValeurEntrée'] = df['ValeurEntrée']
        X['Kilométrage'] = df['Kilométrage']
        X['ImportancePieces'] = df['Pièces'].apply(self.process_pieces)

        y = df['ValeurSortie']

        # Split et entrainement
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

        # Scores
        return {
            'train_score': self.model.score(X_train, y_train),
            'test_score': self.model.score(X_test, y_test),
            'coefficients': dict(zip(self.feature_names, self.model.coef_))
        }

    def predict(self, annee, valeur_entree, kilometrage, pieces):
        if self.model is None:
            raise ValueError("Le modèle doit d'abord être entraîné")
        
        importance_pieces = self.process_pieces(pieces)
        X_pred = pd.DataFrame([[annee, valeur_entree, kilometrage, importance_pieces]], 
                            columns=self.feature_names)
        prediction = self.model.predict(X_pred)[0]
        return round(prediction, 2)


def estimate_price(price_predictor):
    """
    Affiche un formulaire d'estimation de prix et calcule le prix estimé
    basé sur le modèle de prédiction.
    Entrée :
        price_predictor: Instance de CarPricePredictor entraînée
    """
    import streamlit as st
    
    st.subheader("💹 Estimation du prix d'un véhicule")
    
    # Créer une interface sans formulaire
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
    
    if st.button("Calculer l'estimation", use_container_width=True):
        try:
            estimated_price = price_predictor.predict(
                annee, valeur_entree, kilometrage, pieces
            )
            
            # Calculer une fourchette de prix (±5%)
            price_min = estimated_price * 0.95
            price_max = estimated_price * 1.05
            
            st.success(f"### Prix estimé: {estimated_price:,.2f} €")
            st.info(f"Fourchette de prix recommandée: {price_min:,.2f} € - {price_max:,.2f} €")
            
            # Afficher quelques métriques supplémentaires
            col1, col2, col3 = st.columns(3)
            with col1:
                marge = estimated_price - valeur_entree
                marge_percent = (marge / valeur_entree) * 100 if valeur_entree > 0 else 0
                st.metric("Marge potentielle", f"{marge:,.2f} €", f"{marge_percent:.1f}%")
            
            with col2:
                marche_actuel = estimated_price * 0.98  # Simuler prix du marché
                diff = estimated_price - marche_actuel
                diff_percent = (diff / marche_actuel) * 100
                st.metric("Comparaison marché", f"{marche_actuel:,.2f} €", f"{diff_percent:.1f}%")
            
            with col3:
                st.metric("Prix au km", f"{estimated_price / kilometrage:.2f} €/km" if kilometrage > 0 else "N/A")
            
        except Exception as e:
            st.error(f"Erreur lors de l'estimation du prix: {str(e)}")
            st.error("Veuillez vérifier que le modèle a été correctement entraîné avec les données")