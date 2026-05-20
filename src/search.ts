import type { TermEvidence } from "./types";

export function scoreTerm(term: TermEvidence, query: string): number {
  if (!query) return term.sourceCount;
  const normalizedQuery = query.toLocaleLowerCase();
  const headword = term.original.toLocaleLowerCase();

  if (headword === normalizedQuery) return 1000 + term.sourceCount;
  if (headword.includes(normalizedQuery)) return 800 + term.sourceCount;
  return 0;
}
