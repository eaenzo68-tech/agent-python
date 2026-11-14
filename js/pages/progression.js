// Page 5 — Progression : carte d'agent, grades, statistiques, concepts, badges, historique.

import { el, carte, barre, formaterDate, puce } from "../interface.js";
import { donnees, THEMES } from "../donnees.js";
import {
  GRADES, grade, statistiques, bilanConcepts, progressionThemes, LIBELLES_STATUT_CONCEPT,
} from "../progression.js";
import { carteAgent, insigne } from "../composants.js";

export function afficher(vue, { etat }) {
  const stats = statistiques(etat);
  const g = grade(etat.xp);

  vue.append(el("header", { class: "entete-page" },
    el("p", { class: "surtitre", text: "DOSSIER PERSONNEL" }),
    el("h1", { text: "Progression" })));

  vue.append(el("div", { class: "grille-deux" },
    carteAgent(etat),
    carte("Échelle des grades",
      el("ol", { class: "echelle-grades" }, GRADES.map((gr, i) => el("li", {
        class: i < g.index ? "passe" : i === g.index ? "actuel" : "",
      }, el("span", { class: "grade-numero", text: String(i + 1) }),
      el("span", { class: "grade-nom", text: gr.nom }),
      el("span", { class: "texte-doux mono petit", text: `${gr.xp} XP` })))),
      g.suivant ? el("div", {},
        el("p", { class: "texte-doux petit", text: `${g.suivant.xp - etat.xp} XP avant « ${g.suivant.nom} »` }),
        barre(g.progression)) : null)));

  vue.append(el("section", { class: "carte" },
    el("h2", { class: "carte-titre", text: "Tableau de progression" }),
    el("div", { class: "grille-stats grille-stats-large" },
      stat("Missions terminées", stats.missionsAccomplies),
      stat("Série actuelle", stats.serie),
      stat("Meilleure série", stats.meilleureSerie),
      stat("Envois au total", stats.tentatives),
      stat("Indices utilisés", stats.indices),
      stat("Réussite des envois", `${Math.round(stats.tauxReussite * 100)} %`),
      stat("Erreurs analysées", etat.erreurs.length),
      stat("Badges", `${stats.badges}/${donnees.badges.length}`))));

  const themes = progressionThemes(etat);
  const bilan = bilanConcepts(etat).filter((c) => c.reussites + c.echecs > 0);
  vue.append(el("div", { class: "grille-deux" },
    carte("Missions par thème",
      el("div", { class: "liste-themes" }, themes.map((th) => el("div", { class: "ligne-theme" },
        el("span", { text: THEMES[th.theme] || th.theme }), barre(th.accomplies / th.total),
        el("span", { class: "mono texte-doux", text: `${th.accomplies}/${th.total}` }))))),
    carte("Concepts",
      bilan.length ? el("div", { class: "liste-concepts" }, bilan.map((c) => el("a", { class: "ligne-concept", href: `#concept-${c.id}` },
        el("span", { text: c.nom }),
        el("span", { class: "texte-doux petit", text: `${c.reussites} ✓ · ${c.echecs} ✗` }),
        puce(LIBELLES_STATUT_CONCEPT[c.statut], `puce-statut-${c.statut}`))))
        : el("p", { class: "texte-doux", text: "Les concepts apparaîtront ici après tes premières missions." }))));

  vue.append(carte(`Badges (${stats.badges}/${donnees.badges.length})`,
    el("div", { class: "grille-insignes" }, donnees.badges.map((b) => {
      const element = insigne(b, Boolean(etat.badges[b.id]));
      if (etat.badges[b.id]) element.append(el("div", { class: "texte-doux petit", text: `Obtenu le ${formaterDate(etat.badges[b.id])}` }));
      return element;
    }))));

  vue.append(carte("Historique des missions",
    etat.historique.length ? el("div", { class: "tableau-defilant" }, el("table", { class: "tableau" },
      el("thead", {}, el("tr", {}, ["Date", "Mission", "Score", "XP", "Qualité", "Envois", "Indices"].map((t) => el("th", { text: t })))),
      el("tbody", {}, etat.historique.slice(0, 50).map((h) => el("tr", {},
        el("td", { class: "mono petit", text: formaterDate(h.date) }),
        el("td", {}, el("a", { href: `#mission-${h.missionId}`, text: h.titre })),
        el("td", { text: `${h.score}` }), el("td", { text: `+${h.xp}` }),
        el("td", { text: `${h.qualite}/100` }), el("td", { text: String(h.envois) }),
        el("td", { text: h.solution ? `${h.indices} + solution` : String(h.indices) }))))))
      : el("p", { class: "texte-doux", text: "Ton historique est vide pour l'instant." })));
}

function stat(libelle, valeur) {
  return el("div", { class: "stat" }, el("div", { class: "stat-valeur", text: String(valeur) }), el("div", { class: "stat-libelle", text: libelle }));
}
