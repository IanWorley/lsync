import { Button, ButtonGroup } from "@nextui-org/button";
import { createFileRoute } from "@tanstack/react-router";
import { useServerState } from "../hooks/grabState";
import { FileSchemaType } from "../types/ftpSchema";

export const Route = createFileRoute("/")({
  component: Home,
});

function Home() {
  const { model, isLoading } = useServerState();
  console.log(model);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <div className="p-3">
        {model.map((f) => (
          <FtpFile key={f.name} f={f} />
        ))}
      </div>
    </>
  );
}

interface FtpFileProps {
  f: FileSchemaType;
}

function FtpFile(props: FtpFileProps) {
  const { f } = props;
  const takeSize = (size: number): string => {
    // guess size of the unit by looking at the file size
    const units = ["B", "KB", "MB", "GB", "TB"];
    let unitIndex = 0;
    let unitSize = size;
    while (unitSize > 1024) {
      unitSize /= 1024;
      unitIndex++;
    }
    return `${unitSize.toFixed(2)} ${units[unitIndex]}`;
  };

  return (
    <div className="bg-[#18181b] p-2 m-3">
      <div className="flex justify-between">
        <p> {f.name} </p>
        <ButtonGroup>
          <Button>Queue</Button>
          <Button>Pause</Button>
          <Button>Delete Local</Button>
          <Button>Delete Remote</Button>
        </ButtonGroup>
      </div>
      <p>
        {takeSize(f.local_size ?? 0)} / {takeSize(f.remote_size ?? 0)}
      </p>
      <p> {f.downloading_speed} </p>
      {f.state === "downloading" ? <p> ETA {f.eta}</p> : null}
    </div>
  );
}
