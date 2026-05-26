function isUnused(s) {
  if (s.fill && s.fill.forced && s.fill.color && s.fill.color.type === 'solid') {
    return s.fill.color.r === 255 && s.fill.color.g === 0 && s.fill.color.b === 255;
  }
  return false;
}

function getSampleText(name) {
  if (SAMPLE_TEXT_BY_NAME[name] !== undefined) return SAMPLE_TEXT_BY_NAME[name];
  if (name.startsWith('Intensity')) return 'Texto';
  if (name.startsWith('User_Defined_')) return '';
  if (name.startsWith('Alarm_')) return name.replace('Alarm_', '').replace(/_/g, ' ');
  return name.replace(/_/g, ' ');
}

function pill(letter, on) {
  const cls = on ? (letter === 'B' ? 'blink-on' : 'on') : '';
  return '<span class="pill ' + cls + '">' + letter + '</span>';
}

function colorToCSS(c) {
  if (!c) return 'transparent';
  if (c.type === 'pattern') {
    return 'repeating-linear-gradient(45deg, ' + c.fore + ' 0 2px, ' + c.back + ' 2px 6px)';
  }
  return c.css;
}

function renderPreview(s, unused) {
  const hasText = s.text.forced;
  const hasFill = s.fill.forced;
  const hasLine = s.line.forced;
  const hasOutline = s.outline.forced;
  const isAvailable = s.category === 'UserDefined' && !hasText && !hasFill && !hasLine && !hasOutline;

  const animId = 'bk' + s.id;
  let extraStyle = '';

  // Fill blink: animate background-color between c1 and c2
  let bgStyle = '';
  if (hasFill && s.fill.color) {
    const c1 = s.fill.color.type === 'pattern' ? colorToCSS(s.fill.color) : s.fill.color.css;
    if (s.fill.blink && s.fill.blink.color) {
      const c2 = s.fill.blink.color.css;
      extraStyle += '@keyframes ' + animId + 'f{0%,49%{background:' + c1 + '}50%,100%{background:' + c2 + '}} ';
      bgStyle = 'background:' + c1 + ';animation:' + animId + 'f 1.4s step-end infinite;';
    } else {
      bgStyle = 'background:' + c1 + ';';
    }
  }

  // Line/Outline blink: animate border-color between c1 and c2
  let borderStyle = '';
  let borderBase = '';
  let borderBlink2 = '';
  let borderWeight = 1;
  if (hasOutline && s.outline.color) {
    borderWeight = s.outline.weight || 1;
    borderBase = colorToCSS(s.outline.color);
    if (s.outline.blink && s.outline.blink.color) borderBlink2 = s.outline.blink.color.css;
  } else if (hasLine && s.line.color) {
    borderWeight = s.line.weight || 1;
    borderBase = s.line.color.type === 'pattern' ? s.line.color.fore : s.line.color.css;
    if (s.line.blink && s.line.blink.color) borderBlink2 = s.line.blink.color.css;
  }
  if (borderBase) {
    if (borderBlink2) {
      extraStyle += '@keyframes ' + animId + 'b{0%,49%{border-color:' + borderBase + '}50%,100%{border-color:' + borderBlink2 + '}} ';
      borderStyle = 'border:' + borderWeight + 'px solid ' + borderBase + ';animation:' + animId + 'b 1.4s step-end infinite;';
      if (bgStyle.includes('animation:')) {
        // Merge both animations
        bgStyle = bgStyle.replace('animation:', 'animation:' + animId + 'b 1.4s step-end infinite,');
        borderStyle = 'border:' + borderWeight + 'px solid ' + borderBase + ';';
      }
    } else {
      borderStyle = 'border:' + borderWeight + 'px solid ' + borderBase + ';';
    }
  }

  const styleTag = extraStyle ? '<style>' + extraStyle + '</style>' : '';

  let textHTML = '';
  if (unused) {
    textHTML = '<span class="preview-text" style="color:#fff;font-weight:700;font-size:11px;text-transform:uppercase;letter-spacing:0.05em;">EN DESUSO</span>';
  } else if (isAvailable) {
    textHTML = '<span class="available-msg">Disponible</span>';
  } else if (hasText) {
    const t = s.text;
    const fontFamily = t.font ? "'" + t.font + "', sans-serif" : 'inherit';
    const size = t.size ? t.size + 'pt' : 'inherit';
    const weight = t.bold ? '700' : '400';
    const italic = t.italic ? 'italic' : 'normal';
    const color = (t.color && t.color.css) ? t.color.css : 'currentColor';
    const sample = getSampleText(s.name);
    if (sample === '') {
      textHTML = '<span class="empty-msg">(sin muestra)</span>';
    } else {
      textHTML = '<span class="preview-text" style="font-family:' + fontFamily + ';font-size:' + size + ';font-weight:' + weight + ';font-style:' + italic + ';color:' + color + ';">' + sample + '</span>';
    }
  } else {
    textHTML = '<span class="empty-msg">—</span>';
  }

  return styleTag + '<div class="preview" style="' + bgStyle + ' ' + borderStyle + '">' + textHTML + '</div>';
}
function toHex(color) {
  if (!color || color.type !== 'solid') return '';
  const h = v => v.toString(16).padStart(2,'0').toUpperCase();
  return '#' + h(color.r) + h(color.g) + h(color.b);
}

