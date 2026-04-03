import streamlit as st
import pandas as pd
from pyairtable import Api

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Cocktail Planner", layout="wide")

API_KEY = st.secrets.get("AIRTABLE_API_KEY", "YOUR_API_KEY")
BASE_ID = st.secrets.get("AIRTABLE_BASE_ID", "YOUR_BASE_ID")

api = Api(API_KEY)

TABLES = {
    "Commande": api.table(BASE_ID, "Commande"),
    "Liste": api.table(BASE_ID, "Liste"),
    "Recettes": api.table(BASE_ID, "Recettes"),
    "ALCOOL": api.table(BASE_ID, "ALCOOL"),
    "PREMIX": api.table(BASE_ID, "PREMIX"),
    "SOFT": api.table(BASE_ID, "SOFT"),
    "GARNISH": api.table(BASE_ID, "GARNISH"),
    "VERRES": api.table(BASE_ID, "VERRES"),
    "CLEAR ICE": api.table(BASE_ID, "CLEAR ICE"),
}

# =========================
# LOAD DATA
# =========================
@st.cache_data(ttl=60)
def load_table(table):
    records = table.all()
    return pd.DataFrame([r["fields"] for r in records])

def load_all():
    data = {}
    for name, table in TABLES.items():
        data[name] = load_table(table)
    return data

data = load_all()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🍸 Navigation")
page = st.sidebar.radio(
    "Aller vers",
    ["Dashboard", "Commandes", "Recettes", "Ingrédients"]
)

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":
    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric("Commandes", len(data["Commande"]))
    col2.metric("Recettes", len(data["Recettes"]))
    col3.metric("Alcools", len(data["ALCOOL"]))

    st.subheader("Quantités finales")

    if "Quantité finale" in data["Recettes"].columns:
        st.bar_chart(data["Recettes"]["Quantité finale"])

# =========================
# COMMANDES
# =========================
elif page == "Commandes":
    st.title("📦 Commandes")

    st.dataframe(data["Commande"], use_container_width=True)

    st.divider()
    st.subheader("➕ Nouvelle commande")

    recette = st.text_input("Nom du cocktail")
    nombre = st.number_input("Nombre de cocktails", min_value=1, value=1)

    if st.button("Ajouter la commande"):
        TABLES["Commande"].create({
            "Recette": recette,
            "Nombre de cocktails": nombre
        })
        st.success("✅ Commande ajoutée")
        st.cache_data.clear()

# =========================
# RECETTES
# =========================
elif page == "Recettes":
    st.title("🍸 Recettes")

    df = data["Recettes"]

    if "Cocktails" in df.columns:
        cocktail = st.selectbox(
            "Choisir un cocktail",
            sorted(df["Cocktails"].dropna().unique())
        )

        filtered = df[df["Cocktails"] == cocktail]

        st.dataframe(filtered, use_container_width=True)

    else:
        st.warning("Colonne 'Cocktails' non trouvée")

# =========================
# INGREDIENTS
# =========================
elif page == "Ingrédients":
    st.title("🧪 Ingrédients")

    tabs = st.tabs([
        "Alcool", "Premix", "Soft",
        "Garnish", "Verres", "Glace"
    ])

    tables_map = {
        "Alcool": "ALCOOL",
        "Premix": "PREMIX",
        "Soft": "SOFT",
        "Garnish": "GARNISH",
        "Verres": "VERRES",
        "Glace": "CLEAR ICE"
    }

    for i, (label, key) in enumerate(tables_map.items()):
        with tabs[i]:
            df = data[key]

            st.subheader(label)

            if "Cumul de Quantité finale" in df.columns:
                st.dataframe(
                    df.sort_values(
                        by="Cumul de Quantité finale",
                        ascending=False
                    ),
                    use_container_width=True
                )
            else:
                st.dataframe(df, use_container_width=True)