import Image from "next/image";
import { Fragment } from "react";

export default function Home() {
  return (
    <div className="grid grid-cols-12 grid-rows-12 w-screen h-screen bg-[radial-gradient(ellipse_at_top_left,rgba(155,214,228,1)_60%,rgba(218,248,255,1)_100%)]">
      <div className="col-start-7 col-end-13 row-start-3 row-end-13">
        <img src="/rocket.png" width={800}></img>
        {/* <video src="/db_merged.mp4" width={1200} autoPlay muted loop></video> */}
      </div>
      <div className="col-start-2 row-start-3 col-end-5 row-end-10">
        <p className="font-['Bebas_Neue'] text-black text-9xl mb-2">
          make your database wickedly fast
        </p>
        <button className="bg-[linear-gradient(90deg,hsla(58,100%,68%,1)_0%,_hsla(45,80%,81%,1)100%)] rounded-md">
          <p className="font-['Roboto'] text-xl mx-12 my-4 font-medium text-black">
            Get Started
          </p>
        </button>
      </div>
    </div>
  );
}
