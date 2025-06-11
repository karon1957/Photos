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

fetch('books.json')
  .then(r => r.json())
  .then(books => {
    const list = document.getElementById('books');
    books.forEach(b => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = b.url;
      a.textContent = b.title;
      a.target = '_blank';
      li.appendChild(a);
      list.appendChild(li);
    });
  })
  .catch(err => {
    console.error('Erreur lors du chargement des livres:', err);
  });
