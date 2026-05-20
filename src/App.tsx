import { useEffect, useMemo, useState } from "react";
import { appData } from "./generated/app-data";
import { scoreTerm } from "./search";
import { groupSentenceEvidence, type SentenceEvidenceGroup } from "./sentence-groups";
import { formatSourceSummary } from "./source-summary";
import { groupTermsByHeadword, type TermGroup } from "./term-groups";
import { getHighlightParts } from "./text-highlight";
import type { SentenceEvidence, TermEvidence } from "./types";
import { buildSearchUrl, readSearchQuery } from "./url-state";

type EntryTypeFilter = "all" | "term" | "sentence";

interface ResultSet {
  terms: TermEvidence[];
  sentences: SentenceEvidence[];
}

function domainOk(item: { domains: string[] }, domain: string): boolean {
  return !domain || item.domains.includes(domain);
}

function categoryOk(item: TermEvidence | SentenceEvidence, category: string): boolean {
  if (!category) return true;
  if ("sourceCategories" in item) return item.sourceCategories.includes(category);
  return item.sourceCategory === category;
}

function Chip({ label, tone = "" }: { label: string; tone?: "warn" | "bad" | "" }) {
  if (!label) return null;
  return <span className={`chip ${tone}`}>{label}</span>;
}

function HighlightText({ text, query, skipExact = false }: { text: string; query: string; skipExact?: boolean }) {
  if (skipExact && query && text.toLocaleLowerCase() === query.toLocaleLowerCase()) {
    return <>{text}</>;
  }

  return (
    <>
      {getHighlightParts(text, query).map((part, index) => (
        part.match ? <mark key={index}>{part.text}</mark> : <span key={index}>{part.text}</span>
      ))}
    </>
  );
}

function Summary({ terms, sentences }: ResultSet) {
  const sourceOrgs = new Set<string>();
  terms.forEach((term) => term.sourceOrgs.forEach((org) => sourceOrgs.add(org)));
  sentences.forEach((sentence) => {
    if (sentence.sourceOrg) sourceOrgs.add(sentence.sourceOrg);
  });

  return (
    <div className="summary" aria-label="検索サマリー">
      <span><strong>用語前例</strong> {terms.length}件</span>
      <span><strong>文例</strong> {sentences.length}件</span>
      <span><strong>出典組織</strong> {sourceOrgs.size}組織</span>
    </div>
  );
}

function TermRenderingRow({ term, query }: { term: TermEvidence; query: string }) {
  return (
    <div className="term-rendering-row">
      <div>
        <div className="yasashii"><HighlightText text={term.yasashii} query={query} /></div>
        <div className="meta">
          {term.isNegativeExample ? <Chip label="非推奨例" tone="bad" /> : null}
          <span>出典 {term.sourceCount}: {formatSourceSummary(term.sourceShortNames)}</span>
          {term.notes.length ? <><br /><span>備考: {term.notes.join("；")}</span></> : null}
        </div>
      </div>
    </div>
  );
}

function TermGroupCard({ group, query }: { group: TermGroup; query: string }) {
  return (
    <article className="card term-group">
      <div className="term-group-headword">
        <div>
          <div className="label">原文</div>
          <div className="original"><HighlightText text={group.original} query={query} skipExact /></div>
        </div>
        <div className="headword-stats" aria-label={`${group.terms.length} 前例、${group.sourceCount} 出典`}>
          <span>{group.terms.length} 前例</span>
          <span>{group.sourceCount} 出典</span>
          {group.isNegativeExample ? <Chip label="非推奨例" tone="bad" /> : null}
        </div>
      </div>
      <div className="term-renderings">
        <div className="result-header term-rendering-row">
          <div>やさしい日本語の前例</div>
        </div>
        {group.terms.map((term) => <TermRenderingRow key={`${term.original}-${term.yasashii}`} term={term} query={query} />)}
      </div>
    </article>
  );
}

