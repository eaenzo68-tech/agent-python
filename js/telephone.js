// Le téléphone d'agent : l'assistant pédagogique.
//
// Trois onglets :
// - Diagnostic : explication de la dernière erreur (jamais la solution) ;
// - Indices    : trois niveaux d'aide progressifs (chacun coûte des points) ;
// - Solution   : verrouillée, révélable volontairement avec un avertissement.

import { el, vider, extraitCode, blocCode, formaterIndice, texteRiche, icone, confirmer } from "./interface.js";

const NOMS_INDICES = ["Piste légère", "Explication du concept", "Exemple similaire"];
const ESSAIS_AVANT_SOLUTION = 3;

const ASTUCES = [
  "Avant de coder, écris les étapes en français sous forme de commentaires.",
  "Une erreur n'est pas un échec : c'est un indice que Python te donne.",
  "Teste ton code sur un tout petit exemple, à la main, ligne par ligne.",
  "Un bon nom de variable vaut mieux qu'un long commentaire.",
  "Ajoute un print() temporaire pour voir ce que contient une variable.",
  "Lis le message d'erreur en entier : il indique souvent la ligne exacte.",
];

class Telephone {
  constructor() {
    this.racine = null;
    this.ouvert = false;
    this.onglet = "diagnostic";
    this.mission = null;
    this.contexte = null; // { suivi, surIndice, surSolution, revision }
    this.diagnostic = null;
    this.nonLu = false;
  }

  monter(conteneur) {
    this.racine = conteneur;
    this.rendre();
    setInterval(() => this._majHeure(), 30_000);
  }

  /** Associe le téléphone à la mission ouverte (ou null pour le mode veille). */
  configurer(mission, contexte = null) {
    this.mission = mission;
    this.contexte = contexte;
    this.diagnostic = null;
    this.nonLu = false;
    this.onglet = "diagnostic";
    this.rendre();
  }

  afficherDiagnostic(diagnostic, { ouvrir = true, revision = null } = {}) {
    this.diagnostic = diagnostic;
    if (this.contexte) this.contexte.revision = revision;
    this.onglet = "diagnostic";
    this.nonLu = !ouvrir;
    if (ouvrir) this.ouvert = true;
    this.rendre();
    if (ouvrir) this._vibrer();
  }

  effacerDiagnostic() {
    this.diagnostic = null;
    this.rendre();
  }

  basculer(ouvrir = !this.ouvert) {
    this.ouvert = ouvrir;
    if (ouvrir) this.nonLu = false;
    this.rendre();
  }

  ouvrirOnglet(onglet) {
    this.onglet = onglet;
    this.basculer(true);
  }

  _vibrer() {
    const corps = this.racine?.querySelector(".telephone-corps");
    if (!corps) return;
    corps.classList.remove("vibre");
    void corps.offsetWidth; // relance l'animation
    corps.classList.add("vibre");
  }

  _majHeure() {
    const heure = this.racine?.querySelector(".telephone-heure");
    if (heure) heure.textContent = new Date().toLocaleTimeString("fr-CH", { hour: "2-digit", minute: "2-digit" });
  }

  // -------------------------------------------------------------------------
  // Affichage
  // -------------------------------------------------------------------------

