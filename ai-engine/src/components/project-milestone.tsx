"use client";

export const ProjectMilestone = () => {
  return (
    <div className="bg-white dark:bg-zinc-800 rounded-xl p-6 shadow-sm">
      <h2 className="text-xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">
        Current Project Milestone
      </h2>
      <div className="space-y-4">
        <div className="p-4 border rounded-md border-zinc-200 dark:border-zinc-700">
          <h3 className="font-medium text-zinc-700 dark:text-zinc-300">No active project</h3>
          <p className="text-zinc-500 dark:text-zinc-400 mt-1 text-sm">
            Project tracking will be added in a later phase.
          </p>
        </div>
      </div>
    </div>
  );
};
