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
# Monte-Carlo (100.000 runs) geschätzte Wahrscheinlichkeiten (in %).
# Key = Team, Value = dict: overall Pick -> Wahrscheinlichkeit in %
lottery_odds = {
    "OG Kobolde": {
        2: 17.01, 3: 15.61, 4: 14.15, 5: 12.58, 6: 11.08, 7: 9.48,
        8: 7.51, 9: 5.60, 10: 3.79, 11: 2.04, 12: 0.91, 13: 0.21, 14: 0.04
    },
    "Luca Magic": {
        2: 14.35, 3: 13.88, 4: 13.11, 5: 12.21, 6: 11.21, 7: 10.06,
        8: 8.49, 9: 6.83, 10: 4.95, 11: 3.06, 12: 1.39, 13: 0.43, 14: 0.05
    },
    "Jonas Darkhorses": {
        2: 13.07, 3: 12.68, 4: 12.34, 5: 11.96, 6: 11.01, 7: 10.24,
        8: 9.11, 9: 7.50, 10: 5.82, 11: 3.65, 12: 1.91, 13: 0.62, 14: 0.09
    },
    "Team 0 vom Drei": {
        2: 10.85, 3: 11.00, 4: 10.94, 5: 10.94, 6: 10.76, 7: 10.37,
        8: 9.99, 9: 8.69, 10: 7.23, 11: 5.28, 12: 2.74, 13: 1.02, 14: 0.19
    },
    "Tim's Resterampe": {
        2: 10.03, 3: 10.14, 4: 10.40, 5: 10.42, 6: 10.26, 7: 10.19,
        8: 10.00, 9: 9.46, 10: 7.92, 11: 6.02, 12: 3.50, 13: 1.39, 14: 0.28
    },
    "FL Hot Dogs": {
        2: 9.10, 3: 9.33, 4: 9.46, 5: 9.92, 6: 9.93, 7: 10.13,
        8: 9.97, 9: 9.65, 10: 9.02, 11: 7.01, 12: 4.22, 13: 1.87, 14: 0.39
    },
    "Schnelle Brecher": {
        2: 7.49, 3: 7.90, 4: 8.24, 5: 8.58, 6: 9.27, 7: 9.56,
        8: 10.03, 9: 10.31, 10: 10.04, 11: 8.73, 12: 6.12, 13: 3.00, 14: 0.73
    },
    "Team Franzmann": {
        2: 6.05, 3: 6.40, 4: 6.82, 5: 7.16, 6: 7.93, 7: 8.53,
        8: 9.66, 9: 10.59, 10: 11.05, 11: 10.76, 12: 8.66, 13: 4.92, 14: 1.47
    },
    "Flensburg Penguins": {
        2: 4.60, 3: 4.80, 4: 5.37, 5: 5.85, 6: 6.44, 7: 7.32,
        8: 8.24, 9: 9.69, 10: 11.47, 11: 12.69, 12: 12.11, 13: 8.29, 14: 3.12
    },
    "SunshineCoast SuperSonics": {
        2: 2.98, 3: 3.27, 4: 3.69, 5: 3.99, 6: 4.58, 7: 5.30,
        8: 6.24, 9: 7.85, 10: 10.07, 11: 13.43, 12: 16.11, 13: 14.58, 14: 7.91
    },
    "Load Management": {
        2: 1.98, 3: 2.22, 4: 2.43, 5: 2.80, 6: 3.31, 7: 3.85,
        8: 4.65, 9: 5.95, 10: 7.85, 11: 11.11, 12: 16.75, 13: 20.54, 14: 16.57
    },
    "Norderbrooklyn Wildcats": {
        2: 1.50, 3: 1.63, 4: 1.87, 5: 2.11, 6: 2.53, 7: 2.96,
        8: 3.62, 9: 4.64, 10: 6.24, 11: 9.43, 12: 14.49, 13: 23.12, 14: 25.87
    },
    "Benchwarmers United SC": {
        2: 1.00, 3: 1.12, 4: 1.19, 5: 1.47, 6: 1.71, 7: 2.03,
        8: 2.51, 9: 3.25, 10: 4.56, 11: 6.79, 12: 11.08, 13: 20.01, 14: 43.28
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


