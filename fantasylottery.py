import streamlit as st
import pandas as pd
import itertools, random, os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="Flensballers Fantasy Draft Lottery 2026",
    page_icon="🏀",
    layout="centered"
)
# Wahrscheinlichkeiten für jede Lottery-Position (basierend auf 10.000 Simulationen)
# Hinweis:
# "LotteryDrawPick1" entspricht overall Pick #2, "LotteryDrawPick13" entspricht overall Pick #14.
# mit CHATTI überarbeiten! muss von 2-14 gehen
lottery_odds = {
    "OG Kobolde": {
        1: 13.98, 2: 13.33, 3: 12.91, 4: 11.57, 5: 11.07, 6: 10.27,
        7: 8.60, 8: 7.37, 9: 5.26, 10: 3.32, 11: 1.79, 12: 0.47, 13: 0.06
    },
    "Luca Magic": {
        1: 14.24, 2: 13.50, 3: 13.22, 4: 12.18, 5: 11.85, 6: 10.93,
        7: 9.69, 8: 8.29, 9: 6.75, 10: 4.43, 11: 1.67, 12: 0.56, 13: 0.08
    },
    "Jonas Darkhorses": {
        1: 14.28, 2: 13.83, 3: 12.88, 4: 12.24, 5: 11.19, 6: 9.74,
        7: 8.40, 8: 7.32, 9: 5.93, 10: 3.23, 11: 1.51, 12: 0.45, 13: 0.07
    },
    "Team 0 vom Drei": {
        1: 12.64, 2: 12.32, 3: 11.66, 4: 11.68, 5: 10.80, 6: 10.90,
        7: 9.10, 8: 7.86, 9: 6.35, 10: 4.45, 11: 2.00, 12: 0.84, 13: 0.20
    },
    "Tim": {
        1: 10.80, 2: 10.75, 3: 10.58, 4: 10.49, 5: 10.65, 6: 11.10,
        7: 10.28, 8: 10.20, 9: 8.30, 10: 7.20, 11: 2.86, 12: 1.05, 13: 0.31
    },
    "FL Hot Dogs": {
        1: 8.92, 2: 9.02, 3: 9.61, 4: 9.91, 5: 9.80, 6: 9.74,
        7: 10.41, 8: 9.89, 9: 10.26, 10: 8.68, 11: 4.50, 12: 1.66, 13: 0.46
    },
    "Schnelle Brecher": {
        1: 7.29, 2: 7.56, 3: 8.05, 4: 8.40, 5: 8.46, 6: 9.39,
        7: 8.98, 8: 9.85, 9: 10.30, 10: 9.74, 11: 5.82, 12: 3.07, 13: 0.69
    },
    "Team Franzmann": {
        1: 5.96, 2: 6.26, 3: 6.48, 4: 7.08, 5: 6.74, 6: 7.66,
        7: 8.86, 8: 9.75, 9: 10.55, 10: 11.65, 11: 8.76, 12: 4.84, 13: 1.48
    },
    "Flensburg Penguins": {
        1: 4.37, 2: 5.14, 3: 4.76, 4: 5.45, 5: 5.28, 6: 6.61,
        7: 7.25, 8: 8.34, 9: 9.95, 10: 11.28, 11: 12.14, 12: 8.21, 13: 3.34
    },
    "SunshineCoast SuperSonics": {
        1: 3.22, 2: 3.32, 3: 3.01, 4: 3.19, 5: 4.19, 6: 4.14,
        7: 5.66, 8: 6.26, 9: 7.70, 10: 10.40, 11: 15.90, 12: 14.83, 13: 8.08
    },
    "Load Management": {
        1: 1.87, 2: 2.14, 3: 2.23, 4: 2.60, 5: 2.90, 6: 3.06,
        7: 3.51, 8: 4.68, 9: 5.93, 10: 7.79, 11: 17.09, 12: 20.97, 13: 16.20
    },
    "Norderbrooklyn Wildcats": {
        1: 1.40, 2: 1.74, 3: 1.74, 4: 1.88, 5: 2.08, 6: 2.39,
        7: 2.73, 8: 3.89, 9: 4.62, 10: 6.20, 11: 14.97, 12: 23.19, 13: 25.53
    },
    "Benchwarmers United SC": {
        1: 1.03, 2: 1.09, 3: 0.99, 4: 1.28, 5: 1.46, 6: 1.65,
        7: 1.83, 8: 2.23, 9: 3.18, 10: 4.71, 11: 10.99, 12: 19.86, 13: 43.50
    }
}
def get_lottery_odds(team: str, pick_number: int) -> float:
    """Gibt die prozentuale Wahrscheinlichkeit zurück, dass ein Team diesen Pick landet."""
    try:
        return lottery_odds[team][pick_number]
    except KeyError:
        return None
# ============ TEAMDATEN ============
# Lose überarbeiten - lenno, luka, jonas klar abgrenzen
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

# ============ GENERATE COMBOS ============
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

# ============ SESSION-STATE INITIALISIERUNG ============
if "drawn_combos" not in st.session_state:
    st.session_state.drawn_combos = []

if "draft_order" not in st.session_state:
    st.session_state.draft_order = [fixed_pick]

if "remaining_df" not in st.session_state:
    st.session_state.remaining_df = generate_combos()

# ==== HIER CSV-Download BUTTON EINFÜGEN ====
csv_bytes = st.session_state.remaining_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 CSV der Zuteilungen herunterladen",
    data=csv_bytes,
    file_name="lottery_assignments.csv",
    mime="text/csv"
)

if "reset_inputs" not in st.session_state:
    st.session_state.reset_inputs = False
