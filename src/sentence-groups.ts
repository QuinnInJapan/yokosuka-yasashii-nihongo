import type { SentenceEvidence } from "./types";

export type SentenceMatchRole = "original" | "yasashii" | "related";

export interface SentenceEvidenceGroup {
  key: string;
  label: string;
  role: SentenceMatchRole;
  count: number;
  sourceShortNames: string[];
  sentences: SentenceEvidence[];
}

const roleRank: Record<SentenceMatchRole, number> = {
  original: 0,
  yasashii: 1,
  related: 2,
};

function evidenceRank(group: SentenceEvidenceGroup): number {
  if (group.role === "original" && group.label === "そのまま") return 1;
  return 0;
}

function includesText(text: string, query: string): boolean {
  return text.toLocaleLowerCase().includes(query.toLocaleLowerCase());
}

function findKnownRendering(sentence: SentenceEvidence, renderings: string[]): string {
  const sortedRenderings = [...renderings]
    .filter(Boolean)
    .sort((a, b) => b.length - a.length || a.localeCompare(b, "ja"));

  return sortedRenderings.find((rendering) => includesText(sentence.yasashii, rendering)) ?? "";
}

function classifySentence(sentence: SentenceEvidence, query: string, renderings: string[]) {
  if (!query) {
    return { role: "related" as const, label: "関連文例" };
  }

  const originalMatch = includesText(sentence.original, query);
  if (originalMatch) {
    if (includesText(sentence.yasashii, query)) {
      return { role: "original" as const, label: "そのまま" };
    }

    const rendering = findKnownRendering(sentence, renderings);
    return { role: "original" as const, label: rendering || "文全体で言い換え" };
  }

  return { role: "related" as const, label: "関連文例" };
}

export function groupSentenceEvidence(
  sentences: SentenceEvidence[],
  query: string,
  renderings: string[],
): SentenceEvidenceGroup[] {
  const groups = new Map<string, SentenceEvidenceGroup>();

  for (const sentence of sentences) {
    const classification = classifySentence(sentence, query.trim(), renderings);
    const key = `${classification.role}\u0000${classification.label}`;
    const group = groups.get(key) ?? {
      key,
      label: classification.label,
      role: classification.role,
      count: 0,
      sourceShortNames: [],
      sentences: [],
    };

    group.count += 1;
    group.sentences.push(sentence);
    if (sentence.sourceShortName && !group.sourceShortNames.includes(sentence.sourceShortName)) {
      group.sourceShortNames.push(sentence.sourceShortName);
      group.sourceShortNames.sort((a, b) => a.localeCompare(b, "ja"));
    }
    groups.set(key, group);
  }

  return [...groups.values()].sort((a, b) => (
    roleRank[a.role] - roleRank[b.role]
    || evidenceRank(a) - evidenceRank(b)
    || b.count - a.count
    || a.label.localeCompare(b.label, "ja")
  ));
}
