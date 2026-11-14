// Génération de missions via le moteur Python, partagée par plusieurs pages.

import { moteur } from "./moteur_python.js";
import { stockage } from "./stockage.js";
import { toast } from "./interface.js";

/**
 * Demande au moteur de fabriquer des missions et les enregistre.
 * options : { concepts, nombre, difficulte, niveaux, mixte }
 * Renvoie la liste des missions créées.
 */
export async function genererMissions(options) {
  const reponse = await moteur.appeler("generer", {
    concepts: options.concepts || [],
    nombre: options.nombre || 1,
    difficulte: options.difficulte || "facile",
    niveaux: options.niveaux || {},
    mixte: Boolean(options.mixte),
    graine: Math.floor(Math.random() * 1e9),
  }, 30);
  const etat = stockage.etat;
  for (const mission of reponse.missions) {
    mission.creeLe = new Date().toISOString();
    if (options.etiquette) mission.etiquette = options.etiquette;
    etat.missionsGenerees[mission.id] = mission;
  }
  stockage.sauver();
  return reponse.missions;
}

/** Génère une seule mission et l'ouvre directement. */
export async function genererEtOuvrir(options) {
  try {
    const [mission] = await genererMissions({ ...options, nombre: 1 });
    if (mission) location.hash = `#mission-${mission.id}`;
  } catch (erreur) {
    toast(`Génération impossible : ${erreur.message}`, { type: "alerte" });
  }
}