function colorLine(color) {
  if (!color || color.type !== 'solid') return '';
  return '<span class="color-rgb">' + color.css + '</span><span class="color-hex" onclick="copyHex(this)" title="Copiar hex">' + toHex(color) + '</span>';
}

function copyHex(el) {
  navigator.clipboard.writeText(el.textContent).then(() => {
    const orig = el.textContent;
    el.textContent = '✓';
    setTimeout(() => el.textContent = orig, 900);
  });
}

function renderMeta(s) {
  const lines = [];
  if (s.text.forced && s.text.font) {
    lines.push('<div class="meta-row"><span class="meta-label">FONT</span><span class="meta-val">' + s.text.font + ' ' + s.text.size + 'pt' + (s.text.bold ? ' bold' : '') + '</span></div>');
  }
  if (s.text.forced && s.text.color) {
    lines.push('<div class="meta-row"><span class="meta-label">COL</span><span class="meta-val meta-color">' + colorLine(s.text.color) + '</span></div>');
  }
  if (s.fill.forced && s.fill.color) {
    if (s.fill.color.type === 'pattern') {
      lines.push('<div class="meta-row"><span class="meta-label">FILL</span><span class="meta-val">pattern ' + s.fill.color.hatch + '</span></div>');
    } else {
      lines.push('<div class="meta-row"><span class="meta-label">FILL</span><span class="meta-val meta-color">' + colorLine(s.fill.color) + '</span></div>');
      if (s.fill.blink && s.fill.blink.color) {
        lines.push('<div class="meta-row"><span class="meta-label">↔</span><span class="meta-val meta-color">' + colorLine(s.fill.blink.color) + '</span></div>');
      }
    }
  }
  if (s.line.forced) {
    const chip = s.line.color && s.line.color.type === 'solid' ? colorLine(s.line.color) : (s.line.color ? 'pattern' : '');
    lines.push('<div class="meta-row"><span class="meta-label">LINE</span><span class="meta-val meta-right">' + s.line.weight + 'px ' + chip + '</span></div>');
    if (s.line.blink && s.line.blink.color) {
      lines.push('<div class="meta-row"><span class="meta-label">↔</span><span class="meta-val meta-color">' + colorLine(s.line.blink.color) + '</span></div>');
    }
  }
  if (s.outline.forced) {
    const chip = s.outline.color && s.outline.color.type === 'solid' ? colorLine(s.outline.color) : '';
    lines.push('<div class="meta-row"><span class="meta-label">OUT</span><span class="meta-val meta-right">' + s.outline.weight + 'px ' + chip + '</span></div>');
  }
  return '<div class="meta">' + lines.join('') + '</div>';
}


