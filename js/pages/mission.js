// Page 3 — Mission en cours : dossier, éditeur, console, tests, téléphone et débriefing.

import {
  el, vider, carte, puce, tampon, texteRiche, blocCode, toast, confirmer, icone, videEtat,
} from "../interface.js";
import { THEMES, DIFFICULTES, NIVEAUX_PEDAGOGIQUES, CONCEPTS_GENERABLES, trouverMission, nomConcept } from "../donnees.js";
import {
  statutMission, suiviMission, enregistrerEnvoi, enregistrerErreur, enregistrerIndice,
  enregistrerSolution, missionSuivante, nombreOccurrences, missionDeRevision, SEUIL_ERREUR_RECURRENTE,
} from "../progression.js";
import { moteur, DelaiDepasse } from "../moteur_python.js";
import { creerEditeur } from "../editeur.js";
import { telephone } from "../telephone.js";
import { stockage } from "../stockage.js";
import { lienMission, puceConcept, insigne } from "../composants.js";
import { genererEtOuvrir } from "../generation.js";

export function afficher(vue, { etat, idMission }) {
  const mission = idMission ? trouverMission(etat, idMission) : null;
  if (!mission) {
    vue.append(carte("Mission introuvable", videEtat(
      idMission ? "Cette mission n'existe plus (mission générée supprimée ?)." : "Aucune mission en cours pour le moment.",
      el("a", { class: "bouton bouton-principal", href: "#tableau-de-bord", text: "Tableau de bord" }),
      el("a", { class: "bouton", href: "#entrainement", text: "Choisir une mission" }))));
    return null;
  }

  const statut = statutMission(etat, mission);
  if (statut === "classifie") {
    vue.append(el("section", { class: "carte dossier-verrouille" },
      el("div", { class: "dossier-classifie" }, icone("verrou", 36), el("strong", { text: "DOSSIER CLASSIFIÉ" })),
      el("p", { text: "Ton niveau d'habilitation est insuffisant : accomplis d'abord la mission précédente de ce thème." }),
      el("p", { class: "texte-doux", text: "Astuce : le « mode libre » (Paramètres) débloque toutes les missions, pratique pour suivre l'ordre de ton cours." }),
      el("a", { class: "bouton bouton-principal", href: "#entrainement", text: "Retour aux missions" })));
    return null;
  }

  etat.derniereMission = mission.id;
  stockage.sauver();
  return new PageMission(vue, mission).nettoyer;
}

class PageMission {
  constructor(vue, mission) {
    this.vue = vue;
    this.mission = mission;
    this.occupe = false;
    this.minuterieBrouillon = null;
    this.nettoyer = () => this._nettoyer();
    this._construire();
  }

  get etat() { return stockage.etat; }
  get suivi() { return suiviMission(this.etat, this.mission.id); }

  // -------------------------------------------------------------------------
  // Construction de la page
  // -------------------------------------------------------------------------

  _construire() {
    const { mission, etat } = this;
    const statut = statutMission(etat, mission);

    this.vue.append(el("header", { class: "entete-mission" },
      el("div", { class: "fil-ariane" },
        el("a", { href: "#entrainement", text: "Missions" }), el("span", { text: " / " }),
        el("span", { text: THEMES[mission.theme] || mission.theme })),
      el("div", { class: "entete-mission-titre" },
        el("div", {},
          el("p", { class: "surtitre mono", text: `DOSSIER ${mission.id}` }),
          el("h1", { text: mission.titre })),
        this.tamponStatut = tampon(statut, { grand: true })),
      el("div", { class: "carte-mission-puces" },
        puce(`Niveau ${mission.niveau} · ${NIVEAUX_PEDAGOGIQUES[mission.niveau] || ""}`),
        puce(DIFFICULTES[mission.difficulte] || mission.difficulte, `puce-${mission.difficulte}`),
        puce(`${mission.tests.length} tests`),
        mission.note_difficulte ? puce("Difficulté adaptée", "puce-info") : null)));

    if (this.etat.missions[mission.id]?.accomplie) {
      this.vue.append(el("div", { class: "bandeau bandeau-vert" },
        `Mission déjà accomplie (meilleur score : ${this.etat.missions[mission.id].meilleurScore} pts). `,
        "Rejoue-la pour améliorer ton score : seuls les points gagnés en plus rapportent de l'XP."));
    }

    const grille = el("div", { class: "grille-mission" });
    this.vue.append(grille);
    grille.append(this._dossier(), this._poste());
    this._configurerTelephone();
    this.retirerEcouteurMoteur = moteur.ecouter(() => this._majBoutons());
  }