function SentenceCard({ sentence, query }: { sentence: SentenceEvidence; query: string }) {
  return (
    <div className="sentence-example sentence-row">
      <div>
        <div className="label">原文</div>
        <div className="sentence-text"><HighlightText text={sentence.original} query={query} /></div>
      </div>
      <div>
        <div className="label">やさしい日本語</div>
        <div className="sentence-text"><HighlightText text={sentence.yasashii} query={query} /></div>
      </div>
      <div className="meta">
        <span>{sentence.sourceShortName || sentence.sourceOrg}</span>
        {sentence.isNegativeExample ? <Chip label="非推奨例" tone="bad" /> : null}
      </div>
    </div>
  );
}

function SourceMeta({ group }: { group: SentenceEvidenceGroup }) {
  return (
    <div className="sentence-group-meta">
      <strong>{group.count}件</strong>
      {group.sourceShortNames.length ? (
        <span>出典: {formatSourceSummary(group.sourceShortNames)}</span>
      ) : null}
    </div>
  );
}

function SentenceGroupHeader({ group }: { group: SentenceEvidenceGroup }) {
  return (
    <header className="sentence-group-header">
      <div>
        <h3 className="sentence-pattern">{group.label}</h3>
      </div>
      <SourceMeta group={group} />
    </header>
  );
}

