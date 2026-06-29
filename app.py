import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mon_profil import MON_PROFIL

st.set_page_config(
    page_title="Market Tension Radar",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
    .badge-disqualified { background:#ff4444; color:white; padding:2px 10px; border-radius:20px; font-size:0.8rem; font-weight:bold; }
    .badge-fort  { background:#00ff88; color:black; padding:2px 10px; border-radius:20px; font-size:0.8rem; font-weight:bold; }
    .badge-moyen { background:#ffd700; color:black; padding:2px 10px; border-radius:20px; font-size:0.8rem; font-weight:bold; }
    .sidebar-tip { background:#1a1a2e; border-left:3px solid #00ff88; padding:8px 12px; border-radius:4px; font-size:0.85rem; }
</style>
""", unsafe_allow_html=True)

# ── Chargement données ────────────────────────────────────────────────────────
@st.cache_data
def load_offres():
    return pd.read_csv("data/offres_emploi.csv")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Profil personnalisable en live
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.title("👤 Mon Profil")
st.sidebar.markdown('<div class="sidebar-tip">✏️ Modifiez votre profil ici — les scores se recalculent instantanément</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

nom   = st.sidebar.text_input("Votre nom", value=MON_PROFIL["nom"])
titre = st.sidebar.text_input("Votre titre", value=MON_PROFIL["titre"])

st.sidebar.markdown("**Hard Skills** *(séparés par des virgules)*")
hard_skills_input = st.sidebar.text_area(
    "Vos compétences",
    value=", ".join(MON_PROFIL["hard_skills"]),
    height=80,
    label_visibility="collapsed"
)

st.sidebar.markdown("**Skills bloquants maîtrisés** *(les plus exigés du marché)*")
skills_bloquants_input = st.sidebar.text_area(
    "Skills bloquants",
    value=", ".join(MON_PROFIL["skills_bloquants_maitrises"]),
    height=60,
    label_visibility="collapsed"
)

st.sidebar.markdown("**Mots-clés de votre Rare Skill** *(séparés par des virgules)*")
rare_tags_input = st.sidebar.text_area(
    "Rare skill tags",
    value=", ".join(MON_PROFIL["rare_skill_tags"]),
    height=100,
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Préférences**")
teletravail_pref = st.sidebar.multiselect(
    "Télétravail accepté",
    ["Hybride", "Full Remote", "Présentiel"],
    default=MON_PROFIL["preferences"]["teletravail"]
)
contrats_pref = st.sidebar.multiselect(
    "Types de contrat acceptés",
    ["CDI", "CDD", "Freelance", "Mission", "Alternance"],
    default=MON_PROFIL["preferences"]["contrats_acceptes"]
)
salaire_min = st.sidebar.slider(
    "Salaire minimum (€/an)",
    min_value=25000, max_value=100000,
    value=MON_PROFIL["preferences"]["salaire_min"],
    step=1000
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 *Forkez ce projet sur [GitHub](https://github.com/Kingdmfncr/market-tension-radar) pour personnaliser les offres aussi.*")

# ── Construction du profil depuis la sidebar ─────────────────────────────────
PROFIL = {
    "nom": nom,
    "titre": titre,
    "hard_skills": [s.strip() for s in hard_skills_input.split(",") if s.strip()],
    "skills_bloquants_maitrises": [s.strip() for s in skills_bloquants_input.split(",") if s.strip()],
    "rare_skill": MON_PROFIL["rare_skill"],
    "rare_skill_tags": [s.strip() for s in rare_tags_input.split(",") if s.strip()],
    "annees_experience": MON_PROFIL["annees_experience"],
    "resultats_cles": MON_PROFIL["resultats_cles"],
    "preferences": {
        "teletravail": teletravail_pref,
        "contrats_acceptes": contrats_pref,
        "salaire_min": salaire_min,
    }
}

# ── Moteur de scoring v2 ─────────────────────────────────────────────────────
def scorer_offre(offre, profil):
    details = {}
    disqualified = False
    raison_disqualif = []

    contrat_ok = offre["type_contrat"] in profil["preferences"]["contrats_acceptes"]
    if not contrat_ok:
        disqualified = True
        raison_disqualif.append(f"Contrat '{offre['type_contrat']}' non accepté")

    tele_ok = offre["teletravail"] in profil["preferences"]["teletravail"]
    if not tele_ok:
        disqualified = True
        raison_disqualif.append(f"Télétravail '{offre['teletravail']}' non compatible")

    if disqualified:
        return 0, {}, True, raison_disqualif

    hard_skills_offre = [s.strip() for s in offre["hard_skills"].split(",")]
    skills_bloquants_offre = [s.strip() for s in str(offre["skills_bloquants"]).split(",") if s.strip()]

    match_general = sum(1 for s in hard_skills_offre if any(
        s.lower() in ps.lower() or ps.lower() in s.lower()
        for ps in profil["hard_skills"]
    ))
    pts_general = (match_general / max(len(hard_skills_offre), 1)) * 10

    if skills_bloquants_offre:
        match_bloquants = sum(1 for s in skills_bloquants_offre if any(
            s.lower() in ps.lower() or ps.lower() in s.lower()
            for ps in profil["skills_bloquants_maitrises"]
        ))
        pts_bloquants = (match_bloquants / len(skills_bloquants_offre)) * 15
    else:
        pts_bloquants = 15

    details["Hard Skills"] = round(min(25, pts_general + pts_bloquants))

    rare_offre = offre["rare_skill_recherche"].lower()
    match_rare = any(tag.lower() in rare_offre or rare_offre in tag.lower() for tag in profil["rare_skill_tags"])
    details["Rare Skill"] = 20 if match_rare else 0

    secteur_ok = str(offre.get("secteur_accessible", "Oui")) == "Oui"
    details["Cadrage Contractuel"] = 15 if secteur_ok else 7

    details["Télétravail"] = 15

    fit_transfo = str(offre.get("fit_transformation", "Non")) == "Oui"
    details["Autonomie & Fit Transfo"] = min(15, round((offre["autonomie_score"] / 5) * 10) + (5 if fit_transfo else 0))

    details["Progression"] = round((offre["progression_score"] / 5) * 10)

    return sum(details.values()), details, False, []

# ══════════════════════════════════════════════════════════════════════════════
# MAIN — Calcul scores
# ══════════════════════════════════════════════════════════════════════════════
st.title("🎯 Market Tension Radar")
st.caption(f"Profil actif : **{PROFIL['nom']}** — {PROFIL['titre']}")

df = load_offres()
scores, details_list, disqualifs, raisons = [], [], [], []
for _, row in df.iterrows():
    s, d, dq, r = scorer_offre(row, PROFIL)
    scores.append(s)
    details_list.append(d)
    disqualifs.append(dq)
    raisons.append(", ".join(r) if r else "")

df["score"]         = scores
df["_details"]      = details_list
df["disqualifie"]   = disqualifs
df["raison_disqualif"] = raisons
df_valides = df[~df["disqualifie"]]

tab1, tab2, tab3 = st.tabs(["👤 Mon Profil", "📊 Analyse du Marché", "🏆 Top Opportunités"])

# ── TAB 1 : Profil ───────────────────────────────────────────────────────────
with tab1:
    st.header(PROFIL["nom"])
    st.subheader(PROFIL["titre"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Hard Skills")
        for s in PROFIL["hard_skills"]:
            st.markdown(f"- `{s}`")
        st.markdown("### Skills bloquants maîtrisés")
        for s in PROFIL["skills_bloquants_maitrises"]:
            st.success(f"✅ {s}")

    with col2:
        st.markdown("### Résultats clés (preuves terrain)")
        for r in PROFIL["resultats_cles"]:
            st.success(f"✅ {r}")
        st.markdown("### Deal-breakers")
        st.error(f"❌ Contrats refusés : tout sauf `{', '.join(PROFIL['preferences']['contrats_acceptes'])}`")
        st.error(f"❌ Présentiel pur = disqualification automatique")
        st.markdown(f"💰 Salaire minimum : `{PROFIL['preferences']['salaire_min']:,} €/an`")

    st.divider()
    st.markdown("### Grille de scoring — 6 dimensions")
    st.dataframe(pd.DataFrame([
        {"Critère": "Hard Skills Bloquants & Transférables", "Poids": "25 pts", "Logique": "Skills clés pèsent 60% de la note"},
        {"Critère": "Rare Skill Match",                      "Poids": "20 pts", "Logique": "Mon expertise rare correspond-elle à ce qu'ils cherchent ?"},
        {"Critère": "Cadrage Contractuel & Sectoriel",       "Poids": "15 pts", "Logique": "DEAL-BREAKER : contrat et secteur accessibles ?"},
        {"Critère": "Télétravail / Flexibilité",             "Poids": "15 pts", "Logique": "DEAL-BREAKER : Hybride ou Full Remote uniquement"},
        {"Critère": "Autonomie & Fit Transformation",        "Poids": "15 pts", "Logique": "Poste de cadrage/pilotage vs exécution pure"},
        {"Critère": "Progression & Potentiel Scale",         "Poids": "10 pts", "Logique": "Évolution possible, structure en croissance"},
    ]), use_container_width=True, hide_index=True)

# ── TAB 2 : Analyse marché ────────────────────────────────────────────────────
with tab2:
    st.header("Analyse du marché")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Offres analysées", len(df))
    col2.metric("Disqualifiées auto", len(df[df["disqualifie"]]), delta_color="inverse",
                delta=f"-{len(df[df['disqualifie']])} deal-breakers")
    col3.metric("Fort match (≥70)", len(df_valides[df_valides["score"] >= 70]))
    col4.metric("Score moyen", f"{df_valides['score'].mean():.0f}/100" if len(df_valides) > 0 else "—")

    if len(df[df["disqualifie"]]) > 0:
        with st.expander(f"⚠️ {len(df[df['disqualifie']])} offre(s) disqualifiée(s)"):
            for _, row in df[df["disqualifie"]].iterrows():
                st.markdown(f"- **{row['titre']}** ({row['entreprise']}) — {row['raison_disqualif']}")

    fig_hist = px.histogram(df_valides, x="score", nbins=8,
                            title="Distribution des scores",
                            color_discrete_sequence=["#00ff88"],
                            labels={"score": "Score /100"})
    fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#00ff88")
    st.plotly_chart(fig_hist, use_container_width=True, key="hist_marche")

    df_sec = df_valides.groupby("secteur")["score"].mean().reset_index().sort_values("score", ascending=False)
    fig_sec = px.bar(df_sec, x="secteur", y="score",
                     title="Score moyen par secteur",
                     color="score", color_continuous_scale=["#ff4444","#ffd700","#00ff88"],
                     labels={"score": "Score moyen /100"})
    fig_sec.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e", font_color="white", title_font_color="#00ff88")
    st.plotly_chart(fig_sec, use_container_width=True, key="bar_secteur")

# ── TAB 3 : Top opportunités ──────────────────────────────────────────────────
with tab3:
    st.header("🏆 Top opportunités")

    MAX_VALS = {"Hard Skills": 25, "Rare Skill": 20, "Cadrage Contractuel": 15,
                "Télétravail": 15, "Autonomie & Fit Transfo": 15, "Progression": 10}

    top = df_valides.sort_values("score", ascending=False).head(5)

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
                cats = list(d.keys())
                vals = [round(d[k] / MAX_VALS.get(k, 1) * 100) for k in cats]
                fig_radar = go.Figure(go.Scatterpolar(
                    r=vals + [vals[0]], theta=cats + [cats[0]],
                    fill="toself", line_color=color,
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0,100], color="white"), bgcolor="#1a1a2e"),
                    paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=320,
                    margin=dict(l=40, r=40, t=20, b=20),
                )
                st.plotly_chart(fig_radar, use_container_width=True, key=f"radar_top_{i}")

    st.divider()
    st.caption("💡 *Modifiez votre profil dans la sidebar — les scores se recalculent en temps réel. Construit avec l'IA sans background technique.*")