  _dossier() {
    const { mission } = this;
    const section = (titre, ...contenu) => el("div", { class: "dossier-section" }, el("h3", { text: titre }), ...contenu);
    return el("section", { class: "carte dossier" },
      el("div", { class: "dossier-onglet", text: "CONFIDENTIEL · BRIEFING" }),
      section("Briefing", el("p", { class: "briefing" }, texteRiche(mission.briefing))),
      section("Objectif pédagogique", el("p", {}, texteRiche(mission.objectif))),
      section("Concepts travaillés", el("div", { class: "nuage-puces" }, (mission.concepts || []).map(puceConcept))),
      section("Énoncé", el("p", {}, texteRiche(mission.enonce))),
      mission.donnees ? section("Données / exemple", blocCode(mission.donnees)) : null,
      mission.resultat_attendu ? section("Résultat attendu", blocCode(mission.resultat_attendu)) : null,
      el("details", { class: "methode" },
        el("summary", { text: "Méthode d'agent : réfléchir avant de coder" }),
        el("ol", {},
          el("li", { text: "Reformule la mission avec tes mots : quelles sont les ENTRÉES, quelle est la SORTIE ?" }),
          el("li", { text: "Résous l'exemple à la main, sur papier." }),
          el("li", { text: "Écris les étapes en commentaires (# 1. … # 2. …)." }),
          el("li", { text: "Code une étape à la fois et clique sur « Exécuter » souvent." }),
          el("li", { text: "Quand tout marche sur l'exemple, envoie la mission." }))));
  }

  _poste() {
    const { mission, etat } = this;
    const code = etat.brouillons[mission.id] ?? mission.code_depart ?? "";
    this.editeur = creerEditeur({
      valeur: code,
      taille: etat.reglages.tailleEditeur,
      coloration: etat.reglages.coloration,
      barreSymboles: etat.reglages.barreSymboles,
      surChange: (texte) => this._sauverBrouillon(texte),
      surExecuter: () => this.executer(),
      surEnvoyer: () => this.envoyer(),
    });

    const entreesTest = mission.tests.find((t) => t.entrees && t.entrees.length)?.entrees || [];
    this.zoneEntrees = el("textarea", {
      class: "zone-entrees", rows: "3", spellcheck: "false", autocapitalize: "off", autocorrect: "off",
      placeholder: "Une valeur par ligne (réponses aux input())", "aria-label": "Entrées du programme",
    });
    this.zoneEntrees.value = entreesTest.join("\n");

    this.boutonExecuter = el("button", { class: "bouton", type: "button", on: { click: () => this.executer() } });
    this.boutonEnvoyer = el("button", { class: "bouton bouton-principal", type: "button", on: { click: () => this.envoyer() } });
    this._majBoutons();

    this.console = el("pre", { class: "console-sortie", "aria-live": "polite" });
    this._ecrireConsole("Console prête. Clique sur « Exécuter le code » pour tester ton programme.", "info");
    this.zoneResultats = el("div", { class: "zone-resultats" });

    this.terminal = el("div", { class: "carte terminal" },
        el("div", { class: "terminal-entete" },
          el("span", { class: "terminal-voyants", "aria-hidden": "true" }, el("i"), el("i"), el("i")),
          el("span", { class: "mono", text: "terminal-securise ~ mission.py" }),
          el("button", { class: "bouton-texte", type: "button", title: "Revenir au code de départ",
            on: { click: () => this.reinitialiser() } }, icone("reinitialiser", 14), "Code de départ")),
        this.editeur.element,
        el("details", { class: "entrees", open: entreesTest.length > 0 },
          el("summary", { text: "Entrées du programme (input)" }),
          el("p", { class: "texte-doux petit", text: "Pour « Exécuter » seulement : chaque ligne est une réponse à un input(). Les tests utilisent leurs propres entrées." }),
          this.zoneEntrees),
        el("div", { class: "actions-terminal" },
          this.boutonExecuter, this.boutonEnvoyer,
          el("span", { class: "raccourci texte-doux petit", text: "Ctrl/Cmd + Entrée : exécuter · + Maj : envoyer" })));
    return el("section", { class: "poste" },
      this.terminal,
      el("div", { class: "carte console" },
        el("div", { class: "console-entete" }, el("span", { class: "mono", text: "CONSOLE" }),
          el("button", { class: "bouton-texte", type: "button", text: "Effacer", on: { click: () => this._ecrireConsole("", "info") } })),
        this.console),
      this.zoneResultats);
  }

