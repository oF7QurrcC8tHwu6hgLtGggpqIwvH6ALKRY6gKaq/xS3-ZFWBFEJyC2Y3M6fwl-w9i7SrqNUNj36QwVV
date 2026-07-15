// ==========================================================
// LootBar 荒野行動マーケット価格一覧
// data/latest.csv を読み込んで一覧表示する。
// pipeline.py が実行のたびに data/history/YYYY-MM-DD.csv と
// 同じ内容を data/latest.csv にも書き出す想定（固定ファイル名）。
// ==========================================================

const CSV_PATH = "data/latest.csv";

// 表示する列（CSV上のヘッダー名 -> 内部キー）
const DISPLAY_COLUMNS = [
  { csvKey: "商品名", key: "name", type: "str" },
  { csvKey: "ジャンル", key: "genre", type: "str" },
  { csvKey: "直近成約価格_円", key: "lastPrice", type: "num" },
  { csvKey: "直近成約日", key: "lastDate", type: "str" },
  { csvKey: "直近30日間の成約数_近似", key: "count30", type: "num" },
  { csvKey: "直近30日間の平均成約価格_円", key: "avgPrice", type: "num" },
  { csvKey: "現在出品最安値_円", key: "minPrice", type: "num" },
  { csvKey: "現在出品数", key: "sellCount", type: "num" },
];

let allRows = [];
let sortState = { key: null, dir: 1 };

init();

async function init() {
  const tbody = document.getElementById("market-tbody");
  try {
    const text = await fetchCsvText(CSV_PATH);
    const { header, rows } = parseCsv(text);
    allRows = rows.map((cols) => rowFromCsv(header, cols));

    if (allRows.length === 0) {
      showState("表示できるデータがありません。");
      return;
    }

    setUpdatedDate(allRows[0].updatedAt);
    render(allRows);

    document.getElementById("search-input").addEventListener("input", onSearch);
    document.querySelectorAll("thead th[data-key]").forEach((th) => {
      th.addEventListener("click", () => onSortClick(th));
    });
  } catch (err) {
    console.error(err);
    showState("データの読み込みに失敗しました。しばらくしてから再読み込みしてください。");
  }
}

async function fetchCsvText(path) {
  // GitHub PagesのCDNキャッシュ対策で毎回クエリを変える
  const res = await fetch(`${path}?t=${Date.now()}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`CSV fetch failed: ${res.status}`);
  const buf = await res.arrayBuffer();
  // utf-8-sig(BOM付き)で書き出されているためBOMを除去
  return new TextDecoder("utf-8").decode(buf).replace(/^\uFEFF/, "");
}

// シンプルなRFC4180準拠CSVパーサ（ダブルクォート・カンマ・改行に対応）
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i++;
        } else {
          inQuotes = false;
        }
      } else {
        field += c;
      }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ",") {
      row.push(field);
      field = "";
    } else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field);
      field = "";
      if (row.some((v) => v !== "")) rows.push(row);
      row = [];
    } else {
      field += c;
    }
  }
  if (field !== "" || row.length) {
    row.push(field);
    rows.push(row);
  }

  const header = rows.shift() || [];
  return { header, rows };
}

function rowFromCsv(header, cols) {
  const get = (name) => {
    const idx = header.indexOf(name);
    return idx === -1 ? "" : (cols[idx] ?? "").trim();
  };

  const record = { updatedAt: get("取得日") };
  for (const col of DISPLAY_COLUMNS) {
    const raw = get(col.csvKey);
    record[col.key] = col.type === "num" ? toNumberOrNull(raw) : raw;
  }
  return record;
}

function toNumberOrNull(v) {
  if (v === "" || v === null || v === undefined) return null;
  const n = Number(v);
  return Number.isNaN(n) ? null : n;
}

function setUpdatedDate(dateStr) {
  document.getElementById("updated-date").textContent = dateStr || "--";
}

function showState(msg) {
  document.getElementById("market-tbody").innerHTML =
    `<tr class="state-row"><td colspan="9">${escapeHtml(msg)}</td></tr>`;
}

function render(rows) {
  const tbody = document.getElementById("market-tbody");
  document.getElementById("result-count").textContent = rows.length.toLocaleString("ja-JP");

  if (rows.length === 0) {
    showState("該当する商品がありません。");
    return;
  }

  const html = rows.map((r, i) => `
    <tr>
      <td class="col-no">${i + 1}</td>
      <td class="col-name">${escapeHtml(r.name)}</td>
      <td class="col-genre">${escapeHtml(r.genre)}</td>
      <td data-type="num">${formatNum(r.lastPrice)}</td>
      <td class="col-date">${escapeHtml(r.lastDate)}</td>
      <td data-type="num">${formatNum(r.count30)}</td>
      <td data-type="num">${formatNum(r.avgPrice)}</td>
      <td data-type="num">${formatNum(r.minPrice)}</td>
      <td data-type="num">${formatNum(r.sellCount)}</td>
    </tr>
  `).join("");

  tbody.innerHTML = html;
}

function formatNum(n) {
  return n === null || n === undefined ? "-" : n.toLocaleString("ja-JP");
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function getFilteredSortedRows() {
  const q = document.getElementById("search-input").value.trim().toLowerCase();
  let rows = allRows;

  if (q) {
    rows = rows.filter((r) =>
      (r.name && r.name.toLowerCase().includes(q)) ||
      (r.genre && r.genre.toLowerCase().includes(q))
    );
  }

  if (sortState.key) {
    const col = DISPLAY_COLUMNS.find((c) => c.key === sortState.key);
    rows = [...rows].sort((a, b) => {
      const av = a[sortState.key];
      const bv = b[sortState.key];
      if (col.type === "num") {
        const an = av === null ? -Infinity : av;
        const bn = bv === null ? -Infinity : bv;
        return (an - bn) * sortState.dir;
      }
      return String(av ?? "").localeCompare(String(bv ?? ""), "ja") * sortState.dir;
    });
  }

  return rows;
}

function onSearch() {
  render(getFilteredSortedRows());
}

function onSortClick(th) {
  const key = th.dataset.key;
  if (key === "no") return; // No.列はソート対象外（表示順の連番）

  if (sortState.key === key) {
    sortState.dir *= -1;
  } else {
    sortState.key = key;
    sortState.dir = 1;
  }

  document.querySelectorAll("thead th").forEach((el) => el.classList.remove("sort-asc", "sort-desc"));
  th.classList.add(sortState.dir === 1 ? "sort-asc" : "sort-desc");

  render(getFilteredSortedRows());
}
