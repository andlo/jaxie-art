let ALL_ITEMS = [];

const galleryEl = document.getElementById("gallery");
const yearSel = document.getElementById("filter-year");
const monthSel = document.getElementById("filter-month");
const weekSel = document.getElementById("filter-week");
const searchEl = document.getElementById("search");
const countEl = document.getElementById("result-count");

fetch("manifest.json")
  .then(r => r.json())
  .then(data => {
    ALL_ITEMS = data.items || [];
    populateFilters();
    render();
  })
  .catch(() => {
    galleryEl.innerHTML = '<p class="empty-state">Couldn\'t load manifest.json yet — add images to images/ and run the build script.</p>';
  });

function populateFilters() {
  const years = [...new Set(ALL_ITEMS.map(i => i.year))].sort((a, b) => b - a);
  for (const y of years) {
    const opt = document.createElement("option");
    opt.value = y; opt.textContent = y;
    yearSel.appendChild(opt);
  }
  updateMonthOptions();
  yearSel.addEventListener("change", () => { updateMonthOptions(); updateWeekOptions(); render(); });
  monthSel.addEventListener("change", () => { updateWeekOptions(); render(); });
  weekSel.addEventListener("change", render);
  searchEl.addEventListener("input", render);
}
function scoped(upToLevel) {
  // upToLevel: 'year' -> only year filter applies, 'month' -> year+month apply
  const y = yearSel.value;
  const m = monthSel.value;
  return ALL_ITEMS.filter(i => {
    if (y && String(i.year) !== y) return false;
    if (upToLevel === "month" && m && i.month !== m) return false;
    return true;
  });
}

function updateMonthOptions() {
  const current = monthSel.value;
  monthSel.innerHTML = '<option value="">All</option>';
  const months = [...new Map(
    scoped("year").map(i => [i.month, i.monthLabel])
  )].sort((a, b) => b[0].localeCompare(a[0]));
  for (const [val, label] of months) {
    const opt = document.createElement("option");
    opt.value = val; opt.textContent = label;
    monthSel.appendChild(opt);
  }
  if ([...monthSel.options].some(o => o.value === current)) monthSel.value = current;
}

function updateWeekOptions() {
  const current = weekSel.value;
  weekSel.innerHTML = '<option value="">All</option>';
  const weeks = [...new Map(
    scoped("month").map(i => [i.week, i.weekLabel])
  )].sort((a, b) => b[0].localeCompare(a[0]));
  for (const [val, label] of weeks) {
    const opt = document.createElement("option");
    opt.value = val; opt.textContent = label;
    weekSel.appendChild(opt);
  }
  if ([...weekSel.options].some(o => o.value === current)) weekSel.value = current;
}
function render() {
  const y = yearSel.value;
  const m = monthSel.value;
  const w = weekSel.value;
  const q = searchEl.value.trim().toLowerCase();

  const filtered = ALL_ITEMS.filter(i =>
    (!y || String(i.year) === y) &&
    (!m || i.month === m) &&
    (!w || i.week === w) &&
    (!q || i.title.toLowerCase().includes(q))
  );

  countEl.textContent = `${filtered.length} drawing${filtered.length === 1 ? "" : "s"}`;
  galleryEl.innerHTML = "";

  if (filtered.length === 0) {
    galleryEl.innerHTML = '<p class="empty-state">No drawings found.</p>';
    return;
  }

  let lastWeek = null;
  for (const item of filtered) {
    if (item.week !== lastWeek) {
      const heading = document.createElement("h2");
      heading.className = "day-heading";
      heading.textContent = item.weekLabel;
      galleryEl.appendChild(heading);
      lastWeek = item.week;
    }
    galleryEl.appendChild(makeThumb(item));
  }
}
function formatDateLabel(iso) {
  const d = new Date(iso + "T00:00:00");
  return d.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}
function makeThumb(item) {
  const div = document.createElement("div");
  div.className = "thumb";
  div.innerHTML = `<img src="${item.src}" alt="${item.title}" loading="lazy">
    <span class="thumb-date">${item.title}</span>`;
  div.addEventListener("click", () => openLightbox(item));
  return div;
}

const REPO = "andlo/sonias-drawings";
const lightbox = document.getElementById("lightbox");
const lbImg = document.getElementById("lightbox-img");
const lbDate = document.getElementById("lightbox-date");
const lbDownload = document.getElementById("lightbox-download");
const lbRemove = document.getElementById("lightbox-remove");

function openLightbox(item) {
  lbImg.src = item.src;
  lbImg.alt = item.title;
  lbDate.textContent = formatDateLabel(item.date) + " — " + item.title;
  lbDownload.href = item.src;
  lbDownload.download = item.src.split("/").pop();
  const title = encodeURIComponent(`Remove: ${item.title}`);
  const imgUrl = `https://andlo.github.io/sonias-drawings/${item.src}`;
  const body = encodeURIComponent(
    `Please remove this drawing from the gallery.\n\n![preview](${imgUrl})\n\nFile: \`${item.src}\`\nDate: ${item.date}\n\n(Do not edit the File line above — it's used to find and delete the file automatically.)`
  );
  lbRemove.href = `https://github.com/${REPO}/issues/new?title=${title}&body=${body}&labels=remove-request`;
  lightbox.classList.remove("hidden");
}
function closeLightbox() { lightbox.classList.add("hidden"); }

document.getElementById("lightbox-close").addEventListener("click", closeLightbox);
lightbox.addEventListener("click", e => { if (e.target === lightbox) closeLightbox(); });
document.addEventListener("keydown", e => { if (e.key === "Escape") closeLightbox(); });
