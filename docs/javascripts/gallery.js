/* gallery.js  v2.6 — 12 / 06 / 2025
   • Affiche le nom de fichier (caption) sous chaque miniature
   • Quatre sections de filtre : Dossier, Mot-clé, Année, Mois
   • Grille vide au chargement
*/

document.addEventListener("DOMContentLoaded", () => {

  // 1) Références DOM
  const root   = document.getElementById("gallery");
  const master = Array.from(root.querySelectorAll(".all-photos a")); // tous les <a> cachés
  const grid   = root.querySelector(".gallery-grid");
  const panel  = document.getElementById("filters");

  // 2) Construire les sets uniques pour chaque facette
  const setF = new Set(), setK = new Set(), setY = new Set(), setM = new Set();

  master.forEach(a => {
    // Dossier
    setF.add(a.dataset.folder);

    // Mots-clés : "clé1,clé2,clé3"
    a.dataset.keywords.split(",").filter(Boolean).forEach(k => setK.add(k));

    // Date : "YYYY-MM-DD"
    const d = a.dataset.date;
    if (d) {
      setY.add(d.slice(0, 4));   // ex. "2023"
      setM.add(d.slice(0, 7));   // ex. "2023-03"
    }
  });

  // 3) Générer le HTML du panneau avec quatre sections
  panel.innerHTML = `
    <button id="sel">Tout sélectionner</button>
    <button id="des">Tout désélectionner</button>
    <hr>

    <strong>Dossier</strong><br>
    ${[...setF].sort().map(f =>
      `<label><input type="checkbox" class="chk fol" value="${f}"> ${f}</label><br>`
    ).join("")}

    <hr><strong>Mot-clé</strong><br>
    <div style="max-height:50vh; overflow:auto">
      ${[...setK].sort((a, b) => a.localeCompare(b, 'fr')).map(k =>
        `<label><input type="checkbox" class="chk kw" value="${k}"> ${k}</label><br>`
      ).join("")}
    </div>

    <hr><strong>Année</strong><br>
    ${[...setY].sort().map(y =>
      `<label><input type="checkbox" class="chk yr" value="${y}"> ${y}</label><br>`
    ).join("")}

    <hr><strong>Mois</strong><br>
    <div style="max-height:25vh; overflow:auto">
      ${[...setM].sort().map(mo =>
        `<label><input type="checkbox" class="chk mo" value="${mo}"> ${mo}</label><br>`
      ).join("")}
    </div>
  `;

  // 4) Écouteurs sur chaque case à cocher + boutons globaux
  panel.querySelectorAll(".chk").forEach(cb => cb.onchange = updateGrid);
  panel.querySelector("#sel").onclick = () => {
    panel.querySelectorAll("input[type=checkbox]").forEach(c => c.checked = true);
    updateGrid();
  };
  panel.querySelector("#des").onclick = () => {
    panel.querySelectorAll("input[type=checkbox]").forEach(c => c.checked = false);
    updateGrid();
  };

  // 5) Fonction de filtrage
  function updateGrid() {
    const onF = new Set([...panel.querySelectorAll(".fol:checked")].map(c => c.value));
    const onK = new Set([...panel.querySelectorAll(".kw:checked")].map(c => c.value));
    const onY = new Set([...panel.querySelectorAll(".yr:checked")].map(c => c.value));
    const onM = new Set([...panel.querySelectorAll(".mo:checked")].map(c => c.value));

    // Si aucun filtre n’est coché → grille vide
    if (!onF.size && !onK.size && !onY.size && !onM.size) {
      grid.innerHTML = "";
      return;
    }

    // Filtrer la liste complète
    const filtered = master.filter(a => {
      const folderOK   = !onF.size || onF.has(a.dataset.folder);
      const kwsArr     = a.dataset.keywords.split(",").filter(Boolean);
      const keywordsOK = !onK.size || kwsArr.some(k => onK.has(k));
      const d          = a.dataset.date || "";
      const yearOK     = !onY.size || onY.has(d.slice(0, 4));
      const monthOK    = !onM.size || onM.has(d.slice(0, 7));
      return folderOK && keywordsOK && yearOK && monthOK;
    });

    // Reconstruire dynamiquement la grille
    grid.innerHTML = "";  // vider
    filtered.forEach(a => {
      // a) Créer l’image
      const img = new Image();
      img.src = a.href;
      img.alt = a.dataset.title;
      img.loading = "lazy";

      // b) Créer une nouvelle balise <a> clonée avec tout son contenu
      const link = a.cloneNode(true);

      // c) Vider link (on va réinsérer caption et img dans le bon ordre)
      link.innerHTML = "";

      // d) Ajouter img
      link.appendChild(img);

      // e) Ajouter le caption (span.captions déjà présent dans a)
      const cap = document.createElement("div");
      cap.className = "caption";
      cap.textContent = a.dataset.title;
      link.appendChild(cap);

      // f) Attribuer la lightbox
      link.setAttribute("data-lightbox", "gallery");

      // g) Enfin, insérer dans la grille
      grid.appendChild(link);
    });
  }

  // 6) Appel initial : grille vide
  updateGrid();
});
