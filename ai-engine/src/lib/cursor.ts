import { api } from "@/lib/api";

/** Where the learner is, independent of whether today's session exists. */
export type CursorTopic = {
  topic_id: number;
  slug: string | null;
  name: string;
  domain: string | null;
  module_name: string | null;
  estimated_minutes: number;
};

export type Cursors = {
  core: CursorTopic | null;
  dsa: CursorTopic | null;
};

export const getCursors = () => api<Cursors>("/api/cursor");
