import type { CurriculumTree, TopicNode } from "./curriculum";

export type DomainConfig = { key: string; label: string };

export const DOMAIN_CONFIG: DomainConfig[] = [
  { key: "foundations", label: "Foundations" },
  { key: "dsa", label: "DSA" },
  { key: "java", label: "Java" },
  { key: "ml", label: "Machine Learning" },
  { key: "mathematics", label: "Mathematics" },
  { key: "backend", label: "Backend" },
  { key: "software-engineering", label: "Software Engineering" },
  // Aliases for future curriculum expansion — normalized to canonical keys above
  { key: "dl", label: "Deep Learning" },
  { key: "cv", label: "Computer Vision" },
  { key: "nlp", label: "NLP" },
  { key: "genai", label: "GenAI" },
  { key: "ai-engineering", label: "AI Engineering" },
];

const CANONICAL_MAP: Record<string, string> = {
  foundations: "foundations",
  java: "java",
  dsa: "dsa",
  ml: "ml",
  "machine-learning": "ml",
  dl: "dl",
  "deep-learning": "dl",
  cv: "cv",
  "computer-vision": "cv",
  nlp: "nlp",
  genai: "genai",
  "generative-ai": "genai",
  "ai-engineering": "ai-engineering",
  mathematics: "mathematics",
  math: "mathematics",
  backend: "backend",
  "software-engineering": "software-engineering",
  se: "software-engineering",
  mlops: "software-engineering",
};

export function normalizeDomainKey(raw?: string | null): string | null {
  if (!raw) return null;
  const k = raw.toLowerCase().trim();
  return CANONICAL_MAP[k] ?? k;
}

export function getAllTopics(tree: CurriculumTree | null): TopicNode[] {
  if (!tree) return [];
  return tree.tracks.flatMap((t) => t.levels.flatMap((l) => l.subjects.flatMap((s) => s.modules.flatMap((m) => m.topics))));
}

function isLearnableTopic(topic: TopicNode): boolean {
  // Per spec: exclude NON_LEARNABLE_CONTAINER etc. Backend currently marks all as learnable;
  // we treat a topic as learnable if it has learner-visible status and is not explicitly container.
  // If backend adds a flag, filter here. For now all topics with domain/slug are learnable.
  if (!topic.slug) return false;
  return true;
}

export function getCompletedTopicCount(tree: CurriculumTree | null): { completed: number; total: number } {
  const all = getAllTopics(tree).filter(isLearnableTopic);
  const completed = all.filter((t) => t.status === "completed").length;
  return { completed, total: all.length };
}

export function getDomainProgress(tree: CurriculumTree | null): { key: string; label: string; completed: number; total: number; percent: number }[] {
  const all = getAllTopics(tree).filter(isLearnableTopic);
  const byKey = new Map<string, TopicNode[]>();
  for (const t of all) {
    const k = normalizeDomainKey(t.domain) ?? "other";
    if (!byKey.has(k)) byKey.set(k, []);
    byKey.get(k)!.push(t);
  }
  // Include all configured keys even with 0 total for transparency
  const seen = new Set<string>(byKey.keys());
  for (const cfg of DOMAIN_CONFIG) seen.add(cfg.key);
  const result: { key: string; label: string; completed: number; total: number; percent: number }[] = [];
  for (const key of Array.from(seen).sort()) {
    const cfg = DOMAIN_CONFIG.find((d) => d.key === key);
    const label = cfg?.label ?? key;
    const list = byKey.get(key) ?? [];
    const total = list.length;
    const completed = list.filter((t) => t.status === "completed").length;
    const percent = total ? Math.round((completed / total) * 100) : 0;
    if (total === 0 && !DOMAIN_CONFIG.some((d) => d.key === key)) continue;
    // Only include configured or non-empty
    if (total === 0) {
      // For dl/cv/nlp/genai with 0 total, still show as 0/0 if curriculum lacks them
      result.push({ key, label, completed: 0, total: 0, percent: 0 });
    } else {
      result.push({ key, label, completed, total, percent });
    }
  }
  return result;
}

export function getTrackProgress(tree: CurriculumTree | null): Map<string, { completed: number; total: number; percent: number }> {
  const m = new Map<string, { completed: number; total: number; percent: number }>();
  if (!tree) return m;
  for (const track of tree.tracks) {
    const topics = track.levels.flatMap((l) => l.subjects.flatMap((s) => s.modules.flatMap((mod) => mod.topics))).filter(isLearnableTopic);
    const total = topics.length;
    const completed = topics.filter((t) => t.status === "completed").length;
    const percent = total ? Math.round((completed / total) * 100) : 0;
    m.set(track.name, { completed, total, percent });
  }
  return m;
}

export function getWeeklyStudyStats(data: { scheduled_minutes: number; capacity_minutes: number; remaining_minutes: number } | null | undefined) {
  if (!data) return null;
  return {
    planned: data.scheduled_minutes,
    capacity: data.capacity_minutes,
    available: data.remaining_minutes,
  };
}