function SentenceGroupBody({
  group,
  query,
  expanded,
  onToggle,
}: {
  group: SentenceEvidenceGroup;
  query: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  const visibleSentences = expanded ? group.sentences : group.sentences.slice(0, 2);
  const hiddenCount = Math.max(group.sentences.length - 2, 0);

  return (
    <div className="sentence-group-body">
      <div className="sentence-examples">
        {visibleSentences.map((sentence, index) => (
          <SentenceCard key={`${sentence.sourceId}-${group.key}-${index}`} sentence={sentence} query={query} />
        ))}
      </div>
      {hiddenCount > 0 ? (
        <div className="sentence-group-actions">
          <button className="button subtle" type="button" onClick={onToggle}>
            {expanded ? "このパターンを少なく表示" : `残り${hiddenCount}件を表示`}
          </button>
        </div>
      ) : null}
    </div>
  );
}

function SentenceGroupCard({
  group,
  query,
  expanded,
  onToggle,
}: {
  group: SentenceEvidenceGroup;
  query: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <article className={`sentence-group-card ${group.role}`}>
      <SentenceGroupHeader group={group} />
      <SentenceGroupBody group={group} query={query} expanded={expanded} onToggle={onToggle} />
    </article>
  );
}

export function App() {
  const [query, setQuery] = useState(() => readSearchQuery(window.location.search));
  const [domain, setDomain] = useState("");
  const [category, setCategory] = useState("");
  const [type, setType] = useState<EntryTypeFilter>("all");
  const [termLimit, setTermLimit] = useState(12);
  const [expandedSentenceGroups, setExpandedSentenceGroups] = useState<Set<string>>(() => new Set());

  const normalizedQuery = query.trim().toLowerCase();

  useEffect(() => {
    const nextUrl = buildSearchUrl(window.location.href, query);
    if (nextUrl !== window.location.href) {
      window.history.replaceState(null, "", nextUrl);
    }
  }, [query]);

  useEffect(() => {
    function handlePopState() {
      setQuery(readSearchQuery(window.location.search));
      resetLimits();
    }

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const results = useMemo<ResultSet>(() => {
    const terms = type === "sentence" ? [] : appData.terms
      .map((term) => ({ term, score: scoreTerm(term, normalizedQuery) }))
      .filter(({ term, score }) => (!normalizedQuery || score > 0) && domainOk(term, domain) && categoryOk(term, category))
      .sort((a, b) => b.score - a.score || b.term.sourceCount - a.term.sourceCount)
      .map(({ term }) => term);

    const sentences = type === "term" ? [] : appData.sentences
      .filter((sentence) => (!normalizedQuery || sentence.searchText.includes(normalizedQuery)) && domainOk(sentence, domain) && categoryOk(sentence, category));

    return { terms, sentences };
  }, [category, domain, normalizedQuery, type]);

  function resetLimits() {
    setTermLimit(12);
    setExpandedSentenceGroups(new Set());
  }

  function toggleSentenceGroup(groupKey: string) {
    setExpandedSentenceGroups((current) => {
      const next = new Set(current);
      if (next.has(groupKey)) {
        next.delete(groupKey);
      } else {
        next.add(groupKey);
      }
      return next;
    });
  }

  const hasSearchContext = Boolean(normalizedQuery || domain || category);
  const termGroups = useMemo(() => groupTermsByHeadword(results.terms), [results.terms]);
  const visibleTermGroups = termGroups.slice(0, termLimit);
  const sentenceRenderings = useMemo(() => (
    normalizedQuery
      ? appData.terms
        .filter((term) => scoreTerm(term, normalizedQuery) > 0 && domainOk(term, domain) && categoryOk(term, category))
        .map((term) => term.yasashii)
      : []
  ), [category, domain, normalizedQuery]);
  const sentenceGroups = useMemo(
    () => groupSentenceEvidence(results.sentences, normalizedQuery, sentenceRenderings),
    [normalizedQuery, results.sentences, sentenceRenderings],
  );

  return (
    <div className="app">
      <main>
        <aside className="search-panel" aria-label="検索">
          <header className="app-intro">
            <h1 className="title">やさしい日本語 前例リファレンス</h1>
            <p className="subtitle">公的資料にある書き換え例を検索し、前例にもとづいて判断するための参照ツールです。</p>
          </header>
          <div className="search-row">
            <input
              id="query"
              className="query"
              type="search"
              autoComplete="off"
              placeholder="調べたい語を入力（例：避難、届出、津波）"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                resetLimits();
              }}
            />
            <button
              className="button"
              type="button"
              onClick={() => {
                setQuery("");
                resetLimits();
              }}
            >
              クリア
            </button>
          </div>
          <div className="filters">
            <select className="filter" aria-label="分野" value={domain} onChange={(event) => { setDomain(event.target.value); resetLimits(); }}>
              <option value="">すべての分野</option>
              {appData.filters.domains.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <select className="filter" aria-label="出典種別" value={category} onChange={(event) => { setCategory(event.target.value); resetLimits(); }}>
              <option value="">すべての出典種別</option>
              {appData.filters.sourceCategories.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <select className="filter" aria-label="種別" value={type} onChange={(event) => { setType(event.target.value as EntryTypeFilter); resetLimits(); }}>
              <option value="all">用語と文例</option>
              <option value="term">用語のみ</option>
              <option value="sentence">文例のみ</option>
            </select>
          </div>
          <Summary terms={results.terms} sentences={results.sentences} />
          {hasSearchContext ? (
            <nav className="evidence-nav" aria-label="結果セクション">
              <a href="#term-section">用語前例 {results.terms.length}件</a>
              <a href="#sentence-section">文例 {results.sentences.length}件</a>
            </nav>
          ) : null}
        </aside>

        <section className="results-stack">
          <section id="term-section">
            <h2 className="section-title">用語前例</h2>
            {!hasSearchContext ? (
              <div className="empty">検索語を入力してください。例: 避難、避難指示、届出、津波</div>
            ) : visibleTermGroups.length ? (
              <>
                {visibleTermGroups.map((group) => <TermGroupCard key={group.original} group={group} query={normalizedQuery} />)}
                {termGroups.length > visibleTermGroups.length ? <button className="button" type="button" onClick={() => setTermLimit(termLimit + 12)}>もっと見る</button> : null}
              </>
            ) : (
              <div className="empty">用語前例は見つかりませんでした。</div>
            )}
          </section>
          <section id="sentence-section">
            <div className="section-heading-row">
              <h2 className="section-title">文例</h2>
            </div>
            {!hasSearchContext ? (
              <div className="empty">文例もここに表示されます。</div>
            ) : sentenceGroups.length ? (
              <>
                {sentenceGroups.map((group) => (
                  <SentenceGroupCard
                    key={group.key}
                    group={group}
                    query={normalizedQuery}
                    expanded={expandedSentenceGroups.has(group.key)}
                    onToggle={() => toggleSentenceGroup(group.key)}
                  />
                ))}
              </>
            ) : (
              <div className="empty">文例は見つかりませんでした。</div>
            )}
          </section>
        </section>
      </main>
    </div>
  );
}
