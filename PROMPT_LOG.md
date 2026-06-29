# PROMPT LOG — Comment j'ai construit ce projet avec l'IA

> Ce fichier documente ma méthode de travail réelle avec l'IA (Claude).
> Je n'ai pas de background développeur. Ce log prouve que la valeur n'est pas dans le code — elle est dans la capacité à cadrer un problème et à piloter l'IA jusqu'au livrable.

---

## Contexte de départ

**Mon problème réel :** Quand je cherche un poste ou que j'aide quelqu'un, je passe trop de temps à évaluer des offres qui ne correspondent pas vraiment. J'avais une grille de lecture dans la tête depuis 8 ans de terrain — je voulais la formaliser.

**Ce que je n'avais pas :** du code Python, des connaissances Streamlit ou Plotly, le temps d'apprendre.

**Ce que j'avais :** une logique métier claire, des résultats terrain chiffrés, et une méthode de travail avec l'IA.

---

## Étape 1 — Cadrage du problème (moi → IA)

**Mon prompt de départ :**
> "Je veux construire un outil pour scorer des offres d'emploi par rapport à un profil candidat. Je n'ai pas de bagage technique. Je veux montrer comment je travaille avec l'IA même sans savoir coder. Pose-moi toutes les questions nécessaires en une fois."

**Ce que j'ai apporté à cette étape :**
- La logique de scoring (hard skills transférables, rare skill, télétravail, autonomie, progression)
- La source de données (LinkedIn + Welcome to the Jungle)
- L'objectif final (aider quelqu'un à connaître sa valeur marché)
- Le profil pilote (le mien, pour une démo authentique)

**Ce que l'IA a apporté :**
- La structure technique (Streamlit + Pandas + Plotly)
- La traduction de ma logique en algorithme de scoring
- La génération du code complet

---

## Étape 2 — Données simulées

**Mon input :**
> "Crée 15 offres d'emploi réalistes issues de LinkedIn et WTTJ, adaptées à un profil Data/Product/BA avec expérience santé, cosmétique et international."

**Décision métier que j'ai prise :**
- Inclure des secteurs variés (Santé, Conseil, FinTech, Cosmétique, ONG) pour que le radar soit parlant
- Ajouter un champ `rare_skill_recherche` par offre — c'est le critère différenciant, celui qui me sépare des candidats interchangeables

---

## Étape 3 — Architecture 3 onglets

**Mon prompt :**
> "L'app doit avoir 3 onglets : Mon Profil (mes preuves terrain), Analyse du Marché (distribution + secteurs), Top Opportunités (top 5 avec radar visuel par offre)."

**Ma contrainte explicite :**
> "Le design doit être sombre, premium, avec du vert émeraude pour les bons scores et du rouge pour les mauvais. Pas de design générique."

**Itération :**
J'ai demandé à l'IA d'ajouter le radar Plotly par offre dans le 3ème onglet après avoir vu la première version — parce que la liste seule n'était pas assez visuelle pour un recruteur pressé.

---

## Étape 4 — Rendre l'outil open source

**Ma décision stratégique :**
> "Je veux que n'importe qui puisse forker ce projet et l'adapter à son propre profil sans toucher au code."

**Ce que j'ai demandé à l'IA :**
> "Sépare le profil dans un fichier `mon_profil.py` avec des commentaires en français qui expliquent chaque champ sans jargon technique. L'utilisateur ne doit modifier QUE ce fichier."

**Résultat :** Le fichier `mon_profil.py` est auto-documenté. Un non-développeur peut le personnaliser en 5 minutes.

---

## Ce que ce projet prouve (pour un recruteur)

| Compétence démontrée | Preuve dans ce projet |
|---|---|
| Cadrage d'un problème métier | Logique de scoring issue de 8 ans terrain, pas d'un template |
| Décomposition analytique | 5 critères pondérés avec justification métier |
| Pilotage de l'IA | Prompts précis, itérations ciblées, décisions validées par moi |
| Product thinking | 3 onglets correspondant à 3 cas d'usage distincts |
| Open source mindset | Fichier `mon_profil.py` pensé pour la réutilisation par des non-devs |
| Autonomie de livraison | Projet complet livré end-to-end, sans équipe technique |

---

## Ma conclusion

> Je ne suis pas développeuse. Je suis quelqu'un qui comprend suffisamment le métier et la donnée pour piloter l'IA vers des livrables de niveau senior.
> Ce log en est la preuve transparente.

*Gisèle Metouck — Data & Product Manager | AI Orchestrator*
