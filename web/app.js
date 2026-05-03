const ACTION_LABELS = {
  create_page: "Создать страницу",
  update_page: "Обновить страницу",
  create_blog: "Создать статью",
  add_faq: "Добавить FAQ",
  skip: "Не брать"
};

const INTENT_LABELS = {
  commercial: "Коммерческий",
  transactional: "Транзакционный",
  informational: "Информационный",
  comparison: "Сравнение",
  navigational: "Навигационный",
  local: "Локальный",
  problem_based: "Проблемный"
};

const INTENT_PAGE_TYPES = {
  commercial: "Категория / листинг",
  transactional: "Категория / лендинг",
  informational: "Статья / гайд",
  comparison: "Comparison page",
  navigational: "Не брать",
  local: "Гео-страница",
  problem_based: "FAQ + подборка"
};

const SCORING_WEIGHTS = {
  search_volume: 0.25,
  business_value: 0.2,
  ranking_opportunity: 0.2,
  intent_match: 0.15,
  trend_growth: 0.1,
  content_gap: 0.1,
  keyword_difficulty: -0.2,
  cannibalization_risk: -0.15
};

const HIGH_PRIORITY_THRESHOLD = 70;
const MAX_SIMILARITY_ISSUES = 12;
const MAX_RENDERED_RISKS = 24;

const MODIFIERS = {
  commercial: ["купить", "цена", "заказать", "недорого", "стоимость"],
  geo: ["в Москве", "в СПб", "с доставкой", "рядом"],
  characteristics: ["премиум", "недорогой", "под ключ", "быстрый"],
  purpose: ["для бизнеса", "для сайта", "для интернет-магазина", "для лидогенерации"],
  audience: ["для малого бизнеса", "для B2B", "для стартапа"],
  problem: ["без ошибок", "легко внедрить", "окупается быстро"],
  comparison: ["или альтернатива", "что лучше", "отличие"],
  materials: ["с интеграцией", "с аналитикой", "с CRM"],
  size: ["под ключ", "комплексный", "индивидуальный"]
};

const STOP_PATTERNS = [
  /\bбесплатно\b/i,
  /\bскачать\b/i,
  /\bторрент\b/i,
  /\bсвоими руками\b/i,
  /\bсделать самому\b/i,
  /\bчертежи\b/i,
  /\bбу\b/i,
  /\bаренда\b/i,
  /\bнапрокат\b/i,
  /\bремонт\b/i,
  /\bреставрация\b/i
];

const INTENT_RULES = [
  ["купить", "commercial"],
  ["цена", "commercial"],
  ["стоимость", "commercial"],
  ["заказать", "transactional"],
  ["доставка", "transactional"],
  ["под ключ", "transactional"],
  ["как выбрать", "informational"],
  ["что такое", "informational"],
  ["почему", "informational"],
  ["гайд", "informational"],
  ["какой лучше", "comparison"],
  [" или ", "comparison"],
  ["что лучше", "comparison"],
  ["отличие", "comparison"],
  ["в москве", "local"],
  ["в спб", "local"],
  ["рядом", "local"],
  ["не скрипит", "problem_based"],
  ["легко чистить", "problem_based"],
  ["без ошибок", "problem_based"],
  ["окупается", "problem_based"],
  [".ru ", "navigational"],
  [".com ", "navigational"]
];

const CLUSTER_RULES = [
  ["для сна", "{base} для сна", "commercial", "category"],
  ["для кухни", "{base} для кухни", "commercial", "category"],
  ["для офиса", "{base} для офиса", "commercial", "category"],
  ["для бизнеса", "{base} для бизнеса", "commercial", "category"],
  ["для интернет-магазина", "{base} для интернет-магазина", "commercial", "category"],
  ["угловой", "{base}: угловой формат", "commercial", "category"],
  ["раскладной", "{base}: раскладной формат", "commercial", "category"],
  ["кожаный", "{base}: кожаный материал", "commercial", "category"],
  ["в москве", "{base} в Москве", "local", "geo"],
  ["в спб", "{base} в СПб", "local", "geo"],
  ["недорого", "{base}: недорого", "commercial", "category"],
  ["как выбрать", "Как выбрать {baseLower}", "informational", "blog"],
  ["или ", "{base}: сравнение вариантов", "comparison", "blog"],
  ["что лучше", "Что лучше: {baseLower}", "comparison", "blog"],
  ["не скрипит", "{base}: решение проблемы", "problem_based", "blog"],
  ["легко чистит", "{base}: простой уход", "problem_based", "blog"],
  ["без ошибок", "{base}: без ошибок", "problem_based", "blog"],
  ["с интеграцией", "{base}: интеграции", "commercial", "category"],
  ["с аналитикой", "{base}: аналитика", "commercial", "category"],
  ["с crm", "{base}: CRM-интеграция", "commercial", "category"],
  ["под ключ", "{base} под ключ", "transactional", "category"],
  ["заказать", "{base}: заявка онлайн", "transactional", "category"]
];

const PAGE_STRUCTURES = {
  commercial: [
    "Фильтры: цена, характеристики, сценарий использования",
    "Карточки товаров или услуг",
    "Блок преимуществ и гарантий",
    "SEO-текст 400-600 слов",
    "FAQ по покупке"
  ],
  transactional: [
    "H1 с CTA",
    "Форма заявки / корзина",
    "Условия оплаты и доставки",
    "Гарантии",
    "Отзывы и кейсы"
  ],
  informational: [
    "Введение через проблему читателя",
    "Основной гайд 1500-2500 слов",
    "Списки и таблицы выбора",
    "Ошибки и критерии",
    "CTA в каталог или заявку"
  ],
  comparison: [
    "Таблица сравнения вариантов",
    "Плюсы и минусы",
    "Кому подходит каждый вариант",
    "Итоговая рекомендация",
    "CTA на целевую страницу"
  ],
  local: [
    "H1 с гео",
    "Преимущества работы в регионе",
    "Каталог / форма заявки",
    "Доставка или зона обслуживания",
    "Отзывы локальных клиентов"
  ],
  problem_based: [
    "Описание проблемы",
    "Критерии выбора решения",
    "Подборка подходящих страниц",
    "Экспертный блок",
    "FAQ"
  ]
};

