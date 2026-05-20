export function formatSourceSummary(names: string[], cap = 2): string {
  const cleanedNames = Array.from(
    new Set(names.map((name) => name.trim()).filter(Boolean)),
  );

  if (cleanedNames.length <= cap) {
    return cleanedNames.join("、");
  }

  return `${cleanedNames.slice(0, cap).join("、")}、他${cleanedNames.length - cap}件`;
}
