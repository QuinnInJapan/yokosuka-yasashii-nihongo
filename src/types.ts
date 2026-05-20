export interface SourceSummary {
  sourceId: string;
  sourceOrg: string;
  sourceDocument: string;
  sourceDate: string;
  sourceShortName: string;
  sourceCategory: string;
  sourceUrl: string;
  domains: string[];
  notes: string;
  retainOriginal: boolean;
  isNegativeExample: boolean;
}

export interface TermEvidence {
  original: string;
  yasashii: string;
  sourceCount: number;
  sourceOrgs: string[];
  sourceShortNames: string[];
  sourceCategories: string[];
  domains: string[];
  notes: string[];
  retainOriginal: boolean;
  isNegativeExample: boolean;
  sources: SourceSummary[];
  jlpt: string;
  searchText: string;
}

export interface SentenceEvidence extends SourceSummary {
  original: string;
  yasashii: string;
  searchText: string;
}

export interface AppPayload {
  meta: {
    termCount: number;
    sentenceCount: number;
    sourceCount: number;
  };
  filters: {
    domains: string[];
    sourceCategories: string[];
  };
  terms: TermEvidence[];
  sentences: SentenceEvidence[];
}
