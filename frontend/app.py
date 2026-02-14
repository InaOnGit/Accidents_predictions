import streamlit as st
import requests
import os

# Configuration de la page
st.set_page_config(
    page_title="Prédiction Accidents",
    layout="centered"
)

# Titre
st.title("Prédiction de Gravité d'Accident")
st.markdown("---")

# Informations sur le modèle
with st.expander("À propos du modèle utilisé"):
    st.write("""
    **Modèle :** Logistic Regression  
    **Recall (Graves) :** 66.8%  
    **Dataset :** Accidents 2022-2024 (126,662 usagers)
    
    Le modèle prédit si un accident sera **grave** (hospitalisé ou tué) ou **non grave** (indemne ou blessé léger).
    """)

st.markdown("---")

# Formulaire de saisie
st.subheader("Caractéristiques de l'accident selon BAAC")

col1, col2 = st.columns(2)

with col1:
    heure = st.slider("Heure de l'accident", 0, 23, 14, 
                      help="Heure de la journée (0-23h)")
    
    lum = st.selectbox("Luminosité", 
                       options=[1, 2, 3, 4, 5],
                       format_func=lambda x: {
                           1: "Plein jour",
                           2: "Crépuscule/aube",
                           3: "Nuit sans éclairage",
                           4: "Nuit éclairage non allumé",
                           5: "Nuit éclairage allumé"
                       }[x])
    
    atm = st.selectbox("Conditions météo",
                       options=[1, 2, 3, 4, 5, 6],
                       format_func=lambda x: {
                           1: "Normale",
                           2: "Pluie légère",
                           3: "Pluie forte",
                           4: "Neige/grêle",
                           5: "Brouillard",
                           6: "Vent fort"
                       }[x])
    
    age = st.slider("Âge du conducteur", 16, 100, 30)

with col2:
    catr = st.selectbox("Type de route",
                        options=[1, 2, 3, 4],
                        format_func=lambda x: {
                            1: "Autoroute",
                            2: "Route nationale",
                            3: "Route départementale",
                            4: "Voie communale"
                        }[x])
    
    agg = st.selectbox("Localisation",
                       options=[1, 2],
                       format_func=lambda x: {
                           1: "Hors agglomération",
                           2: "En agglomération"
                       }[x])
    
    sexe = st.selectbox("Sexe",
                        options=[1, 2],
                        format_func=lambda x: {
                            1: "Masculin",
                            2: "Féminin"
                        }[x])
    
    catv = st.selectbox("Type de véhicule",
                        options=[1, 2, 7, 10, 31, 33],
                        format_func=lambda x: {
                            1: "Vélo",
                            2: "Cyclomoteur",
                            7: "Voiture",
                            10: "Utilitaire",
                            31: "Moto 50-125cc",
                            33: "Moto >125cc"
                        }[x],
                        index=2)

st.markdown("---")

# Bouton de prédiction
if st.button("Prédire la gravité de l'accident", type="primary", use_container_width=True):
    
    with st.spinner("Prédiction en cours..."):
        try:
            # Appeler l'API
            API_URL = os.getenv("API_URL", "http://localhost:8000")
            url = f"{API_URL}/predict"
            params = {
                "heure": heure,
                "lum": lum,
                "atm": atm,
                "age": age,
                "catr": catr,
                "agg": agg,
                "sexe": sexe,
                "catv": catv
            }
            
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                
                # Afficher le résultat
                st.markdown("---")
                st.subheader("Résultat de la prédiction")
                
                gravite = result["gravite"]
                proba_grave = result["probabilite_grave"]
                proba_non_grave = result["probabilite_non_grave"]
                
                # Affichage avec couleur selon la gravité
                if gravite == "Grave":
                    st.error(f"### ⚠️ ACCIDENT GRAVE")
                    st.metric("Probabilité d'accident grave", f"{proba_grave}%")
                    st.warning("Mobiliser des secours importants immédiatement")
                else:
                    st.success(f"### Accident non grave")
                    st.metric("Probabilité d'accident non grave", f"{proba_non_grave}%")
                    st.info("Intervention standard suffisante")
                
                # Détails
                with st.expander("Voir les détails"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Probabilité Non Grave", f"{proba_non_grave}%")
                    with col_b:
                        st.metric("Probabilité Grave", f"{proba_grave}%")
                    
                    # Barre de progression
                    st.progress(proba_grave / 100)
                    
                    # Contexte
                    st.write("**Contexte de l'accident :**")
                    nuit = "Oui" if (heure >= 22 or heure <= 6) else "Non"
                    jeune = "Oui" if age < 25 else "Non"
                    conditions = "Oui" if (atm in [2,3,4,5,6] or lum in [3,4]) else "Non"
                    
                    st.write(f"- Nuit : {nuit}")
                    st.write(f"- Jeune conducteur (<25 ans) : {jeune}")
                    st.write(f"- Conditions dangereuses : {conditions}")
                
            else:
                st.error(f"Erreur API : {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("**Erreur de connexion à l'API**")
            st.info("Assurez-vous que l'API est lancée avec : `uvicorn api:app --reload`")
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

# Footer
st.markdown("---")
st.caption("Projet ML - Prédiction Accidents Routiers | Données BAAC 2022-2024")
