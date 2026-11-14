// Page 4 — Centre d'entraînement : révisions, missions mixtes, catalogue filtrable.

import { el, vider, carte, toast, confirmer, videEtat } from "../interface.js";
import { THEMES, CONCEPTS_GENERABLES, toutesLesMissions, nomConcept } from "../donnees.js";
import { revisionsRecommandees, bilanConcepts, statutMission } from "../progression.js";
import { carteMission, lienMission, puceConcept } from "../composants.js";
import { genererEtOuvrir } from "../generation.js";
import { stockage } from "../stockage.js";

export function afficher(vue, { etat }) {
  vue.append(el("header", { class: "entete-page" },
    el("p", { class: "surtitre", text: "CENTRE D'ENTRAÎNEMENT" }),
    el("h1", { text: "Révisions et missions" }),
    el("p", { class: "texte-doux", text: "Revois tes erreurs, consolide les notions fragiles et recommence n'importe quelle mission." })));

  const bilan = bilanConcepts(etat);
  const maitrises = bilan.filter((c) => c.statut === "maitrise");
  const aRevoir = bilan.filter((c) => c.statut === "a_revoir");
  const revisions = revisionsRecommandees(etat);

  // Révisions intelligentes ---------------------------------------------------
  const blocRevisions = el("div", { class: "liste-revisions" });
  for (const r of revisions) {
    blocRevisions.append(el("div", { class: "revision" },
      el("div", {},
        el("strong", { text: r.nom }), el("span", { class: "texte-doux", text: ` · ${r.nombre} fois récemment` }),
        el("p", { class: "texte-doux petit", text: r.mission ? `Mission ciblée : ${r.mission.titre}` : `Notion : ${r.nomConcept}` })),
      r.mission
        ? el("a", { class: "bouton bouton-petit bouton-alerte", href: lienMission(r.mission), text: "Mission ciblée" })
        : CONCEPTS_GENERABLES.includes(r.concept)
          ? el("button", { class: "bouton bouton-petit bouton-alerte", type: "button", text: "Générer une révision",
            on: { click: () => genererEtOuvrir({ concepts: [r.concept], difficulte: "facile", etiquette: "révision" }) } })
          : el("a", { class: "bouton bouton-petit", href: `#concept-${r.concept}`, text: "Fiche" })));
  }
  for (const concept of aRevoir) {
    if (!CONCEPTS_GENERABLES.includes(concept.id)) continue;
    blocRevisions.append(el("div", { class: "revision" },
      el("div", {}, el("strong", { text: concept.nom }),
        el("p", { class: "texte-doux petit", text: `${concept.echecs} échec(s) pour ${concept.reussites} réussite(s)` })),
      el("button", { class: "bouton bouton-petit", type: "button", text: "Mission de révision",
        on: { click: () => genererEtOuvrir({ concepts: [concept.id], difficulte: "facile", etiquette: "révision" }) } })));
  }

  const conceptsMixte = new Set();
  const selecteurMixte = el("div", { class: "nuage-puces" }, CONCEPTS_GENERABLES.map((id) => {
    const bouton = el("button", { type: "button", class: "puce puce-bouton", text: nomConcept(id), "aria-pressed": "false",
      on: { click: () => {
        if (conceptsMixte.has(id)) conceptsMixte.delete(id); else conceptsMixte.add(id);
        bouton.classList.toggle("active", conceptsMixte.has(id));
        bouton.setAttribute("aria-pressed", String(conceptsMixte.has(id)));
      } } });
    return bouton;
  }));

  vue.append(el("div", { class: "grille-deux" },
    carte("Révisions recommandées",
      blocRevisions.childElementCount ? blocRevisions
        : el("p", { class: "texte-doux", text: "Aucune erreur récurrente pour l'instant. Les révisions apparaîtront ici automatiquement." }),
      el("div", { class: "actions" }, el("a", { class: "bouton bouton-discret", href: "#erreurs", text: "Revoir mes anciennes erreurs" }))),
    carte("Mission mixte",
      el("p", { class: "texte-doux", text: "Choisis au moins deux notions : le QG prépare une mission qui les combine." }),
      selecteurMixte,
      el("div", { class: "actions" },
        el("button", { class: "bouton bouton-principal", type: "button", text: "Lancer une mission mixte",
          on: { click: () => {
            const choix = conceptsMixte.size >= 2 ? [...conceptsMixte] : melanger(CONCEPTS_GENERABLES).slice(0, 2);
            if (conceptsMixte.size < 2) toast(`Notions tirées au hasard : ${choix.map(nomConcept).join(" + ")}`);
            genererEtOuvrir({ concepts: choix, difficulte: "intermediaire", mixte: true, etiquette: "mixte" });
          } } }),
        el("button", { class: "bouton", type: "button", text: "Révision surprise",
          on: { click: () => {
            const fragiles = aRevoir.map((c) => c.id).filter((id) => CONCEPTS_GENERABLES.includes(id));
            const source = fragiles.length ? fragiles : CONCEPTS_GENERABLES;
            genererEtOuvrir({ concepts: [source[Math.floor(Math.random() * source.length)]], difficulte: "facile", etiquette: "révision" });
          } } })))));

  vue.append(el("div", { class: "grille-deux" },
    carte(`Notions maîtrisées (${maitrises.length})`,
      maitrises.length ? el("div", { class: "nuage-puces" }, maitrises.map((c) => puceConcept(c.id)))
        : el("p", { class: "texte-doux", text: "Une notion est maîtrisée après au moins 2 missions réussies sans trop d'échecs." })),
    carte(`Notions à travailler (${aRevoir.length})`,
      aRevoir.length ? el("div", { class: "nuage-puces" }, aRevoir.map((c) => puceConcept(c.id)))
        : el("p", { class: "texte-doux", text: "Aucune notion en difficulté. Bravo !" }),
      el("p", { class: "texte-doux petit" }, el("a", { href: "#concepts", text: "Toutes les fiches récapitulatives →" })))));

  // Catalogue ----------------------------------------------------------------
  let filtreTheme = "tous";
  let filtreStatut = "tous";
  const filtres = el("div", { class: "filtres" });
  const grille = el("div", { class: "grille-missions" });

  const rendre = () => {
    const etatActuel = stockage.etat;
    vider(filtres).append(
      el("div", { class: "nuage-puces" }, [["tous", "Tous les thèmes"], ...Object.entries(THEMES), ["generees", "Générées"], ["perso", "Mes missions"]]
        .map(([id, nom]) => el("button", { type: "button", class: `puce puce-bouton${filtreTheme === id ? " active" : ""}`, text: nom,
          on: { click: () => { filtreTheme = id; rendre(); } } }))),
      el("div", { class: "nuage-puces" }, [["tous", "Tous"], ["disponible", "Disponibles"], ["en_cours", "En cours"], ["accomplie", "Accomplies"], ["classifie", "Classifiées"]]
        .map(([id, nom]) => el("button", { type: "button", class: `puce puce-bouton${filtreStatut === id ? " active" : ""}`, text: nom,
          on: { click: () => { filtreStatut = id; rendre(); } } }))));

    const missions = toutesLesMissions(etatActuel).filter((m) => {
      if (filtreTheme === "generees" && m.origine !== "generee") return false;
      if (filtreTheme === "perso" && m.origine !== "perso") return false;
      if (!["tous", "generees", "perso"].includes(filtreTheme) && m.theme !== filtreTheme) return false;
      return filtreStatut === "tous" || statutMission(etatActuel, m) === filtreStatut;
    });
    vider(grille);
    if (!missions.length) grille.append(videEtat("Aucune mission ne correspond à ces filtres."));
    for (const mission of missions) {
      const carteM = carteMission(mission, etatActuel, { compacte: true });
      if (mission.origine === "generee" || mission.origine === "perso") {
        carteM.querySelector(".carte-mission-bas").append(el("button", {
          class: "bouton-texte texte-rouge", type: "button", text: "Supprimer",
          on: { click: async () => {
            const ok = await confirmer({ titre: "Supprimer cette mission ?", message: `« ${mission.titre} » sera retirée de la liste (ta progression est conservée).`, ok: "Supprimer", danger: true });
            if (!ok) return;
            delete etatActuel.missionsGenerees[mission.id];
            delete etatActuel.missionsPerso[mission.id];
            delete etatActuel.brouillons[mission.id];
            stockage.sauver();
            rendre();
          } } }));
      }
      grille.append(carteM);
    }
  };
  rendre();

  vue.append(carte("Catalogue des missions", filtres, grille));
  return null;
}

function melanger(liste) {
  const copie = [...liste];
  for (let i = copie.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copie[i], copie[j]] = [copie[j], copie[i]];
  }
  return copie;
}

