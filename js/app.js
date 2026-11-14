// Point d'entrée de l'interface : chargement, navigation entre les pages, barre du haut.

import { el, vider, icone, modale, toast } from "./interface.js";
import { chargerDonnees } from "./donnees.js";
import { stockage } from "./stockage.js";
import { moteur } from "./moteur_python.js";
import { telephone } from "./telephone.js";
import { grade, niveau } from "./progression.js";
import * as tableau from "./pages/tableau_de_bord.js";
import * as nouvelle from "./pages/nouvelle_mission.js";
import * as mission from "./pages/mission.js";
import * as entrainement from "./pages/entrainement.js";
import * as progression from "./pages/progression.js";
import * as concepts from "./pages/concepts.js";
import * as erreurs from "./pages/erreurs.js";
import * as parametres from "./pages/parametres.js";

const PAGES = [
  { route: "tableau-de-bord", nom: "Tableau de bord", icone: "tableau", afficher: tableau.afficher },
  { route: "nouvelle-mission", nom: "Nouvelle mission", icone: "nouvelle", afficher: nouvelle.afficher },
  { route: "mission-en-cours", nom: "Mission en cours", icone: "mission", afficher: mission.afficherMissionEnCours },
  { route: "entrainement", nom: "Centre d'entraînement", icone: "entrainement", afficher: entrainement.afficher },
  { route: "progression", nom: "Progression", icone: "progression", afficher: progression.afficher },
  { route: "concepts", nom: "Concepts", icone: "concepts", afficher: concepts.afficher },
  { route: "erreurs", nom: "Historique des erreurs", icone: "erreurs", afficher: erreurs.afficher },
  { route: "parametres", nom: "Paramètres", icone: "parametres", afficher: parametres.afficher },
];

const vue = document.getElementById("vue");
let nettoyerPage = null;

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

function construireNavigation() {
  const nav = document.getElementById("nav");
  vider(nav).append(
    el("a", { class: "marque", href: "#tableau-de-bord", "aria-label": "Agent Python, accueil" },
      el("span", { class: "marque-logo", "aria-hidden": "true", text: "▲" }),
      el("span", { class: "marque-texte" }, el("strong", { text: "AGENCE PY" }), el("small", { text: "Centre de formation" }))),
    el("ul", { class: "nav-liens" }, PAGES.map((page) => el("li", {},
      el("a", { href: `#${page.route}`, class: "nav-lien", "data-route": page.route, title: page.nom },
        icone(page.icone, 20), el("span", { class: "nav-texte", text: page.nom }))))),
    el("div", { class: "nav-pied mono", text: "LIGNE SÉCURISÉE · HORS LIGNE" }));
}

function routeActuelle() {
  const hash = decodeURIComponent(location.hash.slice(1)) || "tableau-de-bord";
  if (hash.startsWith("mission-") && hash !== "mission-en-cours") {
    return { route: "mission-en-cours", afficher: mission.afficher, params: { idMission: hash.slice("mission-".length) } };
  }
  if (hash.startsWith("concept-")) {
    return { route: "concepts", afficher: concepts.afficherFiche, params: { idConcept: hash.slice("concept-".length) } };
  }
  const page = PAGES.find((p) => p.route === hash) || PAGES[0];
  return { route: page.route, afficher: page.afficher, params: {} };
}

function afficherPage() {
  if (typeof nettoyerPage === "function") nettoyerPage();
  nettoyerPage = null;
  const { route, afficher, params } = routeActuelle();
  for (const lien of document.querySelectorAll(".nav-lien")) {
    lien.classList.toggle("actif", lien.dataset.route === route);
    if (lien.dataset.route === route) lien.setAttribute("aria-current", "page"); else lien.removeAttribute("aria-current");
  }
  vider(vue);
  vue.classList.remove("apparition");
  void vue.offsetWidth;
  vue.classList.add("apparition");
  try {
    nettoyerPage = afficher(vue, { etat: stockage.etat, ...params, rafraichir: afficherPage });
  } catch (erreur) {
    console.error(erreur);
    vue.append(el("section", { class: "carte" }, el("h2", { text: "Erreur d'affichage" }), el("p", { text: String(erreur.message || erreur) })));
  }
  window.scrollTo(0, 0);
  vue.focus({ preventScroll: true });
}

