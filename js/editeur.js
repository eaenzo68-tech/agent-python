// Éditeur de code Python léger, pensé pour Windows (clavier) ET iPad (écran tactile).
//
// Principe : une zone de texte (<textarea>) transparente est posée exactement
// au-dessus d'un bloc coloré (<pre>). On tape dans la zone de texte, on voit la
// coloration en dessous. Aucune bibliothèque externe : tout fonctionne hors ligne.
//
// Fonctions utiles pour coder :
// - Tab / Maj+Tab : indenter / désindenter (4 espaces) ;
// - Entrée : garde l'indentation, et l'augmente après « : » ;
// - Ctrl/Cmd + Entrée : exécuter ; Ctrl/Cmd + Maj + Entrée : envoyer ;
// - Ctrl/Cmd + / : commenter / décommenter ;
// - barre de symboles pour l'iPad (Tab, :, (), [], {}, guillemets…).

import { colorer } from "./coloration.js";
import { el } from "./interface.js";

const INDENT = "    ";
const GUILLEMETS_COURBES = /[\u201c\u201d\u2018\u2019]/g;
const CONTIENT_GUILLEMETS_COURBES = /[\u201c\u201d\u2018\u2019]/;
const REMPLACEMENTS = { "“": '"', "”": '"', "‘": "'", "’": "'" };

// Sur iPhone / iPad, Safari décale légèrement le texte d'une zone de saisie par rapport
// au calque coloré : le curseur ne tombe plus au bon endroit. On y affiche donc
// directement le texte tapé (sans coloration), ce qui garantit un curseur aligné.
const APPAREIL_IOS = /iP(hone|ad|od)/.test(navigator.userAgent)
  || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