  _configurerTelephone() {
    telephone.configurer(this.mission, {
      suivi: this.suivi,
      accomplie: Boolean(this.etat.missions[this.mission.id]?.accomplie),
      surIndice: (numero) => {
        enregistrerIndice(this.etat, this.mission, numero);
        stockage.sauver();
      },
      surSolution: () => {
        enregistrerSolution(this.etat, this.mission);
        this.etat.serie = 0;
        stockage.sauver();
        toast("Solution révélée : le score maximal de cette mission est réduit.", { type: "alerte" });
      },
    });
  }

  _majBoutons() {
    if (!this.boutonExecuter) return;
    const pret = moteur.etat === "pret";
    const libelle = moteur.etat === "erreur" ? "Moteur indisponible" : "Chargement de Python…";
    vider(this.boutonExecuter).append(icone("executer", 16), pret ? (this.occupe ? "Exécution…" : "Exécuter le code") : libelle);
    vider(this.boutonEnvoyer).append(icone("envoyer", 16), pret ? (this.occupe ? "Vérification…" : "Envoyer la mission") : "Envoyer la mission");
    this.boutonExecuter.disabled = !pret || this.occupe;
    this.boutonEnvoyer.disabled = !pret || this.occupe;
  }

  _occuper(valeur) {
    this.occupe = valeur;
    this._majBoutons();
  }

  _sauverBrouillon(texte) {
    clearTimeout(this.minuterieBrouillon);
    this.minuterieBrouillon = setTimeout(() => {
      this.etat.brouillons[this.mission.id] = texte;
      stockage.sauver();
    }, 600);
  }

  _ecrireConsole(texte, type = "normal", avertissements = []) {
    vider(this.console);
    for (const avertissement of avertissements || []) {
      this.console.append(el("span", { class: "console-avertissement", text: `⚠ ${avertissement}\n` }));
    }
    this.console.append(el("span", { class: `console-${type}`, text: texte }));
  }

  // -------------------------------------------------------------------------
  // Exécuter
  // -------------------------------------------------------------------------

  async executer() {
    if (this.occupe || moteur.etat !== "pret") return;
    this._occuper(true);
    this._ecrireConsole("▶ Exécution en cours…", "info");
    const delai = this.etat.reglages.delai;
    const code = this.editeur.valeur;
    try {
      const entrees = this.zoneEntrees.value.split("\n").filter((ligne, i, tout) => ligne !== "" || i < tout.length - 1);
      const reponse = await moteur.appeler("executer", { code, entrees, delai }, delai + 8);
      this.etat.stats.executions += 1;
      const texte = reponse.console || (reponse.erreur ? "" : "(Le programme s'est exécuté sans rien afficher.)");
      this._ecrireConsole(texte, reponse.erreur ? "erreur" : "normal", reponse.avertissements);
      this.editeur.marquerLigne(reponse.erreur?.ligne);
      if (reponse.diagnostic) this._signalerErreur(reponse.diagnostic, "execution");
      else telephone.effacerDiagnostic();
      stockage.sauver();
    } catch (erreur) {
      await this._gererEchecMoteur(erreur, code);
    } finally {
      this._occuper(false);
    }
  }

  // -------------------------------------------------------------------------
  // Envoyer la mission
  // -------------------------------------------------------------------------

