import Image from "next/image";
import { Fragment } from "react";

function BackgroundLayer() {
  return (
    <div className="grid grid-cols-12 grid-rows-12 w-screen h-screen bg-[radial-gradient(circle_at_top_left,rgba(155,214,228,1)_0%,rgba(218,248,255,1)_100%)]">
      <div className="col-start-6 col-end-13 row-start-5 row-end-13">
        <video src="/db_merged.mp4" width={1200} autoPlay muted loop></video>
      </div>
      <div className="col-start-2 row-start-3 col-end-5 row-end 10">
        <p className="font-['Bebas_Neue'] text-black text-9xl">
          make your database wickedly fast
        </p>
      </div>
    </div>
  );
}

export default function Home() {
  return <BackgroundLayer />;
}
