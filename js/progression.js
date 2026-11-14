// Règles de progression : score, XP, niveaux, grades, badges, déblocage,
// statistiques par concept et recommandations de révision.
// Ce fichier ne touche pas à l'affichage : il ne fait que calculer.

import { donnees, trouverMission, toutesLesMissions, nomConcept } from "./donnees.js";

export const GRADES = [
  { nom: "Recrue", xp: 0 },
  { nom: "Agent junior", xp: 250 },
  { nom: "Agent de terrain", xp: 700 },
  { nom: "Analyste", xp: 1500 },
  { nom: "Agent spécial", xp: 2700 },
  { nom: "Expert Python", xp: 4200 },
];

export const MULTIPLICATEURS = { facile: 1, intermediaire: 1.5, difficile: 2 };
export const SEUIL_ERREUR_RECURRENTE = 3;

const BAREME_PAR_DEFAUT = {
  points: 100, penalite_indice: 10, penalite_tentative: 5, penalite_solution: 50, bonus_qualite: 10,
};

// ---------------------------------------------------------------------------
// Niveaux et grades
// ---------------------------------------------------------------------------

export function grade(xp) {
  let index = 0;
  GRADES.forEach((g, i) => { if (xp >= g.xp) index = i; });
  const suivant = GRADES[index + 1] || null;
  const progression = suivant ? (xp - GRADES[index].xp) / (suivant.xp - GRADES[index].xp) : 1;
  return { ...GRADES[index], index, habilitation: index + 1, suivant, progression };
}

/** Niveau d'agent : il faut 50 × (n - 1)² XP pour atteindre le niveau n. */
export function niveau(xp) {
  const n = Math.floor(Math.sqrt(Math.max(0, xp) / 50)) + 1;
  const debut = 50 * (n - 1) ** 2;
  const fin = 50 * n ** 2;
  return { niveau: n, xpDansNiveau: xp - debut, xpPourNiveau: fin - debut, progression: (xp - debut) / (fin - debut) };
}

// ---------------------------------------------------------------------------
// Suivi d'une mission
// ---------------------------------------------------------------------------

function nouvelEnCours() {
  return { indicesUtilises: 0, envoisEchoues: 0, solutionRevelee: false, debut: new Date().toISOString() };
}

export function suiviMission(etat, id) {
  if (!etat.missions[id]) {
    etat.missions[id] = {
      accomplie: false, nbReussites: 0, meilleurScore: 0, meilleureQualite: 0,
      tentativesTotales: 0, indicesTotaux: 0, enCours: nouvelEnCours(),
    };
  }
  if (!etat.missions[id].enCours) etat.missions[id].enCours = nouvelEnCours();
  return etat.missions[id];
}

export function calculerScore(mission, enCours, scoreQualite) {
  const bareme = { ...BAREME_PAR_DEFAUT, ...(mission.bareme || {}) };
  const details = [{ libelle: "Mission accomplie", valeur: bareme.points }];
  const indices = Math.min(3, enCours.indicesUtilises || 0);
  if (indices) details.push({ libelle: `${indices} indice(s) utilisé(s)`, valeur: -indices * bareme.penalite_indice });
  const echecs = Math.min(5, enCours.envoisEchoues || 0);
  if (echecs) details.push({ libelle: `${echecs} envoi(s) échoué(s)`, valeur: -echecs * bareme.penalite_tentative });
  if (enCours.solutionRevelee) details.push({ libelle: "Solution révélée", valeur: -bareme.penalite_solution });
  if (scoreQualite >= 85) details.push({ libelle: "Bonus code propre", valeur: bareme.bonus_qualite });
  const score = Math.max(10, details.reduce((total, d) => total + d.valeur, 0));
  return { score, details, maximum: bareme.points + bareme.bonus_qualite };
}

