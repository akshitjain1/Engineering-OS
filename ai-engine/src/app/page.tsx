import { redirect } from "next/navigation";

// The front door is the session, not a summary screen.
export default function Home() {
  redirect("/today");
}
