// Petits outils d'affichage partagés par toutes les pages.
// Règle de sécurité : on crée les éléments avec el() et du TEXTE ;
// on n'injecte jamais de HTML venant de l'utilisateur.

import { colorer } from "./coloration.js";

/** Crée un élément HTML. el("p", { class: "x", on: { click: f } }, "texte", autreElement) */
export function el(balise, attributs = {}, ...enfants) {
  const noeud = document.createElement(balise);
  for (const [cle, valeur] of Object.entries(attributs || {})) {
    if (valeur === undefined || valeur === null || valeur === false) continue;
    if (cle === "class") noeud.className = valeur;
    else if (cle === "text") noeud.textContent = valeur;
    else if (cle === "html") noeud.innerHTML = valeur; // uniquement pour du HTML écrit par nous
    else if (cle === "on") for (const [evt, fn] of Object.entries(valeur)) noeud.addEventListener(evt, fn);
    else if (cle === "style" && typeof valeur === "object") Object.assign(noeud.style, valeur);
    else if (valeur === true) noeud.setAttribute(cle, "");
    else noeud.setAttribute(cle, valeur);
  }
  ajouter(noeud, enfants);
  return noeud;
}

function ajouter(parent, enfants) {
  for (const enfant of enfants.flat(Infinity)) {
    if (enfant === null || enfant === undefined || enfant === false) continue;
    parent.append(enfant instanceof Node ? enfant : document.createTextNode(String(enfant)));
  }
}

export function vider(noeud) {
  while (noeud.firstChild) noeud.firstChild.remove();
  return noeud;
}

