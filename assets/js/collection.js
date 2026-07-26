(function () {
  var ledger = document.getElementById('ledger');
  if (!ledger) return;

  var entries = Array.prototype.slice.call(ledger.querySelectorAll('.entry'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var tally = document.getElementById('tally-count');
  var empty = document.getElementById('empty');
  var sortSelect = document.getElementById('sort');

  var active = { type: [], brand: [] };

  function matches(entry) {
    return Object.keys(active).every(function (facet) {
      var chosen = active[facet];
      return chosen.length === 0 || chosen.indexOf(entry.dataset[facet]) !== -1;
    });
  }

  function apply() {
    var shown = 0;
    entries.forEach(function (entry) {
      var ok = matches(entry);
      entry.hidden = !ok;
      if (ok) shown++;
    });
    tally.textContent = shown;
    empty.hidden = shown !== 0;
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var facet = chip.dataset.facet;
      var value = chip.dataset.value;
      var chosen = active[facet];
      var at = chosen.indexOf(value);

      if (at === -1) { chosen.push(value); } else { chosen.splice(at, 1); }
      chip.setAttribute('aria-pressed', at === -1 ? 'true' : 'false');
      apply();
    });
  });

  var comparators = {
    'acquired-desc': function (a, b) { return b.dataset.acquired - a.dataset.acquired; },
    'acquired-asc': function (a, b) { return a.dataset.acquired - b.dataset.acquired; },
    'brand': function (a, b) { return a.dataset.brandName.localeCompare(b.dataset.brandName, 'ja'); }
  };

  if (sortSelect) {
    sortSelect.addEventListener('change', function () {
      var sorted = entries.slice().sort(comparators[sortSelect.value]);
      sorted.forEach(function (entry) { ledger.insertBefore(entry, empty); });
    });
  }

  apply();
})();
