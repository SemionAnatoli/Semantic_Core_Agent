"""
HTML-дашборд — топовый визуальный отчёт.
Анимации, glassmorphism, интерактивность, Charts.js, sidebar.
"""
from pathlib import Path
from datetime import datetime


def generate_html_report(state: dict, output_path: str = "data/output/report.html") -> str:
    Path("data/output").mkdir(parents=True, exist_ok=True)

    clusters    = state.get("clusters", [])
    site_url    = state.get("site_url", "—")
    business    = state.get("business_description", "—")
    geo         = state.get("geo", "—")
    raw_count   = len(state.get("raw_keywords", []))
    clean_count = len(state.get("cleaned_keywords", []))
    generated   = datetime.now().strftime("%d.%m.%Y  %H:%M")
    issues      = state.get("cannibalization_issues", [])
    briefs      = state.get("briefs", [])

    high   = [c for c in clusters if c["priority_score"] >= 70]
    medium = [c for c in clusters if 40 <= c["priority_score"] < 70]
    low    = [c for c in clusters if c["priority_score"] < 40]
    create = [c for c in clusters if c["action"] == "create_page"]
    update = [c for c in clusters if c["action"] == "update_page"]
    blog   = [c for c in clusters if c["action"] == "create_blog"]
    skip   = [c for c in clusters if c["action"] == "skip"]

    ACTION_LABELS = {
        "create_page": "Создать страницу",
        "update_page": "Обновить страницу",
        "create_blog": "Написать статью",
        "add_faq":     "Добавить в FAQ",
        "skip":        "Не брать",
    }
    ACTION_COLORS = {
        "create_page": "#ff6b6b",
        "update_page": "#ffd93d",
        "create_blog": "#4ecdc4",
        "add_faq":     "#c77dff",
        "skip":        "#555f6e",
    }
    INTENT_LABELS = {
        "commercial":    "🛒 Коммерческий",
        "transactional": "💳 Транзакционный",
        "informational": "📖 Информационный",
        "comparison":    "⚖️ Сравнительный",
        "navigational":  "🧭 Навигационный",
        "local":         "📍 Локальный",
        "problem_based": "🔧 Проблемный",
    }

    # ── Chart данные ─────────────────────────────────────────
    intent_stats: dict[str,int] = {}
    for c in clusters:
        i = c.get("intent","?")
        intent_stats[i] = intent_stats.get(i,0) + 1

    donut_labels = list(intent_stats.keys())
    donut_values = list(intent_stats.values())
    PALETTE = ["#ff6b6b","#ffd93d","#4ecdc4","#c77dff","#74b9ff","#fd79a8","#55efc4","#fdcb6e"]
    donut_colors = PALETTE[:len(donut_labels)]

    priority_names  = [c["name"][:20] for c in clusters[:8]]
    priority_scores = [c["priority_score"] for c in clusters[:8]]
    priority_colors = [
        "#ff6b6b" if s >= 70 else "#ffd93d" if s >= 40 else "#555f6e"
        for s in priority_scores
    ]

    import json as _json
    dl_js  = _json.dumps(donut_labels)
    dv_js  = _json.dumps(donut_values)
    dc_js  = _json.dumps(donut_colors)
    pn_js  = _json.dumps(priority_names)
    ps_js  = _json.dumps(priority_scores)
    pc_js  = _json.dumps(priority_colors)

    # ── Таблица строки ───────────────────────────────────────
    rows_html = ""
    for rank, c in enumerate(clusters, 1):
        score      = c["priority_score"]
        action     = c.get("action","skip")
        acol       = ACTION_COLORS.get(action,"#555f6e")
        albl       = ACTION_LABELS.get(action, action)
        ilbl       = INTENT_LABELS.get(c.get("intent",""), c.get("intent",""))
        cannibal   = c.get("cannibalization_risk","low")

        pct = min(int(score),100)
        if score >= 70:   scol,sico = "#ff6b6b","🔴"
        elif score >= 40: scol,sico = "#ffd93d","🟡"
        else:             scol,sico = "#555f6e","⚫"

        kw_pills = "".join(f'<span class="pill">{kw}</span>' for kw in c.get("keywords",[])[:5])
        extra = len(c.get("keywords",[])) - 5
        if extra > 0: kw_pills += f'<span class="pill pm">+{extra}</span>'

        cbadge = '<span class="cbadge">⚠️ риск</span>' if cannibal == "high" else ""

        rows_html += f"""<tr>
          <td class="td-r">#{rank}</td>
          <td><div class="cn">{c["name"]}{cbadge}</div><div class="cm">{c["main_keyword"]}</div></td>
          <td><div class="pw">{kw_pills}</div></td>
          <td><span class="ichip">{ilbl}</span></td>
          <td><code class="uc">{c.get("recommended_url","—")}</code></td>
          <td><span class="achip" style="color:{acol};background:{acol}15;border:1px solid {acol}35">{albl}</span></td>
          <td><div class="sw"><div class="sn" style="color:{scol}">{sico} {score}</div>
            <div class="st"><div class="sf" style="width:{pct}%;background:{scol}"></div></div></div></td>
        </tr>"""

    # ── Топ-3 ────────────────────────────────────────────────
    top3     = sorted(clusters, key=lambda c: c["priority_score"], reverse=True)[:3]
    medals   = ["🥇","🥈","🥉"]
    glow_col = ["#ff6b6b","#ffd93d","#4ecdc4"]
    top3_html = ""
    for i, c in enumerate(top3):
        ac   = ACTION_COLORS.get(c.get("action","skip"),"#555")
        alb  = ACTION_LABELS.get(c.get("action","skip"),"")
        gcol = glow_col[i]
        top3_html += f"""
        <div class="tc" style="--glow:{gcol}">
          <div class="tc-glow"></div>
          <div class="tc-medal">{medals[i]}</div>
          <div class="tc-score" style="color:{gcol}">{c['priority_score']}</div>
          <div class="tc-label">баллов</div>
          <div class="tc-name">{c['name']}</div>
          <div class="tc-url">{c.get('recommended_url','—')}</div>
          <div class="tc-cnt">{len(c.get('keywords',[]))} запросов</div>
          <div class="tc-act" style="color:{ac};background:{ac}18;border:1px solid {ac}40">{alb}</div>
        </div>"""

    # ── Каннибализация ───────────────────────────────────────
    sev_map = {"critical":("#ff6b6b","КРИТИЧНО"),"high":("#ffd93d","ВЫСОКИЙ"),"medium":("#4ecdc4","СРЕДНИЙ")}
    if issues:
        can_html = ""
        for iss in issues[:6]:
            col,lbl = sev_map.get(iss.get("severity","medium"),("#aaa","—"))
            can_html += f"""
            <div class="iss" style="border-left:3px solid {col}">
              <span class="iss-b" style="background:{col}20;color:{col}">{lbl}</span>
              <span class="iss-t">{iss.get('type','').replace('_',' ').upper()}</span>
              <div class="iss-txt">{iss.get('recommendation','')}</div>
            </div>"""
    else:
        can_html = '<div class="ok-box">✅ Каннибализация не обнаружена — все кластеры чисты</div>'

    # ── Бриф карточки ────────────────────────────────────────
    br_html = ""
    for b in briefs[:4]:
        sl = "".join(f"<li>{s}</li>" for s in b.get("structure",[])[:5])
        lp = "".join(f'<span class="lp">{w}</span>' for w in b.get("lsi_words",[]))
        ic = INTENT_LABELS.get(b.get("intent",""),b.get("intent",""))
        br_html += f"""
        <div class="br">
          <div class="br-h">
            <span class="br-name">{b['cluster']}</span>
            <span class="br-ic">{ic}</span>
          </div>
          <div class="br-body">
            <div class="br-f">
              <div class="br-l">Title <span class="br-len">{len(b.get('title',''))} симв.</span></div>
              <div class="br-v">{b.get('title','—')}</div>
            </div>
            <div class="br-f">
              <div class="br-l">H1</div>
              <div class="br-v">{b.get('h1','—')}</div>
            </div>
            <div class="br-f br-full">
              <div class="br-l">Meta Description <span class="br-len">{len(b.get('description',''))} симв.</span></div>
              <div class="br-v">{b.get('description','—')}</div>
            </div>
            <div class="br-f">
              <div class="br-l">Структура страницы</div>
              <ul class="br-s">{sl}</ul>
            </div>
            <div class="br-f">
              <div class="br-l">LSI-слова</div>
              <div>{lp if lp else '<span style="color:#555">—</span>'}</div>
            </div>
          </div>
        </div>"""

    # ── Счётчики для JS анимации ──────────────────────────────
    counters = _json.dumps([
        raw_count, clean_count, len(clusters),
        len(high), len(medium), len(create), len(update), len(blog)
    ])

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Семантическое ядро — {site_url}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root{{
  --bg:#060810; --s1:#0d1117; --s2:#131720; --s3:#1a1f2e;
  --br:#1e2535; --br2:#252d40;
  --tx:#e2e8f8; --mu:#4a5568; --mu2:#6b7a8d;
  --ac:#6366f1; --ac2:#818cf8;
  --r:#ff6b6b; --y:#ffd93d; --g:#4ecdc4; --p:#c77dff; --b:#74b9ff;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--tx);
  min-height:100vh;overflow-x:hidden}}