  async envoyer() {
    if (this.occupe || moteur.etat !== "pret") return;
    this._occuper(true);
    this._ecrireConsole("⬆ Transmission au QG… exécution des tests automatiques.", "info");
    vider(this.zoneResultats);
    const delai = this.etat.reglages.delai;
    const code = this.editeur.valeur;
    this.etat.brouillons[this.mission.id] = code;
    try {
      const rapport = await moteur.appeler("evaluer", {
        mission: this.mission, code, delai, reveler_donnees: this.suivi.enCours.envoisEchoues >= 3,
      }, delai * 2 + this.mission.tests.length + 12);
      const resume = enregistrerEnvoi(this.etat, this.mission, rapport);
      this._ecrireConsole(rapport.console || "(aucun affichage pendant l'exécution)", rapport.reussi ? "normal" : "erreur",
        rapport.avertissements);
      this.zoneResultats.append(this._rapportTests(rapport));
      if (rapport.reussi) {
        this.editeur.marquerLigne(null);
        telephone.effacerDiagnostic();
        telephone.contexte.accomplie = true;
        telephone.basculer(false); // place au débriefing
        this.tamponStatut.replaceWith(this.tamponStatut = tampon("accomplie", { grand: true }));
        this.zoneResultats.prepend(this._debriefing(rapport, resume));
        this._celebrer(resume);
        this.zoneResultats.scrollIntoView({ behavior: this.etat.reglages.animations ? "smooth" : "auto", block: "start" });
      } else {
        this.editeur.marquerLigne(rapport.diagnostic?.ligne);
        if (rapport.diagnostic) this._signalerErreur(rapport.diagnostic, "envoi");
        if (resume.envoisEchoues === 3) {
          toast("Après 3 envois, la solution peut être consultée dans le téléphone (avec pénalité).", { type: "info" });
        }
      }
      stockage.sauver();
    } catch (erreur) {
      await this._gererEchecMoteur(erreur, code);
    } finally {
      this._occuper(false);
    }
  }

  async _gererEchecMoteur(erreur, code) {
    if (erreur instanceof DelaiDepasse) {
      this._ecrireConsole(`⏱ ${erreur.message}\nLe moteur Python redémarre… (quelques secondes)`, "erreur");
      try {
        const diagnostic = await moteur.appeler("expliquer", {
          code, erreur: { type: "DelaiDepasse", message: "Le programme ne répondait plus et a été arrêté.", ligne: null },
        }, 30);
        this._signalerErreur(diagnostic, "execution");
        this._ecrireConsole(`⏱ ${erreur.message}\nMoteur Python redémarré. Vérifie tes boucles (voir le téléphone).`, "erreur");
        stockage.sauver();
      } catch {
        this._ecrireConsole(`⏱ ${erreur.message}\nLe moteur n'a pas pu redémarrer : recharge la page.`, "erreur");
      }
      return;
    }
    this._ecrireConsole(`Erreur interne de l'application : ${erreur.message}\nTon code n'est pas en cause. Réessaie ; si le problème persiste, recharge la page.`, "erreur");
  }

  /** Enregistre l'erreur, l'affiche dans le téléphone et propose une révision si elle revient souvent. */
  _signalerErreur(diagnostic, source) {
    const entree = enregistrerErreur(this.etat, this.mission, diagnostic, source);
    const nombre = nombreOccurrences(this.etat, diagnostic.categorie);
    let revision = null;
    if (nombre >= SEUIL_ERREUR_RECURRENTE) {
      const missionCiblee = missionDeRevision(diagnostic.categorie);
      if (missionCiblee && missionCiblee.id !== this.mission.id) {
        revision = {
          nombre,
          texte: `Le QG te propose une mission courte centrée sur cette notion : « ${missionCiblee.titre} ».`,
          libelle: "Lancer la mission ciblée",
          action: () => { location.hash = lienMission(missionCiblee); },
        };
      } else if (CONCEPTS_GENERABLES.includes(diagnostic.concept) && !missionCiblee) {
        revision = {
          nombre,
          texte: `Je peux générer une mission plus simple sur « ${nomConcept(diagnostic.concept)} ».`,
          libelle: "Générer une mission de révision",
          action: () => genererEtOuvrir({ concepts: [diagnostic.concept], difficulte: "facile", etiquette: "révision" }),
        };
      }
      if (entree && nombre === SEUIL_ERREUR_RECURRENTE) {
        toast(`« ${diagnostic.nom_categorie} » revient souvent. Une mission de révision est proposée.`,
          { type: "alerte", titre: "Erreur récurrente détectée" });
      }
    }
    telephone.afficherDiagnostic(diagnostic, { ouvrir: true, revision });
    this._garderTerminalVisible();
  }