/** À appeler après chaque « Envoyer la mission ». Modifie l'état et renvoie un résumé. */
export function enregistrerEnvoi(etat, mission, rapport) {
  const suivi = suiviMission(etat, mission.id);
  const enCours = suivi.enCours;
  suivi.tentativesTotales += 1;
  etat.stats.envois += 1;
  etat.derniereMission = mission.id;

  if (!rapport.reussi) {
    enCours.envoisEchoues += 1;
    for (const concept of mission.concepts || []) statConcept(etat, concept).echecs += 1;
    return { reussi: false, envoisEchoues: enCours.envoisEchoues };
  }

  const scoreQualite = rapport.qualite?.score ?? 0;
  const { score, details, maximum } = calculerScore(mission, enCours, scoreQualite);
  const ancienMeilleur = suivi.meilleurScore || 0;
  const multiplicateur = MULTIPLICATEURS[mission.difficulte] || 1;
  const xpGagne = Math.round(Math.max(0, score - ancienMeilleur) * multiplicateur);
  const premiereFois = !suivi.accomplie;
  const propre = enCours.envoisEchoues <= 1 && !enCours.solutionRevelee;
  const maintenant = new Date().toISOString();

  Object.assign(suivi, {
    accomplie: true,
    nbReussites: suivi.nbReussites + 1,
    meilleurScore: Math.max(ancienMeilleur, score),
    meilleureQualite: Math.max(suivi.meilleureQualite || 0, scoreQualite),
    derniereReussite: maintenant,
    premiereReussite: suivi.premiereReussite || maintenant,
    indicesTotaux: suivi.indicesTotaux + enCours.indicesUtilises,
    // Copie des informations utiles même si la mission générée est supprimée plus tard.
    theme: mission.theme, niveau: mission.niveau, origine: mission.origine || "banque",
    concepts: mission.concepts || [], titre: mission.titre, difficulte: mission.difficulte,
  });

  etat.serie = propre ? etat.serie + 1 : 0;
  etat.meilleureSerie = Math.max(etat.meilleureSerie, etat.serie);
  if (enCours.indicesUtilises === 0 && !enCours.solutionRevelee) etat.stats.sansIndice += 1;
  etat.stats.perseverance = Math.max(etat.stats.perseverance, enCours.envoisEchoues);
  for (const concept of mission.concepts || []) statConcept(etat, concept).reussites += 1;

  const avant = { grade: grade(etat.xp).nom, niveau: niveau(etat.xp).niveau };
  etat.xp += xpGagne;
  const apres = { grade: grade(etat.xp).nom, niveau: niveau(etat.xp).niveau };

  etat.historique.unshift({
    date: maintenant, missionId: mission.id, titre: mission.titre, score, xp: xpGagne,
    qualite: scoreQualite, theme: mission.theme, indices: enCours.indicesUtilises,
    envois: enCours.envoisEchoues + 1, solution: enCours.solutionRevelee,
  });
  const resume = {
    reussi: true, score, details, maximum, xpGagne, premiereFois, ancienMeilleur, propre,
    indices: enCours.indicesUtilises, envoisEchoues: enCours.envoisEchoues,
    nouveauGrade: avant.grade !== apres.grade ? apres.grade : null,
    nouveauNiveau: avant.niveau !== apres.niveau ? apres.niveau : null,
  };
  suivi.enCours = nouvelEnCours();
  resume.nouveauxBadges = evaluerBadges(etat);
  return resume;
}

export function enregistrerIndice(etat, mission, numero) {
  const enCours = suiviMission(etat, mission.id).enCours;
  enCours.indicesUtilises = Math.max(enCours.indicesUtilises, numero);
  etat.derniereMission = mission.id;
}

export function enregistrerSolution(etat, mission) {
  suiviMission(etat, mission.id).enCours.solutionRevelee = true;
}

/** Garde une trace d'une erreur pour l'historique et les révisions intelligentes. */
export function enregistrerErreur(etat, mission, diagnostic, source) {
  if (!diagnostic || !diagnostic.categorie) return null;
  const precedente = etat.erreurs[0];
  if (precedente && precedente.missionId === mission.id && precedente.categorie === diagnostic.categorie
      && precedente.ligne === diagnostic.ligne && Date.now() - new Date(precedente.date).getTime() < 60_000) {
    return null; // même erreur répétée à la suite : on ne la compte qu'une fois
  }
  const entree = {
    date: new Date().toISOString(),
    missionId: mission.id,
    titreMission: mission.titre,
    source,
    categorie: diagnostic.categorie,
    nomCategorie: diagnostic.nom_categorie,
    type: diagnostic.type,
    titre: diagnostic.titre,
    description: diagnostic.description,
    ligne: diagnostic.ligne,
    concept: diagnostic.concept,
    extrait: (diagnostic.extrait || []).map((l) => ({ numero: l.numero, texte: l.texte, erreur: l.erreur })),
  };
  etat.erreurs.unshift(entree);
  return entree;
}

function statConcept(etat, id) {
  if (!etat.concepts[id]) etat.concepts[id] = { reussites: 0, echecs: 0 };
  return etat.concepts[id];
}

