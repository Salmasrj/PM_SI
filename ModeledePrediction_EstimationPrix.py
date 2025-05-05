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