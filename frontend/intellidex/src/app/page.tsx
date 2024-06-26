import Image from "next/image";
import { Fragment } from "react";

export default function Home() {
  return (
    <div className="grid grid-cols-12 grid-rows-12 w-screen h-screen bg-[radial-gradient(ellipse_at_top_left,rgba(11,149,181,1)_60%,rgba(218,248,255,1)_100%)]">
      <div className="col-start-7 col-end-13 row-start-3 row-end-13">
        <img src="/rocket.png" width={800}></img>
      </div>
      <div className="col-start-3 row-start-4 col-end-6 row-end-10">
        <div className="font-['Bebas_Neue'] text-white text-9xl mb-2 hover:translate-x-1 hover:-translate-y-1 transition-all group">
          make your database wickedly
          <p className="custom-anim bg-clip-text text-transparent">fast</p>
        </div>
        <button className="bg-[linear-gradient(90deg,hsla(58,100%,68%,1)_0%,_hsla(45,80%,81%,1)100%)] rounded-lg  hover:translate-x-1 hover:-translate-y-1 hover:shadow transition">
          <p className="font-['Roboto'] text-xl mx-12 my-4 font-medium text-black ">
            Get Started
          </p>
        </button>
      </div>
      <div className="col-start-3 col-end-11 row-start-1 row-end-3 flex justify-between items-center font-[Roboto]">
        <div className="w-[75px] h-[75px] my-auto hover:rotate-45 transition-all">
          <img src="/ln.png" className="w-full h-full "></img>
        </div>

        <div className="flex text-xl font-medium">
          <div className="mx-5 group">
            <p>About us</p>
            <div className="h-1 bg-white w-0 group-hover:w-full transition-all"></div>
          </div>
          <div className="mx-5 group">
            <p>How it works</p>
            <div className="h-1 bg-white w-0 group-hover:w-full transition-all"></div>
          </div>
          <div className="mx-5 group">
            <p>Get In Touch</p>
            <div className="h-1 bg-white w-0 group-hover:w-full transition-all"></div>
          </div>
        </div>

        <button className="rounded-lg bg-transparent border-4 group hover:bg-white hover:text-black transition-all">
          <p className=" text-xl font-semibold mx-8 my-4 ">Log In</p>
        </button>
      </div>
    </div>
  );
}
