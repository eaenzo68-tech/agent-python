// Chargement des données de l'application (missions, concepts, badges)
// et petites fonctions pour les retrouver.

export const THEMES = {
  variables: "Variables et types",
  conditions: "Conditions",
  boucles: "Boucles",
  listes: "Listes",
  dictionnaires: "Dictionnaires",
  chaines: "Chaînes de caractères",
  fonctions: "Fonctions",
  exceptions: "Gestion des erreurs",
};

export const DIFFICULTES = { facile: "Facile", intermediaire: "Intermédiaire", difficile: "Difficile" };

export const NIVEAUX_PEDAGOGIQUES = {
  1: "Compléter une ligne",
  2: "Écrire quelques lignes",
  3: "Compléter une fonction",
  4: "Écrire une fonction",
  5: "Combiner des concepts",
  6: "Situation réelle",
  7: "Corriger un programme",
};

// Concepts pour lesquels le générateur possède des modèles de missions.
export const CONCEPTS_GENERABLES = [
  "variables", "types", "conditions", "boucle-for", "boucle-while", "listes",
  "dictionnaires", "chaines", "fonctions", "print-return", "exceptions",
];

export const donnees = {
  missions: [],
  concepts: [],
  badges: [],
  missionsParId: new Map(),
  conceptsParId: new Map(),
};

async function lireJson(chemin) {
  const reponse = await fetch(chemin, { cache: "no-cache" });
  if (!reponse.ok) throw new Error(`Impossible de lire ${chemin} (${reponse.status})`);
  return reponse.json();
}

export async function chargerDonnees() {
  const [missions, concepts, badges] = await Promise.all([
    lireJson("data/missions.json"),
    lireJson("data/concepts.json"),
    lireJson("data/badges.json"),
  ]);
  donnees.missions = missions.sort((a, b) => a.ordre - b.ordre);
  donnees.concepts = concepts;
  donnees.badges = badges;
  donnees.missionsParId = new Map(missions.map((m) => [m.id, m]));
  donnees.conceptsParId = new Map(concepts.map((c) => [c.id, c]));
}

/** Toutes les missions : banque + générées + créées à la main. */
export function toutesLesMissions(etat) {
  return [
    ...donnees.missions,
    ...Object.values(etat.missionsGenerees || {}),
    ...Object.values(etat.missionsPerso || {}),
  ];
}

export function trouverMission(etat, id) {
  return donnees.missionsParId.get(id) || etat.missionsGenerees?.[id] || etat.missionsPerso?.[id] || null;
}

export function nomConcept(id) {
  return donnees.conceptsParId.get(id)?.nom || id;
}
