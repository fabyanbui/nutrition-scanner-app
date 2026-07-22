export interface LocalJobData {
  jobId: string;
  filename: string;
  sizeBytes: number;
  contentType: string;
  base64Image?: string;
  createdAt: number;
}

const localJobs = new Map<string, LocalJobData>();

export function createLocalJob(data: Omit<LocalJobData, "createdAt">): string {
  const job: LocalJobData = {
    ...data,
    createdAt: Date.now(),
  };
  localJobs.set(data.jobId, job);
  return data.jobId;
}

export function getLocalJob(jobId: string): LocalJobData | undefined {
  return localJobs.get(jobId);
}
