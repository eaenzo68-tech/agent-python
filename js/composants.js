// Composants réutilisés par plusieurs pages : carte de mission, carte d'agent, badge…

import { el, tampon, puce, barre, icone } from "./interface.js";
import { THEMES, DIFFICULTES, NIVEAUX_PEDAGOGIQUES, nomConcept } from "./donnees.js";
import { statutMission, grade, niveau } from "./progression.js";

export function lienMission(mission) {
  return `#mission-${mission.id}`;
}

export function carteMission(mission, etat, { compacte = false, actionTexte = null } = {}) {
  const statut = statutMission(etat, mission);
  const suivi = etat.missions[mission.id];
  const verrouillee = statut === "classifie";
  const texteBouton = actionTexte
    || (verrouillee ? "Accès refusé" : statut === "accomplie" ? "Rejouer" : statut === "en_cours" ? "Reprendre" : "Commencer");

  return el("article", { class: `carte-mission statut-${statut}${compacte ? " compacte" : ""}` },
    el("div", { class: "carte-mission-haut" },
      el("span", { class: "mission-id", text: mission.id.startsWith("GEN-") ? "GÉNÉRÉE" : mission.id }),
      tampon(statut)),
    el("h3", { class: "carte-mission-titre", text: verrouillee ? "▓▓▓▓▓▓ ▓▓▓▓▓▓▓" : mission.titre }),
    verrouillee
      ? el("p", { class: "texte-doux", text: "Accomplis la mission précédente de ce thème pour obtenir l'habilitation." })
      : (!compacte ? el("p", { class: "carte-mission-briefing", text: mission.briefing }) : null),
    el("div", { class: "carte-mission-puces" },
      puce(THEMES[mission.theme] || mission.theme, "puce-theme"),
      puce(`Niv. ${mission.niveau} · ${NIVEAUX_PEDAGOGIQUES[mission.niveau] || ""}`),
      puce(DIFFICULTES[mission.difficulte] || mission.difficulte, `puce-${mission.difficulte}`),
      mission.demo ? puce("Démo", "puce-demo") : null,
      mission.revision_pour?.length ? puce("Révision", "puce-revision") : null),
    el("div", { class: "carte-mission-bas" },
      suivi?.accomplie ? el("span", { class: "texte-doux", text: `Meilleur score : ${suivi.meilleurScore} pts` }) : el("span"),
      verrouillee
        ? el("span", { class: "bouton bouton-petit desactive" }, icone("verrou", 14), "Classifié")
        : el("a", { class: "bouton bouton-petit bouton-principal", href: lienMission(mission), text: texteBouton })));
}

export function carteAgent(etat) {
  const g = grade(etat.xp);
  const n = niveau(etat.xp);
  return el("section", { class: "carte carte-agent" },
    el("div", { class: "carte-agent-entete" },
      el("span", { text: "AGENCE PY · CARTE D'IDENTITÉ" }),
      el("span", { class: "habilitation", text: `HABILITATION ${g.habilitation}` })),
    el("div", { class: "carte-agent-corps" },
      el("div", { class: "carte-agent-photo", "aria-hidden": "true" },
        el("span", { text: (etat.agent.nom || "?").slice(0, 1).toUpperCase() })),
      el("div", {},
        el("div", { class: "carte-agent-nom", text: etat.agent.nom || "Agent sans nom" }),
        el("div", { class: "carte-agent-grade", text: g.nom }),
        el("div", { class: "texte-doux mono", text: `Matricule ${etat.agent.matricule} · Niveau ${n.niveau}` }))),
    el("div", { class: "carte-agent-xp" },
      el("div", { class: "ligne-entre" }, el("span", { text: `${etat.xp} XP` }),
        el("span", { class: "texte-doux", text: `${n.xpDansNiveau} / ${n.xpPourNiveau} vers niveau ${n.niveau + 1}` })),
      barre(n.progression, { libelle: "Progression vers le niveau suivant" }),
      g.suivant ? el("div", { class: "texte-doux petit", text: `Prochain grade : ${g.suivant.nom} (${g.suivant.xp} XP)` })
        : el("div", { class: "texte-vert petit", text: "Grade maximal atteint." })));
}

export function insigne(badge, obtenu) {
  return el("div", { class: `insigne${obtenu ? " obtenu" : ""}`, title: badge.description },
    el("div", { class: "insigne-symbole", text: obtenu ? badge.symbole : "?" }),
    el("div", { class: "insigne-nom", text: badge.nom }),
    el("div", { class: "insigne-description", text: badge.description }));
}

export function puceConcept(id) {
  return el("a", { class: "puce puce-concept", href: `#concept-${id}`, text: nomConcept(id) });
}
