# 🚀 ResearchPilot

ResearchPilot est une plateforme intelligente d'analyse et de recommandation d'articles scientifiques basée sur l'intelligence artificielle.

L'application permet aux chercheurs, étudiants et enseignants de télécharger un article scientifique au format PDF et d'obtenir automatiquement :

- Une classification du domaine de recherche.
- Un résumé académique structuré.
- Des mots-clés pertinents.
- Des recommandations d'articles similaires.
- Une analyse rapide du contenu scientifique.

---

## ✨ Fonctionnalités

### 📄 Analyse de PDF

- Téléchargement d'articles scientifiques.
- Extraction automatique du texte.
- Traitement et analyse du contenu.

### 🧠 Classification

- Classification du document par domaine.
- Identification du sous-domaine.
- Score de confiance de prédiction.

### 📝 Résumé automatique

Génération d'un résumé académique comprenant :

- Objectif de l'étude
- Méthodologie
- Résultats principaux
- Conclusion

### 🔑 Extraction de mots-clés

Identification automatique des mots-clés les plus importants du document.

### 📚 Recommandation d'articles

- Recherche d'articles similaires.
- Classement selon la similarité sémantique.
- Affichage des scores de pertinence.

---

## 🛠️ Technologies utilisées

### Frontend

- React.js
- Tailwind CSS
- Axios

### Backend

- FastAPI
- Python
- PostgreSQL

### Intelligence Artificielle

- Langchain

### APIs

- Groq API

---

## 📂 Architecture du projet

```text
ResearchPilot
│
├── frontend
│   ├── src
│   ├── components
│   ├── pages
│   └── services
│
├── backend
│   ├── app
│   ├── models
│   ├── routes
│   ├── services
│   └── database
│
└── README.md
```

---

## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone https://github.com/FatimaZahraLasfar/ResearchPilot.git
cd ResearchPilot
```

### 2. Backend

```bash
cd researchpilot_backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uv run uvicorn app.main:app --reload   
```

Le serveur sera accessible sur :

```text
http://localhost:8000
```

### 3. Frontend

```bash
cd researchpilot_frontend

npm install

npm run dev
```

Le frontend sera accessible sur :

```text
http://localhost:8080
```

## 📜 Licence

Ce projet est réalisé dans un cadre académique et pédagogique.
