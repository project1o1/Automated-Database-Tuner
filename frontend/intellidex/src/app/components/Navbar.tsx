import Image from "next/image";

export default function Navbar() {
  return (
    <div className="flex bg-primary">
      <div className="flex my-4">
        <Image
          src={"/logo.png"}
          alt="intellidex logo"
          width={50}
          height={50}
        ></Image>
        <p className="text-white text">Intellidex</p>
      </div>
    </div>
  );
}