// ---------------------------------------------------------------------------
// Déblocage et statut des missions
// ---------------------------------------------------------------------------

export function estDebloquee(etat, mission) {
  if (etat.reglages.modeLibre) return true;
  if ((mission.origine && mission.origine !== "banque") || mission.demo || mission.revision_pour?.length) return true;
  const memeTheme = donnees.missions.filter((m) => m.theme === mission.theme).sort((a, b) => a.ordre - b.ordre);
  const position = memeTheme.findIndex((m) => m.id === mission.id);
  if (position <= 0) return true;
  return Boolean(etat.missions[memeTheme[position - 1].id]?.accomplie);
}

export function statutMission(etat, mission) {
  const suivi = etat.missions[mission.id];
  if (suivi?.accomplie) return "accomplie";
  if (!estDebloquee(etat, mission)) return "classifie";
  if ((suivi && suivi.tentativesTotales > 0) || etat.brouillons[mission.id]) return "en_cours";
  return "disponible";
}

/** Mission à faire après celle-ci : la suivante du même thème, sinon la prochaine du parcours. */
export function missionSuivante(etat, mission) {
  if (mission.origine === "banque" || !mission.origine) {
    const memeTheme = donnees.missions.filter((m) => m.theme === mission.theme && m.ordre > mission.ordre)
      .sort((a, b) => a.ordre - b.ordre);
    const suivante = memeTheme.find((m) => !etat.missions[m.id]?.accomplie && estDebloquee(etat, m));
    if (suivante) return suivante;
  } else {
    const autres = Object.values(mission.origine === "perso" ? etat.missionsPerso : etat.missionsGenerees)
      .filter((m) => m.id !== mission.id && !etat.missions[m.id]?.accomplie);
    if (autres.length) return autres[0];
  }
  return donnees.missions.find((m) => !etat.missions[m.id]?.accomplie && estDebloquee(etat, m)) || null;
}

// ---------------------------------------------------------------------------
// Badges
// ---------------------------------------------------------------------------

function missionsAccomplies(etat) {
  return Object.entries(etat.missions).filter(([, suivi]) => suivi.accomplie);
}

export function valeurBadge(etat, condition) {
  const accomplies = missionsAccomplies(etat);
  switch (condition.type) {
    case "missions_accomplies": return accomplies.length;
    case "theme": return accomplies.filter(([, s]) => s.theme === condition.theme).length;
    case "niveau": return accomplies.filter(([, s]) => s.niveau === condition.niveau).length;
    case "qualite_excellente": return accomplies.filter(([, s]) => (s.meilleureQualite || 0) >= 85).length;
    case "sans_indice": return etat.stats.sansIndice;
    case "serie": return etat.meilleureSerie;
    case "perseverance": return etat.stats.perseverance;
    case "missions_hors_banque": return accomplies.filter(([, s]) => s.origine && s.origine !== "banque").length;
    default: return 0;
  }
}

/** Débloque les nouveaux badges et renvoie la liste de ceux qui viennent d'être obtenus. */
export function evaluerBadges(etat) {
  const nouveaux = [];
  for (const badge of donnees.badges) {
    if (etat.badges[badge.id]) continue;
    if (valeurBadge(etat, badge.condition) >= badge.condition.valeur) {
      etat.badges[badge.id] = new Date().toISOString();
      nouveaux.push(badge);
    }
  }
  return nouveaux;
}

// ---------------------------------------------------------------------------
// Concepts maîtrisés / à revoir
// ---------------------------------------------------------------------------

export function statutConcept(stat) {
  if (!stat || stat.reussites + stat.echecs === 0) return "nouveau";
  if (stat.reussites >= 2 && stat.echecs <= stat.reussites * 2) return "maitrise";
  if (stat.echecs >= 3 && stat.echecs > stat.reussites * 2) return "a_revoir";
  return "en_cours";
}

export const LIBELLES_STATUT_CONCEPT = {
  nouveau: "Pas encore travaillé", maitrise: "Maîtrisé", a_revoir: "À revoir", en_cours: "En progression",
};

export function bilanConcepts(etat) {
  return donnees.concepts.map((concept) => {
    const stat = etat.concepts[concept.id] || { reussites: 0, echecs: 0 };
    return { ...concept, ...stat, statut: statutConcept(stat) };
  });
}

