import { z } from "zod";

export type FileSchemaType = {
  name: string;
  is_dir: boolean;
  state: string;
  remote_size: number | null;
  local_size: number | null;
  downloading_speed: number | null;
  eta: number | null;
  is_extractable: boolean;
  local_created_timestamp: string | null;
  local_modified_timestamp: string | null;
  remote_created_timestamp: string | null;
  remote_modified_timestamp: string | null;
  full_path: string;
  children: FileSchemaType[];
};

export const FileSchema: z.ZodSchema<FileSchemaType> = z.object({
  name: z.string(),
  is_dir: z.boolean(),
  state: z.string(),
  remote_size: z.nullable(z.number()),
  local_size: z.nullable(z.number()),
  downloading_speed: z.nullable(z.number()),
  eta: z.nullable(z.number()),
  is_extractable: z.boolean(),
  local_created_timestamp: z.nullable(z.string()),
  local_modified_timestamp: z.nullable(z.string()),
  remote_created_timestamp: z.nullable(z.string()),
  remote_modified_timestamp: z.nullable(z.string()),
  full_path: z.string(),
  children: z.array(z.lazy(() => FileSchema)),
});

export type File = z.infer<typeof FileSchema>;

export const updateFTP = z.object({ new: FileSchema, old: FileSchema });

export type Config = {
  general: {
    debug: boolean;
    verbose: boolean;
  };
  lftp: {
    remote_address: string;
    remote_username: string;
    remote_password: string;
    remote_port: number;
    remote_path: string;
    local_path: string;
    remote_path_to_scan_script: string;
    use_ssh_key: boolean;
    num_max_parallel_downloads: number;
    num_max_parallel_files_per_download: number;
    num_max_connections_per_root_file: number;
    num_max_connections_per_dir_file: number;
    num_max_total_connections: number;
    use_temp_file: boolean;
  };
  controller: {
    interval_ms_remote_scan: number;
    interval_ms_local_scan: number;
    interval_ms_downloading_scan: number;
    extract_path: string;
    use_local_path_as_extract_path: boolean;
  };
  web: {
    port: number;
  };
  autoqueue: {
    enabled: boolean;
    patterns_only: boolean;
    auto_extract: boolean;
  };
};

export const ConfigSchema = z.object({
  general: z.object({
    debug: z.boolean(),
    verbose: z.boolean(),
  }),
  lftp: z.object({
    remote_address: z.string(),
    remote_username: z.string(),
    remote_password: z.string(),
    remote_port: z.number(),
    remote_path: z.string(),
    local_path: z.string(),
    remote_path_to_scan_script: z.string(),
    use_ssh_key: z.boolean(),
    num_max_parallel_downloads: z.number(),
    num_max_parallel_files_per_download: z.number(),
    num_max_connections_per_root_file: z.number(),
    num_max_connections_per_dir_file: z.number(),
    num_max_total_connections: z.number(),
    use_temp_file: z.boolean(),
  }),
  controller: z.object({
    interval_ms_remote_scan: z.number(),
    interval_ms_local_scan: z.number(),
    interval_ms_downloading_scan: z.number(),
    extract_path: z.string(),
    use_local_path_as_extract_path: z.boolean(),
  }),
  web: z.object({
    port: z.number(),
  }),
  autoqueue: z.object({
    enabled: z.boolean(),
    patterns_only: z.boolean(),
    auto_extract: z.boolean(),
  }),
});
