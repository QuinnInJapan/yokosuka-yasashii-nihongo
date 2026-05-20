import type { TermEvidence } from "./types";

export interface TermGroup {
  original: string;
  terms: TermEvidence[];
  sourceCount: number;
  sourceShortNames: string[];
  retainOriginal: boolean;
  isNegativeExample: boolean;
}

export function groupTermsByHeadword(terms: TermEvidence[]): TermGroup[] {
  const groups = new Map<string, TermEvidence[]>();

  for (const term of terms) {
    const group = groups.get(term.original) ?? [];
    group.push(term);
    groups.set(term.original, group);
  }

  return [...groups.entries()].map(([original, groupTerms]) => {
    const sourceOrgs = new Set<string>();
    const sourceShortNames = new Set<string>();
    groupTerms.forEach((term) => {
      term.sourceOrgs.forEach((sourceOrg) => sourceOrgs.add(sourceOrg));
      term.sourceShortNames.forEach((sourceShortName) => sourceShortNames.add(sourceShortName));
    });

    return {
      original,
      terms: groupTerms,
      sourceCount: sourceOrgs.size,
      sourceShortNames: [...sourceShortNames].sort(),
      retainOriginal: groupTerms.some((term) => term.retainOriginal),
      isNegativeExample: groupTerms.some((term) => term.isNegativeExample)
    };
  }).sort((a, b) => b.sourceCount - a.sourceCount || a.original.localeCompare(b.original, "ja"));
}
