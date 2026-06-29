import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mon_profil import MON_PROFIL

# ── Configuration page ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Market Tension Radar",
    page_icon="🎯",
    layout="wide",
)

# ── Style ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #00ff88;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .score-high { color: #00ff88; font-size: 2rem; font-weight: bold; }
    .score-mid  { color: #ffd700; font-size: 2rem; font-weight: bold; }
    .score-low  { color: #ff4444; font-size: 2rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

PROFIL_DEFAULT = MON_PROFIL

# ── Chargement données ───────────────────────────────────────────────────────
@st.cache_data
def load_offres():
    df = pd.read_csv("data/offres_emploi.csv")
    return df

# ── Moteur de scoring ────────────────────────────────────────────────────────
def scorer_offre(offre, profil):
    score = 0
    details = {}

    # 1. Hard skills transférables (30 pts)
    hard_skills_offre = [s.strip() for s in offre["hard_skills"].split(",")]
    profil_skills = profil["hard_skills"]
    match = sum(1 for s in hard_skills_offre if any(s.lower() in ps.lower() or ps.lower() in s.lower() for ps in profil_skills))
    pts_hard = min(30, round((match / max(len(hard_skills_offre), 1)) * 30))
    score += pts_hard
    details["Hard Skills"] = pts_hard

    # 2. Rare skill (25 pts)
    rare_offre = offre["rare_skill_recherche"].lower()
    match_rare = any(tag.lower() in rare_offre or rare_offre in tag.lower() for tag in profil["rare_skill_tags"])
    pts_rare = 25 if match_rare else 0
    score += pts_rare
    details["Rare Skill"] = pts_rare

    # 3. Télétravail (15 pts)
    pts_tele = 15 if offre["teletravail"] in profil["preferences"]["teletravail"] else 0
    score += pts_tele
    details["Télétravail"] = pts_tele

    # 4. Autonomie (15 pts)
    pts_auto = round((offre["autonomie_score"] / 5) * 15)
    score += pts_auto
    details["Autonomie"] = pts_auto

    # 5. Progression (15 pts)
    pts_prog = round((offre["progression_score"] / 5) * 15)
    score += pts_prog
    details["Progression"] = pts_prog

    # Bonus salaire (hors score, filtre seulement)
    salaire_ok = offre["salaire_min"] >= profil["preferences"]["salaire_min"]

    return score, details, salaire_ok

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🎯 Market Tension Radar")
st.caption("Outil de scoring d'adéquation candidat × marché — piloté par IA, construit sans background technique")

tab1, tab2, tab3 = st.tabs(["👤 Mon Profil", "📊 Analyse du Marché", "🏆 Top Opportunités"])

# ── TAB 1 : Profil ───────────────────────────────────────────────────────────
with tab1:
    st.header(f"{PROFIL_DEFAULT['nom']}")
    st.subheader(PROFIL_DEFAULT["titre"])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Hard Skills transférables")
        for skill in PROFIL_DEFAULT["hard_skills"]:
            st.markdown(f"- `{skill}`")

        st.markdown("### Rare Skill")
        st.info(PROFIL_DEFAULT["rare_skill"])

        st.markdown(f"### Expérience : **{PROFIL_DEFAULT['annees_experience']} ans**")

    with col2:
        st.markdown("### Résultats clés (preuves terrain)")
        for r in PROFIL_DEFAULT["resultats_cles"]:
            st.success(f"✅ {r}")

        st.markdown("### Préférences")
        st.markdown(f"- Télétravail : `{', '.join(PROFIL_DEFAULT['preferences']['teletravail'])}`")
        st.markdown(f"- Salaire minimum : `{PROFIL_DEFAULT['preferences']['salaire_min']:,} €/an`")

# ── TAB 2 : Analyse marché ───────────────────────────────────────────────────
with tab2:
    st.header("Analyse du marché en cours")

    df = load_offres()

    # Calcul scores
    scores, details_list, salaire_flags = [], [], []
    for _, row in df.iterrows():
        s, d, ok = scorer_offre(row, PROFIL_DEFAULT)
        scores.append(s)
        details_list.append(d)
        salaire_flags.append(ok)

    df["score_adequation"] = scores
    df["salaire_ok"] = salaire_flags
    df["label_score"] = df["score_adequation"].apply(
        lambda x: "🟢 Fort" if x >= 70 else ("🟡 Moyen" if x >= 45 else "🔴 Faible")
    )

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offres analysées", len(df))
    col2.metric("Score moyen", f"{df['score_adequation'].mean():.0f}/100")
    col3.metric("Offres Fort match (≥70)", len(df[df['score_adequation'] >= 70]))
    col4.metric("Salaire compatible", len(df[df['salaire_ok']]))

    # Distribution scores
    fig_hist = px.histogram(
        df, x="score_adequation", nbins=10,
        title="Distribution des scores d'adéquation",
        color_discrete_sequence=["#00ff88"],
        labels={"score_adequation": "Score /100"},
    )
    fig_hist.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#1a1a2e",
        font_color="white", title_font_color="#00ff88"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Par secteur
    df_secteur = df.groupby("secteur")["score_adequation"].mean().reset_index().sort_values("score_adequation", ascending=False)
    fig_sec = px.bar(
        df_secteur, x="secteur", y="score_adequation",
        title="Score moyen d'adéquation par secteur",
        color="score_adequation",
        color_continuous_scale=["#ff4444", "#ffd700", "#00ff88"],
        labels={"score_adequation": "Score moyen /100", "secteur": "Secteur"},
    )
    fig_sec.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#1a1a2e",
        font_color="white", title_font_color="#00ff88"
    )
    st.plotly_chart(fig_sec, use_container_width=True)

# ── TAB 3 : Top opportunités ─────────────────────────────────────────────────
with tab3:
    st.header("🏆 Top opportunités pour votre profil")

    df = load_offres()
    scores, details_list, salaire_flags = [], [], []
    for _, row in df.iterrows():
        s, d, ok = scorer_offre(row, PROFIL_DEFAULT)
        scores.append(s)
        details_list.append(d)
        salaire_flags.append(ok)
    df["score_adequation"] = scores
    df["salaire_ok"] = salaire_flags

    top = df.sort_values("score_adequation", ascending=False).head(5)

    for _, offre in top.iterrows():
        score = offre["score_adequation"]
        color = "#00ff88" if score >= 70 else ("#ffd700" if score >= 45 else "#ff4444")

        with st.expander(f"{'🟢' if score >= 70 else '🟡'} {offre['titre']} — {offre['entreprise']} ({score}/100)"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Score adéquation", f"{score}/100")
            c2.metric("Salaire", f"{offre['salaire_min']:,}–{offre['salaire_max']:,} €")
            c3.metric("Télétravail", offre["teletravail"])

            st.markdown(f"**Secteur :** {offre['secteur']} | **Lieu :** {offre['lieu']} | **Source :** {offre['source']}")
            st.markdown(f"**Skills demandés :** `{offre['hard_skills']}`")
            st.markdown(f"**Rare skill recherché :** *{offre['rare_skill_recherche']}*")

            # Radar chart par offre
            _, d, _ = scorer_offre(offre, PROFIL_DEFAULT)
            max_vals = {"Hard Skills": 30, "Rare Skill": 25, "Télétravail": 15, "Autonomie": 15, "Progression": 15}
            categories = list(d.keys())
            vals_pct = [round(d[k] / max_vals[k] * 100) for k in categories]

            fig_radar = go.Figure(go.Scatterpolar(
                r=vals_pct + [vals_pct[0]],
                theta=categories + [categories[0]],
                fill="toself",
                line_color=color,
                fillcolor=color.replace(")", ", 0.2)").replace("rgb", "rgba") if "rgb" in color else color,
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="white"),
                    bgcolor="#1a1a2e",
                ),
                paper_bgcolor="#0a0a0a",
                font_color="white",
                height=300,
                margin=dict(l=40, r=40, t=20, b=20),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()
    st.caption("💡 *Ce radar a été construit avec l'IA (Claude) pour démontrer une méthode de travail, pas un background technique. Chaque critère de scoring traduit une logique métier réelle issue de 8 ans d'expérience terrain.*")