# ==================== PDF-DOWNLOAD ====================
def generate_draft_pdf(draft_order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Titel
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Flensballers Fantasy Draft Lottery 2026")

    # Inhalt
    p.setFont("Helvetica", 12)
    y = height - 90
    for i, team in enumerate(draft_order, start=1):
        p.drawString(50, y, f"{i}. {team}")
        y -= 20
        if y < 50:  # Neue Seite bei Platzmangel
            p.showPage()
            p.setFont("Helvetica", 12)
            y = height - 50

    p.save()
    buffer.seek(0)
    return buffer

# PDF immer verfügbar machen
pdf_buffer = generate_draft_pdf(st.session_state.draft_order)
st.download_button(
    label="📄 Ergebnisse als PDF herunterladen",
    data=pdf_buffer,
    file_name="draft_order.pdf",
    mime="application/pdf"
)

# ============ UI ============
st.title("🏀 Flensballers Fantasy Draft Lottery 2026")
st.write("Pick #1 wurde letztes Jahr hart erkämpft! Shoutout an Jonas!! Doch wer kriegt die nächsten Picks? ")
st.divider()

# ============ ZAHLENEINGABE ============
st.header("🎲 Neues Los ziehen")
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
if st.button("🎯 Los prüfen"):
    combo_nums = [int(z1), int(z2), int(z3), int(z4)]
    combo_str = " ".join(map(str, sorted(combo_nums)))
    row = st.session_state.remaining_df.loc[st.session_state.remaining_df["Kombination"] == combo_str]
    
    if not row.empty:
        team = row.iloc[0]["Team"]
        if team in st.session_state.draft_order:
            st.warning(f"⚠️ {team} wurde bereits gezogen.")
        else:
            # Ursprüngliche Lose / Wahrscheinlichkeit
            original_chances = teams[team]
            total_original = sum(teams.values())
            original_percent = round(original_chances / total_original * 100, 1)

            # Pick hinzufügen
            st.session_state.draft_order.append(team)
            pick_number = len(st.session_state.draft_order)

            # Wahrscheinlichkeit für diesen Pick
            odds_for_pick = get_lottery_odds(team, pick_number)

            # Originalposition für Differenz
            original_rank = list(teams.keys()).index(team) + 2  # +2 wegen festem Pick #1
            diff = original_rank - pick_number

            st.success(f"🏆 {team} wurde gezogen! (Original-Wahrscheinlichkeit: {original_percent:.1f}%)")
            if odds_for_pick:
                st.info(f"📊 Wahrscheinlichkeit für diesen Pick: {odds_for_pick:.2f}%")

            # Differenz zur Originalposition
            if diff > 0:
                st.success(f"⬆️ Verbesserung: +{diff}")
            elif diff < 0:
                st.error(f"⬇️ Verschlechterung: {diff}")
            else:
                st.warning("⏺️ Keine Veränderung")

            # Entferne alle Combos des Teams aus dem Pott
            st.session_state.remaining_df = st.session_state.remaining_df[
                st.session_state.remaining_df["Team"] != team]
            st.session_state.reset_inputs = True
            st.session_state.drawn_combos.append({"Kombination": combo_str, "Team": team, "Original_Chancen": original_chances})
    else:
        st.error("❌ Kombination nicht gefunden oder bereits gezogen.")

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ============ DRAFT-ORDER ANZEIGE ============
st.subheader("📊 Aktuelle Draft-Reihenfolge")

for i, team in enumerate(st.session_state.draft_order, start=1):
    if i == 1:
        st.write(f"Pick {i}: {fixed_pick} (fest)")
    else:
        pick_number = i
        original_percent = lottery_odds.get(team, {}).get(pick_number, 0)
        # Differenz zur ursprünglichen Position (Liste der Teams als Originalposition)
        original_rank = list(teams.keys()).index(team) + 2  # +2 wegen festem Pick #1
        diff = original_rank - pick_number
        diff_text = f"+{diff}" if diff > 0 else f"{diff}" if diff < 0 else "0"
        st.write(f"Pick {i}: {team} ({original_percent:.2f}%, Δ {diff_text})")
st.divider()
# ==================== LIVEANZEIGE ====================
st.markdown(f"##### 🎯 Anzahl verbleibender Lose im Pott: **{len(st.session_state.remaining_df)}**")
# ============ DYNAMISCHE WAHRSCHEINLICHKEITEN ============
st.subheader("📊 Aktuelle Gewinnchancen")
total_remaining = st.session_state.remaining_df.shape[0]
team_counts = st.session_state.remaining_df['Team'].value_counts().to_dict()

prob_data = []
for team in teams.keys():
    count = team_counts.get(team, 0)
    prob = (count / total_remaining * 100) if total_remaining > 0 else 0
    prob_data.append({"Team": team, "Anteil der Lose im Topf (%)": round(prob,1)})

prob_df = pd.DataFrame(prob_data).sort_values(by="Anteil der Lose im Topf (%)", ascending=False)
st.table(prob_df)
st.bar_chart(prob_df.set_index("Team")["Anteil der Lose im Topf (%)"])

# ============ GEZOGENE KOMBINATIONEN ============
st.subheader("📋 Bereits gezogene Lose")
if st.session_state.drawn_combos:
    drawn_df = pd.DataFrame(st.session_state.drawn_combos)
    st.table(drawn_df)
else:
    st.write("Noch keine Lose gezogen.")

# ============ RESET OPTION ============
if st.button("🔄 Neue Lottery starten"):
    if os.path.exists(save_file):
        os.remove(save_file)
    st.session_state.clear()
    st.session_state.remaining_df = generate_combos()
    st.session_state.draft_order = [fixed_pick]
    st.session_state.drawn_combos = []
    st.session_state.reset_inputs = True

st.markdown("---")
st.caption("Powered by Streamlit • Flensballers Fantasy League 2026 🏀")


