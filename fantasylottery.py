import streamlit as st
import pandas as pd
import itertools, random, os

st.set_page_config(page_title="Flensballers Fantasy Draft Lottery 2026", page_icon="🎲", layout="centered")

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
    combos = list(itertools.combinations(numbers, 4))
    random.shuffle(combos)
    combos = combos[:1000]
    assignments = []
    i = 0
    for team, n in teams.items():
        for c in combos[i:i+n]:
            combo_str = " ".join(map(str, sorted(c)))
            assignments.append({"Kombination": combo_str, "Team": team})
        i += n
    return pd.DataFrame(assignments)

if "remaining_df" not in st.session_state:
    if os.path.exists(save_file):
        df = pd.read_csv(save_file)
        st.session_state.remaining_df = df.copy()
        st.session_state.draft_order = df[df["Pick"].notna()]["Team"].tolist()
    else:
        st.session_state.remaining_df = generate_combos()
        st.session_state.draft_order = [fixed_pick]

# ============ UI ============
st.title("🎲 Flensballers Fantasy Draft Lottery 2026")
st.write("Wer kriegt Pick #2-#5?! Pick #1 wurde letztes Jahr hart erkämpft! Herzloichen Glückwunsch nochmal an Jonas!")
# ============ DRAFT-ORDER ANZEIGE ============
st.subheader("📊 Aktueller Draft-Order")
for i, t in enumerate(st.session_state.draft_order, start=1):
    fest = " (fest)" if i == 1 else ""
    st.write(f"**Pick {i}:**(fest)")
st.divider()
# ============ ZAHLENEINGABE UND ZIEHUNG ============
st.header("🎲 Neue Kombination ziehen")

# Session-Flag initialisieren
if "reset_inputs" not in st.session_state:
    st.session_state.reset_inputs = False

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

# Flag zurücksetzen, sonst würden die Inputs immer auf 1 springen
if st.session_state.reset_inputs:
    st.session_state.reset_inputs = False


if st.button("🎯 Kombination prüfen"):
    combo_nums = [int(z1), int(z2), int(z3), int(z4)]

    # Kombination sortieren
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

            # Reset der Inputs über Session-Flag
            st.session_state.reset_inputs = True
    else:
        st.error("❌ Kombination nicht gefunden oder bereits gezogen.")

# ============ AKTUELLE CHANCEN ============

st.divider()
st.subheader("📈 Aktuelle Wahrscheinlichkeiten (verbleibende Teams)")

# Zähle, wie viele Kombinationen jedes Team noch hat
remaining_counts = st.session_state.remaining_df["Team"].value_counts().sort_values(ascending=False)

# Berechne die neuen Prozentwerte
total_remaining = remaining_counts.sum()
chances_df = pd.DataFrame({
    "Team": remaining_counts.index,
    "Verbleibende Lose": remaining_counts.values,
    "Chance (%)": (remaining_counts / total_remaining * 100).round(2)
})

# Anzeige als Tabelle
st.dataframe(chances_df, hide_index=True, use_container_width=True)

# Optional: Balkendiagramm für visuelle Darstellung
st.markdown("### 🎞️ Verteilung der Chancen")
st.bar_chart(
    data=chances_df.set_index("Team")["Chance (%)"],
    height=400,
    use_container_width=True
)

# ============ FORTSCHRITT SPEICHERN ============
def save_state():
    picks_df = pd.DataFrame({
        "Pick": list(range(1, len(st.session_state.draft_order)+1)),
        "Team": st.session_state.draft_order
    })
    merged = st.session_state.remaining_df.copy()
    merged["Pick"] = merged["Team"].map({t: i for i, t in enumerate(st.session_state.draft_order, start=1)})
    merged.to_csv(save_file, index=False)

if st.button("💾 Fortschritt speichern"):
    save_state()
    st.success("Fortschritt gespeichert!")

# ============ RESET OPTION ============
if st.button("🔄 Neue Lottery starten"):
    os.remove(save_file) if os.path.exists(save_file) else None
    st.session_state.clear()
    st.experimental_rerun()

st.markdown("---")
st.caption("Powered by Streamlit • flensballers fantasy league 2026 🏀")
