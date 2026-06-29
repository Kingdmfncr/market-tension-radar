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
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #00ff88;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .badge-disqualified {
        background: #ff4444;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-fort {
        background: #00ff88;
        color: black;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-moyen {
        background: #ffd700;
        color: black;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

PROFIL_DEFAULT = MON_PROFIL

# ── Chargement données ───────────────────────────────────────────────────────
@st.cache_data
def load_offres():
    return pd.read_csv("data/offres_emploi.csv")

# ── Moteur de scoring v2 (6 dimensions + deal-breakers) ─────────────────────
def scorer_offre(offre, profil):
    details = {}
    disqualified = False
    raison_disqualif = []

    # ── DEAL-BREAKER 1 : Type de contrat ──────────────────────────────────
    contrat_ok = offre["type_contrat"] in profil["preferences"]["contrats_acceptes"]
    if not contrat_ok:
        disqualified = True
        raison_disqualif.append(f"Contrat '{offre['type_contrat']}' non accepté")

    # ── DEAL-BREAKER 2 : Télétravail ──────────────────────────────────────
    tele_ok = offre["teletravail"] in profil["preferences"]["teletravail"]
    if not tele_ok:
        disqualified = True
        raison_disqualif.append(f"Télétravail '{offre['teletravail']}' non compatible")

    if disqualified:
        return 0, {}, True, raison_disqualif

    # ── 1. Hard Skills Bloquants & Transférables (25 pts) ─────────────────
    hard_skills_offre = [s.strip() for s in offre["hard_skills"].split(",")]
    skills_bloquants_offre = [s.strip() for s in str(offre["skills_bloquants"]).split(",") if s.strip()]

    # Maîtrise générale (40% de la note)
    match_general = sum(1 for s in hard_skills_offre if any(
        s.lower() in ps.lower() or ps.lower() in s.lower()
        for ps in profil["hard_skills"]
    ))
    pts_general = (match_general / max(len(hard_skills_offre), 1)) * 10

    # Maîtrise des skills bloquants (60% de la note — pondération forte)
    if skills_bloquants_offre:
        match_bloquants = sum(1 for s in skills_bloquants_offre if any(
            s.lower() in ps.lower() or ps.lower() in s.lower()
            for ps in profil["skills_bloquants_maitrises"]
        ))
        pts_bloquants = (match_bloquants / len(skills_bloquants_offre)) * 15
    else:
        pts_bloquants = 15

    pts_hard = round(min(25, pts_general + pts_bloquants))
    details["Hard Skills"] = pts_hard

    # ── 2. Rare Skill Match (20 pts) ──────────────────────────────────────
    rare_offre = offre["rare_skill_recherche"].lower()
    match_rare = any(
        tag.lower() in rare_offre or rare_offre in tag.lower()
        for tag in profil["rare_skill_tags"]
    )
    pts_rare = 20 if match_rare else 0
    details["Rare Skill"] = pts_rare

    # ── 3. Cadrage Contractuel & Sectoriel (15 pts) ───────────────────────
    secteur_ok = str(offre.get("secteur_accessible", "Oui")) == "Oui"
    pts_contrat = 15 if (contrat_ok and secteur_ok) else 7 if contrat_ok else 0
    details["Cadrage Contractuel"] = pts_contrat

    # ── 4. Télétravail / Flexibilité (15 pts) ────────────────────────────
    pts_tele = 15 if tele_ok else 0
    details["Télétravail"] = pts_tele

    # ── 5. Autonomie & Niveau du Poste (15 pts) ──────────────────────────
    fit_transfo = str(offre.get("fit_transformation", "Non")) == "Oui"
    pts_auto = round((offre["autonomie_score"] / 5) * 10) + (5 if fit_transfo else 0)
    pts_auto = min(15, pts_auto)
    details["Autonomie & Fit Transfo"] = pts_auto

    # ── 6. Progression & Potentiel Scale (10 pts) ────────────────────────
    pts_prog = round((offre["progression_score"] / 5) * 10)
    details["Progression"] = pts_prog

    score_total = sum(details.values())
    salaire_ok = offre["salaire_min"] >= profil["preferences"]["salaire_min"]

    return score_total, details, False, []


# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════

st.title("🎯 Market Tension Radar")
st.caption("Outil de scoring d'adéquation candidat × marché — piloté par IA, construit sans background technique")

tab1, tab2, tab3 = st.tabs(["👤 Mon Profil", "📊 Analyse du Marché", "🏆 Top Opportunités"])

# ── TAB 1 : Profil ───────────────────────────────────────────────────────────
with tab1:
    st.header(PROFIL_DEFAULT["nom"])
    st.subheader(PROFIL_DEFAULT["titre"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Hard Skills")
        for skill in PROFIL_DEFAULT["hard_skills"]:
            st.markdown(f"- `{skill}`")

        st.markdown("### Skills bloquants maîtrisés")
        for skill in PROFIL_DEFAULT["skills_bloquants_maitrises"]:
            st.success(f"✅ {skill}")

        st.markdown("### Rare Skill")
        st.info(PROFIL_DEFAULT["rare_skill"])

    with col2:
        st.markdown("### Résultats clés (preuves terrain)")
        for r in PROFIL_DEFAULT["resultats_cles"]:
            st.success(f"✅ {r}")

        st.markdown("### Deal-breakers")
        st.error(f"❌ Contrats refusés : tout sauf `{', '.join(PROFIL_DEFAULT['preferences']['contrats_acceptes'])}`")
        st.error(f"❌ Présentiel pur = disqualification automatique")
        st.markdown(f"💰 Salaire minimum : `{PROFIL_DEFAULT['preferences']['salaire_min']:,} €/an`")

    st.divider()
    st.markdown("### Grille de scoring v2 — 6 dimensions")
    grille = pd.DataFrame([
        {"Critère": "Hard Skills Bloquants & Transférables", "Poids": "25 pts", "Logique": "Skills clés (SQL/Power BI) pèsent 60% de la note"},
        {"Critère": "Rare Skill Match", "Poids": "20 pts", "Logique": "Mon expertise rare correspond-elle à ce qu'ils cherchent ?"},
        {"Critère": "Cadrage Contractuel & Sectoriel", "Poids": "15 pts", "Logique": "DEAL-BREAKER : contrat et secteur accessibles ?"},
        {"Critère": "Télétravail / Flexibilité", "Poids": "15 pts", "Logique": "DEAL-BREAKER : Hybride ou Full Remote uniquement"},
        {"Critère": "Autonomie & Fit Transformation", "Poids": "15 pts", "Logique": "Poste de cadrage/pilotage vs exécution pure"},
        {"Critère": "Progression & Potentiel Scale", "Poids": "10 pts", "Logique": "Évolution possible, structure en croissance"},
    ])
    st.dataframe(grille, use_container_width=True, hide_index=True)

# ── TAB 2 : Analyse marché ───────────────────────────────────────────────────
with tab2:
    st.header("Analyse du marché")

    df = load_offres()
    scores, details_list, disqualifs, raisons = [], [], [], []
    for _, row in df.iterrows():
        s, d, dq, r = scorer_offre(row, PROFIL_DEFAULT)
        scores.append(s)
        details_list.append(d)
        disqualifs.append(dq)
        raisons.append(", ".join(r) if r else "")

    df["score"] = scores
    df["disqualifie"] = disqualifs
    df["raison_disqualif"] = raisons
    df["statut"] = df.apply(
        lambda x: "❌ Disqualifié" if x["disqualifie"]
        else ("🟢 Fort" if x["score"] >= 70 else ("🟡 Moyen" if x["score"] >= 45 else "🔴 Faible")),
        axis=1
    )

    df_valides = df[~df["disqualifie"]]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offres analysées", len(df))
    col2.metric("Disqualifiées auto", len(df[df["disqualifie"]]), delta=f"-{len(df[df['disqualifie']])} deal-breakers", delta_color="inverse")
    col3.metric("Fort match (≥70)", len(df_valides[df_valides["score"] >= 70]))
    col4.metric("Score moyen (valides)", f"{df_valides['score'].mean():.0f}/100" if len(df_valides) > 0 else "—")

    if len(df[df["disqualifie"]]) > 0:
        with st.expander(f"⚠️ {len(df[df['disqualifie']])} offre(s) disqualifiée(s) automatiquement"):
            for _, row in df[df["disqualifie"]].iterrows():
                st.markdown(f"- **{row['titre']}** ({row['entreprise']}) — {row['raison_disqualif']}")

    fig_hist = px.histogram(
        df_valides, x="score", nbins=8,
        title="Distribution des scores (offres valides)",
        color_discrete_sequence=["#00ff88"],
        labels={"score": "Score /100"},
    )
    fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#00ff88")
    st.plotly_chart(fig_hist, use_container_width=True)

    df_secteur = df_valides.groupby("secteur")["score"].mean().reset_index().sort_values("score", ascending=False)
    fig_sec = px.bar(
        df_secteur, x="secteur", y="score",
        title="Score moyen par secteur (offres valides)",
        color="score",
        color_continuous_scale=["#ff4444", "#ffd700", "#00ff88"],
        labels={"score": "Score moyen /100"},
    )
    fig_sec.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#00ff88")
    st.plotly_chart(fig_sec, use_container_width=True)

# ── TAB 3 : Top opportunités ─────────────────────────────────────────────────
with tab3:
    st.header("🏆 Top opportunités")

    df = load_offres()
    scores, details_list, disqualifs, raisons = [], [], [], []
    for _, row in df.iterrows():
        s, d, dq, r = scorer_offre(row, PROFIL_DEFAULT)
        scores.append(s)
        details_list.append(d)
        disqualifs.append(dq)
        raisons.append(", ".join(r) if r else "")

    df["score"] = scores
    df["disqualifie"] = disqualifs
    df["_details"] = details_list

    top = df[~df["disqualifie"]].sort_values("score", ascending=False).head(5)

    MAX_VALS = {
        "Hard Skills": 25,
        "Rare Skill": 20,
        "Cadrage Contractuel": 15,
        "Télétravail": 15,
        "Autonomie & Fit Transfo": 15,
        "Progression": 10,
    }

    for i, (_, offre) in enumerate(top.iterrows()):
        score = offre["score"]
        color = "#00ff88" if score >= 70 else ("#ffd700" if score >= 45 else "#ff4444")
        badge = "🟢 Fort match" if score >= 70 else ("🟡 Moyen" if score >= 45 else "🔴 Faible")

        with st.expander(f"{badge} — {offre['titre']} | {offre['entreprise']} ({score}/100)"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Score", f"{score}/100")
            c2.metric("Salaire", f"{offre['salaire_min']:,}–{offre['salaire_max']:,} €")
            c3.metric("Contrat", offre["type_contrat"])
            c4.metric("Télétravail", offre["teletravail"])

            st.markdown(f"**Secteur :** {offre['secteur']} | **Lieu :** {offre['lieu']} | **Source :** {offre['source']}")
            st.markdown(f"**Skills demandés :** `{offre['hard_skills']}`")
            st.markdown(f"**Rare skill recherché :** *{offre['rare_skill_recherche']}*")

            d = offre["_details"]
            if d:
                categories = list(d.keys())
                vals_pct = [round(d[k] / MAX_VALS.get(k, 1) * 100) for k in categories]

                fig_radar = go.Figure(go.Scatterpolar(
                    r=vals_pct + [vals_pct[0]],
                    theta=categories + [categories[0]],
                    fill="toself",
                    line_color=color,
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color="white"),
                        bgcolor="#1a1a2e",
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    height=320,
                    margin=dict(l=40, r=40, t=20, b=20),
                )
                st.plotly_chart(fig_radar, use_container_width=True, key=f"radar_top_{i}")

    st.divider()
    st.caption("💡 *Ce radar a été construit avec l'IA (Claude) pour démontrer une méthode de travail, pas un background technique. Chaque critère de scoring traduit une logique métier réelle issue de 8 ans d'expérience terrain.*")
