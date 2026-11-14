// Page 7 — Historique des erreurs : pour apprendre de ses erreurs passées.

import { el, vider, carte, puce, extraitCode, formaterDate, videEtat } from "../interface.js";
import { categoriesFrequentes, missionDeRevision, SEUIL_ERREUR_RECURRENTE } from "../progression.js";
import { CONCEPTS_GENERABLES, nomConcept } from "../donnees.js";
import { lienMission } from "../composants.js";
import { genererEtOuvrir } from "../generation.js";

export function afficher(vue, { etat }) {
  vue.append(el("header", { class: "entete-page" },
    el("p", { class: "surtitre", text: "JOURNAL DES INCIDENTS" }),
    el("h1", { text: "Historique des erreurs" }),
    el("p", { class: "texte-doux", text: "Chaque erreur est une information. Repère celles qui reviennent : ce sont tes meilleures pistes de progrès." })));

  if (!etat.erreurs.length) {
    vue.append(carte(null, videEtat("Aucune erreur enregistrée pour le moment. Elles apparaîtront ici dès ta première mission.")));
    return;
  }

  const frequentes = categoriesFrequentes(etat, 300);
  vue.append(carte("Erreurs par catégorie",
    el("div", { class: "liste-categories" }, frequentes.map((f) => {
      const mission = missionDeRevision(f.categorie);
      const recurrente = f.nombre >= SEUIL_ERREUR_RECURRENTE;
      return el("div", { class: `categorie-erreur${recurrente ? " recurrente" : ""}` },
        el("div", {},
          el("strong", { text: f.nom }),
          el("div", { class: "texte-doux petit", text: `${f.nombre} fois · dernière : ${formaterDate(f.derniere)} · notion : ${nomConcept(f.concept)}` })),
        el("div", { class: "actions" },
          mission ? el("a", { class: `bouton bouton-petit${recurrente ? " bouton-alerte" : ""}`, href: lienMission(mission), text: "Mission ciblée" })
            : CONCEPTS_GENERABLES.includes(f.concept)
              ? el("button", { class: "bouton bouton-petit", type: "button", text: "Mission de révision",
                on: { click: () => genererEtOuvrir({ concepts: [f.concept], difficulte: "facile", etiquette: "révision" }) } })
              : null,
          f.concept ? el("a", { class: "bouton bouton-petit bouton-discret", href: `#concept-${f.concept}`, text: "Fiche" }) : null));
    }))));

  let filtre = "toutes";
  const liste = el("div", { class: "journal" });
  const filtres = el("div", { class: "nuage-puces" });
  const rendre = () => {
    vider(filtres).append(...[["toutes", "Toutes"], ...frequentes.map((f) => [f.categorie, f.nom])].map(([id, nom]) =>
      el("button", { type: "button", class: `puce puce-bouton${filtre === id ? " active" : ""}`, text: nom,
        on: { click: () => { filtre = id; rendre(); } } })));
    vider(liste);
    const erreurs = etat.erreurs.filter((e) => filtre === "toutes" || e.categorie === filtre).slice(0, 100);
    for (const erreur of erreurs) {
      liste.append(el("details", { class: "entree-journal" },
        el("summary", {},
          el("span", { class: "mono texte-doux petit", text: formaterDate(erreur.date) }),
          puce(erreur.nomCategorie || erreur.categorie, "puce-alerte"),
          el("span", { text: erreur.titre }),
          el("span", { class: "texte-doux petit", text: ` — ${erreur.titreMission}` })),
        el("div", { class: "entree-journal-corps" },
          el("p", { text: erreur.description }),
          erreur.extrait?.length ? extraitCode(erreur.extrait) : null,
          el("p", { class: "texte-doux petit", text: `Source : ${erreur.source === "envoi" ? "envoi de la mission" : "exécution"}${erreur.type ? ` · ${erreur.type}` : ""}` }),
          el("a", { class: "bouton bouton-petit", href: `#mission-${erreur.missionId}`, text: "Ouvrir la mission" }))));
    }
  };
  rendre();
  vue.append(carte("Journal", filtres, liste));
}