/** Concepts des dernières missions (pour le tableau de bord). */
export function conceptsRecents(etat, nombre = 6) {
  const vus = [];
  for (const entree of etat.historique) {
    const mission = trouverMission(etat, entree.missionId) || etat.missions[entree.missionId];
    for (const concept of mission?.concepts || []) {
      if (!vus.includes(concept)) vus.push(concept);
    }
    if (vus.length >= nombre) break;
  }
  return vus.slice(0, nombre);
}

// ---------------------------------------------------------------------------
// Erreurs récurrentes et révisions intelligentes
// ---------------------------------------------------------------------------

export function categoriesFrequentes(etat, fenetre = 60) {
  const compte = new Map();
  for (const erreur of etat.erreurs.slice(0, fenetre)) {
    const entree = compte.get(erreur.categorie) || {
      categorie: erreur.categorie, nom: erreur.nomCategorie || erreur.categorie,
      concept: erreur.concept, nombre: 0, derniere: erreur.date,
    };
    entree.nombre += 1;
    compte.set(erreur.categorie, entree);
  }
  return [...compte.values()].sort((a, b) => b.nombre - a.nombre);
}

/** Mission de la banque spécialement conçue pour cette catégorie d'erreur. */
export function missionDeRevision(categorie) {
  return donnees.missions.find((m) => (m.revision_pour || []).includes(categorie)) || null;
}

/** Erreurs revenues souvent, avec la mission ciblée proposée (si elle n'a pas déjà été faite depuis). */
export function revisionsRecommandees(etat) {
  const resultat = [];
  for (const frequente of categoriesFrequentes(etat)) {
    if (frequente.nombre < SEUIL_ERREUR_RECURRENTE) continue;
    const mission = missionDeRevision(frequente.categorie);
    const suivi = mission ? etat.missions[mission.id] : null;
    const dejaRevisee = suivi?.derniereReussite && suivi.derniereReussite > frequente.derniere;
    if (!dejaRevisee) resultat.push({ ...frequente, mission, nomConcept: nomConcept(frequente.concept) });
  }
  return resultat;
}

export function nombreOccurrences(etat, categorie) {
  return etat.erreurs.slice(0, 60).filter((e) => e.categorie === categorie).length;
}

/** La mission conseillée sur le tableau de bord, avec la raison. */
export function missionRecommandee(etat) {
  const revision = revisionsRecommandees(etat).find((r) => r.mission);
  if (revision) {
    return {
      mission: revision.mission,
      raison: `Tu as rencontré ${revision.nombre} fois l'erreur « ${revision.nom} ». Cette mission courte cible précisément cette notion.`,
      type: "revision",
    };
  }
  const derniere = etat.derniereMission && trouverMission(etat, etat.derniereMission);
  if (derniere && !etat.missions[derniere.id]?.accomplie) {
    return { mission: derniere, raison: "Reprends là où tu t'es arrêté.", type: "reprise" };
  }
  const prochaine = donnees.missions.find((m) => !etat.missions[m.id]?.accomplie && estDebloquee(etat, m));
  if (prochaine) {
    return { mission: prochaine, raison: "Prochaine étape de ta formation d'agent.", type: "parcours" };
  }
  const generee = toutesLesMissions(etat).find((m) => !etat.missions[m.id]?.accomplie);
  if (generee) return { mission: generee, raison: "Une de tes missions générées t'attend.", type: "generee" };
  return null;
}

/** Progression par thème : [{theme, total, accomplies}] */
export function progressionThemes(etat) {
  const parTheme = new Map();
  for (const mission of donnees.missions) {
    const entree = parTheme.get(mission.theme) || { theme: mission.theme, total: 0, accomplies: 0 };
    entree.total += 1;
    if (etat.missions[mission.id]?.accomplie) entree.accomplies += 1;
    parTheme.set(mission.theme, entree);
  }
  return [...parTheme.values()];
}

export function statistiques(etat) {
  const accomplies = missionsAccomplies(etat);
  const tentatives = Object.values(etat.missions).reduce((t, s) => t + (s.tentativesTotales || 0), 0);
  const indices = Object.values(etat.missions).reduce((t, s) => t + (s.indicesTotaux || 0) + (s.enCours?.indicesUtilises || 0), 0);
  return {
    missionsAccomplies: accomplies.length,
    tentatives,
    indices,
    tauxReussite: tentatives ? accomplies.reduce((t, [, s]) => t + s.nbReussites, 0) / tentatives : 0,
    badges: Object.keys(etat.badges).length,
    serie: etat.serie,
    meilleureSerie: etat.meilleureSerie,
  };
}
