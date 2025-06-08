/* gallery.js  v2.4 – 12 / 06 / 2025 */
document.addEventListener("DOMContentLoaded", () => {

  const root   = document.getElementById("gallery");
  const master = [...root.querySelectorAll(".all-photos a")];    // 10 000 liens cachés
  const grid   = root.querySelector(".gallery-grid");
  const panel  = document.getElementById("filters");

  /* ----------- collecter les facettes ---------------- */
  const F = new Set(), K = new Set();
  master.forEach(a=>{
    F.add(a.dataset.folder);
    a.dataset.keywords.split(",").filter(Boolean).forEach(K.add.bind(K));
  });

  /* ----------- construire le panneau ----------------- */
  panel.innerHTML = `
    <button id="sel">Tout sélectionner</button>
    <button id="des">Tout désélectionner</button><hr>
    <strong>Dossier</strong><br>
      ${[...F].sort().map(f=>`<label><input type="checkbox" class="chk fol" value="${f}"> ${f}</label><br>`).join("")}
    <hr><strong>Mot-clé</strong><br>
    <div style="max-height:60vh;overflow:auto">
      ${[...K].sort((a,b)=>a.localeCompare(b,'fr')).map(k=>`<label><input type="checkbox" class="chk kw" value="${k}"> ${k}</label><br>`).join("")}
    </div>`;

  panel.querySelectorAll(".chk").forEach(cb=>cb.onchange=apply);
  panel.querySelector("#sel").onclick = ()=>{panel.querySelectorAll("input").forEach(c=>c.checked=true); apply();};
  panel.querySelector("#des").onclick = ()=>{panel.querySelectorAll("input").forEach(c=>c.checked=false);apply();};

  /* ----------- filtrage --------------------------------- */
  function apply(){
    const onF = new Set([...panel.querySelectorAll(".fol:checked")].map(c=>c.value));
    const onK = new Set([...panel.querySelectorAll(".kw:checked" )].map(c=>c.value));

    /* → si AUCUN filtre actif, on n’affiche rien */
    if (!onF.size && !onK.size){
      grid.innerHTML = "";   return;
    }

    const list = master.filter(a=>{
      const okF = !onF.size || onF.has(a.dataset.folder);
      const okK = !onK.size || a.dataset.keywords.split(",").some(k=>onK.has(k));
      return okF && okK;
    });

    grid.innerHTML = "";
    list.forEach(a=>{
      const img = new Image(); img.src = a.href; img.alt = a.dataset.title; img.loading="lazy";
      const link = a.cloneNode(); link.appendChild(img); link.setAttribute("data-lightbox","gallery");
      grid.appendChild(link);
    });
  }

  /* grille vide au démarrage */
  apply();
});