  rendre() {
    if (!this.racine) return;
    vider(this.racine);
    this.racine.className = `telephone${this.ouvert ? " ouvert" : ""}`;
    // Sur grand écran, la page se décale pour que le téléphone ne cache rien.
    document.body.classList.toggle("telephone-ouvert", this.ouvert);

    const bouton = el("button", {
      class: "telephone-bouton", type: "button",
      "aria-label": this.ouvert ? "Fermer le téléphone d'agent" : "Ouvrir le téléphone d'agent",
      "aria-expanded": String(this.ouvert),
      on: { click: () => this.basculer() },
    }, icone("telephone", 22), el("span", { class: "telephone-bouton-texte", text: "Téléphone" }),
    this.nonLu ? el("span", { class: "pastille", "aria-label": "Nouveau message" }) : null);

    const onglets = [["diagnostic", "Diagnostic"], ["indices", "Indices"], ["solution", "Solution"]];
    const corps = el("div", { class: "telephone-corps", role: "dialog", "aria-label": "Téléphone d'agent" },
      el("div", { class: "telephone-encoche" }),
      el("div", { class: "telephone-statut" },
        el("span", { text: "AGENCE · LIGNE SÉCURISÉE" }),
        el("span", { class: "telephone-heure", text: new Date().toLocaleTimeString("fr-CH", { hour: "2-digit", minute: "2-digit" }) })),
      el("div", { class: "telephone-entete" },
        el("strong", { text: "QG · Assistant" }),
        el("button", { class: "bouton-icone", type: "button", "aria-label": "Fermer", on: { click: () => this.basculer(false) } }, icone("fermer", 16))),
      this.mission ? el("div", { class: "telephone-onglets", role: "tablist" }, onglets.map(([id, nom]) => el("button", {
        type: "button", role: "tab", class: `telephone-onglet${this.onglet === id ? " actif" : ""}`,
        "aria-selected": String(this.onglet === id), text: nom,
        on: { click: () => { this.onglet = id; this.rendre(); } },
      }))) : null,
      el("div", { class: "telephone-ecran" }, this._contenu()));

    this.racine.append(corps, bouton);
  }

  _contenu() {
    if (!this.mission) return this._veille();
    if (this.onglet === "indices") return this._indices();
    if (this.onglet === "solution") return this._solution();
    return this._diagnostic();
  }

  _veille() {
    const astuce = ASTUCES[new Date().getDate() % ASTUCES.length];
    return el("div", { class: "telephone-veille" },
      el("div", { class: "bulle bulle-qg" }, el("span", { class: "bulle-auteur", text: "QG" }),
        el("p", { text: "Aucune mission active. Ouvre une mission : je t'aiderai à comprendre tes erreurs, sans te donner la réponse." })),
      el("div", { class: "bulle bulle-qg" }, el("span", { class: "bulle-auteur", text: "Conseil du jour" }), el("p", { text: astuce })));
  }

  _diagnostic() {
    const d = this.diagnostic;
    if (!d) {
      return el("div", { class: "telephone-veille" },
        el("div", { class: "bulle bulle-qg" }, el("span", { class: "bulle-auteur", text: "QG" }),
          el("p", { text: "Ligne ouverte. Exécute ton code ou envoie la mission : si quelque chose ne va pas, j'analyserai l'erreur ici." })),
        el("p", { class: "telephone-note", text: "Besoin d'un coup de pouce sans erreur ? Onglet « Indices »." }));
    }
    const sections = [
      el("div", { class: "diagnostic-entete" },
        el("span", { class: "puce puce-alerte", text: d.nom_categorie || "Erreur" }),
        d.ligne ? el("span", { class: "puce", text: `Ligne ${d.ligne}` }) : null),
      el("h3", { class: "diagnostic-titre", text: d.titre }),
      this._section("Ce qui se passe", texteRiche(d.description)),
    ];
    if (d.extrait && d.extrait.length) sections.push(this._section("Le passage concerné", extraitCode(d.extrait)));
    if (d.message_python) sections.push(el("p", { class: "message-python" }, el("span", { text: "Python dit : " }), el("code", { text: `${d.type}: ${d.message_python}` })));
    sections.push(
      this._section("Pourquoi ?", texteRiche(d.pourquoi)),
      el("div", { class: "bulle bulle-qg bulle-question" }, el("span", { class: "bulle-auteur", text: "Question du QG" }), el("p", {}, texteRiche(d.question))),
      this._section("Rappel du concept", blocCode(d.rappel)),
    );
    if (d.exemple) sections.push(this._section("Exemple (différent de ta mission)", blocCode(d.exemple)));
    sections.push(el("div", { class: "piste" }, el("strong", { text: "Piste : " }), texteRiche(d.indice)));

    const revision = this.contexte?.revision;
    if (revision) {
      sections.push(el("div", { class: "alerte-revision" },
        el("strong", { text: `Erreur récurrente (${revision.nombre} fois)` }),
        el("p", { text: revision.texte }),
        el("button", { class: "bouton bouton-petit bouton-principal", type: "button", text: revision.libelle,
          on: { click: revision.action } })));
    }
    return el("div", { class: "diagnostic" }, sections);
  }