function renderCard(s) {
  const unused = isUnused(s);
  const unusedClass = unused ? ' unused' : '';
  const unusedTag = unused ? ' <span class="unused-tag">desuso</span>' : '';
  const usageHTML = s.usage ? '<div class="card-usage">' + s.usage + '</div>' : '';
  const blinkActive = (s.text.forced && s.text.blink) || (s.fill.forced && s.fill.blink) || (s.line.forced && s.line.blink) || (s.outline.forced && s.outline.blink);
  const pills = '<div class="pills">' +
    pill('T', s.text.forced) +
    pill('F', s.fill.forced) +
    pill('L', s.line.forced) +
    pill('O', s.outline.forced) +
    pill('B', blinkActive) +
    '</div>';
  return '<div class="card' + unusedClass + '" data-cat="' + s.category + '" data-text="' + s.text.forced + '" data-fill="' + s.fill.forced + '" data-line="' + s.line.forced + '" data-outline="' + s.outline.forced + '">' +
    '<div class="card-header">' +
      '<div>' +
        '<div class="card-name">' + s.name + unusedTag + '</div>' +
        usageHTML +
      '</div>' +
      '<div class="card-id">#' + s.id + '</div>' +
    '</div>' +
    pills +
    renderPreview(s, unused) +
    renderMeta(s) +
  '</div>';
}

function render() {
  const main = document.getElementById('main');
  const groups = {};
  STYLES.forEach(s => {
    const key = s.category + '|' + s.subgroup;
    if (!groups[key]) groups[key] = [];
    groups[key].push(s);
  });
  const catOrder = { HMI: 0, Alarm: 1, UserDefined: 2 };
  const sortedKeys = Object.keys(groups).sort((a, b) => {
    const catA = a.split('|')[0];
    const catB = b.split('|')[0];
    if (catOrder[catA] !== catOrder[catB]) return catOrder[catA] - catOrder[catB];
    return a.localeCompare(b);
  });
  let html = '';
  sortedKeys.forEach(key => {
    const parts = key.split('|');
    const cat = parts[0];
    const subgroup = parts[1];
    let tagClass = 'cat-tag';
    let tagText = cat;
    if (cat === 'Alarm') { tagClass += ' alarm'; tagText = 'ALM'; }
    else if (cat === 'UserDefined') { tagClass += ' userdefined'; tagText = 'USR'; }
    else { tagText = 'HMI'; }
    html += '<div class="subgroup" data-cat="' + cat + '">' +
      '<div class="subgroup-title"><span class="' + tagClass + '">' + tagText + '</span>' + subgroup + '</div>' +
      '<div class="grid">' +
        groups[key].map(renderCard).join('') +
      '</div>' +
    '</div>';
  });
  main.innerHTML = html;
  applyFilters();
}

let filterCat = 'all';
let filterForce = 'all';

function applyFilters() {
  document.querySelectorAll('.subgroup').forEach(sg => {
    const cards = sg.querySelectorAll('.card');
    let visible = 0;
    cards.forEach(card => {
      const catMatch = filterCat === 'all' || card.dataset.cat === filterCat;
      let forceMatch = true;
      if (filterForce !== 'all') {
        forceMatch = card.dataset[filterForce] === 'true';
      }
      const show = catMatch && forceMatch;
      card.style.display = show ? '' : 'none';
      if (show) visible++;
    });
    sg.style.display = visible > 0 ? '' : 'none';
  });
}

document.querySelectorAll('[data-cat]').forEach(btn => {
  if (btn.tagName === 'BUTTON') {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-cat]').forEach(b => {
        if (b.tagName === 'BUTTON') b.classList.remove('active');
      });
      btn.classList.add('active');
      filterCat = btn.dataset.cat;
      applyFilters();
    });
  }
});
document.querySelectorAll('[data-force]').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-force]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filterForce = btn.dataset.force;
    applyFilters();
  });
});

function downloadXML() {
  const a = document.createElement('a');
  a.href = '../styles/Standard_Style.xml';
  a.download = 'Standard_Style.xml';
  a.click();
}

render();
document.getElementById("total-count").textContent = STYLES.length;