::-webkit-scrollbar{{width:5px;height:5px}}
::-webkit-scrollbar-track{{background:var(--s1)}}
::-webkit-scrollbar-thumb{{background:var(--br2);border-radius:3px}}

/* ═══════════════ PARTICLES BG ═══════════════ */
#particles{{position:fixed;top:0;left:0;width:100%;height:100%;
  pointer-events:none;z-index:0;overflow:hidden}}
.pt{{position:absolute;border-radius:50%;animation:float linear infinite}}
@keyframes float{{0%{{transform:translateY(100vh) scale(0);opacity:0}}
  10%{{opacity:1}}90%{{opacity:.3}}100%{{transform:translateY(-100px) scale(1);opacity:0}}}}

/* ═══════════════ SIDEBAR ═══════════════ */
.sidebar{{position:fixed;left:0;top:0;height:100vh;width:220px;
  background:var(--s1);border-right:1px solid var(--br);
  z-index:100;display:flex;flex-direction:column;padding:24px 0}}
.sb-logo{{padding:0 20px 24px;border-bottom:1px solid var(--br)}}
.sb-logo-icon{{font-size:24px;margin-bottom:4px}}
.sb-logo-title{{font-size:13px;font-weight:800;color:var(--tx);letter-spacing:.5px}}
.sb-logo-sub{{font-size:11px;color:var(--mu2);margin-top:2px}}
.sb-nav{{padding:16px 0;flex:1}}
.sb-item{{display:flex;align-items:center;gap:10px;padding:10px 20px;
  font-size:13px;color:var(--mu2);cursor:pointer;transition:.2s;
  border-left:2px solid transparent;text-decoration:none}}
