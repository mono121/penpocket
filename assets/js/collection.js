(function () {
  var ledger = document.getElementById('ledger');
  if (!ledger) return;

  var entries = Array.prototype.slice.call(ledger.querySelectorAll('.entry'));
  var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.filters__group'));
  var tally = document.getElementById('tally-count');
  var empty = document.getElementById('empty');
  var sortSelect = document.getElementById('sort');
  var resetButton = document.getElementById('reset');
  var narrow = window.matchMedia('(max-width: 640px)');

  var active = { type: [], brand: [] };

  function matches(entry) {
    return Object.keys(active).every(function (facet) {
      var chosen = active[facet];
      return chosen.length === 0 || chosen.indexOf(entry.dataset[facet]) !== -1;
    });
  }

  function heads() {
    groups.forEach(function (group) {
      var state = group.querySelector('.filters__state');
      if (!state) return;
      var chosen = active[group.dataset.facet] || [];
      var total = group.querySelectorAll('.chip').length;
      state.textContent = chosen.length ? chosen.length + '件選択' : total + '件';
    });
    if (resetButton) {
      resetButton.hidden = !Object.keys(active).some(function (facet) { return active[facet].length; });
    }
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
    heads();
  }

  function setOpen(group, open) {
    var toggle = group.querySelector('.filters__toggle');
    var box = group.querySelector('.filters__chips');
    if (!toggle || !box) return;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    box.hidden = !open;
  }

  // 狭い画面では未選択のグループを畳む。選択中のものは開いたままにして、
  // 何で絞り込んでいるかが畳まれて見えなくなることを避ける。
  function syncGroups() {
    groups.forEach(function (group) {
      var chosen = active[group.dataset.facet] || [];
      setOpen(group, !narrow.matches || chosen.length > 0);
    });
  }

  groups.forEach(function (group) {
    var toggle = group.querySelector('.filters__toggle');
    if (!toggle) return;
    toggle.addEventListener('click', function () {
      setOpen(group, toggle.getAttribute('aria-expanded') !== 'true');
    });
  });

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

  if (resetButton) {
    resetButton.addEventListener('click', function () {
      Object.keys(active).forEach(function (facet) { active[facet].length = 0; });
      chips.forEach(function (chip) { chip.setAttribute('aria-pressed', 'false'); });
      apply();
    });
  }

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

  if (narrow.addEventListener) {
    narrow.addEventListener('change', syncGroups);
  } else if (narrow.addListener) {
    narrow.addListener(syncGroups);
  }

  apply();
  syncGroups();
})();
