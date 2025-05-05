
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