import { redirect } from "next/navigation";

/**
 * Old /disease route — redirects to the canonical /diseases page.
 * The old page used mock data; the new one uses real backend APIs.
 */
export default function OldDiseasePage() {
  redirect("/diseases");
}
