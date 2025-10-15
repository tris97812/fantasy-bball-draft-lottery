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
# Monte-Carlo (5.000 runs) geschätzte Wahrscheinlichkeiten (in %).
# Key = Team, Value = dict: overall Pick -> Wahrscheinlichkeit in %
lottery_odds = {
    "OG Kobolde": {
        2: 15.52, 3: 14.12, 4: 13.19, 5: 12.02, 6: 10.42, 7: 8.70, 8: 7.18, 9: 5.52, 10: 4.11, 11: 2.64, 12: 1.06, 13: 0.50, 14: 0.09
    },
    "Luca Magic": {
        2: 13.93, 3: 13.39, 4: 12.76, 5: 12.01, 6: 11.17, 7: 9.64, 8: 8.57, 9: 6.95, 10: 5.43, 11: 3.48, 12: 1.79, 13: 0.64, 14: 0.24
    },
    "Jonas Darkhorses": {
        2: 13.58, 3: 13.25, 4: 12.37, 5: 11.63, 6: 10.59, 7: 9.45, 8: 8.14, 9: 6.60, 10: 4.92, 11: 3.15, 12: 1.55, 13: 0.55, 14: 0.22
    },
    "Team 0 vom Drei": {
        2: 12.79, 3: 12.13, 4: 11.54, 5: 11.19, 6: 10.85, 7: 9.53, 8: 8.07, 9: 6.61, 10: 4.85, 11: 3.31, 12: 1.67, 13: 0.55, 14: 0.34
    },
    "Tim's Resterampe": {
        2: 11.38, 3: 10.78, 4: 10.66, 5: 10.88, 6: 11.20, 7: 9.42, 8: 9.52, 9: 8.94, 10: 7.58, 11: 5.34, 12: 2.88, 13: 1.24, 14: 0.18
    },
    "FL Hot Dogs": {
        2: 9.28, 3: 9.64, 4: 9.76, 5: 9.89, 6: 9.74, 7: 10.41, 8: 9.87, 9: 10.26, 10: 8.68, 11: 4.50, 12: 1.66, 13: 0.46, 14: 0.06
    },
    "Schnelle Brecher": {
        2: 7.29, 3: 7.63, 4: 8.06, 5: 8.40, 6: 9.39, 7: 8.98, 8: 9.85, 9: 10.30, 10: 9.74, 11: 5.82, 12: 3.07, 13: 0.69, 14: 0.06
    },
    "Team Franzmann": {
        2: 6.03, 3: 6.38, 4: 6.77, 5: 7.19, 6: 7.64, 7: 8.86, 8: 9.75, 9: 10.55, 10: 11.65, 11: 8.76, 12: 4.84, 13: 1.48, 14: 0.06
    },
    "Flensburg Penguins": {
        2: 4.37, 3: 5.14, 4: 4.76, 5: 5.45, 6: 5.28, 7: 6.61, 8: 7.25, 9: 8.34, 10: 9.95, 11: 11.28, 12: 12.14, 13: 8.21, 14: 3.34
    },
    "SunshineCoast SuperSonics": {
        2: 3.22, 3: 3.32, 4: 3.01, 5: 3.19, 6: 4.19, 7: 4.14, 8: 5.66, 9: 6.26, 10: 7.70, 11: 10.40, 12: 15.90, 13: 14.83, 14: 8.08
    },
    "Load Management": {
        2: 1.87, 3: 2.14, 4: 2.23, 5: 2.60, 6: 2.90, 7: 3.06, 8: 3.51, 9: 4.68, 10: 5.93, 11: 7.79, 12: 17.09, 13: 20.97, 14: 16.20
    },
    "Norderbrooklyn Wildcats": {
        2: 1.40, 3: 1.74, 4: 1.74, 5: 1.88, 6: 2.08, 7: 2.39, 8: 2.73, 9: 3.89, 10: 4.62, 11: 6.20, 12: 14.97, 13: 23.19, 14: 25.53
    },
    "Benchwarmers United SC": {
        2: 0.84, 3: 1.06, 4: 1.18, 5: 1.38, 6: 1.68, 7: 1.96, 8: 2.44, 9: 3.48, 10: 4.64, 11: 6.58, 12: 10.46, 13: 19.72, 14: 44.58
    }
}

def get_lottery_odds(team: str, pick_number: int) -> float:
    """Gibt die prozentuale Wahrscheinlichkeit zurück, dass ein Team diesen Pick landet."""
    try:
        return lottery_odds[team][pick_number]
    except KeyError:
        return None
# ============ TEAMDATEN ============
teams = {
    "OG Kobolde": 170,
    "Luca Magic": 145,
    "Jonas Darkhorses": 130,
    "Team 0 vom Drei": 110,
    "Tim's Resterampe": 100,
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
st.write("Schreibe die Zahlen 1-14 auf 14 Zettel. Falte die Zettelchen und tue sie in ein Glas. Ziehe vier Zettel aus dem Glas, ohne die Zettel zurück ins Glas zu legen. Gebe die Zahlen der vier Zettelchen hier ein. Die vier Zahlen ergeben ein Los.")
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
st.divider()
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
# ============ DYNAMISCHE WAHRSCHEINLICHKEITEN ============
st.subheader("📊 Aktuelle Gewinnchancen")
st.markdown(f"🎯 Anzahl verbleibender Lose im Pott: **{len(st.session_state.remaining_df)}**")
total_remaining = st.session_state.remaining_df.shape[0]
team_counts = st.session_state.remaining_df['Team'].value_counts().to_dict()

prob_data = []
for team in teams.keys():
    count = team_counts.get(team, 0)
    prob = (count / total_remaining * 100) if total_remaining > 0 else 0
    prob_data.append({"Team": team, "Anteil der Lose im Pott (%)": round(prob,1)})

prob_df = pd.DataFrame(prob_data).sort_values(by="Anteil der Lose im Pott (%)", ascending=False)
st.table(prob_df)
st.bar_chart(prob_df.set_index("Team")["Anteil der Lose im Pott (%)"])

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