  /** Après l'ouverture du téléphone, la mise en page change : on garde le code sous les yeux. */
  _garderTerminalVisible() {
    requestAnimationFrame(() => {
      const position = this.terminal.getBoundingClientRect();
      if (position.top < 56 || position.top > window.innerHeight * 0.6) {
        this.terminal.scrollIntoView({ block: "start", behavior: "auto" });
      }
    });
  }

  // -------------------------------------------------------------------------
  // Affichage des résultats
  // -------------------------------------------------------------------------

  _rapportTests(rapport) {
    const liste = el("ol", { class: "liste-tests" });
    for (const test of rapport.tests) {
      const details = [];
      if (test.appel) details.push(el("div", { class: "test-ligne" }, el("span", { class: "texte-doux", text: "Appel : " }), el("code", { text: test.appel })));
      if (!test.reussi && test.attendu !== "" && test.type !== "structure") {
        const multiligne = String(test.attendu).includes("\n") || String(test.obtenu).includes("\n");
        const valeur = (texte) => (multiligne ? el("pre", { class: "bloc-code mini", text: texte || "(rien)" }) : el("code", { text: texte || "(rien)" }));
        details.push(el("div", { class: "test-ligne" }, el("span", { class: "texte-doux", text: "Attendu : " }), valeur(test.attendu)));
        if (test.obtenu !== "") details.push(el("div", { class: "test-ligne" }, el("span", { class: "texte-doux", text: "Obtenu : " }), valeur(test.obtenu)));
      }
      if (!test.reussi && test.sortie && test.type === "appel") {
        details.push(el("div", { class: "test-ligne" }, el("span", { class: "texte-doux", text: "Affiché pendant l'appel : " }), el("code", { text: test.sortie.trim().slice(0, 200) })));
      }
      if (!test.reussi && test.message) details.push(el("div", { class: "test-message", text: test.message }));
      liste.append(el("li", { class: `test ${test.reussi ? "reussi" : "echoue"}` },
        el("span", { class: "test-icone", "aria-label": test.reussi ? "réussi" : "échoué", text: test.reussi ? "✓" : "✗" }),
        el("div", { class: "test-corps" },
          el("div", { class: "test-titre" },
            el("strong", { text: `Test ${test.numero}` }),
            test.description ? el("span", { text: ` — ${test.description}` }) : null,
            !test.visible ? puce("caché", "puce-mini") : null),
          details)));
    }
    return el("section", { class: `carte rapport-tests ${rapport.reussi ? "succes" : "echec"}` },
      el("div", { class: "ligne-entre" },
        el("h2", { class: "carte-titre", text: "Rapport des tests automatiques" }),
        el("span", { class: `puce ${rapport.reussi ? "puce-succes" : "puce-alerte"}`, text: `${rapport.nb_reussis} / ${rapport.nb_total} réussis` })),
      liste,
      !rapport.reussi ? el("div", { class: "actions" },
        el("button", { class: "bouton bouton-petit", type: "button", text: "Voir le diagnostic",
          on: { click: () => telephone.ouvrirOnglet("diagnostic") } }),
        el("button", { class: "bouton bouton-petit bouton-discret", type: "button", text: "Demander un indice",
          on: { click: () => telephone.ouvrirOnglet("indices") } })) : null);
  }

