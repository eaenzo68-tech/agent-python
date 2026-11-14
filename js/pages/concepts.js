// Page 6 — Bibliothèque des concepts : fiches récapitulatives.

import { el, carte, blocCode, puce, videEtat } from "../interface.js";
import { donnees, toutesLesMissions } from "../donnees.js";
import { statutConcept, LIBELLES_STATUT_CONCEPT } from "../progression.js";
import { carteMission } from "../composants.js";
import { genererEtOuvrir } from "../generation.js";
import { CONCEPTS_GENERABLES } from "../donnees.js";

export function afficher(vue, { etat }) {
  vue.append(el("header", { class: "entete-page" },
    el("p", { class: "surtitre", text: "ARCHIVES DE L'AGENCE" }),
    el("h1", { text: "Bibliothèque des concepts" }),
    el("p", { class: "texte-doux", text: "Une fiche récapitulative par notion : l'essentiel, la syntaxe, un exemple et les pièges à éviter." })));

  const categories = new Map();
  for (const concept of donnees.concepts) {
    if (!categories.has(concept.categorie)) categories.set(concept.categorie, []);
    categories.get(concept.categorie).push(concept);
  }
  for (const [categorie, concepts] of categories) {
    vue.append(el("h2", { class: "titre-section", text: categorie }),
      el("div", { class: "grille-fiches" }, concepts.map((c) => {
        const statut = statutConcept(etat.concepts[c.id]);
        return el("a", { class: "fiche-carte", href: `#concept-${c.id}` },
          el("div", { class: "ligne-entre" }, el("strong", { text: c.nom }), puce(LIBELLES_STATUT_CONCEPT[statut], `puce-statut-${statut}`)),
          el("p", { class: "texte-doux petit", text: c.resume }));
      })));
  }
}

export function afficherFiche(vue, { etat, idConcept }) {
  const concept = donnees.conceptsParId.get(idConcept);
  if (!concept) {
    vue.append(carte("Fiche introuvable", videEtat("Ce concept n'existe pas.", el("a", { class: "bouton", href: "#concepts", text: "Retour" }))));
    return;
  }
  const stat = etat.concepts[concept.id] || { reussites: 0, echecs: 0 };
  const statut = statutConcept(stat);
  const missions = toutesLesMissions(etat).filter((m) => (m.concepts || []).includes(concept.id));

  vue.append(el("header", { class: "entete-page" },
    el("div", { class: "fil-ariane" }, el("a", { href: "#concepts", text: "Bibliothèque" }), el("span", { text: ` / ${concept.categorie}` })),
    el("h1", { text: concept.nom }),
    el("div", { class: "nuage-puces" }, puce(LIBELLES_STATUT_CONCEPT[statut], `puce-statut-${statut}`),
      puce(`${stat.reussites} réussite(s)`), puce(`${stat.echecs} échec(s)`))));

  vue.append(el("div", { class: "grille-deux" },
    el("div", { class: "colonne" },
      carte("L'essentiel", el("p", { text: concept.resume })),
      carte("Syntaxe", blocCode(concept.syntaxe)),
      carte("Exemple", blocCode(concept.exemple))),
    el("div", { class: "colonne" },
      carte("Pièges fréquents", el("ul", { class: "liste-pieges" }, concept.pieges.map((p) => el("li", { text: p })))),
      carte("Conseil de code propre", el("p", { text: concept.conseil })),
      CONCEPTS_GENERABLES.includes(concept.id) ? carte("S'entraîner",
        el("p", { class: "texte-doux", text: "Le QG peut générer une mission inédite sur cette notion." }),
        el("div", { class: "actions" },
          el("button", { class: "bouton bouton-principal", type: "button", text: "Mission facile",
            on: { click: () => genererEtOuvrir({ concepts: [concept.id], difficulte: "facile" }) } }),
          el("button", { class: "bouton", type: "button", text: "Mission difficile",
            on: { click: () => genererEtOuvrir({ concepts: [concept.id], difficulte: "difficile" }) } })))
        : carte("S'entraîner", el("p", { class: "texte-doux", text: "Pas encore de modèle de mission pour cette notion : crée ta propre mission depuis « Nouvelle mission »." })))));

  if (missions.length) {
    vue.append(el("h2", { class: "titre-section", text: "Missions liées" }),
      el("div", { class: "grille-missions" }, missions.slice(0, 12).map((m) => carteMission(m, etat, { compacte: true }))));
  }
}