export function creerEditeur({
  valeur = "", taille = 15, coloration = true, barreSymboles = "auto",
  surChange = () => {}, surExecuter = () => {}, surEnvoyer = () => {},
} = {}) {
  const hauteurLigne = Math.round(taille * 1.6);
  if (APPAREIL_IOS) coloration = false;

  const saisie = el("textarea", {
    class: "editeur-saisie", spellcheck: "false", autocapitalize: "off", autocomplete: "off",
    autocorrect: "off", wrap: "off", "aria-label": "Éditeur de code Python", "data-gramm": "false",
  });
  const calque = el("pre", { class: "editeur-calque", "aria-hidden": "true" }, el("code"));
  const marque = el("div", { class: "editeur-marque", hidden: true });
  const gouttiere = el("pre", { class: "editeur-gouttiere", "aria-hidden": "true" });
  const defilement = el("div", { class: "editeur-defilement" }, marque, calque, saisie);

  const touches = [
    ["⇥", "Indenter", () => indenter(false)], ["⇤", "Désindenter", () => indenter(true)],
    [":", null, () => inserer(":")], ["( )", null, () => entourer("(", ")")],
    ["[ ]", null, () => entourer("[", "]")], ["{ }", null, () => entourer("{", "}")],
    ['" "', null, () => entourer('"', '"')], ["' '", null, () => entourer("'", "'")],
    ["=", null, () => inserer(" = ")], ["==", null, () => inserer(" == ")],
    ["_", null, () => inserer("_")], ["#", null, () => inserer("# ")],
    ["+", null, () => inserer(" + ")], ["<", null, () => inserer(" < ")], [">", null, () => inserer(" > ")],
  ];
  const barre = el("div", { class: "editeur-touches", role: "toolbar", "aria-label": "Symboles" },
    touches.map(([texte, titre, action]) => el("button", {
      type: "button", class: "touche", text: texte, title: titre || `Insérer ${texte}`, tabindex: "-1",
      // pointerdown + preventDefault : le clavier de l'iPad reste ouvert
      on: { pointerdown: (evt) => { evt.preventDefault(); action(); }, click: (evt) => evt.preventDefault() },
    })));

  const racine = el("div", {
    class: `editeur${coloration ? "" : " sans-coloration"}${barreSymboles === "toujours" ? " touches-visibles" : ""}${barreSymboles === "jamais" ? " touches-cachees" : ""}`,
    style: { "--taille-code": `${taille}px`, "--hauteur-ligne": `${hauteurLigne}px` },
  }, barre, el("div", { class: "editeur-zone" }, gouttiere, defilement));

  // -------------------------------------------------------------------------
  // Mise à jour de l'affichage
  // -------------------------------------------------------------------------

  function mettreAJour() {
    const texte = saisie.value;
    const lignes = texte.split("\n");
    calque.firstChild.innerHTML = (coloration ? colorer(texte) : texte.replace(/&/g, "&amp;").replace(/</g, "&lt;")) + "\n";
    gouttiere.textContent = lignes.map((_, i) => i + 1).join("\n");
    const colonnes = Math.max(...lignes.map((l) => l.length), 20);
    racine.style.setProperty("--colonnes", String(colonnes + 2));
    racine.style.setProperty("--lignes", String(Math.max(lignes.length, 12)));
  }

  function changer() {
    // Clavier iPad : remplace les guillemets « intelligents » par des guillemets droits.
    if (CONTIENT_GUILLEMETS_COURBES.test(saisie.value)) {
      const debut = saisie.selectionStart;
      const fin = saisie.selectionEnd;
      saisie.value = saisie.value.replace(GUILLEMETS_COURBES, (c) => REMPLACEMENTS[c]);
      saisie.setSelectionRange(debut, fin);
    }
    mettreAJour();
    surChange(saisie.value);
  }

  // -------------------------------------------------------------------------
  // Édition (on passe par insertText pour garder l'annulation Ctrl+Z)
  // -------------------------------------------------------------------------

  function inserer(texte) {
    saisie.focus();
    let ok = false;
    try { ok = document.execCommand("insertText", false, texte); } catch { ok = false; }
    if (!ok) {
      saisie.setRangeText(texte, saisie.selectionStart, saisie.selectionEnd, "end");
      changer();
    }
  }

  function entourer(avant, apres) {
    const selection = saisie.value.slice(saisie.selectionStart, saisie.selectionEnd);
    const debut = saisie.selectionStart;
    inserer(avant + selection + apres);
    if (!selection) saisie.setSelectionRange(debut + avant.length, debut + avant.length);
  }

  function debutDeLigne(position) {
    return position === 0 ? 0 : saisie.value.lastIndexOf("\n", position - 1) + 1;
  }

  function lignesSelectionnees() {
    const texte = saisie.value;
    const { selectionStart: s, selectionEnd: e } = saisie;
    const debut = debutDeLigne(s);
    // Si la sélection finit juste après un retour à la ligne, la ligne suivante n'est pas incluse.
    const finSelection = e > s && texte[e - 1] === "\n" ? e - 1 : e;
    let fin = texte.indexOf("\n", finSelection);
    if (fin === -1) fin = texte.length;
    return { debut, fin, bloc: texte.slice(debut, fin) };
  }

  function remplacerLignes(transformer) {
    const { debut, fin, bloc } = lignesSelectionnees();
    const nouveau = bloc.split("\n").map(transformer).join("\n");
    saisie.setSelectionRange(debut, fin);
    inserer(nouveau);
    saisie.setSelectionRange(debut, debut + nouveau.length);
  }

  function indenter(inverse) {
    saisie.focus();
    const multiligne = saisie.value.slice(saisie.selectionStart, saisie.selectionEnd).includes("\n");
    if (!inverse && !multiligne) {
      const { debut } = lignesSelectionnees();
      const colonne = saisie.selectionStart - debut;
      inserer(" ".repeat(4 - (colonne % 4)));
      return;
    }
    remplacerLignes((ligne) => (inverse ? ligne.replace(/^ {1,4}/, "") : INDENT + ligne));
  }

  function nouvelleLigne() {
    const avant = saisie.value.slice(debutDeLigne(saisie.selectionStart), saisie.selectionStart);
    let indentation = avant.match(/^\s*/)[0];
    if (/:\s*(#.*)?$/.test(avant)) indentation += INDENT;
    else if (/^\s*(return|pass|break|continue|raise)\b/.test(avant)) indentation = indentation.slice(0, -4);
    inserer("\n" + indentation);
  }

  function commenter() {
    const { bloc } = lignesSelectionnees();
    const toutesCommentees = bloc.split("\n").filter((l) => l.trim()).every((l) => l.trim().startsWith("#"));
    remplacerLignes((ligne) => {
      if (!ligne.trim()) return ligne;
      return toutesCommentees ? ligne.replace(/^(\s*)# ?/, "$1") : ligne.replace(/^(\s*)/, "$1# ");
    });
  }

  saisie.addEventListener("input", changer);
  saisie.addEventListener("keydown", (evt) => {
    const commande = evt.ctrlKey || evt.metaKey;
    if (evt.key === "Tab" && !commande) {
      evt.preventDefault();
      indenter(evt.shiftKey);
    } else if (evt.key === "Enter" && commande) {
      evt.preventDefault();
      if (evt.shiftKey) surEnvoyer(); else surExecuter();
    } else if (evt.key === "Enter" && !evt.shiftKey && !evt.altKey) {
      evt.preventDefault();
      nouvelleLigne();
    } else if (evt.key === "Backspace" && saisie.selectionStart === saisie.selectionEnd) {
      const { debut } = lignesSelectionnees();
      const avant = saisie.value.slice(debut, saisie.selectionStart);
      if (avant.length >= 4 && /^ +$/.test(avant) && avant.length % 4 === 0) {
        evt.preventDefault();
        saisie.setSelectionRange(saisie.selectionStart - 4, saisie.selectionStart);
        inserer("");
      }
    } else if (evt.key === "/" && commande) {
      evt.preventDefault();
      commenter();
    }
  });

  saisie.value = valeur;
  mettreAJour();

  return {
    element: racine,
    get valeur() { return saisie.value; },
    definir(texte) {
      saisie.value = texte;
      mettreAJour();
      surChange(texte);
    },
    marquerLigne(numero) {
      if (!numero) { marque.hidden = true; return; }
      marque.hidden = false;
      marque.style.top = `calc(var(--marge-code) + ${(numero - 1) * hauteurLigne}px)`;
    },
    focus() { saisie.focus(); },
  };
}