const PIPELINE_STEPS = [
  ["research", "Research"],
  ["expansion", "Expansion"],
  ["cleaning", "Cleaning"],
  ["intent", "Intent"],
  ["clustering", "Clustering"],
  ["mapping", "Mapping"],
  ["prioritization", "Scoring"],
  ["cannibalization", "Risks"],
  ["brief", "Briefs"],
  ["output", "Output"]
];

const THEME_STORAGE_KEY = "sca-theme";

const state = {
  result: null,
  filters: {
    query: "",
    intent: "all",
    action: "all"
  }
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function normalize(text) {
  return String(text || "").toLowerCase().replace(/\s+/g, " ").trim();
}

function parseLines(value) {
  return String(value || "")
    .split(/[\n,;]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function parsePriority(value) {
  const result = {};
  String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .forEach((pair) => {
      const [key, rawValue] = pair.split(":").map((part) => part.trim());
      const number = Number(rawValue);
      if (key && Number.isFinite(number)) {
        result[key] = Math.max(1, Math.min(5, number));
      }
    });
  return result;
}

function createKeyword(text, source, extra = {}) {
  return {
    text: normalize(text),
    source,
    volume: null,
    clicks: null,
    impressions: null,
    position: null,
    intent: null,
    intent_confidence: null,
    cluster: null,
    action: null,
    priority_score: null,
    recommended_url: null,
    reason: null,
    ...extra
  };
}

function createInitialState(input) {
  return {
    ...input,
    raw_keywords: [],
    cleaned_keywords: [],
    classified_keywords: [],
    clusters: [],
    gap_analysis: [],
    output_table: [],
    cannibalization_issues: [],
    briefs: [],
    logs: [],
    errors: [],
    current_step: "init"
  };
}

function researchAgent(pipelineState) {
  const all = pipelineState.seed_keywords.map((kw) => createKeyword(kw, "seed"));

  if (pipelineState.options.mockSources) {
    all.push(...buildMockSearchData(pipelineState));
  }

  if (pipelineState.options.competitorMode && pipelineState.competitors.length) {
    all.push(...buildMockCompetitorData(pipelineState));
  }

  pipelineState.raw_keywords = all;
  pipelineState.logs.push(`research: ${all.length} keywords collected`);
  return pipelineState;
}

function seedBase(seed) {
  return stripCommercialWords(seed) || normalize(seed);
}

function buildMockSearchData(pipelineState) {
  const bases = [...new Set(pipelineState.seed_keywords.map(seedBase).filter(Boolean))];
  const primary = bases[0] || "услуга";
  const secondary = bases[1] || primary;
  const geo = pipelineState.geo || "Москва";
  return [
    createKeyword(`${primary} с доставкой`, "gsc", { clicks: 12, impressions: 3200, position: 14.7 }),
    createKeyword(`${primary} недорого`, "gsc", { clicks: 45, impressions: 890, position: 7.3 }),
    createKeyword(`${secondary} цена`, "gsc", { clicks: 8, impressions: 1800, position: 18.2 }),
    createKeyword(`${primary} для бизнеса`, "gsc", { clicks: 5, impressions: 2100, position: 16.5 }),
    createKeyword(`${primary} в ${geo}`, "yandex_webmaster", { volume: 4200, clicks: 23, impressions: 1200, position: 11 }),
    createKeyword(`${secondary} под ключ`, "yandex_webmaster", { volume: 3100, clicks: 67, impressions: 2300, position: 5.4 })
  ];
}

function buildMockCompetitorData(pipelineState) {
  const bases = [...new Set(pipelineState.seed_keywords.map(seedBase).filter(Boolean))];
  const primary = bases[0] || "услуга";
  const secondary = bases[1] || primary;
  const third = bases[2] || secondary;
  return [
    createKeyword(`${primary} для интернет-магазина`, "competitor", { volume: 1800 }),
    createKeyword(`${primary} с интеграцией`, "competitor", { volume: 2400 }),
    createKeyword(`${secondary} комплексный`, "competitor", { volume: 5600 }),
    createKeyword(`${third} без ошибок`, "competitor", { volume: 890 })
  ];
}

function expansionAgent(pipelineState) {
  const expanded = [];
  pipelineState.seed_keywords.forEach((seed) => {
    Object.entries(MODIFIERS).forEach(([type, modifiers]) => {
      modifiers.slice(0, 3).forEach((modifier) => {
        expanded.push(createKeyword(`${seed} ${modifier}`, `expansion_modifier_${type}`));
      });
    });
  });
  pipelineState.raw_keywords = pipelineState.raw_keywords.concat(expanded);
  pipelineState.logs.push(`expansion: +${expanded.length}, total: ${pipelineState.raw_keywords.length}`);
  return pipelineState;
}

function cleaningAgent(pipelineState) {
  const seen = new Set();
  const cleaned = [];
  const removed = { dup: 0, stop: 0, short: 0, long: 0 };

  pipelineState.raw_keywords.forEach((keyword) => {
    const text = normalize(keyword.text);
    if (seen.has(text)) {
      removed.dup += 1;
      return;
    }
    seen.add(text);
    if (STOP_PATTERNS.some((pattern) => pattern.test(text))) {
      removed.stop += 1;
      return;
    }
    const words = text.split(" ").filter(Boolean).length;
    if (words < 2) {
      removed.short += 1;
      return;
    }
    if (words > 8) {
      removed.long += 1;
      return;
    }
    cleaned.push({ ...keyword, text });
  });

  pipelineState.cleaned_keywords = cleaned;
  pipelineState.cleaning_removed = removed;
  pipelineState.logs.push(`cleaning: ${pipelineState.raw_keywords.length} -> ${cleaned.length}`);
  return pipelineState;
}

function classifyIntent(text) {
  const prepared = ` ${normalize(text)} `;
  const rule = INTENT_RULES.find(([pattern]) => prepared.includes(pattern));
  return rule ? rule[1] : "commercial";
}

function intentAgent(pipelineState) {
  pipelineState.classified_keywords = pipelineState.cleaned_keywords.map((keyword) => ({
    ...keyword,
    intent: classifyIntent(keyword.text),
    intent_confidence: classifyIntent(keyword.text) === "commercial" ? 0.58 : 0.75
  }));
  pipelineState.logs.push(`intent: ${pipelineState.classified_keywords.length} keywords classified`);
  return pipelineState;
}

function stripCommercialWords(text) {
  return normalize(text)
    .replace(/\b(купить|заказать|цена|стоимость|недорого|дешево|под ключ|в москве|в спб|с доставкой)\b/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function significantWords(text) {
  const stop = new Set(["для", "или", "что", "как", "где", "под", "при", "без", "с", "в", "на", "по", "и", "а", "от"]);
  return normalize(text)
    .split(" ")
    .filter((word) => word.length > 1 && !stop.has(word));
}

function titleCase(text) {
  const prepared = normalize(text);
  if (!prepared) return "Новый кластер";
  return prepared.charAt(0).toUpperCase() + prepared.slice(1);
}

function stemTerm(term) {
  const prepared = normalize(term);
  const stem = prepared.replace(/[ыиаяоеуюэь]+$/i, "");
  return stem.length >= 3 ? stem : prepared;
}

function categoryMatches(text, category) {
  const prepared = normalize(text);
  const normalizedCategory = normalize(category);
  if (prepared.includes(normalizedCategory)) return true;

  const textStems = new Set(significantWords(prepared).map(stemTerm));
  return significantWords(normalizedCategory).some((word) => textStems.has(stemTerm(word)));
}

const translitMap = {
  а: "a", б: "b", в: "v", г: "g", д: "d", е: "e", ё: "e", ж: "zh", з: "z", и: "i",
  й: "y", к: "k", л: "l", м: "m", н: "n", о: "o", п: "p", р: "r", с: "s", т: "t",
  у: "u", ф: "f", х: "h", ц: "c", ч: "ch", ш: "sh", щ: "sch", ъ: "", ы: "y", ь: "",
  э: "e", ю: "yu", я: "ya"
};

function slugify(text) {
  return normalize(text)
    .split("")
    .map((char) => translitMap[char] ?? char)
    .join("")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 72) || "page";
}

function findSeedBase(text, seeds) {
  const normalizedText = normalize(text);
  const bases = seeds
    .map((seed) => stripCommercialWords(seed) || normalize(seed))
    .filter(Boolean)
    .sort((a, b) => b.length - a.length);
  return bases.find((base) => normalizedText.includes(base)) || bases[0] || stripCommercialWords(text);
}

function estimateKeywordDemand(keyword) {
  const volume = Number(keyword.volume);
  if (Number.isFinite(volume) && volume > 0) return volume;

  const impressions = Number(keyword.impressions);
  if (Number.isFinite(impressions) && impressions > 0) return impressions;

  const clicks = Number(keyword.clicks);
  if (Number.isFinite(clicks) && clicks > 0) return clicks * 80;

  if (keyword.source === "seed") return 600;
  if (String(keyword.source || "").includes("competitor")) return 700;
  if (String(keyword.source || "").includes("expansion")) return 160;
  return 250;
}

function buildGenericCluster(keyword, pipelineState) {
  const text = normalize(keyword.text);
  const intent = keyword.intent || classifyIntent(text);
  const base = findSeedBase(text, pipelineState.seed_keywords) || significantWords(text).slice(0, 3).join(" ");
  const baseTitle = titleCase(base);
  let name = baseTitle;
  let url = `/catalog/${slugify(base)}/`;
  let pageType = "category";

  if (intent === "local") {
    const geo = text.includes("спб") ? "СПб" : pipelineState.geo;
    name = `${baseTitle} в ${geo}`;
    url = `/catalog/${slugify(base)}-${slugify(geo)}/`;
    pageType = "geo";
  } else if (intent === "informational") {
    name = text.includes("как") ? titleCase(text) : `Как выбрать ${base}`;
    url = `/blog/${slugify(name)}/`;
    pageType = "blog";
  } else if (intent === "comparison") {
    name = text.includes("что лучше") ? `Что лучше: ${base}` : titleCase(text);
    url = `/blog/${slugify(name)}/`;
    pageType = "blog";
  } else if (intent === "problem_based") {
    const words = significantWords(text).filter((word) => !base.includes(word)).slice(0, 3);
    name = words.length ? `${baseTitle}: ${words.join(" ")}` : `${baseTitle}: решение проблемы`;
    url = `/blog/${slugify(name)}/`;
    pageType = "faq";
  } else if (intent === "transactional") {
    name = `${baseTitle} под заявку`;
    url = `/catalog/${slugify(base)}/`;
  } else if (text.includes("цена") || text.includes("стоимость")) {
    name = `${baseTitle}: цены`;
  } else {
    const descriptor = significantWords(stripCommercialWords(text))
      .filter((word) => !base.split(" ").includes(word))
      .slice(0, 2)
      .join(" ");
    if (descriptor) {
      name = `${baseTitle}: ${descriptor}`;
      url = `/catalog/${slugify(`${base}-${descriptor}`)}/`;
    }
  }

  return { name, intent, url, pageType };
}

function buildRuleCluster(keywordText, pipelineState, rule) {
  const [, template, intent, pageType] = rule;
  const base = findSeedBase(keywordText, pipelineState.seed_keywords) || significantWords(keywordText).slice(0, 3).join(" ") || "услуга";
  const baseTitle = titleCase(base);
  const name = template
    .replaceAll("{base}", baseTitle)
    .replaceAll("{baseLower}", base);
  const prefix = pageType === "blog" ? "blog" : "catalog";
  return {
    name,
    intent,
    url: `/${prefix}/${slugify(name)}/`,
    pageType
  };
}

function clusteringAgent(pipelineState) {
  const clustersMap = new Map();

  pipelineState.classified_keywords.forEach((keyword) => {
    const text = normalize(keyword.text);
    const specific = CLUSTER_RULES.find(([pattern]) => text.includes(pattern));
    const data = specific
      ? buildRuleCluster(text, pipelineState, specific)
      : buildGenericCluster(keyword, pipelineState);

    if (!clustersMap.has(data.name)) {
      clustersMap.set(data.name, {
        name: data.name,
        main_keyword: keyword.text,
        keywords: [],
        sources: {},
        intent: data.intent,
        recommended_page_type: data.pageType,
        recommended_url: data.url,
        action: "create_page",
        priority_score: 0,
        reason: specific ? `pattern: '${specific[0]}'` : "generic semantic grouping",
        existing_page: null,
        cannibalization_risk: "low",
        total_volume: 0
      });
    }

    const cluster = clustersMap.get(data.name);
    cluster.keywords.push(keyword.text);
    cluster.sources[keyword.source] = (cluster.sources[keyword.source] || 0) + 1;
    cluster.total_volume += estimateKeywordDemand(keyword);
  });

  pipelineState.clusters = Array.from(clustersMap.values());
  pipelineState.logs.push(`clustering: ${pipelineState.clusters.length} clusters formed`);
  return pipelineState;
}

function findExistingPage(cluster, targetPages) {
  const recommendedUrl = normalizeUrl(cluster.recommended_url);
  const kwWords = new Set(significantWords(cluster.main_keyword));
  const slugWords = new Set(significantWords(cluster.recommended_url.replaceAll("/", " ").replaceAll("-", " ")));

  for (const page of targetPages) {
    if (normalizeUrl(page) === recommendedUrl) {
      return page;
    }
    const pageWords = new Set(significantWords(page.replaceAll("/", " ").replaceAll("-", " ").replaceAll("_", " ")));
    const overlap = [...kwWords].filter((word) => pageWords.has(word)).length;
    const slugOverlap = [...slugWords].filter((word) => pageWords.has(word)).length;
    if (overlap >= Math.max(1, Math.floor(kwWords.size / 2)) || slugOverlap >= 2) {
      return page;
    }
  }
  return null;
}

function normalizeUrl(url) {
  const prepared = String(url || "").trim().toLowerCase();
  if (!prepared) return "";
  return prepared.endsWith("/") ? prepared : `${prepared}/`;
}

function decideAction(cluster, existingPage) {
  if (cluster.intent === "navigational") return "skip";
  if (cluster.intent === "informational") return "create_blog";
  if (cluster.intent === "problem_based") return existingPage ? "add_faq" : "create_blog";
  if (cluster.intent === "comparison") return "create_blog";
  return existingPage ? "update_page" : "create_page";
}

function mappingAgent(pipelineState) {
  pipelineState.clusters.forEach((cluster) => {
    const existing = findExistingPage(cluster, pipelineState.target_pages);
    cluster.existing_page = existing;
    cluster.action = decideAction(cluster, existing);
    if (existing) {
      cluster.recommended_url = existing;
    }
  });
  pipelineState.logs.push(`mapping: ${pipelineState.clusters.length} clusters mapped`);
  return pipelineState;
}

function estimateSearchVolume(cluster) {
  const demand = cluster.total_volume || cluster.keywords.length * 150;
  const demandScore = Math.log10(demand + 1) / Math.log10(8000);
  const breadthScore = Math.min(1, cluster.keywords.length / 8);
  return Math.max(0.25, Math.min(1, demandScore * 0.72 + breadthScore * 0.28));
}

function estimateBusinessValue(cluster, priority) {
  const text = normalize(`${cluster.main_keyword} ${cluster.name}`);
  const values = Object.values(priority);
  const max = values.length ? Math.max(...values) : 5;
  for (const [category, value] of Object.entries(priority)) {
    if (categoryMatches(text, category)) return value / max;
  }
  if (cluster.intent === "transactional") return 0.75;
  if (cluster.intent === "commercial") return 0.65;
  if (cluster.intent === "local") return 0.7;
  if (cluster.intent === "informational") return 0.35;
  return 0.45;
}

function estimateRankingOpportunity(cluster) {
  if (cluster.action === "update_page") return 0.8;
  if (cluster.action === "create_page") return 0.7;
  if (cluster.action === "create_blog") return 0.55;
  return 0.3;
}

function estimateIntentMatch(cluster) {
  const scores = {
    commercial: 1,
    transactional: 0.9,
    local: 0.8,
    problem_based: 0.6,
    comparison: 0.5,
    informational: 0.3,
    navigational: 0
  };
  return scores[cluster.intent] ?? 0.5;
}

function estimateContentGap(cluster) {
  return cluster.existing_page ? 0.2 : 1;
}

function estimateCannibalizationRisk(cluster) {
  if (cluster.existing_page && cluster.action === "create_page") return 0.8;
  return 0.1;
}

function estimateKeywordDifficulty(cluster) {
  if (cluster.action === "update_page") return 0.35;
  if (["informational", "problem_based", "comparison"].includes(cluster.intent)) return 0.35;
  if ((cluster.total_volume || 0) >= 3000) return 0.45;
  return 0.4;
}

function calculateScore(cluster, priority) {
  const w = SCORING_WEIGHTS;
  const score =
    w.search_volume * estimateSearchVolume(cluster) +
    w.business_value * estimateBusinessValue(cluster, priority) +
    w.ranking_opportunity * estimateRankingOpportunity(cluster) +
    w.intent_match * estimateIntentMatch(cluster) +
    w.trend_growth * 0.6 +
    w.content_gap * estimateContentGap(cluster) +
    w.keyword_difficulty * estimateKeywordDifficulty(cluster) +
    w.cannibalization_risk * estimateCannibalizationRisk(cluster);
  return Math.round(Math.max(0, Math.min(100, score * 100)) * 10) / 10;
}

function semanticSimilarityIssue(left, right) {
  const leftWords = [...new Set(significantWords(left.name).map(stemTerm))];
  const rightWords = [...new Set(significantWords(right.name).map(stemTerm))];
  const overlap = leftWords.filter((word) => rightWords.includes(word));
  const union = new Set([...leftWords, ...rightWords]);
  const ratio = union.size ? overlap.length / union.size : 0;

  if (overlap.length < 3 || ratio < 0.45) return null;
  return {
    type: "intent_similarity",
    severity: "medium",
    clusters: [left.name, right.name],
    shared_words: overlap,
    similarity: ratio,
    recommendation: `Кластеры "${left.name}" и "${right.name}" похожи по интенту. Проверить, не конкурируют ли они в SERP.`
  };
}

function prioritizationAgent(pipelineState) {
  pipelineState.clusters.forEach((cluster) => {
    cluster.priority_score = calculateScore(cluster, pipelineState.commercial_priority);
  });
  pipelineState.clusters.sort((a, b) => b.priority_score - a.priority_score);
  pipelineState.logs.push("prioritization: scores calculated");
  return pipelineState;
}

function cannibalizationAgent(pipelineState) {
  const issues = [];
  const keywordMap = new Map();
  const urlMap = new Map();

  pipelineState.clusters.forEach((cluster) => {
    cluster.keywords.forEach((keyword) => {
      const key = normalize(keyword);
      keywordMap.set(key, [...(keywordMap.get(key) || []), cluster.name]);
    });
    const url = cluster.recommended_url;
    if (url) {
      urlMap.set(url, [...(urlMap.get(url) || []), cluster.name]);
    }
  });

  keywordMap.forEach((clusters, keyword) => {
    const unique = [...new Set(clusters)];
    if (unique.length > 1) {
      issues.push({
        type: "keyword_overlap",
        severity: "high",
        keyword,
        clusters: unique,
        recommendation: `Запрос "${keyword}" встречается в нескольких кластерах: ${unique.join(", ")}. Оставить запрос в самом релевантном кластере.`
      });
    }
  });

  urlMap.forEach((clusters, url) => {
    const unique = [...new Set(clusters)];
    if (unique.length > 1) {
      issues.push({
        type: "url_conflict",
        severity: "critical",
        url,
        clusters: unique,
        recommendation: `URL ${url} назначен ${unique.length} кластерам: ${unique.join(", ")}. Развести посадочные или объединить кластеры.`
      });
    }
  });

  const similarityIssues = [];
  const checked = new Set();
  pipelineState.clusters.forEach((left, i) => {
    pipelineState.clusters.forEach((right, j) => {
      if (i >= j) return;
      const key = `${i}:${j}`;
      if (checked.has(key) || left.intent !== right.intent) return;
      checked.add(key);
      const issue = semanticSimilarityIssue(left, right);
      if (issue) similarityIssues.push(issue);
    });
  });
  issues.push(
    ...similarityIssues
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, MAX_SIMILARITY_ISSUES)
  );

  const conflictNames = new Set(
    issues
      .filter((issue) => ["critical", "high"].includes(issue.severity))
      .flatMap((issue) => issue.clusters || [])
  );
  pipelineState.clusters.forEach((cluster) => {
    if (conflictNames.has(cluster.name)) {
      cluster.cannibalization_risk = "high";
      cluster.priority_score = Math.max(0, Math.round((cluster.priority_score - 15) * 10) / 10);
    } else {
      cluster.cannibalization_risk = "low";
    }
  });
  pipelineState.clusters.sort((a, b) => b.priority_score - a.priority_score);
  pipelineState.cannibalization_issues = issues;
  pipelineState.logs.push(`cannibalization: ${issues.length} issues`);
  return pipelineState;
}

function briefAgent(pipelineState) {
  const currentYear = new Date().getFullYear();
  pipelineState.briefs = pipelineState.clusters
    .filter((cluster) => cluster.action !== "skip")
    .map((cluster) => {
      const baseBusiness = pipelineState.business_description.split(",")[0].trim() || "компания";
      let title;
      if (["commercial", "transactional"].includes(cluster.intent)) {
        title = `${cluster.name} — купить в ${pipelineState.geo} | ${titleCase(baseBusiness)}`;
      } else if (cluster.intent === "local") {
        title = `${cluster.name} — цены, доставка, каталог`;
      } else if (cluster.intent === "informational") {
        title = `${cluster.name} — подробный гайд ${currentYear}`;
      } else {
        title = `${cluster.name} — ${baseBusiness}`;
      }

      const description = ["commercial", "transactional", "local"].includes(cluster.intent)
        ? `Купить ${cluster.main_keyword} в ${pipelineState.geo}. Подборка решений, понятные цены, доставка и консультация.`
        : `${cluster.name}. Практические советы, критерии выбора и рекомендации экспертов.`;

      return {
        cluster: cluster.name,
        url: cluster.recommended_url,
        intent: cluster.intent,
        title: title.slice(0, 65),
        h1: cluster.name,
        description: description.slice(0, 160),
        structure: PAGE_STRUCTURES[cluster.intent] || PAGE_STRUCTURES.commercial,
        main_keyword: cluster.main_keyword,
        secondary_keywords: cluster.keywords.slice(0, 5),
        lsi_words: [...new Set(cluster.keywords.filter((keyword) => keyword !== cluster.main_keyword))].slice(0, 6),
        word_count: cluster.intent === "commercial" ? "400-600" : "1500-2500",
        generated_by: "rules"
      };
    });
  pipelineState.logs.push(`brief: ${pipelineState.briefs.length} briefs generated`);
  return pipelineState;
}

function outputAgent(pipelineState) {
  pipelineState.gap_analysis = pipelineState.clusters.map((cluster) => ({
    cluster: cluster.name,
    main_keyword: cluster.main_keyword,
    has_page: cluster.existing_page ? "да" : "нет",
    existing_url: cluster.existing_page || "—",
    intent: cluster.intent,
    action: ACTION_LABELS[cluster.action] || cluster.action,
    priority: cluster.priority_score,
    reason: cluster.reason
  }));

  pipelineState.output_table = pipelineState.clusters.map((cluster) => ({
    "Кластер": cluster.name,
    "Главный ключ": cluster.main_keyword,
    "Все запросы": cluster.keywords.slice(0, 8).join(" | "),
    "Кол-во запросов": cluster.keywords.length,
    "Интент": INTENT_LABELS[cluster.intent] || cluster.intent,
    "Тип страницы": INTENT_PAGE_TYPES[cluster.intent] || cluster.intent,
    "URL страницы": cluster.recommended_url || "—",
    "Действие": ACTION_LABELS[cluster.action] || cluster.action,
    "Приоритет": priorityLabel(cluster.priority_score),
    "Риск каннибализации": cluster.cannibalization_risk === "high" ? "высокий" : "низкий",
    "Причина": cluster.reason
  }));
  pipelineState.generated_at = new Date().toLocaleString("ru-RU");
  pipelineState.logs.push("output: tables ready");
  return pipelineState;
}

function priorityLabel(score) {
  if (score >= HIGH_PRIORITY_THRESHOLD) return `ВЫСОКИЙ (${score})`;
  if (score >= 40) return `СРЕДНИЙ (${score})`;
  return `НИЗКИЙ (${score})`;
}

function collectInput() {
  const seedKeywords = parseLines($("#seed-keywords").value);
  return {
    site_url: $("#site-url").value.trim() || "example.ru",
    business_description: $("#business-description").value.trim() || "описание бизнеса",
    seed_keywords: seedKeywords.length ? seedKeywords : ["купить услугу"],
    geo: $("#geo").value.trim() || "Москва",
    language: $("#language").value,
    target_pages: parseLines($("#target-pages").value),
    competitors: parseLines($("#competitors").value),
    commercial_priority: parsePriority($("#commercial-priority").value),
    options: {
      mockSources: $("#mock-sources").checked,
      competitorMode: $("#competitor-mode").checked
    }
  };
}

async function runAnalysis(event) {
  if (event) event.preventDefault();
  const input = collectInput();
  let pipelineState = createInitialState(input);
  renderPipelineSteps("research");

  const steps = [
    ["research", researchAgent],
    ["expansion", expansionAgent],
    ["cleaning", cleaningAgent],
    ["intent", intentAgent],
    ["clustering", clusteringAgent],
    ["mapping", mappingAgent],
    ["prioritization", prioritizationAgent],
    ["cannibalization", cannibalizationAgent],
    ["brief", briefAgent],
    ["output", outputAgent]
  ];

  for (const [key, agent] of steps) {
    renderPipelineSteps(key);
    await sleep(55);
    pipelineState.current_step = key;
    pipelineState = agent(pipelineState);
    renderPipelineSteps(key, pipelineState);
  }

  state.result = pipelineState;
  populateFilters();
  renderAll();
  showToast("Анализ готов");
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function renderPipelineSteps(activeKey = "output", pipelineState = state.result) {
  const activeIndex = PIPELINE_STEPS.findIndex(([key]) => key === activeKey);
  $("#pipeline-steps").innerHTML = PIPELINE_STEPS.map(([key, label], index) => {
    const done = index <= activeIndex;
    const count = stepCount(key, pipelineState);
    return `<li class="${done ? "done" : ""}"><i>${done ? "✓" : index + 1}</i><span>${label}</span><em>${count}</em></li>`;
  }).join("");
}

function stepCount(key, pipelineState) {
  if (!pipelineState) return "";
  const map = {
    research: pipelineState.raw_keywords?.length,
    expansion: pipelineState.raw_keywords?.length,
    cleaning: pipelineState.cleaned_keywords?.length,
    intent: pipelineState.classified_keywords?.length,
    clustering: pipelineState.clusters?.length,
    mapping: pipelineState.gap_analysis?.length || pipelineState.clusters?.length,
    prioritization: pipelineState.clusters?.filter((cluster) => cluster.priority_score >= HIGH_PRIORITY_THRESHOLD).length,
    cannibalization: pipelineState.cannibalization_issues?.length,
    brief: pipelineState.briefs?.length,
    output: pipelineState.output_table?.length
  };
  const value = map[key];
  return Number.isFinite(value) ? String(value) : "";
}

function renderAll() {
  if (!state.result) return;
  renderSummary();
  renderTopClusters();
  renderCharts();
  renderClusterTable();
  renderRisks();
  renderBriefs();
  renderExportPreview();
}

function renderSummary() {
  const result = state.result;
  const high = result.clusters.filter((cluster) => cluster.priority_score >= HIGH_PRIORITY_THRESHOLD).length;
  const create = result.clusters.filter((cluster) => cluster.action === "create_page").length;
  $("#report-title").textContent = `Семантическое ядро: ${result.site_url}`;
  $("#metric-raw").textContent = result.raw_keywords.length;
  $("#metric-clean").textContent = result.cleaned_keywords.length;
  $("#metric-clusters").textContent = result.clusters.length;
  $("#metric-high").textContent = high;
  $("#metric-create").textContent = create;
  $("#metric-issues").textContent = result.cannibalization_issues.length;
  $("#generated-at").textContent = result.generated_at || "—";
}

function renderTopClusters() {
  const top = state.result.clusters.slice(0, 3);
  $("#top-clusters").innerHTML = top.map((cluster) => `
    <article class="priority-card">
      <span class="score">${cluster.priority_score}</span>
      <h3>${escapeHtml(cluster.name)}</h3>
      <p class="muted">${escapeHtml(cluster.main_keyword)} · ${cluster.keywords.length} запросов</p>
      <div class="chip-row">
        <span class="intent-chip ${cluster.intent}">${INTENT_LABELS[cluster.intent]}</span>
        <span class="action-chip ${cluster.action}">${ACTION_LABELS[cluster.action]}</span>
      </div>
    </article>
  `).join("");
}

function groupBy(items, keyGetter) {
  return items.reduce((acc, item) => {
    const key = keyGetter(item);
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
}

function renderCharts() {
  const clusters = state.result.clusters;
  const intentStats = groupBy(clusters, (cluster) => cluster.intent);
  const actionStats = groupBy(clusters, (cluster) => cluster.action);
  const intentColors = ["#1e6b5f", "#2563eb", "#c2413a", "#7856c9", "#b7791f", "#16805a", "#8a95a7"];
  const total = Math.max(1, clusters.length);
  let current = 0;
  const slices = Object.entries(intentStats).map(([intent, value], index) => {
    const start = current;
    const end = current + (value / total) * 360;
    current = end;
    return `${intentColors[index % intentColors.length]} ${start}deg ${end}deg`;
  });

  $("#intent-chart").innerHTML = `
    <div class="donut" style="background: conic-gradient(${slices.join(", ")})"></div>
    <div class="legend">
      ${Object.entries(intentStats).map(([intent, value], index) => `
        <div class="legend-row">
          <span><i class="legend-dot" style="background:${intentColors[index % intentColors.length]}"></i>${INTENT_LABELS[intent] || intent}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${Math.round(value / total * 100)}%;background:${intentColors[index % intentColors.length]}"></div></div>
          <b>${value}</b>
        </div>
      `).join("")}
    </div>
  `;

  $("#action-chart").innerHTML = Object.entries(actionStats).map(([action, value]) => `
    <div class="bar-row">
      <span>${ACTION_LABELS[action] || action}</span>
      <div class="bar-track"><div class="bar-fill" style="width:${Math.round(value / total * 100)}%"></div></div>
      <b>${value}</b>
    </div>
  `).join("");
}

function populateFilters() {
  const result = state.result;
  const intents = [...new Set(result.clusters.map((cluster) => cluster.intent))].sort();
  const actions = [...new Set(result.clusters.map((cluster) => cluster.action))].sort();
  $("#intent-filter").innerHTML = `<option value="all">Все</option>${intents.map((intent) => `<option value="${intent}">${INTENT_LABELS[intent] || intent}</option>`).join("")}`;
  $("#action-filter").innerHTML = `<option value="all">Все</option>${actions.map((action) => `<option value="${action}">${ACTION_LABELS[action] || action}</option>`).join("")}`;
}

function filteredClusters() {
  const query = normalize(state.filters.query);
  return state.result.clusters.filter((cluster) => {
    const matchesQuery = !query || normalize(`${cluster.name} ${cluster.main_keyword} ${cluster.recommended_url} ${cluster.keywords.join(" ")}`).includes(query);
    const matchesIntent = state.filters.intent === "all" || cluster.intent === state.filters.intent;
    const matchesAction = state.filters.action === "all" || cluster.action === state.filters.action;
    return matchesQuery && matchesIntent && matchesAction;
  });
}

function renderClusterTable() {
  const rows = filteredClusters();
  $("#cluster-table").innerHTML = rows.length ? rows.map((cluster, index) => `
    <tr>
      <td>${index + 1}</td>
      <td>
        <div class="cluster-name">${escapeHtml(cluster.name)}</div>
        <div class="cluster-key">${escapeHtml(cluster.main_keyword)} · ${cluster.keywords.length} запросов</div>
      </td>
      <td><span class="intent-chip ${cluster.intent}">${INTENT_LABELS[cluster.intent] || cluster.intent}</span></td>
      <td><code>${escapeHtml(cluster.recommended_url || "—")}</code></td>
      <td><span class="action-chip ${cluster.action}">${ACTION_LABELS[cluster.action] || cluster.action}</span></td>
      <td><span class="score-pill">${cluster.priority_score}</span></td>
      <td><button class="button" data-open-cluster="${escapeHtml(cluster.name)}">Открыть</button></td>
    </tr>
  `).join("") : `<tr><td colspan="7"><div class="empty-state">Ничего не найдено</div></td></tr>`;
}

function renderRisks() {
  const issues = state.result.cannibalization_issues;
  $("#risk-count").textContent = `${issues.length} проблем`;
  const visibleIssues = issues.slice(0, MAX_RENDERED_RISKS);
  const hiddenCount = Math.max(0, issues.length - visibleIssues.length);
  $("#risk-list").innerHTML = issues.length ? `
    ${visibleIssues.map((issue) => `
      <article class="risk-item ${issue.severity}">
        <h3>${riskTitle(issue)}</h3>
        <p>${escapeHtml(issue.recommendation)}</p>
      </article>
    `).join("")}
    ${hiddenCount ? `<div class="empty-state">Показаны первые ${MAX_RENDERED_RISKS} проблем. Полный список есть в JSON-экспорте.</div>` : ""}
  ` : `<div class="empty-state">Критичных пересечений не найдено</div>`;
}

function riskTitle(issue) {
  const severity = { critical: "Критично", high: "Высокий риск", medium: "Средний риск" }[issue.severity] || "Риск";
  const type = {
    keyword_overlap: "дубли запросов",
    url_conflict: "конфликт URL",
    intent_similarity: "похожие интенты"
  }[issue.type] || issue.type;
  return `${severity}: ${type}`;
}

function renderBriefs() {
  const briefs = state.result.briefs;
  $("#brief-list").innerHTML = briefs.map((brief) => `
    <article class="brief-item">
      <div class="section-head tight">
        <h3>${escapeHtml(brief.cluster)}</h3>
        <button class="button" data-copy-brief="${escapeHtml(brief.cluster)}">Копировать</button>
      </div>
      <div class="brief-grid">
        <div class="brief-field">
          <b>Title</b>
          <p>${escapeHtml(brief.title)}</p>
        </div>
        <div class="brief-field">
          <b>H1</b>
          <p>${escapeHtml(brief.h1)}</p>
        </div>
        <div class="brief-field full">
          <b>Description</b>
          <p>${escapeHtml(brief.description)}</p>
        </div>
        <div class="brief-field">
          <b>Структура</b>
          <ul>${brief.structure.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </div>
        <div class="brief-field">
          <b>LSI</b>
          <div class="keyword-cloud">${brief.lsi_words.map((word) => `<span class="chip">${escapeHtml(word)}</span>`).join("") || "—"}</div>
        </div>
      </div>
    </article>
  `).join("");
}

function renderExportPreview() {
  $("#export-preview").textContent = JSON.stringify({
    site_url: state.result.site_url,
    generated_at: state.result.generated_at,
    summary: {
      raw_keywords: state.result.raw_keywords.length,
      cleaned_keywords: state.result.cleaned_keywords.length,
      clusters: state.result.clusters.length,
      issues: state.result.cannibalization_issues.length
    },
    top_clusters: state.result.clusters.slice(0, 5).map((cluster) => ({
      name: cluster.name,
      score: cluster.priority_score,
      action: ACTION_LABELS[cluster.action],
      url: cluster.recommended_url
    }))
  }, null, 2);
}

function openDrawer(clusterName) {
  const cluster = state.result.clusters.find((item) => item.name === clusterName);
  if (!cluster) return;
  const brief = state.result.briefs.find((item) => item.cluster === cluster.name);
  $("#drawer-title").textContent = cluster.name;
  $("#drawer-body").innerHTML = `
    <div class="detail-block">
      <h3>Решение</h3>
      <div class="chip-row">
        <span class="score-pill">${cluster.priority_score}</span>
        <span class="intent-chip ${cluster.intent}">${INTENT_LABELS[cluster.intent]}</span>
        <span class="action-chip ${cluster.action}">${ACTION_LABELS[cluster.action]}</span>
      </div>
    </div>
    <div class="detail-block">
      <h3>Посадочная</h3>
      <p><code>${escapeHtml(cluster.recommended_url || "—")}</code></p>
    </div>
    <div class="detail-block">
      <h3>Запросы</h3>
      <div class="keyword-cloud">${cluster.keywords.map((keyword) => `<span class="chip">${escapeHtml(keyword)}</span>`).join("")}</div>
    </div>
    <div class="detail-block">
      <h3>Источники</h3>
      <div class="keyword-cloud">${Object.entries(cluster.sources || {}).map(([source, count]) => `<span class="chip">${source}: ${count}</span>`).join("")}</div>
    </div>
    ${brief ? `
      <div class="detail-block">
        <h3>ТЗ</h3>
        <p><b>Title:</b> ${escapeHtml(brief.title)}</p>
        <p><b>H1:</b> ${escapeHtml(brief.h1)}</p>
        <p><b>Description:</b> ${escapeHtml(brief.description)}</p>
      </div>
      <button class="button primary" data-copy-brief="${escapeHtml(brief.cluster)}">Скопировать ТЗ</button>
    ` : ""}
  `;
  $("#detail-drawer").classList.add("open");
  $("#detail-drawer").setAttribute("aria-hidden", "false");
}

function closeDrawer() {
  $("#detail-drawer").classList.remove("open");
  $("#detail-drawer").setAttribute("aria-hidden", "true");
}

function briefToText(brief) {
  return [
    `Кластер: ${brief.cluster}`,
    `URL: ${brief.url}`,
    `Title: ${brief.title}`,
    `H1: ${brief.h1}`,
    `Description: ${brief.description}`,
    `Главный ключ: ${brief.main_keyword}`,
    `Вторичные ключи: ${brief.secondary_keywords.join(", ")}`,
    `LSI: ${brief.lsi_words.join(", ")}`,
    `Структура:\n${brief.structure.map((item) => `- ${item}`).join("\n")}`,
    `Объём: ${brief.word_count} слов`
  ].join("\n");
}

function actionPlanText() {
  const result = state.result;
  const top = result.clusters.slice(0, 7).map((cluster, index) =>
    `${index + 1}. ${ACTION_LABELS[cluster.action]}: ${cluster.name} (${cluster.priority_score}) -> ${cluster.recommended_url}`
  ).join("\n");
  return [
    `Semantic Core Agent: ${result.site_url}`,
    `Собрано запросов: ${result.raw_keywords.length}`,
    `После чистки: ${result.cleaned_keywords.length}`,
    `Кластеров: ${result.clusters.length}`,
    `Рисков каннибализации: ${result.cannibalization_issues.length}`,
    "",
    "Топ действий:",
    top
  ].join("\n");
}

function exportCsv() {
  const headers = Object.keys(state.result.output_table[0] || {});
  const rows = state.result.output_table.map((row) => headers.map((header) => csvCell(row[header])).join(";"));
  downloadFile(`semantic-core-${slugify(state.result.site_url)}.csv`, [headers.join(";"), ...rows].join("\n"), "text/csv;charset=utf-8");
  showToast("CSV скачан");
}

function exportJson() {
  downloadFile(`semantic-core-${slugify(state.result.site_url)}.json`, JSON.stringify(state.result, null, 2), "application/json;charset=utf-8");
  showToast("JSON скачан");
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadFile(filename, content, type) {
  const blob = new Blob(["\ufeff", content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function copyText(text, message = "Скопировано") {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }
  showToast(message);
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 2200);
}

function getSavedTheme() {
  try {
    return localStorage.getItem(THEME_STORAGE_KEY) === "dark" ? "dark" : "light";
  } catch {
    return "light";
  }
}

function applyTheme(theme, persist = true) {
  const normalizedTheme = theme === "dark" ? "dark" : "light";
  document.documentElement.dataset.theme = normalizedTheme;
  const toggle = $("#theme-toggle");
  const icon = $("#theme-toggle-icon");

  if (toggle) {
    const isDark = normalizedTheme === "dark";
    toggle.setAttribute("aria-pressed", String(isDark));
    toggle.title = isDark ? "Включить светлую тему" : "Включить тёмную тему";
  }
  if (icon) {
    icon.textContent = normalizedTheme === "dark" ? "☀" : "☾";
  }

  if (persist) {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, normalizedTheme);
    } catch {
      // Настройки темы не критичны для работы пайплайна.
    }
  }
}

function initTheme() {
  applyTheme(document.documentElement.dataset.theme || getSavedTheme(), false);
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(nextTheme);
  showToast(nextTheme === "dark" ? "Тёмная тема включена" : "Светлая тема включена");
}

function resetForm() {
  $("#analysis-form").reset();
  $("#site-url").value = "";
  $("#business-description").value = "";
  $("#seed-keywords").value = "";
  $("#target-pages").value = "";
  $("#competitors").value = "";
  $("#commercial-priority").value = "";
  $("#mock-sources").checked = true;
  $("#competitor-mode").checked = true;
  showToast("Форма очищена");
}

function loadDemo() {
  $("#site-url").value = "mebel-dom.ru";
  $("#business-description").value = "интернет-магазин мебели, продаём диваны, кресла, пуфы";
  $("#seed-keywords").value = "купить диван\nугловой диван\nдиван кровать";
  $("#geo").value = "Москва";
  $("#language").value = "ru";
  $("#target-pages").value = "/catalog/divany/\n/catalog/uglovye-divany/\n/catalog/divany-krovati/";
  $("#competitors").value = "divan.ru\nhoff.ru";
  $("#commercial-priority").value = "диваны:5, кресла:3, пуфы:2";
  $("#mock-sources").checked = true;
  $("#competitor-mode").checked = true;
  runAnalysis();
}

function setActiveTab(tabName) {
  $$(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === tabName));
  $$(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === `tab-${tabName}`));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function bindEvents() {
  $("#analysis-form").addEventListener("submit", runAnalysis);
  $("#theme-toggle").addEventListener("click", toggleTheme);
  $("#demo-button").addEventListener("click", loadDemo);
  $("#reset-button").addEventListener("click", resetForm);
  $("#drawer-close").addEventListener("click", closeDrawer);
  $("#export-csv-button-2").addEventListener("click", exportCsv);
  $("#export-json-button-2").addEventListener("click", exportJson);
  $("#copy-plan-button-2").addEventListener("click", () => copyText(actionPlanText(), "План скопирован"));
  $("#copy-briefs-button").addEventListener("click", () => copyText(state.result.briefs.map(briefToText).join("\n\n---\n\n"), "ТЗ скопированы"));

  $("#cluster-search").addEventListener("input", (event) => {
    state.filters.query = event.target.value;
    renderClusterTable();
  });
  $("#intent-filter").addEventListener("change", (event) => {
    state.filters.intent = event.target.value;
    renderClusterTable();
  });
  $("#action-filter").addEventListener("change", (event) => {
    state.filters.action = event.target.value;
    renderClusterTable();
  });

  document.addEventListener("click", (event) => {
    const openButton = event.target.closest("[data-open-cluster]");
    if (openButton) {
      openDrawer(openButton.dataset.openCluster);
      return;
    }
    const copyBriefButton = event.target.closest("[data-copy-brief]");
    if (copyBriefButton) {
      const brief = state.result.briefs.find((item) => item.cluster === copyBriefButton.dataset.copyBrief);
      if (brief) copyText(briefToText(brief), "ТЗ скопировано");
    }
  });

  $$(".tab").forEach((tab) => tab.addEventListener("click", () => setActiveTab(tab.dataset.tab)));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeDrawer();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  bindEvents();
  renderPipelineSteps();
  runAnalysis();
});
