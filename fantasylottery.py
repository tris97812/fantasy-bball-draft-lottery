import streamlit as st
import pandas as pd
import itertools, random, os

st.set_page_config(page_title="Fantasy Draft Lottery", page_icon="🎲", layout="centered")

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
st.title("🎲 Fantasy League Draft Lottery")
st.write("Willkommen zur diesjährigen Ziehung!")
st.markdown(f"**Pick #1:** 🏆 {fixed_pick} *(fest vergeben)*")
st.divider()

col1, col2 = st.columns([2,1])
with col1:
    combo = st.text_input("Gezogene Kombination eingeben (z. B. 1 5 7 11):", key="combo_input")

with col2:
    if st.button("🎯 Ziehung starten"):
        combo_str = " ".join(sorted(combo.split()))
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
        else:
            st.error("❌ Kombination nicht gefunden oder bereits gezogen.")

# ============ DRAFT-ORDER ANZEIGE ============
st.subheader("📊 Aktueller Draft-Order")
for i, t in enumerate(st.session_state.draft_order, start=1):
    fest = " (fest)" if i == 1 else ""
    st.write(f"**Pick {i}:** {t}{fest}")

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
