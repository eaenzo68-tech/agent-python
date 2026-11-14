// Page 1 — Tableau de bord : vue d'ensemble de l'agent.

import { el, carte, barre, puce, formaterRelatif, videEtat } from "../interface.js";
import { donnees, THEMES } from "../donnees.js";
import {
  missionRecommandee, progressionThemes, conceptsRecents, bilanConcepts,
  revisionsRecommandees, statistiques, statutMission,
} from "../progression.js";
import { carteAgent, carteMission, lienMission, puceConcept } from "../composants.js";

export function afficher(vue, { etat }) {
  const stats = statistiques(etat);
  const recommandation = missionRecommandee(etat);
  const revisions = revisionsRecommandees(etat);
  const demo = donnees.missions.find((m) => m.demo);

  vue.append(
    el("header", { class: "entete-page" },
      el("p", { class: "surtitre", text: "CENTRE DE COMMANDEMENT" }),
      el("h1", { text: etat.agent.nom ? `Bon retour, agent ${etat.agent.nom}.` : "Bienvenue, recrue." }),
      el("p", { class: "texte-doux", text: "Chaque mission t'apprend une notion de Python. Réfléchis, découpe le problème, puis code." })),
  );

  const grille = el("div", { class: "grille-tableau" });
  vue.append(grille);

  // Colonne principale ------------------------------------------------------
  const principale = el("div", { class: "colonne" });
  grille.append(principale);

  if (revisions.length) {
    const r = revisions[0];
    principale.append(el("section", { class: "carte carte-alerte" },
      el("p", { class: "surtitre texte-orange", text: "ALERTE · ERREUR RÉCURRENTE" }),
      el("h2", { text: `« ${r.nom} » détectée ${r.nombre} fois` }),
      el("p", { text: r.mission
        ? `Une mission courte, centrée sur cette notion, t'aidera à la maîtriser : ${r.mission.titre}.`
        : `Revois la fiche « ${r.nomConcept} » puis lance une mission de révision depuis le Centre d'entraînement.` }),
      el("div", { class: "actions" },
        r.mission ? el("a", { class: "bouton bouton-alerte", href: lienMission(r.mission), text: "Lancer la mission ciblée" }) : null,
        el("a", { class: "bouton bouton-discret", href: "#entrainement", text: "Centre d'entraînement" }))));
  }

  if (recommandation) {
    const { mission, raison } = recommandation;
    principale.append(el("section", { class: "carte carte-recommandee" },
      el("p", { class: "surtitre", text: "MISSION RECOMMANDÉE" }),
      el("p", { class: "texte-doux", text: raison }),
      carteMission(mission, etat)));
  } else {
    principale.append(carte("Mission recommandée",
      videEtat("Toutes les missions de la banque sont accomplies. Impressionnant !",
        el("a", { class: "bouton bouton-principal", href: "#nouvelle-mission", text: "Générer de nouvelles missions" }))));
  }

  if (demo && statutMission(etat, demo) !== "accomplie" && recommandation?.mission.id !== demo.id) {
    principale.append(el("section", { class: "carte carte-demo" },
      el("div", {},
        el("p", { class: "surtitre", text: "MISSION DE DÉMONSTRATION" }),
        el("h3", { text: demo.titre }),
        el("p", { class: "texte-doux", text: "Teste immédiatement toute la boucle : éditeur, tests automatiques, téléphone, indices et débriefing." })),
      el("a", { class: "bouton", href: lienMission(demo), text: "Essayer" })));
  }

  // Progression générale
  const themes = progressionThemes(etat);
  const total = themes.reduce((t, th) => t + th.total, 0);
  const faites = themes.reduce((t, th) => t + th.accomplies, 0);
  principale.append(carte("Progression générale",
    el("div", { class: "ligne-entre" }, el("span", { text: `${faites} / ${total} missions de la banque` }),
      el("strong", { text: `${Math.round((faites / Math.max(total, 1)) * 100)} %` })),
    barre(faites / Math.max(total, 1), { classe: "barre-large" }),
    el("div", { class: "liste-themes" }, themes.map((th) => el("div", { class: "ligne-theme" },
      el("span", { text: THEMES[th.theme] || th.theme }),
      barre(th.accomplies / th.total),
      el("span", { class: "texte-doux mono", text: `${th.accomplies}/${th.total}` }))))));

  // Colonne latérale --------------------------------------------------------
  const laterale = el("div", { class: "colonne" });
  grille.append(laterale);
  laterale.append(carteAgent(etat));

  laterale.append(el("section", { class: "carte" },
    el("div", { class: "grille-stats" },
      stat("Missions", stats.missionsAccomplies),
      stat("Série", stats.serie, "réussites d'affilée"),
      stat("Badges", `${stats.badges}/${donnees.badges.length}`),
      stat("Tentatives", stats.tentatives))));

  const recents = conceptsRecents(etat);
  const aRevoir = bilanConcepts(etat).filter((c) => c.statut === "a_revoir");
  laterale.append(carte("Concepts récents",
    recents.length ? el("div", { class: "nuage-puces" }, recents.map(puceConcept))
      : el("p", { class: "texte-doux", text: "Accomplis ta première mission pour voir apparaître tes concepts." })));
  laterale.append(carte("Notions à revoir",
    aRevoir.length || revisions.length
      ? el("div", { class: "nuage-puces" },
        aRevoir.map((c) => puceConcept(c.id)),
        revisions.map((r) => puce(`${r.nom} ×${r.nombre}`, "puce-alerte")))
      : el("p", { class: "texte-doux", text: "Rien à signaler. Continue comme ça !" })));

  const dernieres = etat.historique.slice(0, 5);
  laterale.append(carte("Dernières missions",
    dernieres.length
      ? el("ul", { class: "liste-simple" }, dernieres.map((h) => el("li", {},
        el("a", { href: `#mission-${h.missionId}`, text: h.titre }),
        el("span", { class: "texte-doux petit", text: ` · ${h.score} pts · ${formaterRelatif(h.date)}` }))))
      : el("p", { class: "texte-doux", text: "Aucune mission accomplie pour l'instant." })));
}

function stat(libelle, valeur, aide = "") {
  return el("div", { class: "stat", title: aide },
    el("div", { class: "stat-valeur", text: String(valeur) }),
    el("div", { class: "stat-libelle", text: libelle }));
}
