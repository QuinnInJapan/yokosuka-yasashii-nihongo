const SEARCH_PARAM = "q";

export function readSearchQuery(search: string): string {
  return new URLSearchParams(search).get(SEARCH_PARAM) ?? "";
}

export function buildSearchUrl(currentHref: string, query: string): string {
  const url = new URL(currentHref);
  const trimmed = query.trim();
  if (trimmed) {
    url.searchParams.set(SEARCH_PARAM, trimmed);
  } else {
    url.searchParams.delete(SEARCH_PARAM);
  }
  return url.toString();
}