// ---------------------------------------------------------------------------
// Barre du haut : agent + état du moteur Python
// ---------------------------------------------------------------------------

function majBarreHaut() {
  const etat = stockage.etat;
  const g = grade(etat.xp);
  const n = niveau(etat.xp);
  const zone = document.getElementById("barre-agent");
  vider(zone).append(
    el("span", { class: "barre-agent-grade", text: g.nom }),
    el("span", { class: "barre-agent-nom", text: etat.agent.nom || "Recrue" }),
    el("span", { class: "barre-agent-xp mono", text: `Niv. ${n.niveau} · ${etat.xp} XP` }),
    el("span", { class: "mini-barre", "aria-hidden": "true" }, el("span", { style: { width: `${Math.round(n.progression * 100)}%` } })));
}

function majMoteur(m) {
  const zone = document.getElementById("etat-moteur");
  if (!zone) return;
  zone.className = `etat-moteur etat-${m.etat}`;
  zone.title = m.message;
  vider(zone).append(el("span", { class: "voyant", "aria-hidden": "true" }),
    el("span", { class: "etat-moteur-texte", text: m.etat === "pret" ? m.message : m.etat === "erreur" ? "Python indisponible" : "Chargement de Python…" }));
  if (m.etat === "erreur") toast(m.message, { type: "alerte", titre: "Moteur Python", duree: 9000 });
}

// ---------------------------------------------------------------------------
// Premier lancement
// ---------------------------------------------------------------------------

async function accueillirNouvelAgent() {
  if (stockage.etat.agent.nom) return;
  const champ = el("input", { type: "text", class: "champ", maxlength: "30", placeholder: "ex. : Faucon", "aria-label": "Nom de code" });
  const nom = await modale({
    titre: "Identification de l'agent",
    contenu: el("div", {},
      el("p", { text: "Bienvenue à l'Agence. Avant ta première mission, choisis ton nom de code." }),
      champ,
      el("p", { class: "texte-doux petit", text: "Tout reste sur cet appareil : aucun compte, aucune connexion." })),
    actions: [{ texte: "Plus tard", valeur: null, classe: "bouton-discret" }, { texte: "Valider", valeur: () => champ.value.trim(), classe: "bouton-principal" }],
  });
  stockage.etat.agent.nom = nom || "Recrue";
  stockage.sauver();
  afficherPage();
}

// ---------------------------------------------------------------------------
// Démarrage
// ---------------------------------------------------------------------------

async function demarrer() {
  stockage.charger();
  document.body.classList.toggle("sans-animations", !stockage.etat.reglages.animations);
  construireNavigation();
  telephone.monter(document.getElementById("telephone"));
  stockage.ecouter(majBarreHaut);
  majBarreHaut();
  moteur.ecouter(majMoteur);
  moteur.demarrer();

  try {
    await chargerDonnees();
  } catch (erreur) {
    vider(vue).append(el("section", { class: "carte" },
      el("h2", { text: "Impossible de charger les données" }),
      el("p", { text: erreur.message }),
      el("p", { class: "texte-doux", text: "Lance l'application avec serveur.py (ou lancer_windows.bat) : ouvrir index.html directement ne fonctionne pas." })));
    return;
  }

  window.addEventListener("hashchange", afficherPage);
  afficherPage();
  accueillirNouvelAgent();
  enregistrerServiceWorker();
}

/** Mode hors ligne : met l'application et Python en cache (https ou localhost uniquement). */
function enregistrerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  const local = ["localhost", "127.0.0.1"].includes(location.hostname);
  if (location.protocol !== "https:" && !local) return;
  navigator.serviceWorker.register("service-worker.js").catch((erreur) => {
    console.info("Mode hors ligne indisponible ici :", erreur.message);
  });
}

demarrer();
