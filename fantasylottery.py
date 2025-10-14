import streamlit as st
import pandas as pd
import itertools, random, os

st.set_page_config(page_title="Flensballers Fantasy Draft Lottery 2026",
                   page_icon="🎲", layout="centered")

# ============ TEAMDATEN ============
teams = {
    "OG Kobolde": 140,
    "Luca Magic": 140,
    "Jonas Darkhorses": 140,
    "Team 0 vom Drei": 125,
    "Tim": 110,
    "FL Hot Dogs": 90,
    "Schnelle Brecher": 75,
    "Team Franzmann": 60,
    "Flensburg Penguins": 45,
    "SunshineCoast SuperSonics": 30,
    "Load Management": 20,
    "Norderbrooklyn Wildcats": 15,
    "Benchwarmers United SC": 10
}

fixed_pick = "Flensburger Fantasialand"
save_file = "lottery_state.csv"

# ============ INITIALISIERUNG ============
def generate_combos():
    numbers = list(range(1, 15))
    all_combos = list(itertools.combinations(numbers, 4))
    random.shuffle(all_combos)
    all_combos = all_combos[:1000]

    assignments = []
    remaining_combos = all_combos.copy()

    for team, n in teams.items():
        chosen = random.sample(remaining_combos, n)
        for c in chosen:
            combo_str = " ".join(map(str, sorted(c)))
            assignments.append({"Kombination": combo_str, "Team": team})
        remaining_combos = [c for c in remaining_combos if c not in chosen]

    return pd.DataFrame(assignments)

if "remaining_df" not in st.session_state:
    if os.path.exists(save_file):
        df = pd.read_csv(save_file)
        st.session_state.remaining_df = df.copy()
        st.session_state.draft_order = df[df["Pick"].notna()]["Team"].tolist()
    else:
        st.session_state.remaining_df = generate_combos()
        st.session_state.draft_order = [fixed_pick]

# Session-Flag für Input-Reset
if "reset_inputs" not in st.session_state:
    st.session_state.reset_inputs = False

# ============ UI ============
st.title("🎲 Flensballers Fantasy Draft Lottery 2026")
st.write("Wer kriegt Pick #2-#5?! Pick #1 wurde letztes Jahr hart erkämpft! Herzlichen Glückwunsch nochmal!")
st.markdown(f"**Pick #1:** 🏆 {fixed_pick} *(fest vergeben)*")
st.divider()

# ============ ZAHLENEINGABE ============
st.header("🎲 Neue Kombination ziehen")
col1, col2, col3, col4 = st.columns(4)

z1 = col1.number_input("Zahl 1", min_value=1, max_value=14, step=1,
                       value=1 if st.session_state.reset_inputs else st.session_state.get("z1", 1),
                       key="z1")
z2 = col2.number_input("Zahl 2", min_value=1, max_value=14, step=1,
                       value=1 if st.session_state.reset_inputs else st.session_state.get("z2", 1),
                       key="z2")
z3 = col3.number_input("Zahl 3", min_value=1, max_value=14, step=1,
                       value=1 if st.session_state.reset_inputs else st.session_state.get("z3", 1),
                       key="z3")
z4 = col4.number_input("Zahl 4", min_value=1, max_value=14, step=1,
                       value=1 if st.session_state.reset_inputs else st.session_state.get("z4", 1),
                       key="z4")

if st.session_state.reset_inputs:
    st.session_state.reset_inputs = False

# ============ ZIEHUNGS-LOGIK ============
if st.button("🎯 Kombination prüfen"):
    combo_nums = [int(z1), int(z2), int(z3), int(z4)]
    combo_str = " ".join(map(str, sorted(combo_nums)))
    row = st.session_state.remaining_df.loc[st.session_state.remaining_df["Kombination"] == combo_str]

    if not row.empty:
        team = row.iloc[0]["Team"]
        if team in st.session_state.draft_order:
            st.warning(f"⚠️ {team} wurde bereits gezogen.")
        else:
            st.success(f"🏆 {team} wurde gezogen!")
            st.session_state.remaining_df = st.session_state.remaining_df[
                st.session_state.remaining_df["Team"] != team
            ]
            st.session_state.draft_order.append(team)
            st.session_state.reset_inputs = True
    else:
        st.error("❌ Kombination nicht gefunden oder bereits gezogen.")

# ============ DRAFT-ORDER ANZEIGE ============
st.subheader("📊 Aktueller Draft-Order")
for i, t in enumerate(st.session_state.draft_order, start=1):
    fest = " (fest)" if i == 1 else ""
    st.write(f"**Pick {i}:** {t}{fest}")

st.divider()

# ============ DYNAMISCHE WAHRSCHEINLICHKEITEN ============
st.subheader("📊 Aktuelle Gewinnchancen")
total_remaining = st.session_state.remaining_df.shape[0]
team_counts = st.session_state.remaining_df['Team'].value_counts().to_dict()

prob_data = []
for team in teams.keys():
    count = team_counts.get(team, 0)
    prob = (count / total_remaining * 100) if total_remaining > 0 else 0
    prob_data.append({"Team": team, "Chancen (%)": round(prob,1)})

prob_df = pd.DataFrame(prob_data).sort_values(by="Chancen (%)", ascending=False)
st.table(prob_df)

# Optional: Balkendiagramm
st.bar_chart(prob_df.set_index("Team")["Chancen (%)"])

# ============ RESET OPTION ============
if st.button("🔄 Neue Lottery starten"):
    os.remove(save_file) if os.path.exists(save_file) else None
    st.session_state.clear()
    st.experimental_rerun()

st.markdown("---")
st.caption("Powered by Streamlit • Flensballers Fantasy League 2026 🏀")

