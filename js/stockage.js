// Sauvegarde locale de la progression (localStorage du navigateur).
//
// Pourquoi pas SQLite ? SQLite demande un serveur Python, impossible à faire
// tourner sur iPad. Le localStorage est intégré à tous les navigateurs
// (Windows et iPad), fonctionne hors ligne et ne quitte jamais l'appareil.
// Pour ne rien perdre, Paramètres > « Exporter ma progression » crée une copie
// de sauvegarde dans un fichier JSON, réimportable à tout moment (et sur un
// autre appareil).

const CLE = "agent-python:etat:v1";
const MAX_HISTORIQUE = 300;
const MAX_ERREURS = 300;

function nouveauMatricule() {
  return `AG-${String(Math.floor(1000 + Math.random() * 9000))}`;
}

export function etatInitial() {
  return {
    version: 1,
    agent: { nom: "", matricule: nouveauMatricule(), creeLe: new Date().toISOString() },
    xp: 0,
    serie: 0,
    meilleureSerie: 0,
    stats: { envois: 0, executions: 0, sansIndice: 0, perseverance: 0 },
    missions: {},          // id -> suivi de la mission
    concepts: {},          // id concept -> { reussites, echecs }
    historique: [],        // missions réussies, la plus récente en premier
    erreurs: [],           // erreurs rencontrées, la plus récente en premier
    badges: {},            // id badge -> date d'obtention
    missionsGenerees: {},  // missions créées par le générateur
    missionsPerso: {},     // missions créées à la main
    brouillons: {},        // id mission -> code en cours d'écriture
    derniereMission: null,
    formulaireGeneration: null,
    reglages: {
      delai: 3,
      tailleEditeur: 15,
      coloration: true,
      modeLibre: false,
      animations: true,
      barreSymboles: "auto",
    },
  };
}

/** Complète un état ancien avec les champs ajoutés depuis (compatibilité). */
function completer(etat) {
  const base = etatInitial();
  const resultat = { ...base, ...etat };
  resultat.agent = { ...base.agent, ...(etat.agent || {}) };
  resultat.stats = { ...base.stats, ...(etat.stats || {}) };
  resultat.reglages = { ...base.reglages, ...(etat.reglages || {}) };
  for (const cle of ["missions", "concepts", "badges", "missionsGenerees", "missionsPerso", "brouillons"]) {
    if (typeof resultat[cle] !== "object" || resultat[cle] === null || Array.isArray(resultat[cle])) resultat[cle] = {};
  }
  for (const cle of ["historique", "erreurs"]) {
    if (!Array.isArray(resultat[cle])) resultat[cle] = [];
  }
  return resultat;
}

class Stockage {
  constructor() {
    this.etat = etatInitial();
    this.persistant = true;
    this.ecouteurs = new Set();
  }

  charger() {
    try {
      const brut = window.localStorage.getItem(CLE);
      this.etat = brut ? completer(JSON.parse(brut)) : etatInitial();
      window.localStorage.setItem(CLE, JSON.stringify(this.etat));
      this.persistant = true;
    } catch (erreur) {
      console.warn("Stockage local indisponible : la progression ne sera pas conservée.", erreur);
      this.persistant = false;
    }
    // Demande au navigateur de ne pas effacer les données (ignoré si non pris en charge).
    try { navigator.storage?.persist?.(); } catch { /* sans importance */ }
    return this.etat;
  }

  sauver() {
    this.etat.historique = this.etat.historique.slice(0, MAX_HISTORIQUE);
    this.etat.erreurs = this.etat.erreurs.slice(0, MAX_ERREURS);
    try {
      window.localStorage.setItem(CLE, JSON.stringify(this.etat));
    } catch (erreur) {
      console.warn("Sauvegarde impossible", erreur);
      this.persistant = false;
    }
    for (const ecouteur of this.ecouteurs) ecouteur(this.etat);
  }

  ecouter(fonction) {
    this.ecouteurs.add(fonction);
    return () => this.ecouteurs.delete(fonction);
  }

  exporter() {
    return JSON.stringify({ application: "agent-python", exporteLe: new Date().toISOString(), etat: this.etat }, null, 1);
  }

  importer(texte) {
    const donnees = JSON.parse(texte);
    const etat = donnees && donnees.application === "agent-python" ? donnees.etat : donnees;
    if (!etat || typeof etat !== "object" || !("missions" in etat) || !("xp" in etat)) {
      throw new Error("Ce fichier ne ressemble pas à une sauvegarde de l'application.");
    }
    this.etat = completer(etat);
    this.sauver();
  }

  reinitialiser() {
    const reglages = this.etat.reglages;
    this.etat = etatInitial();
    this.etat.reglages = reglages;
    this.sauver();
  }
}

export const stockage = new Stockage();