export function echapper(texte) {
  return String(texte ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

/** Texte avec mise en forme légère : noms de fonctions et valeurs Python en police code. */
export function texteRiche(texte) {
  const html = echapper(texte)
    .replace(/\b([A-Za-z_][A-Za-z0-9_]*\([^()]{0,60}\))/g, "<code>$1</code>")
    .replace(/\b(True|False|None)\b/g, "<code>$1</code>")
    .replace(/\n/g, "<br>");
  return el("span", { html });
}

/** Bloc de code coloré, avec numéros de ligne facultatifs. */
export function blocCode(code, { numeros = false, ligneErreur = null, classe = "" } = {}) {
  const pre = el("pre", { class: `bloc-code ${classe}` });
  if (numeros) {
    const lignes = String(code).replace(/\n$/, "").split("\n");
    lignes.forEach((ligne, i) => {
      const numero = typeof numeros === "number" ? numeros + i : i + 1;
      pre.append(el("span", { class: `ligne-code${numero === ligneErreur ? " ligne-erreur" : ""}` },
        el("span", { class: "num-ligne", text: String(numero) }),
        el("span", { html: colorer(ligne) || " " })));
    });
  } else {
    pre.append(el("code", { html: colorer(String(code).replace(/\n$/, "")) }));
  }
  return pre;
}

/** Extrait de code venant du moteur : [{numero, texte, erreur}] */
export function extraitCode(lignes) {
  const pre = el("pre", { class: "bloc-code extrait" });
  for (const ligne of lignes || []) {
    pre.append(el("span", { class: `ligne-code${ligne.erreur ? " ligne-erreur" : ""}` },
      el("span", { class: "num-ligne", text: String(ligne.numero) }),
      el("span", { html: colorer(ligne.texte) || " " })));
  }
  return pre;
}

/** Texte d'indice : première ligne en paragraphe, le reste (s'il y a du code) en bloc de code. */
export function formaterIndice(texte) {
  const conteneur = el("div", { class: "indice-texte" });
  const morceaux = String(texte).split("\n");
  if (morceaux.length === 1) {
    conteneur.append(el("p", {}, texteRiche(texte)));
  } else {
    conteneur.append(el("p", {}, texteRiche(morceaux[0])));
    conteneur.append(blocCode(morceaux.slice(1).join("\n")));
  }
  return conteneur;
}

// ---------------------------------------------------------------------------
// Statuts, puces, barres
// ---------------------------------------------------------------------------

const STATUTS = {
  classifie: ["CLASSIFIÉ", "tampon-rouge"],
  disponible: ["DISPONIBLE", "tampon-cyan"],
  en_cours: ["EN COURS", "tampon-orange"],
  accomplie: ["MISSION ACCOMPLIE", "tampon-vert"],
};

export function tampon(statut, { grand = false } = {}) {
  const [texte, classe] = STATUTS[statut] || STATUTS.disponible;
  return el("span", { class: `tampon ${classe}${grand ? " tampon-grand" : ""}`, text: texte });
}

export function puce(texte, classe = "") {
  return el("span", { class: `puce ${classe}`, text: texte });
}

export function barre(valeur, { classe = "", libelle = "" } = {}) {
  const pourcentage = Math.round(Math.max(0, Math.min(1, valeur || 0)) * 100);
  return el("div", { class: `barre ${classe}`, role: "progressbar", "aria-valuenow": pourcentage,
    "aria-valuemin": 0, "aria-valuemax": 100, "aria-label": libelle || `${pourcentage} %` },
  el("div", { class: "barre-remplie", style: { width: `${pourcentage}%` } }));
}

export function carte(titre, ...contenu) {
  return el("section", { class: "carte" },
    titre ? el("h2", { class: "carte-titre", text: titre }) : null, ...contenu);
}

export function videEtat(message, ...actions) {
  return el("div", { class: "vide" }, el("p", { text: message }), ...actions);
}

// ---------------------------------------------------------------------------
// Dates
// ---------------------------------------------------------------------------

const FORMAT_DATE = new Intl.DateTimeFormat("fr-CH", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });

export function formaterDate(iso) {
  if (!iso) return "";
  try { return FORMAT_DATE.format(new Date(iso)); } catch { return iso; }
}

export function formaterRelatif(iso) {
  if (!iso) return "";
  const secondes = (Date.now() - new Date(iso).getTime()) / 1000;
  if (secondes < 60) return "à l'instant";
  if (secondes < 3600) return `il y a ${Math.floor(secondes / 60)} min`;
  if (secondes < 86400) return `il y a ${Math.floor(secondes / 3600)} h`;
  const jours = Math.floor(secondes / 86400);
  return jours === 1 ? "hier" : `il y a ${jours} jours`;
}

// ---------------------------------------------------------------------------
// Notifications et fenêtres (sans alert() ni confirm() : ils bloquent l'iPad)
// ---------------------------------------------------------------------------

export function toast(message, { type = "info", duree = 4200, titre = "" } = {}) {
  const zone = document.getElementById("toasts");
  if (!zone) return;
  const notification = el("div", { class: `toast toast-${type}`, role: "status" },
    titre ? el("strong", { text: titre }) : null, el("span", { text: message }));
  zone.append(notification);
  setTimeout(() => notification.classList.add("toast-sortie"), duree);
  setTimeout(() => notification.remove(), duree + 400);
}

/**
 * Fenêtre modale. actions = [{ texte, valeur, classe }]. Renvoie une promesse avec la valeur choisie.
 */
export function modale({ titre, contenu, actions = [{ texte: "Fermer", valeur: null }], classe = "" }) {
  return new Promise((resoudre) => {
    const zone = document.getElementById("modales");
    const precedent = document.activeElement;
    const fermer = (valeur) => {
      fond.remove();
      document.removeEventListener("keydown", clavier);
      if (precedent && precedent.focus) precedent.focus();
      resoudre(valeur);
    };
    const clavier = (evt) => { if (evt.key === "Escape") fermer(null); };
    const boutons = actions.map((action) => el("button", {
      class: `bouton ${action.classe || ""}`, type: "button", text: action.texte,
      on: { click: () => fermer(typeof action.valeur === "function" ? action.valeur() : action.valeur) },
    }));
    const boite = el("div", { class: `modale ${classe}`, role: "dialog", "aria-modal": "true", "aria-label": titre },
      el("h2", { class: "modale-titre", text: titre }),
      el("div", { class: "modale-contenu" }, contenu),
      el("div", { class: "modale-actions" }, boutons));
    const fond = el("div", { class: "modale-fond", on: { click: (evt) => { if (evt.target === fond) fermer(null); } } }, boite);
    zone.append(fond);
    document.addEventListener("keydown", clavier);
    (boite.querySelector("input, textarea") || boutons[boutons.length - 1])?.focus();
  });
}

export function confirmer({ titre, message, ok = "Confirmer", annuler = "Annuler", danger = false }) {
  return modale({
    titre,
    contenu: typeof message === "string" ? el("p", { text: message }) : message,
    actions: [
      { texte: annuler, valeur: false, classe: "bouton-discret" },
      { texte: ok, valeur: true, classe: danger ? "bouton-danger" : "bouton-principal" },
    ],
  }).then(Boolean);
}

/** Télécharge un texte comme fichier (fonctionne sur Windows et sur iPad : le fichier va dans « Fichiers »). */
export function telecharger(nomFichier, contenu, type = "application/json") {
  const blob = new Blob([contenu], { type });
  const url = URL.createObjectURL(blob);
  const lien = el("a", { href: url, download: nomFichier, style: { display: "none" } });
  document.body.append(lien);
  lien.click();
  setTimeout(() => { URL.revokeObjectURL(url); lien.remove(); }, 1000);
}

export async function copierTexte(texte) {
  try {
    await navigator.clipboard.writeText(texte);
    return true;
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Icônes (SVG en ligne, aucun fichier externe)
// ---------------------------------------------------------------------------

const CHEMINS = {
  tableau: "M3 3h8v8H3zM13 3h8v5h-8zM13 10h8v11h-8zM3 13h8v8H3z",
  nouvelle: "M12 5v14M5 12h14",
  mission: "M4 4h12l4 4v12H4zM8 12h8M8 16h5",
  entrainement: "M12 2l3 7h7l-5.5 4.5L18 21l-6-4-6 4 1.5-7.5L2 9h7z",
  progression: "M4 20V10M10 20V4M16 20v-7M22 20H2",
  concepts: "M4 4h7v16H4zM13 4h7v16h-7zM6 8h3M15 8h3",
  erreurs: "M12 3l10 18H2zM12 10v5M12 18v.5",
  parametres: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1",
  executer: "M7 4l12 8-12 8z",
  envoyer: "M4 12l16-8-6 16-3-7z",
  telephone: "M8 2h8a2 2 0 0 1 2 2v16a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zM11 18h2",
  reinitialiser: "M4 4v6h6M20 12a8 8 0 1 1-2.3-5.7L20 9",
  verrou: "M6 11h12v10H6zM8 11V7a4 4 0 0 1 8 0v4",
  fermer: "M6 6l12 12M18 6L6 18",
};

export function icone(nom, taille = 18) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("viewBox", "0 0 24 24");
  svg.setAttribute("width", taille);
  svg.setAttribute("height", taille);
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("class", "icone");
  const chemin = document.createElementNS(ns, "path");
  chemin.setAttribute("d", CHEMINS[nom] || CHEMINS.mission);
  svg.append(chemin);
  return svg;
}
