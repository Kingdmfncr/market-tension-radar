# 🎯 Market Tension Radar

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://market-tension-radar.streamlit.app)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Built with Claude](https://img.shields.io/badge/Built%20with-Claude%20AI-orange)

> **Proof of concept** — Outil de scoring d'adéquation candidat × offres d'emploi, construit avec l'IA sans background technique.
>
> 📖 **Transparence totale :** lisez [`PROMPT_LOG.md`](PROMPT_LOG.md) pour voir exactement comment j'ai piloté l'IA à chaque étape.

---

## Le contexte réel derrière ce projet

Ce projet est né de **Sovereign Career**, un système de veille et de pilotage de recherche d'emploi que j'ai conçu pour répondre à un problème concret : comment savoir rapidement si une offre vaut la peine qu'on la travaille sérieusement ?

En 8 ans de terrain (CHU Rouen, CODEVI, PERAGRO), j'ai développé une grille de lecture instinctive du marché. Ce projet la formalise en algo.

---

## Ce que fait l'app

**3 onglets, 1 logique claire :**

| Onglet | Contenu |
|--------|---------|
| 👤 Mon Profil | Hard skills, rare skill, résultats terrain chiffrés |
| 📊 Analyse du Marché | Distribution des scores, comparaison par secteur |
| 🏆 Top Opportunités | Top 5 offres avec radar de détail par critère |

---

## Moteur de scoring (5 dimensions)

| Critère | Poids | Logique |
|---------|-------|---------|
| Hard Skills transférables | 30 pts | % des skills demandés que je maîtrise |
| Rare Skill match | 25 pts | Mon expertise rare correspond-elle à ce qu'ils cherchent ? |
| Télétravail | 15 pts | Hybride ou Full Remote = deal-breaker |
| Autonomie sur les missions | 15 pts | Score interne basé sur le descriptif |
| Progression possible | 15 pts | Potentiel d'évolution dans l'entreprise |

**Total : 100 pts** → ≥70 : Fort match | 45-69 : Moyen | <45 : Faible

---

## Comment j'ai construit ça (ma méthode IA)

Je n'ai pas de background développeur. Voici mon process réel :

1. **J'ai défini la logique métier** — les critères de scoring viennent de mon expérience terrain, pas d'un algo existant
2. **J'ai décrit la structure à Claude (IA)** — "je veux un tableau avec ces colonnes, un score sur ces 5 dimensions, un radar visuel par offre"
3. **J'ai itéré sur les prompts** — chaque ajustement visuel ou logique a été une demande précise ("ajoute un radar, change la couleur des scores forts en vert")
4. **J'ai validé la cohérence métier** — l'IA génère le code, moi je valide que le résultat a du sens dans la réalité du recrutement

**Ce projet démontre :** capacité à cadrer un problème, à le décomposer en critères mesurables, et à piloter un outil IA jusqu'au livrable final.

---

## Utiliser cet outil pour votre propre profil

**Aucune connaissance technique requise. 3 étapes :**

**Étape 1 — Forkez ce dépôt** (bouton "Fork" en haut à droite sur GitHub)

**Étape 2 — Ouvrez `mon_profil.py`** et remplacez les valeurs par les vôtres :
- Votre nom, vos hard skills, votre rare skill
- Vos résultats terrain (chiffrés si possible)
- Vos préférences (télétravail, salaire minimum)

**Étape 3 — Lancez l'app :**
```bash
pip install -r requirements.txt
streamlit run app.py
```

> 💡 Vous pouvez aussi remplacer `data/offres_emploi.csv` par vos vraies offres copiées depuis LinkedIn ou WTTJ.

---

## Lancer l'app en local (version originale)

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Stack technique

- **Python** + **Streamlit** (interface)
- **Pandas** (manipulation données)
- **Plotly** (visualisations interactives)
- **Claude (Anthropic)** — co-pilote de développement

---

*Construit par Gisèle Metouck | Data & Product Manager | AI Orchestrator*
*Ce n'est pas du code pour du code — c'est 8 ans d'expérience terrain formalisés en outil.*
