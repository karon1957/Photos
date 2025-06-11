fetch('photos.json')
  .then(r => r.json())
  .then(photos => {
    const gallery = document.getElementById('gallery');
    photos.forEach(p => {
      const img = document.createElement('img');
      img.src = p.file;
      img.alt = p.title || '';
      gallery.appendChild(img);
    });
  })
  .catch(err => {
    console.error('Erreur lors du chargement des photos:', err);
  });