.sb-item:hover,.sb-item.active{{color:var(--tx);background:var(--s2);
  border-left-color:var(--ac)}}
.sb-item .ico{{font-size:16px;width:20px;text-align:center}}
.sb-footer{{padding:16px 20px;border-top:1px solid var(--br);
  font-size:11px;color:var(--mu);line-height:1.6}}

/* ═══════════════ MAIN ═══════════════ */
.main{{margin-left:220px;position:relative;z-index:1}}

/* ═══════════════ HERO ═══════════════ */
.hero{{
  min-height:280px;padding:56px 56px 48px;
  background:linear-gradient(135deg,#0d1a3a 0%,#0a0f1e 50%,#0d0810 100%);
  border-bottom:1px solid var(--br);position:relative;overflow:hidden;
}}
.hero-orb{{position:absolute;border-radius:50%;filter:blur(80px);pointer-events:none}}
.orb1{{width:400px;height:400px;top:-100px;right:-50px;
  background:radial-gradient(circle,#6366f130,transparent 70%)}}
.orb2{{width:300px;height:300px;bottom:-80px;left:200px;
  background:radial-gradient(circle,#ff6b6b18,transparent 70%)}}
.hero-badge{{display:inline-flex;align-items:center;gap:6px;
  background:var(--ac)15;border:1px solid var(--ac)40;color:var(--ac2);
  padding:5px 14px;border-radius:20px;font-size:11px;font-weight:700;
  letter-spacing:1px;text-transform:uppercase;margin-bottom:16px}}
.hero-badge::before{{content:'';width:6px;height:6px;background:var(--ac);
  border-radius:50%;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.4;transform:scale(.8)}}}}
.hero h1{{font-size:36px;font-weight:900;line-height:1.15;
  background:linear-gradient(135deg,#fff 0%,#818cf8 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;margin-bottom:8px}}
.hero-site{{font-size:20px;font-weight:700;color:var(--ac2);margin-bottom:12px}}
.hero-desc{{font-size:14px;color:var(--mu2);max-width:600px;line-height:1.6}}
.hero-tags{{display:flex;gap:10px;margin-top:24px;flex-wrap:wrap}}
.htag{{background:var(--s3);border:1px solid var(--br2);padding:6px 14px;
  border-radius:20px;font-size:12px;color:var(--mu2)}}
.htag b{{color:var(--tx)}}

/* ═══════════════ CONTENT ═══════════════ */
.content{{padding:40px 48px;max-width:1200px}}
.sec{{margin-bottom:48px}}
.sec-hd{{display:flex;align-items:center;gap:12px;margin-bottom:24px}}
.sec-ico{{font-size:22px}}
.sec-ttl{{font-size:18px;font-weight:800;color:var(--tx)}}
.sec-sub{{font-size:13px;color:var(--mu2);margin-left:auto}}

/* ═══════════════ STAT CARDS ═══════════════ */
.sg{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
@media(max-width:900px){{.sg{{grid-template-columns:repeat(2,1fr)}}}}
.sc{{
  background:var(--s2);border:1px solid var(--br);border-radius:16px;
  padding:22px 20px;position:relative;overflow:hidden;
  transition:transform .25s,border-color .25s,box-shadow .25s;cursor:default;
}}
.sc:hover{{transform:translateY(-4px);border-color:var(--br2);
  box-shadow:0 20px 40px #00000040}}
.sc-glow{{position:absolute;top:0;right:0;width:80px;height:80px;
  border-radius:0 16px 0 80px;opacity:.06}}
.sc-n{{font-size:38px;font-weight:900;line-height:1;
  background:linear-gradient(135deg,var(--col1) 0%,var(--col2) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text}}
.sc-l{{font-size:12px;color:var(--mu2);margin-top:8px;font-weight:500;
  text-transform:uppercase;letter-spacing:.6px}}
.sc-bar{{margin-top:14px;background:var(--br);border-radius:3px;height:3px}}
.sc-bar-f{{height:3px;border-radius:3px;background:linear-gradient(90deg,var(--col1),var(--col2))}}

/* ═══════════════ TOP-3 ═══════════════ */
.tg{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
@media(max-width:900px){{.tg{{grid-template-columns:1fr}}}}
.tc{{
  background:var(--s2);border:1px solid var(--br);border-radius:20px;
  padding:28px 24px;position:relative;overflow:hidden;
  transition:transform .25s,box-shadow .25s;
}}
.tc:hover{{transform:translateY(-6px);box-shadow:0 24px 60px #00000050}}
.tc-glow{{position:absolute;top:-40px;right:-40px;width:160px;height:160px;
  border-radius:50%;background:radial-gradient(circle,var(--glow)20,transparent 70%);
  pointer-events:none}}
.tc-medal{{font-size:30px;margin-bottom:12px}}
.tc-score{{font-size:52px;font-weight:900;line-height:1}}
.tc-label{{font-size:11px;color:var(--mu2);text-transform:uppercase;
  letter-spacing:1px;margin-bottom:14px;margin-top:2px}}
.tc-name{{font-size:16px;font-weight:700;color:#fff;margin-bottom:6px;line-height:1.3}}
.tc-url{{font-size:12px;font-family:'Courier New',monospace;color:var(--b);
  margin-bottom:6px}}
.tc-cnt{{font-size:12px;color:var(--mu2);margin-bottom:14px}}
.tc-act{{display:inline-block;padding:5px 14px;border-radius:8px;
  font-size:12px;font-weight:700}}

/* ═══════════════ CHARTS ═══════════════ */
.cg{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:900px){{.cg{{grid-template-columns:1fr}}}}
.cb{{background:var(--s2);border:1px solid var(--br);border-radius:20px;padding:28px}}
.cb h3{{font-size:14px;font-weight:700;color:var(--mu2);
  text-transform:uppercase;letter-spacing:1px;margin-bottom:22px}}
.cw{{height:240px;position:relative}}

/* ═══════════════ TABLE ═══════════════ */
.tb-wrap{{background:var(--s2);border:1px solid var(--br);border-radius:20px;overflow:hidden}}
.tb-scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
thead tr{{background:var(--s3)}}
th{{padding:13px 16px;text-align:left;white-space:nowrap;
  font-size:11px;font-weight:700;letter-spacing:1px;
  text-transform:uppercase;color:var(--mu2);
  border-bottom:1px solid var(--br)}}
td{{padding:14px 16px;border-bottom:1px solid #0f1520;vertical-align:middle}}
tbody tr{{transition:background .15s}}
tbody tr:hover td{{background:#131c2e}}
tbody tr:last-child td{{border-bottom:none}}
.td-r{{color:var(--mu);font-size:12px;font-weight:700;width:40px}}
.cn{{font-size:14px;font-weight:700;color:#fff;margin-bottom:2px;
  display:flex;align-items:center;gap:6px}}
.cm{{font-size:11px;color:var(--mu2)}}
.pw{{display:flex;flex-wrap:wrap;gap:4px;max-width:260px}}
.pill{{background:#0f1e30;color:#5b9bd5;padding:2px 8px;
  border-radius:10px;font-size:11px;white-space:nowrap;
  border:1px solid #1a2e45}}
.pm{{background:var(--s3);color:var(--mu2);border-color:var(--br)}}
.ichip{{background:#151530;color:#818cf8;padding:4px 10px;
  border-radius:8px;font-size:11px;white-space:nowrap;
  border:1px solid #252550}}
.uc{{font-family:'Courier New',monospace;font-size:12px;color:var(--b);
  background:#0a1520;padding:3px 8px;border-radius:6px;white-space:nowrap;
  border:1px solid #152030}}
.achip{{padding:4px 12px;border-radius:8px;font-size:12px;font-weight:600;white-space:nowrap}}
.sw{{min-width:90px}}
.sn{{font-size:13px;font-weight:700;margin-bottom:5px}}
.st{{background:var(--s3);border-radius:3px;height:4px;width:80px}}
.sf{{height:4px;border-radius:3px;transition:width .8s ease}}
.cbadge{{background:#ff6b6b18;color:#ff6b6b;border:1px solid #ff6b6b40;
  padding:1px 7px;border-radius:6px;font-size:10px;font-weight:700}}

/* ═══════════════ CANNIBALIZATION ═══════════════ */
.il{{display:flex;flex-direction:column;gap:12px}}
.iss{{background:var(--s2);border:1px solid var(--br);border-radius:14px;
  padding:16px 20px;display:flex;align-items:flex-start;gap:12px;flex-wrap:wrap;
  transition:transform .2s}}
.iss:hover{{transform:translateX(4px)}}
.iss-b{{padding:3px 10px;border-radius:6px;font-size:11px;
  font-weight:800;white-space:nowrap;flex-shrink:0;letter-spacing:.5px}}
.iss-t{{font-size:10px;font-weight:700;color:var(--mu2);letter-spacing:.8px;
  flex-shrink:0;margin-top:4px;text-transform:uppercase}}
.iss-txt{{font-size:13px;color:#b0bcd0;flex:1;min-width:200px;line-height:1.5}}
.ok-box{{background:linear-gradient(135deg,#0a1f15,#0d2010);
  border:1px solid #1a3a20;border-radius:14px;padding:20px 24px;
  color:#4ecdc4;font-weight:700;font-size:15px;
  display:flex;align-items:center;gap:10px}}

/* ═══════════════ BRIEFS ═══════════════ */
.bg{{display:flex;flex-direction:column;gap:20px}}
.br{{background:var(--s2);border:1px solid var(--br);border-radius:20px;
  overflow:hidden;transition:box-shadow .25s}}
.br:hover{{box-shadow:0 8px 40px #00000040}}
.br-h{{background:var(--s3);padding:18px 26px;display:flex;
  align-items:center;gap:12px;border-bottom:1px solid var(--br)}}
.br-name{{font-size:16px;font-weight:800;color:#fff}}
.br-ic{{font-size:12px;color:var(--mu2);margin-left:auto;background:var(--s2);
  padding:4px 12px;border-radius:20px;border:1px solid var(--br)}}
.br-body{{display:grid;grid-template-columns:1fr 1fr;gap:0}}
.br-f{{padding:18px 26px;border-right:1px solid var(--br);
  border-bottom:1px solid var(--br)}}
.br-f:nth-child(2n){{border-right:none}}
.br-full{{grid-column:1/-1;border-right:none}}
.br-l{{font-size:10px;font-weight:700;color:var(--mu2);
  text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;
  display:flex;align-items:center;gap:8px}}
.br-len{{background:var(--ac)18;color:var(--ac2);padding:1px 7px;
  border-radius:10px;font-size:10px}}
.br-v{{font-size:13px;color:#c5d0e0;line-height:1.5}}
.br-s{{padding-left:18px;font-size:13px;color:#c5d0e0;line-height:2}}
.lp{{display:inline-block;background:#0a1f15;color:var(--g);
  border:1px solid #152a1a;padding:3px 10px;
  border-radius:10px;font-size:12px;margin:2px}}

/* ═══════════════ FOOTER ═══════════════ */
.footer{{padding:40px 48px;border-top:1px solid var(--br);
  display:flex;align-items:center;justify-content:space-between;
  color:var(--mu);font-size:12px}}
.footer-logo{{font-size:13px;font-weight:700;color:var(--mu2)}}
</style>
</head>
<body>

<!-- PARTICLES -->
<div id="particles"></div>

<!-- SIDEBAR -->
<div class="sidebar">
  <div class="sb-logo">
    <div class="sb-logo-icon">🧠</div>
    <div class="sb-logo-title">Semantic Core</div>
    <div class="sb-logo-sub">Agent Report</div>
  </div>
  <nav class="sb-nav">
    <a href="#overview" class="sb-item active"><span class="ico">📊</span> Обзор</a>
    <a href="#top3"     class="sb-item"><span class="ico">🔥</span> Топ приоритеты</a>
    <a href="#charts"   class="sb-item"><span class="ico">📈</span> Аналитика</a>
    <a href="#table"    class="sb-item"><span class="ico">📋</span> Все кластеры</a>
    <a href="#cannibal" class="sb-item"><span class="ico">⚔️</span> Каннибализация</a>
    <a href="#briefs"   class="sb-item"><span class="ico">📝</span> ТЗ страниц</a>
  </nav>
  <div class="sb-footer">
    <div>🌐 {site_url}</div>
    <div>🕐 {generated}</div>
  </div>
</div>

<!-- MAIN -->
<div class="main">

<!-- HERO -->
<div class="hero">
  <div class="hero-orb orb1"></div>
  <div class="hero-orb orb2"></div>
  <div class="hero-badge">✦ Semantic Core Agent</div>
  <h1>Анализ семантического<br>ядра завершён</h1>
  <div class="hero-site">{site_url}</div>
  <div class="hero-desc">{business}</div>
  <div class="hero-tags">
    <div class="htag">📍 <b>{geo}</b></div>
    <div class="htag">🔑 <b>{raw_count}</b> запросов</div>
    <div class="htag">🧩 <b>{len(clusters)}</b> кластеров</div>
    <div class="htag">📄 <b>{len(briefs)}</b> ТЗ готово</div>
    <div class="htag">⚔️ <b>{len(issues)}</b> рисков</div>
    <div class="htag">🕐 <b>{generated}</b></div>
  </div>
</div>

<div class="content">

<!-- OVERVIEW -->
<div class="sec" id="overview">
  <div class="sec-hd">
    <span class="sec-ico">📊</span>
    <span class="sec-ttl">Обзор результатов</span>
  </div>
  <div class="sg">
    <div class="sc" style="--col1:#fff;--col2:#a0b0d0">
      <div class="sc-glow" style="background:#fff"></div>
      <div class="sc-n" data-target="{raw_count}">0</div>
      <div class="sc-l">Запросов собрано</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:100%"></div></div>
    </div>
    <div class="sc" style="--col1:#4ecdc4;--col2:#26d0ce">
      <div class="sc-glow" style="background:#4ecdc4"></div>
      <div class="sc-n" data-target="{clean_count}">0</div>
      <div class="sc-l">После очистки</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:{int(clean_count/max(raw_count,1)*100)}%"></div></div>
    </div>
    <div class="sc" style="--col1:#74b9ff;--col2:#6366f1">
      <div class="sc-glow" style="background:#74b9ff"></div>
      <div class="sc-n" data-target="{len(clusters)}">0</div>
      <div class="sc-l">Кластеров итого</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:100%"></div></div>
    </div>
    <div class="sc" style="--col1:#ff6b6b;--col2:#ee5a24">
      <div class="sc-glow" style="background:#ff6b6b"></div>
      <div class="sc-n" data-target="{len(high)}">0</div>
      <div class="sc-l">🔴 Высокий приоритет</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:{int(len(high)/max(len(clusters),1)*100)}%"></div></div>
    </div>
    <div class="sc" style="--col1:#ffd93d;--col2:#f9ca24">
      <div class="sc-glow" style="background:#ffd93d"></div>
      <div class="sc-n" data-target="{len(medium)}">0</div>
      <div class="sc-l">🟡 Средний приоритет</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:{int(len(medium)/max(len(clusters),1)*100)}%"></div></div>
    </div>
    <div class="sc" style="--col1:#ff6b6b;--col2:#c0392b">
      <div class="sc-glow" style="background:#ff6b6b"></div>
      <div class="sc-n" data-target="{len(create)}">0</div>
      <div class="sc-l">Создать страниц</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:{int(len(create)/max(len(clusters),1)*100)}%"></div></div>
    </div>
    <div class="sc" style="--col1:#ffd93d;--col2:#e67e22">
      <div class="sc-glow" style="background:#ffd93d"></div>
      <div class="sc-n" data-target="{len(update)}">0</div>
      <div class="sc-l">Обновить страниц</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:{int(len(update)/max(len(clusters),1)*100)}%"></div></div>
    </div>
    <div class="sc" style="--col1:#4ecdc4;--col2:#2ecc71">
      <div class="sc-glow" style="background:#4ecdc4"></div>
      <div class="sc-n" data-target="{len(blog)}">0</div>
      <div class="sc-l">Написать статей</div>
      <div class="sc-bar"><div class="sc-bar-f" style="width:{int(len(blog)/max(len(clusters),1)*100)}%"></div></div>
    </div>
  </div>
</div>

<!-- TOP-3 -->
<div class="sec" id="top3">
  <div class="sec-hd">
    <span class="sec-ico">🔥</span>
    <span class="sec-ttl">Топ приоритеты — начать с них</span>
    <span class="sec-sub">Высший ROI</span>
  </div>
  <div class="tg">{top3_html}</div>
</div>

<!-- CHARTS -->
<div class="sec" id="charts">
  <div class="sec-hd">
    <span class="sec-ico">📈</span>
    <span class="sec-ttl">Аналитика</span>
  </div>
  <div class="cg">
    <div class="cb">
      <h3>Интенты запросов</h3>
      <div class="cw"><canvas id="donut"></canvas></div>
    </div>
    <div class="cb">
      <h3>Приоритеты кластеров</h3>
      <div class="cw"><canvas id="hbar"></canvas></div>
    </div>
  </div>
</div>

<!-- TABLE -->
<div class="sec" id="table">
  <div class="sec-hd">
    <span class="sec-ico">📋</span>
    <span class="sec-ttl">Все кластеры</span>
    <span class="sec-sub">{len(clusters)} кластеров</span>
  </div>
  <div class="tb-wrap">
    <div class="tb-scroll">
      <table>
        <thead><tr>
          <th>#</th><th>Кластер</th><th>Запросы</th>
          <th>Интент</th><th>URL</th><th>Действие</th><th>Приоритет</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
  </div>
</div>

<!-- CANNIBALIZATION -->
<div class="sec" id="cannibal">
  <div class="sec-hd">
    <span class="sec-ico">⚔️</span>
    <span class="sec-ttl">Анализ каннибализации</span>
    <span class="sec-sub">{len(issues)} проблем</span>
  </div>
  <div class="il">{can_html}</div>
</div>

<!-- BRIEFS -->
<div class="sec" id="briefs">
  <div class="sec-hd">
    <span class="sec-ico">📝</span>
    <span class="sec-ttl">ТЗ для копирайтера</span>
    <span class="sec-sub">Топ-{len(briefs[:4])} кластера</span>
  </div>
  <div class="bg">{br_html}</div>
</div>

</div><!-- /content -->

<div class="footer">
  <div class="footer-logo">🧠 Semantic Core Agent</div>
  <div>{generated} &nbsp;·&nbsp; {site_url}</div>
</div>

</div><!-- /main -->

<script>
// ── PARTICLES ──────────────────────────────────────────────
(function(){{
  const c = document.getElementById('particles');
  const colors = ['#6366f1','#818cf8','#ff6b6b','#4ecdc4','#ffd93d','#c77dff'];
  for(let i=0;i<25;i++){{
    const d = document.createElement('div');
    d.className='pt';
    const sz = Math.random()*4+1;
    d.style.cssText = `width:${{sz}}px;height:${{sz}}px;
      left:${{Math.random()*100}}%;
      background:${{colors[Math.floor(Math.random()*colors.length)]}};
      animation-duration:${{Math.random()*20+15}}s;
      animation-delay:-${{Math.random()*20}}s;
      opacity:${{Math.random()*.4+.1}}`;
    c.appendChild(d);
  }}
}})();

// ── COUNTER ANIMATION ──────────────────────────────────────
function animateCounter(el){{
  const target = parseInt(el.dataset.target)||0;
  const dur = 1200;
  const step = dur/60;
  let cur = 0;
  const inc = target/60;
  const t = setInterval(()=>{{
    cur = Math.min(cur+inc, target);
    el.textContent = Math.floor(cur);
    if(cur>=target)clearInterval(t);
  }},step);
}}
const obs = new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{ if(e.isIntersecting){{ animateCounter(e.target); obs.unobserve(e.target); }} }});
}},{{threshold:.5}});
document.querySelectorAll('[data-target]').forEach(el=>obs.observe(el));

// ── SIDEBAR ACTIVE ─────────────────────────────────────────
const secs = document.querySelectorAll('.sec');
const items = document.querySelectorAll('.sb-item');
const sObs = new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{
    if(e.isIntersecting){{
      items.forEach(i=>i.classList.remove('active'));
      const a = document.querySelector(`.sb-item[href="#${{e.target.id}}"]`);
      if(a)a.classList.add('active');
    }}
  }});
}},{{threshold:.4}});
secs.forEach(s=>sObs.observe(s));

// ── CHARTS ────────────────────────────────────────────────
Chart.defaults.color='#4a5568';
Chart.defaults.borderColor='#1e2535';

new Chart(document.getElementById('donut'),{{
  type:'doughnut',
  data:{{
    labels:{dl_js},
    datasets:[{{data:{dv_js},backgroundColor:{dc_js},
      borderWidth:0,hoverOffset:10}}]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    cutout:'68%',
    animation:{{animateRotate:true,duration:1200}},
    plugins:{{
      legend:{{position:'right',labels:{{boxWidth:10,padding:12,font:{{size:11}}}}}}
    }}
  }}
}});

new Chart(document.getElementById('hbar'),{{
  type:'bar',
  data:{{
    labels:{pn_js},
    datasets:[{{
      data:{ps_js},
      backgroundColor:{pc_js},
      borderRadius:8,borderSkipped:false,
    }}]
  }},
  options:{{
    indexAxis:'y',
    responsive:true,maintainAspectRatio:false,
    animation:{{duration:1200,easing:'easeOutQuart'}},
    plugins:{{legend:{{display:false}}}},
    scales:{{
      x:{{grid:{{color:'#1e2535'}},max:100,ticks:{{font:{{size:11}}}}}},
      y:{{grid:{{display:false}},ticks:{{font:{{size:11}}}}}}
    }}
  }}
}});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
