import { useEffect, useState } from "react";
import { z } from "zod";
import { FileSchema, FileSchemaType } from "../types/ftpSchema";

export const useServerState = () => {
  const [model, setModel] = useState([{} as FileSchemaType]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    const fetchState = async () => {
      const event = new EventSource(
        `http://${import.meta.env.VITE_SeedSync_IP}/server/stream`
      );

      // event.onerror = () => {
      //   console.error("Error ");
      // };

      event.onopen = () => {
        // console.log("Connected to server");

        event.addEventListener("model-init", (e) => {
          console.log(JSON.parse(e.data));
          const data = JSON.parse(e.data);
          const parse = z.array(FileSchema).safeParse(data);

          if (parse.success) {
            setModel(JSON.parse(e.data));
          } else {
            data.forEach((d: unknown) => {
              const parsed = FileSchema.safeParse(d);
              if (parsed.error) {
                console.error(parsed.error);
                console.log(parse.data);
              }
            });
          }
          setIsLoading(false);
        });

        event.addEventListener("model-removed", (e) => {
          const a = JSON.parse(e.data);
          const b = model.filter((m) => a.file !== m);
          setModel(b);
          setIsLoading(false);
        });

        event.addEventListener("model-updated", (e) => {
          const data = JSON.parse(e.data);
          console.log(model);
          //   console.log(a.old_file);
          const b = model.filter((m) => a.old_file !== m);
          b.push(a.new_file);
          setModel(b);
          setIsLoading(false);
        });
      };
    };

    fetchState();
  }, []);

  return { model, isLoading };
};