  _debriefing(rapport, resume) {
    const { mission } = this;
    const qualite = rapport.qualite || {};
    const suivante = missionSuivante(this.etat, mission);
    return el("section", { class: "carte debriefing" },
      el("div", { class: "debriefing-tampon" }, tampon("accomplie", { grand: true })),
      el("div", { class: "debriefing-resultats" },
        el("div", { class: "resultat-bloc succes" },
          el("div", { class: "resultat-libelle", text: "Mission accomplie" }),
          el("div", { class: "resultat-valeur", text: "✓" }),
          el("div", { class: "texte-doux petit", text: `${rapport.nb_reussis}/${rapport.nb_total} tests réussis` })),
        el("div", { class: `resultat-bloc qualite-${qualite.score >= 85 ? "haute" : qualite.score >= 70 ? "moyenne" : "basse"}` },
          el("div", { class: "resultat-libelle", text: "Qualité du code" }),
          el("div", { class: "resultat-valeur", text: `${qualite.score ?? "—"}/100` }),
          el("div", { class: "texte-doux petit", text: qualite.niveau || "" })),
        el("div", { class: "resultat-bloc" },
          el("div", { class: "resultat-libelle", text: "Score" }),
          el("div", { class: "resultat-valeur", text: `${resume.score} pts` }),
          el("div", { class: "texte-vert petit", text: resume.xpGagne ? `+${resume.xpGagne} XP` : "Pas d'XP (score non amélioré)" }))),
      el("div", { class: "debriefing-grille" },
        el("div", {},
          el("h3", { text: "Conseils de l'instructeur" }),
          qualite.conseils?.length
            ? el("ol", { class: "conseils" }, qualite.conseils.map((c) => el("li", {},
              el("strong", { text: c.titre }), el("p", { class: "texte-doux", text: c.detail }))))
            : el("p", { text: "Aucun conseil : ton code est propre et lisible. Excellent travail !" }),
          qualite.points_forts?.length
            ? el("div", { class: "nuage-puces" }, qualite.points_forts.map((p) => puce(`✓ ${p}`, "puce-succes"))) : null),
        el("div", {},
          el("h3", { text: "Détail du score" }),
          el("ul", { class: "liste-score" }, resume.details.map((d) => el("li", {},
            el("span", { text: d.libelle }), el("span", { class: d.valeur < 0 ? "texte-rouge" : "texte-vert", text: `${d.valeur > 0 ? "+" : ""}${d.valeur}` })))),
          resume.nouveauxBadges?.length ? el("div", {},
            el("h3", { text: "Badges débloqués" }),
            el("div", { class: "grille-insignes" }, resume.nouveauxBadges.map((b) => insigne(b, true)))) : null)),
      el("h3", { text: "Explication pédagogique" }),
      el("p", {}, texteRiche(mission.explication || "")),
      mission.solution ? el("details", { class: "solution-reference" },
        el("summary", { text: "Comparer avec la solution de l'agence" }),
        blocCode(mission.solution, { numeros: true })) : null,
      el("div", { class: "actions" },
        suivante ? el("a", { class: "bouton bouton-principal", href: lienMission(suivante), text: `Mission suivante : ${suivante.titre}` }) : null,
        el("a", { class: "bouton", href: "#tableau-de-bord", text: "Tableau de bord" }),
        el("button", { class: "bouton bouton-discret", type: "button", text: "Rejouer avec le code de départ",
          on: { click: () => this.reinitialiser(true) } })));
  }

  _celebrer(resume) {
    for (const badge of resume.nouveauxBadges || []) {
      toast(badge.description, { type: "badge", titre: `Badge débloqué : ${badge.nom}`, duree: 6000 });
    }
    if (resume.nouveauGrade) toast(`Nouveau grade : ${resume.nouveauGrade}`, { type: "succes", titre: "Promotion !", duree: 6000 });
    else if (resume.nouveauNiveau) toast(`Tu passes au niveau ${resume.nouveauNiveau}.`, { type: "succes", titre: "Niveau supérieur" });
  }

  async reinitialiser(sansConfirmation = false) {
    if (!sansConfirmation) {
      const ok = await confirmer({
        titre: "Revenir au code de départ ?", message: "Ton code actuel sera remplacé.", ok: "Remplacer", danger: true,
      });
      if (!ok) return;
    }
    this.editeur.definir(this.mission.code_depart || "");
    this.editeur.marquerLigne(null);
    delete this.etat.brouillons[this.mission.id];
    stockage.sauver();
    vider(this.zoneResultats);
    this.editeur.focus();
  }

  _nettoyer() {
    clearTimeout(this.minuterieBrouillon);
    if (this.editeur && this.etat.brouillons[this.mission.id] !== this.editeur.valeur
        && this.editeur.valeur !== (this.mission.code_depart || "")) {
      this.etat.brouillons[this.mission.id] = this.editeur.valeur;
      stockage.sauver();
    }
    this.retirerEcouteurMoteur?.();
    telephone.configurer(null);
  }
}

// Utilisé par le routeur pour « Mission en cours ».
export function afficherMissionEnCours(vue, contexte) {
  return afficher(vue, { ...contexte, idMission: contexte.etat.derniereMission });
}