  _section(titre, contenu) {
    return el("div", { class: "telephone-section" }, el("h4", { text: titre }), contenu);
  }

  _indices() {
    const enCours = this.contexte?.suivi?.enCours || { indicesUtilises: 0 };
    const indices = this.mission.indices || [];
    const penalite = this.mission.bareme?.penalite_indice ?? 10;
    const liste = el("div", { class: "indices" },
      el("p", { class: "telephone-note", text: `Chaque indice débloqué retire ${penalite} points au score de la mission. Essaie d'abord seul !` }));
    indices.forEach((texte, i) => {
      const numero = i + 1;
      const debloque = enCours.indicesUtilises >= numero;
      const accessible = enCours.indicesUtilises >= numero - 1;
      const carte = el("div", { class: `indice${debloque ? " debloque" : ""}` },
        el("div", { class: "indice-entete" }, el("strong", { text: `Indice ${numero}` }), el("span", { text: NOMS_INDICES[i] })));
      if (debloque) {
        carte.append(formaterIndice(texte));
      } else {
        carte.append(el("button", {
          class: "bouton bouton-petit", type: "button", disabled: !accessible,
          text: accessible ? `Déverrouiller (−${penalite} pts)` : `Débloque d'abord l'indice ${numero - 1}`,
          on: { click: () => { this.contexte?.surIndice?.(numero); this.rendre(); } },
        }, icone("verrou", 14)));
      }
      liste.append(carte);
    });
    return liste;
  }

  _solution() {
    const enCours = this.contexte?.suivi?.enCours || { envoisEchoues: 0, solutionRevelee: false };
    const penalite = this.mission.bareme?.penalite_solution ?? 50;
    if (enCours.solutionRevelee || this.contexte?.accomplie) {
      return el("div", { class: "solution" },
        el("p", { class: "telephone-note", text: "Ne la copie pas : retape-la à ta façon, ligne par ligne, en comprenant chaque instruction. C'est comme ça qu'on apprend." }),
        this.mission.solution ? blocCode(this.mission.solution, { numeros: true }) : el("p", { text: "Cette mission n'a pas de solution de référence." }),
        el("h4", { text: "Explication" }), el("p", {}, texteRiche(this.mission.explication || "")));
    }
    const restants = Math.max(0, ESSAIS_AVANT_SOLUTION - enCours.envoisEchoues);
    return el("div", { class: "solution verrouillee" },
      el("div", { class: "dossier-classifie" }, icone("verrou", 28), el("strong", { text: "SOLUTION CLASSIFIÉE" })),
      el("p", { text: restants > 0
        ? `Le QG recommande au moins ${ESSAIS_AVANT_SOLUTION} tentatives avant de consulter la solution (encore ${restants}).`
        : "Tu as fait plusieurs tentatives : tu peux consulter la solution si tu es bloqué." }),
      el("button", {
        class: `bouton ${restants > 0 ? "bouton-discret" : "bouton-alerte"}`, type: "button", text: "Révéler la solution",
        on: { click: async () => {
          const ok = await confirmer({
            titre: "Révéler la solution ?",
            message: `Attention : révéler la solution retire ${penalite} points au score de cette mission et interrompt ta série de réussites. As-tu essayé les indices ?`,
            ok: "Révéler quand même", annuler: "Je réessaie", danger: true,
          });
          if (ok) { this.contexte?.surSolution?.(); this.rendre(); }
        } },
      }));
  }
}

export const telephone = new Telephone();
